Listening is only half of it. Because a CAN frame carries no evidence of who
sent it, any controller that can reach the bus can *originate* any message on
it. If the body control module unlocks the doors when it sees a particular
frame, it does not --- and cannot --- care whether that frame came from the key
fob receiver or from you.

`cansend` puts a frame on the bus, using the same notation `candump` prints:

    cansend vcan0 19B#0200ABCD

That is identifier `0x19B` carrying the four bytes `02 00 AB CD`.

This car's body control module speaks the following (this is the kind of thing
you would recover from a leaked DBC file, or from a firmware dump):

| Identifier | Direction | Layout |
| --- | --- | --- |
| `0x19A` | BCM broadcast | byte 0: `01` locked / `00` unlocked. bytes 2-3: current session counter, big endian. |
| `0x19B` | BCM receive | byte 0: `02` to unlock. byte 1: `FF` for all doors. bytes 2-3: the session counter the BCM is currently advertising. |

That session counter is the entire extent of this car's security, and it is
broadcast in the clear on the very bus you are attacking. It is rotated every
fifteen seconds, so read it, then act on it.

Unlock the doors, and the BCM will be pleased enough to tell you the flag.
