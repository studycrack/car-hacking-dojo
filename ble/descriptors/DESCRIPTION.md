A characteristic list is not the whole attribute table.

A characteristic is at minimum two attributes: a **declaration** saying what
properties it has and where its value lives, and the **value** itself. It may
also carry **descriptors**, further attributes that annotate it. The common one
is the Characteristic User Description, UUID `0x2901`, which holds a
human-readable label --- firmware authors treat it as a comment field, and
comments get left in.

`--characteristics` will not show descriptors, because they are not
characteristics. To see every attribute, handle by handle:

    gatttool -b <address> --char-desc

You will get far more rows than the characteristic listing had. Read them.
