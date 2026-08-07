# Getting Through an Interlock That Counts (Interlock)

The goal of this stage is as follows:
*  The vault before this opened on a single write. Things that matter are not usually left that way.
*  This is an immobiliser. It takes **several writes in a fixed order** and keeps count of how far you have got.
*  A wrong step is not ignored: it **sends you back to the start**. Tolerating a wrong step would let you brute force each position separately.
*  A status characteristic tells you which step you are on.
*  You need to walk the sequence to the end.

Task:
*  Find the service procedure extract in the attribute table and read it. The steps are in there.

```
gatttool -b <address> --char-desc
```

*  Read the status to see where you are starting.
*  Write the values the procedure names, in order.

```
gatttool -b <address> --char-write-req -a <handle> -n <value>
```

*  **Read the status after every write.** Confirm the step advanced before you send the next one.
*  If the status has gone back to the start, start over.

Reach the end and the status characteristic hands you the flag!
