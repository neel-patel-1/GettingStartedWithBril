build/probe/ProbePass.so: probe/ProbePass.cpp
	mkdir -p build && \
	cd build && \
	cmake .. && \
	make && \
	cd ..

something: histogram.o rdtsc.o something.c build/probe/ProbePass.so
	clang -g -fpass-plugin=build/probe/ProbePass.so -c -emit-llvm something.c
	llvm-dis-18 -o something.ll something.bc
	llc-18 -filetype=obj something.bc -o something.o
	clang -g -o something something.o histogram.o rdtsc.o

rdtsc.o: rdtsc.c
	clang -g -c -o rdtsc.o rdtsc.c
histogram.o: histogram.c
	clang -g -c -o histogram.o histogram.c

clean:
	rm -f *.o
	rm -rf build
	rm -f something
	rm -f something.ll
	rm -f build/probe/ProbePass.so
