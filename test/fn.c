#include <stdlib.h>

float foo(int32_t a, int32_t b) {
  return a * b + 1337.0;
}

int32_t bar(int32_t a, float b) {
  return (int32_t)(a / b - 10);
}

