SHELL := /bin/bash

.DEFAULT_GOAL := all

.PHONY: help all clean

CC = gcc
CFLAGS = -Wall -g
BIN_DIR = bin

OBJ_COMMON = parser.o vec.o
OBJ_INTERPRETER = interpreter.o interpreter_main.o $(OBJ_COMMON)
OBJ_COMPILER = compiler.o compiler_main.o $(OBJ_COMMON)

DEPS = parser.h interpreter.h vec.h compiler.h

TARGET_INTERPRETER = $(BIN_DIR)/interpreter
TARGET_COMPILER = $(BIN_DIR)/compiler

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

all: $(TARGET_INTERPRETER) $(TARGET_COMPILER)  ## compile all

$(TARGET_INTERPRETER): $(OBJ_INTERPRETER)  ## compile interpreter binary
	mkdir -p $(BIN_DIR)
	$(CC) -o $@ $^ $(CFLAGS)

$(TARGET_COMPILER): $(OBJ_COMPILER)  ## compile compiler binary
	mkdir -p $(BIN_DIR)
	$(CC) -o $@ $^ $(CFLAGS)

%.o: %.c $(DEPS)  ## compile .o and .c
	$(CC) -c -o $@ $< $(CFLAGS)

clean:  ## clean .o and bin
	rm -f *.gch *.o $(TARGET_INTERPRETER) $(TARGET_COMPILER)

format:  ## Format
	clang-format -i -style=Webkit *.c *.h
