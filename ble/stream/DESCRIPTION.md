A notification carries at most twenty bytes. The opcode and the handle take
three of the twenty-three an ATT PDU has, and that is the whole budget.

So anything longer arrives as a stream, and the telematics unit's journey log
is longer. Subscribe and the fragments come at you as fast as the peripheral
can push them.

They do not come in order.

There is no sequencing in ATT itself --- a notification is a handle and some
bytes, and the protocol has no concept of one arriving before another. If a
peripheral wants a client to be able to reassemble something, it has to put the
ordering *in the payload*, which is what this one does: the first byte of every
fragment is its position.

Collect them all, sort by that byte, and drop it before you join the rest.
