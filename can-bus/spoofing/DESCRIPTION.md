When you unlocked the doors you were handed the message layout. Nobody hands it
to you in the field. You reverse engineer it by correlating something you can
*see* with something you can *capture*.

Start the instrument cluster display:

    /challenge/dashboard

The car is rolling, so the needle is moving. Find the payload bytes that track
it, and work out the encoding --- it is not simply km/h, so compare a byte pair
against the displayed value and recover the scale factor.

`candump` scrolls too fast to read. Use:

    cansniffer -c vcan0

It keeps one line per identifier and colours the bytes that just changed. Quit
with `q`.

More than one identifier tracks the needle. One is what the cluster *listens
to*; another is the cluster *announcing* what it shows. Only the first is worth
attacking, and the display will not tell you which is which: it draws whatever
the announcement says, so injecting on the announcement paints 133 on the
screen while the cluster has believed nothing. One honest way to tell them
apart is that the announcement carries engine RPM next to the speed, and a
wheel speed sensor has no idea what the engine is doing.

Make the cluster believe the car is doing **exactly 133 km/h**.

The real sensor is still reporting the truth five times a second, and the
cluster believes whichever frame arrived last, so a single injected frame is
overwritten at once. Your frames have to drown it out for three seconds
straight.

A shell loop around `cansend` spawns a process per frame and will not keep up.
Talk to the bus from Python:

    import sys
    sys.path.insert(0, "/challenge")
    import vcan

    bus = vcan.Bus("vcan0")
    bus.send(0x123, bytes([0x11, 0x22]))
