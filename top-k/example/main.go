package main

import (
	"fmt"
	"math/rand"
	"sort"
	"strings"

	"github.com/Hanaasagi/kaleido"
)

func lessInt(a, b int) bool {
	return a < b
}


func greaterInt(a, b int) bool {
	return a > b
}


func main() {
	k := 3

	numbers := make([]int, 10)
	for i := range numbers {
		numbers[i] = rand.Intn(99)  + 1
	}

	fmt.Print("All elements: ", numbers, "\n")
	fmt.Println(strings.Repeat("====", 4))

	{

		topK := top_k.NewTopK(k, lessInt)
		for _, num := range numbers {
			topK.Push(num)
		}

		elements := make([]int, 0, k)
		for topK.Len() > 0 {
			elements = append(elements, topK.Pop())
		}

		sort.Sort(sort.Reverse(sort.IntSlice(numbers)))
		fmt.Print("After sort: ", numbers, "\n")
		fmt.Print("Top max ", k, " elements: ", elements, "\n")

	}

	fmt.Println(strings.Repeat("====", 4))

	{

		topK := top_k.NewTopK(k, greaterInt)
		for _, num := range numbers {
			topK.Push(num)
		}

		elements := make([]int, 0, k)
		for topK.Len() > 0 {
			elements = append(elements, topK.Pop())
		}

		// sort.Sort(sort.Reverse(sort.IntSlice(numbers)))
		sort.Ints(numbers)
		fmt.Print("After sort: ", numbers, "\n")
		fmt.Print("Top min ", k, " elements: ", elements, "\n")
	}
}
