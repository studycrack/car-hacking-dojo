# Reassembling a Record Scattered Across Services (Fragments)

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

Hints:
*  Do not join in handle order. It does not read as anything.
*  Do not read meaning into handles. They are just numbers assigned in declaration order when the firmware built the table.
*  Read the index characteristic. It is the only thing that says how the fragments fit together.
*  Count that you have all five. Miss one and there is a hole in the middle.

Get the order right and the flag falls out!
