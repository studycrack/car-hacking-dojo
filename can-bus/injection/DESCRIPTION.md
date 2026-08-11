The goal of this stage is as follows:
*  A CAN frame carries no evidence of who sent it, so anything that can reach the bus can originate any message on it.
*  This car's body control module (BCM) speaks the following:

| Identifier | Direction | Layout |
| --- | --- | --- |
| `0x19A` | BCM broadcast | byte 0: `01` locked / `00` unlocked. bytes 2-3: session counter, big endian |
| `0x19B` | BCM receive | byte 0: `02` to unlock. byte 1: `FF` for all doors. bytes 2-3: the session counter currently being advertised |

*  The session counter is broadcast in the clear and rotates every thirty seconds.
*  You need to read it, then forge a `0x19B` frame with it and unlock the doors.

Task:
*  Watch `0x19A` and read the current session counter.

```
candump vcan0,19A:7FF
```

*  Build a `0x19B` frame with it. `cansend` uses the notation `candump` prints.

```
cansend vcan0 19B#02FFABCD
```

*  Fill the bytes as follows.
   *  Byte 0 is `02` to unlock, byte 1 is `FF` for all doors.
   *  Bytes 2-3 take the session counter you just read, in place of `ABCD` above.
*  Confirm that byte 0 of `0x19A` goes from `01` to `00`.

Unlock the doors and the flag goes out on the bus, on its own identifier rather than the one you filtered for. Watch all of it with `candump -a vcan0`!
