A modern vehicle has several buses kept apart on purpose, with a **central
gateway** between them moving only the messages that need to cross. The OBD-II
connector is on the diagnostic side of that gateway, not on the powertrain bus.

Your workspace has two interfaces this time:

    ls -l /run/vcan/

`vcan0` is what the connector reaches. Try to listen to `vcan1` and you will be
told you are not on that bus, because that pair of wires runs to the engine bay
and nowhere near you.

So you do not attack the bus. You attack the thing that bridges it.

A gateway is told which identifiers to carry across, and that routing table is
configuration: written once, copied between model years, rarely audited.

Find the gateway on the diagnostic bus. It answers like any other controller,
and among its identification records is the list of identifiers it forwards
onto the powertrain bus. Read it carefully --- three entries are the ordinary
diagnostic addresses you would expect, and one is nowhere near the range you
would have thought to scan.

Behind it is the immobilizer, which will run routine `0xC001` for anyone who
can reach it.
