from enum import auto, Enum

from PyQt5.Qsci import QsciScintilla, QsciLexerCustom
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QSizePolicy
from sievelib.parser import Lexer, Parser, ParseError
from sievelib.commands import get_command_instance, UnknownCommand, ControlCommand, ActionCommand, TestCommand


class Style(Enum):
    Default = 0
    Punctuation = auto()
    Comment = auto()
    String = auto()
    Number = auto()
    Tag = auto()
    Identifier = auto()

class IdentifierStyle(Enum):
    Unknown = Style.Identifier.value
    Control = auto()
    Action = auto()
    Test = auto()

class SieveLexer(QsciLexerCustom):
    _TOKEN_STYLES = {
        'left_bracket': Style.Punctuation,
        'right_bracket': Style.Punctuation,
        'left_parenthesis': Style.Punctuation,
        'right_parenthesis': Style.Punctuation,
        'left_cbracket': Style.Punctuation,
        'right_cbracket': Style.Punctuation,
        'semicolon': Style.Punctuation,
        'comma': Style.Punctuation,
        'hash_comment': Style.Comment,
        'bracket_comment': Style.Comment,
        'multiline': Style.String,
        'string': Style.String,
        'number': Style.Number,
        'tag': Style.Tag,
        'identifier': Style.Identifier,
    }
    _IDENTIFIER_STYLES = {
        'control': IdentifierStyle.Control,
        'action': IdentifierStyle.Action,
        'test':  IdentifierStyle.Test,
    }
    _FONTS = ['Source Code Pro', 'DejaVu Sans Mono', 'Monospace', 'Consolas', 'Courier New']

    def __init__(self, parent):
        super().__init__(parent)
        # QScintilla only uses the primary font family rather than searching through alternatives.
        # So we need to do this manually...
        for font in (QFont(name, 10) for name in self._FONTS):
            if font.exactMatch():
                break
        self.setDefaultFont(font)
        #self.setColor(QColor('#ff0000bf'), Style.Punctuation.value)
        self.setColor(QColor('#ff007f00'), Style.Comment.value)
        self.setColor(QColor('#ff7f0000'), Style.String.value)
        self.setColor(QColor('#ff7f0000'), Style.Number.value)
        self.setColor(QColor('#ff7f007f'), Style.Tag.value)
        self.setColor(QColor('#ff0000bf'), IdentifierStyle.Control.value)
        self.setColor(QColor('#ff0000bf'), IdentifierStyle.Action.value)
        self.setColor(QColor('#ff0000bf'), IdentifierStyle.Test.value)
        self.setFont(QFont(font.family(), 10, weight=QFont.Bold), IdentifierStyle.Control.value)
        self.setFont(QFont(font.family(), 10, weight=QFont.Bold, italic=True), IdentifierStyle.Action.value)
        self.setFont(QFont(font.family(), 10, italic=True), IdentifierStyle.Test.value)
        self._lexer = Lexer(Parser.lrules)
        self._stylingPos: int

    def language(self):
        return 'Sieve'

    def description(self, style):
        for style_class in (Style, IdentifierStyle):
            try:
                return style_class(style).name
            except ValueError:
                pass
        return ''

    def styleText(self, start, end):
        editor = self.parent()
        editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 0)
        editor.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, len(editor.text()))
        # We're alwaysd parsing the entire file.
        # This is not ideal, but QScintilla and sievelib don't cooperate nicely on multi-line comments / strings.
        # Hopefully scripts won't get too long.
        self.startStyling(0)
        start = 0
        while True:
            try:
                self._doStyleText(editor.text().encode('utf-8')[start:])
                break
            except ParseError:
                # Mark and skip past any syntactical errors
                start += self._lexer.pos + 1
                error_len = start - self._stylingPos
                editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, start - 1, error_len)
                self.setStyling(error_len, 0)

    def _doStyleText(self, text: bytes) -> None:
        self._stylingPos = 0
        for token, value in self._lexer.scan(text):
            length = self._lexer.pos - self._stylingPos
            style = self._TOKEN_STYLES[token]
            # Get the correct sub-style for identifiers
            if style is Style.Identifier:
                try:
                    command = get_command_instance(value.decode('ascii'), checkexists=False)
                    style = self._IDENTIFIER_STYLES[command.get_type()]
                except (UnknownCommand, NotImplementedError, KeyError):
                    style = IdentifierStyle.Unknown
            self.setStyling(length, style.value)
            self._stylingPos = self._lexer.pos

class Editor(QsciScintilla):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(300, 200))
        self.setUtf8(True)
        self.setEolMode(QsciScintilla.EolWindows)
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setLexer(SieveLexer(self))

    def sizeHint(self):
        return QSize(450, 300)
