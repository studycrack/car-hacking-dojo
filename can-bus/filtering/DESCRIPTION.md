A real bus carries thousands of frames a second across dozens of identifiers.
`candump` takes a filter, appended to the interface as `ID:MASK`. A frame is
shown when `received_id & MASK == ID & MASK`.

To see only `0x1C4`, match all eleven bits:

    candump vcan0,1C4:7FF

A looser mask matches a range: `candump vcan0,100:700` shows `0x100` to
`0x1FF`.

One controller here is leaking the flag on a single identifier. Find which ---
sorting a capture by identifier is one way, `candump vcan0 | awk` another ---
then filter it down.

The chunks arrive out of order. Each payload is seven bytes of text prefixed
with one byte giving the position that chunk belongs at. Put them back in
order.
