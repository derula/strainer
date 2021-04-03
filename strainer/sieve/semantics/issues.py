from dataclasses import dataclass, field

from lark import Token


@dataclass(order=True)
class Issue:
    line: int
    column: int
    message: str = field(compare=False)


@dataclass
class IssueCollector:
    __dirty: bool = field(default=False, init=False)
    __issues: list = field(default_factory=list, init=False)

    def append(self, source: Token, message: str):
        self.__issues.append(Issue(source.line, source.column, message))
        self.__dirty = True

    def extend(self, other: 'IssueCollector'):
        self.__issues.extend(other.__issues)
        self.__dirty = True

    @property
    def issues(self):
        if self.__dirty:
            self.__issues = sorted(self.__issues)
            self.__dirty = False
        return sorted(self.__issues)
