from sys import argv, exit

from .config import accounts
from .widgets import Application


exit(Application(argv, accounts).exec_())
