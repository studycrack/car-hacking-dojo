Reading is half of GATT. A characteristic can be writable too, and a
peripheral that changes its behaviour when you write to it is a peripheral you
can operate rather than merely observe.

This is the body control module's Bluetooth side --- the part that decides
whether the doors open. Its vault characteristic reads `locked`, and will keep
reading `locked` no matter how many times you ask.

Writing takes the value as hex, because a characteristic holds bytes:

    gatttool -b <address> --char-write-req -a <handle> -n d34dbeef

The `-req` matters. A Write Request is acknowledged: the peripheral answers,
and you learn whether it worked. The alternative, Write Command, is fire and
forget --- faster, and silent about failure.

Try writing to the vault directly and the peripheral will tell you exactly what
it thinks of that. Attributes carry permissions, and the error you get back
names the one you violated.

So find what *is* writable, and find out what it wants. The installer who
commissioned this module left themselves a note in the attribute table, the
way installers do. You know how to read the parts of the table that are not
characteristic values.
