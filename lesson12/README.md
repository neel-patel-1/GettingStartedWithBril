# Lesson 12

```sh
./run.sh <example_name> <example_args>
# e.g.,
./run.sh example 10
```
1) runs the unmodified version of the example through trace-brili to generate traces
2) applies inlining and lvn to the trace
3) reinserts the trace into the program
4) applies dce to the full program
5) reruns regular brili, printing dynamic instruction count of the "optimized" program