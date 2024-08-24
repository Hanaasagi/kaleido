package main

import (
	"fmt"
	"github.com/Hanaasagi/kaleido"
)


func main() {
	skiplist := skiplist.NewSkipList[int]()

	values := []int{3, 7, 6, 9, 12, 19, 17, 26, 21, 25}
	for i, v := range values {
		skiplist.Insert(float64(i), v)
	}

	fmt.Println("Skip list after insertion:")
	skiplist.Display()

	searchValues := []int{19, 15}
	for _, v := range searchValues {
		found := skiplist.Search(float64(v), v) != nil
		fmt.Printf("Search for %v: %v\n", v, found)
	}

	skiplist.Delete(float64(19), int(19))
	fmt.Println("Skip list after deletion of 19:")
	skiplist.Display()

	node := skiplist.GetElementByRank(3)
	if node != nil {

		fmt.Println("Get rand 3", node.Value())
	}
}
