"""Luca: An easy to write and implement programming language.
"""

from . import luca
import sys


def main():
    lexer = luca.LucaLexer()
    parser = luca.LucaParser()
    for line in sys.stdin:
        parser.parse(lexer.tokenize(line.strip()))


if __name__ == "__main__":
    main()
