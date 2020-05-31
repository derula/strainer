from sys import argv, exit

from .config import accounts
from .application import Application


exit(Application(argv, accounts).exec_())
