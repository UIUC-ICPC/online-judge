#include <sys/wait.h>
#include <unistd.h>

int main() {
  pid_t pid = fork();

  if (pid < 0) {
    return 1;
  }

  if (pid == 0) {
    return 0;
  }

  wait(nullptr);
}
