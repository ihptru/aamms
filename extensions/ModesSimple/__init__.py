from . import ModeCommands
from . import LadderHandlers
from . import SimpleMode
import atexit

SimpleMode.LoadModes()
atexit.register(SimpleMode.SaveModes)
exit_handlers=[SimpleMode.SaveModes]
if len(SimpleMode.modes):
    next(iter(SimpleMode.modes.values())).activate() # Get first mode and activate it

def __del__():
    for x in globals():
        if type(globals()[x])==type(__builtins__):
            if hasattr(globals()[x], "__del__"):
                globals()[x].__del__()
    for x in exit_handlers:
        atexit.unregister(x)