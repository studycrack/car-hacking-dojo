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
ATT_WRITE_REQ = 0x12
ATT_WRITE_RSP = 0x13

ERR_INVALID_HANDLE = 0x01
ERR_READ_NOT_PERMITTED = 0x02
ERR_WRITE_NOT_PERMITTED = 0x03
ERR_INVALID_PDU = 0x04
ERR_ATTRIBUTE_NOT_FOUND = 0x0A
ERR_INVALID_OFFSET = 0x07
ERR_UNLIKELY_ERROR = 0x0E
ERR_UNSUPPORTED_GROUP_TYPE = 0x10

UUID_PRIMARY_SERVICE = 0x2800
UUID_CHARACTERISTIC = 0x2803
UUID_USER_DESCRIPTION = 0x2901
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


class Attribute:
    def __init__(self, handle, uuid, value=b"", readable=True, writable=False, on_write=None):
        self.handle = handle
        self.uuid = uuid
        self.value = value
        self.readable = readable
        self.writable = writable
        self.on_write = on_write


class Server:
    """A GATT peripheral.

    Attributes are added in handle order, the way a real attribute table is
    laid out: a service declaration, then for each characteristic a declaration
    followed by its value, followed by any descriptors.
    """

    def __init__(self, address, name, advertising=None):
        self.address = address
        self.name = name
        self.advertising = dict(advertising or {})
        self.advertising.setdefault("name", name)
        self.attributes = []
        self.next_handle = 1
        self.service_handle = None

        self.add_service(0x1800)
        self.add_characteristic(UUID_DEVICE_NAME, name.encode(), PROP_READ)

    def _append(self, uuid, value, readable=True, writable=False, on_write=None):
        attribute = Attribute(self.next_handle, uuid, value, readable, writable, on_write)
        self.attributes.append(attribute)
        self.next_handle += 1
        return attribute

    def add_service(self, uuid):
        declaration = self._append(UUID_PRIMARY_SERVICE, struct.pack("<H", uuid))
        self.service_handle = declaration.handle
        return declaration.handle

    def add_characteristic(self, uuid, value=b"", properties=PROP_READ, on_write=None):
        # a characteristic is two attributes: the declaration announcing the
        # properties and where the value lives, and the value itself
        value_handle = self.next_handle + 1
        self._append(UUID_CHARACTERISTIC,
                     struct.pack("<BH H", properties, value_handle, uuid))
        return self._append(uuid, value,
                            readable=bool(properties & PROP_READ),
                            writable=bool(properties & (PROP_WRITE | PROP_WRITE_NO_RESPONSE)),
                            on_write=on_write)

    def add_descriptor(self, uuid, value):
        return self._append(uuid, value)

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
            if attribute.on_write:
                result = attribute.on_write(value, connection)
                if result is not None:
                    return self.error(opcode, handle, result)
            else:
                attribute.value = value
            return bytes([ATT_WRITE_RSP])

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
                       if a.uuid == kind and start <= a.handle <= end]
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
            matches = [a for a in self.attributes if start <= a.handle <= end]
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
        os.makedirs(SOCKET_DIR, exist_ok=True)
        lines = "".join(f"{key}={value}\n" for key, value in self.advertising.items())
        path = advertising_path(self.address)
        with open(path, "w") as handle:
            handle.write(lines)
        os.chmod(path, 0o644)

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

    def request(self, pdu):
        self.sock.sendall(struct.pack("<H", len(pdu)) + pdu)
        header = self._recv_exactly(2)
        (length,) = struct.unpack("<H", header)
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


def scan():
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
        devices.append((address, record))
    return devices
