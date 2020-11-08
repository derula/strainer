from sievelib import managesieve

from .connection import SieveConnectionQueue
from .parser import lex, parse, SieveScript

__all__ = ('lex', 'parse', 'SieveScript', 'SieveConnectionQueue')

# Monkeypatch sievelib#95
old_get_script = managesieve.Client.getscript


def getscript(self, name):
    script = old_get_script.__get__(self)(name)
    if script is not None:
        script = script.replace('\n', '\r\n')
    return script


managesieve.Client.getscript = getscript


# TODO remove
from sievelib import parser
# Save error line and column on error
@property
def error(self):
    return self._error
@error.setter
def error(self, msg):
    self.error_pos = (self.lexer.curlineno(), self.lexer.curcolno())
    self._error = msg
parser.Lexer.curcolno = lambda self: self.pos - self.text.rfind(b'\n', 0, self.pos)
parser.Parser.error = error
