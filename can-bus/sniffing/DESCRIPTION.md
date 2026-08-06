Your workspace has a CAN interface, `vcan0`, attached to a running car. Every
controller sees every frame. A frame carries an 11-bit *identifier* saying what
it means, and up to 8 bytes of data.

Listen:

    candump vcan0

Each line is the interface, the identifier in hex, the payload length, then the
bytes:

     vcan0  0C0   [8]  0B 54 00 00 27 10 00 00

One controller is broadcasting text. `-a` renders each payload as ascii
alongside the hex:

    candump -a vcan0

Read the flag off the wire.
