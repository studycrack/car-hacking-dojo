# Car Hacking

A DOJO teaching automotive bus security: CAN frame analysis, frame injection,
signal reverse engineering, and the UDS diagnostic protocol.

## Modules

| Module | Challenge | Skill |
| --- | --- | --- |
| The CAN Bus | `sniffing` | reading a bus with `candump` |
| | `filtering` | identifier filters, payload structure |
| | `fob-capture` | capturing a one-shot transmission: attach the capture before triggering the event |
| | `injection` | forging frames with `cansend` against a live controller |
| | `spoofing` | reverse engineering a signal's identifier, offset, and scale, then out-transmitting the real sensor |
| Diagnostics and UDS | `iso-tp` | segmentation and flow control, by hand |
| | `ecu-discovery` | address and data-identifier enumeration |
| | `security-access` | bypassing a SecurityAccess attempt limiter via session reset, then brute forcing a 16-bit key |

## The bus is emulated in userspace

Workspace containers run under `runc` with only `SYS_PTRACE` (see
`dojo_plugin/api/v1/docker.py`), so a challenge cannot `ip link add dev vcan0
type vcan` --- that needs `CAP_NET_ADMIN`, which is only granted to
`privileged` challenges in dojos holding the `workspace_net_admin` permission.

So `shared/vcan.py` emulates the bus instead. A hub process, started as root by
each challenge's `.init`, listens on a unix socket at `/run/vcan/vcan0` and
broadcasts every frame it receives to every *other* attached client --- which is
what a CAN transceiver sees on a real bus, including the absence of loopback to
the sender.

Frames cross that socket in can-utils notation, one per line:

    1A0#DEADBEEF00112233

`shared/tools/` then provides `candump`, `cansend`, `canascii`, and `isotpreq`
with the same argument syntax and output format as the real can-utils, so
everything a student learns here transfers directly to a real SocketCAN
interface.

## Layout

Each challenge directory symlinks the shared code it needs:

    can-bus/injection/
      .init          starts the hub and the ECU as root, hides the ECU
      ecu            the controller under attack; reads /flag as root
      DESCRIPTION.md
      vcan.py     -> ../../shared/vcan.py
      bin/candump -> ../../../shared/tools/candump

The DOJO resolves symlinks when it copies a challenge into a container
(`resolved_tar` in `dojo_plugin/utils/__init__.py`), inlining the target's
contents, so there is exactly one copy of the bus implementation in the repo.
Symlinks must stay inside the dojo root, and must point at files rather than
directories --- a symlinked directory is copied as an empty directory.

Every file placed in `/challenge` is made `root:root 4755` by the DOJO, so
anything a student should not read --- the ECU firmware, and `isotp.py` in the
challenge whose objective is to implement ISO-TP --- is `chmod 600`'d by `.init`.
Since `.init` runs as root, the ECU still starts fine.

## Adding a challenge

1. Create `<module>/<challenge-id>/` with `.init`, `ecu`, and `DESCRIPTION.md`.
2. Symlink `vcan.py` (and `isotp.py` if needed) plus the tools into `bin/`.
3. Add a `type: challenge` entry to the module's `module.yml`.

The ECU reads `/flag` at startup as root and emits it only when its win
condition is met, either as ascii frames on identifier `0x7C0` or as a UDS
response payload.

## Testing

Challenges are ordinary DOJO challenges; load the dojo and use the standard
test flow (`./deploy.sh -t` in the DOJO repo). The bus, the tools, and each
challenge's win condition can also be exercised outside a container --- run the
hub and an `ecu` as root with `/run/vcan` writable and a `/flag` in place, then
talk to the socket with the tools in `shared/tools/`.
