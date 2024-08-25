#include "interpreter.h"
#include "parser.h"
#include <errno.h>
#include <stdio.h>

void print_help(const char* program_name)
{
    fprintf(stdout, "Usage: %s <input_file>\n", program_name);
    fprintf(stdout, "  <input_file>  : The path to the source file.\n");
}

int main(int argc, char* argv[])
{
    if (argc != 2) {
        print_help(argv[0]);
        return 1;
    }

    FILE* fp = fopen(argv[1], "r");
    if (!fp) {
        perror("Failed to open file");
        return 1;
    }

    parser_t parser;
    parser_new(&parser, RUNTIME_STACK_SIZE);

    int ret = parser_parse_file(&parser, fp);
    fclose(fp);

    if (ret != 0) {
        fprintf(stdout, "parse error: %d\n", errno);
        parser_free(&parser);
        return ret;
    }

    interpreter_t interpreter;
    interpreter_new(&interpreter, &parser.opcodes);

    ret = interpreter_run(&interpreter);
    if (ret != 0) {
        fprintf(stdout, "run error: %d\n", errno);
    }

    parser_free(&parser);
    return ret;
}
