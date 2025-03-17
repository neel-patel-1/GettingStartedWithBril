PASSES=loop-simplify,indvars,lcssa
build/licm/LICMPass.so: licm/LICM.cpp
	mkdir -p build && \
	cd build && \
	cmake .. && \
	make && \
	cd ..

.PHONY: test_impl test test_indvar_elim test_dependent_passes.ll clean

test_impl: test test_indvar_elim
	@echo "Optimized:"
	./test_indvar_elim
	@echo "Original:"
	./test

test: test.cpp build/licm/LICMPass.so
	clang++-18 -g -fPIE -O2 -emit-llvm -c test.cpp -o test.bc
	llvm-dis-18 -o test.ll test.bc
	opt-18 -O2 -S test.bc > test.ll
	clang++-18 -o test.o -c test.bc
	clang++-18 -fPIE -pie -o test test.o

test_dependent_passes.ll: test.ll
	@cp test.ll test_dependent_passes.ll

test_indvar_elim: test_dependent_passes.ll build/licm/LICMPass.so
	opt-18 -load-pass-plugin=build/licm/LICMPass.so -passes="licm-indvar-elim" -S test_dependent_passes.ll > test.opt.ll
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