Thirty-one bytes is not much, so the specification gives a device a second
thirty-one, with a condition attached.

An advertisement goes out unprompted. The **scan response** does not: a scanner
that wants it has to transmit a scan request, and the peripheral answers with a
second payload. That difference has a name.

- a **passive** scan listens, and reveals nothing about the listener
- an **active** scan asks, which means transmitting, which means the peripheral
  and anyone nearby knows somebody is looking

This key fob keeps half of what you want in each:

    hcidump --passive
    hcidump

Compare the two, then decide to be seen and collect the rest. The fragments in
the scan response continue the numbering from the advertisement, so the
ordering tells you how they join.

What the dojo models is the asymmetry: the advertisement sits where anyone can
read it, the scan response exists only as an answer. What it does not model is
range.
