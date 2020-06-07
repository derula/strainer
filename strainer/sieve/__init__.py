from sievelib.commands import ExistsCommand
from sievelib.parser import *

# Patch sievelib bug #90
ExistsCommand.args_definition[0]['type'].append('string')

# Save error line and column on error
# Due to a problem in sievelib, column number is currently at the _end_ of a token, not the start.
# Cf. tonioo/sievelib#92 for a fix.
@property
def error(self):
    return self._error

@error.setter
def error(self, msg):
    self.error_pos = (self.lexer.curlineno(), self.lexer.curcolno())
    self._error = msg

Lexer.curcolno = lambda self: self.pos - self.text.rfind(b'\n', 0, self.pos)
Parser.error = error

from .connection import *

__all__ = ('SieveConnectionQueue')
