In the last challenge you were handed the message layout. In the field, nobody
hands you the message layout. Identifiers and byte offsets are specific to a
manufacturer, a model, and often a model year, and they are not published.

So you reverse engineer them, by correlating something you can *see* with
something you can *capture*. Start the instrument cluster display:

    /challenge/dashboard

and, in a second terminal, watch the bus. The car is rolling, so the speed on
that display is moving. Dump the bus, and find the payload bytes that track the
needle. Work out how the number is encoded while you are there --- it is not
simply km/h, so compare a byte pair against the displayed value and recover the
scale factor.

More than one identifier tracks that needle, and the difference matters. One of
them is what the cluster *listens to*; another is the cluster *announcing* what
it is currently showing, for the benefit of the rest of the car. Only the first
one is worth attacking. Injecting on the second changes nothing at all, which
is itself a useful signal about which is which.

Then lie to the cluster. Make it display **exactly 133 km/h**.

The catch is that the wheel speed sensor is still on the bus, still reporting
the truth, five times a second. The cluster believes whichever frame arrived
most recently, so a single injected frame is overwritten almost immediately.
You have to hold the bus --- your frames need to drown the real ones out for
three seconds straight.

A shell loop around `cansend` spawns a process per frame and will struggle to
keep up. Talk to the bus directly from Python instead:

    import sys
    sys.path.insert(0, "/challenge")
    import vcan

    bus = vcan.Bus("vcan0")
    bus.send(0x123, bytes([0x11, 0x22]))

Hold the needle at 133 and the cluster will give up the flag.
