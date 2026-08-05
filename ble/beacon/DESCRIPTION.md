Every peripheral you have attacked so far, you connected to. This one you do
not have to.

A device that wants to be found **advertises**: it broadcasts a payload, over
and over, to nobody in particular. Anyone within range hears it. There is no
connection, no handshake, and nothing in the peripheral that could tell you
were listening.

The payload is a sequence of **AD structures**, each one a length byte, a type
byte, and its data:

    02 01 06        length 2, type 0x01 (Flags), value 06
    0b ff 99 04 ..  length 11, type 0xFF (Manufacturer Specific Data)

`hcitool lescan` prints the name and nothing else, because a name is all a scan
list needs. To see the payload itself:

    hcidump

Manufacturer Specific Data, type `0xFF`, is the escape hatch: two bytes of
company identifier and then whatever the vendor likes. It is where beacons put
their readings, and where firmware puts things nobody expected to be read off
the air.

One constraint shapes everything here. **An advertising payload is thirty-one
bytes**, in total, including every structure. What this sensor has to say does
not fit in thirty-one bytes, so it does what real beacons do and sends a piece
at a time, cycling. Each fragment is prefixed with its position.

Watch long enough to see them all, then put them in order. `hcidump -n` will
report more than once for you.
