The goal of this stage is as follows:
*  This bus carries close to forty identifiers at once.
*  One controller leaks the flag on a single identifier.
*  The flag goes out seven bytes at a time, each fragment prefixed with one byte saying where it belongs.
*  The fragments arrive out of order, and after a full round the controller pauses about four seconds before starting again.
*  You need to filter down to that identifier, collect the fragments and put them back in order.

Task:
*  Watch the bus with `-a` and find the identifier showing ascii text.

```
candump -a vcan0
```

*  Filter down to it. `candump` takes filters after the interface, as `ID:MASK`.

```
candump -a vcan0,<the identifier you found>:7FF
```

*  The fragments scroll past faster than you can copy them, so send the capture to a file and work on that.

```
timeout 12 candump vcan0,<the identifier you found>:7FF > /tmp/fragments.txt
```

*  Twelve seconds covers more than one full round, so every fragment is in there.
*  Sort by the first byte of each payload, then strip that byte and join the rest.

```
#!/usr/bin/python3
pieces = {}
for line in open("/tmp/fragments.txt"):
    payload = [int(x, 16) for x in line.split("]")[1].split()]
    pieces[payload[0]] = bytes(payload[1:])
print(b"".join(pieces[index] for index in sorted(pieces)).decode())
```

Join the fragments in index order and you have the flag!
