Somebody left a dongle in this car's OBD-II port. Half the fleet vehicles on
the road have one --- insurance telematics, a fuel-card logger, a workshop tool
nobody took back out --- and it is bridged straight onto the diagnostic bus you
spent the last two modules attacking. It also speaks Bluetooth, because that is
how it talks to the phone app.

Start by finding it. A peripheral that wants to be connected to *advertises*:

    hcitool lescan

That is all it takes. The device is broadcasting itself to the street, and it
will answer a scan from anyone in range --- no pairing, no key, nobody asked
for permission.

Now connect and look at what it exposes. BLE's data model, **GATT**, is a flat
table of attributes. Services group them, characteristics hold the values, and
every one has a 16-bit handle:

    gatttool -b <address> --primary
    gatttool -b <address> --characteristics

The `--characteristics` listing gives you, for each one, the handle of its
*declaration* and separately the handle of its *value*. Those are different
attributes and it matters: reading the declaration gets you the properties, not
the data. The value handle is the one you read from.

    gatttool -b <address> --char-read -a <value handle>

Values come back as hex bytes, because a characteristic holds bytes and the
protocol has no opinion about what they mean.

Nothing here asked you for a key, a pairing, or a password. Enumerate the
table, read what is readable, and one of those characteristics is holding
something the dongle's manufacturer would rather it did not.
