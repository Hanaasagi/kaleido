#include "libmalloc.h"
#include <stdatomic.h>

typedef struct header {
    struct header *next;
    size_t size;
    unsigned is_free;
    char padding[12];
} header_t __attribute__((aligned(16)));

#define HEADER_SIZE sizeof(header_t)

header_t *head = NULL; // Head of the free list
header_t *tail = NULL; // Tail of the free list


atomic_flag global_lock = ATOMIC_FLAG_INIT;

static void lock(atomic_flag* f) {
  do {
  // } while (atomic_flag_test_and_set(f));
  } while (atomic_flag_test_and_set_explicit(f, memory_order_acquire));
}

static void unlock(atomic_flag* f) {
  atomic_flag_clear_explicit(f, memory_order_release);
    // atomic_flag_clear(f);
}

// Find a free block
header_t *find_free_block(size_t size) {
    header_t *current = head;
    while (current) {
        if (current->is_free && current->size >= size) {
            return current;
        }
        current = current->next;
    }
    return NULL; // No free block found
}

// Request more space from the system
header_t *request_space(header_t *last, size_t size) {
    header_t *block = (header_t *)sbrk(0);
    void *request = sbrk(size + HEADER_SIZE);
    if (request == (void *)-1) {
        return NULL; // sbrk failed
    }

    if (last) { // NULL on first request
        last->next = block;
    }

    block->size = size;
    block->is_free = 0;
    block->next = NULL;

    return block;
}

void *malloc(size_t size) {
    if (size <= 0) {
        return NULL;
    }

    lock(&global_lock);
    header_t *block;
    size_t prev_size = size;
    size = ((size + (sizeof(void *) - 1)) & (~(sizeof(void *) - 1)));
    __debug("====> malloc %d bytes => %d\n", prev_size, size);

    if (!head) {
        block = request_space(NULL, size);
        if (!block) {
            unlock(&global_lock);
            return NULL;
        }
        head = block;
        tail = block;
    } else {
        header_t *last = head;
        block = find_free_block(size);
        if (!block) {
            block = request_space(tail, size);
            if (!block) {
                unlock(&global_lock);
                return NULL;
            }
            tail = block;
        } else {
            block->is_free = 0;
        }
    }

    unlock(&global_lock);
    return (block + 1);
}

void free(void *ptr) {
    if (ptr == NULL) {
        return;
    }

    lock(&global_lock);
    header_t *block = (header_t *)ptr - 1;
    block->is_free = 1;

    unlock(&global_lock);
    return;
}

void *calloc(size_t num, size_t size) {
    size_t total_size = num * size;
    void *ptr = malloc(total_size);
    if (ptr != NULL) {
        memset(ptr, 0, total_size);
    }
    return ptr;
}

void *realloc(void *ptr, size_t size) {
    if (ptr == NULL) {
        return malloc(size);
    }
    
    if (size == 0) {
        free(ptr);
        return NULL;
    }

    header_t *block = (header_t *)ptr - 1;
    if (block->size >= size) {
        return ptr;
    }

    void *new_ptr = malloc(size);
    if (!new_ptr) {
        return NULL;
    }

    memcpy(new_ptr, ptr, block->size);
    free(ptr);

    return new_ptr;
}


int main() {
    printf("Size of struct header: %zu\n", sizeof(header_t));

    // Test the malloc implementation
    void *ptr = malloc(100);
    if (ptr) {
        printf("Memory allocated at %p\n", ptr);
    } else {
        printf("Memory allocation failed\n");
    }

    // Test the calloc implementation
    void *ptr_calloc = calloc(10, 20);
    if (ptr_calloc) {
        printf("Memory allocated and zeroed at %p\n", ptr_calloc);
    } else {
        printf("Memory allocation failed\n");
    }

    // Test the realloc implementation
    void *ptr_realloc = realloc(ptr, 200);
    if (ptr_realloc) {
        printf("Memory reallocated at %p\n", ptr_realloc);
    } else {
        printf("Memory reallocation failed\n");
    }

    free(ptr);
    free(ptr_calloc);
    free(ptr_realloc);

    return 0;
}
