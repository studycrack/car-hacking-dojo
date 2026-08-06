You have subscribed, and you have written. This module needs both, in the right
order, and it is the order that catches people.

The keyless module answers a challenge on request: write to one characteristic,
and it pushes the answer as a notification on another. Straightforward --- until
you notice that the answer goes to whoever is subscribed **at that instant**,
and to nobody else.

Write first and the response is generated, pushed to the empty set of
subscribers, and gone. There is no queue. A notification is not mail; it is
something said out loud in a room, and if you were not in the room you did not
hear it.

You met this in the CAN module, when a fob transmitted once and a capture that
started afterwards found nothing. It is the same lesson with different wires,
and it is worth learning twice, because it is the single most common way to
sit in front of a working attack and conclude that it does not work.

One consequence is worth spelling out, because it decides what you can do this
with. The answer goes back over the connection that asked for it. Subscribing
on one connection and writing from another earns you the same silence, for the
same reason --- so whatever you use has to hold a single connection open and do
both things through it.

Subscribe. Then write.
