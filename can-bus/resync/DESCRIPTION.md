# Walking a Rolling Code Counter Backwards (Resynchronisation)

The goal of this stage is as follows:
*  A rolling code receiver has to tolerate a fob pressed out of range, so it keeps a window. When it sees a run of consecutive counters it **resynchronises to the run**.
*  The assumption underneath is that only the real fob can produce consecutive valid codes. A recording can: it holds a run of them.
*  Replaying a captured sequence drags the counter back to where it was recorded, and the codes that follow it in the recording become live again.
*  This receiver is the one you already defeated with an unconsumed code, plus that tolerance. The single spare code will not reach: the counter has moved far past your recording by the time you use it.
*  `0x19A` reports on the receiver.
   *  byte 0: `01` locked / `00` unlocked
   *  byte 1: how many times it has been unlocked
   *  byte 2: `01` unlocked / `02` counter behind / `03` code did not verify / `04` resynchronised
   *  bytes 3-4: the counter it currently accepts, big endian
*  Unlock the car with a code the counter had already moved past.

Task:
*  Record a press, and keep the whole burst. The counters in it are consecutive.

```
candump -l vcan0 &
/challenge/press-fob
```

*  Drive the counter well past your recording. Press the fob several more times and watch bytes 3-4 of `0x19A` climb.
*  Replay the first few frames of the recording, in order, one at a time. Watch byte 2.
*  Once it reports `04`, replay the next frame in the recording.

```
cansend vcan0 <fob identifier>#<counter><code>
```

*  Byte 1 of `0x19A` climbs by one as the car unlocks. Byte 0 went to `00` on your very first press, so it tells you nothing here.

Unlock the car from behind its own counter and the flag goes out on the bus. Watch for it with `candump -a vcan0`!
