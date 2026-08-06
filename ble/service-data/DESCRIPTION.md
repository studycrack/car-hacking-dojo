**Service Data**, AD type `0x16`, says *this data belongs to this service*. The
structure begins with the 16-bit service UUID, and the payload follows it:

    12 16 6f fd 00 70 77 6e ...
    ^  ^  ^^^^^ ^^^^^^^^^^^^^
    |  |  UUID  the actual data
    |  type 0x16
    length

A parser that treats the whole structure as data gets two bytes of UUID at the
front of every fragment. It will look almost right, which is worse than looking
wrong.

AD structures are **typed**, and each type has a layout. Knowing a payload is
Service Data tells you where its data starts.

This tracker cycles its fragments the way the beacon did. Read the type
correctly, strip what is not payload, and put the pieces in order.
