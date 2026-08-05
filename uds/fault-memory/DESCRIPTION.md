Everything you have done to this car so far, it has been writing down.

A controller that is asked for something it cannot do does not simply answer
`7F` and forget. It records a **Diagnostic Trouble Code** --- a three-byte fault
identifier and a status byte --- in non-volatile memory, where it stays until a
technician clears it. That is the entire point of the mechanism: the car is
supposed to be able to tell someone, months later, what went wrong.

It works just as well for telling someone what *you* did. Scan a controller's
services and you have written a line in its logbook for every request it did
not like. Fuzz one and you have filled its fault memory with the shape of your own
reconnaissance.

Two services matter here.

`19 02 <mask>` --- ReadDTCInformation, reportDTCByStatusMask --- returns the
stored faults whose status byte overlaps your mask. Use `FF` to see everything.
The response is `59 02`, an availability mask, and then four bytes per fault:
three of identifier, one of status.

`14 FF FF FF` --- ClearDiagnosticInformation --- erases the lot.

This controller has a release routine that will hand you the flag. Finding it
is a matter of trying routine identifiers with `31 01 <id>` until one stops
saying `requestOutOfRange`, and that search is exactly the kind of noisy thing
that fills a fault memory.

It also will not run a release routine while it has faults recorded --- which is
a real interlock on real controllers, and which here means the search that
finds the routine is the same search that stops it from running.

Read the fault memory as you go. It will tell you plainly what you look like
from the car's side.
