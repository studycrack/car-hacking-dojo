# Writing to a Characteristic and Reading the Permission Error (Write)

The goal of this stage is as follows:
*  Characteristics are not only for reading. Some accept writes, and a peripheral whose behaviour changes when you write to it is something to operate, not just observe.
*  This is the Bluetooth side of a body control module.
*  Its vault characteristic reads `locked`, and reads `locked` however many times you ask.
*  The value that opens it is written down in the attribute table.
*  You need to find it and write it.

Task:
*  Find which characteristic is writable. It has `write` in the properties column.

```
gatttool -b <address> --characteristics
```

*  Write anything to the vault. The peripheral's error tells you what it wants.

```
gatttool -b <address> --char-write-req -a <handle> -n d34dbeef
```

*  Walk the attribute table for the note whoever installed this module left behind.

```
gatttool -b <address> --char-desc
```

*  Write the value the note names.
*  Read the vault characteristic again and confirm it no longer says `locked`.

Hints:
*  Use `-req`. A Write Request gets a response, so you learn whether it worked.
*  Do not use `--char-write-cmd`. A Write Command is fire and forget and stays quiet when it fails.
*  Read the error you get back. It names the permission you violated.
*  Give the value as hex. If it is an ascii string, convert it first.

Open the vault, then read that characteristic for the flag!
