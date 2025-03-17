build/licm/LICMPass.so: licm/LICM.cpp
	mkdir -p build && \
	cd build && \
	cmake .. && \
	make && \
	cd ..

.PHONY: test_impl test test_opt

test_impl: test test_opt
	@echo "Optimized:"
	./test_opt
	@echo "Original:"
	./test

test: test.cpp build/licm/LICMPass.so
	clang++-18 -g -fPIE -O0 -emit-llvm -c test.cpp -o test.bc
	llvm-dis-18 -o test.ll test.bc
	clang++-18 -o test.o -c test.bc
	clang++-18 -fPIE -pie -o test test.o

test_opt: test build/licm/LICMPass.so
	opt-18 -load-pass-plugin=build/licm/LICMPass.so -passes=licm-indvar-elim -S test.ll > test.opt.ll
	llvm-as-18 -o test.opt.bc test.opt.ll
	clang++-18 -o test_opt.o -c test.opt.bc
	clang++-18 -fPIE -pie -o test_opt test_opt.o

clean:
	rm -f *.o
	rm -f *.bc
	rm -f *.opt.bc
	rm -f *.opt.ll
	rm -rf build
	rm -f test
	rm -f *.ll