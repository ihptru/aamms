#!/usr/bin/python3
## @file Messages.py
# @brief Game messages
# @details This file contains game messages

## @brief The color code for user messages
# @details Color code for all messages sent to a specific player.
PlayerColorCode="0xddffdd"

## @brief Command not found message
# @details This message is printed if the player tries to execute an invalid command
# @param command The command the player wanted to execute.
CommandNotFound="Sorry, command /{command} doesn't exist. Maybe you can try /info."

## @brief Access denied message
# @details This message is printed if the player isn't allowed to execute the command
# @param command The command the player wanted to execute
NotAllowed="You're not allowed to use the command /{command}. "

## @brief Player not found message
# @details This message is printed if the player doesn't exist in player list (bug)..
PlayerNotExist="Sorry, the script has a bug. You don't exist in the script's player list. \n"\
                "Maybe leave the server, then come back and try again. This bug has been reported."

## @brief Teleport message
# @details This message is printed when a player teleports himself with /tele command.
# @param player The name of the player who teleported.
# @param x The x coordinate to which the player teleported.
# @param y The y coordinate to which the player teleported.
PlayerSelfTeleport="0xff0000{player} 0xff0088teleported himself to (0xff0000{x}0xff0088|0xff0000{y}0xff0088)"
PlayerTeleported="0xff0000{player} 0xff0088got teleported to (0xff0000{x}0xff0088|0xff0000{y}0xff0088) by 0xff0000{by}"

## @brief Feature not implemented message
# @details This message is printed when a feature is currently not available, but in develop.
# @param feature The name of the feature
FeatureNotImplemented="{feature} is currently not supported, but it's coming soon! :)"

## @brief Mode not exists message
# @details This message is printed when a mode doesn't exist.
# @param mode The name of the mode
ModeNotExist="Mode {mode} doesn't exist! Look at /info modes for a list of all available modes."

## @brief Vote is in progress message
# @details This message is printed when a vote is active.
# @param target The target of the active vote
# @param expire How much rounds does this vote still stay alive?
PollInProgress="0xff8844Poll for 0xffff00{target} 0xff8844in progress. Use /yes or /no to vote! This vote expires in {expire} rounds"

PollInProgressCenter="0xff8800Poll in progress! Vote!"

## @brief Vote added message
# @details This message is displayed when a new vote was added.
# @param target The target of the vote which was added
# @param player The player who added the vote.
PollAdded="0x00ff00Poll for 0xffff00{target} 0x00ff00submitted by 0x00ff88{player}. Type /yes or /no to vote!"

## @brief Vote cancelled message
# @details This message is printed when an admin cancelled a vote.
# @param target The target of the cancelled vote.
PollCancelled="0xff2200Poll for 0xffff00{target} 0xff2200got cancelled by an administrator."

## @brief Vote successed message
# @details This message is printed when a vote successed.
# @param target The target of the vote which successed.
PollSuccessed="0x00ffffPoll for 0xffff00{target} 0x00ffffaccepted!"

## @brief Vote failed message
# @details This message is printed when a vote failed.
# @param target The target of the vote which failed.
PollFailed="0x00ffffPoll for 0xffff00{target} 0x00fffffailed!"

## @brief Player voted for a vote message
# @details This message is displayed when a player used the /yes command
# @param player The name of the player who voted.
# @param target The target of the vote for which the player voted.
PlayerVotedYes="0x00ff88{player} 0x99ff99voted for 0xffff00{target}."

## @brief Player voted against a vote message
# @details This message is displayed when a player used the /no command
# @param player The name of the player who voted.
# @param target The target of the vote for which the player voted.
PlayerVotedNo="0x00ff88{player} 0x99ff99voted against 0xffff00{target}."

## @brief Player has already voted message.
# @details This message is printed when a player tries to use the /yes or /no commands
#          but has already voted.
PlayerAlreadyVoted="0xff0033You have already voted!"

## @brief No vote active message.
# @details This message is printed when a player tries to use the /yes or /no commands, but
#          there isn't any active vote at the time.
NoActivePoll="There's no poll in progress!"

## @brief Access level changed message.
# @details This message is printed when /acl was successfully called.
# @param command The command of which the access level has changed.
# @param access The access level to which the required access level has changed.
AccessLevelChanged="0x00ff00The needed access level for {command} has changed to {access}."

## @brief Already a vote active message
# @details This message is printed when a player tries to create a vote, but there is already one active.
PollAlreadyActive="0xff4400There is already a poll in progress! Try again when the current poll finished."

## @brief Wrong state message.
# @details This message is printed when a player tries to use a command in the wrong state.
# @param command The command name.
WrongState="0xff0000/{command} cannot be used in this state."

## @brief Disabled command message.
# @param This message is printed when a player tries to use a disabled command.
DisabledCommand="0xff0000This command has been disabled by an administrator."

## @brief This is the Message that is printed when a player got respawned by the script.
PlayerRespawned="0x0066ff{player}0x00ff44 has been respawned. {msg}"
PlayerDied="0x0066ff{player}0x00ff44 is dead!"

LastLifeMsg="0xff0000Last respawn!"
OneLifeMsg="0x88ff88One 0x00ff44respawn left!"
LivesMsg="0x88ff88{lives} 0x00ff44respawns left!"

## @brief About message displayed by /info about
About="""0x00ffff                  About
0x00ff00The name of the script that runs on this server is AAMMS.
0x0000ffIt was written just for fun and can still have bugs.
0xff0000You can find the code on 0xffff00github.com/buntu/aamms.
0xff0000H0x00ff00a0x0000ffv0xffff00e 0xff0000f0x00ff00u0x0000ffn0xff0088 !!!!
"""

## @brief Invalid info topic message
InfoTopicInvalid="0xff0000Error: There is no topic {topic}!"

SpecNotAllowed="0xff8800Spectators aren't allowed to vote!"

ModeMessage="0x00aaffNow playing: 0xff8800{mode}"

NextRoundMode="0xffff00{player} 0x00aaffchanged next round's mode to 0xffdd00{mode}."

NextMatchMode="0xffff00{player} 0x00aaffchanged next match's mode to 0xffdd00{mode}."

ModeChanged="0xffff00{player} 0x00aaffchanged the mode to 0xffdd00{mode}."

PollTimedOut="0xffff00The poll about {target} timed out."

ModeAlreadyPlaying="0xff0000You are already playing this mode!"

ModeLocked="0xff0000Mode got locked by an adminsitrator."

LivesChanged="0xffff00{player} 0x00aaffchanged the number of respawns to 0xffdd00{new_lives}."
