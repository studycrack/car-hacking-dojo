# Catching a Transmission That Happens Once (One-Shot Capture)

The goal of this stage is as follows:
*  CAN frames do not queue up and wait. They are on the wire for a moment and then they are gone.
*  Whoever was listening heard it. For everyone else it did not happen.
*  This car's key fob transmits exactly once per button press.
*  That transmission carries the flag in ascii.
*  You need to start the capture first and press the button second.

Task:
*  Start capturing. Use a second terminal, or put it in the background with `&`.

```
candump -a vcan0 > /tmp/capture.txt &
```

*  Then press the fob button.

```
/challenge/press-fob
```

*  Find the frame with readable ascii in your capture file.

```
grep -a pwn /tmp/capture.txt
```

Hints:
*  Get the order right. Capturing after the press leaves you an empty capture, and nothing reports an error.
*  Just do it again if you get it wrong. There is no limit on presses.
*  Stop a backgrounded capture with `kill %1`.
*  Remember this ordering. Every challenge after this one assumes it.

The ascii text left in your capture is the flag!
