# Forging an Authenticated Frame Without the Key (SecOC)

The goal of this stage is as follows:
*  **SecOC** attaches a **MAC** to frames that matter, computed with a key the sender and receiver share.
*  Every transmission carries the payload, a **freshness value** and a truncated MAC.
*  Freshness must never go backwards, so replaying a frame you saw earlier is refused.
*  This car's body controller takes door commands on `0x1B0`: two bytes of payload, one of freshness, three of MAC, six in total.
*  It reports on `0x1B1`.
   *  byte 0: `01` locked / `00` unlocked
   *  byte 1: the last freshness value it accepted
   *  byte 2: `01` accepted / `02` MAC did not verify / `03` freshness was not ahead
*  You need to unlock a car the owner did not ask you to unlock, without the key.

Task:
*  Watch the car lock itself several times. A lock command goes out every four seconds.

```
candump vcan0,1B0:7FF
```

*  Press the fob too, so you know what an unlock command looks like.

```
/challenge/press-fob
```

*  Compare the frames you captured and work out **what the MAC was computed over**.
   *  Watch what the MAC does when the payload is the same.
   *  Watch what the MAC does when the freshness differs.
*  Use what you found to build an unlock command, send it, and read the result off `0x1B1`.

Hints:
*  Do not attack the cryptography. Without the key you cannot compute a MAC.
*  Find what the MAC does not cover instead. A field left out of the computation can be changed freely and still verify.
*  Read byte 2 carefully. `02` means the MAC was wrong; `03` means the freshness was. They are different problems.
*  Pick a freshness ahead of what byte 1 reports, but do not reach too far ahead.

Unlock the doors and the flag goes out on the bus. Watch for it with `candump -a vcan0`!
