build/licm/LICMPass.so: licm/LICM.cpp
	mkdir -p build && \
	cd build && \
	cmake .. && \
	make && \
	cd ..

.PHONY: test

test: test.cpp build/licm/LICMPass.so
	clang++-18 -g -fPIE -emit-llvm -c test.cpp -o test.bc
	llvm-dis-18 -o test.ll test.bc
	opt-18 -load-pass-plugin=build/licm/LICMPass.so -passes=skeleton-pass < test.ll > test.opt.bc
	llvm-dis-18 -o test.opt.ll test.opt.bc
	clang++-18 -o test.o -c test.bc
	clang++-18 -fPIE -pie -o test test.o

clean:
	rm -f *.o
	rm -f *.bc
	rm -f *.opt.bc
	rm -f *.opt.ll
	rm -rf build
	rm -f test
	rm -f *.ll