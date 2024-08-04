SHELL := /bin/bash

.DEFAULT_GOAL := all

.PHONY: help all clean

CC = gcc
CFLAGS = -Wall -g
OBJ = compiler.o interpreter.o main.o vec.o
DEPS = compiler.h interpreter.h vec.h
BIN_DIR = bin
TARGET = $(BIN_DIR)/interpreter

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

all: $(TARGET)  ## compile all

$(TARGET): $(OBJ)  ## compile binary
	mkdir -p $(BIN_DIR)
	$(CC) -o $@ $^ $(CFLAGS)

%.o: %.c $(DEPS)  ## compile .o and .c
	$(CC) -c -o $@ $< $(CFLAGS)

clean:  ## clean .o and bin
	rm -f *.gch *.o $(TARGET)

format:  ## Format
	clang-format -i -style=Webkit *.c *.h
