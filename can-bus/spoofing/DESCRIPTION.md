# Reverse Engineering a Signal to Lie to the Cluster (Spoofing)

The goal of this stage is as follows:
*  In the field nobody hands you a message layout. Identifiers and byte positions vary by manufacturer, model and year, and are not published.
*  So you work them out by lining up what you can see on a display against what you can capture on the bus.
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
*  Transmit 133 km/h, in that encoding, on the identifier the cluster *listens to*, continuously for three seconds.

```
import sys
sys.path.insert(0, "/challenge")
import vcan

bus = vcan.Bus("vcan0")
bus.send(0x123, bytes([0x11, 0x22]))
```

Hints:
*  Do not assume there is only one identifier tracking the needle. One is what the cluster **listens to**, the other is what the cluster **reports**.
*  **Do not judge by the display.** It draws whatever the status frame says, so injecting on the status frame puts 133 on the screen without the cluster having believed anything.
*  Tell them apart by what travels alongside. The status frame carries engine RPM next to the speed, and a wheel speed sensor has no way to know the engine's state.
*  Do not loop `cansend` in the shell. It will not outpace the real sensor. Drive the bus from python instead.

Get the cluster to believe 133 and the flag goes out on the bus. Watch for it with `candump -a vcan0`!
