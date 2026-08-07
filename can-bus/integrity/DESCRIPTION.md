# Recovering an Alive Counter and Checksum to Forge a Frame (E2E)

The goal of this stage is as follows:
*  The cluster you lied to earlier believed whatever arrived. Modern modules do not.
*  There is no room for a signature in eight bytes, so safety-relevant messages carry two small fields instead, from AUTOSAR End-to-End protection.
   *  an **alive counter**, incremented on every transmission
   *  a **checksum**, computed over the payload
*  This car's steering assist module takes torque requests on `0x1F5` and rejects anything whose two fields do not agree.
*  Nobody is going to tell you how they are computed. You have to recover both.
*  You need to get **eight consecutive frames** carrying a steering torque of `0x0BB8` accepted.

Task:
*  Start capturing, then have a properly protected request generated for you.

```
candump vcan0,1F5:7FF &
/challenge/park-assist
```

*  Watch how the last two bytes move across the sample.
   *  One increments regularly, transmission to transmission.
   *  The other changes whenever the earlier bytes change.
*  Recover how each field is computed.
*  Send eight consecutive frames carrying `0x0BB8`, with both fields correct. Each one needs its own counter and checksum, so drive the bus from python with `vcan.py` from `/challenge`.

```
#!/usr/bin/python3
import sys
sys.path.insert(0, "/challenge")
import vcan

bus = vcan.Bus("vcan0")
for can_id, data in bus.frames():     # what the bus is carrying
    ...
bus.send(0x1F5, payload)              # what you put on it
```

*  Read the verdict off `0x1F6`.
   *  byte 0: `01` accepted / `10` checksum wrong / `11` counter wrong
   *  byte 1: how many consecutive frames carrying the watched value have been accepted

Get eight in a row accepted and the flag goes out on the bus — on its own identifier, not the one you filtered for, so watch all of it with `candump -a vcan0`!
