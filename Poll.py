## @file Poll.py
# @package Poll
# @brief Classes and functions for voting.
# @details This file contains classes and functions needed for votes.

import logging
import Armagetronad
import Player
import Messages

__save_vars=["log", "current_poll"]
## @brief The logging object
# @details The logging object used for log messages by this module.
# @note To enable or disable logging for this module use \link Poll.enableLogging\endlink
log=logging.getLogger("VoteModule")
log.addHandler(logging.NullHandler() )

## @brief The current poll
# @details None or an instance of the current Poll.
current_poll=None

## @brief Can spectators vote?
# @details If set to True, votes of spectators are ignored.
spec_allowed=False

## @brief When should a vote expire? (Default value)
# @details Default number of rounds for which a vote stays alive.
defaultStayAlive=3

## @brief Creates a Poll.
# @details Creates a Poll with the given name and set it as current_poll.
# @exception RuntimeError Raised if there is already a Poll. (current_poll not None)
# @param target_human The human readable target of the Poll (What is the Poll about? ). Used for displaying.
# @param action Function that is executed when the Poll succeed.
# @param force Cancel current Poll if a Poll is already active? 

def Add(target_human, action,player, force=False):
    global current_poll
    if player not in Player.players:
        raise RuntimeError("Player doesn't exist.")
    if Player.players[player].getTeam()==None and not spec_allowed:
        raise RuntimeError("Spectators are not allowed to vote",3)
    if current_poll != None:
        if not force:
            raise RuntimeError("Already a vote active", 1)
        else:
            Cancel()
    current_poll=Poll(target_human, action)        
    log.info("New Poll  "+target_human+" created.")

## @brief Cancels the current Poll.
# @details Sets current_poll to None and prints a message.
def Cancel():
    global current_poll
    target=current_poll.target
    current_poll=None
    log.info("Poll cancelled.")
    Armagetronad.PrintMessage(Messages.PollCancelled.format(target=target))


## @brief The vote class
# @details This class is used to manage a Poll.
class Poll:
    ## @property __players_voted_yes
    # @brief What players voted for the Poll?
    # @details Set of the players who voted for the Poll.

    ## @property __players_voted_no
    # @brief What players voted against the Poll?
    # @details Set of the players who voted against the Poll.

    ## @property target
    # @brief The human readable target of the Poll.
    # @details Target: What is the Poll about? Used by the script to display to the user.

    ## @property action
    # @brief Function that is called when the Poll success.
    # @details Function could be every object that has a __call__ method(is callable)

    ## @property aliveRounds
    # @brief When does the Poll expire?
    # @details Number of round for which the Poll stays "alive".

    ## @brief Init function (Constructor)
    # @details Inits a new Poll.
    # @param target Human readable target of the Poll.
    # @param action Action. None if no function should be called.
    def __init__(self, target, action=None):
        global defaultStayAlive
        self.target=target
        self.action=action
        self.aliveRounds=defaultStayAlive
        self.__players_voted_no=[]
        self.__players_voted_yes=[]

    ## @brief Checks the result of the Poll.
    # @details Checks if the vote successed or failed.
    #          or "Poll failed" event.
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
    def CheckResult(self, not_voted="dont_count", not_voted_spec=None, min_needed=51, only_sure=False):
        if not_voted not in {"dont_count","yes","no"}:
            raise ValueError("Invalid value of argument not_voted")
        if not_voted_spec == None:
            not_voted_spec=not_voted
        elif not_voted_spec not in {"dont_count","yes","no"}:
            raise ValueError("Invalid value of argument not_voted_spec")
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
            if player in bots or Player.players[player].ip in voted_players:
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
        num_allowed=len(Player.players)-len(Player.getBots())
        if not spec_allowed:
            num_allowed=num_allowed-len([i for i in Player.players.values() if i.getTeam()==None])
        if yes_count+no_count==0 or num_allowed==0:
            percent_yes=0
            percent_no=0
        elif only_sure==False:
            percent_yes=yes_count/(yes_count+no_count)*100
            percent_no=100-percent_yes
        else:
            percent_yes=yes_count/num_allowed*100
            percent_no=no_count/num_allowed*100
        if num_allowed==1:
            percent_yes=100
            percent_no=0
        if percent_yes >= min_needed:
            log.info("Poll for {0} successed.".format(self.target) )
            Armagetronad.SendCommand("CENTER_MESSAGE "+Messages.PollSuccessed.format(target=self.target) )
            self.action()
        elif percent_no>(100-min_needed):
            log.info("Poll for {0} failed.".format(self.target) )
            Armagetronad.SendCommand("CENTER_MESSAGE "+Messages.PollFailed.format(target=self.target) )
        else:
            return False
        global current_poll
        current_poll=None
        return True

    ## @brief Sets what a player voted.
    # @details Checks if the player is a spectator. If yes and
    #          spec_allowed is set to False, return immediately. Otherwise,
    #          add the player to the list of players who voted for|against the Poll.
    # @param player The ladder name of the player who voted.
    # @param vote True if the player voted yes for the Poll, False otherwise.
    # @exception RuntimeError Raised if the player has already voted.
    # @exception ValueError Raised if the player doesn't exist.'
    def SetPlayerVote(self, player, vote):
        if player not in Player.players:
            raise RuntimeError("Player doesn't exist", 2)
        if Player.players[player].ip in (self.__players_voted_yes + self.__players_voted_no):
            raise RuntimeError("Player already voted", 1)
        if Player.players[player].getTeam()==None and not spec_allowed: #spec not allowed and player is spectator
            raise RuntimeError("Player not allowed to vote", 3)
        if vote:
            self.__players_voted_yes.append(Player.players[player].ip)
        else:
            self.__players_voted_no.append(Player.players[player].ip)
    
    def RemovePlayerVote(self, player):
        player=Player.players[player].ip
        try:
            del self.__players_voted_no[self.__players_voted_no.index(player)]
        except IndexError:
            del self.__players_voted_yes[self.__players_voted_yes.index(player)]


## @brief Enables logging
# @details This function enables logging for this module.
# @param h The handler used for logging
# @param f The formatter used for logging
# @param level The logging level
def enableLogging(level=logging.DEBUG, h=None,f=None):
    global log
    log.setLevel(level)
    if not h:
        h=logging.StreamHandler()
        h.setLevel(level)
    if not f:
        f=logging.Formatter("[%(name)s] (%(asctime)s) %(levelname)s: %(message)s")
    h.setFormatter(f)
    for handler in log.handlers:
        if type(handler)==type(h):
            log.removeHandler(handler)
    log.addHandler(h)
