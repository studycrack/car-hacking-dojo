#!/run/dojo/bin/python3 -u
"""A userspace CAN bus.

Container workspaces do not have CAP_NET_ADMIN, so a real SocketCAN `vcan`
interface cannot be created. This module emulates one: a hub process
broadcasts every frame it receives to every other attached client, which is
the behavior a CAN transceiver sees on a real bus.

Frames are carried over the socket in can-utils notation, one per line:

    1A0#DEADBEEF00112233
"""

import os
import select
import selectors
import socket
import sys
import threading
import time

SOCKET_DIR = "/run/vcan"
MAX_QUEUED_BYTES = 1 << 20


def socket_path(interface):
    return os.path.join(SOCKET_DIR, interface)


def parse_frame(line):
    can_id, _, data = line.strip().partition("#")
    return int(can_id, 16), bytes.fromhex(data)


def format_frame(can_id, data):
    return f"{can_id:03X}#{data.hex().upper()}"


def ascii_repr(data):
    return "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in data)


class Bus:
    def __init__(self, interface="vcan0", timeout=10):
        deadline = time.time() + timeout
        while True:
            try:
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(socket_path(interface))
                break
            except (FileNotFoundError, ConnectionRefusedError):
                self.sock.close()
                if time.time() > deadline:
                    raise
                time.sleep(0.05)
        self.buffer = b""
        self.send_lock = threading.Lock()
        # when set, frames() yields None if nothing arrives within the interval,
        # so a reader waiting on a deadline can notice time passing on a bus
        # that has gone quiet. Left off by default: every other caller wants to
        # block until there is genuinely a frame.
        self.poll_interval = None

    def send(self, can_id, data):
        line = (format_frame(can_id, bytes(data)) + "\n").encode()
        with self.send_lock:
            self.sock.sendall(line)

    def send_text(self, can_id, text, chunk_size=8, prefix=b""):
        payload = text.encode() if isinstance(text, str) else text
        chunk_size -= len(prefix)
        lines = "".join(
            format_frame(can_id, prefix + payload[offset:offset + chunk_size]) + "\n"
            for offset in range(0, len(payload), chunk_size)
        )
        with self.send_lock:
            self.sock.sendall(lines.encode())

    def frames(self):
        while True:
            while b"\n" not in self.buffer:
                # select rather than settimeout: this socket is shared with the
                # threads that transmit on it, so a timeout set here would be
                # inherited by their sendall. It also leaves nothing to restore
                # if this generator is abandoned while parked on the yield.
                if self.poll_interval is not None:
                    readable, _, _ = select.select([self.sock], [], [], self.poll_interval)
                    if not readable:
                        yield None
                        continue
                chunk = self.sock.recv(4096)
                if not chunk:
                    return
                self.buffer += chunk
            line, _, self.buffer = self.buffer.partition(b"\n")
            try:
                yield parse_frame(line.decode())
            except ValueError:
                continue

    def close(self):
        self.sock.close()


def attach(interface, tool, timeout=3):
    try:
        return Bus(interface, timeout=timeout)
    except PermissionError:
        raise SystemExit(f"{tool}: {interface}: permission denied -- you are not on that bus")
    except OSError:
        raise SystemExit(f"{tool}: {interface}: no such interface (is the challenge running?)")


def transmit_periodically(bus, can_id, payload_source, hz):
    def loop():
        period = 1.0 / hz
        while True:
            payload = payload_source() if callable(payload_source) else payload_source
            if payload is not None:
                bus.send(can_id, payload)
            time.sleep(period)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    return thread


class Hub:
    def __init__(self, interface, private=False):
        self.path = socket_path(interface)
        os.makedirs(SOCKET_DIR, exist_ok=True)
        if os.path.exists(self.path):
            os.remove(self.path)
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.path)
        # a private bus stands in for one the attacker cannot physically reach
        os.chmod(self.path, 0o600 if private else 0o666)
        self.server.listen(64)
        self.server.setblocking(False)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.server, selectors.EVENT_READ, None)
        self.inbox = {}
        self.outbox = {}
        self.filters = {}

    def run(self):
        while True:
            for key, events in self.selector.select():
                try:
                    if key.data is None:
                        self.accept()
                    elif events & selectors.EVENT_READ:
                        self.read(key.fileobj)
                    elif events & selectors.EVENT_WRITE:
                        self.flush(key.fileobj)
                except Exception:
                    # the socket is world writable, so anything a client can
                    # put on the wire must cost that client its connection at
                    # worst, never the bus everyone else is sharing
                    if key.data is not None:
                        self.drop(key.fileobj)
                    else:
                        # nothing to drop when it is the listening socket that
                        # failed, and it stays readable, so without this the
                        # loop spins on it at full speed
                        time.sleep(0.01)

    def accept(self):
        client, _ = self.server.accept()
        client.setblocking(False)
        self.inbox[client] = b""
        self.outbox[client] = b""
        self.filters[client] = []
        self.selector.register(client, selectors.EVENT_READ, True)

    def read(self, client):
        try:
            chunk = client.recv(4096)
        except (BlockingIOError, ConnectionResetError):
            return self.drop(client)
        if not chunk:
            return self.drop(client)
        self.inbox[client] += chunk
        while b"\n" in self.inbox[client]:
            line, _, self.inbox[client] = self.inbox[client].partition(b"\n")
            if line.startswith(b"!"):
                self.set_filters(client, line[1:])
                continue
            self.broadcast(client, line + b"\n")

    def set_filters(self, client, spec):
        """Filter for a client, the way the kernel does it for a CAN socket.

        A reader that discards unwanted frames itself has to block while it
        waits for a wanted one, which breaks the promise select() made to the
        caller; doing it here keeps every readable byte a frame the reader
        asked for.

        A rule written ~ID:MASK is inverted, the way CAN_INV_FILTER is: it
        matches every identifier except that one.
        """
        rules = []
        for rule in spec.decode(errors="replace").split(","):
            if ":" not in rule:
                continue
            wanted, _, mask = rule.partition(":")
            inverted = wanted.startswith("~")
            try:
                rules.append((int(wanted[1:] if inverted else wanted, 16),
                              int(mask, 16), inverted))
            except ValueError:
                continue
        self.filters[client] = rules

    def broadcast(self, sender, line):
        try:
            can_id = int(line.split(b"#")[0], 16) if b"#" in line else None
        except ValueError:
            return
        for client in list(self.outbox):
            if client is sender:
                continue
            rules = self.filters.get(client)
            # the kernel ORs the rules together, and an inverted rule matches
            # when the identifier does not
            if rules and can_id is not None and not any(
                    (can_id & mask == wanted & mask) != inverted
                    for wanted, mask, inverted in rules):
                continue
            if len(self.outbox[client]) > MAX_QUEUED_BYTES:
                continue
            self.outbox[client] += line
            self.selector.modify(client, selectors.EVENT_READ | selectors.EVENT_WRITE, True)
        self.flush_all()

    def flush_all(self):
        for client in list(self.outbox):
            self.flush(client)

    def flush(self, client):
        if client not in self.outbox:
            return
        if self.outbox[client]:
            try:
                sent = client.send(self.outbox[client])
            except BlockingIOError:
                return
            except (BrokenPipeError, ConnectionResetError):
                return self.drop(client)
            self.outbox[client] = self.outbox[client][sent:]
        if not self.outbox[client]:
            self.selector.modify(client, selectors.EVENT_READ, True)

    def drop(self, client):
        try:
            self.selector.unregister(client)
        except KeyError:
            pass
        self.inbox.pop(client, None)
        self.outbox.pop(client, None)
        self.filters.pop(client, None)
        client.close()


def main():
    arguments = [argument for argument in sys.argv[1:] if not argument.startswith("--")]
    interface = arguments[0] if arguments else "vcan0"
    Hub(interface, private="--private" in sys.argv[1:]).run()


if __name__ == "__main__":
    main()
