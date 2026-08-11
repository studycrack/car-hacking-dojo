# Eavesdropping on the CAN Bus (Sniffing)

The goal of this stage is as follows:
*  Every controller sees every frame, so listening costs nothing more than attaching to the bus.
*  One controller is broadcasting the flag as ascii text, eight bytes at a time.
*  Nothing marks those frames as different from the rest of the traffic.
*  You need to find that identifier and read the text across its frames.

Task:
*  Listen to the frames on the bus.

```
candump vcan0
```

*  Read the output format: interface, identifier, payload length, then the bytes.

```
vcan0  0C0   [8]  0B 54 00 00 27 10 00 00
```

*  Add `-a` to render each payload as ascii alongside the hex.

```
candump -a vcan0
```

*  Find the identifier whose ascii column shows readable text.

The text running down the ascii column is the flag!
