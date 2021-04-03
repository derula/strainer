from lark.lexer import LexerState, LineCounter
from typing import Callable

from .ast import SieveScript

__all__ = ('lex', 'parse', 'SieveScript')

try:
    from .builder import load
    parser, lexer = load()
except FileNotFoundError:
    from .builder import build
    parser, lexer = build()

parse: Callable[[bytes], SieveScript] = parser.parse


def lex(text):
    return lexer.lex(LexerState(text, LineCounter(b'\r\n')), ...)
