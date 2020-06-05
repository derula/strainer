from sievelib.commands import ExistsCommand

# Patch sievelib bug #90
ExistsCommand.args_definition[0]['type'].append('string')

from .connection import SieveConnectionQueue, SieveErrorChecker

__all__ = ('SieveConnectionQueue', 'SieveErrorChecker')
