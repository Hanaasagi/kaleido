#ifndef HASHMAP_H
#define HASHMAP_H

#include <assert.h>
#include <ctype.h>
#include <errno.h>
#include <glob.h>
#include <libgen.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdnoreturn.h>
#include <string.h>
#include <strings.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

char* format(const char* fmt, ...) __attribute__((format(printf, 1, 2)));

// noreturn void error(char* fmt, ...) __attribute__((format(printf, 1, 2)));
void error(const char* fmt, ...) __attribute__((format(printf, 1, 2))) __attribute__((noreturn));
// void error(const char* fmt, ...) __attribute__((format(printf, 1, 2)));
// void error(char *fmt, ...) __attribute__((format(printf, 1, 2)));

#define unreachable() \
    error("internal error at %s:%d", __FILE__, __LINE__)

typedef struct {
    char* key;
    int keylen;
    void* val;
} HashEntry;

typedef struct {
    HashEntry* buckets;
    int capacity;
    int used;
} HashMap;

void* hashmap_get(HashMap* map, const char* key);
void* hashmap_get2(HashMap* map, const char* key, int keylen);
void hashmap_put(HashMap* map, const char* key, void* val);
void hashmap_put2(HashMap* map, const char* key, int keylen, void* val);
void hashmap_delete(HashMap* map, const char* key);
void hashmap_delete2(HashMap* map, const char* key, int keylen);
void hashmap_test(void);
#endif // HASHMAP_H
