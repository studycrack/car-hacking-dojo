The goal of this stage is as follows:
*  A controller that is handed a request it cannot serve does not just answer `7F` and forget. It records a **DTC**.
*  A DTC is three bytes of identifier and one of status, and it stays until a technician clears it.
*  So sweeping a controller's services leaves fault memory behind, one line for each kind of request it did not like.
*  This controller has a release routine that hands over the flag, but the routine **will not run while a single DTC remains**.
*  You need to clear the fault memory your sweep created, then run the release routine.

Task:
*  Find the release routine's identifier. Sweep with `31 01 <id>`; the identifier that answers anything other than `7F 31 31` (requestOutOfRange) is the one. That is more requests than anyone types, so script it with `isotp.py` and `vcan.py` from `/challenge`.

```
#!/usr/bin/python3
import sys
sys.path.insert(0, "/challenge")
import isotp, vcan

bus = vcan.Bus("vcan0")
response = isotp.request(bus, 0x7E0, 0x7E8, bytes.fromhex("31010000"), timeout=0.2)
```
*  Look at the trail you have left.

```
19 02 FF
```

*  Read the response format.
   *  `19 02 <mask>` returns DTCs whose status byte overlaps the mask. Use `FF` to see all of them.
   *  The response is `59 02`, an availability mask, then four bytes per DTC.
*  Clear the fault memory.

```
14 FF FF FF
```

*  Run the release routine.

Run the release routine and its response carries the flag!
