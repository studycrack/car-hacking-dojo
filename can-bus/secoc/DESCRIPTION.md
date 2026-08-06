**SecOC** puts a message authentication code on the frames that matter. Sender
and receiver share a key; each transmission carries the payload, a **freshness
value** that must never go backwards, and a truncated MAC.

Doors are commanded on `0x1B0`: two bytes of payload, one of freshness, three
of MAC. The controller reports itself on `0x1B1` --- byte 0 locked, byte 1 the
freshness it last accepted, byte 2 what it made of the last frame: `01`
accepted, `02` MAC did not verify, `03` freshness was not ahead.

The car locks itself periodically, and the fob still works:

    /challenge/press-fob

You cannot compute a MAC without the key. Attack what it was computed over
instead: a MAC is only a promise about the bytes that went into it, and any
field left out is one you are free to change.

Watch the car lock itself several times. The payload is identical each time and
the freshness is not. Look at what the MAC does.

Then unlock a car whose owner never asked you to.
