// Memory-only deployment adapter. Algorithm unchanged; retain final verifier
// state until the observer samples simultaneous parent/child RSS.
#define main vipr_original_main
#include "../dependencies/research86/dependencies/vipr/viprchk.cpp"
#undef main
#include <unistd.h>
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    alarm(10);
    int status = vipr_original_main(argc, argv);
    std::cout << "MEMORY_CHECKPOINT " << status << std::endl;
    std::cin.get();
    return status;
}
