A car's controllers talk to each other over a bus with no addressing, no
authentication and no encryption. Any node that can reach the wire can say
anything to any other node, as anyone. Every attack here follows from that.

You will read a running vehicle's traffic, forge frames its modules obey, and
reverse engineer a message layout nobody handed you a specification for. Then
**UDS**, the diagnostic protocol dealer tools use, and the authentication
standing between a diagnostic session and the parts of an ECU that were never
meant to be reachable from the OBD-II port. Then the Bluetooth the car answers
on --- including the aftermarket dongle bridged onto the bus you spent the
first two modules attacking. The capstone is that bridge.

Everything here is a simulation. Your workspace has a virtual CAN interface,
`vcan0`, and peripherals advertising over a virtual radio, both attached to a
simulated vehicle. What is simulated is the wire and the air; the tools, the
frame formats, the protocols and the attacks are the real ones.

## Where to start

The modules are grouped by interface, not by difficulty, and within each one the
challenges build on each other. Work down a module and the ramp is already
there.

Below is the other view: the same thirty-four sorted by what they ask of you.

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
