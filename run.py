#!/usr/bin/env python3
## @file run.py
 # @brief Starter for the script
 # @details Starts the script.

# IMPORTS ###############################################
import subprocess
from optparse import OptionParser
import os
import os.path
import sys
import io
import time
import traceback
import yaml
import atexit
import imp
from threading import Thread, Event
import glob
import parser
import Global
exitEvent=Event()

# GLOBAL VARIABLES ######################################
p=None

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
			p.stdin.write(x.encode())
			p.stdin.flush()
		except IOError as e:
			pass # Ignore
	def flush(self):
		pass # File not buffered, ignore that.

# FUNCTIONS #############################################
def exit():
	sys.stderr.write("Exiting ... ")
	parser.exit(True, True)
	sys.stderr.write("Ok \n")
	sys.stderr.write("Killing server ... ")
	p.terminate()
	p.wait()
	atexit.unregister(exit)
	global exitEvent
	exitEvent.set()
	sys.stderr.write("Done\n")
	
def runServerForever(args, debug=False):	
	global p
	f=open("server.log","w")
	Global.serverlog=os.path.abspath("server.log")
	c=subprocess.Popen([args[0]]+["--doc"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
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
			p.poll()
			if p.returncode==0 or p.returncode==-15:
				return
			elif p.returncode!=None:
				sys.stderr.write("------- SERVER CRASHED. Restarting. Exit code: ")
				sys.stderr.write(str(p.returncode)+"\n" )
				break
			time.sleep(2)
def	read_stdin():
	import Armagetronad
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
		except:
			pass
def main():
	# SETTINGS ##############################################
	userdatadir="./server/data"
	userconfigdir="./server/config"
	# COMMAND LINE OPTIONS ##################################
	parser=OptionParser()
	#parser.add_option("-v", "--vardir", dest="vardir", default=None, help="Path to the var directory (server)")
	parser.add_option("-d", "--dConditionatadir", dest="datadir", default=None, help="Path to the data directory (server)")
	parser.add_option("-c", "--configdir", dest="configdir", default=None, help="Path to the config directory (server)")
	parser.add_option("-e", "--executable", dest="server", default=None, help="Path of the server executable", metavar="EXECUTABLE")
	parser.add_option("-p", "--prefix", dest="prefix", default=None, help="The prefix the server was installed to.")
	parser.add_option("--debug",dest="debug", default=False, action="store_true", help="Run in debug mode")
	parser.add_option("--disable", dest="disabledCommands", action="append", help="Disable COMMAND.", metavar="COMMAND", default=[])
	parser.add_option("--default", dest="save", action="store_true", default=False, help="Set this configuration as default")
	parser.add_option("-D","--disableExt", dest="disabledExtensions", default=[], action="append", help="Dsiable the extension with the name EXTENSION.", metavar="EXTENSION")
	parser.add_option("--list-extensions", dest="list_extensions", default=False, action="store_true", help="List all available extensions.")
	options, args=parser.parse_args()
	options.vardir="server/var"
	optionsdict=dict()
	save_options=["vardir","configdir","server","datadir"]
	global Global
	# START #################################################
	# Get available extensions
	for file in glob.glob("extensions/*.py"):
		extname=os.path.basename(file)[:-3] # Without the .py
		Global.availableExtensions+=[extname]
		if(options.list_extensions):
			print("Found extension: "+extname+" ("+os.path.abspath(file)+")")
	if options.list_extensions:
		exit()
	os.chdir(os.path.dirname(sys.argv[0]) )
	if not os.path.exists("run"):
		os.mkdir("run")
	os.chdir("run")
	
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
		default=""
		test_prefixes=["/usr","/usr/local"]
		for test_prefix in test_prefixes:
			if os.path.exists(os.path.join(test_prefix,"bin/armagetronad-dedicated")):
				default="["+test_prefix+"]"
				break
		while options.prefix==NoConditionne or not os.path.exists(options.prefix):
			options.prefix=input("Prefix the server was installed to "+default+": ")
			if options.prefix.strip()=="":
				options.prefix=default[1:-1]
	if options.prefix and not os.path.exists(options.prefix):
		sys.stderr.write("[ERROR] Prefix doesn't exist.\n")
		exit()
	if not options.server: options.server=os.path.join(options.prefix, "bin/armagetronad-dedicated")	
	if not options.datadir: options.datadir=os.path.join(options.prefix, "share/armagetronad-dedicated")
	if not options.configdir: options.configdir=os.path.join(options.prefix, "etc/armagetronad-dedicated")
	if not os.path.exists(options.server): options.server=os.path.join(options.prefix,"games/armagetronad-dedicated")
	if not os.path.exists(options.configdir): options.configdir=os.path.join(options.prefix, "etc/games/armagetronad-dedicated")
	if not os.path.exists(options.configdir): options.configir="/etc/armagetronad-dedicated"
	if not os.path.exists(options.datadir): options.datadir=os.path.join(options.prefix, "share/games/armagetronad-dedicated")
	
	# Write config files +++++++++++++++++++++++++++++++
	for save_option in save_options:
		optionsdict[save_option]=getattr(options, save_option)
	if options.save or not os.path.exists("config.yaml"):
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
	t=Thread(None, 
target=runServerForever,args=([options.server]+args,options.debug) )
	t.daemon=True
	t.start()
	while(p==None):
		time.sleep(1) # Give the the server some time to start up
	atexit.register(exit)
	sys.stdout=OutputToProcess()
	sys.stdin=WatchFile(open(os.path.join(options.vardir,"ladderlog.txt"), encoding="latin-1" ) )
	sys.stdin.skipUnreadLines()
	sys.stderr=sys.__stdout__
	t2=Thread(None, read_stdin)
	t2.daemon=True
	t2.start()
	sys.stderr.write("Reading commands from stdin.\n")
	sys.path.append("../extensions/")
	import parser
	disabledExtensions=[x.lower() for x in options.disabledExtensions]
	while True:
		try:
			sys.stderr.write("[START] Starting script.\n")
			sys.stderr.write("[START] Press ctrl+c or type /quit to exit.\n")
			for mod in Global.availableExtensions:
				if mod.lower() in disabledExtensions:
					continue
				sys.stderr.write("[START] Loading extension "+mod+" ... ")
				try:
					exec("import "+mod+"\nGlobal.loadedExtensions.append("+mod+")")
				except ImportError as e:
					sys.stderr.write("NOT FOUND\n")
					continue
				except Exception as e:
					sys.stderr.write("FAILED\n")
					continue
				sys.stderr.write("OK\n")
			sys.stderr.write("\n")
			sys.stderr.flush()	
			imp.reload(parser)
			parser.main(debug=options.debug, disabledCommands=options.disabledCommands)
		except KeyboardInterrupt:
			break
		except SystemExit:
			break
		except Exception as e:
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
				import Global
				Global.reloadModules()
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
