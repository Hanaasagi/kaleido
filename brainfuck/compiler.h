#ifndef COMPILER_H
#define COMPILER_H

#include "vec.h"
#include <stdio.h>

typedef enum {
    INCREMENT_PTR,
    DECREMENT_PTR,
    INCREMENT_VAL,
    DECREMENT_VAL,
    OUTPUT_VAL,
    INPUT_VAL,
    LOOP_BEGIN,
    LOOP_END
} OpcodeType;

typedef struct Opcode {
    OpcodeType type;
    size_t operand;
} Opcode __attribute__((aligned(8)));

typedef struct compiler {
    vec_t opcodes;
} compiler_t __attribute__((aligned(8)));

void compiler_new(compiler_t* compiler, size_t opcode_capacity);
void compiler_free(compiler_t* compiler);
int compiler_parse_file(compiler_t* compiler, FILE* fp);

#endif
