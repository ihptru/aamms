import glob
import imp
import sys
import Global
import os.path
import LadderLogHandlers, Commands

loadedExtensions=[]

def getExtensions():
    extensions=[]
    for i in glob.glob(__path__[0]+"/*/__init__.py"):
        i=i[len(__path__[0])+1:-(len("/__init__.py"))]
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
    for i in dir(module):
        if not (i.startswith("__") and i.endswith("__")):
            i=getattr(module, i)
            if type(i)==type(glob):
                if os.path.dirname(i.__file__) == __path__[0]+"/"+name:
                    del(sys.modules[i.__name__])
                    delattr(module, i.__name__)
    del(sys.modules[module.__name__])
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
    if os.path.exists(__path__[0]+"/"+name+"/config.py"):
        config=imp.new_module("extensions/"+name+"/config")
        loadedExtNames=[i.__name__ for i in loadedExtensions]
        missing_deps=[i for i in getExtensions() if i not in loadedExtNames]
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
        missing_deps=loadExtension(i)
