The previous challenge told you that the engine controller lives at `0x7E0`.
On a car you have never seen before, nobody tells you that.

ISO 15765-4 reserves `0x7E0` through `0x7E7` for diagnostic requests, with
responses eight identifiers higher at `0x7E8`-`0x7EF`, and a legislated OBD-II
scan tool will only ever talk to those. Manufacturers, however, put their own
controllers wherever they like --- and the interesting ones, the telematics
units and the engineering interfaces, are exactly the ones that are not where
the standard says to look.

So you enumerate. Two sweeps:

**Which addresses answer?** Service `0x3E`, TesterPresent, is the "are you
there" of UDS. Every controller implements it, and it changes no state. Send
`3E 00` to each identifier in `0x700`-`0x7FF` and see which ones respond.

**What does an address expose?** Once you have found a controller, sweep data
identifiers with service `0x22`. Records in the `0xF1xx` block are the
identification records --- part numbers, software versions, serial numbers ---
and are where manufacturers habitually leave things they should not. A
controller answers `62` plus the identifier when a record exists, and
`7F 22 31` (requestOutOfRange) when it does not.

You have a tool for the transport layer this time; `isotpreq` handles frame
segmentation and flow control for you:

    isotpreq vcan0 7E0 7E8 22F190

Sweeping several hundred requests through a process per request is slow. Script
it instead --- both `vcan.py` and `isotp.py` are importable from `/challenge`:

    import sys
    sys.path.insert(0, "/challenge")
    import isotp, vcan

    bus = vcan.Bus("vcan0")
    response = isotp.request(bus, 0x7E0, 0x7E8, bytes.fromhex("3E00"), timeout=0.2)

Find the controller that should not be there, and read what it is holding.
