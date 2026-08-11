# Forging an Authenticated Frame Without the Key (SecOC)

The goal of this stage is as follows:
*  **SecOC** attaches a **MAC**, computed with a key the sender and receiver share, to frames that matter.
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

```
cansend vcan0 1B0#<payload><freshness><mac>
```

Unlock the doors and the flag goes out on the bus, on its own identifier rather than the one you filtered for. Watch all of it with `candump -a vcan0`!
