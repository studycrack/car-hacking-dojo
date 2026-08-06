A notification is fire and forget. ATT has a second push for anything that
matters: the **indication**, which the client must acknowledge with a Handle
Value Confirmation before the peripheral will send another. One outstanding at
a time, acknowledged, in order.

This immobiliser keeps its audit log that way. Two things follow, and both are
the challenge.

Subscribing for notifications on a characteristic that only indicates achieves
nothing --- the CCCD value has to match what the characteristic actually does.
`0x0001` is not `0x0002`.

And once records start arriving they stop after the first unless you confirm
it. A client that listens without answering gets exactly one record and waits
forever for the rest.

Collect the whole log.
