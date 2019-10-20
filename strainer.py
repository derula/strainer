from sys import argv, exit

from widgets import Application


if __name__ == '__main__':
    exit(Application(argv).exec_())
