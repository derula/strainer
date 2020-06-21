from functools import partial

from PyQt5.Qsci import QsciScintilla, QsciLexerCustom
from PyQt5.QtGui import QFontDatabase, QFont, QColor
from sievelib.parser import Parser, ParseError
from sievelib.commands import UnknownCommand, comparator, address_part, match_type, get_command_instance

from .styles import Style, TagStyle, IdentifierStyle


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
        'bracket_comment': Style.CommentMultiline,
        'multiline': Style.StringMultiline,
        'string': Style.String,
        'number': Style.Number,
        'tag': Style.Tag,
        'identifier': Style.Identifier,
    }
    _TAG_STYLES = {
        **{value: TagStyle.Comparator for value in comparator['values']},
        **{value: TagStyle.AddressPart for value in address_part['values']},
        **{value: TagStyle.MatchType for value in match_type['values']},
    }
    _IDENTIFIER_STYLES = {
        'control': IdentifierStyle.Control,
        'action': IdentifierStyle.Action,
        'test':  IdentifierStyle.Test,
    }
    _STYLE_SETTINGS = {
        Style.Comment: ('#007f00', {}),
        Style.CommentMultiline: ('#007f00', {}),
        Style.String: ('#7f0000', {}),
        Style.StringMultiline: ('#7f0000', {}),
        Style.Number: ('#7f0000', {}),
        Style.Tag: ('#7f007f', {}),
        TagStyle.Comparator: ('#7f007f', {}),
        TagStyle.AddressPart: ('#7f007f', {}),
        TagStyle.MatchType: ('#7f007f', {}),
        IdentifierStyle.Control: ('#0000bf', {'weight': QFont.Bold}),
        IdentifierStyle.Action: ('#0000bf', {'weight': QFont.Bold, 'italic': True}),
        IdentifierStyle.Test: ('#0000bf', {'italic': True}),
    }
    _FONTS = ['Source Code Pro', 'Noto Mono', 'DejaVu Sans Mono', 'Monospace', 'Consolas']
    _MULTILINE_STYLES = {Style.CommentMultiline, Style.StringMultiline}

    def __init__(self, parent):
        super().__init__(parent)
        # QScintilla only uses the primary font family rather than searching through alternatives.
        # So we need to do this manually...
        db = QFontDatabase()
        fonts = set(db.families(QFontDatabase.WritingSystem.Latin))
        for font_name in self._FONTS:
            if font_name in fonts:
                font = QFont(font_name, 10)
                break
        else:
            font = db.systemFont(QFontDatabase.FixedFont)
        self.setDefaultFont(font)
        for style, (color, font_kwargs) in self._STYLE_SETTINGS.items():
            self.setColor(QColor(color), style)
            self.setFont(QFont(font.family(), font.pointSize(), **font_kwargs), style)
        self._lexer = Parser().lexer
        self._stylingPos: int
        for style in set(TagStyle) | set(IdentifierStyle):
            parent.SendScintilla(QsciScintilla.SCI_STYLESETHOTSPOT, style, True)
        self.getStyling = partial(parent.SendScintilla, QsciScintilla.SCI_GETSTYLEAT)

    def language(self):
        return 'Sieve'

    def description(self, style):
        for style_class in (Style, TagStyle, IdentifierStyle):
            try:
                return style_class(style).name
            except ValueError:
                pass
        return ''

    def styleText(self, start, end):
        editor = self.parent()
        start, end = self._fixRange(start, end)
        editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 0)
        editor.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, editor.length())
        while True:
            try:
                self._doStyleText(start, end)
                break
            except ParseError:
                # Mark and skip past any syntactical errors
                start += self._lexer.pos + 1
                editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, start - 1, 1)
                self.setStyling(1, 0)

    def _fixRange(self, start, end):
        editor = self.parent()
        # Include current block of the same style (use case: removing text:, ., /*, or */)
        while start > 0 and self.getStyling(start) == self.getStyling(start - 1):
            start -= 1
        while end < editor.length() and self.getStyling(end) == self.getStyling(end + 1):
            end += 1

        # Include first and last error (use case: adding text:, ., /*, or */)
        if editor.SendScintilla(QsciScintilla.SCI_INDICATORVALUEAT, 0, 0):
            start = 0
        else:
            first_error = editor.SendScintilla(QsciScintilla.SCI_INDICATOREND, 0, 0)
            if first_error:  # because if there is no error, SCI_INDICATOREND will return 0
                start = min(start, first_error)
        if editor.SendScintilla(QsciScintilla.SCI_INDICATORVALUEAT, 0, editor.length() - 1):
            end = editor.length()
        else:
            end = max(end, editor.SendScintilla(QsciScintilla.SCI_INDICATORSTART, 0, editor.length()))

        return start, end

    def _doStyleText(self, start: int, end: int):
        self._stylingPos = 0
        self.startStyling(start)
        for style, value in self.scan(start):
            self.setStyling(self._lexer.pos - self._stylingPos - len(value), 0)
            self.setStyling(len(value), style)
            self._stylingPos = self._lexer.pos
            if start + self._lexer.pos > end:
                break

    def scan(self, start):
        editor = self.parent()
        for token, value in self._lexer.scan(editor.bytes(start, editor.length())):
            style = self._TOKEN_STYLES[token]
            # Get the correct sub-style for identifiers
            try:
                if style is Style.Tag:
                    style = self._TAG_STYLES[value.decode('ascii')]
                elif style is Style.Identifier:
                    command = get_command_instance(value.decode('ascii'), checkexists=False)
                    style = self._IDENTIFIER_STYLES[command.get_type()]
            except (UnknownCommand, NotImplementedError, KeyError):
                value_start = start + self._lexer.pos - len(value)
                editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, value_start, len(value))
            yield style, value


# Fix a bug in sievelib (adhering to \r\n as per spec)
for i, (key, _) in enumerate(Parser.lrules):
    if key == b'multiline':
        Parser.lrules[i] = (key, br'text:[^$]*?[\r\n]+\.\r?$')
