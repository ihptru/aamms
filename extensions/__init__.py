import glob
import imp
import sys

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
        print("[EXTENSION] Loading "+i+" ... ", end="")
        try:
            imp.acquire_lock()
            loadedExtensions+=[imp.load_module(i, *imp.find_module("extensions/"+i))]
            imp.release_lock()
        except ImportError:
            print("Not found.")
        #except BaseException as b:
        #    print("Error")
        else:
            print("Ok")