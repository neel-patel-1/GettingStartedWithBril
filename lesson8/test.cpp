#include <stdio.h>

volatile int sink;  // Prevent removal of computed result

void foo() {
    int sum = 0;
    // A simple loop with an induction variable 'i'
    for (int i = 0; i < 1000; i++) {
        // Compute an affine expression: 2*i + 1
        int x = 2 * i + 1;
        sum += x;
    }
    // Store the result in a volatile global variable.
    sink = sum;
}

int main() {
    foo();
    printf("Sum: %d\n", sink);
    return 0;
}
