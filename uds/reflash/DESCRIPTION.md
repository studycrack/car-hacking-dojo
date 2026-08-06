Reading a controller's memory is reconnaissance. Writing it is the attack. The
sequence is fixed:

| Request | Meaning |
| --- | --- |
| `34 <fmt> <ALFI> <addr> <size>` | RequestDownload --- announce where and how much |
| `36 <n> <data...>` | TransferData --- one block, `n` counting `01, 02, 03, ...` |
| `37 <checksum>` | RequestTransferExit --- finish and prove the bytes arrived |

`RequestDownload` answers `74`, a length format byte, and the largest block it
will take. Every `TransferData` must carry the *next* block number; a repeat or
a skip is a `requestSequenceError`. `RequestTransferExit` commits only if the
whole announced length arrived and your checksum matches --- the two's
complement of the sum of the bytes, truncated to one byte.

None of this works outside the **programming session**.

The calibration area is at `0x08010000`, and `0x23` reads it. It is a small
structure with its field layout spelled out inside it, including a four-byte
field that decides whether the immobilizer is armed. The controller considers
it disarmed when that field reads `DE AD BE EF`.

Write a calibration block that says so.
