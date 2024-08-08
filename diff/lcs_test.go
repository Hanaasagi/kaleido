package diff

import (
	"testing"
)

func intPtr(i int) *int {
	return &i
}

func TestLcsDiff(t *testing.T) {
	tests := []struct {
		left     []int
		right    []int
		expected []DiffResult[int]
	}{
		{
			left:  []int{1, 2, 3},
			right: []int{2, 3, 4},
			expected: []DiffResult[int]{
				Removed[int]{intPtr(0), nil, 1},
				Common[int]{intPtr(1), intPtr(0), 2},
				Common[int]{intPtr(2), intPtr(1), 3},
				Added[int]{nil, intPtr(2), 4},
			},
		},
		{
			left:  []int{5, 6, 7},
			right: []int{5, 6, 7},
			expected: []DiffResult[int]{
				Common[int]{intPtr(0), intPtr(0), 5},
				Common[int]{intPtr(1), intPtr(1), 6},
				Common[int]{intPtr(2), intPtr(2), 7},
			},
		},
		{
			left:  []int{1, 2, 3},
			right: []int{4, 5, 6},
			expected: []DiffResult[int]{
				Added[int]{nil, intPtr(0), 4},
				Added[int]{nil, intPtr(1), 5},
				Added[int]{nil, intPtr(2), 6},
				Removed[int]{intPtr(0), nil, 1},
				Removed[int]{intPtr(1), nil, 2},
				Removed[int]{intPtr(2), nil, 3},
			},
		},
	}
	for _, tt := range tests {
		result := LcsDiff(tt.left, tt.right)
		ok := true
		if len(result) != len(tt.expected) {
			ok = false
		}
		for i := 0; ok && i < len(result); i++ {
			if !Equal(result[i], tt.expected[i]) {
				ok = false
			}

		}
		if !ok {
			t.Errorf("Diff(%v, %v) = %v, expected %v", tt.left, tt.right, result, tt.expected)
		}
	}

}
