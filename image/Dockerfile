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
 && rm -rf /var/lib/apt/lists/*

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
