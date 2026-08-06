# Building a Signal From a DBC File (DBC)

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
*  Encode the values with `cantools`, which does the bit packing for you.

```
#!/usr/bin/python3
import cantools
db = cantools.database.load_file("/challenge/vehicle.dbc")
message = db.get_message_by_name("BCM_Command")
data = message.encode({...})
```

*  Transmit the encoded eight bytes on the `BCM_Command` identifier.

Hints:
*  Run it with `/usr/bin/python3`. There are two interpreters on this machine and `cantools` is installed in the challenge image one.

```
/usr/bin/python3 -c 'import cantools; print(cantools.__version__)'
```

*  Start your script with `#!/usr/bin/python3`.
*  Fill in every signal name `cantools dump` lists. `message.encode` requires the ones you do not care about too.
*  Do not pack the bits by hand. Motorola ordering is easy to get wrong. Let the library do it.

Get the command accepted and the flag goes out on the bus. Watch for it with `candump -a vcan0`!
