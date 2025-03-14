build/probe/ProbePass.so: probe/ProbePass.cpp
	mkdir -p build && \
	cd build && \
	cmake .. && \
	make && \
	cd ..

something: histogram.o rdtsc.o something.c build/probe/ProbePass.so
	clang -g -fpass-plugin=build/probe/ProbePass.so -o something histogram.o rdtsc.o something.c

rdtsc.o: rdtsc.c
	clang -g -c -o rdtsc.o rdtsc.c
histogram.o: histogram.c
	clang -g -c -o histogram.o histogram.c

clean:
	rm -f *.o
	rm -rf build
	rm -f something
	rm -f build/probe/ProbePass.so
