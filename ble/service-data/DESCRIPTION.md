# Extracting the Payload From a Service Data Structure (Service Data)

The goal of this stage is as follows:
*  Manufacturer Specific Data left everything after two bytes of company identifier free. Advertising has more structured members too.
*  **Service Data**, AD type `0x16`, says which service the data belongs to. It opens with a 16-bit service UUID, and the payload follows.

```
12 16 6f fd 00 70 77 6e ...
^  ^  ^^^^^ ^^^^^^^^^^^^^
|  |  UUID  the actual data
|  type 0x16
length
```

*  This tracker rotates through fragments the same way the beacon did.
*  You need to start reading at the right offset for the type and pull out just the fragments.

Task:
*  Watch the advertising and find the AD structure whose type is `0x16`.

```
hcidump --passive
```

*  Read from **after the two UUID bytes**.
*  Collect the fragments, sort by the position byte, strip it, and join.

Hints:
*  Do not treat the whole structure as data. Every fragment picks up two bytes of UUID in front, which leaves you something that looks almost right and is not, which is harder to notice than being completely wrong.
*  If the same two characters keep appearing at regular intervals, you did not strip the UUID. Move the offset along by two.
*  Check the type first and then apply its layout. AD structures are typed, and each type lays its bytes out its own way.

Strip the UUID, join in order, and you have the flag!
