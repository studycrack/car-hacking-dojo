The goal of this stage is as follows:
*  You have subscribed and you have written. This one needs both, and the **order** matters.
*  Write to one characteristic on this keyless module and it pushes the answer as a notification on another.
*  That answer goes only to **whoever is subscribed at that moment**. Nothing is queued, so writing first produces an answer that is pushed at nobody and lost.
*  And the answer comes back **on the connection that asked**.
*  You need to hold one connection open and do both inside it.

Task:
*  Find the characteristic the answer arrives on and the one that takes the request.
*  Open one connection and **subscribe first**.
*  Write to the request characteristic on that same connection.
*  Receive the notification on it.

```
import sys
sys.path.insert(0, "/challenge")
import ble

client = ble.Client("<address>")
client.subscribe(<cccd handle>)
client.write(<request handle>, b"\x01")
for handle, value in client.events_stream(timeout=5):
    print(hex(handle), value)
```

The answer that arrives as a notification is the flag!
