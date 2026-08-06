# Enumerating Controllers and Data Identifiers (Enumeration)

The goal of this stage is as follows:
*  Last time you were told the engine controller sits at `0x7E0`. On a car you have never seen, nobody tells you.
*  ISO 15765-4 reserves `0x7E0` through `0x7E7` for diagnostic requests, with responses eight above, at `0x7E8` through `0x7EF`.
*  Manufacturers put their own controllers wherever they like, and the interesting ones are rarely where the specification says.
*  You need to sweep `0x700` through `0x7FF`, find the controller that should not be there, and read what it holds.

Task:
*  Send `3E 00` (TesterPresent) to each identifier and see which addresses answer.
*  Sweep data identifiers on every controller you find, using service `0x22`.

```
isotpreq vcan0 7E0 7E8 22F190
```

*  Sort the answers into two kinds.
   *  A record that exists comes back as `62` followed by the identifier.
   *  One that does not comes back as `7F 22 31` (requestOutOfRange).
*  Read the records off the controller that answered outside the range the specification set aside.

Hints:
*  Sweep with `3E 00`. Every controller implements it and it changes no state.
*  Try the `0xF1xx` block first. That is where part numbers, software versions and serial numbers live.
*  Apply the same rule for response addresses: eight above the request.
*  Do not spawn a process per request. Script it, importing `vcan.py` and `isotp.py` from `/challenge`.

```
import sys
sys.path.insert(0, "/challenge")
import isotp, vcan

bus = vcan.Bus("vcan0")
response = isotp.request(bus, 0x7E0, 0x7E8, bytes.fromhex("3E00"), timeout=0.2)
```

The records on the controller that was hiding carry the flag!
