# Eavesdropping on the CAN Bus (Sniffing)

The goal of this stage is as follows:
*  Your workspace has a virtual CAN interface, `vcan0`, attached to a running vehicle.
*  CAN is a broadcast bus, so every controller sees every frame.
*  A frame carries an 11-bit identifier and up to 8 bytes of data, and the identifier says what the frame means.
*  One controller is broadcasting the flag as ascii text.
*  You need to find that frame.

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
