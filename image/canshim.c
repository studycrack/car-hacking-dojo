/*
 * Make the real can-utils talk to the userspace bus.
 *
 * A workspace container has no CAP_NET_ADMIN, so there is no vcan netdevice
 * for an AF_CAN socket to bind to. This intercepts the handful of calls the
 * can-utils make against such a socket and routes them to the hub's unix
 * socket instead, translating between struct can_frame and the hub's line
 * format. The tools themselves are unmodified.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <net/if.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/un.h>
#include <unistd.h>

#define MAX_FD 4096
#define LINE_MAX_LEN 64
#define FAKE_IFINDEX 42
#define SOCKET_DIR "/run/vcan"

struct can_state {
    int is_can;
    int bound;
    char ifname[IFNAMSIZ];
    struct can_filter *filters;
    int filter_count;
    int want_timestamp;
    char buffer[LINE_MAX_LEN * 8];
    size_t buffered;
};

static struct can_state states[MAX_FD];

/* the tools reach for an interface either by ioctl or by if_nametoindex, and
 * then bind by index, so both directions of the mapping have to exist */
#define MAX_INTERFACES 8
static char interface_names[MAX_INTERFACES][IFNAMSIZ];
static int interface_count;

static int index_for_name(const char *name)
{
    for (int slot = 0; slot < interface_count; slot++)
        if (strcmp(interface_names[slot], name) == 0)
            return FAKE_IFINDEX + slot;
    if (interface_count >= MAX_INTERFACES)
        return FAKE_IFINDEX;
    snprintf(interface_names[interface_count], IFNAMSIZ, "%s", name);
    return FAKE_IFINDEX + interface_count++;
}

static const char *name_for_index(int index)
{
    int slot = index - FAKE_IFINDEX;
    if (slot < 0 || slot >= interface_count)
        return NULL;
    return interface_names[slot];
}

unsigned int if_nametoindex(const char *name)
{
    if (strncmp(name, "vcan", 4) == 0 || strncmp(name, "can", 3) == 0)
        return index_for_name(name);
    unsigned int (*real)(const char *) = dlsym(RTLD_NEXT, "if_nametoindex");
    return real(name);
}

char *if_indextoname(unsigned int index, char *buffer)
{
    const char *name = name_for_index(index);
    if (name) {
        snprintf(buffer, IFNAMSIZ, "%s", name);
        return buffer;
    }
    char *(*real)(unsigned int, char *) = dlsym(RTLD_NEXT, "if_indextoname");
    return real(index, buffer);
}

static int (*real_socket)(int, int, int);
static int (*real_bind)(int, const struct sockaddr *, socklen_t);
static int (*real_ioctl)(int, unsigned long, ...);
static int (*real_setsockopt)(int, int, int, const void *, socklen_t);
static int (*real_close)(int);
static ssize_t (*real_read)(int, void *, size_t);
static ssize_t (*real_write)(int, const void *, size_t);
static ssize_t (*real_recvmsg)(int, struct msghdr *, int);
static ssize_t (*real_sendmsg)(int, const struct msghdr *, int);

static void resolve(void)
{
    if (real_socket)
        return;
    real_socket = dlsym(RTLD_NEXT, "socket");
    real_bind = dlsym(RTLD_NEXT, "bind");
    real_ioctl = dlsym(RTLD_NEXT, "ioctl");
    real_setsockopt = dlsym(RTLD_NEXT, "setsockopt");
    real_close = dlsym(RTLD_NEXT, "close");
    real_read = dlsym(RTLD_NEXT, "read");
    real_write = dlsym(RTLD_NEXT, "write");
    real_recvmsg = dlsym(RTLD_NEXT, "recvmsg");
    real_sendmsg = dlsym(RTLD_NEXT, "sendmsg");
}

static struct can_state *lookup(int fd)
{
    if (fd < 0 || fd >= MAX_FD || !states[fd].is_can)
        return NULL;
    return &states[fd];
}

static void send_filters(int fd, struct can_state *state)
{
    if (state->filter_count <= 0)
        return;
    char line[512];
    int offset = snprintf(line, sizeof(line), "!");
    for (int index = 0; index < state->filter_count && offset < (int)sizeof(line) - 24; index++)
        offset += snprintf(line + offset, sizeof(line) - offset, "%s%X:%X",
                           index ? "," : "",
                           state->filters[index].can_id & ~CAN_INV_FILTER,
                           state->filters[index].can_mask);
    offset += snprintf(line + offset, sizeof(line) - offset, "\n");
    real_write(fd, line, offset);
}

int socket(int domain, int type, int protocol)
{
    resolve();
    if (domain != AF_CAN || protocol != CAN_RAW)
        return real_socket(domain, type, protocol);

    int fd = real_socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0 || fd >= MAX_FD)
        return fd;
    memset(&states[fd], 0, sizeof(states[fd]));
    states[fd].is_can = 1;
    strcpy(states[fd].ifname, "vcan0");
    return fd;
}

int ioctl(int fd, unsigned long request, ...)
{
    resolve();
    va_list arguments;
    va_start(arguments, request);
    void *argument = va_arg(arguments, void *);
    va_end(arguments);

    struct can_state *state = lookup(fd);
    if (!state)
        return real_ioctl(fd, request, argument);

    struct ifreq *request_data = argument;
    if (request == SIOCGIFINDEX) {
        memcpy(state->ifname, request_data->ifr_name, IFNAMSIZ - 1);
        state->ifname[IFNAMSIZ - 1] = '\0';
        request_data->ifr_ifindex = index_for_name(state->ifname);
        return 0;
    }
    if (request == SIOCGIFNAME) {
        // candump resolves the index carried on each frame back to a name
        snprintf(request_data->ifr_name, IFNAMSIZ, "%s", state->ifname);
        return 0;
    }
    return real_ioctl(fd, request, argument);
}

int bind(int fd, const struct sockaddr *address, socklen_t length)
{
    resolve();
    struct can_state *state = lookup(fd);
    if (!state)
        return real_bind(fd, address, length);

    if (length >= sizeof(struct sockaddr_can)) {
        const struct sockaddr_can *requested = (const struct sockaddr_can *)address;
        const char *name = name_for_index(requested->can_ifindex);
        if (name)
            snprintf(state->ifname, IFNAMSIZ, "%s", name);
    }

    struct sockaddr_un target;
    memset(&target, 0, sizeof(target));
    target.sun_family = AF_UNIX;
    snprintf(target.sun_path, sizeof(target.sun_path), "%s/%s", SOCKET_DIR, state->ifname);

    int (*real_connect)(int, const struct sockaddr *, socklen_t) = dlsym(RTLD_NEXT, "connect");
    if (real_connect(fd, (struct sockaddr *)&target, sizeof(target)) < 0)
        return -1;
    state->bound = 1;
    send_filters(fd, state);
    return 0;
}

int setsockopt(int fd, int level, int option, const void *value, socklen_t length)
{
    resolve();
    struct can_state *state = lookup(fd);
    if (!state)
        return real_setsockopt(fd, level, option, value, length);
    if (level == SOL_SOCKET && (option == SO_TIMESTAMP || option == SO_TIMESTAMPNS)) {
        state->want_timestamp = option;
        return 0;
    }
    if (level != SOL_CAN_RAW)
        return 0;

    if (option == CAN_RAW_FILTER) {
        free(state->filters);
        state->filter_count = length / sizeof(struct can_filter);
        state->filters = malloc(length ? length : 1);
        if (state->filters)
            memcpy(state->filters, value, length);
        else
            state->filter_count = 0;
        if (state->bound)
            send_filters(fd, state);
    }
    return 0;
}

int close(int fd)
{
    resolve();
    struct can_state *state = lookup(fd);
    if (state) {
        free(state->filters);
        memset(state, 0, sizeof(*state));
    }
    return real_close(fd);
}

static int passes_filters(struct can_state *state, canid_t can_id)
{
    if (state->filter_count == 0)
        return 1;
    for (int index = 0; index < state->filter_count; index++) {
        struct can_filter *filter = &state->filters[index];
        int inverted = !!(filter->can_id & CAN_INV_FILTER);
        canid_t wanted = filter->can_id & ~CAN_INV_FILTER;
        int matched = ((can_id & filter->can_mask) == (wanted & filter->can_mask));
        if (matched != inverted)
            return 1;
    }
    return 0;
}

static int take_line(struct can_state *state, char *line, size_t size)
{
    char *newline = memchr(state->buffer, '\n', state->buffered);
    if (!newline)
        return 0;
    size_t length = newline - state->buffer;
    if (length >= size)
        length = size - 1;
    memcpy(line, state->buffer, length);
    line[length] = '\0';
    size_t consumed = (newline - state->buffer) + 1;
    memmove(state->buffer, state->buffer + consumed, state->buffered - consumed);
    state->buffered -= consumed;
    return 1;
}

static int parse_line(const char *line, struct can_frame *frame)
{
    const char *hash = strchr(line, '#');
    if (!hash)
        return 0;
    memset(frame, 0, sizeof(*frame));
    frame->can_id = strtoul(line, NULL, 16);

    const char *payload = hash + 1;
    size_t digits = strlen(payload);
    size_t length = digits / 2;
    if (length > 8)
        length = 8;
    for (size_t index = 0; index < length; index++) {
        char byte[3] = {payload[index * 2], payload[index * 2 + 1], '\0'};
        frame->data[index] = (unsigned char)strtoul(byte, NULL, 16);
    }
    frame->can_dlc = length;
    return 1;
}

static ssize_t receive_frame(int fd, struct can_state *state, void *destination, size_t size)
{
    if (size < sizeof(struct can_frame)) {
        errno = EINVAL;
        return -1;
    }

    for (;;) {
        char line[LINE_MAX_LEN];
        while (take_line(state, line, sizeof(line))) {
            struct can_frame frame;
            if (!parse_line(line, &frame))
                continue;
            memcpy(destination, &frame, sizeof(frame));
            return sizeof(frame);
        }

        if (state->buffered >= sizeof(state->buffer)) {
            state->buffered = 0;
            continue;
        }
        ssize_t got = real_read(fd, state->buffer + state->buffered,
                                sizeof(state->buffer) - state->buffered);
        if (got <= 0)
            return got;
        state->buffered += got;
    }
}

static ssize_t send_frame(int fd, struct can_state *state, const void *source, size_t size)
{
    (void)state;
    if (size < sizeof(struct can_frame)) {
        errno = EINVAL;
        return -1;
    }
    const struct can_frame *frame = source;
    char line[LINE_MAX_LEN];
    int offset = snprintf(line, sizeof(line), "%03X#", frame->can_id & CAN_SFF_MASK);
    int length = frame->can_dlc > 8 ? 8 : frame->can_dlc;
    for (int index = 0; index < length; index++)
        offset += snprintf(line + offset, sizeof(line) - offset, "%02X", frame->data[index]);
    offset += snprintf(line + offset, sizeof(line) - offset, "\n");

    if (real_write(fd, line, offset) < 0)
        return -1;
    return sizeof(struct can_frame);
}

ssize_t read(int fd, void *destination, size_t size)
{
    resolve();
    struct can_state *state = lookup(fd);
    if (!state || !state->bound)
        return real_read(fd, destination, size);
    return receive_frame(fd, state, destination, size);
}

ssize_t write(int fd, const void *source, size_t size)
{
    resolve();
    struct can_state *state = lookup(fd);
    if (!state || !state->bound)
        return real_write(fd, source, size);
    return send_frame(fd, state, source, size);
}

ssize_t recv(int fd, void *destination, size_t size, int flags)
{
    (void)flags;
    return read(fd, destination, size);
}

ssize_t recvfrom(int fd, void *destination, size_t size, int flags,
                 struct sockaddr *address, socklen_t *address_length)
{
    resolve();
    struct can_state *state = lookup(fd);
    if (!state || !state->bound) {
        ssize_t (*real_recvfrom)(int, void *, size_t, int, struct sockaddr *, socklen_t *) =
            dlsym(RTLD_NEXT, "recvfrom");
        return real_recvfrom(fd, destination, size, flags, address, address_length);
    }
    if (address && address_length && *address_length >= sizeof(struct sockaddr_can)) {
        struct sockaddr_can source;
        memset(&source, 0, sizeof(source));
        source.can_family = AF_CAN;
        source.can_ifindex = FAKE_IFINDEX;
        memcpy(address, &source, sizeof(source));
        *address_length = sizeof(source);
    }
    return receive_frame(fd, state, destination, size);
}

ssize_t send(int fd, const void *source, size_t size, int flags)
{
    (void)flags;
    return write(fd, source, size);
}

ssize_t sendto(int fd, const void *source, size_t size, int flags,
               const struct sockaddr *address, socklen_t address_length)
{
    resolve();
    struct can_state *state = lookup(fd);
    if (!state || !state->bound) {
        ssize_t (*real_sendto)(int, const void *, size_t, int, const struct sockaddr *, socklen_t) =
            dlsym(RTLD_NEXT, "sendto");
        return real_sendto(fd, source, size, flags, address, address_length);
    }
    return send_frame(fd, state, source, size);
}

ssize_t recvmsg(int fd, struct msghdr *message, int flags)
{
    resolve();
    struct can_state *state = lookup(fd);
    if (!state || !state->bound)
        return real_recvmsg(fd, message, flags);

    if (message->msg_iovlen < 1) {
        errno = EINVAL;
        return -1;
    }
    ssize_t got = receive_frame(fd, state, message->msg_iov[0].iov_base,
                                message->msg_iov[0].iov_len);
    if (got > 0) {
        message->msg_flags = 0;
        // candump -l stamps each logged frame from this ancillary data
        struct cmsghdr *header = CMSG_FIRSTHDR(message);
        if (state->want_timestamp && header &&
            message->msg_controllen >= CMSG_SPACE(sizeof(struct timeval))) {
            struct timeval now;
            gettimeofday(&now, NULL);
            header->cmsg_level = SOL_SOCKET;
            header->cmsg_type = SO_TIMESTAMP;
            header->cmsg_len = CMSG_LEN(sizeof(now));
            memcpy(CMSG_DATA(header), &now, sizeof(now));
            message->msg_controllen = CMSG_SPACE(sizeof(now));
        } else {
            message->msg_controllen = 0;
        }
        if (message->msg_name && message->msg_namelen >= sizeof(struct sockaddr_can)) {
            struct sockaddr_can source;
            memset(&source, 0, sizeof(source));
            source.can_family = AF_CAN;
            source.can_ifindex = FAKE_IFINDEX;
            memcpy(message->msg_name, &source, sizeof(source));
            message->msg_namelen = sizeof(source);
        }
    }
    return got;
}

ssize_t sendmsg(int fd, const struct msghdr *message, int flags)
{
    resolve();
    struct can_state *state = lookup(fd);
    if (!state || !state->bound)
        return real_sendmsg(fd, message, flags);
    if (message->msg_iovlen < 1) {
        errno = EINVAL;
        return -1;
    }
    return send_frame(fd, state, message->msg_iov[0].iov_base, message->msg_iov[0].iov_len);
}
