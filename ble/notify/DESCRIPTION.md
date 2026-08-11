The goal of this stage is as follows:
*  So far you asked and the peripheral answered. Sensors do not want to work that way.
*  BLE's answer is the **notification**: a PDU the peripheral pushes without being asked.
*  It sends nothing until you turn it on. A characteristic that can notify has a CCCD next to it, UUID `0x2902`, and it is an ordinary writable attribute.

```
write 0x0001 to enable notifications
write 0x0002 to enable indications
```

*  It defaults to off, and the setting is remembered per connection.
*  What this one has to say does not fit in a single PDU, so it arrives in several.
*  You need to turn the CCCD on and listen until it is done.

Task:
*  Find the CCCD handle in the attribute table. It is the row with UUID `0x2902`.

```
gatttool -b <address> --char-desc
```

*  Write `0100` to it and stay connected, listening.

```
gatttool -b <address> --char-write-req -a <cccd handle> -n 0100 --listen
```

*  Collect the notifications and join them in order.

Join the notifications and you have the flag!
