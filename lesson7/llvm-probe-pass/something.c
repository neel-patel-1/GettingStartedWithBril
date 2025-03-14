#include <stdio.h>

int main(){

	printf("foo\n");
	int a = 0;
	for (int i = 0; i < 10; i++) {
		a += i;
	}
	printf("a = %d\n", a);
	int b = 0;
	for (int i = 0; i < 10; i++) {
		b += i * 2;
	}
	printf("b = %d\n", b);
	int c = 0;
	for (int i = 0; i < 10; i++) {
		c += i * 3;
	}
	printf("c = %d\n", c);
	int d = 0;
	for (int i = 0; i < 10; i++) {
		d += i * 4;
	}
	printf("d = %d\n", d);
	return 0;

}