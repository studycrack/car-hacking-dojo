Each wheel on this car has a tyre pressure sensor, and the modern ones do not
just talk to the receiver behind the wheel arch --- they advertise, so the
owner's phone app can show four pressures on a screen.

You already know how to walk a characteristic list. That list is not the whole
attribute table.

A characteristic is at minimum two attributes: a **declaration** saying what
properties it has and where its value lives, and the **value** itself. It may
also carry **descriptors** --- further attributes that annotate it. The common
one is the Characteristic User Description, UUID `0x2901`, which holds a
human-readable label. Firmware authors treat it as a comment field, which is
exactly why it is worth reading: comments get left in.

`--characteristics` will not show you descriptors, because they are not
characteristics. To see every attribute in the table, handle by handle, ask for
all of them:

    gatttool -b <address> --char-desc

You will get far more rows than the characteristic listing had. Some are the
declarations you already know about, some are values, and some are the
descriptors nobody thought anyone would look at.

Read them.
