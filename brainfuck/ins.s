global _start

_start:
    xor eax, eax
    xor ebx, ebx
    mov rax, r12
    mov rax, 0
    mov rax, 0
    mov rax, 1

    sub rsi, 0
    mov rsi, rsp
    add rsi, byte 0
    add rsi, 0
    sub rsi, byte 0
    add byte [rsi], 0
    add dword [rsi], 0
    sub byte [rsi], 0
    sub dword [rsi], 0

    sub sp, byte 0
    sub esp, byte 0
    sub rsp, byte 0
    sub rsp, 0xffff
    add rsp, byte 0
    add rsp, 0xffff
    sub byte [rsp], 0
    sub dword [rsp], 0

    mov rdi, r12
    mov rdi, 1
    mov rdi, rsp
    xor rdi, rdi
    xor al, al
    mov r12, 1
    mov edx, 1
    mov rcx, 0
    cmp [rsi], bl
    jz 0
    jmp 0
    syscall
    rep stosb
