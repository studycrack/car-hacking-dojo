# Reading and Clearing DTCs to Cover Your Tracks (Fault Memory)

The goal of this stage is as follows:
*  A controller handed a request it cannot serve does not just answer `7F` and forget. It records a **DTC**.
*  A DTC is three bytes of identifier and one of status, and it stays until a technician clears it.
*  So sweeping a controller's services leaves one line of fault memory per request it did not like.
*  This controller has a release routine that hands over the flag, and it **will not run while a single DTC remains**.
*  You need to clear the fault memory your sweep created, then run the release routine.

Task:
*  Find the release routine's identifier. Sweep with `31 01 <id>`; the identifier that answers anything other than `requestOutOfRange` is the one.
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

*  Run the release routine immediately after.

Hints:
*  **Get the order right.** Finish the sweep, then clear, then run.
*  Do not clear while you are still hunting for the routine. The rest of the sweep just fills the memory again.
*  Read `19 02 FF` as you go, so you can see how you look right now.
*  After clearing, send only requests that leave no DTC behind.

Run the release routine and its response carries the flag!
