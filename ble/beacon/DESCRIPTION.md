# Reading a Device Without Connecting to It (Beacon)

The goal of this stage is as follows:
*  Every peripheral so far you connected to. This one you do not have to.
*  A device that wants to be found **advertises**: it broadcasts a payload at nobody in particular, with no connection and no handshake.
*  An advertising payload is a sequence of **AD structures**, each a length byte, a type byte, and data.

```
02 01 06        length 2, type 0x01 (Flags), value 06
14 ff 99 04 ..  length 20, type 0xFF (Manufacturer Specific Data)
```

*  Type `0xFF` is two bytes of company identifier followed by whatever the manufacturer wants.
*  **The whole payload, every structure together, is 31 bytes.** What this sensor has to say does not fit, so it rotates through fragments, each prefixed with its position.
*  You need to collect them all and put them in order.

Task:
*  Watch the advertising payload directly.

```
hcidump --passive
```

*  Find the type `0xFF` structure and read from after the two company identifier bytes.
*  Watch until you have seen every fragment.
*  Sort by the position byte, strip it, and join.

Hints:
*  Add `-n` to have it report repeatedly.
*  Do not look for it by name. This device does not advertise one, so `hcitool lescan` shows it as `(unknown)`.
*  Wait for a full round. Miss a fragment and there is a hole in the middle.
*  Do not reach for `gatttool`. There is nothing to connect to.

Join the fragments in order and you have the flag!
