A CAN frame is not a message waiting in a queue. Whoever was listening at that
instant heard it; for everyone else it never happened. A key fob transmits
**once** per press.

Press the button:

    /challenge/press-fob

The burst it triggers carries the flag in plain ascii, so the order of your
commands is the whole challenge:

- Start your capture, in another terminal or backgrounded with `&`.
- *Then* press the button.

Press first and you get an empty capture. There is no penalty and no limit on
presses --- set the capture up and press again.

Every remaining challenge assumes you are already listening when you act.
