import glob
import imp
import sys

loadedExtensions=[]

def getExtensions():
    for i in glob.glob(__path__[0]+"/*/__init__.py"):
        i=i[:-(len("/__init__.py"))]
        print(i)
def loadExtensions():
    global loadedExtensions
    for i in getExtensions():
        print("[EXTENSION] Loading "+i+" ... ", end="")
        try:
            loadedExtensions+=imp.load_module(i, imp.find_module("extensions."+i))
        except ImportError:
            print("Not found.")
        except:
            print("Error")
        else:
            print("Ok")