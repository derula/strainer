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
