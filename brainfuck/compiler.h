#ifndef COMPILER_H
#define COMPILER_H

#include "parser.h"

#define RUNTIME_STACK_SIZE 512

typedef struct compiler {
    vec_t* opcodes;
    vec_t code;

} compiler_t __attribute__((aligned(8)));

void compiler_new(compiler_t* compiler, vec_t* opcodes);
int compiler_compile(compiler_t* compiler);
void compiler_write_elf(compiler_t* compiler, FILE* fd);
void compiler_free(compiler_t* compiler);

#endif
