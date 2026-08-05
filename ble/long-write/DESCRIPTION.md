Reading has this problem and you have never had to notice. A Read Response
carries at most MTU-1 bytes, so every value longer than that has been arriving
in pieces, gathered up with Read Blob requests your client sent on your behalf
without mentioning it.

Writing has the same problem and a different answer. There is no
`Write Blob` --- instead the client queues the pieces and then commits them:

| Request | Meaning |
| --- | --- |
| `16` Prepare Write | here is a fragment, and the offset it belongs at |
| `18` Execute Write | apply everything I queued (`01`), or throw it away (`00`) |

Nothing is written until the Execute. The peripheral holds the fragments,
reassembles them in offset order, and applies the result as one value --- which
is what makes it safe to write something that could not fit in a single packet
without the attribute being briefly half-written.

This body control module has a service mode, and it opens for a command that
is thirty-six bytes long. A plain Write Request will not carry it.

The command itself is not a secret; it is sitting in the attribute table where
the workshop tool's installer left it. Getting it *in* is the exercise.
