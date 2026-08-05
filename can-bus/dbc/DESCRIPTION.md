You reverse engineered a signal by hand in an earlier challenge: watch a needle,
find the bytes that move with it, work out the scale. That is what you do when
nobody will give you the database.

Sometimes somebody gives you the database.

A **DBC file** is the format the industry writes bus definitions in --- one
entry per message, one line per signal, with its start bit, width, byte order,
scale factor and offset. Every workshop tool reads them, every OEM has them,
and they leak constantly.

There is one in `/challenge/vehicle.dbc`. Read it.

Then look at the comfort message it describes and notice what decoding it by
hand would cost you: the cabin temperature is scaled by `0.5` and offset by
`-20`, the fan is four bits, and the byte order is Motorola --- big endian, with
start bits counted in a way that has caught out everyone who has ever tried it
freehand.

Do not do it freehand. `cantools` reads DBC files and does the packing for
you. It is on your path:

    cantools dump /challenge/vehicle.dbc

and it is importable, with one wrinkle worth understanding. `python3` in this
workspace is the dojo's own interpreter, shared by every challenge in every
dojo; `cantools` is installed in the challenge image, alongside the can-utils.
Those are two different interpreters, and only one of them has the library:

    /usr/bin/python3 -c 'import cantools; print(cantools.__version__)'

So write your script for that one:

    #!/usr/bin/python3
    import cantools
    db = cantools.database.load_file("/challenge/vehicle.dbc")
    message = db.get_message_by_name("BCM_Command")
    data = message.encode({...})

Command a cabin target of **30.5 degrees** with the vent fan at **11**, and put
that frame on the bus.
