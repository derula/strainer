from enum import auto, Enum

__all__ = ('Style', 'TagStyle', 'IdentifierStyle')


class Style(int, Enum):
    Default = 0
    Punctuation = auto()
    Comment = auto()
    CommentMultiline = auto()
    String = auto()
    StringMultiline = auto()
    Number = auto()
    Tag = auto()
    Identifier = auto()


class TagStyle(int, Enum):
    Comparator = max(Style) + 1
    AddressPart = auto()
    MatchType = auto()


class IdentifierStyle(int, Enum):
    Control = max(TagStyle) + 1
    Action = auto()
    Test = auto()
