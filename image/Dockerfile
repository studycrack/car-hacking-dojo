# The challenge image for the car hacking dojo.
#
# It exists to carry the real can-utils plus the shim that lets them talk to
# the dojo's userspace bus. Challenge logic stays in the repository -- the DOJO
# copies it into /challenge at container start -- so this image changes rarely.
FROM ubuntu:24.04 AS build

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gcc libc6-dev \
 && rm -rf /var/lib/apt/lists/*

COPY canshim.c /build/canshim.c
RUN gcc -shared -fPIC -O2 -Wall -o /build/canshim.so /build/canshim.c -ldl


FROM ubuntu:24.04

# 24.04 ships an "ubuntu" account on uid 1000, which is the uid the dojo runs
# the student as. Leaving it makes every prompt read ubuntu@ instead of
# hacker@, and getpwuid(1000) hand out /home/ubuntu as the home directory.
RUN userdel --remove ubuntu

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        can-utils \
        binutils \
        python3 \
        python3-pip \
        xxd \
        dbus \
        bluez \
 && rm -rf /var/lib/apt/lists/*

# bluez is here for bluetoothctl, which drives org.bluez over D-Bus and so
# works against shared/bluez.py exactly as it would against a real controller.
#
# The rest of the package is not wanted. hcitool, gatttool and friends are
# deprecated upstream and talk to an HCI socket that does not exist here, and
# the first two would collide by name with the emulations in shared/tools that
# the challenges actually use. bluetoothd has to go as well: it would contend
# for the org.bluez name the shim owns, and its D-Bus activation file would let
# something start it by accident.
RUN rm -f /usr/bin/hcitool /usr/bin/gatttool /usr/bin/hciconfig \
          /usr/bin/sdptool /usr/bin/rfcomm /usr/bin/ciptool \
          /usr/bin/hciattach /usr/bin/btattach /usr/bin/l2ping \
          /usr/bin/l2test /usr/bin/rctest /usr/bin/bluemoon \
          /usr/bin/hex2hcd /usr/bin/obexctl /usr/bin/mpris-proxy \
          /usr/sbin/bluetoothd /usr/libexec/bluetooth/bluetoothd \
          /usr/share/dbus-1/system-services/org.bluez.service

# cantools pulls python-can in with it. Installing the distribution's
# python-can as well leaves pip trying to replace a package it did not install,
# which it refuses to do.
RUN pip3 install --no-cache-dir --break-system-packages cantools bleak \
 && apt-get purge -y python3-pip \
 && apt-get autoremove -y

COPY --from=build /build/canshim.so /opt/canshim.so
COPY wrappers/ /opt/can-wrappers/
RUN chmod 755 /opt/can-wrappers/*

# the bus that shared/bluez.py serves org.bluez on, so bleak has something to
# talk to. The stock system policy only lets the bluetooth user own that name.
COPY dbus.conf /opt/dbus.conf
