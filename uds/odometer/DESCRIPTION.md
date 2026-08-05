Rolling back an odometer is the most commonly committed vehicle crime there is,
and it is a diagnostic operation. Service `0x2E`, WriteDataByIdentifier, is the
mirror of the `0x22` you already know:

    2E F1 A2 00 03 46 F0        write 214,768 to data identifier 0xF1A2

Same identifier space, same session rules --- writing is not something a
controller will do in the default session.

Read `0xF1A2` from the instrument cluster at `0x7E0` and it will tell you what
this car has done. Put it back to something under forty thousand kilometres and
the car is worth several thousand more.

Except that clusters stopped being the only witness twenty years ago.

Mileage is written into more than one controller precisely so that rewriting
one of them can be caught. The cluster publishes its own verdict on data
identifier `0xF1A3`, and it is not reading its own memory to reach it --- it is
comparing. Change one copy and the verdict says so.

Find every controller that remembers, and make them agree on a number they were
never at.
