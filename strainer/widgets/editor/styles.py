from enum import auto, Enum

__all__ = ('Style')


class Style(int, Enum):
    Default = 0
    Comment = auto()
    String = auto()
    Number = auto()
    Tag = auto()
    KnownTag = auto()
    Identifier = auto()
    Control = auto()
    Action = auto()
    Test = auto()


Style.TAG_STYLES = {Style.KnownTag}
Style.IDENTIFIER_STYLES = {Style.Control, Style.Action, Style.Test}
