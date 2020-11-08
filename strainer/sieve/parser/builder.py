from io import BytesIO
from os import path
import pickle
import re

from lark import Lark
from lark.common import LexerConf
from lark.lexer import PatternRE, PatternStr, TerminalDef, TraditionalLexer

from .semantics import SemanticTransformer


__path__ = path.join(path.dirname(__file__), 'sieve.')
_lark_args = {'use_bytes': True, 'g_regex_flags': re.IGNORECASE.value}


def get_lark():
    with open(__path__ + 'lark', 'r') as f:
        larkfile = f.read()
    return Lark(larkfile, parser='lalr', transformer=SemanticTransformer(), maybe_placeholders=True, **_lark_args)


def get_lexer_from_lark(lark):
    return get_lexer_from_tokens(get_lexer_tokens(lark))


def get_lexer_tokens(lark):
    tokens = [
        # Punctuation matters for parsing, but not for lexing, so we create a token for it that can be easily ignored.
        TerminalDef('PUNCTUATION', PatternRE(r'[\[\](){},;]')),
        # These tokens are ignored if part of the grammar, but we want it for pure lexing so that lexer won't die on error.
        TerminalDef('E_UNDEFINED_TOKEN', PatternRE(r'[^\0\r\n]+'), -1),
        TerminalDef('E_INVALID_LINEBREAK', PatternRE(r'\r|\n'), -1),
        TerminalDef('E_NULL_CHARACTER', PatternStr('\0'), -1),
    ]
    # Remove underscored from all tokens because we don't want / need them when lexing.
    for token in lark.lexer_conf.tokens:
        name = token.name.lstrip('_')
        if name != token.name:
            token = TerminalDef(name, token.pattern, token.priority)
        tokens.append(token)
    return tokens


def get_lexer_from_tokens(tokens):
    # When lexing, we actually _want_ to match comments as tokens, but _ignore_ punctuation.
    return TraditionalLexer(LexerConf(tokens, re, ignore=['WHITE_SPACE', 'PUNCTUATION'], **_lark_args))


def build():
    _lark = get_lark()
    return _lark.parser, get_lexer_from_lark(_lark)


def loads(data):
    return _load(data)


def load():
    return _load()


def dumps():
    return _dump(True)


def dump():
    _dump()


def _load(data=None):
    if data is None:
        data = pickle.load(open(__path__ + 'bin', 'rb'))
    else:
        data = pickle.loads(data)
    lark_data, lexer_terminals = data
    return (
        Lark.load(BytesIO(lark_data)).parser,
        get_lexer_from_tokens(
            TerminalDef.deserialize(token, {})
            for token in lexer_terminals
        )
    )


def _dump(to_string=False):
    io = BytesIO()
    lark = get_lark()
    lark.save(io)
    io.seek(0)
    data = [
        io.read(),
        [token.serialize() for token in get_lexer_tokens(lark)]
    ]
    if to_string:
        return pickle.dumps(data)
    else:
        pickle.dump(data, open(__path__ + 'bin', 'wb'))
