package top_k

import (
	"math/rand"
	"sort"
	"testing"
)

func lessInt(a, b int) bool {
	return a < b
}

func greaterInt(a, b int) bool {
	return a > b
}

func getTopKBySorting(arr []int, k int, compareSort func(a, b int) bool) []int {
	sort.Slice(arr, func(i, j int) bool {
		return compareSort(arr[i], arr[j])
	})
	if len(arr) < k {
		return arr
	}
	return arr[:k]
}

func commonTest(t *testing.T, arr []int, k int, less func(a, b int) bool, compareSort func(a, b int) bool) {
	expectedTopK := getTopKBySorting(append([]int{}, arr...), k, compareSort)

	topK := NewTopK[int](k, less)
	for _, val := range arr {
		topK.Push(val)
	}

	topKResult := make([]int, 0, k)
	for topK.Len() > 0 {
		topKResult = append(topKResult, topK.Pop())
	}
	sort.Slice(topKResult, func(i, j int) bool {
		return compareSort(topKResult[i], topKResult[j])
	})

	if len(topKResult) != len(expectedTopK) {
		t.Fatalf("Expected top %d elements, but got different sizes", k)
	}

	for i := range expectedTopK {
		if topKResult[i] != expectedTopK[i] {
			t.Errorf("Mismatch at index %d: expected %d, got %d", i, expectedTopK[i], topKResult[i])
		}
	}
}

func TestTopK_TopSmallK(t *testing.T) {
	arrLength := rand.Intn(90) + 10
	k := rand.Intn(10) + 1

	arr := make([]int, arrLength)
	for i := range arr {
		arr[i] = rand.Intn(1000)
	}

	commonTest(t, arr, k, greaterInt, func(a, b int) bool {
		return a < b
	})
}

func TestTopK_TopLargeK(t *testing.T) {
	arrLength := rand.Intn(90) + 10
	k := rand.Intn(10) + 1

	arr := make([]int, arrLength)
	for i := range arr {
		arr[i] = rand.Intn(100000)
	}

	commonTest(t, arr, k, lessInt, func(a, b int) bool {
		return a > b
	})
}
