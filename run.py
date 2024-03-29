#!/usr/bin/env python3
## @file run.py
# @brief Starter for the script
# @details Starts the script.

# IMPORTS ###############################################
import subprocess
from optparse import OptionParser
import os.path
import sys
import io
import time
import traceback
import yaml
import atexit
from threading import Thread, Event
import parser
import Global
import extensions
import Armagetronad
exitEvent=Event()
__save_vars=["p"]

# GLOBAL VARIABLES ######################################
p=None


class FlushFile(io.TextIOWrapper):
    def __init__(self, file):
        self.f=file
    def write(self, x):
        self.f.write(x)
        self.f.flush()
    def writelines(self, lines):
        for l in lines:
            self.write(l+"\n")
    def writeable(self):
        return True
    def close(self):
        pass
    def flush(self):
        pass
    
# CLASSES ###############################################
class WatchFile():
    def __init__(self, f):
        self.f=f
        self.last_read=""
    def read(self, b=0):
        while(True):
            r=self.f.read()
            if r!='':
                return r
            time.sleep(0.07)
    def skipUnreadLines(self):
        self.f.seek(0, io.SEEK_END)
    def readline(self):
        r=self.last_read
        while(r.find("\n")==-1):
            r=self.read()
        self.last_read=r.split("\n",1)[1]
        return r.split("\n")[0]

class OutputToProcess(io.TextIOWrapper):
    def __init__(self):
        pass
    def write(self, x):
        try:
            p.stdin.write(x.encode("latin-1"))
            if Global.debug:
                f=open("debug.log", "a+")
                f.write(x)
                f.close()
            p.stdin.flush()
        except IOError:
            pass # Ignore
    def flush(self):
        pass # File not buffered, ignore that.

# FUNCTIONS #############################################
def exit():
    sys.stderr.write("Exiting ... ")
    parser.exit(True, True)
    sys.stderr.write("Ok \n")
    sys.stderr.write("Exiting server ... ")
    global p
    if p!=None:
        print("QUIT")
        p.wait()
    atexit.unregister(exit)
    global exitEvent
    exitEvent.set()
    sys.stderr.write("Done\n")
    
def runServerForever(args, debug=False):    
    global p
    f=open("server.log","w")
    Global.serverlog=os.path.abspath("server.log")
    c=subprocess.Popen([args[0]]+["--doc"]+args[1:], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    doctext=c.communicate()[0].decode()
    c.wait()
    doctext=doctext[doctext.find("Available console commands/config file settings")+len("Available console commands/config file settings"):]
    for line in doctext.split("\n"):
        line=line.strip()
        if len(line)==0 or line[0] not in "QWERTZUIOPASDFGHJKLYXCVBNM":    
            continue
        command=line[:line.find(" ")]
        Global.supportedCommands.append(command)
    while(True):
        p=subprocess.Popen(args, stdin=subprocess.PIPE, stdout=f, stderr=subprocess.STDOUT )
        if debug:
            sys.stderr.write("DEBUG: Executing "+" ".join(args)+"\n")
        while(True):
            if p==None:
                return
            p.poll()
            if p.returncode==0 or p.returncode==-15:
                return
            elif p.returncode!=None:
                sys.stderr.write("------- SERVER CRASHED. Restarting. Exit code: ")
                sys.stderr.write(str(p.returncode)+"\n" )
                break
            time.sleep(2)
def read_stdin():
    while(True):
        try:
            line=sys.__stdin__.readline().strip()
            if line.startswith("/"):
                command=line[1:]
                if command=="quit":
                    parser.exit(True)
                    exit()
            else:
                Armagetronad.SendCommand(line)
                sys.stderr.write("Command sent to server.\n")
        except Exception as e:
            print(e)
def main():
    # SETTINGS ##############################################
    userdatadir="./server/data"
    userconfigdir="./server/config"
    # COMMAND LINE OPTIONS ##################################
    oparser=OptionParser()
    #parser.add_option("-v", "--vardir", dest="vardir", default=None, help="Path to the var directory (server)")
    oparser.add_option("-d", "--datadir", dest="datadir", default=None, help="Path to the data directory (server)")
    oparser.add_option("-c", "--configdir", dest="configdir", default=None, help="Path to the config directory (server)")
    oparser.add_option("-e", "--executable", dest="server", default=None, help="Path of the server executable", metavar="EXECUTABLE")
    oparser.add_option("-p", "--prefix", dest="prefix", default=None, help="The prefix the server was installed to.")
    oparser.add_option("-n", "--name", dest="servername", default=None, help="The name of the server", metavar="SERVERNAME")
    oparser.add_option("--debug",dest="debug", default=False, action="store_true", help="Run in debug mode")
    oparser.add_option("--disable", dest="disabledCommands", action="append", help="Disable COMMAND.", metavar="COMMAND", default=[])
    oparser.add_option("--default", dest="save", action="store_true", default=False, help="Set this configuration as default")
    oparser.add_option("-D","--disableExt", dest="disabledExtensions", default=[], action="append", help="Dsiable the extension with the name EXTENSION.", metavar="EXTENSION")
    oparser.add_option("--list-extensions", dest="list_extensions", default=False, action="store_true", help="List all available extensions.")
    options=oparser.parse_args()[0]
    options.vardir="server/var"
    optionsdict=dict()
    save_options=["vardir","configdir","server","datadir", "servername", "prefix"]

    # START #################################################
    # Get available extensions
    if options.list_extensions:
        print("Extensions:")
        print("\n".join(extensions.getExtensions()))
    os.chdir(os.path.dirname(sys.argv[0]) )
    if not os.path.exists("run"):
        os.mkdir("run")
    os.chdir("run")
    asked=False
    # Read prefix
    def read_prefix():
        global asked
        default=""
        test_prefixes=["/usr","/usr/local"]
        for test_prefix in test_prefixes:
            if os.path.exists(os.path.join(test_prefix,"bin/armagetronad-dedicated")):
                default="["+test_prefix+"]"
                break
        while options.prefix==None or not os.path.exists(options.prefix):
            options.prefix=input("Prefix the server was installed to "+default+": ")
            if options.prefix.strip()=="":
                options.prefix=default[1:-1]
            if not os.path.exists(options.prefix):
                print("Error: Prefix doesn't exist.")
    # Read config files ++++++++++++++++++++++++++++++++
    if os.path.exists("config.yaml"):
        optionsdict2=yaml.load(open("config.yaml","r") )
        for key,value in optionsdict2.items():
            try:
                if getattr(options, key)==None:
                    setattr(options, key, value)
            except:
                pass
    else:
        read_prefix()
        asked=True
    if ( not options.prefix or not os.path.exists(options.prefix)) and not all((not os.path.exists(i) for i in (options.datadir, options.configdir, options.server))):
        read_prefix()
        asked=True
        options.server=None
        options.datadir=None
        options.configdir=None     
    if not options.server: options.server=os.path.join(options.prefix, "bin/armagetronad-dedicated")    
    if not options.datadir: options.datadir=os.path.join(options.prefix, "share/armagetronad-dedicated")
    if not options.configdir: options.configdir=os.path.join(options.prefix, "etc/armagetronad-dedicated")
    if not os.path.exists(options.server): options.server=os.path.join(options.prefix,"games/armagetronad-dedicated")
    if not os.path.exists(options.configdir): options.configdir=os.path.join(options.prefix, "etc/games/armagetronad-dedicated")
    if not os.path.exists(options.configdir): options.configir="/etc/armagetronad-dedicated"
    if not os.path.exists(options.datadir): options.datadir=os.path.join(options.prefix, "share/games/armagetronad-dedicated")
    
    Global.datadir=options.datadir
    Global.configdir=options.configdir
    Global.debug=options.debug
    
    if options.servername==None:
        options.servername=input("Please enter a name for your server: ")
        asked=True
    # Write config files +++++++++++++++++++++++++++++++
    for save_option in save_options:
        optionsdict[save_option]=getattr(options, save_option)
    if options.save or not os.path.exists("config.yaml") or asked:
        yaml.dump(optionsdict, open("config.yaml","w"), default_flow_style=False )
    
    if not os.path.exists(userconfigdir):
        os.makedirs(userconfigdir)
    if not os.path.exists(userdatadir):
        os.makedirs(userdatadir)
    if not os.path.exists(options.vardir):
        os.makedirs(options.vardir)
    open(os.path.join(options.vardir,"ladderlog.txt"),"w" ).close()
    print("[START] Starting server. Serverlog can be found in run/server.log")
    args=["--vardir",options.vardir, "--datadir",options.datadir, "--configdir",options.configdir,
          "--userdatadir",userdatadir, "--userconfigdir",userconfigdir]
    print("[START] Executable: "+options.server)
    t=Thread(None, target=runServerForever,args=([options.server]+args,options.debug) )
    t.daemon=True
    t.start()
    while(p==None):
        time.sleep(1) # Give the the server some time to start up
    atexit.register(exit)
    sys.stdout=OutputToProcess()
    if os.path.exists("debug.log"):
        os.remove("debug.log")
    sys.stdin=WatchFile(open(os.path.join(options.vardir,"ladderlog.txt"), encoding="latin-1" ) )
    sys.stdin.skipUnreadLines()
    sys.stderr=FlushFile(sys.__stdout__)
    t2=Thread(None, read_stdin)
    t2.daemon=True
    t2.start()
    sys.stderr.write("Reading commands from stdin.\n")
    Global.server_name=options.servername
    extensions.loadExtensions()
    sys.stderr.write("[START] Starting script.\n")
    sys.stderr.write("[START] Press ctrl+c or type /quit to exit.\n")
    sys.stderr.write("\n")
    sys.stderr.flush()    
    reloaded=False
    while True:
        try:
            parser.main(debug=options.debug, disabledCommands=options.disabledCommands, reloaded=reloaded)
        except KeyboardInterrupt:
            break
        except SystemExit:
            break
        except Global.ReloadException:
            import tools
            tools.reload_script_modules()
            reloaded=True
            continue
        except Exception:
            sys.stderr.write("#####################################################################\n")
            sys.stderr.write("################## SCRIPT CRASHED ###################################\n")
            sys.stderr.write("#####################################################################\n")
            traceback.print_exc(file=sys.stderr)
            sys.stderr.write("#####################################################################\n")
            sys.stderr.flush()
            parser.exit(False, quiet=True)        
            try:
                sys.stderr.write("Restarting in 3 seconds ... \n")        
                sys.stderr.write("\n")
                time.sleep(3)
                reloaded=True
            except KeyboardInterrupt:
                break
            except:
                continue
            continue
        break
    exit()
if __name__=="__main__":
    t=Thread(None, target=main)
    t.daemon=True
    t.start()
    try:
        exitEvent.wait()
    except:
        exit()
