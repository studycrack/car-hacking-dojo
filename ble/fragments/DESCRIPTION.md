The tyre pressure gateway keeps a service per sensor --- four wheels and the
spare. Across those five services is a record split into five pieces.

Enumerate and you will find, for each sensor, three characteristics: a signal
strength, an index, and a payload. The payload is a fragment; the index says
which fragment it is.

Read them in handle order and you get nonsense, because **handle order is not
record order**. Handles are assigned when the firmware builds its attribute
table, in whatever sequence the code declared them, and carry no meaning beyond
position. The index characteristic is the only thing that says how the pieces
fit together.

Find the rule, then apply it.
