Not every diagnostic service is free to call. Reflashing firmware, running
actuator tests, clearing an immobilizer --- these sit behind UDS service
`0x27`, **SecurityAccess**, a challenge-response handshake:

1. The tester enters a non-default session with `10 03` (extended session).
2. The tester asks for a seed: `27 01`. The ECU answers `67 01` plus four
   random bytes.
3. The tester computes a key from that seed using a secret algorithm and sends
   it back: `27 02 <key>`. This ECU uses a 16-bit key.
4. If the key is right, the ECU answers `67 02` and the session is unlocked.

The secret algorithm lives in the dealer diagnostic software, and getting hold
of it is its own adventure. You are not going to do that here. You are going
to do what security researchers have repeatedly done to real ECUs instead:
guess.

Sixteen bits is 65,536 possibilities, which a computer exhausts in seconds.
The standard's answer to that is an attempt limiter --- and this ECU has one.
After **three** wrong keys it answers `7F 27 36` (exceedNumberOfAttempts) and
then refuses to talk security at all for ten seconds, which stretches an
exhaustive search out to days.

But look carefully at *what* resets that counter. Requesting a diagnostic
session is a perfectly ordinary thing for a tester to do, and this ECU treats
a fresh session as a fresh start --- no failed attempts, no lockout.
Nothing about UDS says the attempt counter must survive a session change, and
on this ECU it does not.

Script it. Both `vcan.py` and `isotp.py` are importable from `/challenge`:

    import sys
    sys.path.insert(0, "/challenge")
    import isotp, vcan

    bus = vcan.Bus("vcan0")
    print(isotp.request(bus, 0x7E0, 0x7E8, bytes.fromhex("1003")).hex())

A tight loop exhausts the keyspace in seconds. Note that the seed you are
solving against only survives while you stay out of the default session, so
take the seed once and keep it.

Once you are unlocked, the routine you are after is `0xF00D`, started with
RoutineControl:

    31 01 F0 0D

The ECU will tell you rather more than it should.
