#!/bin/bash

CLANG=clang-18
OPT=opt-18
LLVM_AS=llvm-as-18
POLYBENCH_DIR=$(pwd)/PolyBenchC-4.2.1
INCLUDES="-I${POLYBENCH_DIR}/utilities -I${POLYBENCH_DIR}/linear-algebra/kernels/atax"
FLAGS="-DPOLYBENCH_TIME"

PASS=$(pwd)/../build/licm/LICMPass.so

# gcc -O3 -I ${POLYBENCH_DIR}/utilities -I ${POLYBENCH_DIR}/linear-algebra/kernels/atax ${POLYBENCH_DIR}/utilities/polybench.c ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax.c -DPOLYBENCH_TIME -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time

${CLANG} ${FLAGS} -c ${POLYBENCH_DIR}/utilities/polybench.c -o ${POLYBENCH_DIR}/utilities/polybench.o


${CLANG} ${FLAGS} -S -O1 -Xclang -disable-llvm-passes -emit-llvm ${INCLUDES} -S ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax.c -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time.ll

# normal time
${OPT} -passes=mem2reg -S ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time.ll -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_mem2reg.ll
${CLANG} -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_mem2reg.o -c ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_mem2reg.ll
${CLANG} -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_mem2reg ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_mem2reg.o ${POLYBENCH_DIR}/utilities/polybench.o

# licm time
${OPT} -load-pass-plugin ${PASS} -passes=licm-invariant -S ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_mem2reg.ll -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_licm.ll
${CLANG} -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_licm.o -c ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_licm.ll
${CLANG} -o ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_licm ${POLYBENCH_DIR}/linear-algebra/kernels/atax/atax_time_licm.o ${POLYBENCH_DIR}/utilities/polybench.o
