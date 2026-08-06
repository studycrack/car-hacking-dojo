A CAN frame carries no evidence of who sent it, so any controller that can
reach the bus can originate any message on it.

`cansend` puts a frame on the bus, in the notation `candump` prints:

    cansend vcan0 19B#0200ABCD

That is identifier `0x19B` carrying `02 00 AB CD`.

This car's body control module speaks the following:

| Identifier | Direction | Layout |
| --- | --- | --- |
| `0x19A` | BCM broadcast | byte 0: `01` locked / `00` unlocked. bytes 2-3: current session counter, big endian. |
| `0x19B` | BCM receive | byte 0: `02` to unlock. byte 1: `FF` for all doors. bytes 2-3: the session counter the BCM is currently advertising. |

The session counter is broadcast in the clear and rotates every thirty seconds,
so read it, then act on it.

Unlock the doors and the BCM announces the flag on the bus. Keep a `candump`
running in a second terminal while you work.
