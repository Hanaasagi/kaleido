#include "vec.h"
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define RUNTIME_STACK_SIZE 512
#define INITIAL_CODE_SIZE 256

#define EPARSE_ERROR 1
#define ESTACK_OVERFLOW 2

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
  size_t jmp_addr;
} Opcode __attribute__((aligned(8)));

typedef struct interpreter {
  vec_t opcodes;
  size_t pc;
  char bp[RUNTIME_STACK_SIZE];
  char *sp;
} interpreter_t __attribute__((aligned(8)));

void interpreter_new(interpreter_t *interpreter, size_t opcode_capacity) {
  interpreter->pc = 0;
  vec_new(&interpreter->opcodes, sizeof(Opcode), opcode_capacity);

  memset(interpreter->bp, 0, RUNTIME_STACK_SIZE);
  interpreter->sp = interpreter->bp;

  return;
}

void interpreter_free(interpreter_t *interpreter) {
  vec_free(&interpreter->opcodes);

  return;
}

int interpreter_parse_file(interpreter_t *interpreter, FILE *fp) {
  // stack for loop opcode
  size_t stack[100];
  int stack_ptr = -1;

  char c;
  size_t i = 0;
  while ((c = fgetc(fp)) != EOF) {
    Opcode op;
    op.jmp_addr = -1;

    switch (c) {
    case '>':
      op.type = INCREMENT_PTR;
      break;
    case '<':
      op.type = DECREMENT_PTR;
      break;
    case '+':
      op.type = INCREMENT_VAL;
      break;
    case '-':
      op.type = DECREMENT_VAL;
      break;
    case '.':
      op.type = OUTPUT_VAL;
      break;
    case ',':
      op.type = INPUT_VAL;
      break;
    case '[':
      op.type = LOOP_BEGIN;
      stack[++stack_ptr] = interpreter->opcodes.len;
      break;
    case ']':
      if (stack_ptr < 0) {
        perror("Unmatched closing bracket\n");
        errno = EPARSE_ERROR;
        return EPARSE_ERROR;
      }

      op.type = LOOP_END;
      ((Opcode *)vec_get(&interpreter->opcodes, stack[stack_ptr]))->jmp_addr =
          interpreter->opcodes.len;
      op.jmp_addr = stack[stack_ptr--];
      break;
    default:
      continue;
    }
    vec_push(&interpreter->opcodes, &op);
    i += 1;
  }

  if (stack_ptr >= 0) {
    perror("Unmatched opening bracket\n");
    errno = EPARSE_ERROR;
    return EPARSE_ERROR;
  }
  return 0;
}

static inline Opcode *next_op(interpreter_t *interpreter) {
  if (interpreter->pc >= interpreter->opcodes.len) {
    return NULL;
  }

  Opcode *op = vec_get(&interpreter->opcodes, interpreter->pc);
  return op;
}

void interpreter_show_state(interpreter_t *interpreter) {
  const char *env_debug = getenv("DEBUG");
  if (env_debug == NULL || strcmp(env_debug, "1") != 0) {
    return;
  }

  printf("\033[31m");

  printf("pc -> %x, bp -> %x, sp -> %x, ", interpreter->pc, interpreter->bp,
         interpreter->sp);
  printf("[");
  for (char *p = interpreter->bp; p < interpreter->sp; p++) {
    if (p != interpreter->bp) {
      printf(", ");
    }
    printf("%d", *p);
  }
  printf("]\033[0m\n");

  return;
}

int interpreter_run(interpreter_t *interpreter) {
  Opcode *op;
  while ((op = next_op(interpreter)) != NULL) {
    interpreter_show_state(interpreter);
    switch (op->type) {
    case INCREMENT_PTR:
      ++interpreter->sp;
      if (interpreter->sp - interpreter->bp >= RUNTIME_STACK_SIZE) {
        perror("stack overflow\n");
        return ESTACK_OVERFLOW;
      }
      break;
    case DECREMENT_PTR:
      --interpreter->sp;
      if (interpreter->sp < interpreter->bp) {
        perror("stack overflow\n");
        return ESTACK_OVERFLOW;
      }
      break;
    case INCREMENT_VAL:
      ++(*interpreter->sp);
      break;
    case DECREMENT_VAL:
      --(*interpreter->sp);
      break;
    case OUTPUT_VAL:
      putchar(*interpreter->sp);
      break;
    case INPUT_VAL:
      *interpreter->sp = getchar();
      break;
    case LOOP_BEGIN:
      if (*interpreter->sp == 0) {
        assert(op->jmp_addr >= 0 && op->jmp_addr < interpreter->opcodes.len);
        interpreter->pc = op->jmp_addr;
      }
      break;
    case LOOP_END:
      if (*interpreter->sp != 0) {
        assert(op->jmp_addr >= 0 && op->jmp_addr < interpreter->opcodes.len);
        interpreter->pc = op->jmp_addr;
      }
      break;
    }
    interpreter->pc += 1;
  }

  return 0;
}

int main(int argc, char *argv[]) {
  if (argc != 2) {
    fprintf(stdout, "Usage: %s <filename>\n", argv[0]);
    return 1;
  }

  FILE *fp = fopen(argv[1], "r");
  if (!fp) {
    perror("Failed to open file");
    return 1;
  }

  interpreter_t interpreter;
  interpreter_new(&interpreter, INITIAL_CODE_SIZE);

  int ret = interpreter_parse_file(&interpreter, fp);
  fclose(fp);

  if (ret != 0) {
    fprintf(stdout, "parse error: %s\n", strerror(errno));
    interpreter_free(&interpreter);
    return ret;
  }

  ret = interpreter_run(&interpreter);
  if (ret != 0) {
    fprintf(stdout, "run error: %s\n", strerror(errno));
  }
  interpreter_free(&interpreter);
  return 0;
}
