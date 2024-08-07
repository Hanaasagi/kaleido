package main

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/Hanaasagi/kaleido"
)

func readLines(filePath string) ([]string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var lines []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}
	return lines, scanner.Err()
}

func processFiles(oldFile, newFile string) error {
	oldLines, err := readLines(oldFile)
	if err != nil {
		return fmt.Errorf("failed to read old file %s: %v", oldFile, err)
	}

	newLines, err := readLines(newFile)
	if err != nil {
		return fmt.Errorf("failed to read new file %s: %v", newFile, err)
	}

	result := lcs.Diff(oldLines, newLines)

	lcs.DisplayDiff[string](result, func(s string) string {
		return s
	})

	return nil
}

func main() {
	dir := "./test_cases"
	files, err := os.ReadDir(dir)
	if err != nil {
		fmt.Printf("failed to read directory: %v\n", err)
		return
	}

	fileGroups := make(map[string][]string)

	for _, file := range files {
		if file.IsDir() {
			continue
		}

		fileName := file.Name()
		if strings.HasSuffix(fileName, "-old.txt") {
			prefix := strings.TrimSuffix(fileName, "-old.txt")
			if _, ok := fileGroups[prefix]; !ok {
				fileGroups[prefix] = make([]string, 2)
			}
			fileGroups[prefix][0] = filepath.Join(dir, fileName)
		} else if strings.HasSuffix(fileName, "-new.txt") {
			prefix := strings.TrimSuffix(fileName, "-new.txt")
			if _, ok := fileGroups[prefix]; !ok {
				fileGroups[prefix] = make([]string, 2)
			}
			fileGroups[prefix][1] = filepath.Join(dir, fileName)
		}
	}

	idx := -1

	var keys []string
	for prefix := range fileGroups {
		keys = append(keys, prefix)
	}
	sort.Strings(keys)

	for _, prefix := range keys {
		idx += 1
		files := fileGroups[prefix]
		oldFile := files[0]
		newFile := files[1]

		if oldFile == "" || newFile == "" {
			fmt.Printf("Incomplete file group for case %s\n", prefix)
			continue
		}

		fmt.Printf("-------- [%02d] Diff for prefix: %s --------\n", idx, prefix)

		err := processFiles(oldFile, newFile)

		if err != nil {
			fmt.Printf("Error processing files for prefix %s: %v\n", prefix, err)
		}
	}

}
