#include "interpreter.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void interpreter_new(interpreter_t* interpreter, vec_t* opcodes)
{
    interpreter->pc = 0;
    interpreter->opcodes = opcodes;
    memset(interpreter->bp, 0, RUNTIME_STACK_SIZE);
    interpreter->sp = interpreter->bp;
    return;
}

void interpreter_show_state(interpreter_t* interpreter)
{
    const char* env_debug = getenv("DEBUG");
    if (env_debug == NULL || strcmp(env_debug, "1") != 0) {
        return;
    }

    printf("\033[34m");
    printf("pc -> %-2zu, bp -> %016zx, sp -> %016zx, ", interpreter->pc,
        (uintptr_t)interpreter->bp, (uintptr_t)interpreter->sp);
    printf("[");
    for (char* p = interpreter->bp; p < interpreter->sp; p++) {
        if (p != interpreter->bp) {
            printf(", ");
        }
        printf("%d", *p);
    }
    printf("]\033[0m\n");

    return;
}

void interpreter_show_opcodes(interpreter_t* interpreter)
{
    const char* env_debug = getenv("DEBUG");
    if (env_debug == NULL || strcmp(env_debug, "1") != 0) {
        return;
    }

    printf("\033[34m");

    for (size_t i = 0; i < interpreter->opcodes->len; ++i) {
        Opcode* op = vec_get(interpreter->opcodes, i);
        const char* opcode_name;

        switch (op->type) {
        case INCREMENT_PTR:
            opcode_name = "INCREMENT_PTR";
            break;
        case DECREMENT_PTR:
            opcode_name = "DECREMENT_PTR";
            break;
        case INCREMENT_VAL:
            opcode_name = "INCREMENT_VAL";
            break;
        case DECREMENT_VAL:
            opcode_name = "DECREMENT_VAL";
            break;
        case OUTPUT_VAL:
            opcode_name = "OUTPUT_VAL";
            break;
        case INPUT_VAL:
            opcode_name = "INPUT_VAL";
            break;
        case LOOP_BEGIN:
            opcode_name = "LOOP_BEGIN";
            break;
        case LOOP_END:
            opcode_name = "LOOP_END";
            break;
        default:
            opcode_name = "UNKNOWN";
            break;
        }

        printf("%-4zu %-15s %zu\n", i, opcode_name, op->operand);
    }

    printf("\033[0m");
}

static inline Opcode* next_op(interpreter_t* interpreter)
{
    if (interpreter->pc >= interpreter->opcodes->len) {
        return NULL;
    }

    Opcode* op = vec_get(interpreter->opcodes, interpreter->pc);
    return op;
}

int interpreter_run(interpreter_t* interpreter)
{
    interpreter_show_opcodes(interpreter);

    Opcode* op;
    while ((op = next_op(interpreter)) != NULL) {
        interpreter_show_state(interpreter);
        switch (op->type) {
        case INCREMENT_PTR:
            interpreter->sp += op->operand;
            if (interpreter->sp - interpreter->bp >= RUNTIME_STACK_SIZE) {
                perror("stack overflow\n");
                return ESTACK_OVERFLOW;
            }
            break;
        case DECREMENT_PTR:
            interpreter->sp -= op->operand;
            if (interpreter->sp < interpreter->bp) {
                perror("stack overflow\n");
                return ESTACK_OVERFLOW;
            }
            break;
        case INCREMENT_VAL:
            *interpreter->sp += op->operand;
            break;
        case DECREMENT_VAL:
            *interpreter->sp -= op->operand;
            break;
        case OUTPUT_VAL:
            for (size_t i = 0; i < op->operand; ++i) {
                putchar(*interpreter->sp);
            }
            break;
        case INPUT_VAL:
            for (size_t i = 0; i < op->operand; ++i) {
                *interpreter->sp = getchar();
            }
            break;
        case LOOP_BEGIN:
            if (*interpreter->sp == 0) {
                assert(op->operand >= 0 && op->operand < interpreter->opcodes->len);
                interpreter->pc = op->operand;
            }
            break;
        case LOOP_END:
            if (*interpreter->sp != 0) {
                assert(op->operand >= 0 && op->operand < interpreter->opcodes->len);
                interpreter->pc = op->operand;
            }
            break;
        }
        interpreter->pc += 1;
    }
    return 0;
}
