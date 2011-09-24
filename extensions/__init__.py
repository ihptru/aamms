import glob
import imp
import sys
import Global
import os.path

loadedExtensions=[]

def getExtensions():
    extensions=[]
    for i in glob.glob(__path__[0]+"/*/__init__.py"):
        i=i[len(__path__[0])+1:-(len("/__init__.py"))]
        extensions+=[i]
    return extensions

def unloadExtension(name):
    global loadedExtensions
    module=[i for i in loadedExtensions if i.__name__==name]
    if len(module)!=1:
        return False
    module=module[0]
    loadedExtensions.remove(module)
    del(sys.modules[module.__name__])
    sys.stderr.write("[EXTENSION] Unloaded extension "+mod.__name__)

def loadExtension(name, skip_dependency_check=False):
    global loadedExtensions
    sys.path.append(__path__)
    if name not in getExtensions():
        raise RuntimeError("Trying to load Extension "+name+", but it doesn't exists.")
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
    else:
        sys.stderr.write("Ok\n")
    sys.stderr.flush()
    return False

def loadExtensions():
    global loadedExtensions
    sys.path.append(__path__)
    for i in getExtensions():
        missing_deps=loadExtension(i)
