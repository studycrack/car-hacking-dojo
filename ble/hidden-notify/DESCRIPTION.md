# Using a Capability the Declaration Does Not Advertise (Hidden Notify)

The goal of this stage is as follows:
*  Enumerate this dongle and its debug characteristic reads `debug channel idle`.
*  Its declaration says `READ` and nothing else. No notify property means nothing to subscribe to, and a tool that builds its interface from declarations will not even offer you the option.
*  But look at the **attribute table** rather than the characteristic list and there is a `0x2902` sitting underneath it.
*  A CCCD exists to enable notifications. It has no business being attached to a characteristic that cannot send them.
*  Somebody turned off the notify property to tidy up an interface and left the code that sends notifications exactly where it was.
*  You need to write to that CCCD and receive what it pushes.

Task:
*  Check the debug characteristic's properties in the characteristic list. `READ` only.

```
gatttool -b <address> --characteristics
```

*  Open the attribute table and confirm there is a `0x2902` beneath it.

```
gatttool -b <address> --char-desc
```

*  Write to that CCCD and stay connected, listening.

```
gatttool -b <address> --char-write-req -a <cccd handle> -n 0100 --listen
```

Hints:
*  Do not treat the declaration's property byte as a permission. It is **what the firmware says it intends**, and the stack does not enforce it.
*  Just write the CCCD. Nothing checks the properties when a write arrives.
*  Do not go back to reading the characteristic value. It still says `debug channel idle`. The CCCD is the thing to touch.

Turn the subscription on and the flag arrives as a notification!
