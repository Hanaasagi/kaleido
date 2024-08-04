#include "compiler.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define EPARSE_ERROR 1

void compiler_new(compiler_t* compiler, size_t opcode_capacity)
{
    vec_new(&compiler->opcodes, sizeof(Opcode), opcode_capacity);
    return;
}

void compiler_free(compiler_t* compiler)
{
    vec_free(&compiler->opcodes);
    return;
}

int compiler_parse_file(compiler_t* compiler, FILE* fp)
{
    size_t stack[100];
    int stack_ptr = -1;

    char c;
    while ((c = fgetc(fp)) != EOF) {
        Opcode op;
        op.operand = 0;

        switch (c) {
        case '>':
            do {
                op.operand++;
            } while ((c = fgetc(fp)) == '>');
            ungetc(c, fp);
            op.type = INCREMENT_PTR;
            break;
        case '<':
            do {
                op.operand++;
            } while ((c = fgetc(fp)) == '<');
            ungetc(c, fp);
            op.type = DECREMENT_PTR;
            break;
        case '+':
            do {
                op.operand++;
            } while ((c = fgetc(fp)) == '+');
            ungetc(c, fp);
            op.type = INCREMENT_VAL;
            break;
        case '-':
            do {
                op.operand++;
            } while ((c = fgetc(fp)) == '-');
            ungetc(c, fp);
            op.type = DECREMENT_VAL;
            break;
        case '.':
            op.operand = 1;
            op.type = OUTPUT_VAL;
            break;
        case ',':
            op.operand = 1;
            op.type = INPUT_VAL;
            break;
        case '[':
            op.type = LOOP_BEGIN;
            stack[++stack_ptr] = compiler->opcodes.len;
            break;
        case ']':
            if (stack_ptr < 0) {
                perror("Unmatched closing bracket\n");
                return EPARSE_ERROR;
            }
            op.type = LOOP_END;
            ((Opcode*)vec_get(&compiler->opcodes, stack[stack_ptr]))->operand = compiler->opcodes.len;
            op.operand = stack[stack_ptr--];
            break;
        default:
            continue;
        }
        vec_push(&compiler->opcodes, &op);
    }

    if (stack_ptr >= 0) {
        perror("Unmatched opening bracket\n");
        return EPARSE_ERROR;
    }
    return 0;
}
