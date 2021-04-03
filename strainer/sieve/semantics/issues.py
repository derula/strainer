from dataclasses import dataclass, field
from enum import Enum
from typing import AnyStr, List

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
    __by_type: dict = field(default_factory=lambda: {key: [] for key in IssueType}, init=False)

    def add_error(self, source: Token, message: str, *args: AnyStr):
        self.add(IssueType.ERROR, source, message, *args)

    def add_warning(self, source: Token, message: str, *args: AnyStr):
        self.add(IssueType.WARNING, source, message, *args)

    def add(self, issue_type: IssueType, source: Token, message: str, *args: AnyStr):
        def _args():
            for arg in args:
                # Token class gets confused when the value is actually `bytes`
                # instead of `str`, so we manually need to get the value.
                if isinstance(arg, Token):
                    arg = arg.value
                if isinstance(arg, bytes):
                    arg = arg.decode('utf-8')
                yield arg
        # noinspection StrFormat
        self.__issues.append(Issue(issue_type, source.line, source.column, message.format(*_args())))
        self.__dirty = True

    def extend(self, other: 'IssueCollector'):
        self.__issues.extend(other.__issues)
        self.__dirty = True

    @property
    def errors(self) -> List[Issue]:
        self.__clean()
        return self.__by_type[IssueType.ERROR]

    @property
    def warnings(self) -> List[Issue]:
        self.__clean()
        return self.__by_type[IssueType.WARNING]

    @property
    def issues(self) -> List[Issue]:
        self.__clean()
        return self.__issues

    def __clean(self):
        if not self.__dirty:
            return
        self.__issues = sorted(self.__issues)
        for key in IssueType:
            self.__by_type[key].clear()
        for issue in self.__issues:
            self.__by_type[issue.type].append(issue)
        self.__dirty = False
