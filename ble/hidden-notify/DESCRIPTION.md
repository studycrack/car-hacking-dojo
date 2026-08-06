Enumerate the dongle and its debug characteristic reads `debug channel idle`.
Its declaration says `READ` --- no notify property, so a tool that builds its
interface from the declaration will not offer you the option.

Look at the attribute table instead of the characteristic list. There is a
`0x2902` sitting under that characteristic, and a CCCD has no business being
there if the characteristic cannot push.

The properties byte is a **statement of intent by the firmware**, not a
permission the stack enforces. Nothing consults it when a write to the CCCD
arrives, and nothing consults it when the firmware decides to push. Somebody
disabled the notify property to tidy up the interface and left the code path
that does the notifying where it was.

Write to the descriptor that should not matter, and listen.
