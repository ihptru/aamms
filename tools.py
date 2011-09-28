import os.path, sys
import imp

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
        if mod.__name__.startswith("__") and mod.__name__.endswith("__"):
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
    if type(mod)==str:
        mod=sys.modules[mod]
    if not is_script_component(mod):
        sys.stderr.write("[WARNING] Tried to reload non script module. Aborted."+"\n")
        sys.stderr.write(mod.__name__+"\n")
        return
    sys.stderr.write("[Delete Module] "+mod.__name__+"\n")
    if hasattr(mod, "__del__"):
        mod.__del__()
    del sys.modules[mod.__name__]
    for i in sys.modules:
        if is_script_component(i) or i == "__main__":
            if hasattr(sys.modules[i],mod.__name__):
                delattr(sys.modules[i],mod.__name__)
    #reload_none_modules()

def delete_script_modules():
    return delete_modules_from_dir()

def delete_modules_from_dir(dir=None, dir_rel=True):
    need_delete=filter(lambda mod: is_script_component(mod, root=dir, root_rel=dir_rel), sys.modules)
    need_delete=list(need_delete)
    vars=dict()
    for mod in need_delete:
            if hasattr(sys.modules[mod], "__save_vars"):
                vars[mod]=dict()
                for var in sys.modules[mod].__save_vars:
                    if hasattr(sys.modules[mod], var):
                        vars[mod][var]=getattr(sys.modules[mod], var)
            delete_module(mod)
    return need_delete, vars

def reload_script_modules():
    import __main__
    main_modules=[]
    for attr in dir(__main__):
        if attr in sys.modules and is_script_component(attr):
            main_modules.append(attr)
    modules, vars=delete_script_modules()
    import extensions
    for mod in modules:
            if get_package(mod) in extensions.getExtensions():
                continue
            try:
                sys.stderr.write("[ReImport] "+mod+" ... ")
                imp.load_module(mod, *imp.find_module(mod))
            except ImportError:
                sys.stderr.write("Failed.\n")
                continue
            sys.stderr.write("OK\n")
            if mod in vars:
                if hasattr(sys.modules[mod], "__reload__"):
                    sys.modules[mod].__reload__(**vars[mod])
                else:
                    for var in vars[mod]:
                        setattr(sys.modules[mod], var, vars[mod][var])
    for main_module in main_modules:
        setattr(__main__, main_module, sys.modules[main_module])