# ALGO: Tokens implementation is adopted from https://github.com/Jerrylum/PATH.JERRYIO under the GPLv3 license.

from enum import Enum
from typing import Union, Optional, TypeVar, Generic, List, Callable, Type
import math

# Unit.ts conversion


class UnitOfLength(float, Enum):
    Centimeter = 1.0  # default
    Millimeter = Centimeter / 10
    Meter = 100 * Centimeter  # SI base unit
    Inch = 2.54 * Centimeter
    Foot = 12 * Inch
    Tile = 23.576 * Inch  # 59.884 cm

    @staticmethod
    def from_string(s: str) -> "UnitOfLength":
        if s == "cm":
            return UnitOfLength.Centimeter
        if s == "mm":
            return UnitOfLength.Millimeter
        if s == "m":
            return UnitOfLength.Meter
        if s in ["in", "inch"]:
            return UnitOfLength.Inch
        if s in ["ft", "feet", "foot"]:
            return UnitOfLength.Foot
        if s in ["t", "tile"]:
            return UnitOfLength.Tile
        raise ValueError(f"Invalid unit of length: {s}")


class UnitOfAngle(float, Enum):
    Degree = 1.0  # default
    Radian = 180 / math.pi


Unit = Union[UnitOfLength, UnitOfAngle]

# UnitType = TypeVar("UnitType", bound=Unit)
# UnitType2 = TypeVar("UnitType2", bound=Unit)


class Quantity:
    def __init__(self, value: float, unit: Unit):
        self.value = value
        self.unit = unit

    def to(self, unit: Unit) -> float:
        return UnitConverter(self.unit, unit).from_a_to_b(self.value)


class UnitConverter:
    def __init__(self, alpha: Unit, beta: Unit):
        self.alpha = alpha
        self.beta = beta

    def from_a_to_b(self, a: float) -> float:
        return (a * self.alpha) / self.beta

    def from_b_to_a(self, b: float) -> float:
        return (b * self.beta) / self.alpha


# Tokens.ts conversion


def is_delimiter(c: Optional[str]) -> bool:
    return c is None or c == " "


def is_safe_delimiter(c: Optional[str]) -> bool:
    return (
        c is None
        or c == " "
        or c == ":"
        or c == ","
        or c == "+"
        or c == "-"
        or c == "*"
        or c == "/"
        or c == "("
        or c == ")"
    )


T = TypeVar("T", bound=Optional["Token"])


class CodePointBuffer:
    def __init__(self, target: str):
        self.target = target
        self.index = 0
        self.history = []

    def length(self) -> int:
        return len(self.target)

    def get_index(self) -> int:
        return self.index

    def at(self, index: int) -> Optional[str]:
        return self.target[index] if index < self.length() else None

    def savepoint(self) -> None:
        self.history.append(self.index)

    def rollback(self) -> None:
        self.index = self.history.pop()

    def rollback_and_return(self, value: T) -> T:
        self.rollback()
        return value

    def commit(self) -> None:
        self.history.pop()

    def commit_and_return(self, value: T) -> T:
        self.commit()
        return value

    def next(self) -> Optional[str]:
        result = self.at(self.index)
        self.index += 1
        return result

    def peek(self, offset: int = 0) -> Optional[str]:
        return self.at(self.index + offset)

    def has_next(self) -> bool:
        return self.index < self.length()

    def read_delimiter(self) -> int:
        count = 0
        while self.has_next() and is_delimiter(self.peek()):
            count += 1
            self.next()
        return count

    def read_chunk(self) -> str:
        result = ""
        while self.has_next() and not is_delimiter(self.peek()):
            result += self.next()  # type: ignore
        return result

    def read_safe_chunk(self) -> str:
        result = ""
        while self.has_next() and not is_safe_delimiter(self.peek()):
            result += self.next()  # type: ignore
        return result


def do_parse_codepoint(buffer: CodePointBuffer, accepts: List[str], token_class: Type[T]) -> Optional[T]:
    buffer.savepoint()
    target = buffer.next()
    for c in accepts:
        if target == c:
            return buffer.commit_and_return(token_class(c))  # type: ignore
    return buffer.rollback_and_return(None)


def do_parse_quote_string(buffer: CodePointBuffer, quote: str, token_class: Type[T]) -> Optional[T]:
    buffer.savepoint()
    value_sb = ""
    content_sb = ""
    escape = False
    open_quote = True

    if buffer.next() != quote:
        return buffer.rollback_and_return(None)
    value_sb += quote

    while buffer.has_next():
        c: str = buffer.next()  # type: ignore
        if escape:
            escape = False
            content_sb += c
            value_sb += c
        else:
            if c == "\\":
                escape = True
                value_sb += c
            elif c == quote:
                open_quote = False
                value_sb += c
                break
            else:
                value_sb += c
                content_sb += c

    if open_quote:
        return buffer.rollback_and_return(None)
    else:
        return buffer.commit_and_return(token_class(value_sb, content_sb))  # type: ignore


class Token:
    @staticmethod
    def parse(_buffer: CodePointBuffer) -> Optional["Token"]:
        return None

    def __eq__(self, other):
        if other is None or not isinstance(other, self.__class__):
            return False

        # Compare attributes
        for attr in vars(self):
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

    def __hash__(self):
        # Simple default implementation
        return hash(tuple(vars(self).items()))


class BackQuoteString(Token):
    def __init__(self, value: str, content: str):
        self.value = value
        self.content = content

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["BackQuoteString"]:
        return do_parse_quote_string(buffer, "`", BackQuoteString)


class BooleanT(Token):
    def __init__(self, value: str, bool_val: bool):
        self.value = value
        self.bool = bool_val

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["BooleanT"]:
        buffer.savepoint()
        s = buffer.read_chunk()
        if s.lower() == "true":
            return buffer.commit_and_return(BooleanT(s, True))
        elif s.lower() == "false":
            return buffer.commit_and_return(BooleanT(s, False))
        else:
            return buffer.rollback_and_return(None)


class DecimalPoint(Token):
    value = "."

    def __init__(self, _value=None):
        pass

    def __eq__(self, other):
        return isinstance(other, DecimalPoint)

    def __hash__(self):
        return hash("DecimalPoint")

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["DecimalPoint"]:
        return do_parse_codepoint(buffer, ["."], DecimalPoint)


class Digit(Token):
    def __init__(self, value: str):
        self.value = value

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["Digit"]:
        return do_parse_codepoint(buffer, ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], Digit)


class Digit1To9(Token):
    def __init__(self, value: str):
        self.value = value

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["Digit1To9"]:
        return do_parse_codepoint(buffer, ["1", "2", "3", "4", "5", "6", "7", "8", "9"], Digit1To9)


class DoubleQuoteString(Token):
    def __init__(self, value: str, content: str):
        self.value = value
        self.content = content

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["DoubleQuoteString"]:
        return do_parse_quote_string(buffer, '"', DoubleQuoteString)


class Frac(Token):
    def __init__(self, value: str):
        self.value = value

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["Frac"]:
        buffer.savepoint()
        result = ""
        d = DecimalPoint.parse(buffer)
        if not d:
            return buffer.rollback_and_return(None)
        result += d.value

        has_digit = False
        while True:
            d0t9 = Digit.parse(buffer)
            if d0t9 is None:
                break
            result += d0t9.value
            has_digit = True

        if not has_digit:
            return buffer.rollback_and_return(None)

        return buffer.commit_and_return(Frac(result))


class Int(Token):
    def __init__(self, value: str):
        self.value = value

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["Int"]:
        buffer.savepoint()
        z = Zero.parse(buffer)
        if z:
            return buffer.commit_and_return(Int(z.value))
        else:
            p = PositiveInt.parse(buffer)
            if not p:
                return buffer.rollback_and_return(None)
            return buffer.commit_and_return(Int(p.value))


class Minus(Token):
    value = "-"

    def __init__(self, _value=None):
        pass

    def __eq__(self, other):
        return isinstance(other, Minus)

    def __hash__(self):
        return hash("Minus")

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["Minus"]:
        return do_parse_codepoint(buffer, ["-"], Minus)


class NegativeInt(Token):
    def __init__(self, value: str):
        self.value = value

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["NegativeInt"]:
        buffer.savepoint()
        result = ""
        m = Minus.parse(buffer)
        if not m:
            return buffer.rollback_and_return(None)
        result += m.value

        p = PositiveInt.parse(buffer)
        if not p:
            return buffer.rollback_and_return(None)
        result += p.value

        return buffer.commit_and_return(NegativeInt(result))


class NumberT(Token):
    def __init__(self, value: str, is_positive: bool, is_double: bool):
        self.value = value
        self.is_positive = is_positive
        self.is_double = is_double

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["NumberT"]:
        buffer.savepoint()
        result = ""

        m = Minus.parse(buffer)
        if m:
            result += m.value
            is_positive = False
        else:
            is_positive = True

        p = Int.parse(buffer)
        if not p:
            return buffer.rollback_and_return(None)
        result += p.value

        f = Frac.parse(buffer)
        is_double = f is not None
        if is_double:
            result += f.value

        return buffer.commit_and_return(NumberT(result, is_positive, is_double))

    def to_int(self) -> int:
        return int(self.value)

    def to_double(self) -> float:
        return float(self.value)


class PositiveInt(Token):
    def __init__(self, value: str):
        self.value = value

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["PositiveInt"]:
        buffer.savepoint()
        result = ""

        d1t9 = Digit1To9.parse(buffer)
        if not d1t9:
            return buffer.rollback_and_return(None)
        result += d1t9.value

        while True:
            d0t9 = Digit.parse(buffer)
            if d0t9 is None:
                break
            result += d0t9.value

        return buffer.commit_and_return(PositiveInt(result))


class SingleQuoteString(Token):
    def __init__(self, value: str, content: str):
        self.value = value
        self.content = content

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["SingleQuoteString"]:
        return do_parse_quote_string(buffer, "'", SingleQuoteString)


class StringT(Token):
    def __init__(self, content: str):
        self.content = content

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["StringT"]:
        c = buffer.peek()
        if not c:
            return None
        elif c == '"':
            d = DoubleQuoteString.parse(buffer)
            if not d:
                return None
            return StringT(d.content)
        elif c == "'":
            s = SingleQuoteString.parse(buffer)
            if not s:
                return None
            return StringT(s.content)
        else:
            content = buffer.read_chunk()
            return StringT(content)


class Zero(Token):
    def __init__(self, value: str):
        self.value = value

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["Zero"]:
        return do_parse_codepoint(buffer, ["0"], Zero)


class OpenBracket(Token):
    value = "("

    def __init__(self, _value=None):
        pass

    def __eq__(self, other):
        return isinstance(other, OpenBracket)

    def __hash__(self):
        return hash("OpenBracket")

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["OpenBracket"]:
        return do_parse_codepoint(buffer, ["("], OpenBracket)


class CloseBracket(Token):
    value = ")"

    def __init__(self, _value=None):
        pass

    def __eq__(self, other):
        return isinstance(other, CloseBracket)

    def __hash__(self):
        return hash("CloseBracket")

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["CloseBracket"]:
        return do_parse_codepoint(buffer, [")"], CloseBracket)


class NumberWithUnit[UT: Unit](Token):
    def __init__(self, value: str, unit: Optional[UT]):
        self.value = value
        self.unit = unit

    def to_quantity(self, inherit: UT) -> Quantity:
        return Quantity(float(self.value), self.unit or inherit)


class NumberUOL(NumberWithUnit[UnitOfLength]):
    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["NumberUOL"]:
        buffer.savepoint()

        n = NumberT.parse(buffer)
        if not n:
            return buffer.rollback_and_return(None)

        buffer.read_delimiter()
        buffer.savepoint()

        unit_text = buffer.read_safe_chunk()
        unit = None

        if unit_text == "mm":
            unit = UnitOfLength.Millimeter
            buffer.commit()
        elif unit_text == "cm":
            unit = UnitOfLength.Centimeter
            buffer.commit()
        elif unit_text == "m":
            unit = UnitOfLength.Meter
            buffer.commit()
        elif unit_text == "in" or unit_text == "inch":
            unit = UnitOfLength.Inch
            buffer.commit()
        elif unit_text == "ft" or unit_text == "feet" or unit_text == "foot":
            unit = UnitOfLength.Foot
            buffer.commit()
        elif unit_text == "t" or unit_text == "tile":
            unit = UnitOfLength.Tile
            buffer.commit()
        elif unit_text == "":
            buffer.commit()
        else:
            return buffer.rollback_and_return(None)

        return buffer.commit_and_return(NumberUOL(n.value, unit))


class NumberUOA(NumberWithUnit[UnitOfAngle]):
    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["NumberUOA"]:
        buffer.savepoint()

        n = NumberT.parse(buffer)
        if not n:
            return buffer.rollback_and_return(None)

        buffer.read_delimiter()
        buffer.savepoint()

        unit_text = buffer.read_safe_chunk()
        unit = None

        if unit_text == "deg":
            unit = UnitOfAngle.Degree
            buffer.commit()
        elif unit_text == "rad":
            unit = UnitOfAngle.Radian
            buffer.commit()
        elif unit_text == "":
            buffer.commit()
        else:
            return buffer.rollback_and_return(None)

        return buffer.commit_and_return(NumberUOA(n.value, unit))


class Operator(Token):
    def __init__(self, value: str):
        self.value = value

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["Operator"]:
        return do_parse_codepoint(buffer, ["+", "-", "*", "/"], Operator)

    @property
    def prec(self) -> int:
        if self.value in ["+", "-"]:
            return 0
        if self.value in ["*", "/"]:
            return 1
        raise ValueError("never")


TokenT = TypeVar("TokenT", bound=NumberWithUnit)


class Expression(Token, Generic[TokenT]):
    def __init__(self, tokens: List[Union[OpenBracket, CloseBracket, TokenT, Operator]]):
        self.tokens = tokens

    def __eq__(self, other):
        if not isinstance(other, Expression):
            return False

        if len(self.tokens) != len(other.tokens):
            return False

        return all(self.tokens[i] == other.tokens[i] for i in range(len(self.tokens)))

    def __hash__(self):
        return hash(tuple(self.tokens))

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["Expression"]:
        raise NotImplementedError("not implemented")

    @staticmethod
    def parse_with(
        buffer: CodePointBuffer,
        num_parser: Callable[[CodePointBuffer], Optional[TokenT]],
    ) -> Optional["Expression[TokenT]"]:
        buffer.savepoint()
        buffer.read_delimiter()
        tokens = []

        bracket = OpenBracket.parse(buffer)
        if bracket:
            tokens.append(bracket)
            e = Expression.parse_with(buffer, num_parser)
            if not e:
                return buffer.rollback_and_return(None)
            tokens.extend(e.tokens)

            close_bracket = CloseBracket.parse(buffer)
            if not close_bracket:
                return buffer.rollback_and_return(None)
            tokens.append(close_bracket)
        else:
            n = num_parser(buffer)
            if not n:
                return buffer.rollback_and_return(None)
            tokens.append(n)

        buffer.read_delimiter()
        op = Operator.parse(buffer)
        if op:
            tokens.append(op)
            e = Expression.parse_with(buffer, num_parser)
            if not e:
                return buffer.rollback_and_return(None)
            tokens.extend(e.tokens)

        return buffer.commit_and_return(Expression(tokens))


class Computation[UT: Unit](Token):
    def __init__(
        self,
        left: NumberWithUnit[UT] | "Computation[UT]",
        operator: Operator,
        right: NumberWithUnit[UT] | "Computation[UT]",
    ):
        self.left = left
        self.operator = operator
        self.right = right

    def __eq__(self, other):
        if not isinstance(other, Computation):
            return False
        return self.left == other.left and self.operator == other.operator and self.right == other.right

    def __hash__(self):
        return hash((self.left, self.operator, self.right))

    def compute(self, inherit: UT) -> float:
        if isinstance(self.left, Computation):
            left = self.left.compute(inherit)
        else:
            left = self.left.to_quantity(inherit).to(inherit)

        if isinstance(self.right, Computation):
            right = self.right.compute(inherit)
        else:
            right = self.right.to_quantity(inherit).to(inherit)

        if self.operator.value == "+":
            return left + right
        elif self.operator.value == "-":
            return left - right
        elif self.operator.value == "*":
            return left * right
        elif self.operator.value == "/":
            return left / right
        else:
            raise ValueError("never")

    @staticmethod
    def parse(buffer: CodePointBuffer) -> Optional["Computation"]:
        raise NotImplementedError("not implemented")

    @staticmethod
    def parse_with[UT2: Unit](
        buffer: CodePointBuffer,
        num_parser: Callable[[CodePointBuffer], Optional[NumberWithUnit[UT2]]],
    ) -> Optional["Computation[UT2]"]:
        e = Expression.parse_with(buffer, num_parser)
        if not e:
            return None
        if buffer.has_next():
            return None

        output: List[NumberWithUnit[UT2] | "Computation[UT2]"] = []
        stack: List[Union[OpenBracket, Operator]] = []

        def peek():
            return stack[-1] if stack else None

        def out(token: NumberWithUnit[UT2] | "Computation[UT2]"):
            output.append(token)

        def handle_pop():
            op = stack.pop()
            if isinstance(op, OpenBracket):
                return None

            right = output.pop()
            left = output.pop()

            return Computation(left, op, right)

        def handle_token(token):
            if isinstance(token, NumberWithUnit):
                out(token)
            elif isinstance(token, Operator):
                o1 = token
                o2 = peek()

                while o2 is not None and isinstance(o2, Operator) and o1.prec <= o2.prec:
                    result = handle_pop()
                    out(result)  # type: ignore
                    o2 = peek()

                stack.append(o1)
            elif isinstance(token, OpenBracket):
                stack.append(token)
            elif isinstance(token, CloseBracket):
                o = peek()
                while o is not None and not isinstance(o, OpenBracket):
                    result = handle_pop()
                    out(result)  # type: ignore
                    o = peek()
                stack.pop()  # Remove the OpenBracket

        for token in e.tokens:
            handle_token(token)

        while stack:
            result = handle_pop()
            if result:
                out(result)

        rtn = output[0]
        if isinstance(rtn, Computation):
            return rtn
        else:
            zero_buffer = CodePointBuffer("0")
            zero_token: NumberWithUnit[UT2] = num_parser(zero_buffer)  # type: ignore
            return Computation(rtn, Operator("+"), zero_token)
