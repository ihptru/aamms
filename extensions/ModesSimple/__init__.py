from . import ModeCommands
from . import LadderHandlers
from . import SimpleMode
import atexit

SimpleMode.LoadModes()
atexit.register(SimpleMode.SaveModes)
if len(SimpleMode.modes):
    next(iter(SimpleMode.modes.values())).activate() # Get first mode and activate it

class OnShutdown:
    def __del__(self):
        for x in globals():
            if type(globals()[x])==type(__builtins__):
                if hasattr(globals()[x], "onShutdown"):
                    globals()[x].onShutdown()

__on_shutdown=OnShutdown()
