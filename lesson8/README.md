# LICM LLVM Pass

```sh
# test
make all
./test
./test_licm

# benchmark
cd benchmark
git submodule update --init --recursive
./compile_bench.sh
./run_bench.sh | tee executed.log
```


* stats
```sh
cd benchmarks/ && ./compile_bench.sh |& tee hoisted.log

grep Hoisted hoisted.log  | wc -l
# 1407

python3 plot.py benchmarks/executed.log
```