# Asking for the Scan Response With an Active Scan (Scan Response)

The goal of this stage is as follows:
*  Thirty-one bytes is not much, so the specification offers another thirty-one, with a condition attached.
*  Advertising goes out unasked. A **scan response** does not: the scanner has to send a scan request before the peripheral will answer with its second payload.
*  So scanning comes in two kinds.
   *  A **passive scan** only listens, and never reveals that you are looking.
   *  An **active scan** asks, which means transmitting, which means somebody could tell you were there.
*  This key fob put half of what you want in each.
*  You need to collect both halves and join them.

Task:
*  Watch passively first and collect the half you get for free.

```
hcidump --passive
```

*  Accept being seen and take the rest with an active scan.

```
hcidump
```

*  Compare the two outputs to see what appeared. What appeared is the scan response.
*  Join the fragments from both halves in position order.

Put the two halves together and you have the flag!
