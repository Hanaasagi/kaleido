#ifndef INTERPRETER_H
#define INTERPRETER_H

#include "parser.h"

#define RUNTIME_STACK_SIZE 512
#define ESTACK_OVERFLOW 2

typedef struct interpreter {
    vec_t* opcodes;
    size_t pc;
    char bp[512];
    char* sp;
} interpreter_t __attribute__((aligned(8)));

void interpreter_new(interpreter_t* interpreter, vec_t* opcodes);
void interpreter_show_state(interpreter_t* interpreter);
void interpreter_show_opcodes(interpreter_t* interpreter);
int interpreter_run(interpreter_t* interpreter);

#endif
