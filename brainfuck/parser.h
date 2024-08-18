#ifndef PARSER_H
#define PARSER_H

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

typedef struct parser {
    vec_t opcodes;
} parser_t __attribute__((aligned(8)));

void parser_new(parser_t* parser, size_t opcode_capacity);
void parser_free(parser_t* parser);
int parser_parse_file(parser_t* parser, FILE* fp);

#endif
