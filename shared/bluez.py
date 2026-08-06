#!/usr/bin/python3 -u
"""Serve the emulated peripherals on D-Bus as org.bluez, so bleak can drive them.

Runs on the image's interpreter rather than the dojo's, because dbus_fast came
in with bleak through pip and only exists there. The dojo's /run/dojo/bin/python3
carries the standard library and nothing else.

The dojo's Bluetooth is a userspace emulation: a peripheral is a unix socket
under /run/bluetooth, and the shipped hcitool/gatttool/hcidump talk to it
directly. bleak cannot -- it drives BlueZ over D-Bus and has no idea any of
this exists.

canshim.c solves the same problem on the CAN side by intercepting the socket
calls the tools make. That trick does not transfer: bleak is not making socket
calls to a device node, it is making method calls to a service. So this is the
service. It owns the name org.bluez, presents the object tree BlueZ presents --
an adapter, a device per peripheral, and a GATT tree per connection -- and
implements each method against ble.Client underneath.

What bleak needs and therefore what is here:

    /                       ObjectManager: GetManagedObjects, InterfacesAdded
    /org/bluez/hci0         Adapter1: StartDiscovery, StopDiscovery
    .../dev_AA_BB_...       Device1: Connect, Disconnect, ServicesResolved
    .../serviceNNNN         GattService1
    .../charNNNN            GattCharacteristic1: ReadValue, WriteValue,
                            StartNotify, StopNotify
    .../descNNNN            GattDescriptor1: ReadValue, WriteValue

NotifyAcquired and WriteAcquired are deliberately not exposed. bleak only
reaches for AcquireNotify when it sees them, and that path passes a file
descriptor over the bus; leaving them out keeps it on plain StartNotify.
"""

import asyncio
import os
import sys
import threading
import traceback
import time

sys.path.insert(0, "/challenge")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ble

from dbus_fast import BusType, PropertyAccess, Variant
from dbus_fast.aio import MessageBus
from dbus_fast.service import ServiceInterface, dbus_property, method, signal

ADAPTER_PATH = "/org/bluez/hci0"

FLAG_NAMES = [
    (ble.PROP_READ, "read"),
    (ble.PROP_WRITE_NO_RESPONSE, "write-without-response"),
    (ble.PROP_WRITE, "write"),
    (ble.PROP_NOTIFY, "notify"),
    (ble.PROP_INDICATE, "indicate"),
]


def full_uuid(short):
    return f"0000{short:04x}-0000-1000-8000-00805f9b34fb"


def device_path(address):
    return f"{ADAPTER_PATH}/dev_" + address.upper().replace(":", "_")


class ObjectManager(ServiceInterface):
    """The tree bleak asks for before it does anything else."""

    def __init__(self):
        super().__init__("org.freedesktop.DBus.ObjectManager")
        self.objects = {}

    @method()
    def GetManagedObjects(self) -> "a{oa{sa{sv}}}":
        return self.objects

    @signal()
    def InterfacesAdded(self, path, interfaces) -> "oa{sa{sv}}":
        return [path, interfaces]

    @signal()
    def InterfacesRemoved(self, path, interfaces) -> "oas":
        return [path, interfaces]

    def add(self, bus, path, interface):
        bus.export(path, interface)
        self.objects.setdefault(path, {})[interface.name] = interface.snapshot()
        self.InterfacesAdded(path, {interface.name: interface.snapshot()})

    def remove(self, bus, path):
        names = list(self.objects.pop(path, {}))
        if names:
            bus.unexport(path)
            self.InterfacesRemoved(path, names)

    def refresh(self, path, interface):
        if path in self.objects:
            self.objects[path][interface.name] = interface.snapshot()


class Adapter(ServiceInterface):
    def __init__(self, shim):
        super().__init__("org.bluez.Adapter1")
        self.shim = shim
        self._discovering = False

    @method()
    async def StartDiscovery(self):
        if self._discovering:
            return
        self._discovering = True
        self.emit_properties_changed({"Discovering": True})
        self.shim.start_discovery()

    @method()
    async def StopDiscovery(self):
        if not self._discovering:
            return
        self._discovering = False
        self.emit_properties_changed({"Discovering": False})
        self.shim.stop_discovery()

    @method()
    def SetDiscoveryFilter(self, properties: "a{sv}"):
        pass

    @method()
    def RemoveDevice(self, device: "o"):
        self.shim.forget(device)

    @dbus_property(PropertyAccess.READ)
    def Address(self) -> "s":
        return "00:00:00:00:00:00"

    @dbus_property(PropertyAccess.READ)
    def Name(self) -> "s":
        return "dojo"

    @dbus_property(PropertyAccess.READ)
    def Alias(self) -> "s":
        return "dojo"

    @dbus_property(PropertyAccess.READWRITE)
    def Powered(self) -> "b":
        return True

    @Powered.setter
    def Powered(self, value: "b"):
        pass

    @dbus_property(PropertyAccess.READ)
    def Discovering(self) -> "b":
        return self._discovering

    @dbus_property(PropertyAccess.READ)
    def UUIDs(self) -> "as":
        return []

    @dbus_property(PropertyAccess.READ)
    def Roles(self) -> "as":
        # bleak picks its adapter by looking for one that can be a central
        return ["central", "peripheral"]

    def snapshot(self):
        return {
            "Address": Variant("s", "00:00:00:00:00:00"),
            "Name": Variant("s", "dojo"),
            "Alias": Variant("s", "dojo"),
            "Powered": Variant("b", True),
            "Discovering": Variant("b", self._discovering),
            "UUIDs": Variant("as", []),
            "Roles": Variant("as", ["central", "peripheral"]),
        }


class Device(ServiceInterface):
    def __init__(self, shim, address, name, structures):
        super().__init__("org.bluez.Device1")
        self.shim = shim
        self.address = address
        self._name = name or address
        self._connected = False
        self._resolved = False
        self._manufacturer = {}
        self._service_data = {}
        self._uuids = []
        self.absorb(structures)

    def absorb(self, structures):
        """Take what the advertisement carries, the way a scan report would."""
        self._manufacturer = {}
        self._service_data = {}
        self._uuids = []
        for ad_type, payload in structures:
            if ad_type == ble.AD_MANUFACTURER and len(payload) >= 2:
                company = payload[0] | (payload[1] << 8)
                self._manufacturer[company] = Variant("ay", bytes(payload[2:]))
            elif ad_type == ble.AD_SERVICE_DATA_UUID16 and len(payload) >= 2:
                uuid = full_uuid(payload[0] | (payload[1] << 8))
                self._service_data[uuid] = Variant("ay", bytes(payload[2:]))
            elif ad_type in (ble.AD_COMPLETE_UUID16, ble.AD_INCOMPLETE_UUID16):
                for offset in range(0, len(payload) - 1, 2):
                    self._uuids.append(full_uuid(payload[offset] | (payload[offset + 1] << 8)))

    @method()
    async def Connect(self):
        await self.shim.connect(self)

    @method()
    async def Disconnect(self):
        await self.shim.disconnect(self)

    @method()
    def Pair(self):
        pass

    @dbus_property(PropertyAccess.READ)
    def Address(self) -> "s":
        return self.address.upper()

    @dbus_property(PropertyAccess.READ)
    def AddressType(self) -> "s":
        return "public"

    @dbus_property(PropertyAccess.READ)
    def Name(self) -> "s":
        return self._name

    @dbus_property(PropertyAccess.READ)
    def Alias(self) -> "s":
        return self._name

    @dbus_property(PropertyAccess.READ)
    def Paired(self) -> "b":
        return False

    @dbus_property(PropertyAccess.READ)
    def Bonded(self) -> "b":
        return False

    @dbus_property(PropertyAccess.READ)
    def Trusted(self) -> "b":
        return False

    @dbus_property(PropertyAccess.READ)
    def Blocked(self) -> "b":
        return False

    @dbus_property(PropertyAccess.READ)
    def LegacyPairing(self) -> "b":
        return False

    @dbus_property(PropertyAccess.READ)
    def Connected(self) -> "b":
        return self._connected

    @dbus_property(PropertyAccess.READ)
    def ServicesResolved(self) -> "b":
        return self._resolved

    @dbus_property(PropertyAccess.READ)
    def RSSI(self) -> "n":
        return -55

    @dbus_property(PropertyAccess.READ)
    def UUIDs(self) -> "as":
        return self._uuids

    @dbus_property(PropertyAccess.READ)
    def ManufacturerData(self) -> "a{qv}":
        return self._manufacturer

    @dbus_property(PropertyAccess.READ)
    def ServiceData(self) -> "a{sv}":
        return self._service_data

    @dbus_property(PropertyAccess.READ)
    def Adapter(self) -> "o":
        return ADAPTER_PATH

    def snapshot(self):
        return {
            "Address": Variant("s", self.address.upper()),
            "AddressType": Variant("s", "public"),
            "Name": Variant("s", self._name),
            "Alias": Variant("s", self._name),
            "Paired": Variant("b", False),
            "Bonded": Variant("b", False),
            "Trusted": Variant("b", False),
            "Blocked": Variant("b", False),
            "LegacyPairing": Variant("b", False),
            "Connected": Variant("b", self._connected),
            "ServicesResolved": Variant("b", self._resolved),
            "RSSI": Variant("n", -55),
            "UUIDs": Variant("as", self._uuids),
            "ManufacturerData": Variant("a{qv}", self._manufacturer),
            "ServiceData": Variant("a{sv}", self._service_data),
            "Adapter": Variant("o", ADAPTER_PATH),
        }

    def set_state(self, connected=None, resolved=None):
        changed = {}
        if connected is not None and connected != self._connected:
            self._connected = connected
            changed["Connected"] = Variant("b", connected)
        if resolved is not None and resolved != self._resolved:
            self._resolved = resolved
            changed["ServicesResolved"] = Variant("b", resolved)
        if changed:
            self.emit_properties_changed({k: v.value for k, v in changed.items()})
        return changed


class GattService(ServiceInterface):
    def __init__(self, uuid, device_object_path):
        super().__init__("org.bluez.GattService1")
        self._uuid = full_uuid(uuid)
        self._device = device_object_path

    @dbus_property(PropertyAccess.READ)
    def UUID(self) -> "s":
        return self._uuid

    @dbus_property(PropertyAccess.READ)
    def Device(self) -> "o":
        return self._device

    @dbus_property(PropertyAccess.READ)
    def Primary(self) -> "b":
        return True

    @dbus_property(PropertyAccess.READ)
    def Includes(self) -> "ao":
        return []

    def snapshot(self):
        return {
            "UUID": Variant("s", self._uuid),
            "Device": Variant("o", self._device),
            "Primary": Variant("b", True),
            "Includes": Variant("ao", []),
        }


class GattCharacteristic(ServiceInterface):
    def __init__(self, shim, device, uuid, properties, handle, service_path):
        super().__init__("org.bluez.GattCharacteristic1")
        self.shim = shim
        self.device = device
        self.handle = handle
        self.cccd_handle = None
        self._uuid = full_uuid(uuid)
        self._flags = [name for bit, name in FLAG_NAMES if properties & bit]
        self._service = service_path
        self._value = b""
        self._notifying = False

    @method()
    async def ReadValue(self, options: "a{sv}") -> "ay":
        value = await self.shim.read(self.device, self.handle)
        self._value = value
        return value

    @method()
    async def WriteValue(self, value: "ay", options: "a{sv}"):
        await self.shim.write(self.device, self.handle, bytes(value))

    @method()
    async def StartNotify(self):
        if self._notifying:
            return
        await self.shim.start_notify(self)
        self._notifying = True
        self.emit_properties_changed({"Notifying": True})

    @method()
    async def StopNotify(self):
        if not self._notifying:
            return
        await self.shim.stop_notify(self)
        self._notifying = False
        self.emit_properties_changed({"Notifying": False})

    @dbus_property(PropertyAccess.READ)
    def UUID(self) -> "s":
        return self._uuid

    @dbus_property(PropertyAccess.READ)
    def Service(self) -> "o":
        return self._service

    @dbus_property(PropertyAccess.READ)
    def Flags(self) -> "as":
        return self._flags

    @dbus_property(PropertyAccess.READ)
    def Notifying(self) -> "b":
        return self._notifying

    @dbus_property(PropertyAccess.READ)
    def Value(self) -> "ay":
        return self._value

    @dbus_property(PropertyAccess.READ)
    def MTU(self) -> "q":
        return ble.DEFAULT_MTU

    def snapshot(self):
        return {
            "UUID": Variant("s", self._uuid),
            "Service": Variant("o", self._service),
            "Flags": Variant("as", self._flags),
            "Notifying": Variant("b", self._notifying),
            "Value": Variant("ay", self._value),
            "MTU": Variant("q", ble.DEFAULT_MTU),
        }

    def push(self, value):
        self._value = bytes(value)
        self.emit_properties_changed({"Value": self._value})


class GattDescriptor(ServiceInterface):
    def __init__(self, shim, device, uuid, handle, characteristic_path):
        super().__init__("org.bluez.GattDescriptor1")
        self.shim = shim
        self.device = device
        self.handle = handle
        self._uuid = full_uuid(uuid)
        self._characteristic = characteristic_path
        self._value = b""

    @method()
    async def ReadValue(self, options: "a{sv}") -> "ay":
        value = await self.shim.read(self.device, self.handle)
        self._value = value
        return value

    @method()
    async def WriteValue(self, value: "ay", options: "a{sv}"):
        await self.shim.write(self.device, self.handle, bytes(value))

    @dbus_property(PropertyAccess.READ)
    def UUID(self) -> "s":
        return self._uuid

    @dbus_property(PropertyAccess.READ)
    def Characteristic(self) -> "o":
        return self._characteristic

    @dbus_property(PropertyAccess.READ)
    def Value(self) -> "ay":
        return self._value

    @dbus_property(PropertyAccess.READ)
    def Flags(self) -> "as":
        return ["read", "write"]

    def snapshot(self):
        return {
            "UUID": Variant("s", self._uuid),
            "Characteristic": Variant("o", self._characteristic),
            "Value": Variant("ay", self._value),
            "Flags": Variant("as", ["read", "write"]),
        }


class Shim:
    def __init__(self):
        self.bus = None
        self.loop = None
        self.manager = ObjectManager()
        self.adapter = Adapter(self)
        self.devices = {}
        self.clients = {}
        self.paths = {}
        self.notifiers = {}
        self.pumps = {}
        self.locks = {}
        self.announced = set()
        self.discovery = None

    async def run(self):
        self.loop = asyncio.get_running_loop()
        self.bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        self.bus.export("/", self.manager)
        self.manager.objects[ADAPTER_PATH] = {self.adapter.name: self.adapter.snapshot()}
        self.bus.export(ADAPTER_PATH, self.adapter)
        await self.bus.request_name("org.bluez")
        await self.bus.wait_for_disconnect()

    def start_discovery(self):
        # each scan starts over: everything visible is reported again
        self.announced.clear()
        if self.discovery is None or self.discovery.done():
            self.discovery = asyncio.create_task(self._discovery_loop())

    def stop_discovery(self):
        if self.discovery:
            self.discovery.cancel()
            self.discovery = None

    async def _discovery_loop(self):
        """Keep looking while the scan is running.

        A beacon rotates through several payloads, and a scanner that reported
        each device once would only ever see the first of them.
        """
        try:
            while True:
                await self.discover()
                await asyncio.sleep(0.3)
        except asyncio.CancelledError:
            pass
        except Exception:
            # an exception here would otherwise die with the task and leave
            # scanning quietly returning nothing at all
            traceback.print_exc()

    async def discover(self):
        """Publish a Device1 for everything currently advertising."""
        found = await asyncio.to_thread(ble.scan, False)
        for address, advertisement, response in found:
            structures = ble.Advertisement.parse(advertisement)
            if response:
                structures += ble.Advertisement.parse(response)
            path = device_path(address)
            name = ble.local_name(structures)
            if path in self.devices:
                # Report a device already on the bus once per scan, and again
                # whenever what it broadcasts changes. Reporting it on every
                # pass would be a fresh sighting every 0.3s, which buries a
                # console like bluetoothctl; reporting it only on change would
                # leave a second scan silent about a device that never varies,
                # and a scan has to say what is out there.
                device = self.devices[path]
                before = (dict(device._manufacturer), dict(device._service_data))
                device.absorb(structures)
                changed = before != (device._manufacturer, device._service_data)
                if not changed and path in self.announced:
                    continue
                self.announced.add(path)
                self.manager.refresh(path, device)
                device.emit_properties_changed({
                    "RSSI": -55,
                    "ManufacturerData": device._manufacturer,
                    "ServiceData": device._service_data,
                })
                continue
            self.announced.add(path)
            device = Device(self, address, name, structures)
            self.devices[path] = device
            self.manager.add(self.bus, path, device)

    def forget(self, path):
        device = self.devices.pop(path, None)
        if device:
            self.manager.remove(self.bus, path)

    async def connect(self, device):
        path = device_path(device.address)
        if path in self.clients:
            return
        client = await asyncio.to_thread(ble.Client, device.address)
        self.clients[path] = client
        self.locks[path] = threading.Lock()
        device.set_state(connected=True)
        self.manager.refresh(path, device)
        await self._publish_gatt(device, client, path)
        device.set_state(resolved=True)
        self.manager.refresh(path, device)

    async def _publish_gatt(self, device, client, base):
        services = await asyncio.to_thread(client.services)
        characteristics = await asyncio.to_thread(client.characteristics)
        attributes = await asyncio.to_thread(client.attributes)
        by_handle = dict(attributes)
        owned = []

        for start, end, service_uuid in services:
            service_path = f"{base}/service{start:04x}"
            self.manager.add(self.bus, service_path, GattService(service_uuid, base))
            owned.append(service_path)

            inside = [entry for entry in characteristics if start <= entry[0] <= end]
            for index, (declaration, properties, value_handle, uuid) in enumerate(inside):
                char_path = f"{service_path}/char{value_handle:04x}"
                characteristic = GattCharacteristic(
                    self, device, uuid, properties, value_handle, service_path)
                self.manager.add(self.bus, char_path, characteristic)
                owned.append(char_path)
                self.paths[char_path] = characteristic

                # everything between this value handle and the next declaration
                # is this characteristic's descriptors
                limit = inside[index + 1][0] if index + 1 < len(inside) else end
                for handle in sorted(by_handle):
                    if not value_handle < handle <= limit:
                        continue
                    uuid_at = by_handle[handle]
                    if uuid_at in (ble.UUID_PRIMARY_SERVICE, ble.UUID_CHARACTERISTIC):
                        continue
                    descriptor_path = f"{char_path}/desc{handle:04x}"
                    self.manager.add(self.bus, descriptor_path,
                                     GattDescriptor(self, device, uuid_at, handle, char_path))
                    owned.append(descriptor_path)
                    if uuid_at == ble.UUID_CCCD:
                        characteristic.cccd_handle = handle

        self.paths.setdefault(base, [])
        self.paths[base] = owned

    async def disconnect(self, device):
        path = device_path(device.address)
        for char_path, characteristic in list(self.paths.items()):
            if isinstance(characteristic, GattCharacteristic) and char_path.startswith(path):
                await self.stop_notify(characteristic)
                self.paths.pop(char_path, None)
        for owned in self.paths.pop(path, []):
            self.manager.remove(self.bus, owned)
        client = self.clients.pop(path, None)
        if client:
            await asyncio.to_thread(client.close)
        device.set_state(connected=False, resolved=False)
        self.manager.refresh(path, device)

    def _client(self, device):
        return self.clients[device_path(device.address)]

    def _guarded(self, device, call, *arguments):
        """Run one operation on the device's single connection.

        Everything shares that one socket -- reads, writes, and the thread
        draining notifications -- so they take turns.
        """
        with self.locks[device_path(device.address)]:
            return call(*arguments)

    async def read(self, device, handle):
        return await asyncio.to_thread(self._guarded, device, self._client(device).read, handle)

    async def write(self, device, handle, value):
        client = self._client(device)
        # BlueZ splits a value too long for one packet across Prepare Writes
        # without the caller having to know, so this does too
        call = client.write_long if len(value) > ble.DEFAULT_MTU - 3 else client.write
        return await asyncio.to_thread(self._guarded, device, call, handle, value)

    async def start_notify(self, characteristic):
        if characteristic.cccd_handle is None:
            raise ble.ATTError(ble.ERR_WRITE_NOT_PERMITTED)
        device = characteristic.device
        path = device_path(device.address)
        indicate = "indicate" in characteristic._flags

        # the subscription has to live on the same connection the caller writes
        # over: a peripheral that answers whoever asked sends its notification
        # to that connection, and a subscription made on a second one would
        # never hear it
        await asyncio.to_thread(self._guarded, device, self._client(device).subscribe,
                                characteristic.cccd_handle, indicate)
        self.notifiers.setdefault(path, set()).add(characteristic)
        if path not in self.pumps:
            stop = threading.Event()
            thread = threading.Thread(target=self._pump, args=(path, stop), daemon=True)
            self.pumps[path] = (stop, thread)
            thread.start()

    def _pump(self, path, stop):
        """Drain notifications between the caller's own requests."""
        client, lock = self.clients.get(path), self.locks.get(path)
        while not stop.is_set() and client:
            try:
                with lock:
                    for _, handle, value in client.events_stream(timeout=0.1, kind=True):
                        for characteristic in list(self.notifiers.get(path, ())):
                            if characteristic.handle == handle:
                                self.loop.call_soon_threadsafe(characteristic.push, value)
            except OSError:
                return
            time.sleep(0.02)

    async def stop_notify(self, characteristic):
        path = device_path(characteristic.device.address)
        subscribed = self.notifiers.get(path, set())
        subscribed.discard(characteristic)
        if subscribed:
            return
        entry = self.pumps.pop(path, None)
        if entry:
            entry[0].set()


if __name__ == "__main__":
    try:
        asyncio.run(Shim().run())
    except KeyboardInterrupt:
        pass
