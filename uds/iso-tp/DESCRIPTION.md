# Carrying a Diagnostic Request Longer Than Eight Bytes (ISO-TP)

The goal of this stage is as follows:
*  A 17-character VIN does not fit in a CAN frame, so diagnostics run on top of a transport layer, **ISO-TP** (ISO 15765-2).
*  ISO-TP spends the first byte of the payload on a control field.

| First nibble | Kind | Format |
| --- | --- | --- |
| `0` | Single Frame | `0L`, then `L` bytes |
| `1` | First Frame | `1LLL`, 12-bit total length, then the first 6 bytes |
| `2` | Consecutive Frame | `2N`, sequence `1,2,…,F,0,…`, then up to 7 bytes |
| `3` | Flow Control | `30 BS ST`, continue · block size · minimum separation |

*  The **receiver** drives the transfer. A sender that has sent a First Frame stops and waits for flow control.
*  **UDS** (ISO 14229) rides on top: a request is a service byte and arguments, and a positive response is the service byte plus `0x40`.
*  The engine controller receives on `0x7E0` and answers on `0x7E8`.
*  You need to send the flow control yourself to get the VIN, then read DID `0xF1AB`.

Task:
*  Start a capture so you can see the responses.

```
candump vcan0,7E8:7FF &
```

*  Request the VIN. That is `22 F1 90` wrapped in a Single Frame, hence the `03` header.

```
cansend vcan0 7E0#0322F19000000000
```

*  A First Frame arrives and the transfer stops. Send flow control yourself to release the rest.
   *  `30` means continue.
   *  The two bytes after it are block size and minimum separation.
*  Read DID `0xF1AB` from the same controller. It is the bootloader unlock token.

Hints:
*  Join the fragments to read it. The response is `62 F1 90` followed by seventeen bytes.
*  Send flow control as soon as the transfer stalls. The ECU waits thirty seconds for it.
*  If the ECU has gone quiet, wait a moment and ask again. It does not answer anything else while it is waiting.
*  If doing it by hand is tedious, use `isotpreq`, which handles segmentation and flow control for you.

```
isotpreq vcan0 7E0 7E8 22F190
```

The response to `0xF1AB` carries the flag!
