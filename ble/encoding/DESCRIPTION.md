This is the module that lets a phone be the key. Read its characteristics and
you will find values that look like nothing:

    36 31 34 65 33 32 62 61 39 63

That is not encryption. It is ascii digits and letters, which is what you get
when firmware stores a byte array as **hex text**. Decode it and you have half
of something.

The other half is stored differently --- padded, alphanumeric, with the shape
that gives **base64** away.

Neither is a cipher: there is no key and the transformation is published.
Recognising them on sight is the skill. Decode both halves, put them in the
order the descriptors give you, and you have the whole thing.
