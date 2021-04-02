from dataclasses import dataclass, field
from typing import Union

from lark import Token


class SemanticError(Exception):
    def __init__(self, token: Token, message: str):
        self.line = token.line
        self.column = token.column
        super().__init__(f'Semantic error in line {token.line}, column {token.column}: {message}')


@dataclass(order=True)
class Issue:
    line: int
    column: int
    message: str = field(compare=False)


@dataclass
class IssueCollector:
    __dirty: bool = field(default=False, init=False)
    __issues: list = field(default_factory=list, init=False)

    def add_issue(self, source: Union[Token, SemanticError], message: str):
        self.__issues.append(Issue(source.line, source.column, message))
        self.__dirty = True

    @property
    def issues(self):
        if self.__dirty:
            self.__issues = sorted(self.__issues)
            self.__dirty = False
        return sorted(self.__issues)
