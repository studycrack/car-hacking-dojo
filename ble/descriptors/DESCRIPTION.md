The goal of this stage is as follows:
*  A characteristic is at least two attributes: a **declaration** saying what properties it has and where its value lives, and the **value** itself.
*  **Descriptors** may sit alongside them, annotating the characteristic.
*  The most common is the Characteristic User Description, UUID `0x2901`. It holds a human-readable label, which is why firmware developers treat it like a comment field and leave things in it they should not.
*  `--characteristics` does not show descriptors at all.
*  You need to open the whole attribute table and read the descriptor.

Task:
*  List the attribute table handle by handle.

```
gatttool -b <address> --char-desc
```

*  Sort the output into three kinds.
   *  the declarations you already know about
   *  their value handles
   *  the rest, which are the descriptors nobody expected you to look at
*  Read the descriptor handles.

```
gatttool -b <address> --char-read -a <descriptor handle>
```

One of the descriptors holds the flag!
