package diff

import (
	"fmt"
)

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

func LcsDiff[T comparable](oldSeq, newSeq []T) []DiffResult[T] {
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
