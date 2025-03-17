build/licm/LICMPass.so: licm/LICM.cpp
	mkdir -p build && \
	cd build && \
	cmake .. && \
	make && \
	cd ..

.PHONY: test_impl test test_indvar_elim test_dependent_passes.ll clean test.ll

test_impl: test test_indvar_elim
	@echo "Optimized:"
	./test_indvar_elim
	@echo "Original:"
	./test

test.ll: test.cpp
	clang++-18 -g -O0 -emit-llvm -S test.cpp -o test.ll

test: test.ll
	clang++-18 -o test.o -c test.ll
	clang++-18 -o test test.o

test_indvar_elim: test_dependent_passes.ll build/licm/LICMPass.so
	opt-18 -load-pass-plugin=build/licm/LICMPass.so -passes="licm-indvar-elim" -S test.ll > test.opt.ll
	llvm-as-18 -o test.opt.bc test.opt.ll
	clang++-18 -o test_indvar_elim.o -c test.opt.bc
	clang++-18 -fPIE -pie -o test_indvar_elim test_indvar_elim.o

clean:
	rm -f *.o
	rm -f *.bc
	rm -f *.opt.bc
	rm -f *.opt.ll
	rm -rf build
	rm -f test
	rm -f *.ll