from sys import argv, exit

from .widgets import Application


exit(Application(argv).exec_())
