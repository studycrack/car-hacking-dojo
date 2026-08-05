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

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        can-utils \
        binutils \
        python3 \
        python3-can \
        xxd \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /build/canshim.so /opt/canshim.so
COPY wrappers/ /opt/can-wrappers/
RUN chmod 755 /opt/can-wrappers/*
