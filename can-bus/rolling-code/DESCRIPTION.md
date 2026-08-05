The key fob you captured earlier was a toy. Real ones have not sent a fixed
code since the early nineties, because a fixed code is a recording away from a
stolen car.

What replaced it is the **rolling code**. The fob and the receiver share a
secret and a counter. Each press sends the counter along with a value derived
from it, the receiver checks the derivation, and then --- the part that matters
--- refuses to ever accept that counter or anything below it again. Record a
press and play it back and the receiver ignores you, because by then it has
moved on.

This car works that way. Press the button and watch:

    /challenge/press-fob

The body control module reports itself on `0x19A`: byte 0 is `01` while locked,
byte 1 counts unlocks, and byte 2 is what it made of the last fob frame it
looked at --- `01` unlocked, `02` counter already used, `03` code did not match.
Capture a press, replay it, and you can watch it be refused. That is the
countermeasure working exactly as designed.

Now look more carefully at what one press actually puts on the wire.

A fob does not transmit once. Radio is lossy and the button is a moment of
inattention, so a press sends the same intent several times over, each with its
own counter value. The receiver acts on the first one it manages to decode ---
and then, having just unlocked the car, stops paying attention for a moment so
that the rest of the burst does not toggle the doors back and forth.

Which means the remainder of that burst was never consumed. Those counters have
never been used, they are still ahead of where the receiver stopped, and you
have a recording of them.

Capture a press, work out what you are holding, and open the car with a code
the owner never spent.
