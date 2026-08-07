# Dumping the Firmware to Find an Undocumented Service (ReadMemoryByAddress)

The goal of this stage is as follows:
*  Firmware carries every assumption the manufacturer made: services they never documented, constants they compiled in, strings a debug build left behind.
*  UDS service `0x23`, **ReadMemoryByAddress**, is the way in. Address and length widths are not fixed; the byte after the service id declares them.

```
23 <AALFI> <address...> <length...>
```

*  `AALFI` is two nibbles: the high one is how many bytes of **length**, the low one how many bytes of **address**. So `14` is a four-byte address and a one-byte length.

```
23 14 20 00 00 00 10      0x10 bytes from 0x20000000
```

*  A positive response is `63` followed by the data.
*  You need to dump the flash, then find and call a service that is in no specification.

Task:
*  Work out where the flash lives.
   *  Ask for identification record `0xF18C` to get the part name.
   *  The part name tells you its memory layout.
*  Find the largest read the controller will serve. Ask for more and it refuses.
*  Loop until you have the whole image.
*  Search the image for the service that is in no specification, and for the value it demands, then call it.

Call the hidden service correctly and its response carries the flag!
