package skiplist

import (
	"fmt"
	"math/rand"
)

const (
	MaxLevel = 32
)

// https://github.com/redis/redis/blob/b94b714f81f54a28996b0c3724d8346dc8c868b5/src/server.h#L1341
// typedef struct zskiplistNode {
//     sds ele;
//     double score;
//     struct zskiplistNode *backward;
//     struct zskiplistLevel {
//         struct zskiplistNode *forward;
//         unsigned long span;
//     } level[];
// } zskiplistNode;

// typedef struct zskiplist {
//     struct zskiplistNode *header, *tail;
//     unsigned long length;
//     int level;
// } zskiplist;

type Node[T Ordered] struct {
	value T
	score float64
	level []struct {
		forward *Node[T]
		span    uint64
	}
	backward *Node[T]
}

func NewNode[T Ordered](level int, score float64, value T) *Node[T] {
	return &Node[T]{
		value: value,
		score: score,
		level: make([]struct {
			forward *Node[T]
			span    uint64
		}, level),
	}
}

func (n *Node[T]) Value() T {
	return n.value
}

func (n *Node[T]) Score() float64 {
	return n.score
}

type SkipList[T Ordered] struct {
	head   *Node[T]
	tail   *Node[T]
	length uint64
	level  int
}

func NewSkipList[T Ordered]() *SkipList[T] {
	return &SkipList[T]{
		head:  NewNode[T](MaxLevel, 0, *new(T)),
		level: 1,
	}
}

func (sl *SkipList[T]) Len() uint64 {
	return sl.length
}

func (sl *SkipList[T]) Height() int {
	return sl.level
}

func (sl *SkipList[T]) HeadNode() *Node[T] {
	return sl.head.level[0].forward
}

// TailNode return the tail node
func (sl *SkipList[T]) TailNode() *Node[T] {
	return sl.tail
}

func (sl *SkipList[T]) Clear() {
	sl.head = NewNode[T](MaxLevel, 0, *new(T))
	sl.tail = nil
	sl.length = 0
	sl.level = 1
}

func (sl *SkipList[T]) randomLevel() int {
	level := 1
	for rand.Float32() < 0.5 && level < MaxLevel {
		level++
	}
	return level
}

func (sl *SkipList[T]) Insert(score float64, value T) *Node[T] {
	update := make([]*Node[T], MaxLevel)
	rank := make([]uint64, MaxLevel)
	x := sl.head

	for i := sl.level - 1; i >= 0; i-- {
		if i == sl.level-1 {
			rank[i] = 0
		} else {
			rank[i] = rank[i+1]
		}
		for x.level[i].forward != nil && (x.level[i].forward.score < score || (x.level[i].forward.score == score && x.level[i].forward.value != value)) {
			rank[i] += x.level[i].span
			x = x.level[i].forward
		}
		update[i] = x
	}

	level := sl.randomLevel()
	if level > sl.level {
		for i := sl.level; i < level; i++ {
			rank[i] = 0
			update[i] = sl.head
			update[i].level[i].span = sl.length
		}
		sl.level = level
	}

	x = NewNode(level, score, value)
	for i := 0; i < level; i++ {
		x.level[i].forward = update[i].level[i].forward
		update[i].level[i].forward = x

		x.level[i].span = update[i].level[i].span - (rank[0] - rank[i])
		update[i].level[i].span = (rank[0] - rank[i]) + 1
	}

	for i := level; i < sl.level; i++ {
		update[i].level[i].span++
	}

	if update[0] != sl.head {
		x.backward = update[0]
	}

	if x.level[0].forward != nil {
		x.level[0].forward.backward = x
	} else {
		sl.tail = x
	}

	sl.length++
	return x
}

// Finds an element by its rank. The rank argument needs to be 1-based
// https://github.com/redis/redis/blob/b94b714f81f54a28996b0c3724d8346dc8c868b5/src/t_zset.c#L551
func (sl *SkipList[T]) GetElementByRank(rank uint64) *Node[T] {
	var tranversed uint64 = 0
	var x = sl.head
	for i := sl.level - 1; i >= 0; i-- {
		for x.level[i].forward != nil && (tranversed+x.level[i].span <= rank) {
			tranversed += x.level[i].span
			x = x.level[i].forward
		}
		if tranversed == rank {
			return x
		}
	}
	return nil
}

// GetRank Find the rank for an element by both score and key.
// Returns 0 when the element cannot be found, rank otherwise.
// Note that the rank is 1-based due to the span of zsl->header to the first element.
func (sl *SkipList[T]) GetRank(score float64, value T) uint64 {
	var rank uint64 = 0
	var x = sl.head
	for i := sl.level - 1; i >= 0; i-- {
		for x.level[i].forward != nil && (x.level[i].forward.score < score || (x.level[i].forward.score == score && x.level[i].forward.value <= value)) {
			rank += x.level[i].span
			x = x.level[i].forward
		}

		// x might be equal to zsl->header, so test if obj is non-nil
		if x != nil && x.score == score && x.value == value {
			return rank
		}
	}
	return 0
}

func (sl *SkipList[T]) Search(score float64, value T) *Node[T] {
	x := sl.head
	for i := sl.level - 1; i >= 0; i-- {
		for x.level[i].forward != nil && (x.level[i].forward.score < score || (x.level[i].forward.score == score && x.level[i].forward.value != value)) {
			x = x.level[i].forward
		}
	}
	x = x.level[0].forward
	if x != nil && x.score == score && x.value == value {
		return x
	}
	return nil
}

// Delete delete an element with matching score/object from the skiplist
// https://github.com/yangmiok/go-zskiplist/blob/d06ec95f9aeaa761404ccd9dd4a8b806234a7f84/zskiplist.go#L200
func (sl *SkipList[T]) Delete(score float64, value T) bool {
	update := make([]*Node[T], MaxLevel)
	x := sl.head

	for i := sl.level - 1; i >= 0; i-- {
		for x.level[i].forward != nil && (x.level[i].forward.score < score || (x.level[i].forward.score == score && x.level[i].forward.value < value)) {
			x = x.level[i].forward
		}
		update[i] = x
	}

	x = x.level[0].forward
	if x != nil && x.score == score && x.value == value {
		for i := 0; i < sl.level; i++ {
			if update[i].level[i].forward == x {
				update[i].level[i].span += x.level[i].span - 1
				update[i].level[i].forward = x.level[i].forward
			} else {
				update[i].level[i].span -= 1
			}
		}
		if x.level[0].forward != nil {
			x.level[0].forward.backward = x.backward
		} else {
			sl.tail = x.backward
		}
		for sl.level > 1 && sl.head.level[sl.level-1].forward == nil {
			sl.level--
		}
		return true
	}
	return false
}

func (sl *SkipList[T]) Display() {
	for i := sl.level - 1; i >= 0; i-- {
		x := sl.head.level[i].forward
		fmt.Printf("Level %d: ", i)
		for x != nil {
			fmt.Printf("%v ", x.value)
			x = x.level[i].forward
		}
		fmt.Println()
	}
	fmt.Println("------")
}
