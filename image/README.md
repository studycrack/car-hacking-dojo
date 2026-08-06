# Challenge image

Carries the real [can-utils](https://github.com/linux-can/can-utils) and the
shim that lets them run against the dojo's userspace bus.

## Why a shim is needed

`candump` and friends open `AF_CAN` sockets and bind them to a `vcan`
netdevice. Creating that netdevice needs `CAP_NET_ADMIN`, which a workspace
container does not get (`dojo_plugin/api/v1/docker.py` grants `SYS_PTRACE`
only). So there is nothing for a real CAN socket to bind to.

`canshim.c` intercepts the calls the tools make against such a socket and
routes them to the hub's unix socket instead:

| Intercepted | Why |
| --- | --- |
| `socket(AF_CAN, …, CAN_RAW)` | hand back a unix socket instead |
| `ioctl(SIOCGIFINDEX)` / `if_nametoindex` | the two ways the tools resolve an interface |
| `ioctl(SIOCGIFNAME)` / `if_indextoname` | `candump` maps the index on each frame back to a name |
| `bind(sockaddr_can)` | connect to `/run/vcan/<interface>` |
| `setsockopt(CAN_RAW_FILTER)` | forwarded to the hub |
| `read`/`recv`/`recvmsg` and `write`/`send`/`sendmsg` | translate between `struct can_frame` and the hub's line format |
| `setsockopt(SO_TIMESTAMP)` + `recvmsg` ancillary data | `candump -l` stamps each logged frame from it |

Filtering is deliberately **not** done in the shim. A reader that discards
unwanted frames itself has to block waiting for a wanted one, which breaks the
promise `select()` made to the caller and leaves the process unkillable. The
hub applies the filter instead, exactly as the kernel would, so every readable
byte is a frame the reader asked for.

## Building and publishing

The image must be **public**: the platform's pull worker authenticates with
pwn.college's own registry credentials, so it cannot see a private image of
yours.

```bash
cd image
docker build -t <account>/challenge-can:v1 .
docker push <account>/challenge-can:v1
```

Then point the dojo at it, once, at the top level of `dojo.yml`:

```yaml
image: <account>/challenge-can:v1
```

Use a real tag rather than `latest`; the platform pulls onto every workspace
node independently, and a moved tag leaves nodes disagreeing about what they
are running.

## Opting a challenge in

The dojo puts `/run/challenge/bin` ahead of everything else on `PATH`, so a
challenge keeps using the repository's python tools for as long as its `bin/`
symlinks point at `shared/tools`. Switching one challenge over means pointing
them at `shared/real-tools` instead:

```bash
cd can-bus/sniffing/bin
rm candump cansend
ln -s ../../../shared/real-tools/candump candump
ln -s ../../../shared/real-tools/cansend cansend
```

That makes the migration challenge-by-challenge and trivially reversible --
point the symlinks back at `shared/tools` and the challenge is on the python
tools again.

**Do not symlink to `/opt` directly.** `dojo_clone` runs `_assert_no_symlinks`
over the whole repository and refuses anything that resolves outside it, so a
symlink into the image rejects the entire dojo update (and rolls it back). The
wrappers therefore live in `shared/real-tools/` as ordinary files in the
repository, and it is those that set `LD_PRELOAD` and exec the real binary.
`/opt/can-wrappers/` in the image does the same thing and is there for use
inside the container, but nothing in the repository may point at it.

## bleak and bettercap

Both are installed, and neither can reach this dojo's peripherals.

The Bluetooth here is emulated in userspace: a peripheral is a unix socket
under `/run/bluetooth`, and `shared/tools/{hcitool,gatttool,hcidump}` speak to
it directly. `bleak` goes through BlueZ over D-Bus and `bettercap`'s BLE
modules open an HCI socket, so both want a controller the container does not
have --- the same missing `CAP_NET_ADMIN` that made `canshim.c` necessary on
the CAN side, plus no Bluetooth hardware to give it.

There is no shim for this. Making `bleak` work would mean standing up a fake
`org.bluez` on the system bus and exposing the emulated peripherals through
it, which is a much larger piece of work than intercepting a handful of
socket calls.

So they are here as the real tools, for reference and for anyone pointing a
workspace at actual hardware. Every BLE challenge is solved with the shipped
tools or with `ble.py`, and nothing in the dojo asks for either of these.

## What the image does not solve

`isotpsend`, `isotprecv` and `isotpdump` use `CAN_ISOTP`, a separate kernel
protocol that does segmentation and reassembly in the kernel rather than in the
tool. Supporting them means implementing the ISO-TP state machine inside the
shim. The dojo's `shared/isotp.py` already has one, so it is a port rather than
a design problem, but it is not done here.
