// Deployment adapter: the verifier itself is included unchanged.
// The parent never checks a proof; each fork inherits pristine verifier globals.
#define main vipr_original_main
#include "../dependencies/research86/dependencies/vipr/viprchk.cpp"
#undef main
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <iomanip>

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) != "--stream")
        return vipr_original_main(argc, argv);
    if (argc != 2) return 2;
    std::string path;
    while (std::getline(std::cin, path)) {
        std::cout.flush(); std::cerr.flush();
        pid_t child = fork();
        if (child < 0) return 3;
        if (child == 0) {
            alarm(10);
            int quiet = open("/dev/null", O_WRONLY);
            dup2(quiet, STDOUT_FILENO); dup2(quiet, STDERR_FILENO); close(quiet);
            char *args[] = {argv[0], const_cast<char *>(path.c_str())};
            int status = vipr_original_main(2, args);
            _exit(status);
        }
        int status = 0;
        struct rusage usage;
        if (wait4(child, &status, 0, &usage) != child) return 4;
        int code = WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
        double cpu = usage.ru_utime.tv_sec + usage.ru_utime.tv_usec/1e6
                   + usage.ru_stime.tv_sec + usage.ru_stime.tv_usec/1e6;
        std::cout << code << " " << std::setprecision(12) << cpu << std::endl;
    }
    return 0;
}
