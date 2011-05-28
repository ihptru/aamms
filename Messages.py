#!/usr/bin/python3
## @file Messages.py
 # @brief Game messages
 # @details This file contains game messages

## @brief The color code for user messages
 # @details Color code for all messages sent to a specific player.
PlayerColorCode="0xbbbbbb"

## @brief Command not found message
 # @details This message is printed if the player tries to execute an invalid command
 # @param command The command the player wanted to execute.
CommandNotFound="Sorry, command /{command} doesn't exist. Maybe you can try /help."

## @brief Access denied message
 # @details This message is printed if the player isn't allowed to execute the command
 # @param command The command the player wanted to execute
NotAllowed="You're not allowed to use the command /{command}. Go away!"

## @brief Player not found message
 # @details This message is printed if the player doesn't exist in player list (bug)..
PlayerNotExist=("Sorry, the script has a bug. You don't exist in the script's player list. \n"
                "Maybe leave the server, then come back and try again. This bug has been reported.")

## @brief Teleport message
 # @details This message is printed when a player teleports himself with /tele command.
 # @param player The name of the player who teleported.
 # @param x The x coordinate to which the player teleported.
 # @param y The y coordinate to which the player teleported.
PlayerTeleport=("0xff0088Player {player} teleported himself to ({x}|{y})")

## @brief Feature not implemented message
 # @details This message is printed when a feature is currently not avaliable, but still in develop.
 # @param feature The name of the feature
FeatureNotAvaliable=("{feature} is currently not supported, but it's coming soon! :)")

## @brief Mode not exists message
 # @details This message is printed when a mode doesn't exist.
 # @param mode The name of the mode
ModeNotExist=("{mode} doesn't exist! Look at /help modelist for a list of all avaliable modes.")
