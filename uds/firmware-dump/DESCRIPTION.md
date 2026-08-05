Reading a controller's memory is the single most productive thing a diagnostic
session can do for an attacker. Not because the memory itself is interesting,
but because firmware is where every assumption a manufacturer made is written
down: the services they built and never documented, the constants they compiled
in, the strings they left in a debug build that shipped.

UDS service `0x23`, **ReadMemoryByAddress**, is the front door. Its request is
a little unusual, because the address and length widths are not fixed --- the
byte after the service id declares them:

    23 <AALFI> <address...> <length...>

`AALFI` packs two nibbles: the high one is how many bytes carry the *length*,
the low one is how many carry the *address*. So `14` means a four-byte address
followed by a one-byte length, and

    23 14 20 00 00 00 10

asks for `0x10` bytes from `0x20000000`. A positive response comes back as
`63` followed by the data.

Three things stand between you and a dump.

**Where is the memory?** You get `requestOutOfRange` for anything outside the
mapped region. Guessing across a 32-bit space is hopeless, so do what you did
when you enumerated the controllers, and ask this one what it is: identification
record `0xF18C` names the part, and the part names its own memory map. Cortex-M
flash does not move around.

**How much at a time?** More than a controller wants to put on the wire in one
response gets refused. Find the ceiling and write a loop --- this is a dump, not
a read.

**What session?** `0x23` is not something a controller will do for anyone who
asks. You already know how to enter a diagnostic session.

Once you have the image on disk, treat it like firmware, because it is. Run
`strings` over it, or `xxd`, or just walk it in python. The controller is
chattier in its debug build than its engineers intended, and somewhere in there
is a service that appears in no specification --- along with what it expects to
be handed.

Call it, and the unit will give up its secret.
