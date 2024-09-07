SHELL := /bin/bash

.DEFAULT_GOAL := test

.PHONY: test example format

test:
	@go test ./...

example:
	@go run example/main.go

format:
	@go fmt .
