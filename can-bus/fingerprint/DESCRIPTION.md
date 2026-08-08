# Telling Two Senders Apart on One Identifier (Fingerprinting)

The goal of this stage is as follows:
*  A CAN frame says what it means and never who sent it, so a second node can transmit an identifier that belongs to somebody else and no receiver can tell.
*  Cho and Shin showed the bus gives it away anyway. A periodic message is paced by its sender's own crystal, so its period is a fingerprint of the part, not of the payload. Their intrusion detection system, CIDS, watches arrival times for exactly this.
*  Something on this bus is transmitting wheel speed on `0x1C4` alongside the real sensor. Both carry a plausible speed and the frames are the same shape, so nothing you read out of one tells you which sent it.
*  The sensor's datasheet gives its period as **50 ms**. The impostor keeps its own clock.
*  Report the impostor's period on `0x1C5`, as microseconds in four bytes, big endian.

Task:
*  Capture `0x1C4` with arrival times.

```
candump -t a vcan0,1C4:7FF > /tmp/capture.txt
```

*  Both senders are on that identifier, so the intervals between neighbouring frames are not either period. Watch long enough to have a few hundred arrivals.
*  Recover the two periods from the arrival times. A period `T` shows itself when the arrivals stack up in phase against it.

```
#!/usr/bin/python3
import math

def fit(times, period):                       # 1.0 means every arrival in phase
    angles = [2 * math.pi * (t / period % 1.0) for t in times]
    return math.hypot(sum(map(math.cos, angles)),
                      sum(map(math.sin, angles))) / len(times)
```

*  Sweep candidate periods and keep the ones that stand out. Two will.
*  Discard the one the datasheet already gave you. Report the other.

```
python3 -c 'import sys, struct; sys.path.insert(0, "/challenge"); import vcan
vcan.Bus("vcan0").send(0x1C5, struct.pack(">I", 47000) + bytes(4))'
```

Report the impostor's period and the flag goes out on the bus, on its own identifier rather than the one you filtered for. Watch all of it with `candump -a vcan0`!
