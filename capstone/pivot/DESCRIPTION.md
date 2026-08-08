# Using a Bluetooth Dongle as a Bridge to Another Bus (Pivot)

The goal of this stage is as follows:
*  The immobiliser you are after is on the powertrain bus, and you are not on it.
*  There is no gateway routing table to abuse this time either. Try `candump vcan0` and it stops at `bind: Permission denied`.
*  What there is instead is a Bluetooth dongle in the OBD-II port. It is on the bus, because that is what it is for, and it is on the air, because it has an app to talk to.
*  So it is a bridge, and a bridge can be crossed in either direction.
*  You need to put frames on that bus through the dongle and run routine `0xC001` on the immobiliser.

Task:
*  Enumerate the dongle and find how the bus is exposed.
   *  one characteristic that **writes** frames
   *  one that pushes the frames it hears as **notifications**
*  **Subscribe to the notifications first**, for the same reason as in `trigger`.
*  Write frames on the same connection, in the notation you have been reading all along. `gatttool` cannot hold a subscription and write at the same time, so use the client in `/challenge/ble.py`, as in `trigger`.

```
6F2#0322F19000000000
```

*  Once across, it is the previous two modules again. Segment with ISO-TP and get into the right session.
*  Run the routine.

```
31 01 C0 01
```

The routine's response comes back as a notification, and the flag is in it!
