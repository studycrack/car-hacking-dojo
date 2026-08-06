Every peripheral so far, you connected to. This one you do not have to.

A device that wants to be found **advertises**: it broadcasts a payload over
and over, to nobody in particular. No connection, no handshake, and nothing in
the peripheral that could tell you were listening.

The payload is a sequence of **AD structures**, each a length byte, a type
byte, and its data:

    02 01 06        length 2, type 0x01 (Flags), value 06
    14 ff 99 04 ..  length 20, type 0xFF (Manufacturer Specific Data)

`hcitool lescan` gives you an address, and a name if the device advertises one.
This one does not, so it comes back `(unknown)`. To see the payload:

    hcidump --passive

Manufacturer Specific Data, type `0xFF`, is two bytes of company identifier
followed by whatever the vendor likes.

**An advertising payload is thirty-one bytes**, including every structure. What
this sensor has to say does not fit, so it sends a piece at a time, cycling,
each fragment prefixed with its position.

Watch long enough to see them all, then put them in order. `hcidump --passive
-n` will report more than once for you.
