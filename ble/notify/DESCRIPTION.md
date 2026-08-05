Everything you have done so far, you started. You asked; the peripheral
answered. That is fine for a value that sits still, and useless for a sensor.

A tyre pressure gateway does not want to be polled. It wants to speak when a
wheel reports, and be silent otherwise. BLE's answer is the **notification**: a
PDU the peripheral pushes to you, unasked, whenever it has something.

It will not push anything until you say so. Every notifying characteristic has
a **Client Characteristic Configuration Descriptor** --- UUID `0x2902`, one per
characteristic --- and it is a plain writable attribute:

    write 0x0001 to enable notifications
    write 0x0002 to enable indications

Notifications are off by default and the setting is remembered per connection,
which is why two phones can watch the same sensor differently.

You know how to find descriptors. Find this one, turn notifications on, and
then keep listening --- the peripheral speaks when it is ready, not when you
ask, and what it has to say is longer than one PDU will carry.
