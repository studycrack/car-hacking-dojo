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

Hints:
*  Skip the lines whose ascii column is all dots. Those are sensor values.
*  Watch for a while. The controller only transmits every two seconds.
*  Do not stop at one line. The flag goes out eight bytes at a time, on the same identifier, back to back.

The text running down the ascii column is the flag!
