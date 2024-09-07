package heap

import (
	"testing"
)

func lessInt(a, b int) bool {
	return a < b
}

func greaterInt(a, b int) bool {
	return a > b
}

func TestHeap_PushPopMinHeap(t *testing.T) {
	h := New[int](10, lessInt)

	h.Push(3)
	h.Push(1)
	h.Push(5)
	h.Push(2)

	if val := h.Pop(); val != 1 {
		t.Errorf("Expected 1, got %d", val)
	}
	if val := h.Pop(); val != 2 {
		t.Errorf("Expected 2, got %d", val)
	}
	if val := h.Pop(); val != 3 {
		t.Errorf("Expected 3, got %d", val)
	}
	if val := h.Pop(); val != 5 {
		t.Errorf("Expected 5, got %d", val)
	}
}

func TestHeap_PushPopMaxHeap(t *testing.T) {
	h := New[int](10, greaterInt)

	h.Push(3)
	h.Push(1)
	h.Push(5)
	h.Push(2)

	if val := h.Pop(); val != 5 {
		t.Errorf("Expected 5, got %d", val)
	}
	if val := h.Pop(); val != 3 {
		t.Errorf("Expected 3, got %d", val)
	}
	if val := h.Pop(); val != 2 {
		t.Errorf("Expected 2, got %d", val)
	}
	if val := h.Pop(); val != 1 {
		t.Errorf("Expected 1, got %d", val)
	}
}

func TestHeap_EmptyPop(t *testing.T) {
	h := New[int](10, lessInt)

	val := h.Pop()
	if val != 0 {
		t.Errorf("Expected zero value, got %d", val)
	}
}

func TestHeap_PushPopSingleElement(t *testing.T) {
	h := New[int](10, lessInt)

	h.Push(42)

	if val := h.Pop(); val != 42 {
		t.Errorf("Expected 42, got %d", val)
	}
}

func TestHeap_PushPopMultipleSameElements(t *testing.T) {
	h := New[int](10, lessInt)

	h.Push(7)
	h.Push(7)
	h.Push(7)

	if val := h.Pop(); val != 7 {
		t.Errorf("Expected 7, got %d", val)
	}
	if val := h.Pop(); val != 7 {
		t.Errorf("Expected 7, got %d", val)
	}
	if val := h.Pop(); val != 7 {
		t.Errorf("Expected 7, got %d", val)
	}
}

func TestHeap_OrderAfterMultipleOperations(t *testing.T) {
	h := New[int](10, lessInt)

	h.Push(10)
	h.Push(4)
	h.Push(15)
	h.Push(3)

	if val := h.Pop(); val != 3 {
		t.Errorf("Expected 3, got %d", val)
	}

	h.Push(8)

	if val := h.Pop(); val != 4 {
		t.Errorf("Expected 4, got %d", val)
	}

	if val := h.Pop(); val != 8 {
		t.Errorf("Expected 8, got %d", val)
	}

	h.Push(2)
	h.Push(12)

	if val := h.Pop(); val != 2 {
		t.Errorf("Expected 2, got %d", val)
	}

	if val := h.Pop(); val != 10 {
		t.Errorf("Expected 10, got %d", val)
	}
}

func TestHeap_LargeDataset(t *testing.T) {
	h := New[int](10000, lessInt)

	for i := 10000; i > 0; i-- {
		h.Push(i)
	}

	for i := 1; i <= 10000; i++ {
		if val := h.Pop(); val != i {
			t.Errorf("Expected %d, got %d", i, val)
		}
	}
}

func TestHeap_LargeDataset2(t *testing.T) {
	h := New[int](10, lessInt)

	for i := 10000; i > 0; i-- {
		h.Push(i)
	}

	for i := 1; i <= 10000; i++ {
		if val := h.Pop(); val != i {
			t.Errorf("Expected %d, got %d", i, val)
		}
	}
}
