CLANG=clang-18
OPT=opt-18
LLVM_AS=llvm-as-18

.PHONY: all test_licm.ll

all: clean

build/licm/LICMPass.so: licm/LICM.cpp
	mkdir -p build && \
	cd build && \
	cmake .. && \
	make && \
	cd ..

test.ll: test.c
	$(CLANG) -S -O1 -Xclang -disable-llvm-passes -emit-llvm -S test.c -o test.ll

test_mem2reg.ll: test.ll
	$(OPT) -passes=mem2reg -S test.ll -o test_mem2reg.ll

test_licm.ll: test_mem2reg.ll build/licm/LICMPass.so
	$(OPT) -load-pass-plugin build/licm/LICMPass.so -passes=licm-invariant -S test_mem2reg.ll -o test_licm.ll

test: test.ll
	$(CLANG) -o test.o -c test.ll
	$(CLANG) -o test test.o


clean:
	rm -f *.o
	rm -f *.bc
	rm -f *.opt.bc
	rm -f *.opt.ll
	rm -rf build
	rm -f test
	rm -f *.ll
	rm -f test_indvar_elim test_opt