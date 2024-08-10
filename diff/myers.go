package diff

type Frontier[T comparable] struct {
	x       int
	history []DiffResult[T]
}

func MyersDiff[T comparable](oldSeq, newSeq []T) []DiffResult[T] {
	frontier := map[int]Frontier[T]{1: {x: 0, history: nil}}

	one := func(idx int) int {
		return idx - 1
	}

	oldLen := len(oldSeq)
	newLen := len(newSeq)
	for i := 0; i <= oldLen+newLen; i++ {
		for j := -i; j <= i; j += 2 {
			goDown := j == -i || (j != i && frontier[j-1].x < frontier[j+1].x)

			var oldX int
			var history []DiffResult[T]
			if goDown {
				oldX, history = frontier[j+1].x, frontier[j+1].history
			} else {
				oldX, history = frontier[j-1].x, frontier[j-1].history
				oldX++
			}

			historyCopy := append([]DiffResult[T](nil), history...)
			y := oldX - j

			if 1 <= y && y <= newLen && goDown {
				historyCopy = append(historyCopy, Added[T]{oldIndex: nil, newIndex: cloneAndGetPtr(y - 1), data: newSeq[one(y)]})
			} else if 1 <= oldX && oldX <= oldLen {
				historyCopy = append(historyCopy, Removed[T]{oldIndex: cloneAndGetPtr(oldX - 1), newIndex: nil, data: oldSeq[one(oldX)]})
			}

			for oldX < oldLen && y < newLen && oldSeq[one(oldX+1)] == newSeq[one(y+1)] {
				oldX++
				y++
				historyCopy = append(historyCopy, Common[T]{oldIndex: cloneAndGetPtr(oldX - 1), newIndex: cloneAndGetPtr(y - 1), data: oldSeq[one(oldX)]})
			}

			if oldX >= oldLen && y >= newLen {
				return historyCopy
			}

			frontier[j] = Frontier[T]{x: oldX, history: historyCopy}
		}
	}
	panic("unreachable!")
}
