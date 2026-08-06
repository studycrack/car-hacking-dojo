Reflashing firmware, running actuator tests and clearing an immobilizer sit
behind UDS service `0x27`, **SecurityAccess**, a challenge-response handshake:

1. Enter a non-default session with `10 03` (extended session).
2. Ask for a seed: `27 01`. The ECU answers `67 01` plus four random bytes.
3. Compute a key from that seed and send it: `27 02 <key>`. This ECU uses a
   16-bit key.
4. If the key is right, the ECU answers `67 02`.

The secret algorithm lives in the dealer diagnostic software. You are going to
guess instead: sixteen bits is 65,536 possibilities.

The standard's answer to that is an attempt limiter, and this ECU has one.
After **three** wrong keys it answers `7F 27 36` (exceedNumberOfAttempts) and
refuses to talk security for ten seconds, which stretches an exhaustive search
out to days.

But look at *what* resets that counter. Requesting a diagnostic session is an
ordinary thing for a tester to do, and this ECU treats a fresh session as a
fresh start --- no failed attempts, no lockout.

Script it. Both `vcan.py` and `isotp.py` are importable from `/challenge`:

    import sys
    sys.path.insert(0, "/challenge")
    import isotp, vcan

    bus = vcan.Bus("vcan0")
    print(isotp.request(bus, 0x7E0, 0x7E8, bytes.fromhex("1003")).hex())

The seed you are solving against only survives while you stay out of the
default session, so take it once and keep it.

Once unlocked, the routine you want is `0xF00D`:

    31 01 F0 0D
