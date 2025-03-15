build/licm/LICM.so: licm/LICM.cpp
	mkdir -p build && \
	cd build && \
	cmake .. && \
	make && \
	cd ..

test: test.cpp build/licm/LICM.so
	clang++-18 -g -fPIE -emit-llvm -c test.cpp -o test.bc
	clang++-18 -o test.o -c test.bc
	clang++-18 -fPIE -pie -o test test.o

clean:
	rm -f *.o
	rm -f *.bc
	rm -f *.opt.bc
	rm -f *.opt.ll
	# rm -rf build
	rm -f something
	rm -f something.ll