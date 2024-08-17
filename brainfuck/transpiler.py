import argparse
import dis
import importlib
import operator
import os
import subprocess
import sys
import types
import warnings
from collections import namedtuple
from typing import Any, Callable, List, Tuple

"""
Runtime environment
- CPython 3.12.4
"""

DEBUG = os.getenv("DEBUG", "").lower() in ["1", "true"]

################################################################################
#                           CPython utils
################################################################################


class ByteCode:
    """
    CPython bytecode
    """

    def __init__(self, name: str, operand: int, trailing_cache: int) -> None:
        """
        :param name: CPython bytecode name
        :param operand: CPython bytecode argument
        :param trailing_cache: https://docs.python.org/3/library/dis.html#opcode-CACHE
        """
        self._name = name
        self._operand = operand
        self._trailing_cache = trailing_cache

    @property
    def name(self) -> str:
        return self._name

    @property
    def operand(self) -> int:
        return self._operand

    @operand.setter
    def operand(self, value: int) -> None:
        self._operand = value

    @property
    def code_size(self) -> int:
        return 1

    @property
    def occupied_size(self) -> int:
        return self.code_size + self._trailing_cache

    def to_bytes(self) -> bytes:
        """
        :return: CPython bytecode
        """
        base = [dis.opmap[self._name], self._operand]
        for _ in range(self._trailing_cache):
            base.extend([dis.opmap["CACHE"], 0])

        return bytes(base)


def define(name: str, trailing_cache: int) -> Callable[[int], ByteCode]:
    """
    :param name: CPython bytecode name
    :param trailing_cache: https://docs.python.org/3/library/dis.html#opcode-CACHE
    :return: CPython bytecode wrapper
    """

    def wraps(arg: int) -> ByteCode:
        return ByteCode(name, arg, trailing_cache)

    return wraps


def occupied_size(bytecode: List[ByteCode]) -> int:
    return sum(b.occupied_size for b in bytecode)


# access constants
LOAD_CONST = define("LOAD_CONST", 0)

# access co_names
LOAD_NAME = define("LOAD_NAME", 0)
STORE_NAME = define("STORE_NAME", 0)

# access varnames
LOAD_FAST = define("LOAD_FAST", 0)
STORE_FAST = define("STORE_FAST", 0)

# call function
CALL = define("CALL", 3)

# access list
BUILD_LIST = define("BUILD_LIST", 0)
BINARY_SUBSCR = define("BINARY_SUBSCR", 1)
STORE_SUBSCR = define("STORE_SUBSCR", 1)

# condition
POP_JUMP_IF_FALSE = define("POP_JUMP_IF_FALSE", 0)
POP_JUMP_IF_TRUE = define("POP_JUMP_IF_TRUE", 0)
JUMP_BACKWARD = define("JUMP_BACKWARD", 0)

BINARY_OP = define("BINARY_OP", 1)
COMPARE_OP = define("COMPARE_OP", 1)

RESUME = define("RESUME", 0)
RETURN_CONST = define("RETURN_CONST", 0)

COPY = define("COPY", 0)
SWAP = define("SWAP", 0)
PUSH_NULL = define("PUSH_NULL", 0)
POP_TOP = define("POP_TOP", 0)

EXTENDED_ARG = define("EXTENDED_ARG", 0)
KW_NAMES = define("KW_NAMES", 0)

# _nb_ops is not public in dis module
NB_MULTIPLY = 5
NB_ADD = 13
NB_SUBTRACT = 23
CMP_EQ = 40

################################################################################
#                               Code Gen
################################################################################

RUNTIME_STACK_SIZE = 512


class CodeGenerator:
    """
    Brainfuck -> CPython(3.12.4) bytecode generator
    """

    def __init__(self, constants, names, varnames) -> None:
        self.constants = constants
        self.names = names
        self.varnames = varnames

    def const_index(self, value: Any) -> int:
        return self.constants.index(value)

    def name_index(self, name: str) -> int:
        return self.names.index(name)

    def varname_index(self, name: str) -> int:
        return self.varnames.index(name)

    def memset_stack(self) -> List[ByteCode]:
        """
        initialize stack and fill it with zeros
        """
        return [
            LOAD_CONST(self.const_index(0)),
            BUILD_LIST(1),
            LOAD_CONST(self.const_index(RUNTIME_STACK_SIZE)),
            BINARY_OP(NB_MULTIPLY),
            STORE_NAME(self.name_index("stack")),
        ]

    def show_stack(self) -> List[ByteCode]:
        """
        show stack
        """
        return [
            PUSH_NULL(0),
            LOAD_NAME(self.name_index("print")),
            LOAD_NAME(self.name_index("stack")),
            CALL(1),
        ]

    def memset_ptr(self) -> List[ByteCode]:
        """
        ptr = 0
        """
        return [
            LOAD_CONST(self.const_index(0)),
            STORE_FAST(self.varname_index("ptr")),
        ]

    def increment_ptr(self) -> List[ByteCode]:
        """
        ptr += 1
        """
        return [
            LOAD_FAST(self.varname_index("ptr")),
            LOAD_CONST(self.const_index(1)),
            BINARY_OP(NB_ADD),
            STORE_FAST(self.varname_index("ptr")),
        ]

    def decrement_ptr(self) -> List[ByteCode]:
        """
        ptr -= 1
        """
        return [
            LOAD_FAST(self.varname_index("ptr")),
            LOAD_CONST(self.const_index(1)),
            BINARY_OP(NB_SUBTRACT),
            STORE_FAST(self.varname_index("ptr")),
        ]

    def increment_value(self) -> List[ByteCode]:
        """
        stack[ptr] += 1
        """
        return [
            LOAD_NAME(self.name_index("stack")),
            LOAD_FAST(self.varname_index("ptr")),
            COPY(2),
            COPY(2),
            BINARY_SUBSCR(0),
            LOAD_CONST(self.const_index(1)),
            BINARY_OP(NB_ADD),
            SWAP(3),
            SWAP(2),
            STORE_SUBSCR(0),
        ]

    def decrement_value(self) -> List[ByteCode]:
        """
        stack[ptr] -= 1
        """
        return [
            LOAD_NAME(self.name_index("stack")),
            LOAD_FAST(self.varname_index("ptr")),
            COPY(2),
            COPY(2),
            BINARY_SUBSCR(0),
            LOAD_CONST(self.const_index(1)),
            BINARY_OP(NB_SUBTRACT),
            SWAP(3),
            SWAP(2),
            STORE_SUBSCR(0),
        ]

    def input_value(self) -> List[ByteCode]:
        """
        stack[ptr] = ord(input())
        """
        return [
            PUSH_NULL(0),
            LOAD_NAME(self.name_index("ord")),
            PUSH_NULL(0),
            LOAD_NAME(self.name_index("input")),
            CALL(0),
            CALL(1),
            LOAD_NAME(self.name_index("stack")),
            LOAD_FAST(self.varname_index("ptr")),
            STORE_SUBSCR(0),
        ]

    def output_value(self) -> List[ByteCode]:
        """
        print(chr(stack[ptr]))
        """
        return [
            PUSH_NULL(0),
            LOAD_NAME(self.name_index("print")),
            PUSH_NULL(0),
            LOAD_NAME(self.name_index("chr")),
            LOAD_NAME(self.name_index("stack")),
            LOAD_FAST(self.varname_index("ptr")),
            BINARY_SUBSCR(0),
            CALL(1),
            LOAD_CONST(self.const_index("")),
            KW_NAMES(self.const_index(("end",))),
            CALL(2),
        ]

    def loop_begin(self, offset: int) -> List[ByteCode]:
        """
        while stack[ptr]:
        """
        return [
            LOAD_NAME(self.name_index("stack")),
            LOAD_FAST(self.varname_index("ptr")),
            BINARY_SUBSCR(0),
            LOAD_CONST(self.const_index(0)),
            COMPARE_OP(CMP_EQ),
            # for long jump
            EXTENDED_ARG((offset >> 16) & 0xFF),
            EXTENDED_ARG((offset >> 8) & 0xFF),
            POP_JUMP_IF_TRUE(offset & 0xFF),
        ]

    def loop_end(self, offset: int) -> List[ByteCode]:
        """
        end
        """
        return [
            # for long jump
            EXTENDED_ARG((offset >> 16) & 0xFF),
            EXTENDED_ARG((offset >> 8) & 0xFF),
            JUMP_BACKWARD(offset & 0xFF),
        ]

    def loop_begin_occupied_size(self) -> int:
        size: int = sum(map(operator.attrgetter("occupied_size"), self.loop_begin(0)))
        assert size == 10
        return size

    def loop_end_occupied_size(self) -> int:
        size: int = sum(map(operator.attrgetter("occupied_size"), self.loop_end(0)))
        assert size == 3
        return size


################################################################################
#                               Transpiler
################################################################################


class Scanner:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        # This is already buffer I/O
        self.fd = open(file_path, "r")
        self._read_one()

    def _read_one(self) -> None:
        self.char = self.fd.read(1)

    def peek(self) -> str:
        return self.char

    def consume(self) -> str:
        char = self.char
        self._read_one()
        return char

    def close(self) -> None:
        if hasattr(self, "fd") and not self.fd.closed:
            self.fd.close()

    def __del__(self) -> None:
        self.close()


class Transpiler:
    """
    Brainfuck -> CPython ByteCode transpiler
    """

    # TODO: hard code
    constants = (0, 1, RUNTIME_STACK_SIZE, "", ("end",), None)
    names = ("stack", "print", "input", "ord", "chr")
    varnames = ("ptr",)

    def __init__(self, source_path: str, output_path: str) -> None:
        """
        :param source_path: source file
        :output_path: output file
        """
        self.source_path = source_path
        self.output_path = output_path

        self.codegen = CodeGenerator(self.constants, self.names, self.varnames)

    def parse_and_generate_bytecode(self) -> List[ByteCode]:
        scanner = Scanner(self.source_path)

        # initialize
        bytecode = [RESUME(0)]
        bytecode.extend(self.codegen.memset_stack())
        bytecode.extend(self.codegen.memset_ptr())

        LoopStackItem = namedtuple(
            "LoopStackItem", ["bytecode_offset", "bytecode_size_offset"]
        )
        loop_stack: List[LoopStackItem] = []

        current_occupied_size = occupied_size(bytecode)

        def append_bytecode(_bytecode: List[ByteCode]) -> None:
            nonlocal current_occupied_size
            bytecode.extend(_bytecode)
            current_occupied_size += occupied_size(_bytecode)

        while True:
            char = scanner.peek()
            if len(char) == 0:
                break
            scanner.consume()

            if char == ">":
                append_bytecode(self.codegen.increment_ptr())
            elif char == "<":
                append_bytecode(self.codegen.decrement_ptr())
            elif char == "+":
                append_bytecode(self.codegen.increment_value())
            elif char == "-":
                append_bytecode(self.codegen.decrement_value())
            elif char == ".":
                append_bytecode(self.codegen.output_value())
            elif char == ",":
                append_bytecode(self.codegen.input_value())
            elif char == "[":
                loop_stack.append(LoopStackItem(len(bytecode), current_occupied_size))
                # -1 is placeholder
                append_bytecode(self.codegen.loop_begin(-1))
            elif char == "]":
                if not loop_stack:
                    raise ValueError("Unmatched ']' encountered")

                loop_begin, occupied_size_before_loop = loop_stack.pop()
                offset = (
                    current_occupied_size
                    - occupied_size_before_loop
                    + self.codegen.loop_end_occupied_size()
                )
                append_bytecode(self.codegen.loop_end(offset))

                offset -= self.codegen.loop_begin_occupied_size()
                # replace the placeholder
                bytecode[loop_begin + 5].operand = (offset >> 16) & 0xFF
                bytecode[loop_begin + 6].operand = (offset >> 8) & 0xFF
                bytecode[loop_begin + 7].operand = offset & 0xFF

        if loop_stack:
            raise ValueError("Unmatched '[' encountered")

        bytecode.append(POP_TOP(0))
        bytecode.append(RETURN_CONST(self.codegen.const_index(None)))
        return bytecode

    def run(self) -> None:
        bytecode = self.parse_and_generate_bytecode()
        code_object = self.gen_py_code_object(bytecode)
        if DEBUG:
            dis.dis(code_object)
        self.write_file(code_object)

    def gen_co_code(self, bytecodes: List[ByteCode]) -> bytes:
        return b"".join(map(lambda x: x.to_bytes(), bytecodes))

    def gen_py_code_object(self, bytecode: List[ByteCode]) -> types.CodeType:
        co_code = self.gen_co_code(bytecode)
        filename = os.path.basename(self.source_path)
        code_object = types.CodeType(
            0,  # argcount
            0,  # posonlyargcount
            0,  # kwonlyargcount
            1,  # nlocals
            1024,  # stacksize
            0,  # flags
            co_code,
            self.constants,  # constants
            self.names,  # names
            self.varnames,  # varnames
            filename,  # filename
            "<module>",  # name
            "",  # firstlineno
            1,  # lnotab
            b"",
            b"",  # freevars
            (),  # cellvars
        )

        return code_object

    def write_file(self, code_object: types.CodeType) -> None:
        pyc_data = importlib._bootstrap_external._code_to_timestamp_pyc(code_object)  # type: ignore
        with open(self.output_path, "wb") as f:
            f.write(pyc_data)


class Interpreter:

    def __init__(self, file_path: str) -> None:
        """
        :param file_path: path to the pyc file
        """
        self._file_path = file_path

    def run(self) -> None:
        """
        exec the pyc file
        """
        subprocess.run(
            ["python", self._file_path],
            stdout=sys.stdout,
            stderr=sys.stderr,
            check=True,
        )


def parse_arguments() -> str:
    parser = argparse.ArgumentParser(description="Brainfuck transpiler")
    parser.add_argument("file_path", type=str, help="Path to the source file")

    args = parser.parse_args()
    return args.file_path


if __name__ == "__main__":
    py_version = sys.version_info
    if py_version.major != 3 and py_version.minor != 12:
        warnings.warn("This script only tests on Python 3.12")

    file_path = parse_arguments()
    path_without_ext, ext = os.path.splitext(file_path)
    pyc_path = path_without_ext + ".pyc"

    Transpiler(file_path, pyc_path).run()
    Interpreter(pyc_path).run()
