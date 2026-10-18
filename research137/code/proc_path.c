/* Compatibility for hosts where getpid() and /proc numeric PIDs disagree.
   Only executable-path discovery is redirected; no Lean/kernel logic changes. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <string.h>
#include <unistd.h>
ssize_t readlink(const char *path, char *buf, size_t size) {
    ssize_t (*original)(const char *, char *, size_t) = dlsym(RTLD_NEXT, "readlink");
    size_t n = strlen(path);
    if (n > 10 && !strncmp(path, "/proc/", 6) && !strcmp(path + n - 4, "/exe"))
        return original("/proc/self/exe", buf, size);
    return original(path, buf, size);
}
