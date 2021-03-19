from functools import partial
from string import ascii_letters, digits

from PyQt5.Qsci import QsciScintilla, QsciLexerCustom
from PyQt5.QtGui import QFontDatabase, QFont, QColor

from ...sieve import lex
from .styles import Style


class SieveLexer(QsciLexerCustom):
    _TOKEN_STYLES = {
        'COMMENT': Style.Comment,
        'STRING': Style.String,
        'TEXT': Style.String,
        'NUMBER': Style.Number,
        'OVER_UNDER': Style.OverUnder,
        'COMPARATOR': Style.Comparator,
        'ADDRESS_PART': Style.AddressPart,
        'MATCH_TYPE': Style.MatchType,
        'CONTROL': Style.Control,
        'ACTION': Style.Action,
        'TEST': Style.Test,
    }
    _STYLE_SETTINGS = {
        Style.Comment: ('#007f00', {}),
        Style.String: ('#7f0000', {}),
        Style.Number: ('#7f0000', {}),
        Style.OverUnder: ('#7f007f', {}),
        Style.Comparator: ('#7f007f', {}),
        Style.AddressPart: ('#7f007f', {}),
        Style.MatchType: ('#7f007f', {}),
        Style.Control: ('#0000bf', {'weight': QFont.Bold}),
        Style.Action: ('#0000bf', {'weight': QFont.Bold, 'italic': True}),
        Style.Test: ('#0000bf', {'italic': True}),
    }
    _FONTS = ['Source Code Pro', 'Noto Mono', 'DejaVu Sans Mono', 'Monospace', 'Consolas']

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
        self.getStyling = partial(parent.SendScintilla, QsciScintilla.SCI_GETSTYLEAT)

    def language(self):
        return 'Sieve'

    def description(self, style):
        try:
            return Style(style).name
        except ValueError:
            return ''

    def wordCharacters(self):
        return ascii_letters + digits + '_:'

    def styleText(self, start, end):
        editor = self.parent()
        tokens = lex(editor.bytes(0, editor.length())[:-1])  # remove the \0 at the end (QByteArray has no .rstrip())
        tokens = self._getRelevantTokens(start, end, tokens)
        if not tokens:
            return
        last_token_end = tokens[0].pos_in_stream
        editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 0)
        editor.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, editor.length())
        self.startStyling(last_token_end)
        for token in tokens:
            token_start, token_length = token.pos_in_stream, len(token.value)
            # Whitespace is skipped by lexer, deal with it manually here
            if token_start > last_token_end:
                self.setStyling(token_start - last_token_end, 0)
            try:
                # Valid tokens
                self.setStyling(token_length, self._TOKEN_STYLES[token.type])
            except KeyError:
                # Error tokens
                self.setStyling(token_length, 0)
                editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, token_start, token_length)
            last_token_end = token_start + token_length

    def _getRelevantTokens(self, start, end, tokens):
        editor = self.parent()
        for token in tokens:
            # Fast forward to start position
            if start < token.pos_in_stream + len(token.value):
                break
            # Start styling on first error token
            if token.type.startswith('E_'):
                break
            # Start styling on first indicator
            if editor.SendScintilla(QsciScintilla.SCI_INDICATORVALUEAT, 0, token.pos_in_stream):
                break
        else:
            return ()
        tokens = (token, *tokens)
        to_token = len(tokens)
        for token in reversed(tokens):
            # Continue to last indicator
            if editor.SendScintilla(QsciScintilla.SCI_INDICATORVALUEAT, 0, token.pos_in_stream):
                break
            # Continue to last error token
            if token.type.startswith('E_'):
                break
            # Cancel at end position
            if token.pos_in_stream < end:
                break
            to_token -= 1
        return tokens[:to_token]
