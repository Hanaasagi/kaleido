# Brainfuck

## Brainfuck Interpreter

```Bash
make
./bin/interpreter test_cases/hello.bf
```

## Brainfuck Transpiler

```Bash
python transpiler.py ./test_cases/hello.bf
```

## Brainfuck x86-64 Compiler

```Bash
make
./bin/compiler test_cases/hello.bf a.out
./a.out
```
