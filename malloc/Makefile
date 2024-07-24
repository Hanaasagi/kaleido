SHELL := /bin/bash

.DEFAULT_GOAL := compile

.PHONY: help compile

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

compile: ## Compile
	gcc -o libmalloc.so -fPIC -shared libmalloc.c debug.c

t-ls:
	LD_PRELOAD=$$PWD/libmalloc.so ls

t-py:
	LD_PRELOAD=$$PWD/libmalloc.so python

t-node:
	LD_PRELOAD=$$PWD/libmalloc.so node

