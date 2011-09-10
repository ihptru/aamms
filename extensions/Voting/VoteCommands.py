import Poll, Messages, Armagetronad, Player, AccessLevel, Mode, LadderLogHandlers

## @brief Vote for a poll
# @details Adds the player to the list of yes voters
# @param acl The accesslevel of the player
# @param player The name of the player
def yes(acl, player):
    if not Poll.current_poll:
        Armagetronad.PrintPlayerMessage(player, Messages.NoActiveVote)
        return
    try:
        Poll.current_poll.SetPlayerVote(player, True)
        Armagetronad.PrintMessage(Messages.PlayerVotedYes.format(player=Player.players[player].name, target=Poll.current_poll.target) )
    except RuntimeError:
        Armagetronad.PrintPlayerMessage(player, Messages.PlayerAlreadyVoted)

## @brief Vote against a poll
# @details Adds the player to the list of no voters
# @param acl The accesslevel of the player
# @param player The name of the player
def no(acl, player):
    if not Poll.current_poll:
        Armagetronad.PrintPlayerMessage(player, Messages.NoActiveVote)
        return
    try:
        Poll.current_poll.SetPlayerVote(player, False)
        Armagetronad.PrintMessage(Messages.PlayerVotedNo.format(player=Player.players[player].name, target=Poll.current_poll.target) )
    except RuntimeError:
        Armagetronad.PrintPlayerMessage(player, Messages.PlayerAlreadyVoted)

## @brief Cancel a vote.
# @details Cancel the current vote if a vote is active.
# @param acl The accesslevel of the player
# @param player The name of the player
def cancel(acl, player):
    if Poll.current_poll:
        Armagetronad.PrintMessage(Messages.VoteCancelled.format(target=Poll.current_poll.target) )
        Poll.Cancel()  

## @brief Activates a mode.
# @details This is the /mode command
# @param player The player who executed this command
# @param gmode The mode which to activate.
# @param type Optional How does the mode get activated? Could be set or vote. Set isn't avaliable for normal players.
# @param when Optional When gets the mode activated? Only affects if type is set. Could be now, roundend or matchend.
def mode(acl, player, gmode, type="vote", when="now"):
    smode=""
    mode=None
    for key, m in Mode.modes.items():
        if m.short_name.lower()==gmode.lower() or m.getEscapedName==gmode.lower():
            mode=key
            smode=m.short_name.lower()
    if mode not in Mode.modes:
        Armagetronad.PrintPlayerMessage(player, Messages.ModeNotExist.format(mode=gmode))
        return
    if(type=="vote"):
        if Poll.current_poll != None:
            Armagetronad.PrintPlayerMessage(player, Messages.VoteAlreadyActive)
            return
        Poll.Add(Mode.modes[mode].short_name, Mode.modes[mode].activate)
        Poll.current_poll.SetPlayerVote(player, True)
        Armagetronad.PrintMessage(Messages.VoteAdded.format(target=smode, player=Player.players[player].name) )
        return
    elif type=="set":
        if when=="now" and AccessLevel.isAllowed("mode_set_now", acl):
            Mode.modes[mode].activate(True)
        elif when=="roundend" and AccessLevel.isAllowed("mode_set_roundend", acl):
            Armagetronad.PrintMessage("0x00ffffMode will change to {0} after this round. ".format(smode) )
            LadderLogHandlers.atRoundend.append(Mode.modes[mode].activate)
        elif when=="matchend" and AccessLevel.isAllowed("mode_set_matchend", acl):
            Armagetronad.PrintMessage("0x00ffffNext match's gamemode changed to {0}.".format(smode) )
            LadderLogHandlers.atMatchend.append(Mode.modes[mode].activate)
        else:
            pass
    else:
        pass