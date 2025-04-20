# Lesson 12

```sh
deno run --allow-read=./examples --allow-write=. ./trace-brili/brili.ts examples/example.json 10

python3 ./optimizations/lvn.py -p -c -f < traces/example.json/main_0.json  > opt/traces/example.json/main_0.lvn.json
python3 ./utils/trace2txt.py < opt/traces/example.json/main_0.lvn.json
```

```
  lvn.2: int = const 1;
  hundred: int = const 100;
  cond: bool = lt x hundred;
  br cond .then .else;
.then:
  y: int = call @f x;
  one: int = const 1;
  b: int = sub a one;
  ret b;
  jmp .done;
.done:
  print y;
  ret;
```

```sh
python3 ./optimizations/dce.py tdce+  < opt/traces/example.json/main_0.lvn.json | python3 ./utils/trace2txt.py
```
  lvn.2: int = const 1;
  hundred: int = const 100;
  cond: bool = lt x hundred;
  br cond .then .else;
.then:
  y: int = call @f x;
  one: int = const 1;
  b: int = sub a one;
  ret b;
  jmp .done;
.done:
  print y;
  ret;
```

