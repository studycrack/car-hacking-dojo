Reading a controller's memory is reconnaissance. Writing it is the actual
attack, and UDS has a whole vocabulary for it, because reflashing is a thing
every dealership does every day.

The sequence is fixed and unforgiving:

| Request | Meaning |
| --- | --- |
| `34 <fmt> <ALFI> <addr> <size>` | RequestDownload --- announce where and how much |
| `36 <n> <data...>` | TransferData --- one block, `n` counting `01, 02, 03, ...` |
| `37 <checksum>` | RequestTransferExit --- finish, and prove the bytes arrived intact |

`RequestDownload` answers `74` followed by a length format byte and the largest
block it will take. Every `TransferData` must carry the *next* block number ---
the controller is counting, and a repeat or a skip is a `requestSequenceError`.
`RequestTransferExit` only commits the write if the whole announced length
arrived and your checksum matches. This one uses the same checksum every boot
loader has used since the eighties: the two's complement of the sum of the
bytes, truncated to one byte.

None of this happens in an ordinary session. Flashing is what the
**programming session** is for.

The block you want is the calibration area at `0x08010000`, which you can read
before you write --- `0x23` works here too, and reading first is how you learn
what you are about to overwrite. It is a small structure with its field layout
helpfully spelled out in it, including one four-byte field that decides whether
the immobilizer is armed.

The controller considers the immobilizer disarmed when that field reads
`DE AD BE EF`, which is the sort of value that gets compiled into a development
build and then ships. Write a calibration block that says so.

Get the sequence right, get the checksum right, and the controller will commit
your calibration and tell you what it thinks of the result.
