// sample program that benefits from induction elimination
#include <iostream>
using namespace std;

int main() {
  int sum = 0;
  int n = 1000;

  for (int i = 0; i < n; ++i) {
    sum += 2 * i + 1;
  }

  cout << "Sum: " << sum << endl;
  return 0;
}