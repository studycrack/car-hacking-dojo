A counter and a checksum stop an attacker who has not looked. They stop nobody
who has, which is why the industry moved to actual cryptography.

**SecOC** --- Secure Onboard Communication, the AUTOSAR mechanism --- puts a
message authentication code on the frames that matter. Sender and receiver
share a key. Each transmission carries the payload, a **freshness value** that
must never go backwards, and a truncated MAC. Forging a frame now means forging
a MAC, and three bytes of HMAC is not something you are going to guess.

This car's body controller works that way. Doors are commanded on `0x1B0`:
two bytes of payload, one of freshness, three of MAC. It reports itself on
`0x1B1` --- byte 0 locked, byte 1 the freshness it last accepted, byte 2 what
it made of the last frame it looked at: `01` accepted, `02` MAC did not verify,
`03` freshness was not ahead of where it already was.

The car locks itself periodically, so there is authenticated traffic to watch.
And the fob still works:

    /challenge/press-fob

You cannot compute a MAC. You do not have the key and you are not going to get
it. So do not attack the cryptography --- attack what it was computed over.

A MAC is only a promise about the bytes that went into it. Every field that was
left out of that computation is a field you are free to change, and the
specification is explicit that the freshness value has to be one of the inputs
precisely because otherwise the anti-replay counter is not protected by
anything.

Watch the car lock itself several times over. The payload is identical each
time and the freshness is not. Look at what the MAC does.

Then unlock a car whose owner never asked you to.
