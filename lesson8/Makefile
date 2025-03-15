build/licm/LICM.so: licm/LICM.cpp
	mkdir -p build && \
	cd build && \
	cmake .. && \
	make && \
	cd ..

test: test.cpp
	clang++ -g -emit-llvm -c test.cpp -o test.bc
	llvm-dis-18 -o test.ll test.bc
	opt-18 -load-pass-plugin=build/licm/LICM.so -passes=licm < test.ll > test.opt.bc
	llvm-dis-18 -o test.opt.ll test.opt.bc
	llc-18 -filetype=obj test.opt.bc -o test.o
	clang++ -g -o test test.o

clean:
	rm -f *.o
	rm -f *.bc
	rm -f *.opt.bc
	rm -f *.opt.ll
	# rm -rf build
	rm -f something
	rm -f something.ll