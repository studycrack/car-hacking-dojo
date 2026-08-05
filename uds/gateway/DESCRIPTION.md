Everything so far has assumed one bus, with everything on it. No manufacturer
builds a car that way, and has not for twenty years.

A modern vehicle has several buses --- powertrain, chassis, comfort,
infotainment --- kept apart on purpose, because the parts that can stop the car
should not share a wire with the parts that play music. A **central gateway**
sits between them and moves the specific messages that genuinely need to cross.
The OBD-II connector under the dashboard is on the diagnostic side of that
gateway. It is not on the powertrain bus, and no amount of cleverness with
`cansend` will put you there.

Your workspace has two interfaces this time:

    ls -l /run/vcan/

`vcan0` is what the connector reaches. Try to listen to `vcan1` and you will be
told, correctly, that you are not on that bus --- because in the car you are
sitting in, that pair of wires runs to the engine bay and nowhere near you.

So you do not attack the bus. You attack the thing that bridges it.

A gateway must be told which identifiers to carry across, and that routing
table is configuration --- written once during development, copied between
model years, and rarely audited. Service tools need routes that production
cars do not, and a route that exists is a route anyone can use.

Find the gateway on the diagnostic bus. It answers like any other controller,
and among its identification records is the list of identifiers it forwards
onto the powertrain bus. Read it, and read it carefully: three of those entries
are the ordinary diagnostic addresses you would expect. One is not, and it is
nowhere near the range you would have thought to scan.

Behind it is the immobilizer, which will happily run routine `0xC001` for
anyone who can reach it. The gateway is about to decide that you can.
