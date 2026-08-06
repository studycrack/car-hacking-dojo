The immobiliser you want is on the powertrain bus. You are not on it, and this
time there is no gateway routing table to abuse --- try `candump vcan0` and the
kernel will tell you how welcome you are.

What you have is the Bluetooth dongle in the OBD-II port. It is on the bus,
because that is its purpose, and on the air, because that is how it talks to
its phone app. It is a bridge, and a bridge works in both directions.

Enumerate it and you will find the bus exposed as two characteristics: one you
write frames to, one that notifies you of frames it hears. Frames cross in the
notation you have been reading all along:

    6F2#0322F19000000000

Once frames cross, everything from the other two modules still applies ---
ISO-TP still segments, UDS still needs the right session, and the immobiliser
still runs routine `0xC001` for anyone who can reach it.

Subscribe before you transmit.
