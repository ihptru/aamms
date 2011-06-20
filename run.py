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
		p.stdin.write(x.encode())
		p.stdin.flush()
	def flush(self):
		pass # File not buffered, ignore that.

# SETTINGS ##############################################
userdatadir="./server/userdata"
userconfigdir="./server/config"

# COMMAND LINE OPTIONS ##################################
parser=OptionParser()
parser.add_option("-v", "--vardir", dest="vardir", default="/var/games/armagetronad/", help="Path to the var directory (server)")
parser.add_option("-d", "--datadir", dest="datadir", default="/usr/share/games/armagetronad/", help="Path to the data directory (server)")
parser.add_option("-c", "--configdir", dest="configdir", default="/etc/armagetronad-dedicated/", help="Path to the config directory (server)")
parser.add_option("-e", "--executable", dest="server", default="/usr/games/armagetronad-dedicated", help="Path of the server executable")
options, args=parser.parse_args()

# START #################################################
os.chdir(os.path.dirname(sys.argv[0]) )
if not os.path.exists("run"):
	os.mkdir("run")
os.chdir("run")
if not os.path.exists(userconfigdir):
	os.makedirs(userconfigdir)
if not os.path.exists(userdatadir):
	os.makedirs(userdatadir)
args=["--vardir",options.vardir, "--datadir",options.datadir, "--configdir",options.configdir,
      "--userdatadir",userdatadir, "--userconfigdir",userconfigdir]
p=subprocess.Popen([options.server]+args, stdin=subprocess.PIPE)
sys.stdout=OutputToProcess()
sys.stdin=WatchFile(open(os.path.join(options.vardir,"ladderlog.txt") ) )
sys.stdin.skipUnreadLines()
time.sleep(30)
while True:
	try:	
		sys.stderr.write("------ Starting script. Press ctrl+c to exit.\n")
		sys.stderr.flush()
		import parser
	except KeyboardInterrupt:
		break
	except Exception as e:
		sys.stderr.write("[SCRIPT] Script crashed: "+e.__class__.__name__+" ("+str(e.args)[1:-1]+")\n")
		traceback.print_exc(file=sys.stderr)
		sys.stderr.flush()
		parser.exit(False)
		sys.stderr.write("[SCRIPT] Restarting ... ")
		continue
	break
p.terminate()
