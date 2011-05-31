## @file Vote.py
 # @package Vote
 # @brief Classes and functions for votes.
 # @details This file contains classes and functions needed for votes.

import logging
import Event
import Armagetronad
import Player
import Messages

## @brief The logging object
 # @details The logging object used for log messages by this module.
 # @note To enable or disable logging for this module use \link Vote.enableLogging\endlink
log=logging.getLogger("VoteModule")
log.addHandler(logging.NullHandler() )

## @brief The EventGroup
 # @details EventGroup used by this module.
 #          Events definied by this module:
 #             Vote created: triggered when a new vote was created.
 #             Vote successed: triggered when a vote successed. (After a call to \link Vote.Vote.CheckResult()\endlink )
 #             Vote failed: triggered when a vote failed. (After a call to \link Vote.Vote.CheckResult()\endlink )
 #             Vote cancelled: triggered by \link Vote.Cancel()\endlink .
 #          Handlers for Events triggered by this module don't have any arguments.'
events=Event.EventGroup("VoteEvents")
events.addEvent(Event.Event("Vote created") )
events.addEvent(Event.Event("Vote successed") )
events.addEvent(Event.Event("Vote failed") )
events.addEvent(Event.Event("Vote cancelled") )

## @brief The current vote
 # @details None or an instance of the current vote.
current_vote=None

## @brief Can spectators vote?
 # @details If set to True, votes of spectators are ignored.
spec_allowed=False

## @brief When should a vote expire? (Default value)
 # @details Default number of rounds for which a vote stays alive.
defaultStayAlive=5

## @brief Adds a new vote.
 # @details Adds a vote with the given name and set it as current_vote.
 # @exception RuntimeError Raised if there is already a vote. (current_vote not None)
 # @param target_human The human readable target of the vote (What is the vote about? ). Used for displaying.
 # @param target_machine The target of the vote (What is the vote about? ). Could be used to check what to do when the vote successed.
def Add(target_human, target_machine):
	global current_vote
	if current_vote != None:
		raise RuntimeError("Already a vote active", 1)
	current_vote=Vote(target_human, target_machine)
	events.triggerEvent("Vote created")

## @brief Cancels the current vote.
 # @details Sets current_vote to None and prints a message.
def Cancel():
	global current_vote
	current_vote=None


## @brief The vote class
 # @details This class is used to manage a vote.
class Vote:
	## @property __players_voted_yes
	 # @brief What players voted for the vote?
	 # @details Set of the players who voted for the vote.

	## @property __players_voted_no
	 # @brief What players voted against the vote?
	 # @details Set of the players who voted against the vote.

	## @property target
	 # @brief The human readable target of the vote.
	 # @details Target: What is the vote about? Used by the script to display to the user.

	## @property action
	 # @brief Function that is called when the vote success.
	 # @details Function could be every object that has a __call__ method(is callable)

	## @property aliveRounds
	 # @brief When does the vote expire?
	 # @details Number of round for which the vote stays "alive".

	## @brief Init function (Constructor)
	 # @details Inits a new vote.
	 # @param target Human readable target of the vote.
	 # @param mtarget Action. None if no function should be called.
	def __init__(self, target, action=None):
		global defaultStayAlive
		self.target=target
		self.action=action
		self.aliveRounds=defaultStayAlive
		self.__players_voted_no=[]
		self.__players_voted_yes=[]

	## @brief Checks the result of the vote.
	 # @details Checks if the vote successed or failed and triggers "Vote successed"
	 #          or "Vote failed" event.
	 # @param not_voted What happens with players who didn't vote?
	 #                  Could be "yes", "no" or "dont_count".
	 #                  If "yes"|"no" is given, players who didn't vote are counted
	 #                  as if the had voted "yes"|"no". Otherwise, they aren't counted.
	 #                  Default is "dont_count".
	 # @param not_voted_spec Same as not_voted, but only for spectators. If not given
	 #                       or set to None, not_voted is used.
	 # @param min_needed How much precent yes votes are at least needed that the vote gets
	 #                   accepted? Default 51.
	 # @exception ValueError Raised if not_voted ot not_voted_spec aren't on of
	 #                      "yes", "no" or "dont_count".
	def CheckResult(self, not_voted="dont_count", not_voted_spec=None, min_needed=51):
		if not_voted not in {"dont_count","yes","no"}:
			raise ValueError("Invalid value of argument not_voted")
		if not_voted_spec == None:
			not_voted_spec=not_voted
		elif not_voted_spec not in {"dont_count","yes","no"}:
			raise ValueError("Invalid value of argument not_voted")
		if min_needed>100:
			min_needed=100
		elif min_needed<0:
			min_needed=0
		yes_count=len(self.__players_voted_yes)
		no_count=len(self.__players_voted_no)
		voted_players=self.__players_voted_yes + self.__players_voted_no
		bots=Player.getBots()
		cur_mode=None
		for player in Player.players:
			if player in bots or player in voted_players:
				continue
			if Player.players[player].getTeam()==None: # Player is spectating
				cur_mode=not_voted_spec
			else:
				cur_mode=not_voted
			if cur_mode == "yes":
				yes_count=yes_count+1
			elif cur_mode == "no":
				no_count=no_count+1
			else:
				pass
		precent_yes=yes_count/(yes_count+no_count)*100
		if precent_yes >= min_needed:
			events.triggerEvent("Vote successed")
			log.info("Vote for {0} successed.".format(self.target) )
			Armagetronad.PrintMessage(Messages.VoteSuccessed.format(target=self.target) )
			self.action()
		else:
			events.triggerEvent("Vote failed")
			log.info("Vote for {0} failed.")
			Armagetronad.PrintMessage(Messages.VoteFailed.format(target=self.target) )
		global current_vote
		current_vote=None

	## @brief Sets what a player voted.
	 # @details Checks if the player is a spectator. If yes and
	 #          spec_allowed is set to False, return immendiately. Otherwise,
	 #          add the player to the list of players who voted for|agains the vote.
	 # @param name The ladder name of the player who voted.
	 # @param vote True if the player voted for the voted, False otherwise.
	 # @exception RuntimeError Raised if the player has already voted.
	 # @exception ValueError Raised if the player doesn't exist.'
	def SetPlayerVote(self, player, vote):
		if player not in Player.players:
			raise RuntimeError("Player doesn't exist", 2)
		if player in (self.__players_voted_yes + self.__players_voted_no):
			raise RuntimeError("Player already voted", 1)
		if Player.players[player].getTeam()==None and not spec_allowed: #spec not allowed and player is spectator
			return
		if vote:
			self.__players_voted_yes.append(player)
		else:
			self.__players_voted_no.appemd(player)


## @brief Enables logging
 # @details This function enables logging for this module.
 # @param h The handler used for logging
 # @param f The formatter used for logging
 # @param level The logging level
def enableLogging(level=logging.DEBUG, h=None,f=None):
	log.setLevel(level)
	if not h:
		h=logging.StreamHandler()
		h.setLevel(level)
	if not f:
		f=logging.Formatter("[%(name)s] (%(asctime)s) %(levelname)s: %(message)s")
	h.setFormatter(f)
	log.addHandler(h)
