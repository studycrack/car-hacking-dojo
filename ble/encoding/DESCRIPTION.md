This is the module that lets a phone be the key. The app pairs with it once,
and afterwards the car unlocks when the phone is near. It is the most
security-relevant peripheral on the vehicle, and it is on the air permanently.

Read its characteristics and you will find values that look like nothing:

    36 31 34 65 33 32 62 61 39 63

That is not encryption. That is a string of ascii digits and letters, which
happens to be what you get when firmware stores a byte array as **hex text**.
Decode it and you have half of something.

The other half is stored differently --- padded, alphanumeric, with the shape
that gives **base64** away. Same idea: a way to fit arbitrary bytes into a
field that expects text, chosen because it was convenient, not because it
protects anything.

Neither is a cipher. There is no key, and the transformation is published. A
value that has been encoded is a value that has been *written down in a
different alphabet*, and anyone who recognises the alphabet can read it.

Recognising them on sight is the skill. Decode both halves, put them in the
order the descriptors give you, and you have the whole thing.
