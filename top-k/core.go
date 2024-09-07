package top_k

import (
	// "fmt"
	"github.com/Hanaasagi/kaleido/heap"
)

type TopK[T any] struct {
	k    int
	h    *heap.Heap[T]
	less func(a, b T) bool
}

func NewTopK[T any](k int, less func(a, b T) bool) *TopK[T] {
	h := heap.New[T](k, less)

	return &TopK[T]{
		k:    k,
		h:    h,
		less: less,
	}
}

func (t *TopK[T]) Push(value T) {
	if t.h.Len() < t.k {
		t.h.Push(value)
		goto end
	}

	if t.less(t.h.Root(), value) {
		t.h.Pop()
		t.h.Push(value)
		goto end
	}

end:
	// t.printState()
}

func (t *TopK[T]) Pop() T {
	return t.h.Pop()
}

func (t *TopK[T]) Len() int {
	return t.h.Len()
}

func (t *TopK[T]) printState() {
	// fmt.Printf("Current Top %d Elements: %v\n", t.k, *t.h)
	t.h.PrintTree()
}
