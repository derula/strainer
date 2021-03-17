from __future__ import annotations
from dataclasses import dataclass
from re import compile

from lark import Transformer, v_args, Token, Tree


@dataclass
class SieveScript:
    capabilities: Capabilities
    ast: Tree

    def check(self):
        SemanticChecker(self.capabilities).check(self.ast)

    def __getattr__(self, attr):
        return getattr(self.ast, attr)


class Capabilities(frozenset):
    def __new__(cls, requires: list):
        if requires and isinstance(requires[0], Tree):
            requires = (
                b'comparator-i;ascii-casemap', b'comparator-i;octet',
                *(cap.value for node in requires for cap in node.children)
            )
        return super().__new__(cls, requires)


class SemanticTransformer(Transformer):
    ESCAPED_CHARACTER = compile(br'\\(.)')
    start = v_args(inline=True)(SieveScript)
    requires = Capabilities

    @v_args(inline=True)
    def string(self, token: Token):
        token.value = self.ESCAPED_CHARACTER.sub(br'\1', token.value[1:-1])
        return token

    @v_args(inline=True)
    def text(self, token: Token):
        text = token.value
        token.value = text.replace(b'\r\n..', b'\r\n.')[text.index(b'\r\n')+2:-3]
        return token


class SemanticError(Exception):
    def __init__(self, token: Token, message: str):
        self.line = token.line
        self.column = token.column
        super().__init__(f'Semantic error in line {token.line}, column {token.column}: {message}')


class CapabilityError(SemanticError):
    def __init__(self, token: Token, name: bytes, type: str):
        super().__init__(token, f"Used `{name.decode('utf-8')}` {type} without a respective `require`.")


class SemanticChecker():
    def __init__(self, capabilities: Capabilities):
        self._capabilities = capabilities

    def check(self, ast: Tree):
        getattr(self, ast.data)(ast.children)
        return ast

    def __getattr__(self, attr: str):
        setattr(self, attr, self.__default__)
        return self.__default__

    def __default__(self, children: list):
        for child in children:
            if isinstance(child, Tree):
                self.check(child)

    def fileinto(self, tokens: list):
        self._check_cap(tokens[-1], b'fileinto', 'command')

    def size(self, tokens: list):
        self._check_tags(tokens, {'OVER_UNDER'})

    def header(self, tokens: list):
        self._check_tags(tokens, {'COMPARATOR', 'MATCH_TYPE'})

    def address(self, tokens: list):
        self._check_tags(tokens, {'COMPARATOR', 'MATCH_TYPE', 'ADDRESS_PART'})

    def envelope(self, tokens: list):
        self._check_cap(tokens[-1].children[-1], b'envelope', 'test')
        self.address(tokens)

    def _check_tags(self, arguments: list, allowed: set):
        used = set()
        for argument in arguments:
            if not isinstance(argument, Tree) or argument.data != 'tag':
                break
            key, *values = argument.children
            if key.type not in allowed:
                raise SemanticError(key, f'{key.type} tag is not allowed here.')
            if key.type in used:
                raise SemanticError(key, f'Only one {key.type} tag may be specified.')
            if key.type == 'COMPARATOR':
                self._check_comparator(values[0])
            used.add(key.type)

    def _check_comparator(self, token: Token):
        if token:
            comparator = token.value
            self._check_cap(token, b'comparator-' + comparator, 'comparator', comparator)

    def _check_cap(self, token: Token, key: bytes, cap_type: str, cap_name: str = None):
        if key not in self._capabilities:
            if cap_name is None:
                cap_name = key
            raise CapabilityError(token, cap_name, cap_type)
