# Car Hacking

A DOJO teaching automotive bus security: CAN frame analysis, frame injection,
signal reverse engineering, and the UDS diagnostic protocol.

## Modules

| Module | Challenge | Skill | Est. |
| --- | --- | --- | --- |
| The CAN Bus | `sniffing` | reading a bus with `candump` | 10m |
| | `filtering` | identifier filters, payload structure | 20m |
| | `fob-capture` | capturing a one-shot transmission: attach the capture before triggering the event | 15m |
| | `injection` | forging frames with `cansend` against a live controller | 25m |
| | `contention` | out-transmitting the controller that reports the opposite, and holding the majority long enough to be believed | 20m |
| | `rolling-code` | replaying a rolling code the receiver never consumed | 40m |
| | `resync` | replaying a captured run to resynchronise a rolling code receiver backwards, then unlocking with a code it had passed | 45m |
| | `spoofing` | reverse engineering a signal's identifier, offset, and scale, then out-transmitting the real sensor | 50m |
| | `dbc` | reading a DBC file and letting cantools do the Motorola bit packing | 30m |
| | `integrity` | recovering an alive counter and checksum from captured traffic to forge frames a validating module accepts | 55m |
| | `secoc` | forging an authenticated frame without the key, by changing a field the MAC was never computed over | 60m |
| Diagnostics and UDS | `iso-tp` | segmentation and flow control, by hand | 45m |
| | `ecu-discovery` | address and data-identifier enumeration | 30m |
| | `security-access` | bypassing a SecurityAccess attempt limiter via session reset, then brute forcing a 16-bit key | 45m |
| | `firmware-dump` | ReadMemoryByAddress: locating flash, probing the read ceiling, dumping it, and mining the image for an undocumented service | 45m |
| | `fault-memory` | reading and clearing diagnostic trouble codes, once the reconnaissance that finds the routine is what blocks it | 40m |
| | `reflash` | the RequestDownload / TransferData / RequestTransferExit sequence, and patching a calibration block | 50m |
| | `odometer` | WriteDataByIdentifier, and the second controller that remembers the mileage | 35m |
| | `gateway` | reading a central gateway's routing table to reach a bus the OBD connector is not on | 40m |
| Bluetooth and the Phone | `discovery` | scanning for advertisements, then walking a GATT table with `hcitool` and `gatttool` | 20m |
| | `descriptors` | the attribute table is larger than the characteristic list; reading descriptors | 20m |
| | `encoding` | recognising hex and base64 where a device stored bytes as text | 15m |
| | `fragments` | reassembling a record split across services, in index order rather than handle order | 25m |
| | `unlock` | writing to a characteristic, and reading the permission error when you write to the wrong one | 25m |
| | `sequence` | driving a stateful interlock that resets on a wrong step | 30m |
| | `notify` | enabling pushes by writing the CCCD, then listening | 20m |
| | `indicate` | indications are acknowledged, and stop until you confirm | 25m |
| | `stream` | reassembling notifications that arrive out of order | 25m |
| | `trigger` | subscribing before triggering, because a push has no queue | 20m |
| | `hidden-notify` | a declaration's properties are firmware's intent, not the stack's rule | 25m |
| | `beacon` | parsing AD structures out of a broadcast nobody has to connect to | 25m |
| | `scan-response` | the second payload a peripheral only sends when asked, and what asking costs | 25m |
| | `service-data` | AD structures are typed, and the type says where the data starts | 20m |
| | `hidden-handles` | a discovery response is a list the firmware chose to send; the handles work anyway | 25m |
| | `enrolment` | catching the seconds after a key card is presented, when the car enrols a new key without asking who is writing | 40m |
| | `relay` | forwarding a passive entry challenge to a phone the car cannot reach, inside the deadline meant to prove proximity | 40m |
| | `long-write` | Prepare and Execute Write, for a value one request cannot carry | 25m |
| Capstone | `pivot` | reaching an unreachable bus through the BLE dongle bridged onto it | 60m |

The dojo's front page sorts the same challenges a second way, by what they ask
of you rather than which interface they are on: following an instruction,
combining two things, finding what nobody told you, and defeating something
built to stop you. The module headers carry the same bands.

Roughly **eighteen hours** of hands-on time for a student comfortable with Linux
and Python; budget half again as long for one who is not. The modules are
independent of each other, but within a module the challenges assume the
earlier ones. `rolling-code` expects the capture discipline `fob-capture`
teaches, `integrity` expects the signal reverse engineering from `spoofing`,
and `gateway` and `firmware-dump` both expect the enumeration from
`ecu-discovery`.

## The bus is emulated in userspace

Workspace containers run under `runc` with only `SYS_PTRACE` (see
`dojo_plugin/api/v1/docker.py`), so a challenge cannot `ip link add dev vcan0
type vcan`, because that needs `CAP_NET_ADMIN`, which is only granted to
`privileged` challenges in dojos holding the `workspace_net_admin` permission.

So `shared/vcan.py` emulates the bus instead. A hub process, started as root by
each challenge's `.init`, listens on a unix socket at `/run/vcan/vcan0` and
broadcasts every frame it receives to every *other* attached client, which is
what a CAN transceiver sees on a real bus, including the absence of loopback to
the sender.

Frames cross that socket in can-utils notation, one per line:

    1A0#DEADBEEF00112233

The tools on top of it are the genuine article. `image/canshim.c`, carried by
the challenge image, intercepts the calls an `AF_CAN` socket would make and
routes them to that unix socket, so unmodified `candump`, `cansend`,
`cansniffer`, `canplayer` and `cangen` work against the emulated bus. A student
learns the real tools, and what they learn transfers to a real SocketCAN
interface unchanged. See `image/README.md`.

`shared/real-tools/` holds the one-line wrappers that put the shim in front of
each binary. `shared/tools/` holds python implementations: `canascii` and
`isotpreq`, which have no can-utils equivalent for what they do here;
`gatttool`, `hcitool` and `hcidump`, which are the whole of the Bluetooth
tooling, since there is no radio for BlueZ to talk to; and `candump` and
`cansend`, which nothing links to any more but which `image/README.md` still
documents as the fallback if the shim ever has to come out.

## Bluetooth is emulated the same way

A workspace has no Bluetooth controller and cannot create one -- an HCI device
needs `CAP_NET_ADMIN` too. So `shared/ble.py` supplies the radio's absence in
the same shape as the CAN hub: each peripheral listens on a unix socket named
after its address under `/run/bluetooth/`, and writes its advertising data
beside it so a scan can see it without connecting.

Advertising is real too: `Advertisement` builds AD structures -- length, type,
data -- and refuses a payload over the thirty-one bytes the air allows, which
is why anything larger than that goes out as a rotating sequence of payloads
the way a real beacon does. A scan reads the advertisement, and reads the scan
response only when it is active, and that distinction is enforced rather
than declared: the advertisement is written where any process can read it,
because it is broadcast, while the scan response is only ever produced as an
answer to a request sent to the peripheral. A passive scan never touches it.

Above that it is the real protocol. The PDUs are the ATT opcodes from the
Bluetooth Core Specification -- Read, Read Blob, Write, Find Information, Read
By Type, Read By Group Type -- with real handles, real UUIDs and real error
codes, and `shared/tools/gatttool` and `hcitool` take the BlueZ arguments and
print the BlueZ output.

One deliberate deviation: `gatttool --char-read` follows a full-length response
with Read Blob requests until it has the whole value. Real `gatttool` does not,
and truncates at MTU-1; every real *client stack* (bleak, Android, iOS) returns
the complete value. This dojo teaches BLE rather than BlueZ trivia, so it
behaves like the client stacks. `ble.Client.read_once()` is there for a single
untruncated-by-nobody transaction when a challenge wants to make the MTU
visible.

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
Symlinks must stay inside the dojo root. A symlinked directory is copied with
its contents, because the symlink branch of `resolved_tar` calls `tar.add`
without `recursive=False`, unlike the branch for ordinary files, which
passes it.

Every file placed in `/challenge` is made `root:root 4755` by the DOJO, so
anything a student should not read (the ECU firmware, and `isotp.py` in the
challenge whose objective is to implement ISO-TP) is `chmod 600`'d by `.init`.
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
challenge's win condition can also be exercised outside a container. Run the
hub and an `ecu` as root with `/run/vcan` writable and a `/flag` in place, then
talk to the socket with the tools in `shared/tools/`.
