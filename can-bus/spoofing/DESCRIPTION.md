# Reverse Engineering a Signal to Lie to the Cluster (Spoofing)

The goal of this stage is as follows:
*  In the field nobody hands you a message layout. Identifiers and byte positions vary by manufacturer, model and year, and are not published.
*  You work them out by lining up what you can see on a display against what you can capture on the bus.
*  A real wheel speed sensor is transmitting the truth five times a second, and the cluster believes whatever arrived last.
*  You need to make the cluster read **exactly 133 km/h** and hold it there for **three seconds**.

Task:
*  Bring up the instrument cluster.

```
/challenge/dashboard
```

*  Find the bytes that track the needle. `candump` scrolls too fast, so use `cansniffer`.

```
cansniffer -c vcan0
```

*  It keeps one line per identifier and colours the bytes that change. Quit with `q`.
*  Compare the byte pair against the displayed value to recover the encoding. It is not plain km/h.
*  Transmit 133 km/h, in that encoding, on the identifier the cluster *listens to*, for more than three seconds.
*  The real sensor keeps transmitting the truth the whole time, and the cluster weighs what it heard across the window. Matching the sensor's five frames a second is nowhere near enough. Send in a loop with no wait in it.
*  Do not take the display as proof. It draws whatever the status frame says, so injecting there puts 133 on the screen without the cluster having believed anything.
*  Drive the bus from python with `vcan.py` from `/challenge`.

```
import sys
sys.path.insert(0, "/challenge")
import vcan

bus = vcan.Bus("vcan0")
bus.send(0x123, bytes([0x11, 0x22]))
```

Get the cluster to believe 133 and the flag goes out on the bus. Watch for it with `candump -a vcan0`!
