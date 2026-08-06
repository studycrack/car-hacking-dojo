You have subscribed, and you have written. This module needs both, in the right
order.

The keyless module answers a challenge on request: write to one characteristic
and it pushes the answer as a notification on another. The answer goes to
whoever is subscribed **at that instant**, and to nobody else. Write first and
the response is generated, pushed to an empty set of subscribers, and gone.
There is no queue.

You met this in the CAN module, when a fob transmitted once and a capture that
started afterwards found nothing.

One consequence decides what you can do this with: the answer goes back over
the connection that asked for it. Subscribing on one connection and writing
from another earns you the same silence, so whatever you use has to hold a
single connection open and do both through it.

Subscribe. Then write.
