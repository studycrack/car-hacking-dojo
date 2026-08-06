The instrument cluster you lied to believed whatever arrived. Newer modules do
not. There is no room for a signature in eight bytes, so safety-relevant
messages carry two small fields instead, borrowed from AUTOSAR End-to-End
protection:

- An **alive counter**, incrementing by one on every transmission.
- A **checksum** over the payload.

This car's steering assist accepts torque requests on `0x1F5` and rejects
anything whose integrity fields do not hold up. You are not told how they are
computed. Recover that.

Two things are on your side. The module publishes its verdict on `0x1F6` ---
byte 0 is `01` when it accepted the last frame, `10` when the checksum was
wrong, `11` when the counter was wrong, and byte 1 is how many valid frames in
a row it has seen carrying the value it is watching. So you are told *which*
check you failed.

And the park assist issues genuine, correctly protected requests:

    /challenge/park-assist

That burst is your specimen. Capture it --- `candump` running *before* you
trigger it --- and study how the last two bytes behave as the payload changes.
`cansniffer -c vcan0` helps here too.

Then command a steering torque of `0x0BB8` and hold it: the module wants
**eight consecutive accepted frames** carrying that value, so your counters
have to keep marching in step and every checksum has to be right. Replaying the
specimen will not do it.
