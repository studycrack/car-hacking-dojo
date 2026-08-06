# Finding a Handle the Discovery Response Omits (Handle Walking)

The goal of this stage is as follows:
*  Every enumeration so far asked the peripheral to describe itself, and took the answer on trust.
*  That answer is produced by the firmware. A Read By Type response is the list the device **chose to send**, and a device can leave things out of it.
*  Leaving something out of the discovery response does not remove it from the attribute table. **The handle still works.**
*  ATT has no step where a Read Request is checked against a discovery listing. It finds the handle and serves it.
*  You need to walk the handles one at a time and find the attribute the listing left out.

Task:
*  Get the list of handles discovery admits to.

```
gatttool -b <address> --char-desc
```

*  Read handles directly, starting at `0x0001` and counting up.

```
gatttool -b <address> --char-read -a 0x0001
```

*  Sort the responses into two kinds.
   *  `Invalid handle` means there is nothing there.
   *  Anything else means there is.
*  Find the handle that answered but was not in the listing, and read it.

Hints:
*  Write a loop. Handles are small integers and there are not many of them.

```
for h in $(seq 1 60); do
  printf '%04x ' $h
  gatttool -b <address> --char-read -a $h
done
```

*  If that is slow, use the client in `/challenge/ble.py`, which opens the connection once and walks the whole range.
*  Put the two listings side by side. Without comparing them you cannot tell what was hidden.

The attribute that was hiding holds the flag!
