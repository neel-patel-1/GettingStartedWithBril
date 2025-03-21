CLANG=clang++-18
OPT=opt-18
LLVM_AS=llvm-as-18

build/licm/LICMPass.so: licm/LICM.cpp
	mkdir -p build && \
	cd build && \
	cmake .. && \
	make && \
	cd ..

.PHONY: test_impl test test_indvar_elim test.ll clean test.ll

test_impl: test test_indvar_elim
	@echo "Optimized:"
	./test_indvar_elim
	@echo "Original:"
	./test

test_indvar_impl: test_indvar_elim
	@echo "Optimized:"
	./test_indvar_elim

test.ll: test.cpp
	$(CLANG) -g -O0 -Xclang -disable-llvm-passes -emit-llvm -S test.cpp -o test.ll

test: test.ll
	$(CLANG) -o test.o -c test.ll
	$(CLANG) -o test test.o

test_indvar_elim: test.ll build/licm/LICMPass.so
	$(OPT) -load-pass-plugin=build/licm/LICMPass.so -passes="licm-invariant" -S test.ll > test.opt.ll
	$(LLVM_AS) -o test.opt.bc test.opt.ll
	$(CLANG) -o test_indvar_elim.o -c test.opt.bc
	$(CLANG) -o test_indvar_elim test_indvar_elim.o

clean:
	rm -f *.o
	rm -f *.bc
	rm -f *.opt.bc
	rm -f *.opt.ll
	rm -rf build
	rm -f test
	rm -f *.ll
	rm -f test_indvar_elim test_opt