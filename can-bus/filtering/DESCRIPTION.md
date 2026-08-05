A real car is far louder than the last challenge suggested. A mid-range sedan
puts something on the order of two thousand frames per second on its
powertrain bus, spread across dozens of identifiers. Scrolling past that with
your eyes is not analysis.

`candump` takes a filter, appended to the interface name as `ID:MASK`. A frame
is shown when `received_id & MASK == ID & MASK`. To see only identifier `0x1C4`,
match all eleven bits of the identifier:

    candump vcan0,1C4:7FF

A looser mask matches a range. `candump vcan0,100:700` shows every identifier
from `0x100` to `0x1FF`.

Somewhere in this car's noise, one controller is leaking the flag on a single
identifier. Find which one --- sorting a capture by identifier is one way,
`candump vcan0 | awk` is another --- and then filter it down.

You will find the leak is not quite readable when you do. The controller
transmits its chunks in whatever order they come off its internal queue, and
prefixes each payload with the position that chunk belongs at. Seven bytes of
text, one byte of ordering. Put them back in order.
