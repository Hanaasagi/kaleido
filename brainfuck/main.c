#include "compiler.h"
#include "interpreter.h"
#include <errno.h>
#include <stdio.h>

int main(int argc, char* argv[])
{
    if (argc != 2) {
        fprintf(stdout, "Usage: %s <filename>\n", argv[0]);
        return 1;
    }

    FILE* fp = fopen(argv[1], "r");
    if (!fp) {
        perror("Failed to open file");
        return 1;
    }

    compiler_t compiler;
    compiler_new(&compiler, RUNTIME_STACK_SIZE);

    int ret = compiler_parse_file(&compiler, fp);
    fclose(fp);

    if (ret != 0) {
        fprintf(stdout, "parse error: %d\n", errno);
        compiler_free(&compiler);
        return ret;
    }

    interpreter_t interpreter;
    interpreter_new(&interpreter, &compiler.opcodes);

    ret = interpreter_run(&interpreter);
    if (ret != 0) {
        fprintf(stdout, "run error: %d\n", errno);
    }

    compiler_free(&compiler);
    return ret;
}
