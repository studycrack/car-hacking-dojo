The goal of this stage is as follows:
*  Reading had the same problem and you never had to notice. A Read Response carries at most MTU-1 bytes, and anything longer came in pieces your client fetched with Read Blob requests on your behalf.
*  Writing has the same problem and solves it differently. There is no `Write Blob`; the client stages the pieces and they land all at once.

| Request | Meaning |
| --- | --- |
| `16` Prepare Write | one piece, and the offset it belongs at |
| `18` Execute Write | commit what is staged (`01`) or discard it (`00`) |

*  Nothing is written until the Execute. The peripheral holds the pieces, reassembles them by offset, and commits one value.
*  This body control module has a service mode, and it opens on a **36-byte command**, which an ordinary Write Request cannot carry.
*  You need to get that command in with Prepare and Execute Write.

Task:
*  Find the 36-byte command in the attribute table. Whoever installed the service tooling left it there.

```
gatttool -b <address> --char-desc
```

*  Try sending it with an ordinary write once. You get an error about the length.
*  Stage it with Prepare Write and commit it with Execute Write.

```
import sys
sys.path.insert(0, "/challenge")
import ble

client = ble.Client("<address>")
client.write_long(<handle>, b"...36 bytes...")
```

*  Once service mode is open, read that characteristic.

Open service mode, then read that characteristic for the flag!
