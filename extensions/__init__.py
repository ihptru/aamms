import glob
import imp
import sys
import Global

loadedExtensions=[]

def getExtensions():
    extensions=[]
    for i in glob.glob(__path__[0]+"/*/__init__.py"):
        i=i[len(__path__[0])+1:-(len("/__init__.py"))]
        extensions+=[i]
    return extensions
def loadExtensions():
    global loadedExtensions
    sys.path.append(__path__)
    for i in getExtensions():
        sys.stderr.write("[EXTENSION] Loading "+i+" ... ")
        sys.stderr.flush()
        try:
            imp.acquire_lock()
            loadedExtensions+=[imp.load_module(i, *imp.find_module("extensions/"+i))]
            imp.release_lock()
        except ImportError as i:
            sys.stderr.write("Not found.\n")
            raise i
        except BaseException as b: #@UnusedVariable
            if Global.debug:
                raise b
            sys.stderr.write("Error\n")
        else:
            sys.stderr.write("Ok\n")
        sys.stderr.flush()
