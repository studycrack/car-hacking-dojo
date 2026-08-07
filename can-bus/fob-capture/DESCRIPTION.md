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

*  That is only the first eight bytes. Take its identifier and read every frame on it.

```
grep -a ' <that identifier> ' /tmp/capture.txt
```

Join the ascii across those frames and you have the flag!
