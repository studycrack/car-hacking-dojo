Everything so far, you started: you asked, the peripheral answered. A sensor
does not want to be polled. BLE's answer is the **notification**, a PDU the
peripheral pushes to you unasked.

It will not push anything until you say so. Every notifying characteristic has
a **Client Characteristic Configuration Descriptor**, UUID `0x2902`, and it is
a plain writable attribute:

    write 0x0001 to enable notifications
    write 0x0002 to enable indications

Notifications are off by default and the setting is remembered per connection.

Find that descriptor, turn notifications on, and keep listening --- the
peripheral speaks when it is ready, and what it has to say is longer than one
PDU will carry.
