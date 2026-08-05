Enumerate the dongle and its debug characteristic reads `debug channel idle`.
Its declaration says `READ`. No notify property, so there is nothing to
subscribe to, and a tool that builds its interface from the declaration will
not even offer you the option.

Look at the attribute table instead of the characteristic list.

There is a `0x2902` sitting under that characteristic. A CCCD exists to switch
pushes on, and it has no business being there at all if the characteristic
cannot push.

The properties byte in a declaration is a **statement of intent by the
firmware**, not a permission the stack enforces. It tells a well-behaved client
what to expect. Nothing consults it when a write to the CCCD arrives, and
nothing consults it when the firmware decides to push. Somebody built this
device, disabled the notify property to tidy up the interface, and left the
code path that does the notifying exactly where it was.

Write to the descriptor that should not matter, and listen.
