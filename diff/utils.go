package diff

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
