#define _DEFAULT_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>

/* Small launcher; checker exit is unmodified except for the frozen time cap.
   wait4 reports the child lifetime, including fork/exec, not a tree snapshot. */
int main(int argc, char **argv) {
    if (argc < 4) return 2;
    pid_t child = fork();
    if (child < 0) return 3;
    if (child == 0) {
        int fd = open(argv[1], O_WRONLY | O_CREAT | O_TRUNC, 0600);
        if (fd < 0) _exit(4);
        dup2(fd, STDOUT_FILENO); dup2(fd, STDERR_FILENO); close(fd);
        alarm(30);
        execvp(argv[2], &argv[2]); _exit(127);
    }
    int status; struct rusage child_usage, self_usage;
    while (wait4(child, &status, 0, &child_usage) < 0) {
        if (errno != EINTR) return 5;
    }
    getrusage(RUSAGE_SELF, &self_usage);
    double cpu = child_usage.ru_utime.tv_sec + child_usage.ru_utime.tv_usec / 1e6
               + child_usage.ru_stime.tv_sec + child_usage.ru_stime.tv_usec / 1e6;
    printf("{\"exit\":%d,\"child_maxrss_kib\":%ld,\"launcher_maxrss_kib\":%ld,\"child_cpu\":%.9f}\n",
           WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status),
           child_usage.ru_maxrss, self_usage.ru_maxrss, cpu);
    return 0;
}
