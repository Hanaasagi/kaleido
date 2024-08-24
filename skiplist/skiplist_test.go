package skiplist

import (
	"testing"
)

func TestSkipListint(t *testing.T) {
	skiplist := NewSkipList[int]()
	values := []int{3, 6, 7, 9, 12, 19, 17, 26, 21, 25}

	for _, v := range values {
		skiplist.Insert(float64(v), v)
	}

	for _, v := range values {
		if skiplist.Search(float64(v), v) == nil {
			t.Errorf("Expected to find %v in skip list", v)
		}
	}

	if skiplist.Search(15.0, int(15)) != nil {
		t.Errorf("Did not expect to find 15 in skip list")
	}

	skiplist.Delete(19.0, int(19))
	if skiplist.Search(19.0, int(19)) != nil {
		t.Errorf("Expected 19 to be deleted from skip list")
	}
}

func TestSkipListfloat64(t *testing.T) {
	skiplist := NewSkipList[float64]()
	values := []float64{3.1, 6.2, 7.3, 9.4, 12.5, 19.6, 17.7, 26.8, 21.9, 25.0}

	for _, v := range values {
		skiplist.Insert(float64(v), v)
	}

	for _, v := range values {
		if skiplist.Search(float64(v), v) == nil {
			t.Errorf("Expected to find %v in skip list", v)
		}
	}

	if skiplist.Search(15.5, float64(15.5)) != nil {
		t.Errorf("Did not expect to find 15.5 in skip list")
	}

	skiplist.Delete(19.6, float64(19.6))
	if skiplist.Search(19.6, float64(19.6)) != nil {
		t.Errorf("Expected 19.6 to be deleted from skip list")
	}
}

// TestSkipListInsertAndSearch tests basic insertion and search functionality.
func TestSkipListInsertAndSearch(t *testing.T) {
	skiplist := NewSkipList[string]()
	values := []string{"apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew", "kiwi", "lemon"}

	for i, v := range values {
		skiplist.Insert(float64(i), v)
	}

	for i, v := range values {
		if skiplist.Search(float64(i), v) == nil {
			t.Errorf("Expected to find %v in skip list", v)
		}
	}
}

// TestSkipListSearchNonExistent tests searching for a value that does not exist.
func TestSkipListSearchNonExistent(t *testing.T) {
	skiplist := NewSkipList[string]()

	if skiplist.Search(float64(len("mango")), "mango") != nil {
		t.Errorf("Did not expect to find mango in skip list")
	}
}

// TestSkipListDelete tests deletion functionality.
func TestSkipListDelete(t *testing.T) {
	skiplist := NewSkipList[string]()
	values := []string{"fig"}

	skiplist.Insert(float64(len("fig")), values[0])
	skiplist.Delete(float64(len("fig")), values[0])

	if skiplist.Search(float64(len("fig")), values[0]) != nil {
		t.Errorf("Expected fig to be deleted from skip list")
	}
}

// TestSkipListInsertEmptystring tests inserting and deleting an empty string.
func TestSkipListInsertEmptystring(t *testing.T) {
	skiplist := NewSkipList[string]()

	skiplist.Insert(100.0, "")
	if skiplist.Search(100.0, "") == nil {
		t.Errorf("Expected to find empty string in skip list")
	}

	skiplist.Delete(100.0, "")
	if skiplist.Search(100.0, "") != nil {
		t.Errorf("Expected empty string to be deleted from skip list")
	}
}

// TestSkipListDuplicateInsert tests inserting duplicate values.
func TestSkipListDuplicateInsert(t *testing.T) {
	skiplist := NewSkipList[string]()

	skiplist.Insert(1.0, "duplicate")
	skiplist.Insert(1.0, "duplicate")

	// skiplist.Display()
	// if count := skiplist.Count(string("duplicate")); count != 1 {
	// 	t.Errorf("Expected to find exactly one instance of duplicate, found %d", count)
	// }
}

// TestSkipListDeleteNonExistent tests deletion of a non-existent value.
func TestSkipListDeleteNonExistent(t *testing.T) {
	skiplist := NewSkipList[string]()

	skiplist.Delete(200.0, "nonexistent")
	if skiplist.Search(200.0, "nonexistent") != nil {
		t.Errorf("Did not expect to find nonexistent in skip list")
	}
}

// TestSkipListExtremeValues tests inserting and searching extreme values.
func TestSkipListExtremeValues(t *testing.T) {
	skiplist := NewSkipList[string]()

	skiplist.Insert(1.0, "min_value")
	skiplist.Insert(999999.0, "max_value")

	if skiplist.Search(1.0, "min_value") == nil {
		t.Errorf("Expected to find min_value in skip list")
	}
	if skiplist.Search(999999.0, "max_value") == nil {
		t.Errorf("Expected to find max_value in skip list")
	}
}

// TestSkipListClear tests clearing the skip list and searching afterward.
func TestSkipListClear(t *testing.T) {
	skiplist := NewSkipList[string]()

	skiplist.Insert(1.0, "min_value")
	skiplist.Insert(999999.0, "max_value")

	skiplist.Clear()

	if skiplist.Search(1.0, "min_value") != nil {
		t.Errorf("Did not expect to find min_value after clearing skip list")
	}
	if skiplist.Search(999999.0, "max_value") != nil {
		t.Errorf("Did not expect to find max_value after clearing skip list")
	}
}

// TestSkipListSearchEmpty tests searching in an empty skip list.
func TestSkipListSearchEmpty(t *testing.T) {
	skiplist := NewSkipList[string]()

	if skiplist.Search(0.0, "anything") != nil {
		t.Errorf("Did not expect to find anything in an empty skip list")
	}
}

func TestGetElementByRank_EmptyList(t *testing.T) {
	skiplist := NewSkipList[string]()
	if node := skiplist.GetElementByRank(1); node != nil {
		t.Errorf("Expected nil, got %v", node)
	}
}

func TestGetElementByRank_OutOfRange(t *testing.T) {
	skiplist := NewSkipList[string]()
	skiplist.Insert(1, "apple")
	if node := skiplist.GetElementByRank(2); node != nil {
		t.Errorf("Expected nil, got %v", node)
	}
}

func TestGetElementByRank_FirstElement(t *testing.T) {
	skiplist := NewSkipList[string]()
	skiplist.Insert(1, "apple")
	if node := skiplist.GetElementByRank(1); node == nil || node.value != "apple" {
		t.Errorf("Expected 'apple', got %v", node.value)
	}
}

func TestGetElementByRank_LastElement(t *testing.T) {
	skiplist := NewSkipList[string]()
	skiplist.Insert(1, "apple")
	skiplist.Insert(2, "banana")
	skiplist.Insert(3, "cherry")
	if node := skiplist.GetElementByRank(3); node == nil || node.value != "cherry" {
		t.Errorf("Expected 'cherry', got %v", node.value)
	}
}

func TestGetRank_ElementNotFound(t *testing.T) {
	skiplist := NewSkipList[string]()
	skiplist.Insert(1, "apple")
	if rank := skiplist.GetRank(2, "banana"); rank != 0 {
		t.Errorf("Expected rank 0, got %v", rank)
	}
}

func TestGetRank_FirstElement(t *testing.T) {
	skiplist := NewSkipList[string]()
	skiplist.Insert(1, "apple")
	if rank := skiplist.GetRank(1, "apple"); rank != 1 {
		t.Errorf("Expected rank 1, got %v", rank)
	}
}

func TestGetRank_LastElement(t *testing.T) {
	skiplist := NewSkipList[string]()
	skiplist.Insert(1, "apple")
	skiplist.Insert(2, "banana")
	skiplist.Insert(3, "cherry")
	if rank := skiplist.GetRank(3, "cherry"); rank != 3 {
		t.Errorf("Expected rank 3, got %v", rank)
	}
}
