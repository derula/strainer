from .semantics import SieveScript

__all__ = ('lex', 'parse', 'SieveScript')

try:
    from .builder import load
    parser, lexer = load()
except FileNotFoundError:
    from .builder import build
    parser, lexer = build()

parse = parser.parse
lex = lexer.lex
