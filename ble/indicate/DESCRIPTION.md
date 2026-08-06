# Confirming Each Indication to Receive the Whole Log (Indicate)

The goal of this stage is as follows:
*  A notification is fire and forget. The peripheral pushes it and moves on, and if it never arrived, nobody finds out.
*  For anything that matters that is the wrong trade, so ATT has a second push: the **indication**, which the client must acknowledge with a Handle Value Confirmation before the peripheral sends another.
*  One outstanding at a time, acknowledged, in order.
*  This immobiliser keeps an audit log that way.
*  You need to subscribe with the value indications require, and confirm every record, until you have the whole log.

Task:
*  Find the characteristic's CCCD.
*  Subscribe with **the value that means indications**. `0x0001` is not `0x0002`.
*  Confirm each record as it arrives and keep going to the end.

```
import sys
sys.path.insert(0, "/challenge")
import ble

client = ble.Client("<address>")
client.subscribe(<cccd handle>)
for handle, value in client.events_stream(timeout=5):
    print(hex(handle), value)
```

*  Join the records in order.

Hints:
*  Match the CCCD value to what the characteristic actually does. Subscribing for notifications on something that only indicates achieves nothing.
*  Do not just listen. Without a confirmation you get exactly one record and wait forever for the rest.
*  Use the client in `/challenge/ble.py`, which sends the confirmations for you.
*  If you want `bleak`, run it with `/usr/bin/python3`.

Collect the whole log and you have the flag!
