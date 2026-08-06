# Picking an Unconsumed Rolling Code Out of a Burst (Replay)

The goal of this stage is as follows:
*  A rolling code has the fob and the receiver share a secret and a counter. Each press sends the counter and a code derived from it.
*  The receiver refuses a counter it has already accepted, and anything below it, so a straight recording played back is ignored.
*  But the fob does not transmit once. Radio gets lost, so one press goes out **three times, each with a different counter**.
*  The receiver acts on the first one it decodes and then stops listening for a moment, which leaves the rest of the burst unconsumed.
*  A fob frame is six bytes: two of counter, four of code.
*  You need to unlock the car with a code recorded **more than five seconds ago**.

Task:
*  Start the capture, then press the fob.

```
candump -l vcan0 &
/challenge/press-fob
```

*  Find the three six-byte fob frames in the log. Their counters differ by one.
*  Pick a code the receiver did not consume.
*  **Wait at least five seconds**, then send that one frame back.

```
cansend vcan0 <fob identifier>#<counter><code>
```

*  Read the result off `0x19A`.
   *  byte 0: `01` locked / `00` unlocked
   *  byte 1: how many times it has been unlocked
   *  byte 2: `01` unlocked / `02` counter already used / `03` code did not verify

Hints:
*  Record with `candump -l vcan0` and replay with `canplayer -I <logfile>`.
*  **Do not replay the whole log.** It contains the button press frame, and replaying that presses the fob again, pushing the counter past everything you recorded.
*  Cut it down to the one frame you want, or just send it with `cansend`.
*  Do not rush the send. The doors open, but no flag: a code from a moment ago is indistinguishable from the owner pressing the button.

Unlock the car from an aged recording and the flag goes out on the bus. Watch for it with `candump -a vcan0`!
