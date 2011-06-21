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
			time.sleep(0.05)
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
	p.terminate()
	p.wait()
# SETTINGS ##############################################
userdatadir="./server/data"
userconfigdir="./server/config"

# COMMAND LINE OPTIONS ##################################
parser=OptionParser()
#parser.add_option("-v", "--vardir", dest="vardir", default=None, help="Path to the var directory (server)")
parser.add_option("-d", "--datadir", dest="datadir", default=None, help="Path to the data directory (server)")
parser.add_option("-c", "--configdir", dest="configdir", default=None, help="Path to the config directory (server)")
parser.add_option("-e", "--executable", dest="server", default=None, help="Path of the server executable")
options, args=parser.parse_args()
options.vardir="server/var"
optionsdict=dict()
save_options=["vardir","configdir","server","datadir"]

# START #################################################
os.chdir(os.path.dirname(sys.argv[0]) )
if not os.path.exists("run"):
	os.mkdir("run")
os.chdir("run")

# Read and write config files
if os.path.exists("config.conf"):
	optionsdict2=yaml.load(open("config.conf","r") )
	for key,value in optionsdict2.items():
		try:
			if getattr(options, key)==None:
				setattr(options, key, value)
		except:
			pass
for save_option in save_options:
	optionsdict[save_option]=getattr(options, save_option)
yaml.dump(optionsdict, open("config.conf","w"), default_flow_style=False )

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
p=subprocess.Popen([options.server]+args, stdin=subprocess.PIPE, stdout=open("server.log","w"), stderr=subprocess.STDOUT )
atexit.register(exit)
sys.stdout=OutputToProcess()
sys.stdin=WatchFile(open(os.path.join(options.vardir,"ladderlog.txt") ) )
sys.stdin.skipUnreadLines()
sys.stderr=sys.__stdout__
import parser
while True:
	try:
		sys.stderr.write("[START] Starting script.\n")
		sys.stderr.write("[START] Press ctrl+c to exit.\n")
		sys.stderr.flush()	
		imp.reload(parser)
		parser.main()
	except KeyboardInterrupt:
		break
	except Exception as e:
		sys.stderr.write("Script crashed: "+e.__class__.__name__+" ("+str(e.args[0])[1:-1]+")\n")
		traceback.print_exc(file=sys.stderr)
		sys.stderr.flush()
		parser.exit(False)
		sys.stderr.write("Restarting ... \n")
		continue
	break
