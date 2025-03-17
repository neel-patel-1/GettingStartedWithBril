// sample program that benefits from induction elimination
#include <iostream>
#include <x86intrin.h>
#include <stdint.h>
using namespace std;
volatile int g_v = 0;

uint64_t func(){
  uint64_t start, end;

  start = __rdtsc();
  int x, y, z, w, a, b, c, d, e, f, g, h, j, k, l, m, n, o, p;
  for (int i = 0; i < 1000000000; ++i) {
    // This loop is a simple induction variable
    // that can be optimized by LICM.
    x = 2 * i + 1;
    y = 3 * i + 2;
    z = 4 * i + 3;
    w = 5 * i + 4;
    a = 6 * i + 5;
    b = 7 * i + 6;
    c = 8 * i + 7;
    d = 9 * i + 8;
    e = 10 * i + 9;
    f = 11 * i + 10;
    g = 12 * i + 11;
    h = 13 * i + 12;
    j = 14 * i + 13;
    k = 15 * i + 14;
    l = 16 * i + 15;
    m = 17 * i + 16;
    n = 18 * i + 17;
    o = 19 * i + 18;
    p = 20 * i + 19;
  }
  g_v = x + y + z + w + a + b + c + d + e + f + g + h + j + k + l + m + n + o + p;
  end = __rdtsc();
  return end - start;
}

int main() {
  int sum = 0;
  int n = 1000;

  uint64_t time = func();
  cout << "Time: " << time << " cycles" << endl;
  return 0;
}