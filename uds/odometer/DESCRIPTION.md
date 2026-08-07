# Correcting an Odometer Recorded in Several Controllers (WriteDataByIdentifier)

The goal of this stage is as follows:
*  Odometer rollback is the most common vehicle crime there is, and it is also a single diagnostic operation.
*  Service `0x2E`, **WriteDataByIdentifier**, is the other half of the `0x22` you already know. Same identifier space, same session rules, and writing is not served in the default session.

```
2E F1 A2 00 03 46 F0      write 214,768 to DID 0xF1A2
```

*  The cluster is at `0x7E0`, and `0xF1A2` reads back the distance this car has travelled.
*  Except the cluster is no longer the only thing that remembers. The odometer is recorded across several controllers precisely so that changing one is detectable.
*  The cluster publishes a plausibility verdict on `0xF1A3`, and it produces that by **comparing against the other records**, not by reading its own memory.
*  You need every record to read the **same number, below forty thousand kilometres**.

Task:
*  Find every controller that remembers the odometer. Same enumeration you learned earlier.
*  Enter an extended session.

```
10 03
```

*  Write the same value to all of them.
*  Read `0xF1A3` to check the verdict.

Get every record to agree on a low enough value and the plausibility response carries the flag!
