#!/bin/bash

CLANG=clang-18
OPT=opt-18
LLVM_AS=llvm-as-18
POLYBENCH_DIR=$(pwd)/PolyBenchC-4.2.1

PASS=$(pwd)/../build/licm/LICMPass.so

# gcc -O3 -I utilities -I linear-algebra/kernels/atax utilities/polybench.c linear-algebra/kernels/atax/atax.c -DPOLYBENCH_TIME -o atax_time
gcc -O3 -I ${POLYBENCH_DIR}/utilities -I ${POLYBENCH_DIR}/linear-algebra/kernels/atax ${POLYBENCH_DIR}/utilities/polybench.c ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax.c -DPOLYBENCH_TIME -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time