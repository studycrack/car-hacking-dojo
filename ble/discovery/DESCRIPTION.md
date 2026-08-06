Somebody left a dongle in this car's OBD-II port, bridged straight onto the
diagnostic bus you spent the last two modules attacking. It also speaks
Bluetooth, because that is how it talks to the phone app.

Find it. A peripheral that wants to be connected to *advertises*:

    hcitool lescan

Now connect and look at what it exposes. BLE's data model, **GATT**, is a flat
table of attributes. Services group them, characteristics hold the values, and
every one has a 16-bit handle:

    gatttool -b <address> --primary
    gatttool -b <address> --characteristics

The `--characteristics` listing gives you, for each one, the handle of its
*declaration* and separately the handle of its *value*. Those are different
attributes: reading the declaration gets you the properties, not the data. The
value handle is the one you read from.

    gatttool -b <address> --char-read -a <value handle>

Nothing here asks for a key, a pairing, or a password. Enumerate the table,
read what is readable, and one of those characteristics is holding something
the manufacturer would rather it did not.
