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
import threading
import select

# GLOBAL VARIABLES ######################################
p=None

# CLASSES ###############################################
class OutputToProcess(io.TextIOWrapper):
	def __init__(self):
		pass
	def write(self, x):
		p.stdin.write(x.encode())
		p.stdin.flush()
	def flush(self):
		pass # File not buffered, ignore that.

# FUNCTIONS #############################################
def handleStdinInput(stdin):
	cur_text=""
	while(True):
		#select.select(sys.stdin, [], [])
		i=stdin.read(1)
		if i.decode().strip()=='':
			time.sleep(1)
			continue
		elif i=='\n':
			print(cur_text)
			sys.stderr.write("Got command: "+cur_text+"\n")
			sys.stderr.flush()
			cur_text=""
		else:
			sys.stderr.write("Got command: "+i.decode()+"\n")
			cur_text=cur_text+i.decode()

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
if not os.path.exists(userconfigdir):
	os.makedirs(userconfigdir)
if not os.path.exists(userdatadir):
	os.makedirs(userdatadir)
args=["--vardir",options.vardir, "--datadir",options.datadir, "--configdir",options.configdir,
      "--userdatadir",userdatadir, "--userconfigdir",userconfigdir]
p=subprocess.Popen([options.server]+args, stdin=subprocess.PIPE)
sys.stdout=OutputToProcess()
sys.stdin.read(1)
stdinThread=threading.Thread(handleStdinInput, args=(sys.stdin,))
stdinThread.start()
time.sleep(30)
while True:
	try:	
		sys.stderr.write("------ Starting script. Press ctrl+c to exit.\n")
		import parser
	except KeyboardInterrupt:
		break
	except Exception as e:
		sys.stderr.write("[SCRIPT] Script crashed: "+e.__class__.__name__+" ("+str(e.args)[1:-1]+")")
		parser.exit(False)
		sys.stderr.write("[SCRIPT] Restarting ... ")
		continue
	break
if stdinThread.is_alive:
	stdinThread.terminate()
	stdinThread.join()
