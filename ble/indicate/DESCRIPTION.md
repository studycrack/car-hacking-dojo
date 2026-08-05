A notification is fire and forget. The peripheral pushes it and moves on, and
if it never arrived, nobody finds out.

For anything that matters, that is the wrong trade. So ATT has a second push:
the **indication**, which the client must acknowledge with a Handle Value
Confirmation before the peripheral will send another. One outstanding at a
time, acknowledged, in order.

This immobiliser keeps an audit log that way, on the reasoning that a record
the phone never received is a record that did not reach anyone.

Two things follow, and both are the challenge.

Subscribing for notifications on a characteristic that only indicates achieves
nothing --- the CCCD value you write has to match what the characteristic
actually does. `0x0001` is not `0x0002`.

And once records start arriving, they stop after the first unless you confirm
it. A client that listens without answering gets exactly one record and waits
forever for the rest, which is precisely the property the mechanism exists to
provide.

Collect the whole log.
