package heap

import (
	"fmt"
	"strings"
)

type Heap[T any] struct {
	data []T
	cmp  func(a, b T) bool
}

func New[T any](cap int, cmp func(a, b T) bool) *Heap[T] {
	h := &Heap[T]{
		data: make([]T, 0, cap),
		cmp:  cmp,
	}
	return h
}

func (h *Heap[T]) Len() int {
	return h.len()
}

func (h *Heap[T]) Root() T {
	return h.data[0]
}

func (h *Heap[T]) Push(value T) {
	h.data = append(h.data, value)
	h.siftUp(h.len() - 1)
}

func (h *Heap[T]) Pop() T {
	if h.len() == 0 {
		var zero T
		return zero
	}

	n := h.len() - 1
	h.swap(0, n)
	value := h.data[n]
	h.data = h.data[:n]
	h.siftDown(0, len(h.data))
	return value
}

//           1
//      /         \
//    5             3
//  /   \         /   \
// 7     9      8

// [1, 5, 3, 7, 9 8]

// Let n be the number of elements in the heap and i be an arbitrary valid index of the array storing the heap.
// If the tree root is at index 0, with valid indices 0 through n − 1, then each element a at index i has
//
//	children at indices 2i + 1 and 2i + 2
//	its parent at index floor((i − 1) / 2).
func getParentIndex(i int) int {
	return (i - 1) / 2
}

func getLeftChildIndex(i int) int {
	return (2 * i) + 1
}

func getRightChildIndex(i int) int {
	return (2 * i) + 2
}

func (h *Heap[T]) siftUp(i int) {
	cur := i
	for {
		p := getParentIndex(cur)
		if p == cur || h.cmp(h.data[p], h.data[cur]) {
			break
		}
		h.swap(p, cur)
		cur = p
	}
}

func (h *Heap[T]) siftDown(i, n int) bool {
	cur := i
	for {
		left := getLeftChildIndex(cur)
		if left >= n || left < 0 {
			break
		}

		j := left
		if right := left + 1; right < n && h.cmp(h.data[right], h.data[left]) {
			j = right
	}
		if h.cmp(h.data[cur], h.data[j]) {
			break
		}
		h.swap(cur, j)
		cur = j
	}
	return cur > i
}

func (h *Heap[T]) swap(i, j int) {
	h.data[i], h.data[j] = h.data[j], h.data[i]
}

func (h *Heap[T]) len() int {
	return len(h.data)
}

func (h *Heap[T]) PrintTree() {
	h.printTreeHelper(0, 0)
}

func (h *Heap[T]) printTreeHelper(i int, depth int) {
	if i >= len(h.data) {
		return
	}

	// // DFS
	h.printTreeHelper(getLeftChildIndex(i), depth+1)
	fmt.Println(strings.Repeat("    ", depth), h.data[i])
	h.printTreeHelper(getRightChildIndex(i), depth+1)

	// fmt.Println(h.data)
}
