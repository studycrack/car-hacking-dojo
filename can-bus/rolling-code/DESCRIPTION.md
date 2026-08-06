A **rolling code** fob and its receiver share a secret and a counter. Each press
sends the counter plus a value derived from it; the receiver checks the
derivation, then refuses that counter and anything below it ever again.

    /challenge/press-fob

The body control module reports on `0x19A`: byte 0 is `01` while locked, byte 1
counts unlocks, byte 2 is what it made of the last fob frame --- `01` unlocked,
`02` counter already used, `03` code did not match.

A fob does not transmit once. Radio is lossy, so a press sends the same intent
several times, each with its own counter. The receiver acts on the first it
decodes and then stops listening for a moment, so the doors do not toggle. The
rest of that burst was never consumed: those counters are unspent, still ahead
of where the receiver stopped, and you have a recording of them.

Open the car with a code the owner never spent.

Two things will otherwise cost you the flag:

- **Let the capture sit for several seconds before sending it.** Any valid
  unspent code opens the doors, including one you watched go past a moment ago,
  and that proves nothing. What you are demonstrating is a replay. Unlock too
  quickly and the doors open and nothing else happens.
- **Do not replay the whole log.** It holds the frame that pressed the button,
  and replaying that presses the fob again, spending fresh codes and leaving
  the receiver's counter past everything you recorded. Cut the log down to the
  one frame you mean to send.

`candump -l vcan0` writes what it sees to a log file; `canplayer -I <logfile>`
puts it back on the bus.
