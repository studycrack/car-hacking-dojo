Real fobs have not sent a fixed code since the early nineties: a fixed code is
a recording away from a stolen car.

What replaced it is the **rolling code**. The fob and the receiver share a
secret and a counter. Each press sends the counter along with a value derived
from it, the receiver checks the derivation, and then refuses to ever accept
that counter or anything below it again. Record a press, play it back, and the
receiver ignores you.

This car works that way. Press the button and watch:

    /challenge/press-fob

The body control module reports itself on `0x19A`: byte 0 is `01` while locked,
byte 1 counts unlocks, and byte 2 is what it made of the last fob frame it
looked at --- `01` unlocked, `02` counter already used, `03` code did not match.
Replay a captured press and you can watch it refused.

Now look at what one press actually puts on the wire. A fob does not transmit
once: radio is lossy, so a press sends the same intent several times, each with
its own counter. The receiver acts on the first one it decodes and then stops
listening for a moment, so the doors do not toggle back and forth. The rest of
that burst was never consumed --- those counters are unspent, still ahead of
where the receiver stopped, and you have a recording of them.

Capture a press, work out what you are holding, and open the car with a code
the owner never spent.

Opening it is not the whole thing. Any valid unspent code will let you in,
including one you watched go past a heartbeat ago, and that proves nothing:
the owner pressing the button looks the same. What you are demonstrating is a
*replay*, something recorded earlier still opening the car long after the
moment it belonged to. So let the capture sit for several seconds before you
send it. Unlock too quickly and the doors open and nothing else happens.

`candump -l vcan0` writes what it sees to a log file, and
`canplayer -I <logfile>` puts it back on the bus.

Do not replay the whole capture. Your log holds everything that crossed the bus
while it ran, including the frame that pressed the button --- replaying that
presses the fob again, which spends fresh codes and leaves the receiver's
counter *past* everything you recorded. Cut the log down to the one frame you
mean to send, then play that.
