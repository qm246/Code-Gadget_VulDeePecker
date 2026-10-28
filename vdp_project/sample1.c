#include <string.h>
#include <stdio.h>

void greet(char *name) {
  char buf[16];
  strcpy(buf, name);
  printf("hi %s\n", buf);
}

int main(int argc, char **argv) {
  char tmp[64];
  memcpy(tmp, argv[1], 8);
  greet(argv[1]);
  return 0;
}