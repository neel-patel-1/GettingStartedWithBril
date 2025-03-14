build/probe/ProbePass.so: probe/ProbePass.cpp
	mkdir -p build && \
	cd build && \
	cmake .. && \
	make && \
	cd ..

something: histogram.o rdtsc.o something.c build/probe/ProbePass.so
	clang -g -emit-llvm -c something.c -o something.bc
	llvm-dis-18 -o something.ll something.bc
	opt-18 -load-pass-plugin=build/probe/ProbePass.so -passes=insert-rdtsc < something.ll > something.opt.bc
	llvm-dis-18 -o something.opt.ll something.opt.bc
	llc-18 -filetype=obj something.opt.bc -o something.o
	clang -g -o something something.o histogram.o rdtsc.o

rdtsc.o: rdtsc.c
	clang -g -c -o rdtsc.o rdtsc.c
histogram.o: histogram.c
	clang -g -c -o histogram.o histogram.c

clean:
	rm -f *.o
	rm -f *.bc
	rm -f *.opt.bc
	rm -f *.opt.ll
	# rm -rf build
	rm -f something
	rm -f something.ll