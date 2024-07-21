import inspect
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("JSON")


class JSONParseError(Exception):
    """
    JSON Parser Exception
    """

    def __init__(self, pos: int, context: str, message: str) -> None:
        """
        @param pos: The position in the context where the error occurred.
        @param context: The context in which the error occurred.
        @param message: The error message.
        """
        self._pos = pos
        self._context = context
        self._message = message
        super().__init__(
            f"Failed to parse JSON at position {self._pos} in '{self._context}': {self._message}"
        )

    def _format_message(self, with_color: bool = False) -> str:
        if not with_color:
            return f"Failed to parse JSON at position {self._pos} in '{self._context}': {self._message}"

        # FIXME: hard code
        n = 10
        start = max(0, self._pos - n)
        end = min(len(self._context), self._pos + n + 1)

        buf = []
        for i, char in enumerate(self._context):
            if i == self._pos:
                buf.append(f"\033[91m{char}\033[0m")  # Red
            elif start <= i < end:
                buf.append(f"\033[93m{char}\033[0m")  # Yellow
            else:
                buf.append(char)

        context_with_highlight = "".join(buf)
        return f"Failed to parse JSON at position {self._pos} in '{context_with_highlight}': {self._message}"

    def __str__(self) -> str:
        return self._format_message(with_color=True)


def is_ws(char: str) -> bool:
    """
    ws
        ""
        '0020' ws
        '000A' ws
        '000D' ws
        '0009' ws
    """
    # (chr(0x20), chr(0x0A), chr(0x0D), chr(0x09)
    return char in (" ", "\n", "\r", "\t")


def is_onenine(char: str) -> bool:
    """
    onenine
      '1' . '9'
    """

    # (0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39)
    return char in ("1", "2", "3", "4", "5", "6", "7", "8", "9")


class JSONParser:
    """
    Ref: https://www.json.org/json-en.html

    This is the JSON grammar in McKeeman Form.

    ```
    json
        element

    value
        object
        array
        string
        number
        "true"
        "false"
        "null"

    object
        '{' ws '}'
        '{' members '}'

    members
        member
        member ',' members

    member
        ws string ws ':' element

    array
        '[' ws ']'
        '[' elements ']'

    elements
        element
        element ',' elements

    element
        ws value ws

    string
        '"' characters '"'

    characters
        ""
        character characters

    character
        '0020' . '10FFFF' - '"' - '\'
        '\' escape

    escape
        '"'
        '\'
        '/'
        'b'
        'f'
        'n'
        'r'
        't'
        'u' hex hex hex hex

    hex
        digit
        'A' . 'F'
        'a' . 'f'

    number
        integer fraction exponent

    integer
        digit
        onenine digits
        '-' digit
        '-' onenine digits

    digits
        digit
        digit digits

    digit
        '0'
        onenine

    onenine
        '1' . '9'

    fraction
        ""
        '.' digits

    exponent
        ""
        'E' sign digits
        'e' sign digits

    sign
        ""
        '+'
        '-'

    ws
        ""
        '0020' ws
        '000A' ws
        '000D' ws
        '0009' ws
    ```

    """

    def __init__(self):
        self.pos = 0
        self.text = ""

    def has_more(self) -> bool:
        return self.pos < len(self.text)

    def remaining(self) -> str:
        return self.text[self.pos :]

    def reset(self) -> None:
        self.pos = 0
        self.text = ""

    def consume(self, n: int = 1) -> int:
        """
        Consume n characters in the text.
        @param n: The number of characters to consume.
        """
        to_be_consumed = self.text[self.pos : self.pos + n]

        logger.debug(
            "Consuming %d characters '\033[91m%s\033[0m' at position \033[93m%d\033[0m, caller is '\033[92m%s\033[0m'",
            n,
            to_be_consumed,
            self.pos,
            inspect.stack()[2][3],
        )

        self.pos += n

        return n

    def compare_and_consume(self, expect: str) -> bool:
        """
        Compare the next n characters in the text with expect and consume them if they match.

        @param expect: The string to compare with the next n characters in the text.
        @return: True if the next n characters in the text match expect, False otherwise.
        """
        length = len(expect)
        if self.text[self.pos : self.pos + length] == expect:
            self.consume(length)
            return True
        return False

    def peek(self) -> str:
        """
        Peek at the next character in the text.
        """
        if self.has_more():
            return self.text[self.pos]
        raise EOFError("No more characters in the text")

    def skip_whitespace(self) -> int:
        """
        Skip whitespace characters in the text.
        @return: The number of whitespace characters skipped.
        """
        n = 0
        while self.has_more():
            char = self.peek()
            if not is_ws(char):
                break
            n += self.consume()
        return n

    def parse(self, text: str):
        """
        Parse the given text.
        """
        self.reset()
        self.text = text
        return self.parse_element()

    def parse_element(self):
        self.skip_whitespace()
        value = self.parse_value()
        self.skip_whitespace()
        return value

    def parse_value(self):
        """
        value
            object
            array
            string
            number
            "true"
            "false"
            "null"
        """
        char = self.peek()

        if char == "{":
            return self.parse_object()
        elif char == "[":
            return self.parse_array()
        elif char == '"':
            return self.parse_string()
        elif char == "-" or char.isdigit():
            return self.parse_number()
        elif char == "t":
            return self.parse_true()
        elif char == "f":
            return self.parse_false()
        elif char == "n":
            return self.parse_null()

        raise JSONParseError(self.pos, self.text, f"Unexpected character: {char}")

    def parse_object(self):
        """
        object
            '{' ws '}'
            '{' members '}'

        members
            member
            member ',' members

        member
            ws string ws ':' element
        """
        assert self.compare_and_consume("{")
        self.skip_whitespace()
        if self.compare_and_consume("}"):
            return {}

        # we have members
        obj = {}
        while True:
            self.skip_whitespace()
            key = self.parse_string()
            self.skip_whitespace()

            if not self.compare_and_consume(":"):
                raise JSONParseError(self.pos, self.text, "Expected ':'")

            self.skip_whitespace()
            value = self.parse_element()
            self.skip_whitespace()

            obj[key] = value

            if self.compare_and_consume("}"):
                return obj
            elif not self.compare_and_consume(","):
                raise JSONParseError(self.pos, self.text, message="Expected ',' or '}'")

    def parse_string(self):
        """
        string
            '"' characters '"'

        characters
            ""
            character characters

        character
            '0020' . '10FFFF' - '"' - '\'
            '\' escape

        escape
            '"'
            '\'
            '/'
            'b'
            'f'
            'n'
            'r'
            't'
            'u' hex hex hex hex

        hex
            digit
            'A' . 'F'
            'a' . 'f'

        digit
            '0'
            onenine

        onenine
            '1' . '9'
        """

        self.consume()  # consume the opening "
        buf = []

        while True:
            char = self.peek()

            if char == '"':  # end of string
                self.consume()
                return "".join(buf)

            if char == "\\":
                buf.extend(self.handle_escape_sequence())
                continue

            buf.append(char)
            self.consume()

    def handle_escape_sequence(self) -> str:
        if not self.compare_and_consume("\\"):
            raise JSONParseError(self.pos, self.text, "Expected '\\'")

        escape_table = {
            '"': '"',
            "\\": "\\",
            "/": "/",
            "b": "\b",
            "f": "\f",
            "n": "\n",
            "r": "\r",
            "t": "\t",
            "u": "u",  # unicode
        }

        escape_char = self.peek()
        char = escape_table.get(escape_char)

        if char is None:
            raise JSONParseError(
                self.pos, self.text, "Invalid escape sequence: \\" + escape_char
            )

        self.consume()

        if not char == "u":
            return char

        hex_digits = ["", "", "", ""]
        for i in range(4):
            d = self.peek()
            if d not in "0123456789ABCDEFabcdef":
                raise ValueError(f"Invalid unicode escape sequence: \\u{hex_digits}")

            hex_digits[i] = d
            self.consume()
        res = chr(int("".join(hex_digits), 16))
        return res

    def parse_array(self):
        """
        array
            '[' ws ']'
            '[' elements ']'

        elements
            element
            element ',' elements

        element
            ws value ws
        """
        self.consume()  # consume [
        self.skip_whitespace()

        if self.compare_and_consume("]"):
            return []

        array = []
        while True:
            self.skip_whitespace()
            value = self.parse_value()
            array.append(value)
            self.skip_whitespace()

            if self.compare_and_consume("]"):
                return array

            if not self.compare_and_consume(","):
                raise JSONParseError(self.pos, self.text, "Expected ',' or ']'")

    def parse_true(self):
        if self.compare_and_consume("true"):
            return True
        raise JSONParseError(self.pos, self.text, "Invalid literal, expect true")

    def parse_false(self):
        if self.compare_and_consume("false"):
            return False
        raise JSONParseError(self.pos, self.text, "Invalid literal, expect false")

    def parse_null(self):
        if self.compare_and_consume("null"):
            return None
        raise JSONParseError(self.pos, self.text, "Invalid literal, expect null")

    def parse_number(self):
        """
        number
            integer fraction exponent

        fraction
            ""
            '.' digits

        exponent
            ""
            'E' sign digits
            'e' sign digits

        sign
            ""
            '+'
            '-'
        """
        integer_part = self.parse_integer()
        fraction_part = self.parse_fraction()
        exponent_part = self.parse_exponent()

        if not fraction_part and not exponent_part:
            return int(integer_part)

        return float(f"{integer_part}{fraction_part}{exponent_part}")

    def parse_integer(self) -> str:
        """
        integer
            digit
            onenine digits
            '-' digit
            '-' onenine digits

        digits
            digit
            digit digits

        digit
            '0'
            onenine

        onenine
            '1' . '9'

        """
        sign = ""
        if self.compare_and_consume("-"):
            sign = "-"

        # handle following case
        # '-' digit
        # '-' onenine digits
        if is_onenine(self.peek()):
            return sign + self.parse_onenine() + self.parse_digits()
        else:
            return sign + self.parse_digit()

    def parse_onenine(self):
        char = self.peek()
        if is_onenine(char):
            self.consume()
            return char

        raise JSONParseError(self.pos, self.text, "Expected a digit between 1 and 9")

    def parse_digits(self):
        result = ""

        while self.has_more() and self.peek().isdigit():
            result += self.peek()
            self.consume()
        return result

    def parse_digit(self) -> str:
        char = self.peek()
        if is_onenine(char):
            self.consume()
            return char
        elif char == "0":
            self.consume()
            return "0"
        raise JSONParseError(self.pos, self.text, "Expected a digit between 0 and 9")

    def parse_fraction(self):
        if not self.has_more():
            return ""

        char = self.peek()
        if self.compare_and_consume("."):
            return "." + self.parse_digits()
        return ""

    def parse_exponent(self) -> str:
        if not self.has_more():
            return ""

        char = self.peek()
        if char not in "Ee":
            return ""

        self.consume()
        sign = self.parse_sign()
        digits = self.parse_digits()
        return f"E{sign}{digits}"

    def parse_sign(self) -> str:
        char = self.peek()
        if char not in "+-":
            return ""

        self.consume()
        return char


if __name__ == "__main__":

    def run_test():
        import os
        import json

        def read_files_in_directory(directory):
            idx = 0
            for root, dirs, files in os.walk(directory):
                for file in files:
                    idx += 1
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    try:
                        parser = JSONParser()
                        custom_res = parser.parse(content)
                    except Exception as e:
                        print(
                            f"No.{idx} Failed\nFilename: {file}\nContent:\n{content}\n{'-'*40}\n"
                        )
                        raise e

                    stdlib_res = json.loads(content)
                    print(
                        f"No.{idx} Success\nFilename: {file}\nContent:\n{content}\n{'-'*40}\nStdlib: {stdlib_res}\nCustom: {custom_res}\n{'-'*40}\n"
                    )
                    assert custom_res == stdlib_res

        read_files_in_directory("./test_cases")

    run_test()
