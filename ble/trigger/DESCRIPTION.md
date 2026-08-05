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

Subscribe. Then write.
