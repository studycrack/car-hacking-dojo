#!/run/dojo/bin/python3 -u
"""ISO 15765-2 (ISO-TP) transport, as used to carry UDS over CAN.

Payloads longer than 7 bytes are split across a First Frame and a series of
Consecutive Frames, with the receiver granting permission to continue via a
Flow Control frame.
"""

import time

SINGLE_FRAME = 0x0
FIRST_FRAME = 0x1
CONSECUTIVE_FRAME = 0x2
FLOW_CONTROL = 0x3

FLOW_STATUS_CONTINUE = 0x0
FLOW_STATUS_WAIT = 0x1
FLOW_STATUS_OVERFLOW = 0x2

# ISO 15765-2 N_Cr: how long a receiver waits for the next consecutive frame
# before giving up on the burst. This is a property of the protocol, not of
# how long the caller is willing to wait for a request to arrive -- an ECU
# listening all day still abandons an unfinished burst in a second.
CONSECUTIVE_FRAME_TIMEOUT = 1.0

# how often to come up for air while waiting, so that a deadline is still
# noticed on a bus where nothing at all is being transmitted
POLL_INTERVAL = 0.2


def pad(data):
    return bytes(data) + b"\x00" * (8 - len(data))


def send(bus, tx_id, rx_id, payload, timeout=2.0, frames=None):
    payload = bytes(payload)
    if len(payload) <= 7:
        bus.send(tx_id, pad(bytes([len(payload)]) + payload))
        return

    frames = frames if frames is not None else bus.frames()
    header = bytes([(FIRST_FRAME << 4) | (len(payload) >> 8), len(payload) & 0xFF])
    bus.send(tx_id, header + payload[:6])

    separation_time = 0
    deadline = time.time() + timeout
    previous_poll, bus.poll_interval = bus.poll_interval, POLL_INTERVAL
    for item in frames:
        if time.time() > deadline:
            bus.poll_interval = previous_poll
            raise TimeoutError("no flow control frame")
        if item is None:
            continue
        can_id, data = item
        if can_id != rx_id or len(data) < 3 or data[0] >> 4 != FLOW_CONTROL:
            continue
        if data[0] & 0x0F == FLOW_STATUS_WAIT:
            deadline = time.time() + timeout
            continue
        separation_time = data[2]
        break
    else:
        bus.poll_interval = previous_poll
        raise TimeoutError("no flow control frame")
    bus.poll_interval = previous_poll

    separation = separation_time / 1000.0 if separation_time <= 0x7F else 0.0001
    index = 1
    offset = 6
    while offset < len(payload):
        bus.send(tx_id, bytes([(CONSECUTIVE_FRAME << 4) | (index & 0x0F)]) + payload[offset:offset + 7])
        index += 1
        offset += 7
        if separation:
            time.sleep(separation)


def recv(bus, rx_id, tx_id, timeout=5.0, frames=None):
    frames = frames if frames is not None else bus.frames()
    deadline = time.time() + timeout
    previous_poll, bus.poll_interval = bus.poll_interval, POLL_INTERVAL
    for item in frames:
        if time.time() > deadline:
            bus.poll_interval = previous_poll
            raise TimeoutError("no response")
        if item is None:
            continue
        can_id, data = item
        if can_id != rx_id or not data:
            continue
        kind = data[0] >> 4
        if kind == SINGLE_FRAME:
            bus.poll_interval = previous_poll
            return data[1:1 + (data[0] & 0x0F)]
        if kind != FIRST_FRAME:
            continue
        total = ((data[0] & 0x0F) << 8) | data[1]
        payload = bytearray(data[2:8])
        bus.send(tx_id, pad([(FLOW_CONTROL << 4) | FLOW_STATUS_CONTINUE, 0x00, 0x00]))
        # a burst that never finishes must be abandoned rather than waited on
        # forever: a First Frame promising more than its sender goes on to send
        # would otherwise leave this receiver deaf to every later request
        expected = 1
        segment_deadline = time.time() + CONSECUTIVE_FRAME_TIMEOUT
        for item in frames:
            if time.time() > segment_deadline:
                break
            if item is None:
                continue
            can_id, data = item
            if can_id != rx_id or not data or data[0] >> 4 != CONSECUTIVE_FRAME:
                continue
            if data[0] & 0x0F != expected & 0x0F:
                break
            expected += 1
            payload += data[1:]
            segment_deadline = time.time() + CONSECUTIVE_FRAME_TIMEOUT
            if len(payload) >= total:
                bus.poll_interval = previous_poll
                return bytes(payload[:total])
        deadline = time.time() + timeout
    bus.poll_interval = previous_poll
    raise TimeoutError("no response")


def request(bus, tx_id, rx_id, payload, timeout=5.0):
    frames = bus.frames()
    send(bus, tx_id, rx_id, payload, frames=frames)
    response = recv(bus, rx_id, tx_id, timeout=timeout, frames=frames)
    while len(response) >= 3 and response[0] == 0x7F and response[2] == 0x78:
        response = recv(bus, rx_id, tx_id, timeout=timeout, frames=frames)
    return response
