A single write opened the vault. Anything that matters is usually guarded by
more than one.

This is the immobiliser. It expects a **sequence**: several writes, in a
specific order, and it counts.

Its status characteristic tells you where in that sequence it believes it is.
Read it after each write and you can watch the state machine move --- you are
not guessing, you are writing, observing, and letting the peripheral tell you
whether that step counted.

Get a step wrong and it resets to the beginning. An interlock that forgives a
wrong step would let you brute force each position independently while the
earlier ones stayed satisfied.

The workshop manual extract in the attribute table says what the steps are.
Drive it to the end.
