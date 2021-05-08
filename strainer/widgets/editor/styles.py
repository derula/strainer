from enum import auto, Enum

__all__ = ('Style')


class Style(int, Enum):
    Default = 0
    Comment = auto()
    String = auto()
    Number = auto()
    Tag = auto()
    Control = auto()
    Action = auto()
    Test = auto()


Style.TAG_STYLES = {Style.Tag}
Style.IDENTIFIER_STYLES = {Style.Control, Style.Action, Style.Test}
