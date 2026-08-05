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
        python3-can \
        python3-pip \
        xxd \
 && pip3 install --no-cache-dir --break-system-packages cantools \
 && apt-get purge -y python3-pip \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /build/canshim.so /opt/canshim.so
COPY wrappers/ /opt/can-wrappers/
RUN chmod 755 /opt/can-wrappers/*
