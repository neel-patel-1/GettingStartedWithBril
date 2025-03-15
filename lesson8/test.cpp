// sample program that benefits from induction elimination
#include <iostream>
using namespace std;

void func(){
  for (int i = 0; i < 1000; ++i) {
    // This loop is a simple induction variable
    // that can be optimized by LICM.
    int x = 2 * i + 1;
  }
  printf("done\n");
}

int main() {
  int sum = 0;
  int n = 1000;

  for (int i = 0; i < n; ++i) {
    sum += 2 * i + 1;
  }

  cout << "Sum: " << sum << endl;
  return 0;
}