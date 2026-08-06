# Reading a Gateway's Routing Table to Reach Another Bus (Gateway)

The goal of this stage is as follows:
*  A real vehicle has several buses, deliberately kept apart, with a **central gateway** between them forwarding only what has to cross.
*  The OBD-II connector is on the gateway's diagnostic side. It is not on the powertrain bus.
*  This workspace has two interfaces.

```
ls -l /run/vcan/
```

*  The connector reaches `vcan0`. Try to listen on `vcan1` and you are told you are not on that bus.
*  So you attack the thing joining the buses rather than the bus itself.
*  You need to learn which identifiers the gateway forwards to the powertrain side, and use that path to run routine `0xC001` on the immobiliser.

Task:
*  Find the gateway on the diagnostic bus. It answers like any other controller, so enumerate it the way you already know.
*  Sweep its identification records and read the routing table.
*  Pick the entry in the forwarded list that does not look like a diagnostic address.
*  Send a UDS request to the immobiliser on that identifier and run the routine.

```
31 01 C0 01
```

Hints:
*  Read the list carefully. Three are ordinary diagnostic addresses; one is in a range you would never have thought to sweep.
*  Do not expect the routing table to be defensible. It was written once during development and copied forward every model year, and it is almost never audited.
*  Apply the same eight-above rule for response addresses on the far side.
*  Do not go looking for authentication. The immobiliser runs `0xC001` for anything that can reach it.

Run the routine and its response carries the flag!
