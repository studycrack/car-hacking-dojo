A characteristic can be writable, and a peripheral that changes its behaviour
when you write to it is one you can operate rather than merely observe.

This is the body control module's Bluetooth side. Its vault characteristic
reads `locked`, and will keep reading `locked` no matter how many times you
ask.

Writing takes the value as hex:

    gatttool -b <address> --char-write-req -a <handle> -n d34dbeef

The `-req` matters. A Write Request is acknowledged, so you learn whether it
worked; the alternative, Write Command, is fire and forget.

Write to the vault directly and the peripheral will tell you what it thinks of
that --- attributes carry permissions, and the error names the one you
violated.

So find what *is* writable, and what it wants. The installer who commissioned
this module left themselves a note in the attribute table, and you know how to
read the parts of the table that are not characteristic values.
