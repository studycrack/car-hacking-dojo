Every modern car is a small network. Dozens of computers --- the engine
controller, the transmission, the instrument cluster, the body control module
--- shout status updates at each other, continuously, over a shared pair of
wires called a **CAN bus**.

Two things make this bus interesting to an attacker:

- **Everything is broadcast.** There is no addressing in the way you know it
  from IP. Every controller sees every frame and decides for itself whether it
  cares.
- **Nothing is authenticated.** A frame does not say who sent it. It carries an
  11-bit *identifier* that describes what the frame *means*, and up to 8 bytes
  of data.

Your workspace has a CAN interface named `vcan0` attached to this car. Listen
to it:

    candump vcan0

Frames will scroll past. Each line shows the interface, the identifier in hex,
the payload length in brackets, and the payload bytes:

     vcan0  0C0   [8]  0B 54 00 00 27 10 00 00

Most of that traffic is the engine reporting on itself. But one controller on
this bus is chattier than it should be, and is broadcasting text. Add the `-a`
flag to render each payload as ascii alongside the hex:

    candump -a vcan0

Read the flag off the wire.
