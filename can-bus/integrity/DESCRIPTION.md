The car you spoofed in the last challenge believed whatever arrived. Plenty of
cars on the road still do. Newer ones increasingly do not.

The countermeasure is not cryptography --- there is no room for a signature in
eight bytes, and no time for one at 500 kbit/s. Instead, safety-relevant
messages carry two small fields, borrowed from AUTOSAR's End-to-End protection:

- An **alive counter**, incrementing by one on every transmission. A receiver
  that sees the same counter twice, or a jump, knows it is looking at a replay
  or at two senders fighting over one identifier.
- A **checksum** over the payload. A receiver that sees a wrong one knows the
  frame was not built by the real sender.

Neither stops someone who understands the scheme. Both stop someone who does
not, which is most of the point --- and which is why the first thing you do
against a modern bus is work out how its messages are protected.

This car's steering assist module accepts torque requests on identifier
`0x1F5`, and rejects anything whose integrity fields do not hold up. You are
not being told how they are computed. Recover that.

Two things are on your side. The module publishes its verdict on `0x1F6` ---
byte 0 is `01` when it accepted the last frame, `10` when the checksum was
wrong, `11` when the counter was wrong, and byte 1 is how many valid frames in
a row it has seen carrying the value it is watching. So you get told *which*
check you failed, and you can iterate.

And the park assist module issues genuine, correctly protected requests:

    /challenge/park-assist

That burst is your specimen. Capture it --- you know by now to have `candump`
running *before* you trigger it --- and study how the last two bytes behave as
the payload changes. `cansniffer -c vcan0` earns its keep here too: with one
line per identifier and changed bytes highlighted, a counter that steps by one
and a checksum that moves with it are visible at a glance.

Then command a steering torque of `0x0BB8`, which the park assist would never
ask for, and hold it: the module wants **eight consecutive accepted frames**
carrying that value, which means your counters have to keep marching in step
and every checksum has to be right. Replaying the specimen will not do it; the
value has to change, and the protection has to change with it.
