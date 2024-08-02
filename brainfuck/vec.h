#ifndef VEC_H
#define VEC_H

#include <stddef.h>

typedef struct vec {
  void *ptr;
  size_t item_size;
  size_t len;
  size_t capacity;
} vec_t;

//
int vec_new(vec_t *vec, size_t item_size, size_t capacity);

//
void vec_free(vec_t *vec);

//
int vec_resize(vec_t *vec, size_t new_size);

//
int vec_push(vec_t *vec, void *item);

//
int vec_pop(vec_t *vec, void *item);

//
void *vec_get(vec_t *vec, size_t index);

//
void vec_iterate(vec_t *vec, void (*func)(void *));

#endif
