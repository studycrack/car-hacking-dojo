# Out-Talking the Controller That Says No (Contention)

The goal of this stage is as follows:
*  The immobiliser will not authorise the engine until the smart key ECU reports that the key has been validated. That result travels as an ordinary frame, and nothing in the frame says who sent it.
*  The work is not to defeat the key check. It is to report a validated result yourself.
*  **One frame decides nothing.** The smart key ECU is on the same bus reporting the opposite ten times a second, and the immobiliser goes by the recent majority of what it has heard.
*  `0x3D0` carries the smart key status. Byte 0 is `00` for no key and `01` for validated.
*  `0x3D8` is the immobiliser.
   *  byte 0: `00` immobilised / `01` engine authorised
   *  byte 1: validated frames among the last 20 it heard
   *  byte 2: how many of those 20 it needs
   *  byte 3: tenths of a second the majority has held
*  Hold the majority long enough and the engine is authorised.

Task:
*  Watch the immobiliser and the smart key ECU together.

```
candump vcan0,3D0:7FF,3D8:7FF
```

*  Report a validated key once, and watch byte 1 of `0x3D8`. It moves by one, then ages back out of the window.

```
cansend vcan0 3D0#01
```

*  Report it faster than the controller reports otherwise, and do not stop. The loop never returns, so run it in a second terminal or in the background.

```
while true; do cansend vcan0 3D0#01; done &
```

*  Byte 1 climbs past byte 2, byte 3 starts counting, and byte 0 goes to `01`.
*  The filter above does not carry the flag, so run `candump -a vcan0` as well before the majority holds.

Out-talk the smart key ECU for long enough and the flag goes out on the bus, on its own identifier rather than the ones you filtered for. Watch all of it with `candump -a vcan0`!
