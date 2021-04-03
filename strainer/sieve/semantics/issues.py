from dataclasses import dataclass, field
from enum import Enum
from functools import partial
from typing import List

from lark import Token


class IssueType(str, Enum):
    WARNING = 'Warning'
    ERROR = 'Error'


@dataclass(order=True)
class Issue:
    type: IssueType
    line: int
    column: int
    message: str = field(compare=False)


@dataclass
class IssueCollector:
    __dirty: bool = field(default=False, init=False)
    __issues: list = field(default_factory=list, init=False)

    def add_error(self, source: Token, message: str):
        self.add(IssueType.ERROR, source, message)

    def add_warning(self, source: Token, message: str):
        self.add(IssueType.WARNING, source, message)

    def add(self, issue_type: IssueType, source: Token, message: str):
        self.__issues.append(Issue(issue_type, source.line, source.column, message))
        self.__dirty = True

    def extend(self, other: 'IssueCollector'):
        self.__issues.extend(other.__issues)
        self.__dirty = True

    @property
    def errors(self) -> List[Issue]:
        return [issue for issue in self.issues if issue.type is IssueType.ERROR]

    @property
    def warnings(self) -> List[Issue]:
        return [issue for issue in self.issues if issue.type is IssueType.WARNING]

    @property
    def issues(self) -> List[Issue]:
        if self.__dirty:
            self.__issues = sorted(self.__issues)
            self.__dirty = False
        return sorted(self.__issues)
