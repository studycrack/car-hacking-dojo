A single write opened the vault. Anything that matters is usually guarded
by more than a single write.

This is the immobiliser. It will not disarm on one command, because a stray
byte on a radio interface should never be able to disarm an immobiliser. It
expects a **sequence**: several writes, in a specific order, and it counts.

Its status characteristic tells you where in that sequence it currently
believes it is. Read it after each write and you can watch the state machine
move --- which is the whole technique here. You are not guessing; you are
writing, observing, and letting the peripheral tell you whether that step
counted.

Get a step wrong and it does not simply ignore you. It resets to the
beginning, because an interlock that forgives a wrong step is not an interlock
--- it would let you brute force each position independently while the earlier
ones stayed satisfied. You start over.

The workshop manual extract in the attribute table says what the steps are.
Drive it to the end.
