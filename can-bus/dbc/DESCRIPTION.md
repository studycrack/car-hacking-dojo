A **DBC file** is how bus definitions are written down: one entry per message,
one line per signal, with start bit, width, byte order, scale factor and
offset. There is one in `/challenge/vehicle.dbc`.

Its comfort message is awkward by hand --- cabin temperature scaled by `0.5`
and offset by `-20`, a four-bit fan, and Motorola byte order, whose start bits
are counted in a way that catches out everyone who tries it freehand.

`cantools` reads DBC files and does the packing:

    cantools dump /challenge/vehicle.dbc

It is importable, with one wrinkle. `python3` here is the dojo's interpreter;
`cantools` is installed in the challenge image. Only one of them has it:

    /usr/bin/python3 -c 'import cantools; print(cantools.__version__)'

So write your script for that one:

    #!/usr/bin/python3
    import cantools
    db = cantools.database.load_file("/challenge/vehicle.dbc")
    message = db.get_message_by_name("BCM_Command")
    data = message.encode({...})

Command a cabin target of **30.5 degrees** with the vent fan at **11**, and put
that frame on the bus.
