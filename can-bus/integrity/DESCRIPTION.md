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
*  Send eight consecutive frames carrying `0x0BB8`, with both fields correct.
*  Read the verdict off `0x1F6`.
   *  byte 0: `01` accepted / `10` checksum wrong / `11` counter wrong
   *  byte 1: how many consecutive frames carrying the watched value have been accepted

Hints:
*  Work from the verdict byte one field at a time. It tells you which check you failed.
*  Watch it with `cansniffer -c vcan0`, which colours whichever bytes are moving.
*  Do not just replay the sample. Change the value and the protection fields have to change with it.
*  If byte 1 climbs and then drops to `0`, look at byte 0 at that moment. One frame in the middle was rejected.

Get eight in a row accepted and the flag goes out on the bus. Watch for it with `candump -a vcan0`!
