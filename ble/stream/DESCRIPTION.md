# Reassembling Notifications That Arrive Out of Order (Stream)

The goal of this stage is as follows:
*  A notification carries at most twenty bytes: the ATT PDU is twenty-three and the opcode and handle take three.
*  Anything longer arrives in fragments, and this telematics unit's trip log is longer.
*  Subscribe and the fragments pour in as fast as the peripheral can push them, and **they do not arrive in order**.
*  ATT has no notion of ordering, so the peripheral has to put the order **inside the payload**. This one spends the first byte of each fragment on its position.
*  You need to collect them all and put them back in order.

Task:
*  Find the characteristic's CCCD and subscribe.
*  Collect fragments until no more arrive.

```
import sys
sys.path.insert(0, "/challenge")
import ble

client = ble.Client("<address>")
client.subscribe(<cccd handle>)
chunks = [value for handle, value in client.events_stream(timeout=5)]
```

*  Sort what you collected by that first byte.
*  **Strip the position byte before you join.**

Hints:
*  Do not join in arrival order. The protocol does not care what came first.
*  Do not leave the position byte in. It shows up as stray characters between fragments.
*  Check the fragment numbers are contiguous. A gap means you have not received them all.

Join the fragments in order and you have the flag!
