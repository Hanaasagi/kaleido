package diff

import (
	"testing"
)

func intPtr(i int) *int {
	return &i
}

var intCases = []struct {
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
			Removed[int]{intPtr(0), nil, 1},
			Removed[int]{intPtr(1), nil, 2},
			Removed[int]{intPtr(2), nil, 3},
			Added[int]{nil, intPtr(0), 4},
			Added[int]{nil, intPtr(1), 5},
			Added[int]{nil, intPtr(2), 6},
		},
	},
}

var stringCases = []struct {
	left     []string
	right    []string
	expected []DiffResult[string]
}{
	{
		left:  []string{"a", "b", "c"},
		right: []string{"b", "c", "d"},
		expected: []DiffResult[string]{
			Removed[string]{intPtr(0), nil, "a"},
			Common[string]{intPtr(1), intPtr(0), "b"},
			Common[string]{intPtr(2), intPtr(1), "c"},
			Added[string]{nil, intPtr(2), "d"},
		},
	},
	{
		left: []string{
			"This is the first line.",
			"This is the second line.",
			"This is the third line.",
		},
		right: []string{
			"This is the first line.",
			"This is a modified second line.",
			"This is the third line.",
		},
		expected: []DiffResult[string]{
			Common[string]{intPtr(0), intPtr(0), "This is the first line."},
			Removed[string]{intPtr(1), nil, "This is the second line."},
			Added[string]{nil, intPtr(1), "This is a modified second line."},
			Common[string]{intPtr((2)), intPtr(2), "This is the third line."},
		},
	},
}

var byteCases = []struct {
	left     []byte
	right    []byte
	expected []DiffResult[byte]
}{
	{
		left:  []byte{'x', 'y', 'z'},
		right: []byte{'y', 'z', 'a'},
		expected: []DiffResult[byte]{
			Removed[byte]{intPtr(0), nil, 'x'},
			Common[byte]{intPtr(1), intPtr(0), 'y'},
			Common[byte]{intPtr(2), intPtr(1), 'z'},
			Added[byte]{nil, intPtr(2), 'a'},
		},
	},
}

func runTestCase[T comparable](t *testing.T, algorithm DiffAlgorithm, cases []struct {
	left     []T
	right    []T
	expected []DiffResult[T]
}) {
	for _, tt := range cases {
		result := Diff(tt.left, tt.right, algorithm)
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

func TestLcsDiff(t *testing.T) {
	runTestCase[int](t, Lcs, intCases)
	runTestCase[string](t, Lcs, stringCases)
	runTestCase[byte](t, Lcs, byteCases)

}

func TestMyersDiff(t *testing.T) {
	runTestCase[int](t, Myers, intCases)
	runTestCase[string](t, Myers, stringCases)
	runTestCase[byte](t, Myers, byteCases)

}
