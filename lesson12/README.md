# Lesson 12

```sh
./run.sh <example_name> <example_args>
# e.g.,
./run.sh example 10
```


```sh
(1) runs the unmodified version of the example through trace-brili, then (2) applies inlining and lvn to the trace
4:13
then (3) reinserts the trace into the program, and (4) applies dce
4:14
then (5) reruns regular brili, printing dynamic instruction count
4:14
of the "optimized" program
```
