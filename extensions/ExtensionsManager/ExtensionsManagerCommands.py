import extensions
import Armagetronad
import Commands

## @brief Load an extension
#  @param name The name of the extension to load.
def loadExt(acl, player, name):
    Armagetronad.PrintPlayerMessage(player, "Loading "+name+ " ...")
    if extensions.loadExtension(name):
        Armagetronad.PrintPlayerMessage(player, "0xff0000Failed ----------- 0xaaaaaa"+name+" [+]")
    else:
        Armagetronad.PrintPlayerMessage(player, "0x00ff00Succeed ---------- 0xaaaaaa"+name+" [+]")

## @brief Unload an extension
#  @param name The name of the extension to unload.
def unloadExt(acl, player, name):
    Armagetronad.PrintPlayerMessage(player, "Unloading "+name+" ...")
    if extensions.unloadExtension(name):
        Armagetronad.PrintPlayerMessage(player, "0xff0000Failed ---------- 0xaaaaaa"+name+" [-]")
    else:
        Armagetronad.PrintPlayerMessage(player, "0x00ff00Succeed --------- 0xaaaaaa"+name+" [-]")

## @brief List all available extensions.
def listExt(acl, player):
    Armagetronad.PrintPlayerMessage("Available extensions: ")
    Armagetronad.PrintPlayerMessage(", ".join(extensions.getExtensions()))

Commands.add_help_group("extensions", "Extension management tools")
Commands.register_commands(loadExt, unloadExt, listExt, group="extensions")