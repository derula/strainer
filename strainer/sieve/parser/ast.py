from __future__ import annotations
from dataclasses import dataclass
from re import compile

from lark import Transformer, v_args, Token, Tree

from ..semantics import SemanticChecker


@dataclass
class SieveScript:
    ast: Tree

    def check(self):
        return SemanticChecker().check(self.ast).issues

    def __getattr__(self, attr):
        return getattr(self.ast, attr)


class SieveTransformer(Transformer):
    ESCAPED_CHARACTER = compile(br'\\(.)')
    start = v_args(inline=True)(SieveScript)

    @v_args(inline=True)
    def command_name(self, token: Token):
        return token

    tag = test_name = command_name

    @v_args(inline=True)
    def string(self, token: Token):
        token.value = self.ESCAPED_CHARACTER.sub(br'\1', token.value[1:-1])
        return token

    @v_args(inline=True)
    def text(self, token: Token):
        text = token.value
        token.value = text.replace(b'\r\n..', b'\r\n.')[text.index(b'\r\n')+2:-3]
        return token
