A controller asked for something it cannot do does not simply answer `7F` and
forget. It records a **Diagnostic Trouble Code** --- a three-byte fault
identifier and a status byte --- until a technician clears it. Scan a
controller's services and you have written a line in its logbook for every
request it did not like.

Two services matter here.

`19 02 <mask>` --- ReadDTCInformation, reportDTCByStatusMask --- returns the
stored faults whose status byte overlaps your mask. Use `FF` for everything.
The response is `59 02`, an availability mask, then four bytes per fault: three
of identifier, one of status.

`14 FF FF FF` --- ClearDiagnosticInformation --- erases the lot.

This controller has a release routine that will hand you the flag. Finding it
means trying routine identifiers with `31 01 <id>` until one stops saying
`requestOutOfRange` --- and that search is exactly the kind of noisy thing that
fills a fault memory.

It also will not run a release routine while it has faults recorded. So the
search that finds the routine is the same search that stops it from running.

Read the fault memory as you go.
