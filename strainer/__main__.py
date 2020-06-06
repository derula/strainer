from sys import argv, exit

from .application import Application


exit(Application(argv).exec_())
