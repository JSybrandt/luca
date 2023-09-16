from . import sly
import enum
from typing import Any


class Luca:
    def __init__(self):
        self.lexer = LucaLexer()
        self.parser = LucaParser()

    def __call__(self, program: str):
        self.parser.parse(program)


class LucaType(enum.Enum):
    NULL = 1
    NUMBER = 2
    STRING = 3
    BOOLEAN = 4
    OBJECT = 5


class LucaValue:
    def __init__(self, luca_type: LucaType, value: Any):
        self.luca_type = luca_type
        self.raw_value = value

    def __eq__(self, other):
        return self.luca_type == other.luca_type and self.raw_value == other.raw_value

    def __str__(self):
        return f"{self.raw_value}({self.luca_type})"

    def logic_eq(self, other):
        ValidateSameType("==", self.luca_type, other.luca_type)
        return LucaBool(self.raw_value == other.raw_value)


class LucaNull(LucaValue):
    def __init__(self):
        super().__init__(LucaType.NULL, None)

    def __str__(self):
        return "null"


def ValidateSameType(op: str, a: LucaType, b: LucaType):
    if a != b:
        raise TypeError(f"Cannot perform {a} {op} {b}.")


class LucaString(LucaValue):
    def __init__(self, value: str):
        super().__init__(LucaType.STRING, value)

    def __add__(self, other: LucaValue):
        return LucaString(self.raw_value + str(other))

    def __str__(self):
        return self.raw_value


class LucaNumber(LucaValue):
    def __init__(self, value: int | float):
        super().__init__(LucaType.NUMBER, value)

    def __add__(self, other: LucaValue):
        ValidateSameType("+", self.luca_type, other.luca_type)
        return LucaNumber(self.raw_value + other.raw_value)

    def __sub__(self, other: LucaValue):
        ValidateSameType("-", self.luca_type, other.luca_type)
        return LucaNumber(self.raw_value - other.raw_value)

    def __mul__(self, other: LucaValue):
        ValidateSameType("*", self.luca_type, other.luca_type)
        return LucaNumber(self.raw_value * other.raw_value)

    def __truediv__(self, other: LucaValue):
        ValidateSameType("/", self.luca_type, other.luca_type)
        if other.raw_value == 0:
            raise ValueError("Cannot divide by zero.")
        return LucaNumber(self.raw_value / other.raw_value)

    def __mod__(self, other: LucaValue):
        ValidateSameType("%", self.luca_type, other.luca_type)
        if other.raw_value == 0:
            raise ValueError("Cannot mod by zero.")
        return LucaNumber(self.raw_value % other.raw_value)

    def __neg__(self):
        return LucaNumber(-self.raw_value)

    def __str__(self):
        return str(self.raw_value)


class LucaBool(LucaValue):
    def __init__(self, value: bool):
        super().__init__(LucaType.BOOLEAN, value)

    def __str__(self):
        return "true" if self.raw_value else "false"

    def logic_and(self, other: LucaValue):
        ValidateSameType("and", self.luca_type, other.luca_type)
        return LucaBool(self.raw_value and other.raw_value)

    def logic_or(self, other: LucaValue):
        ValidateSameType("or", self.luca_type, other.luca_type)
        return LucaBool(self.raw_value or other.raw_value)

    def logic_not(self):
        return LucaBool(not self.raw_value)


class LucaScope:
    def __init__(self, parent=None):
        self.names = {}
        self.parent = parent

    def set(self, name: str, value: LucaValue):
        self.names[name] = value

    def get(self, name: str) -> LucaValue:
        if name not in self.names:
            if self.parent is None:
                raise ValueError(f"{name} is not in scope.")
            return self.parent.get(name)
        return self.names[name]

    def __str__(self):
        return "{" + ",".join(f"{n}:{v}" for n, v in self.names.items()) + "}"


class LucaReference:
    def __init__(self, name: str, parent_scope: LucaScope):
        self.parent_scope = parent_scope
        self.name = name

    def get(self):
        return self.parent_scope.get(self.name)

    def set(self, value: LucaValue):
        return self.parent_scope.set(self.name, value)


class LucaObject(LucaValue):
    def __init__(self, raw_value: LucaScope):
        super().__init__(LucaType.OBJECT, raw_value)

    def get(self, name: str):
        return self.raw_value.get(name)


class LucaLexer(sly.Lexer):
    tokens = {
        AND,
        ASSIGN,
        BOOLEAN,
        EQ,
        MOD,
        NAME,
        NEQ,
        NEWLINE,
        NOT,
        NULL,
        NUMBER,
        OR,
        PRINT,
        RETURN,
        STRING,
    }
    ignore = " \t"
    ignore_comment = r"\#.*"

    EQ = r"=="
    NEQ = r"!="
    ASSIGN = r"="
    NEWLINE = r"\n"

    literals = {
        "%",
        "+",
        "-",
        "/",
        "*",
        "{",
        "}",
        "(",
        ")",
        "[",
        "]",
        ",",
        ".",
        ":",
        ";",
    }

    @_(r"\"([^\\\"]|\\.)*\"")
    def STRING(self, t):
        t.value = LucaString(t.value.strip('"'))
        return t

    @_(r"(\d*\.)?\d+")
    def NUMBER(self, t):
        try:
            t.value = LucaNumber(int(t.value))
            return t
        except (ValueError):
            pass
        try:
            t.value = LucaNumber(float(t.value))
            return t
        except (ValueError):
            pass
        raise ValueError(f"Invalid number token: {t.value}")

    @_(r"(true|false)")
    def BOOLEAN(self, t):
        t.value = LucaBool(t.value == "true")
        return t

    NAME = r"[a-zA-Z_][a-zA-Z_0-9]*"
    # Reserved words
    NAME["null"] = NULL
    NAME["return"] = RETURN
    NAME["and"] = AND
    NAME["or"] = OR
    NAME["not"] = NOT
    NAME["print"] = PRINT


class LucaParser(sly.Parser):
    debugfile = "luca_parser.debug.log"

    def __init__(self):
        super().__init__()
        self.scope_stack = [LucaScope()]

    def get(self, name: str):
        return self.current_scope().get(name)

    def add(self, name: str, value: LucaValue):
        return self.current_scope().add(name, value)

    def current_scope(self) -> LucaScope:
        return self.scope_stack[-1]

    def push_scope(self):
        self.scope_stack.append(LucaScope(self.current_scope()))

    def pop_scope(self):
        self.scope_stack.pop()

    tokens = LucaLexer.tokens

    precedence = (
        ("left", AND, OR),
        ("left", EQ),
        ("left", "+", "-"),
        ("left", "*", "/", "%"),
        # Unary negation.
        ("right", NEGATE, NOT),
        ("left", "."),
    )

    @_("stmt", "block stmt")
    def block(self, p):
        return p.stmt

    # Omit extra newlines.
    @_("NEWLINE block", "block NEWLINE")
    def block(self, p):
        return p.block

    @_('PRINT "(" expr ")"')
    def stmt(self, p):
        print(str(p.expr))
        return LucaNull()

    @_("expr")
    def stmt(self, p):
        return p.expr

    @_('expr "+" expr')
    def expr(self, p):
        return p.expr0 + p.expr1

    @_('expr "-" expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr "*" expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr "/" expr')
    def expr(self, p):
        return p.expr0 / p.expr1

    @_('expr "%" expr')
    def expr(self, p):
        return p.expr0 % p.expr1

    # Note that this formulation of - has the precendence of "NEGATE."
    @_('"-" expr %prec NEGATE')
    def expr(self, p):
        return -p.expr

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_("expr AND expr")
    def expr(self, p):
        return p.expr0.logic_and(p.expr1)

    @_("expr OR expr")
    def expr(self, p):
        return p.expr0.logic_or(p.expr1)

    @_("expr EQ expr")
    def expr(self, p):
        return p.expr0.logic_eq(p.expr1)

    @_("NOT expr")
    def expr(self, p):
        return p.expr.logic_not()

    @_("NUMBER")
    def expr(self, p):
        return p.NUMBER

    @_("STRING")
    def expr(self, p):
        return p.STRING

    @_("BOOLEAN")
    def expr(self, p):
        return p.BOOLEAN

    @_("NULL")
    def expr(self, p):
        return LucaNull()

    @_('"{" new_scope block "}"', '"{" new_scope "}"')
    def expr(self, p):
        obj = LucaObject(self.current_scope())
        self.pop_scope()
        return obj

    @_("")
    def new_scope(self, p):
        self.push_scope()

    @_('ref "." NAME')
    def ref(self, p):
        # Assumes that 'ref' is a reference to an object.
        return LucaReference(p.NAME, p.ref.get().raw_value)

    @_("NAME")
    def ref(self, p):
        return LucaReference(p.NAME, self.current_scope())

    @_("ref")
    def expr(self, p):
        return p.ref.get()

    @_("ref ASSIGN expr")
    def expr(self, p):
        p.ref.set(p.expr)
        return p.expr
