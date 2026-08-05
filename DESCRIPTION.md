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

And then off the wire entirely, to the Bluetooth the car answers on: the phone
that unlocks it, the tyre sensors, the aftermarket dongle somebody left in the
OBD-II port --- which is bridged onto the very bus you spent the first two
modules attacking. The last challenge is that bridge.

Everything here is a simulation. Your workspace has a virtual CAN interface,
`vcan0`, and peripherals advertising over a virtual radio, both attached to a
simulated vehicle. What is simulated is the wire and the air; the tools, the
frame formats, the protocols and the attacks are the real ones.

## Where to start

The modules are grouped by interface, not by difficulty, because within each one
the challenges build on each other --- the rolling code challenge assumes the
capture discipline the one before it teaches, and the checksum challenge assumes
the signal reverse engineering from the one before that. Work down a module and
the ramp is already there.

What follows is the other view: the same thirty-four challenges sorted by what
they ask of you, so you can judge where to begin and what you are in for.

**Following an instruction.** The description tells you the command. Run it, and
watch what a bus or a peripheral hands over to anyone who asks.

> `sniffing` · `discovery` · `descriptors` · `encoding` · `notify` · `beacon`

**Combining two things.** Read something, then use it: a session counter that
rotates, an index that says which fragment goes where, a subscription that has
to exist before you trigger the thing you want to hear.

> `filtering` · `fob-capture` · `injection` · `fragments` · `unlock` ·
> `sequence` · `stream` · `indicate` · `trigger` · `service-data` ·
> `scan-response` · `long-write` · `dbc`

**Finding what nobody told you.** A handle that is missing from the discovery
response but answers anyway. A service in no specification. A signal whose
scale factor is yours to work out.

> `hidden-notify` · `hidden-handles` · `ecu-discovery` · `fault-memory` ·
> `iso-tp` · `firmware-dump` · `spoofing` · `odometer` · `gateway` ·
> `rolling-code`

**Defeating something built to stop you.** These have a real defence in front of
them, and it is not there for show: an alive counter and a checksum, an attempt
limiter, a message authentication code you cannot forge. You get past them by
understanding exactly what each one covers, and going at what it does not.

> `integrity` · `security-access` · `reflash` · `secoc` · `pivot`

If you are new to this, `sniffing` is the first challenge of the first module
and asks nothing of you but curiosity. If you have done bus work before, start
at `spoofing` or `iso-tp` and come back for anything that turns out to be
unfamiliar.
