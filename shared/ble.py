#!/run/dojo/bin/python3 -u
"""A Bluetooth Low Energy GATT server and client, minus the radio.

A workspace container has no Bluetooth controller and cannot create one: an
HCI device needs CAP_NET_ADMIN, which the dojo does not grant. So the radio and
the controller are the parts that are missing here. Everything above them is
real -- these are the ATT protocol data units from the Bluetooth Core
Specification, with the handles, opcodes, and error codes a genuine peripheral
would answer with.

Each peripheral listens on a unix socket named after its address, and writes
its advertising data alongside it so that a scan can see it without connecting:

    /run/bluetooth/c4:be:84:20:11:07        the ATT bearer
    /run/bluetooth/c4:be:84:20:11:07.adv    advertising data
"""

import os
import selectors
import socket
import struct
import threading
import time

SOCKET_DIR = "/run/bluetooth"

ATT_ERROR_RSP = 0x01
ATT_EXCHANGE_MTU_REQ = 0x02
ATT_EXCHANGE_MTU_RSP = 0x03
ATT_FIND_INFORMATION_REQ = 0x04
ATT_FIND_INFORMATION_RSP = 0x05
ATT_READ_BY_TYPE_REQ = 0x08
ATT_READ_BY_TYPE_RSP = 0x09
ATT_READ_REQ = 0x0A
ATT_READ_RSP = 0x0B
ATT_READ_BLOB_REQ = 0x0C
ATT_READ_BLOB_RSP = 0x0D
ATT_READ_BY_GROUP_TYPE_REQ = 0x10
ATT_READ_BY_GROUP_TYPE_RSP = 0x11
ATT_PREPARE_WRITE_REQ = 0x16
ATT_PREPARE_WRITE_RSP = 0x17
ATT_EXECUTE_WRITE_REQ = 0x18
ATT_EXECUTE_WRITE_RSP = 0x19
ATT_WRITE_REQ = 0x12
ATT_WRITE_RSP = 0x13
ATT_HANDLE_VALUE_NTF = 0x1B
ATT_HANDLE_VALUE_IND = 0x1D
ATT_HANDLE_VALUE_CFM = 0x1E

ERR_INVALID_HANDLE = 0x01
ERR_READ_NOT_PERMITTED = 0x02
ERR_WRITE_NOT_PERMITTED = 0x03
ERR_INVALID_PDU = 0x04
ERR_ATTRIBUTE_NOT_FOUND = 0x0A
ERR_INVALID_OFFSET = 0x07
ERR_INVALID_ATTRIBUTE_LENGTH = 0x0D
ERR_UNLIKELY_ERROR = 0x0E
ERR_UNSUPPORTED_GROUP_TYPE = 0x10

UUID_PRIMARY_SERVICE = 0x2800
UUID_CHARACTERISTIC = 0x2803
UUID_USER_DESCRIPTION = 0x2901
UUID_CCCD = 0x2902

AD_FLAGS = 0x01
AD_INCOMPLETE_UUID16 = 0x02
AD_COMPLETE_UUID16 = 0x03
AD_SHORTENED_NAME = 0x08
AD_COMPLETE_NAME = 0x09
AD_SERVICE_DATA_UUID16 = 0x16
AD_MANUFACTURER = 0xFF

AD_TYPE_NAMES = {
    AD_FLAGS: "Flags",
    AD_INCOMPLETE_UUID16: "Incomplete 16-bit Service UUIDs",
    AD_COMPLETE_UUID16: "Complete 16-bit Service UUIDs",
    AD_SHORTENED_NAME: "Shortened Local Name",
    AD_COMPLETE_NAME: "Complete Local Name",
    AD_SERVICE_DATA_UUID16: "Service Data - 16-bit UUID",
    AD_MANUFACTURER: "Manufacturer Specific Data",
}

ADVERTISING_MAX = 31

# Scanning happens below ATT, at the link layer, which this emulation does not
# otherwise model. These two opcodes stand in for it, and are deliberately
# outside the ATT opcode space. What matters is the asymmetry they preserve:
# an advertisement is broadcast and costs the listener nothing, while a scan
# response only exists because the scanner transmitted a request.
LL_SCAN_REQ = 0xFE
LL_SCAN_RSP = 0xFF

CCCD_NONE = 0x0000
CCCD_NOTIFY = 0x0001
CCCD_INDICATE = 0x0002
UUID_DEVICE_NAME = 0x2A00

PROP_READ = 0x02
PROP_WRITE_NO_RESPONSE = 0x04
PROP_WRITE = 0x08
PROP_NOTIFY = 0x10
PROP_INDICATE = 0x20

DEFAULT_MTU = 23


def device_path(address):
    return os.path.join(SOCKET_DIR, address)


def advertising_path(address):
    return device_path(address) + ".adv"


class Advertisement:
    """One advertising payload.

    A payload is a sequence of AD structures, each a length byte, a type byte,
    and its data. There are thirty-one bytes for the lot, which is the single
    most consequential number in BLE advertising: it is why beacons carry
    almost nothing, and why anything larger needs the scan response as well.
    """

    def __init__(self):
        self.structures = []

    def add(self, ad_type, data):
        self.structures.append((ad_type, bytes(data)))
        return self

    def add_name(self, name, complete=True):
        return self.add(AD_COMPLETE_NAME if complete else AD_SHORTENED_NAME, name.encode())

    def add_manufacturer(self, company, data):
        return self.add(AD_MANUFACTURER, struct.pack("<H", company) + bytes(data))

    def add_service_data(self, uuid, data):
        return self.add(AD_SERVICE_DATA_UUID16, struct.pack("<H", uuid) + bytes(data))

    def encode(self):
        payload = b""
        for ad_type, data in self.structures:
            payload += bytes([len(data) + 1, ad_type]) + data
        if len(payload) > ADVERTISING_MAX:
            raise ValueError(f"advertising payload is {len(payload)} bytes, "
                             f"the air allows {ADVERTISING_MAX}")
        return payload

    @staticmethod
    def parse(payload):
        structures = []
        offset = 0
        while offset < len(payload):
            length = payload[offset]
            if length == 0 or offset + 1 + length > len(payload):
                break
            structures.append((payload[offset + 1], payload[offset + 2:offset + 1 + length]))
            offset += 1 + length
        return structures


class Attribute:
    def __init__(self, handle, uuid, value=b"", readable=True, writable=False, on_write=None,
                 discoverable=True):
        self.handle = handle
        self.uuid = uuid
        self.value = value
        self.readable = readable
        self.writable = writable
        self.on_write = on_write
        # a peripheral chooses what its discovery responses mention; it does
        # not thereby stop serving the handle
        self.discoverable = discoverable


class Server:
    """A GATT peripheral.

    Attributes are added in handle order, the way a real attribute table is
    laid out: a service declaration, then for each characteristic a declaration
    followed by its value, followed by any descriptors.
    """

    def __init__(self, address, name, advertising=None, scan_response=None):
        self.address = address
        self.name = name
        if advertising is None:
            advertising = Advertisement().add(AD_FLAGS, b"\x06").add_name(name)
        self.advertising = advertising
        self.scan_response = scan_response
        self.attributes = []
        self.next_handle = 1
        self.service_handle = None
        self.subscriptions = {}
        self.pending_indications = {}
        self.on_subscribe = None
        self.rotation = None
        self.rotation_period = 0.4
        self.prepared = {}

        self.add_service(0x1800)
        self.add_characteristic(UUID_DEVICE_NAME, name.encode(), PROP_READ)

    def _append(self, uuid, value, readable=True, writable=False, on_write=None,
                discoverable=True):
        attribute = Attribute(self.next_handle, uuid, value, readable, writable, on_write,
                              discoverable)
        self.attributes.append(attribute)
        self.next_handle += 1
        return attribute

    def add_service(self, uuid):
        declaration = self._append(UUID_PRIMARY_SERVICE, struct.pack("<H", uuid))
        self.service_handle = declaration.handle
        return declaration.handle

    def add_characteristic(self, uuid, value=b"", properties=PROP_READ, on_write=None,
                           discoverable=True):
        # a characteristic is two attributes: the declaration announcing the
        # properties and where the value lives, and the value itself
        value_handle = self.next_handle + 1
        self._append(UUID_CHARACTERISTIC,
                     struct.pack("<BH H", properties, value_handle, uuid),
                     discoverable=discoverable)
        return self._append(uuid, value,
                            readable=bool(properties & PROP_READ),
                            writable=bool(properties & (PROP_WRITE | PROP_WRITE_NO_RESPONSE)),
                            on_write=on_write, discoverable=discoverable)

    def add_descriptor(self, uuid, value):
        return self._append(uuid, value)

    def add_cccd(self, value_handle):
        """The Client Characteristic Configuration Descriptor.

        Notifications and indications are off until a client turns them on by
        writing here: 0x0001 for notify, 0x0002 for indicate. The peripheral
        keeps that choice per connection, which is why two clients can watch
        the same characteristic in different ways.
        """
        def on_write(value, connection):
            setting = int.from_bytes(value[:2], "little") if value else CCCD_NONE
            self.subscriptions[(connection, value_handle)] = setting
            if self.on_subscribe:
                self.on_subscribe(value_handle, setting, connection)
            return None

        return self._append(UUID_CCCD, b"\x00\x00", writable=True, on_write=on_write)

    def subscription(self, connection, value_handle):
        return self.subscriptions.get((connection, value_handle), CCCD_NONE)

    def notify(self, connection, value_handle, value):
        if self.subscription(connection, value_handle) != CCCD_NOTIFY:
            return False
        self._send(connection, bytes([ATT_HANDLE_VALUE_NTF]) +
                   struct.pack("<H", value_handle) + value[:DEFAULT_MTU - 3])
        return True

    def indicate(self, connection, value_handle, value):
        """Queue an indication. Only one may be outstanding: the next goes out
        when the client confirms the last, which is the whole difference from a
        notification."""
        if self.subscription(connection, value_handle) != CCCD_INDICATE:
            return False
        queue = self.pending_indications.setdefault(connection, [])
        queue.append((value_handle, value[:DEFAULT_MTU - 3]))
        if len(queue) == 1:
            self._send_indication(connection)
        return True

    def notify_text(self, connection, value_handle, text, prefix=b""):
        """Push a value too long for one PDU.

        A notification carries at most MTU-3 bytes -- opcode and handle take
        the rest -- so anything longer goes out in pieces, which is what a real
        peripheral streaming a long value does.
        """
        payload = text.encode() if isinstance(text, str) else text
        room = DEFAULT_MTU - 3 - len(prefix)
        chunks = [payload[offset:offset + room] for offset in range(0, len(payload), room)]
        return [prefix + chunk for chunk in chunks]

    def _send_indication(self, connection):
        queue = self.pending_indications.get(connection)
        if not queue:
            return
        value_handle, value = queue[0]
        self._send(connection, bytes([ATT_HANDLE_VALUE_IND]) +
                   struct.pack("<H", value_handle) + value)

    def _send(self, connection, pdu):
        try:
            connection.sendall(struct.pack("<H", len(pdu)) + pdu)
        except OSError:
            pass

    def find(self, handle):
        for attribute in self.attributes:
            if attribute.handle == handle:
                return attribute
        return None

    def error(self, opcode, handle, code):
        return struct.pack("<BBHB", ATT_ERROR_RSP, opcode, handle, code)

    def handle_pdu(self, pdu, connection):
        if not pdu:
            return None
        opcode = pdu[0]

        if opcode == LL_SCAN_REQ:
            payload = self.scan_response.encode() if self.scan_response else b""
            return bytes([LL_SCAN_RSP]) + payload

        if opcode == ATT_EXCHANGE_MTU_REQ:
            return struct.pack("<BH", ATT_EXCHANGE_MTU_RSP, DEFAULT_MTU)

        if opcode == ATT_READ_REQ:
            (handle,) = struct.unpack("<H", pdu[1:3])
            attribute = self.find(handle)
            if attribute is None:
                return self.error(opcode, handle, ERR_INVALID_HANDLE)
            if not attribute.readable:
                return self.error(opcode, handle, ERR_READ_NOT_PERMITTED)
            return bytes([ATT_READ_RSP]) + attribute.value[:DEFAULT_MTU - 1]

        if opcode == ATT_WRITE_REQ:
            (handle,) = struct.unpack("<H", pdu[1:3])
            attribute = self.find(handle)
            if attribute is None:
                return self.error(opcode, handle, ERR_INVALID_HANDLE)
            if not attribute.writable:
                return self.error(opcode, handle, ERR_WRITE_NOT_PERMITTED)
            value = pdu[3:]
            # a Write Request carries opcode and handle alongside the value, so
            # anything longer than the MTU less three cannot be sent as one PDU
            if len(value) > DEFAULT_MTU - 3:
                return self.error(opcode, handle, ERR_INVALID_ATTRIBUTE_LENGTH)
            if attribute.on_write:
                result = attribute.on_write(value, connection)
                if result is not None:
                    return self.error(opcode, handle, result)
            else:
                attribute.value = value
            return bytes([ATT_WRITE_RSP])

        if opcode == ATT_HANDLE_VALUE_CFM:
            queue = self.pending_indications.get(connection)
            if queue:
                queue.pop(0)
                self._send_indication(connection)
            return None

        if opcode == ATT_PREPARE_WRITE_REQ:
            handle, offset = struct.unpack("<HH", pdu[1:5])
            attribute = self.find(handle)
            if attribute is None:
                return self.error(opcode, handle, ERR_INVALID_HANDLE)
            if not attribute.writable:
                return self.error(opcode, handle, ERR_WRITE_NOT_PERMITTED)
            self.prepared.setdefault(connection, []).append((handle, offset, pdu[5:]))
            return pdu[:1].replace(bytes([ATT_PREPARE_WRITE_REQ]),
                                   bytes([ATT_PREPARE_WRITE_RSP])) + pdu[1:]

        if opcode == ATT_EXECUTE_WRITE_REQ:
            queued = self.prepared.pop(connection, [])
            if not pdu[1:2] or pdu[1] == 0x00:
                return bytes([ATT_EXECUTE_WRITE_RSP])
            assembled = {}
            for handle, offset, fragment in queued:
                buffer = assembled.setdefault(handle, bytearray())
                if len(buffer) < offset + len(fragment):
                    buffer.extend(b"\x00" * (offset + len(fragment) - len(buffer)))
                buffer[offset:offset + len(fragment)] = fragment
            for handle, buffer in assembled.items():
                attribute = self.find(handle)
                if attribute is None:
                    continue
                if attribute.on_write:
                    attribute.on_write(bytes(buffer), connection)
                else:
                    attribute.value = bytes(buffer)
            return bytes([ATT_EXECUTE_WRITE_RSP])

        if opcode == ATT_READ_BLOB_REQ:
            handle, offset = struct.unpack("<HH", pdu[1:5])
            attribute = self.find(handle)
            if attribute is None:
                return self.error(opcode, handle, ERR_INVALID_HANDLE)
            if not attribute.readable:
                return self.error(opcode, handle, ERR_READ_NOT_PERMITTED)
            if offset > len(attribute.value):
                return self.error(opcode, handle, ERR_INVALID_OFFSET)
            return bytes([ATT_READ_BLOB_RSP]) + attribute.value[offset:offset + DEFAULT_MTU - 1]

        if opcode == ATT_READ_BY_GROUP_TYPE_REQ:
            start, end, group = struct.unpack("<HHH", pdu[1:7])
            if group != UUID_PRIMARY_SERVICE:
                return self.error(opcode, start, ERR_UNSUPPORTED_GROUP_TYPE)
            services = [a for a in self.attributes
                        if a.uuid == UUID_PRIMARY_SERVICE and start <= a.handle <= end]
            if not services:
                return self.error(opcode, start, ERR_ATTRIBUTE_NOT_FOUND)
            first = services[0]
            last_handle = self._group_end(first.handle)
            entry = struct.pack("<HH", first.handle, last_handle) + first.value
            return struct.pack("<BB", ATT_READ_BY_GROUP_TYPE_RSP, len(entry)) + entry

        if opcode == ATT_READ_BY_TYPE_REQ:
            start, end, kind = struct.unpack("<HHH", pdu[1:7])
            matches = [a for a in self.attributes
                       if a.uuid == kind and start <= a.handle <= end and a.discoverable]
            if not matches:
                return self.error(opcode, start, ERR_ATTRIBUTE_NOT_FOUND)
            size = 2 + len(matches[0].value)
            entries = b""
            for attribute in matches:
                if 2 + len(attribute.value) != size:
                    break
                candidate = struct.pack("<H", attribute.handle) + attribute.value
                if 2 + len(entries) + len(candidate) > DEFAULT_MTU:
                    break
                entries += candidate
            return struct.pack("<BB", ATT_READ_BY_TYPE_RSP, size) + entries

        if opcode == ATT_FIND_INFORMATION_REQ:
            start, end = struct.unpack("<HH", pdu[1:5])
            matches = [a for a in self.attributes if start <= a.handle <= end and a.discoverable]
            if not matches:
                return self.error(opcode, start, ERR_ATTRIBUTE_NOT_FOUND)
            entries = b""
            for attribute in matches:
                candidate = struct.pack("<HH", attribute.handle, attribute.uuid)
                if 2 + len(entries) + len(candidate) > DEFAULT_MTU:
                    break
                entries += candidate
            return struct.pack("<BB", ATT_FIND_INFORMATION_RSP, 0x01) + entries

        return self.error(opcode, 0x0000, ERR_INVALID_PDU)

    def _group_end(self, service_handle):
        following = [a.handle for a in self.attributes
                     if a.uuid == UUID_PRIMARY_SERVICE and a.handle > service_handle]
        return (min(following) - 1) if following else self.attributes[-1].handle

    def advertise(self):
        """Put the payloads where a scanner can see them.

        The advertisement goes out unprompted; the scan response only exists
        because a scanner asked for it, which is the difference between a
        passive and an active scan.
        """
        os.makedirs(SOCKET_DIR, exist_ok=True)
        # only the advertisement goes in the file: it is broadcast, so anyone
        # in range has it. The scan response is not written anywhere, because
        # nothing has asked for it yet.
        lines = f"adv={self.advertising.encode().hex()}\n"
        path = advertising_path(self.address)
        with open(path, "w") as handle:
            handle.write(lines)
        os.chmod(path, 0o644)

    def _rotate(self):
        """Re-advertise on a cycle.

        Thirty-one bytes is a hard ceiling, so anything larger than a payload
        goes out as a sequence of payloads instead -- which is what a beacon
        with more to say than fits actually does. A scanner that looks once
        sees one of them.
        """
        index = 0
        while True:
            payloads = self.rotation(index)
            self.advertising = payloads[0]
            self.scan_response = payloads[1] if len(payloads) > 1 else None
            self.advertise()
            index += 1
            time.sleep(self.rotation_period)

    def run(self):
        os.makedirs(SOCKET_DIR, exist_ok=True)
        path = device_path(self.address)
        if os.path.exists(path):
            os.remove(path)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(path)
        os.chmod(path, 0o666)
        server.listen(8)
        self.advertise()
        if self.rotation:
            threading.Thread(target=self._rotate, daemon=True).start()

        selector = selectors.DefaultSelector()
        selector.register(server, selectors.EVENT_READ, None)
        buffers = {}
        while True:
            for key, _ in selector.select():
                if key.data is None:
                    connection, _ = server.accept()
                    buffers[connection] = b""
                    selector.register(connection, selectors.EVENT_READ, True)
                    continue
                connection = key.fileobj
                try:
                    chunk = connection.recv(4096)
                except OSError:
                    chunk = b""
                if not chunk:
                    selector.unregister(connection)
                    buffers.pop(connection, None)
                    connection.close()
                    continue
                buffers[connection] += chunk
                while len(buffers[connection]) >= 2:
                    (length,) = struct.unpack("<H", buffers[connection][:2])
                    if len(buffers[connection]) < 2 + length:
                        break
                    pdu = buffers[connection][2:2 + length]
                    buffers[connection] = buffers[connection][2 + length:]
                    response = self.handle_pdu(pdu, connection)
                    if response:
                        connection.sendall(struct.pack("<H", len(response)) + response)


class Client:
    def __init__(self, address, timeout=5):
        deadline = time.time() + timeout
        while True:
            try:
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(device_path(address))
                break
            except (FileNotFoundError, ConnectionRefusedError):
                self.sock.close()
                if time.time() > deadline:
                    raise
                time.sleep(0.05)
        self.events = []

    def request(self, pdu):
        self.sock.sendall(struct.pack("<H", len(pdu)) + pdu)
        while True:
            response = self._read_pdu()
            # a peripheral may push a notification at any moment, including
            # between your request and its answer; it is not the answer
            if response[0] in (ATT_HANDLE_VALUE_NTF, ATT_HANDLE_VALUE_IND):
                self.events.append(response)
                continue
            return response

    def _read_pdu(self):
        (length,) = struct.unpack("<H", self._recv_exactly(2))
        return self._recv_exactly(length)

    def _recv_exactly(self, count):
        data = b""
        while len(data) < count:
            chunk = self.sock.recv(count - len(data))
            if not chunk:
                raise ConnectionError("peripheral closed the connection")
            data += chunk
        return data

    def read(self, handle):
        response = self.request(struct.pack("<BH", ATT_READ_REQ, handle))
        if response[0] == ATT_ERROR_RSP:
            raise ATTError(response[4])
        chunk = response[1:]
        value = chunk
        # a response carries at most MTU-1 bytes, so a *chunk* that fills one
        # means there is probably more; Read Blob picks up where it left off.
        # The test is on the chunk, not on the total: a value of 44 bytes
        # arrives as two full chunks and still has a third waiting.
        while len(chunk) == DEFAULT_MTU - 1:
            response = self.request(struct.pack("<BHH", ATT_READ_BLOB_REQ, handle, len(value)))
            if response[0] == ATT_ERROR_RSP:
                break
            chunk = response[1:]
            if not chunk:
                break
            value += chunk
        return value

    def read_once(self, handle, offset=0):
        """A single ATT transaction, truncated the way the protocol truncates."""
        if offset:
            pdu = struct.pack("<BHH", ATT_READ_BLOB_REQ, handle, offset)
        else:
            pdu = struct.pack("<BH", ATT_READ_REQ, handle)
        response = self.request(pdu)
        if response[0] == ATT_ERROR_RSP:
            raise ATTError(response[4])
        return response[1:]

    def write(self, handle, value):
        response = self.request(struct.pack("<BH", ATT_WRITE_REQ, handle) + value)
        if response[0] == ATT_ERROR_RSP:
            raise ATTError(response[4])
        return True

    def services(self, start=0x0001, end=0xFFFF):
        """Walk the service declarations.

        A peripheral answers with as many as fit and no more, so a client keeps
        asking from the end of the last group until it is told there are none.
        """
        found = []
        handle = start
        while handle <= end:
            response = self.request(struct.pack("<BHHH", ATT_READ_BY_GROUP_TYPE_REQ,
                                                handle, end, UUID_PRIMARY_SERVICE))
            if response[0] == ATT_ERROR_RSP:
                break
            size = response[1]
            body = response[2:]
            if not body:
                break
            for offset in range(0, len(body), size):
                entry = body[offset:offset + size]
                group_start, group_end = struct.unpack("<HH", entry[:4])
                uuid = struct.unpack("<H", entry[4:6])[0]
                found.append((group_start, group_end, uuid))
                handle = group_end + 1
        return found

    def characteristics(self, start=0x0001, end=0xFFFF):
        found = []
        handle = start
        while handle <= end:
            response = self.request(struct.pack("<BHHH", ATT_READ_BY_TYPE_REQ,
                                                handle, end, UUID_CHARACTERISTIC))
            if response[0] == ATT_ERROR_RSP:
                break
            size = response[1]
            body = response[2:]
            for offset in range(0, len(body), size):
                entry = body[offset:offset + size]
                declaration = struct.unpack("<H", entry[:2])[0]
                properties, value_handle, uuid = struct.unpack("<BHH", entry[2:7])
                found.append((declaration, properties, value_handle, uuid))
                handle = declaration + 1
            if not body:
                break
        return found

    def attributes(self, start=0x0001, end=0xFFFF):
        found = []
        handle = start
        while handle <= end:
            response = self.request(struct.pack("<BHH", ATT_FIND_INFORMATION_REQ, handle, end))
            if response[0] == ATT_ERROR_RSP:
                break
            body = response[2:]
            for offset in range(0, len(body), 4):
                attribute_handle, uuid = struct.unpack("<HH", body[offset:offset + 4])
                found.append((attribute_handle, uuid))
                handle = attribute_handle + 1
            if not body:
                break
        return found

    def write_long(self, handle, value, chunk=None):
        """Write a value that will not fit in one Write Request.

        Each piece is queued with a Prepare Write, carrying the offset it
        belongs at, and nothing is applied until the Execute Write at the end.
        """
        room = chunk or (DEFAULT_MTU - 5)
        for offset in range(0, len(value), room):
            fragment = value[offset:offset + room]
            response = self.request(struct.pack("<BHH", ATT_PREPARE_WRITE_REQ, handle, offset)
                                    + fragment)
            if response[0] == ATT_ERROR_RSP:
                raise ATTError(response[4])
        response = self.request(struct.pack("<BB", ATT_EXECUTE_WRITE_REQ, 0x01))
        if response[0] == ATT_ERROR_RSP:
            raise ATTError(response[4])
        return True

    def subscribe(self, cccd_handle, indicate=False):
        return self.write(cccd_handle, struct.pack("<H", CCCD_INDICATE if indicate else CCCD_NOTIFY))

    def confirm(self):
        self.sock.sendall(struct.pack("<HB", 1, ATT_HANDLE_VALUE_CFM))

    def events_stream(self, timeout=5.0, confirm=True):
        """Yield (handle, value) as the peripheral pushes them.

        An indication is answered with a confirmation unless the caller asks
        otherwise; a peripheral that never gets one never sends the next.
        """
        deadline = time.time() + timeout
        while True:
            while self.events:
                pdu = self.events.pop(0)
                if pdu[0] == ATT_HANDLE_VALUE_IND and confirm:
                    self.confirm()
                yield struct.unpack("<H", pdu[1:3])[0], pdu[3:]
                deadline = time.time() + timeout
            remaining = deadline - time.time()
            if remaining <= 0:
                return
            self.sock.settimeout(remaining)
            try:
                pdu = self._read_pdu()
            except (socket.timeout, TimeoutError):
                return
            finally:
                self.sock.settimeout(None)
            if pdu[0] in (ATT_HANDLE_VALUE_NTF, ATT_HANDLE_VALUE_IND):
                self.events.append(pdu)

    def close(self):
        self.sock.close()


class ATTError(Exception):
    NAMES = {
        ERR_INVALID_HANDLE: "Invalid handle",
        ERR_READ_NOT_PERMITTED: "Attribute can't be read",
        ERR_WRITE_NOT_PERMITTED: "Attribute can't be written",
        ERR_INVALID_PDU: "Invalid PDU",
        ERR_ATTRIBUTE_NOT_FOUND: "No attribute found within the given range",
        ERR_UNLIKELY_ERROR: "Request attribute has encountered an unlikely error",
        ERR_UNSUPPORTED_GROUP_TYPE: "Attribute type is not a supported grouping",
    }

    def __init__(self, code):
        self.code = code
        super().__init__(self.NAMES.get(code, f"ATT error 0x{code:02X}"))


def scan(active=True):
    """Report what is advertising.

    A passive scan hears only what a peripheral broadcasts on its own. An
    active scan sends a scan request and gets a second payload back, which is
    where a device puts what did not fit in the first thirty-one bytes.
    """
    if not os.path.isdir(SOCKET_DIR):
        return []
    devices = []
    for entry in sorted(os.listdir(SOCKET_DIR)):
        if not entry.endswith(".adv"):
            continue
        address = entry[:-4]
        record = {}
        try:
            for line in open(os.path.join(SOCKET_DIR, entry)):
                key, _, value = line.strip().partition("=")
                record[key] = value
        except OSError:
            continue
        advertisement = bytes.fromhex(record.get("adv", ""))
        response = None
        if active:
            # asking means transmitting, and transmitting means touching the
            # peripheral rather than only listening to it
            try:
                client = Client(address, timeout=1)
                reply = client.request(bytes([LL_SCAN_REQ]))
                client.close()
                if reply and reply[0] == LL_SCAN_RSP and len(reply) > 1:
                    response = reply[1:]
            except OSError:
                response = None
        devices.append((address, advertisement, response))
    return devices


def local_name(structures):
    for ad_type, data in structures:
        if ad_type in (AD_COMPLETE_NAME, AD_SHORTENED_NAME):
            return data.decode(errors="replace")
    return None
