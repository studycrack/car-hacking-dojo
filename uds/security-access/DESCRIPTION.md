# Defeating an Attempt Limiter and Brute Forcing the Key (SecurityAccess)

The goal of this stage is as follows:
*  Reflashing, actuator tests and disarming an immobiliser all sit behind service `0x27`.
*  **SecurityAccess** is a challenge-response exchange.
   1.  `10 03` puts you in an extended session.
   2.  `27 01` requests a seed. The ECU answers `67 01` and four random bytes.
   3.  You compute a key from that seed and send `27 02 <key>`. This ECU uses a **16-bit key**.
   4.  If the key is right the ECU answers `67 02`.
*  The key algorithm lives inside the dealer diagnostic software. Here you guess instead: sixteen bits is 65,536 possibilities.
*  But three wrong keys and the ECU answers `7F 27 36` (exceedNumberOfAttempts) and refuses security requests for ten seconds. At that rate an exhaustive search takes days.
*  You need to defeat the limiter, find the key, and then run routine `0xF00D`.

Task:
*  Enter an extended session and take a seed once.

```
import sys
sys.path.insert(0, "/challenge")
import isotp, vcan

bus = vcan.Bus("vcan0")
print(isotp.request(bus, 0x7E0, 0x7E8, bytes.fromhex("1003")).hex())
```

*  Find **what resets the failure counter** after a wrong key.
*  Work that into the loop and sweep the whole sixteen bits.
   *  `7F 27 36` means you are locked out.
   *  `67 02` means you are in.
*  Once unlocked, run the routine.

```
31 01 F0 0D
```

Hints:
*  Ask for a diagnostic session as often as you like. It is what a tester does constantly, so it is never refused.
*  Look at how this ECU treats a new session. No failure count and no lockout survive it.
*  Take the seed once and keep using it. It survives as long as you do not fall back to the default session.
*  Do not fetch a fresh seed per attempt. The target keeps moving and the search never finishes.

The response to the routine carries the flag!
