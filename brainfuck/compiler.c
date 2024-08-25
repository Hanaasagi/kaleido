#include "compiler.h"
#include <elf.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

// rsi - data pointer
// rdi - syscall argument
// rax - temp
// rbx - zero register
// r12 - one register

// nasm -f elf64 -l output.txt ins.s
//  1                                  global _start
//  2
//  3                                  _start:
//  4 00000000 31C0                        xor eax, eax
//  5 00000002 31DB                        xor ebx, ebx
//  6 00000004 4C89E0                      mov rax, r12
//  7 00000007 B800000000                  mov rax, 0
//  8
//  9 0000000C 4883EE00                    sub rsi, 0
// 10 00000010 4889E6                      mov rsi, rsp
// 11 00000013 4883C600                    add rsi, byte 0
// 12 00000017 4883C600                    add rsi, 0
// 13 0000001B 4883EE00                    sub rsi, byte 0
// 14 0000001F 800600                      add byte [rsi], 0
// 15 00000022 830600                      add dword [rsi], 0
// 16 00000025 802E00                      sub byte [rsi], 0
// 17 00000028 832E00                      sub dword [rsi], 0
// 18
// 19 0000002B 6683EC00                    sub sp, byte 0
// 20 0000002F 83EC00                      sub esp, byte 0
// 21 00000032 4883EC00                    sub rsp, byte 0
// 22 00000036 4881ECFFFF0000              sub rsp, 0xffff
// 23 0000003D 802C2400                    sub byte [rsp], 0
// 24 00000041 832C2400                    sub dword [rsp], 0
// 25
// 26 00000045 4C89E7                      mov rdi, r12
// 27 00000048 4889E7                      mov rdi, rsp
// 28 0000004B 4831FF                      xor rdi, rdi
// 29 0000004E 30C0                        xor al, al
// 30 00000050 41BC01000000                mov r12, 1
// 31 00000056 BA01000000                  mov edx, 1
// 32 0000005B B900000000                  mov rcx, 0
// 33 00000060 381E                        cmp [rsi], bl
// 34 00000062 0F84(00000000)              jz 0
// 35 00000068 E9(00000000)                jmp 0
// 36 0000006D 0F05                        syscall
// 37 0000006F F3AA                        rep stosb

void compiler_asm_ins(compiler_t* compiler, int size, uint64_t ins)
{
    for (int i = size - 1; i >= 0; i--) {
        uint8_t val = (ins >> (i * 8)) & 0xff;
        vec_push(&compiler->code, &val);
    }
    return;
}

void compiler_asm_imm(compiler_t* compiler, int size, const void* value)
{
    vec_extend_from_slice(&compiler->code, value, size);
    return;
}

void compiler_asm_syscall(compiler_t* compiler, int syscall)
{
    // https://defuse.ca/online-x86-assembler.htm#disassembly
    // echo -ne "\x31\xc0" | ndisasm -b 64 -
    switch (syscall) {
    case 0:
        // 0x6631c0  xor ax, ax
        compiler_asm_ins(compiler, 2, 0x31C0); // xor  eax, eax
        break;
    case 1:
        compiler_asm_ins(compiler, 3, 0x4C89E0); // mov rax, r12
        break;
    default:
        compiler_asm_ins(compiler, 1, 0xB8); // mov  rax, syscall
        compiler_asm_imm(compiler, 4, &syscall);
        break;
    }
    compiler_asm_ins(compiler, 2, 0x0F05); // syscall
    return;
}

void compiler_new(compiler_t* compiler, vec_t* opcodes)
{
    compiler->opcodes = opcodes;
    // FIXME:
    vec_new(&compiler->code, sizeof(uint8_t), opcodes->len * 2);
    return;
}

void compiler_free(compiler_t* compiler)
{
    vec_free(&compiler->code);
    return;
}

int compiler_compile(compiler_t* compiler)
{
    uint32_t memory_size = RUNTIME_STACK_SIZE;

    // store 0
    compiler_asm_ins(compiler, 2, 0x31DB); // xor ebx, ebx
    // store 1
    compiler_asm_ins(compiler, 6, 0x41BC01000000); // mov r12, 1

    // alloc stack
    compiler_asm_ins(compiler, 3, 0x4881EC); // sub  rsp, ?
    compiler_asm_imm(compiler, 4, &memory_size);
    compiler_asm_ins(compiler, 3, 0x4889E6); // mov  rsi, rsp

    // memset zero
    // https://www.cs.uaf.edu/2017/fall/cs301/lecture/10_06_string_inst.html
    compiler_asm_ins(compiler, 1, 0xB9); // mov  rcx, ?
    compiler_asm_imm(compiler, 4, &memory_size);
    compiler_asm_ins(compiler, 2, 0x30C0); // xor  al, al
    compiler_asm_ins(compiler, 3, 0x4889E7); // mov  rdi, rsp
    compiler_asm_ins(compiler, 2, 0xF3AA); // rep stosb

    // read syscall and write syscall arg2
    compiler_asm_ins(compiler, 5, 0xBA01000000); // mov  edx, 0x1

    uint32_t* table = malloc(sizeof(table[0]) * compiler->opcodes->len);
    for (size_t i = 0; i < compiler->opcodes->len; i++) {
        Opcode* op = vec_get(compiler->opcodes, i);
        table[i] = compiler->code.len;

        switch (op->type) {
        case INCREMENT_PTR:
            // add rsi, byte ?
            // add rsi, ?
            compiler_asm_ins(compiler, 3, (op->operand <= 255) ? 0x4883C6 : 0x4881C6);
            compiler_asm_imm(compiler, (op->operand <= 255) ? 1 : 4, &op->operand);
            break;
        case DECREMENT_PTR:
            // sub rsi, byte ?
            // sub rsi, ?
            compiler_asm_ins(compiler, 3, (op->operand <= 255) ? 0x4883EE : 0x4881EE);
            compiler_asm_imm(compiler, (op->operand <= 255) ? 1 : 4, &op->operand);
            break;
        case INCREMENT_VAL:
            // add byte [rsi], ?
            // add dword [rsi], ?
            // Actually, there's no need to consider the operand size here since each memory unit is 8 bits.
            compiler_asm_ins(compiler, 2, (op->operand <= 255) ? 0x8006 : 0x8306);
            compiler_asm_imm(compiler, (op->operand <= 255) ? 1 : 4, &op->operand);
            break;
        case DECREMENT_VAL:
            // sub byte [rsi], ?
            // sub dword [rsi], ?
            compiler_asm_ins(compiler, 2, (op->operand <= 255) ? 0x802E : 0x832E);
            compiler_asm_imm(compiler, (op->operand <= 255) ? 1 : 4, &op->operand);
            break;
        case OUTPUT_VAL:
            // mov  rdi, r12
            compiler_asm_ins(compiler, 3, 0x4C89E7);
            compiler_asm_syscall(compiler, SYS_write);
            break;
        case INPUT_VAL:
            // xor  rdi, rdi
            compiler_asm_ins(compiler, 3, 0x4831FF);
            compiler_asm_syscall(compiler, SYS_read);
            break;
        case LOOP_BEGIN: {
            uint32_t delta = 0;
            // cmp  [rsi], bl
            compiler_asm_ins(compiler, 2, 0x381E);
            // jz
            compiler_asm_ins(compiler, 2, 0x0F84);
            compiler_asm_imm(compiler, 4, &delta); // patched by LOOP_END
        } break;
        case LOOP_END: {
            uint32_t delta = table[op->operand];
            delta -= compiler->code.len + 5;
            // jmp delta
            compiler_asm_ins(compiler, 1, 0xE9);
            compiler_asm_imm(compiler, 4, &delta);
            void* jz = vec_get(&compiler->code, (table[op->operand] + 4));
            uint32_t patch = compiler->code.len - table[op->operand] - 8;
            memcpy(jz, &patch, 4); // patch previous branch '['
        } break;
        }
    }
    // xor  rdi, rdi
    compiler_asm_ins(compiler, 3, 0x4831FF);
    compiler_asm_syscall(compiler, SYS_exit);
    free(table);

    return 0;
}

void compiler_write_elf(compiler_t* compiler, FILE* fd)
{
    uint64_t entry = 0x400000 + sizeof(Elf64_Ehdr) + sizeof(Elf64_Phdr);
    Elf64_Ehdr ehdr = {
        .e_ident = {
            ELFMAG0,
            ELFMAG1,
            ELFMAG2,
            ELFMAG3,
            ELFCLASS64,
            ELFDATA2LSB,
            EV_CURRENT,
            ELFOSABI_SYSV,
        },
        .e_type = ET_EXEC,
        .e_machine = EM_X86_64,
        .e_version = EV_CURRENT,
        .e_entry = entry,
        .e_phoff = sizeof(Elf64_Ehdr),
        .e_ehsize = sizeof(Elf64_Ehdr),
        .e_phentsize = sizeof(Elf64_Phdr),
        .e_phnum = 1,
    };
    Elf64_Phdr phdr = {
        .p_type = PT_LOAD,
        .p_flags = PF_X | PF_R,
        .p_offset = sizeof(Elf64_Ehdr) + sizeof(Elf64_Phdr),
        .p_vaddr = entry,
        .p_filesz = compiler->code.len,
        .p_memsz = compiler->code.len,
        .p_align = 0,
    };

    fwrite(&ehdr, sizeof(ehdr), 1, fd);
    fwrite(&phdr, sizeof(phdr), 1, fd);
    fwrite(compiler->code.ptr, compiler->code.len, 1, fd);
    return;
}
