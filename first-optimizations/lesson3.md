# Lesson 3:  First Optimizations

* globally unused instructions
```sh
# test globally unused instructions on simple.bril
bril2json < test_cases/simple.bril | python3 globally_unused_insts.py | bril2txt
```
