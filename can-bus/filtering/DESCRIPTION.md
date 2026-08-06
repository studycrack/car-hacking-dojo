# Selecting Frames With an Identifier Filter (Filtering)

The goal of this stage is as follows:
*  This bus carries close to forty identifiers at once.
*  One controller leaks the flag on a single identifier.
*  The flag goes out seven bytes at a time, each fragment prefixed with one byte saying where it belongs.
*  The fragments arrive out of order, and after a full round the controller pauses about four seconds before starting again.
*  You need to filter down to that identifier, collect the fragments and put them back in order.

Task:
*  Watch the bus with `-a` and find the identifier showing ascii text.

```
candump -a vcan0
```

*  Filter down to it. `candump` takes filters after the interface, as `ID:MASK`.

```
candump -a vcan0,<the identifier you found>:7FF
```

*  Watch until you have seen every fragment.
*  Sort by the first byte of each payload, then strip that byte and join the rest.

Hints:
*  Set the mask to `7FF`. It keeps only frames where `received_id & MASK == ID & MASK`.
*  Loosen the mask to catch a range. `candump vcan0,100:700` is `0x100` through `0x1FF`.
*  Sort a capture by identifier to spot the odd one out. `candump vcan0 | awk` is enough.
*  Check that the fragment numbers are contiguous. A gap means you have not seen a full round yet.

Join the fragments in index order and you have the flag!
