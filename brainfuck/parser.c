#include "parser.h"
#include <stdio.h>
#include <unistd.h>

#define EPARSE_ERROR 1

void parser_new(parser_t* parser, size_t opcode_capacity)
{
    vec_new(&parser->opcodes, sizeof(Opcode), opcode_capacity);
    return;
}

void parser_free(parser_t* parser)
{
    vec_free(&parser->opcodes);
    return;
}

int parser_parse_file(parser_t* parser, FILE* fp)
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
            stack[++stack_ptr] = parser->opcodes.len;
            break;
        case ']':
            if (stack_ptr < 0) {
                perror("Unmatched closing bracket\n");
                return EPARSE_ERROR;
            }
            op.type = LOOP_END;
            ((Opcode*)vec_get(&parser->opcodes, stack[stack_ptr]))->operand = parser->opcodes.len;
            op.operand = stack[stack_ptr--];
            break;
        default:
            continue;
        }
        vec_push(&parser->opcodes, &op);
    }

    if (stack_ptr >= 0) {
        perror("Unmatched opening bracket\n");
        return EPARSE_ERROR;
    }
    return 0;
}
