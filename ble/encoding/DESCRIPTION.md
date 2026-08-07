# Decoding Values Stored as Hex and Base64 (Encoding)

The goal of this stage is as follows:
*  This module is the one that lets a phone act as a key.
*  Read its characteristics and you get a value that looks like nothing at all.

```
36 31 34 65 33 32 62 61 39 63
```

*  That is not encryption. It is ascii digits and letters, which is what firmware storing a byte array as **hex text** looks like on the wire.
*  The other half is stored differently: padded, alphanumeric, the shape **base64** always has.
*  You need to decode each half appropriately and join them in the order the descriptors give.

Task:
*  Walk the attribute table and read both halves.
*  Decide which encoding each one is.
   *  Only `0-9a-f`, even length: hex text.
   *  Ends in `=`, or mixes case: base64.
*  Decode each one.

```
echo -n '36313465...' | xxd -r -p
echo -n 'cHduLmNv...' | base64 -d
```

*  Read the descriptors for the ordering, then join.

Join the two halves in order and you have the flag!
