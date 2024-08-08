package diff

import "fmt"

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

type DiffAlgorithm int

const (
	Lcs DiffAlgorithm = iota
	Myers
)

func (da DiffAlgorithm) String() string {
	switch da {
	case Lcs:
		return "lcs"
	case Myers:
		return "myers"
	}
	return "unknown"
}

func Diff[T comparable](oldSeq, newSeq []T, algorithm DiffAlgorithm) []DiffResult[T] {
	switch algorithm {
	case Lcs:
		return LcsDiff(oldSeq, newSeq)
	case Myers:
		panic("unimplemented")
	}
	panic("unknown")
}
