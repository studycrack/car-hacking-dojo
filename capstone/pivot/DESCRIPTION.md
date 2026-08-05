Everything up to here has been one interface at a time. This is what the job
actually looks like.

The immobiliser you want is on the powertrain bus. You are not on the
powertrain bus, and this time there is no gateway routing table to abuse ---
try `candump vcan0` and the kernel will tell you exactly how welcome you are.

What you do have is a Bluetooth dongle in the OBD-II port. Somebody plugged it
in for insurance telematics or fuel logging and forgot it. It is on the bus,
because that is its whole purpose, and it is on the air, because that is how it
talks to its phone app.

It is a bridge. It was built to be a bridge. Nobody involved in building it
considered that a bridge works in both directions.

Enumerate it and you will find it exposes the bus as two characteristics: one
you write frames to, one that notifies you of frames it hears. Frames go across
in the notation you have been reading all along:

    6F2#0322F19000000000

That is the whole pivot. Once frames cross, everything you learned in the other
two modules still applies --- ISO-TP still segments, UDS still needs the right
session, and the immobiliser still runs routine `0xC001` for anyone who can
reach it. Nothing about those protocols knows or cares that its transport is
now a radio link and somebody's forgotten dongle.

Subscribe before you transmit. You know why by now.
