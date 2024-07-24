#ifndef LIBMALLOC_H
#define LIBMALLOC_H

#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdatomic.h>

#define MAX_BUFFER_SIZE 1024

void __debug(const char *format, ...);

#endif
