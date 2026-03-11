from dataclasses import dataclass
from enum import Enum, auto

from hypal_utils.critical_zone.rule import (
    ZoneRule,
    ZoneRule_AND,
    ZoneRule_GREATER,
    ZoneRule_LESS,
    ZoneRule_NOT,
    ZoneRule_OR,
)


class TokenType(Enum):
    NUMBER = auto()
    VAR = auto()
    KW_AND = auto()
    KW_OR = auto()
    KW_NOT = auto()
    OP_LESS = auto()
    OP_GREATER = auto()
    OP_ADD = auto()
    OP_SUB = auto()
    OP_MUL = auto()
    OP_DIV = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    typ: TokenType
    value: str


class Tokenizer:
    _text: str
    _consumed: int
    _tokens: list[Token]

    def tokenize(self, t: str) -> list[Token]:
        self._text = t
        self._consumed = 0
        self._tokens = []

        while not self._is_at_end():
            while not self._is_at_end() and self._peek().isspace():
                self._consume()
            curr_char = self._consume()
            match curr_char:
                case "":
                    break

                case "(":
                    self._tokens.append(Token(TokenType.LEFT_PAREN, curr_char))
                case ")":
                    self._tokens.append(Token(TokenType.RIGHT_PAREN, curr_char))
                case "<":
                    self._tokens.append(Token(TokenType.OP_LESS, curr_char))
                case ">":
                    self._tokens.append(Token(TokenType.OP_GREATER, curr_char))
                case "+":
                    self._tokens.append(Token(TokenType.OP_ADD, curr_char))
                case "-":
                    self._tokens.append(Token(TokenType.OP_SUB, curr_char))
                case "*":
                    self._tokens.append(Token(TokenType.OP_MUL, curr_char))
                case "/":
                    self._tokens.append(Token(TokenType.OP_DIV, curr_char))
                case _:
                    if curr_char.isalpha():
                        self._tokenize_string(curr_char)
                    elif curr_char.isdigit():
                        self._tokenize_number(curr_char)
                    elif curr_char == ".":
                        self._tokenize_number(curr_char)
                    else:
                        self._tokens.append(Token(TokenType.UNKNOWN, curr_char))

        return self._tokens

    def _tokenize_string(self, curr_char: str):
        word = curr_char
        while self._peek().isalpha():
            word += self._consume()

        match word:
            case "x":
                self._tokens.append(Token(TokenType.VAR, word))
            case "and":
                self._tokens.append(Token(TokenType.KW_AND, word))
            case "or":
                self._tokens.append(Token(TokenType.KW_OR, word))
            case "not":
                self._tokens.append(Token(TokenType.KW_NOT, word))
            case _:
                self._tokens.append(Token(TokenType.UNKNOWN, word))

    def _tokenize_number(self, curr_char: str):
        number = curr_char
        has_dot = curr_char == "."
        while not self._is_at_end():
            next_char = self._peek()
            if next_char.isdigit():
                number += self._consume()
            elif next_char == "." and not has_dot:
                number += self._consume()
                has_dot = True
            else:
                break
        if number.endswith(".") and any(c.isdigit() for c in number):
            number += "0"
        if len(number) == 0 or not any(c.isdigit() for c in number):
            self._tokens.append(Token(TokenType.UNKNOWN, number if number else ""))
        else:
            self._tokens.append(Token(TokenType.NUMBER, number))

    def _is_at_end(self) -> bool:
        return self._consumed >= len(self._text)

    def _peek(self) -> str:
        if self._is_at_end():
            return ""
        return self._text[self._consumed]

    def _consume(self) -> str:
        if self._is_at_end():
            return ""
        val = self._text[self._consumed]
        self._consumed += 1
        return val


class Parser:
    def parse(self, tokens: list[Token]) -> ZoneRule:
        self.tokens = tokens
        self.pos = 0
        return self.parse_expression()

    def parse_expression(self) -> ZoneRule:
        expr = self.parse_and()
        while self.match(TokenType.KW_OR):
            right = self.parse_and()
            expr = ZoneRule_OR.model_validate(
                {"lhs": expr, "rhs": right},
            )
        return expr

    def parse_and(self) -> ZoneRule:
        expr = self.parse_not()
        while self.match(TokenType.KW_AND):
            right = self.parse_not()
            expr = ZoneRule_AND.model_validate(
                {"lhs": expr, "rhs": right},
            )
        return expr

    def parse_not(self) -> ZoneRule:
        if self.match(TokenType.KW_NOT):
            return ZoneRule_NOT.model_validate({"rule": self.parse_not()})
        return self.parse_atom()

    def parse_atom(self) -> ZoneRule:
        if self.match(TokenType.LEFT_PAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN)
            return expr
        return self.parse_condition()

    def parse_condition(self) -> ZoneRule:
        if not self.match(TokenType.VAR):
            raise ValueError("Expected 'x'")
        if self.match(TokenType.OP_LESS):
            value = self.parse_arith_expr()
            return ZoneRule_LESS.model_validate({"value": value})
        elif self.match(TokenType.OP_GREATER):
            value = self.parse_arith_expr()
            return ZoneRule_GREATER.model_validate({"value": value})
        else:
            raise ValueError("Expected < or > after 'x'")

    def parse_arith_expr(self) -> float:
        return self.parse_add()

    def parse_add(self) -> float:
        value = self.parse_mul()
        while True:
            if self.match(TokenType.OP_ADD):
                value += self.parse_mul()
            elif self.match(TokenType.OP_SUB):
                value -= self.parse_mul()
            else:
                break
        return value

    def parse_mul(self) -> float:
        value = self.parse_primary()
        while True:
            if self.match(TokenType.OP_MUL):
                value *= self.parse_primary()
            elif self.match(TokenType.OP_DIV):
                right = self.parse_primary()
                if right == 0:
                    raise ValueError("Division by zero")
                value /= right
            else:
                break
        return value

    def parse_primary(self) -> float:
        if self.match(TokenType.OP_SUB):
            return -self.parse_primary()
        if self.match(TokenType.NUMBER):
            return float(self.previous().value)
        if self.match(TokenType.LEFT_PAREN):
            value = self.parse_arith_expr()
            self.consume(TokenType.RIGHT_PAREN)
            return value
        raise ValueError("Expected number, (, or - in arithmetic expression")

    def current(self) -> Token:
        if self.pos >= len(self.tokens):
            raise ValueError("Unexpected end of input")
        return self.tokens[self.pos]

    def previous(self) -> Token:
        if self.pos == 0:
            raise ValueError("No previous token")
        return self.tokens[self.pos - 1]

    def advance(self):
        self.pos += 1

    def match(self, typ: TokenType) -> bool:
        if self.pos < len(self.tokens) and self.tokens[self.pos].typ == typ:
            self.advance()
            return True
        return False

    def consume(self, typ: TokenType):
        if not self.match(typ):
            raise ValueError(
                f"Expected {typ.name}, found {self.current().typ.name if self.pos < len(self.tokens) else 'end'}"
            )


def parse_critical_zone(t: str) -> ZoneRule | None:
    tokens = Tokenizer().tokenize(t)

    for tk in tokens:
        if tk.typ == TokenType.UNKNOWN:
            return None

    return Parser().parse(tokens)
