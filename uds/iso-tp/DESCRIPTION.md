Everything so far has fit in a single frame. Eight bytes is not much, and a
diagnostic tool needs to ask real questions and get real answers back --- a
17-character VIN does not fit in eight bytes, let alone a firmware image.

**ISO-TP** (ISO 15765-2) is the transport layer that solves this, and it is
what every diagnostic session in every car on the road runs on top of. It uses
the first byte (or two) of a payload as a protocol control field:

| First nibble | Frame type | Layout |
| --- | --- | --- |
| `0` | Single Frame | `0L` followed by `L` bytes of data |
| `1` | First Frame | `1LLL` --- twelve bits of total length --- followed by the first 6 bytes |
| `2` | Consecutive Frame | `2N` --- a sequence number counting `1,2,...,F,0,1,...` --- followed by up to 7 bytes |
| `3` | Flow Control | `30 BS ST` --- continue, block size, minimum separation time |

The receiver drives the transfer. When it gets a First Frame, the sender
**stops and waits** until the receiver answers with a Flow Control frame. Only
then do the Consecutive Frames come.

On top of that sits **UDS** (ISO 14229), the diagnostic protocol. A request is
a service byte plus arguments; a positive response is the service byte plus
`0x40`. Service `0x22`, ReadDataByIdentifier, takes a 16-bit identifier:

    22 F1 90        ->      62 F1 90 <17 bytes of VIN>

The engine controller on this bus listens on identifier `0x7E0` and answers on
`0x7E8`. Wrap that request in an ISO-TP Single Frame --- three bytes of data,
so a `03` header --- and send it:

    cansend vcan0 7E0#0322F19000000000

Watch `0x7E8` while you do. You will get a First Frame, and then nothing,
because the ECU is waiting for you to tell it to continue. Send the Flow
Control frame yourself, and collect the rest.

Once you can do that, ask the same ECU for data identifier `0xF1AB`, which is
where this manufacturer parks its bootloader unlock token. The ECU is patient
--- it will wait a full two minutes for your Flow Control frame, so you have
time to type.
