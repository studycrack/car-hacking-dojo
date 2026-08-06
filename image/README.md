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

## bleak, and why bettercap is not here

The Bluetooth here is emulated in userspace: a peripheral is a unix socket
under `/run/bluetooth`, and `shared/tools/{hcitool,gatttool,hcidump}` speak to
it directly. `bleak` does not know any of that exists.

`bleak` is made to work by `shared/bluez.py`, which every BLE challenge's
`.init` starts alongside a private `dbus-daemon` (`/opt/dbus.conf`). The shim
owns the name `org.bluez` and presents the object tree BlueZ presents --- an
adapter, a device per peripheral, a GATT tree per connection --- implementing
each method against `ble.Client` underneath. `bleak` cannot tell the
difference: scanning, connecting, reads (including the Read Blob continuation
for long values), descriptors, notifications and Prepare/Execute long writes
all behave as they would against a real controller.

The `canshim.c` trick does not transfer here, which is why this is a service
rather than a `LD_PRELOAD`. `bleak` is not making socket calls to a device
node; it is making method calls to a name on the system bus. So the shim is
that name.

`bluetoothctl` gets the same benefit for free, because it is a D-Bus client
too: `scan on`, `connect`, and the `gatt` menu all work against the shim. It
prints one `Unable to open mgmt_socket` line on startup --- that socket is for
adapter configuration, and nothing below it needs one.

`bluetoothctl` is the only part of the `bluez` package that survives; the
Dockerfile deletes the rest. `hcitool`, `gatttool`, `hciconfig` and the other
legacy tools are deprecated upstream and drive an HCI socket that does not
exist here, and the first two would shadow or be shadowed by the emulations in
`shared/tools` depending on how `PATH` resolved. `btmon` and `btmgmt` are
current tools rather than legacy ones, but they want those same HCI and
management sockets, and nothing here needs them: no challenge mentions either,
and the packet view `btmon` would give is what the `hcidump` emulation already
provides. `bluetoothd` goes too --- it would contend for the `org.bluez` name
the shim owns, and its D-Bus activation file would let something start it by
accident.

The rule the image follows is that a tool present is a tool that works. A
scan that silently returns nothing teaches a student the wrong thing about the
peripheral in front of them.

`bettercap` was installed here for a while and has been taken out again,
because nothing could make it work and a tool that silently finds nothing is
worse than a tool that is absent. The reasoning, so that it does not get added
back on the assumption that it was an oversight:

Its BLE modules open an HCI socket and drive a controller directly, below the
D-Bus layer the shim provides. Three ways to bridge that, none of them
available:

- A `LD_PRELOAD` shim, as on the CAN side, cannot work at all. bettercap is Go
  and its runtime issues raw syscalls; the binary imports 167 dynamic symbols
  and not one of them is `socket`, `bind` or `connect`. There is nothing to
  interpose on.
- A virtual controller through `/dev/vhci` is the clean answer, and would make
  bettercap, real BlueZ and the real `hcitool` all work natively. It needs the
  device node and `CAP_NET_ADMIN`. The platform grants `SYS_PTRACE` alone and
  allows `/dev/kvm` and `/dev/net/tun` only (`dojo_plugin/api/v1/docker.py`),
  and none of that is reachable from `dojo.yml`.
- A ptrace supervisor could intercept the HCI socket, since `SYS_PTRACE` is
  granted, but it would mean implementing HCI and L2CAP underneath the ATT
  layer that is already emulated, driven through ptrace over a multi-threaded
  Go runtime. Far more machinery than the shim, for a tool no challenge uses.

If the platform ever exposes `/dev/vhci` and `CAP_NET_ADMIN`, the second
option becomes nearly free and is the one to take.

## What the image does not solve

`isotpsend`, `isotprecv` and `isotpdump` use `CAN_ISOTP`, a separate kernel
protocol that does segmentation and reassembly in the kernel rather than in the
tool. Supporting them means implementing the ISO-TP state machine inside the
shim. The dojo's `shared/isotp.py` already has one, so it is a port rather than
a design problem, but it is not done here.
