The goal of this stage is as follows:
*  A **DBC file** is how bus definitions are written down: one entry per message, one line per signal.
*  Each signal carries a start bit, a width, a byte order, a scale and an offset.
*  This car's DBC is at `/challenge/vehicle.dbc`.
*  Its `BCM_Command` message is awkward to pack by hand: cabin temperature is scale `0.5` with offset `-20`, the fan is four bits, and the byte order is Motorola, which numbers start bits in a way that does not match intuition.
*  You need to transmit a frame commanding a cabin target of **30.5 degrees** and a vent fan of **11**.

Task:
*  Read what the DBC declares.

```
cantools dump /challenge/vehicle.dbc
```

*  Work out the signal names and bit positions of `BCM_Command`.
*  `BCM_Command` carries four signals, not two. `encode` refuses to build a frame unless you give it a value for every one of them, so the two you do not care about still need something.
*  Run your script with `/usr/bin/python3`. There are two interpreters here, and only the one in the challenge image has `cantools`. Plain `python3` does not.

```
/usr/bin/python3 -c 'import cantools; print(cantools.__version__)'
```

*  Encode the values with `cantools`, which does the bit packing for you, and put the frame on the bus with `vcan.py` from `/challenge`.

```
#!/usr/bin/python3
import sys
sys.path.insert(0, "/challenge")
import cantools, vcan

db = cantools.database.load_file("/challenge/vehicle.dbc")
message = db.get_message_by_name("BCM_Command")
data = message.encode({...})
vcan.Bus("vcan0").send(message.frame_id, data)
```

*  Or print the encoded bytes and send them with `cansend`, which takes the same notation `candump` prints.

```
cansend vcan0 <BCM_Command id>#<the eight bytes>
```

*  Do not reach for `python-can`. It is installed, but its socketcan interface wants a kernel network device and this bus is a unix socket, so it fails with `No such device`.

Get the command accepted and the flag goes out on the bus. Watch for it with `candump -a vcan0`!
