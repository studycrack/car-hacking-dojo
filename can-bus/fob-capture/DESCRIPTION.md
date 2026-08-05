Everything you have captured so far has been patient with you. The engine
controller repeats itself ten times a second; the telemetry leak cycles round
and round. You could start `candump` whenever you felt like it and the traffic
would still be there.

Almost nothing that matters works that way.

A CAN frame is not a message sitting in a queue waiting to be collected. It is
a few hundred microseconds of voltage on a pair of wires. Every controller that
was listening at that instant heard it, and for everyone else it never
happened. When a key fob authenticates, when an immobilizer answers, when a
crash sensor fires --- those go out **once**, and if your capture was not
already running, that data is gone. Not delayed. Gone.

This car's key fob is on the bus. Press its button:

    /challenge/press-fob

Somewhere in the burst it triggers is the flag, in plain ascii. But the fob
transmits exactly once per press, so the order of your commands is now the
entire challenge:

- Start your capture. Put it in another terminal, or background it with `&`.
- *Then* press the button.

Press first and read second, and you will find a perfectly empty capture ---
which is exactly the failure this challenge exists to teach you. There is no
penalty for it, and no limit on presses. Set your capture up properly and press
again.

Get into this habit now. Every remaining challenge in this dojo assumes you are
already listening when you act, and the real ones will not tell you when you
have missed something.
