#include "compiler.h"
#include "interpreter.h"
#include "parser.h"
#include <errno.h>
#include <stdio.h>
#include <sys/stat.h>

void print_help(const char* program_name)
{
    fprintf(stdout, "Usage: %s <input_file> [output_file]\n", program_name);
    fprintf(stdout, "  <input_file>  : The path to the source file.\n");
    fprintf(stdout, "  [output_file] : The path to the output file (optional, default is './bf.out').\n");
}

int main(int argc, char* argv[])
{
    if (argc < 2 || argc > 3) {
        print_help(argv[0]);
        return 1;
    }

    const char* input_file = argv[1];
    const char* output_file = (argc == 3) ? argv[2] : "bf.out";

    FILE* fp = fopen(input_file, "r");
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

    compiler_t compiler;
    compiler_new(&compiler, &parser.opcodes);
    compiler_compile(&compiler);

    FILE* elf_fp = fopen(output_file, "wb");
    if (!elf_fp) {
        fprintf(stdout, "could not open output file: %s\n", output_file);
        parser_free(&parser);
        compiler_free(&compiler);
        return 1;
    }

    compiler_write_elf(&compiler, elf_fp);
    fchmod(fileno(elf_fp), 0755);
    fclose(elf_fp);

    parser_free(&parser);
    compiler_free(&compiler);

    return ret;
}
