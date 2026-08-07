# Rewriting a Calibration Block to Disarm the Immobiliser (Reflash)

The goal of this stage is as follows:
*  Reading a controller's memory is reconnaissance. Writing to it is the attack.
*  UDS specifies the rewrite in three steps.

| Request | Meaning |
| --- | --- |
| `34 <fmt> <ALFI> <address> <size>` | RequestDownload, declaring where and how much |
| `36 <n> <data...>` | TransferData, one block. `n` counts `01, 02, 03, ...` |
| `37 <checksum>` | RequestTransferExit, finishing and proving the bytes arrived intact. The checksum is every byte summed, two's complemented, truncated to one |

*  `RequestDownload` answers `74`, a length format byte, and the largest block it will accept.
*  `TransferData` must carry the **next** block number. Repeat one or skip one and you get `requestSequenceError`.
*  `RequestTransferExit` only commits if the declared length arrived in full and the checksum matches.
*  The calibration region is at `0x08010000`, and inside it is a four-byte field deciding whether the immobiliser is armed. `DE AD BE EF` counts as disarmed.
*  You need to rewrite the calibration block so the immobiliser is disarmed.

Task:
*  Read the calibration region before you overwrite it. `0x23` works here too.
*  Work out the offset of the immobiliser field inside the structure.
*  Enter a **programming session**. The procedure does not work outside one.
*  Run the three steps in order.
   *  `34` declares the address and size.
   *  `36` sends the blocks in numbered order.
   *  `37` finishes with the checksum.

Once the write commits the controller reports the result, and the flag is in it!
