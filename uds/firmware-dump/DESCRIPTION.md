Firmware is where every assumption a manufacturer made is written down: the
services they built and never documented, the constants they compiled in, the
strings they left in a debug build that shipped.

UDS service `0x23`, **ReadMemoryByAddress**, is the front door. The address and
length widths are not fixed --- the byte after the service id declares them:

    23 <AALFI> <address...> <length...>

`AALFI` packs two nibbles: the high one is how many bytes carry the *length*,
the low one how many carry the *address*. So `14` means a four-byte address
followed by a one-byte length, and

    23 14 20 00 00 00 10

asks for `0x10` bytes from `0x20000000`. A positive response is `63` followed
by the data.

Three things stand between you and a dump.

**Where is the memory?** Anything outside the mapped region gets
`requestOutOfRange`. Guessing across a 32-bit space is hopeless, so do what you
did when you enumerated the controllers and ask this one what it is:
identification record `0xF18C` names the part, and the part names its own
memory map. Cortex-M flash does not move around.

**How much at a time?** More than the controller will put on the wire in one
response gets refused. Find the ceiling and write a loop.

**What session?** `0x23` is not something a controller will do for anyone who
asks.

Once you have the image, run `strings` over it, or `xxd`, or walk it in python.
Somewhere in there is a service that appears in no specification, along with
what it expects to be handed. Call it.
