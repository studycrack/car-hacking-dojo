# Finding a BLE Peripheral and Walking Its GATT Table (Discovery)

The goal of this stage is as follows:
*  Somebody plugged a dongle into this car's OBD-II port and forgot about it.
*  It is wired directly to the diagnostic bus you spent the last two modules attacking, and it also talks Bluetooth, because it has a phone app to answer.
*  BLE's data model is **GATT**: a flat table of attributes, grouped by services, with characteristics holding the values, each with a 16-bit handle.
*  This dongle asks for no pairing and no passphrase.
*  You need to connect, walk the attribute table, and find the value the manufacturer should not have left in it.

Task:
*  Find what is advertising and note its address.

```
hcitool lescan
```

*  Connect and see what it exposes.

```
gatttool -b <address> --primary
gatttool -b <address> --characteristics
```

*  Read every characteristic you can.

```
gatttool -b <address> --char-read -a <value handle>
```

Hints:
*  Separate the **declaration handle** from the **value handle** in the `--characteristics` output. They are different attributes.
*  Read the value handle. Reading a declaration gives you property information and no data.
*  Take the number in the `char value handle` column.
*  If you prefer a shell, `bluetoothctl` works the same way: `scan on`, then `connect`, then its `gatt` menu.

One of the values you read is the flag!
