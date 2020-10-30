from sievelib.parser import Lexer, Parser

from .connection import SieveConnectionQueue
from .parser import SieveScript

__all__ = ('SieveScript', 'SieveConnectionQueue')


# Save error line and column on error
@property
def error(self):
    return self._error


@error.setter
def error(self, msg):
    self.error_pos = (self.lexer.curlineno(), self.lexer.curcolno())
    self._error = msg


Lexer.curcolno = lambda self: self.pos - self.text.rfind(b'\n', 0, self.pos)
Parser.error = error
