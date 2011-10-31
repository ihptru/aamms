import os.path, sys
import imp
import inspect

sub_mods=dict()

def remove_duplicates(l):
    ret=set()
    map(ret.update, l)
    return ret

def get_package(x):
    if type(x)==str:
        mod_name=x
    else:
        mod_name=x.__module__
    if len(mod_name.split("."))>1:
        return mod_name.split(".")[-2]
    else:
        return mod_name
    
def is_in_root(file_name, root=None, root_rel=True):
    if root==None:
        root=os.path.dirname(os.path.abspath(__file__))
    elif root_rel==True:
        root=os.path.join(os.path.dirname(os.path.abspath(__file__)), root)
    file_name=os.path.dirname(os.path.abspath(file_name))
    return os.path.commonprefix([root, file_name])==root

def is_script_component(mod, *args, **kwargs):
    try:
        if type(mod)==str:
            mod=sys.modules[mod]
        if (mod.__name__.startswith("__") and mod.__name__.endswith("__")) or mod.__name__=="__main__": 
            return False
        return is_in_root(os.path.abspath(mod.__file__), *args, **kwargs)
    except ValueError:
        return False
    except AttributeError:
        return False

def reload_none_modules():
    for mod in [i for i in sys.modules if sys.modules[i]==None]:
        sys.stderr.write("[Module None] "+mod+"\n")
        del(sys.modules[mod])
        imp.load_module(mod, *imp.find_module(mod))

def delete_module(mod):
    global sub_mods
    if type(mod)==str:
        mod=sys.modules[mod]
    if mod.__name__=="__main__":
        return
    if not is_script_component(mod):
        sys.stderr.write("[WARNING] Tried to reload non script module. Aborted."+"\n")
        return
    if mod.__name__==__name__:
        return
    sys.stderr.write("[Delete Module] "+mod.__name__+"\n")
    if hasattr(mod, "__del__"):
        mod.__del__()
    for attr in filter(lambda x : not (x.startswith("__") and x.endswith("__")), dir(mod)):
        if inspect.ismodule(getattr(mod, attr)) and not is_script_component(getattr(mod, attr)):
            continue
        elif inspect.ismodule(getattr(mod, attr)):
            delattr(mod, attr)
    del sys.modules[mod.__name__]
    for i in sys.modules:
        if is_script_component(i) or i == "__main__":
            if hasattr(sys.modules[i],mod.__name__):
                delattr(sys.modules[i],mod.__name__)
                if sys.modules[i].__name__ not in sub_mods:
                    sub_mods[sys.modules[i].__name__]=[]
                sub_mods[sys.modules[i].__name__].append(mod.__name__)
    #reload_none_modules()

def delete_script_modules():
    return delete_modules_from_dir()

def delete_modules_from_dir(directory=None, dir_rel=True):
    need_delete=filter(lambda mod: is_script_component(mod, root=directory, root_rel=dir_rel), sys.modules)
    need_delete=list(need_delete)
    vars=dict()
    global sub_mods
    for mod in need_delete:
            if hasattr(sys.modules[mod], "__save_vars"):
                vars[mod]=dict()
                for var in sys.modules[mod].__save_vars:
                    if hasattr(sys.modules[mod], var):
                        vars[mod][var]=getattr(sys.modules[mod], var)
            if mod not in sub_mods:
                sub_mods[mod]=[]
            for attr in dir(sys.modules[mod]):
                x=getattr(sys.modules[mod], attr)
                if inspect.ismodule(x):
                    sub_mods[mod].append(x.__name__)
            delete_module(mod)
    return need_delete, vars

def reload_script_modules():
    import Global
    Global.handleLadderLog=False
    main_mods=list()
    import __main__
    for x in dir(__main__):
        if x=="__builtins__": continue
        if inspect.ismodule(getattr(__main__, x)) and is_script_component(x):
            main_mods+=[x]
    modules, vars=delete_script_modules()
    import extensions
    for mod in modules:
            if get_package(mod) in extensions.getExtensions():
                continue
            try:
                sys.stderr.write("[ReImport] "+mod+" ... ")
                imp.load_module(mod, *imp.find_module(mod))
                if mod in main_mods:
                    setattr(__main__, mod, sys.modules[mod])
            except ImportError:
                sys.stderr.write("Failed.\n")
                continue
            sys.stderr.write("OK\n")
    for mod in modules:
        if mod in sys.modules:
            if mod in sub_mods:
                for sub_mod in sub_mods[mod]:
                    if sub_mod not in extensions.loadedExtensions:
                        setattr(sys.modules[mod], sub_mod, sys.modules[sub_mod])
                    else:
                        setattr(sys.modules[mod], sub_mod, extensions.loadedExtensions[mod])
        if mod in vars:
            if hasattr(sys.modules[mod], "__reload__"):
                vars_new=dict()
                for var in vars[mod]:
                    vars_new[var+"__old"]=vars[mod][var]
                sys.modules[mod].__reload__(**vars_new)
            else:
                for var in vars[mod]:
                    setattr(sys.modules[mod], var, vars[mod][var])
    for mod in main_mods:
            setattr(__main__,mod, sys.modules[mod])
    Global.handleLadderLog=True
