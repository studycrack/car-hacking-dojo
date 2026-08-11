The goal of this stage is as follows:
*  This tyre pressure gateway gives every sensor its own service: four wheels and the spare, five in all.
*  A single record is split into five fragments across those five services.
*  Each sensor has three characteristics: RSSI, index, and payload.
*  The payload is the fragment; the index says where it goes.
*  **Handle order is not record order.** You have to read the index to know.

Task:
*  Enumerate the five services.

```
gatttool -b <address> --primary
```

*  List the characteristics inside them.

```
gatttool -b <address> --characteristics
```

*  Read the index and the payload from each sensor.
*  Join the payloads in the order the indices give.

Get the order right and the flag falls out!
