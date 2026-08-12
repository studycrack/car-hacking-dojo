The goal of this stage is as follows:
*  Last time you were told the engine controller sits at `0x7E0`. On a car you have never seen, nobody tells you.
*  ISO 15765-4 reserves `0x7E0` through `0x7E7` for diagnostic requests, with responses eight above, at `0x7E8` through `0x7EF`.
*  Manufacturers put their own controllers wherever they like, and the interesting ones are rarely where the specification says.
*  You need to sweep `0x700` through `0x7FF`, find the controller that should not be there, and read what it holds.

Task:
*  Send `3E 00` (TesterPresent) to each address and see which ones answer.
   *  A live address answers at once. A dead one never answers, and `isotpreq` waits five seconds for it. That silence is the whole cost of the sweep, so cut it short.

```
timeout 0.2 isotpreq vcan0 700 708 3E00
```

*  Sweep DIDs on every controller you find, using service `0x22`.

```
isotpreq vcan0 7E0 7E8 22F190
```

*  Sort the answers into two kinds.
   *  A record that exists comes back as `62` followed by the identifier.
   *  One that does not comes back as `7F 22 31` (requestOutOfRange).
*  Read the records off the controller whose address falls outside the range the specification set aside.

The records on the controller that was hiding carry the flag!
