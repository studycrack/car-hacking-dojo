The tyre pressure gateway collects from all five sensors --- four wheels and the
spare --- and keeps a service per sensor. Somewhere across those five services
is a record split into five pieces.

Enumerate and you will find, for each sensor, three characteristics: a signal
strength, an index, and a payload. The payload is a fragment of the record. The
index says which fragment it is.

Read them in handle order and you get nonsense, because **handle order is not
record order**. Handles are assigned when the firmware builds its attribute
table, in whatever sequence the code declared them; they carry no meaning
beyond position in the table. The index characteristic is the only thing that
says how the pieces fit together, which is precisely why it exists.

This is the ordinary shape of real BLE data. Anything longer than a
characteristic conveniently holds gets spread out, and the reassembly rule is
somewhere in the table with it. Find the rule, then apply it.
