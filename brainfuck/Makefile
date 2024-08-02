SHELL := /bin/bash

.DEFAULT_GOAL := compile

.PHONY: help compile

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

compile: ## Compile
	gcc interpreter.c vec.c vec.h -o interpreter
