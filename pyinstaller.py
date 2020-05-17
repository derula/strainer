# PyInstaller insists on executing a script, then fails to recognize runpy.run_module.
# This line alone doesn't work either, because PyInstaller doesn't find the __main__ submodule.
# We also have to manually add strainer.__main__ as a hidden import for everything to work...
from strainer import __main__
