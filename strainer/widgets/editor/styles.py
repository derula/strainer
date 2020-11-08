from enum import auto, Enum

__all__ = ('Style')


class Style(int, Enum):
    Default = 0
    Comment = auto()
    String = auto()
    Number = auto()
    OverUnder = auto()
    Comparator = auto()
    AddressPart = auto()
    MatchType = auto()
    Control = auto()
    Action = auto()
    Test = auto()


Style.TAG_STYLES = {Style.OverUnder, Style.Comparator, Style.AddressPart, Style.MatchType}
Style.IDENTIFIER_STYLES = {Style.Control, Style.Action, Style.Test}
