#include "libmalloc.h"

void __debug(const char *format, ...) {
    const char *env_debug = getenv("DEBUG");
    if (env_debug == NULL || strcmp(env_debug, "1") != 0) {
        return;
    }

    char buffer[MAX_BUFFER_SIZE];
    int index = 0;

    va_list args;
    va_start(args, format);

    for (const char *p = format; *p != '\0'; p++) {
        if (*p == '%' && *(p + 1) != '\0') {
            p++;
            switch (*p) {
                case 'd': {
                    int val = va_arg(args, int);
                    index += snprintf(buffer + index, MAX_BUFFER_SIZE - index, "%d", val);
                    break;
                }
                case 'f': {
                    double val = va_arg(args, double);
                    index += snprintf(buffer + index, MAX_BUFFER_SIZE - index, "%.6f", val);
                    break;
                }
                case 's': {
                    const char *val = va_arg(args, const char *);
                    index += snprintf(buffer + index, MAX_BUFFER_SIZE - index, "%s", val);
                    break;
                }
                case 'c': {
                    char val = (char)va_arg(args, int);
                    buffer[index++] = val;
                    break;
                }
                case '%': {
                    buffer[index++] = '%';
                    break;
                }
                default: {
                    buffer[index++] = '%';
                    buffer[index++] = *p;
                    break;
                }
            }
        } else {
            buffer[index++] = *p;
        }

        if (index >= MAX_BUFFER_SIZE - 1) {
            buffer[index] = '\0';
            break;
        }
    }

    va_end(args);

    buffer[index] = '\0';

    write(STDERR_FILENO, buffer, index);
}
