import glob
import imp
import sys
import Global
import os.path
import LadderLogHandlers, Commands
import tools
__save_vars=["loadedExtensions"]

loadedExtensions=[]

def getExtensions():
    root=os.path.dirname(os.path.abspath(__file__))
    extensions=[]
    for i in glob.glob(root+"/*/__init__.py"):
        i=i[len(root)+1:-(len("/__init__.py"))]
        extensions+=[i]
    return extensions

def unloadExtension(name):
    name=[x for x in getExtensions() if x.lower()==name.lower()]
    if not len(name):
        return True
    name=name[0]
    global loadedExtensions
    module=[i for i in loadedExtensions if i.__name__==name]
    if len(module)!=1:
        return False
    module=module[0]
    loadedExtensions.remove(module)
    tools.delete_modules_from_dir(os.path.join("extensions", name))
    LadderLogHandlers.unregister_package(module.__name__)
    Commands.unregister_package(module.__name__)
    sys.stderr.write("[EXTENSION] Unloaded extension "+module.__name__+"\n")

def loadExtension(name, skip_dependency_check=False):
    global loadedExtensions
    sys.path.append(__path__)
    name=[i for i in getExtensions() if i.lower()==name.lower()]
    if len(name)<1:
        raise RuntimeError("Trying to load Extension "+name+", but it doesn't exists.")
    name=name[0]
    if name in [i.__name__ for i in loadedExtensions]:
        return True
    if os.path.exists(__path__[0]+"/"+name+"/config.py"):
        config=imp.new_module("extensions/"+name+"/config")
        loadedExtNames=[i.__name__ for i in loadedExtensions]
        if hasattr(config, "deps"):
            missing_deps=[i for i in config.deps if i not in loadedExtNames]
            if len(missing_deps) and not skip_dependency_check:
                return missing_deps
    sys.stderr.write("[EXTENSION] Loading "+name+" ... ")
    sys.stderr.flush()
    try:
        imp.acquire_lock()
        loadedExtensions+=[imp.load_module(name, *imp.find_module("extensions/"+name))]
        imp.release_lock()
    except BaseException as b: #@UnusedVariable
        if Global.debug:
            raise b
        sys.stderr.write("Error\n")
        return True
    else:
        sys.stderr.write("Ok\n")
    sys.stderr.flush()
    return False

def loadExtensions():
    global loadedExtensions
    sys.path.append(__path__)
    for i in getExtensions():
        missing_deps=loadExtension(i) #@UnusedVariable

def __reload__(loadedExtensions__old):
    for ext in loadedExtensions__old:
        loadExtension(ext.__name__)
