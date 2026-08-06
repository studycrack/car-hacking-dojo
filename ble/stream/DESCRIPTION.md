A notification carries at most twenty bytes: an ATT PDU is twenty-three, and
the opcode and handle take three of them.

So anything longer arrives as a stream, and the telematics unit's journey log
is longer. Subscribe and the fragments come as fast as the peripheral can push
them.

They do not come in order. There is no sequencing in ATT --- a notification is
a handle and some bytes. A peripheral that wants its client to reassemble
something has to put the ordering *in the payload*, which is what this one
does: the first byte of every fragment is its position.

Collect them all, sort by that byte, and drop it before you join the rest.
