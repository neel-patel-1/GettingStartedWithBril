#!/bin/bash
POLYBENCH_DIR=$(pwd)/PolyBenchC-4.2.1

BENCHMARKS=( "datamining/correlation" "datamining/covariance" "linear-algebra/blas/gemm" "linear-algebra/blas/gemver" "linear-algebra/blas/gesummv" "linear-algebra/blas/symm" "linear-algebra/blas/syr2k" "linear-algebra/blas/syrk" "linear-algebra/blas/trmm" "linear-algebra/kernels/2mm" "linear-algebra/kernels/3mm" "linear-algebra/kernels/atax" "linear-algebra/kernels/bicg" "linear-algebra/kernels/doitgen" "linear-algebra/kernels/mvt" "linear-algebra/solvers/cholesky" "linear-algebra/solvers/durbin" "linear-algebra/solvers/gramschmidt" "linear-algebra/solvers/lu" "linear-algebra/solvers/ludcmp" "linear-algebra/solvers/trisolv" "medley/deriche" "medley/floyd-warshall" "medley/nussinov" "stencils/adi" "stencils/fdtd-2d" "stencils/heat-3d" "stencils/jacobi-1d" "stencils/jacobi-2d" "stencils/seidel-2d")

chmod +x ${POLYBENCH_DIR}/utilities/time_benchmark.sh

for benchmark in "${BENCHMARKS[@]}"; do
    echo "Running benchmark for ${benchmark}..."
    DIR="${POLYBENCH_DIR}/${benchmark}"
    FILE="${DIR}/$(basename ${DIR}).c"
    if [ -f "${FILE}" ]; then
        # normal time
        ${POLYBENCH_DIR}/utilities/time_benchmark.sh ${DIR}/$(basename ${DIR})_mem2reg

        # licm time
        ${POLYBENCH_DIR}/utilities/time_benchmark.sh ${DIR}/$(basename ${DIR})_licm

    else
        echo "File not found: ${FILE}"
    fi
done