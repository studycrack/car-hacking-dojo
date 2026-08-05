Thirty-one bytes is not much, so the specification gives a device a second
thirty-one --- with a condition attached.

An advertisement goes out unprompted. The **scan response** does not. A scanner
that wants it has to transmit a scan request, and the peripheral answers with a
second payload. That difference has a name:

- a **passive** scan listens, and reveals nothing about the listener
- an **active** scan asks, which means transmitting, which means the peripheral
  and anyone else nearby knows somebody is looking

That is a real operational trade, not a technicality. Sitting silently in a car
park recording what advertises tells you nothing about who is recording.
Sending a scan request does not.

This key fob keeps half of what you want in each. Both tools take the flag:

    hcidump --passive
    hcidump

Compare the two. Then decide to be seen, and collect the rest --- the fragments
in the scan response continue the numbering from the advertisement, so once you
have both halves the ordering tells you how they join.
