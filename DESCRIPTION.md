A car is a network on wheels.

The engine controller, the transmission, the anti-lock brakes, the airbags, the
instrument cluster, the door modules --- a hundred million lines of code across
dozens of computers, wired together by a bus designed in 1986 for a world where
nobody could plug anything into it. That bus has no addressing, no
authentication, and no encryption. Any node that can reach the wire can say
anything to any other node, as anyone.

For most of automotive history that was fine, because reaching the wire meant
being inside the car with a soldering iron. Then cars got Bluetooth, and
cellular modems, and app stores, and in 2015 Charlie Miller and Chris Valasek
drove a Jeep off the road from ten miles away through its entertainment system.
The wire is reachable now.

This dojo puts you on that wire.

You will start by listening to a running vehicle and learning to read what its
controllers say to one another. You will forge frames and watch modules obey
them. You will reverse engineer the message layout of a car nobody handed you a
specification for. And then you will move up the stack to **UDS**, the
diagnostic protocol that dealer tools use to reprogram controllers, enumerate
the computers that answer on the bus, and defeat the authentication that stands
between a diagnostic session and the parts of an ECU that were never meant to
be reachable from the OBD-II port.

Everything here is a simulation --- your workspace has a virtual CAN interface,
`vcan0`, attached to a simulated vehicle. The tools, the frame formats, the
protocols, and the attacks are the real ones.
