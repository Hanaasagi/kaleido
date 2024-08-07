package lcs

import (
	"fmt"
)

func cloneAndGetPtr[T any](val T) *T {
	clone := val
	return &clone
}

// compareIntPtrs compares two *int pointers and returns true if they are equal or both nil.
func compareIntPtrs(a, b *int) bool {
	if a == nil && b == nil {
		return true
	}
	if a == nil || b == nil {
		return false
	}
	return *a == *b
}

// DiffResult is an interface for the different types of diff results.
type DiffResult[T comparable] interface {
	Type() string
	OldIndex() *int
	NewIndex() *int
	Data() T
}

// Equal compares two DiffResults and returns true if they are equal.
func Equal[T comparable](self, other DiffResult[T]) bool {
	return self.Type() == other.Type() && compareIntPtrs(self.OldIndex(), other.OldIndex()) && compareIntPtrs(self.NewIndex(), other.NewIndex()) && self.Data() == other.Data()
}

type Common[T any] struct {
	oldIndex *int
	newIndex *int
	data     T
}

func (c Common[T]) Type() string {
	return "common"
}
func (c Common[T]) OldIndex() *int {
	return c.oldIndex
}
func (c Common[T]) NewIndex() *int {
	return c.newIndex
}
func (c Common[T]) Data() T {
	return c.data
}

type Added[T any] struct {
	oldIndex *int
	newIndex *int
	data     T
}

func (a Added[T]) Type() string {
	return "added"
}
func (a Added[T]) OldIndex() *int {
	return a.oldIndex
}
func (a Added[T]) NewIndex() *int {
	return a.newIndex
}
func (a Added[T]) Data() T {
	return a.data
}

type Removed[T any] struct {
	oldIndex *int
	newIndex *int
	data     T
}

func (r Removed[T]) Type() string {
	return "removed"
}
func (r Removed[T]) OldIndex() *int {
	return r.oldIndex
}
func (r Removed[T]) NewIndex() *int {
	return r.newIndex
}
func (r Removed[T]) Data() T {
	return r.data
}

// LCS finds the longest common subsequence of two sequences
func createTable[T comparable](column, row []T) [][]int {
	rowLen := len(row)
	columnLen := len(column)

	table := make([][]int, rowLen+1)

	for i := range table {
		table[i] = make([]int, columnLen+1)
	}

	// printTable(table, left, right)

	for i := rowLen - 1; i >= 0; i-- {
		for j := columnLen - 1; j >= 0; j-- {
			if row[i] == column[j] {
				table[i][j] = table[i+1][j+1] + 1
			} else {
				table[i][j] = max(table[i+1][j], table[i][j+1])
			}
			// printTable(table, left, right)
		}
	}
	return table
}

func displayTable[T comparable](table [][]int, left, right []T) {
	fmt.Println("State:")
	fmt.Print("    ")

	for _, item := range left {
		fmt.Printf("%4v", item)
	}
	fmt.Println()

	for i, row := range table {
		if i >= 0 && i < len(right) {
			fmt.Printf("%-4v", right[i])
		} else {
			fmt.Print("    ")
		}
		for _, cell := range row {
			fmt.Printf("%4d", cell)
		}
		fmt.Println()
	}
	fmt.Println()
}

func Diff[T comparable](oldSeq, newSeq []T) []DiffResult[T] {
	var result []DiffResult[T]
	oldLen := len(oldSeq)
	newLen := len(newSeq)

	// Fast path
	if oldLen == 0 {
		for i := 0; i < newLen; i++ {
			result = append(result, Added[T]{oldIndex: nil, newIndex: cloneAndGetPtr(i), data: newSeq[i]})
		}
		return result
	} else if newLen == 0 {
		for i := 0; i < oldLen; i++ {
			result = append(result, Removed[T]{oldIndex: cloneAndGetPtr(i), newIndex: nil, data: oldSeq[i]})
		}
		return result
	}

	i, j := 0, 0
	prefixLen := 0
	// Skip same item from beggining
	for i < oldLen && j < newLen && oldSeq[j] == newSeq[i] {
		result = append(result, Common[T]{oldIndex: cloneAndGetPtr(i), newIndex: cloneAndGetPtr(j), data: oldSeq[i]})
		prefixLen++
		i++
		j++
	}

	// Skip same item from end
	suffixLen := 0
	for i < oldLen && j < newLen && oldSeq[oldLen-1-suffixLen] == newSeq[newLen-1-suffixLen] {
		suffixLen++
	}

	i, j = 0, 0
	table := createTable(oldSeq[prefixLen:oldLen-suffixLen], newSeq[prefixLen:newLen-suffixLen])
	oldLen -= prefixLen + suffixLen
	newLen -= prefixLen + suffixLen

	for i < oldLen && j < newLen {
		oldIndex := i + prefixLen
		newIndex := j + prefixLen

		if oldSeq[oldIndex] == newSeq[newIndex] {
			result = append(result, Common[T]{oldIndex: cloneAndGetPtr(oldIndex), newIndex: cloneAndGetPtr(newIndex), data: newSeq[newIndex]})
			j++
			i++
		} else if table[j+1][i] >= table[j][i+1] {
			result = append(result, Added[T]{oldIndex: nil, newIndex: cloneAndGetPtr(newIndex), data: newSeq[newIndex]})
			j++
		} else {
			result = append(result, Removed[T]{oldIndex: cloneAndGetPtr(oldIndex), newIndex: nil, data: oldSeq[oldIndex]})
			i++
		}
	}

	for i < oldLen {
		oldIndex := i + prefixLen
		result = append(result, Removed[T]{oldIndex: cloneAndGetPtr(oldIndex), newIndex: nil, data: oldSeq[oldIndex]})
		i++
	}

	for j < newLen {
		newIndex := j + prefixLen
		result = append(result, Added[T]{oldIndex: nil, newIndex: cloneAndGetPtr(newIndex), data: newSeq[newIndex]})
		j++
	}

	for i := 0; i < suffixLen; i++ {
		oldIndex := oldLen + prefixLen + i
		newIndex := newLen + prefixLen + i
		result = append(result, Common[T]{oldIndex: cloneAndGetPtr(oldIndex), newIndex: cloneAndGetPtr(newIndex), data: oldSeq[oldIndex]})
	}
	return result
}

const (
	Reset  = "\033[0m"
	Red    = "\033[31m"
	Green  = "\033[32m"
	Yellow = "\033[33m"
)

// DisplayDiff displays the diff result in a human readable format
func DisplayDiff[T comparable](diffResult []DiffResult[T], formatFunc func(T) string) {
	for _, diff := range diffResult {
		switch v := diff.(type) {
		case Common[T]:
			fmt.Printf("%s%s%s\n", Yellow, formatFunc(v.Data()), Reset)
		case Added[T]:
			fmt.Printf("%s+ %s%s\n", Green, formatFunc(v.Data()), Reset)
		case Removed[T]:
			fmt.Printf("%s- %s%s\n", Red, formatFunc(v.Data()), Reset)
		}
	}
}
