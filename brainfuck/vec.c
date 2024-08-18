#include "vec.h"

#include <errno.h>
#include <stdlib.h>
#include <string.h>

int vec_new(vec_t* vec, size_t item_size, size_t capacity)
{
    vec->ptr = malloc(capacity * item_size);
    if (!vec->ptr) {
        return -ENOMEM;
    }
    vec->item_size = item_size;
    vec->len = 0;
    vec->capacity = capacity;
    return 0;
}

void vec_free(vec_t* vec)
{
    free(vec->ptr);
    vec->ptr = NULL;
    vec->len = 0;
    vec->capacity = 0;
}

int vec_resize(vec_t* vec, size_t new_size)
{
    void* new_ptr = realloc(vec->ptr, new_size * vec->item_size);
    if (!new_ptr) {
        return -ENOMEM;
    }
    vec->ptr = new_ptr;
    vec->capacity = new_size;
    return 0;
}

int vec_push(vec_t* vec, void* item)
{
    if (vec->len == vec->capacity) {
        int ret = vec_resize(vec, vec->capacity * 2);
        if (ret != 0) {
            return ret;
        }
    }
    memcpy((char*)vec->ptr + vec->len * vec->item_size, item, vec->item_size);
    vec->len++;
    return 0;
}

int vec_pop(vec_t* vec, void* item)
{
    if (vec->len == 0) {
        return -EINVAL;
    }
    vec->len--;
    memcpy(item, (char*)vec->ptr + vec->len * vec->item_size, vec->item_size);
    return 0;
}

void* vec_get(vec_t* vec, size_t index)
{
    if (index >= vec->len) {
        return NULL;
    }
    return (char*)vec->ptr + index * vec->item_size;
}

void vec_iterate(vec_t* vec, void (*func)(void*))
{
    for (size_t i = 0; i < vec->len; i++) {
        func(vec_get(vec, i));
    }
}

int vec_extend_from_slice(vec_t* vec, const void* slice, size_t len)
{
    if (vec->len == vec->capacity) {
        int ret = vec_resize(vec, vec->capacity * 2);
        if (ret != 0) {
            return ret;
        }
    }

    memcpy((char*)vec->ptr + vec->len * vec->item_size, slice, len);
    vec->len += len;
    return 0;
}
