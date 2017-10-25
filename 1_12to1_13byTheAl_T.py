#! /usr/bin/env python
# coding=utf-8

# Made by TheAl_T
# planetminecraft.com/member/theal_t

# Block data value -> block state database by: Onnowhere youtube.com/onnowhere2

"""
Syntax explanation:
    First character:
        < - required token
        [ - optional token
    Second character:
        @ - player name or entity selector
        ( - one of the literal values separated by '|'
        * - one or more tokens (must be last)
        0 - a number
        ~ - a number prefixed (or not) by '~'
        % - a number suffixed (or not) by 'L'
        = - Block data value or block state or -1 or *
        { - NBT tag
        : - raw JSON
        . - whatever
"""

import re, json, sys, codecs, os, shutil
from time import time as getTime


class Dummy:
    pass
Globals = Dummy()
Globals.commandCounter = 0
Globals.commentedOut = False
Globals.posArgs = ("x", "y", "z", "dx", "dy", "dz", "r", "rm", "c")
Globals.statTags = ("AffectedBlocks", "AffectedEntities", "AffectedItems", "QueryResult", "SuccessCount")
Globals.selectorArgs = ("x", "y", "z", "dx", "dy", "dz", "type", "lm", "l", "m", "team", "score", "name", "tag", "nbt", "rm", "r", "rxm", "rx", "rym", "ry", "c")
Globals.selectorArgsNew = (('x', 'x', 'x'), ('y', 'y', 'y'), ('z', 'z', 'z'), ("dx", "dx", "dx"), ("dy", "dy", "dy"), ("dz", "dz", "dz"), ("type", "type", "type"), ("level", 'lm', "l"), ("gamemode", 'm', 'm'), ("team", "team", "team"), ("score", "score", "score"), ("name", "name", "name"), ("tag", "tag", "tag"), ("nbt", "nbt", "nbt"), ("distance", 'rm', "r"), ('x_rotation', "rxm", "rx"), ('y_rotation', "rym", "ry"), ("limit", 'c', 'c'), ("sort", "sort", "sort"))
Globals.gamerules = ('announceAdvancements', 'commandBlockOutput', 'disableElytraMovementCheck', 'doDaylightCycle', 'doEntityDrops', 'doFireTick', 'doLimitedCrafting', 'doMobLoot', 'doMobSpawning', 'doTileDrops', 'doWeatherCycle', 'drowningdamage', 'falldamage', 'firedamage', 'gameLoopFunction', 'keepInventory', 'logAdminCommands', 'maxCommandChainLength', 'maxEntityCramming', 'mobGriefing', 'naturalRegeneration', 'pvp', 'randomTickSpeed', 'reducedDebugInfo', 'sendCommandFeedback', 'showDeathMessages', 'spawnRadius', 'spectatorsGenerateChunks')
Globals.commands = ["advancement", "ban", "ban-ip", "blockdata", "clear", "clone", "debug", "defaultgamemode", "deop", "difficulty", "effect", "enchant", "entitydata", "execute", "fill", "function", "gamemode", "gamerule", "give", "help", "?", "kick", "kill", "list", "locate", "me", "msg", "op", "pardon", "pardon-ip", "particle", "playsound", "publish", "recipe", "reload", "replaceitem", "save-all", "save-off", "save-on", "say", "scoreboard", "seed", "setblock", "setidletimeout", "setworldspawn", "spawnpoint", "spreadplayers", "stats", "stop", "stopsound", "summon", "teleport", "tell", "tellraw", "testfor", "testforblock", "testforblocks", "time", "title", "toggledownfall", "tp", "trigger", "w", "weather", "whitelist", "worldborder", "xp"]
Globals.blockStates = {"brewing_stand":{0:"has_bottle_0=false,has_bottle_1=false,has_bottle_2=false",1:"has_bottle_0=true,has_bottle_1=false,has_bottle_2=false",2:"has_bottle_0=false,has_bottle_1=true,has_bottle_2=false",3:"has_bottle_0=true,has_bottle_1=true,has_bottle_2=false",4:"has_bottle_0=false,has_bottle_1=false,has_bottle_2=true",5:"has_bottle_0=true,has_bottle_1=false,has_bottle_2=true",6:"has_bottle_0=false,has_bottle_1=true,has_bottle_2=true",7:"has_bottle_0=true,has_bottle_1=true,has_bottle_2=true",8:"has_bottle_0=false,has_bottle_1=false,has_bottle_2=false",9:"has_bottle_0=true,has_bottle_1=false,has_bottle_2=false",10:"has_bottle_0=false,has_bottle_1=true,has_bottle_2=false",11:"has_bottle_0=true,has_bottle_1=true,has_bottle_2=false",12:"has_bottle_0=false,has_bottle_1=false,has_bottle_2=true",13:"has_bottle_0=true,has_bottle_1=false,has_bottle_2=true",14:"has_bottle_0=false,has_bottle_1=true,has_bottle_2=true",15:"has_bottle_0=true,has_bottle_1=true,has_bottle_2=true"},"dark_oak_door":{0:"facing=east,half=lower,hinge=left,open=false,powered=false",1:"facing=south,half=lower,hinge=left,open=false,powered=false",2:"facing=west,half=lower,hinge=left,open=false,powered=false",3:"facing=north,half=lower,hinge=left,open=false,powered=false",4:"facing=east,half=lower,hinge=left,open=true,powered=false",5:"facing=south,half=lower,hinge=left,open=true,powered=false",6:"facing=west,half=lower,hinge=left,open=true,powered=false",7:"facing=north,half=lower,hinge=left,open=true,powered=false",8:"half=upper,hinge=left,powered=false",9:"half=upper,hinge=right,powered=false",10:"half=upper,hinge=left,powered=true",11:"half=upper,hinge=right,powered=true",12:"half=upper,hinge=left,powered=false",13:"half=upper,hinge=right,powered=false",14:"half=upper,hinge=left,powered=true",15:"half=upper,hinge=right,powered=true"},"acacia_door":{0:"facing=east,half=lower,hinge=left,open=false,powered=false",1:"facing=south,half=lower,hinge=left,open=false,powered=false",2:"facing=west,half=lower,hinge=left,open=false,powered=false",3:"facing=north,half=lower,hinge=left,open=false,powered=false",4:"facing=east,half=lower,hinge=left,open=true,powered=false",5:"facing=south,half=lower,hinge=left,open=true,powered=false",6:"facing=west,half=lower,hinge=left,open=true,powered=false",7:"facing=north,half=lower,hinge=left,open=true,powered=false",8:"half=upper,hinge=left,powered=false",9:"half=upper,hinge=right,powered=false",10:"half=upper,hinge=left,powered=true",11:"half=upper,hinge=right,powered=true",12:"half=upper,hinge=left,powered=false",13:"half=upper,hinge=right,powered=false",14:"half=upper,hinge=left,powered=true",15:"half=upper,hinge=right,powered=true"},"jungle_door":{0:"facing=east,half=lower,hinge=left,open=false,powered=false",1:"facing=south,half=lower,hinge=left,open=false,powered=false",2:"facing=west,half=lower,hinge=left,open=false,powered=false",3:"facing=north,half=lower,hinge=left,open=false,powered=false",4:"facing=east,half=lower,hinge=left,open=true,powered=false",5:"facing=south,half=lower,hinge=left,open=true,powered=false",6:"facing=west,half=lower,hinge=left,open=true,powered=false",7:"facing=north,half=lower,hinge=left,open=true,powered=false",8:"half=upper,hinge=left,powered=false",9:"half=upper,hinge=right,powered=false",10:"half=upper,hinge=left,powered=true",11:"half=upper,hinge=right,powered=true",12:"half=upper,hinge=left,powered=false",13:"half=upper,hinge=right,powered=false",14:"half=upper,hinge=left,powered=true",15:"half=upper,hinge=right,powered=true"},"spruce_door":{0:"facing=east,half=lower,hinge=left,open=false,powered=false",1:"facing=south,half=lower,hinge=left,open=false,powered=false",2:"facing=west,half=lower,hinge=left,open=false,powered=false",3:"facing=north,half=lower,hinge=left,open=false,powered=false",4:"facing=east,half=lower,hinge=left,open=true,powered=false",5:"facing=south,half=lower,hinge=left,open=true,powered=false",6:"facing=west,half=lower,hinge=left,open=true,powered=false",7:"facing=north,half=lower,hinge=left,open=true,powered=false",8:"half=upper,hinge=left,powered=false",9:"half=upper,hinge=right,powered=false",10:"half=upper,hinge=left,powered=true",11:"half=upper,hinge=right,powered=true",12:"half=upper,hinge=left,powered=false",13:"half=upper,hinge=right,powered=false",14:"half=upper,hinge=left,powered=true",15:"half=upper,hinge=right,powered=true"},"wooden_door":{0:"facing=east,half=lower,hinge=left,open=false,powered=false",1:"facing=south,half=lower,hinge=left,open=false,powered=false",2:"facing=west,half=lower,hinge=left,open=false,powered=false",3:"facing=north,half=lower,hinge=left,open=false,powered=false",4:"facing=east,half=lower,hinge=left,open=true,powered=false",5:"facing=south,half=lower,hinge=left,open=true,powered=false",6:"facing=west,half=lower,hinge=left,open=true,powered=false",7:"facing=north,half=lower,hinge=left,open=true,powered=false",8:"half=upper,hinge=left,powered=false",9:"half=upper,hinge=right,powered=false",10:"half=upper,hinge=left,powered=true",11:"half=upper,hinge=right,powered=true",12:"half=upper,hinge=left,powered=false",13:"half=upper,hinge=right,powered=false",14:"half=upper,hinge=left,powered=true",15:"half=upper,hinge=right,powered=true"},"birch_door":{0:"facing=east,half=lower,hinge=left,open=false,powered=false",1:"facing=south,half=lower,hinge=left,open=false,powered=false",2:"facing=west,half=lower,hinge=left,open=false,powered=false",3:"facing=north,half=lower,hinge=left,open=false,powered=false",4:"facing=east,half=lower,hinge=left,open=true,powered=false",5:"facing=south,half=lower,hinge=left,open=true,powered=false",6:"facing=west,half=lower,hinge=left,open=true,powered=false",7:"facing=north,half=lower,hinge=left,open=true,powered=false",8:"half=upper,hinge=left,powered=false",9:"half=upper,hinge=right,powered=false",10:"half=upper,hinge=left,powered=true",11:"half=upper,hinge=right,powered=true",12:"half=upper,hinge=left,powered=false",13:"half=upper,hinge=right,powered=false",14:"half=upper,hinge=left,powered=true",15:"half=upper,hinge=right,powered=true"},"iron_door":{0:"facing=east,half=lower,hinge=left,open=false,powered=false",1:"facing=south,half=lower,hinge=left,open=false,powered=false",2:"facing=west,half=lower,hinge=left,open=false,powered=false",3:"facing=north,half=lower,hinge=left,open=false,powered=false",4:"facing=east,half=lower,hinge=left,open=true,powered=false",5:"facing=south,half=lower,hinge=left,open=true,powered=false",6:"facing=west,half=lower,hinge=left,open=true,powered=false",7:"facing=north,half=lower,hinge=left,open=true,powered=false",8:"half=upper,hinge=left,powered=false",9:"half=upper,hinge=right,powered=false",10:"half=upper,hinge=left,powered=true",11:"half=upper,hinge=right,powered=true",12:"half=upper,hinge=left,powered=false",13:"half=upper,hinge=right,powered=false",14:"half=upper,hinge=left,powered=true",15:"half=upper,hinge=right,powered=true"},"leaves":{0:"check_decay=false,decayable=true,variant=oak",1:"check_decay=false,decayable=true,variant=spruce",2:"check_decay=false,decayable=true,variant=birch",3:"check_decay=false,decayable=true,variant=jungle",4:"check_decay=false,decayable=false,variant=oak",5:"check_decay=false,decayable=false,variant=spruce",6:"check_decay=false,decayable=false,variant=birch",7:"check_decay=false,decayable=false,variant=jungle",8:"check_decay=true,decayable=true,variant=oak",9:"check_decay=true,decayable=true,variant=spruce",10:"check_decay=true,decayable=true,variant=birch",11:"check_decay=true,decayable=true,variant=jungle",12:"check_decay=true,decayable=false,variant=oak",13:"check_decay=true,decayable=false,variant=spruce",14:"check_decay=true,decayable=false,variant=birch",15:"check_decay=true,decayable=false,variant=jungle"},"vine":{0:"east=false,north=false,south=false,west=false",1:"east=false,north=false,south=true,west=false",2:"east=false,north=false,south=true,west=true",3:"east=false,north=true,south=false,west=false",4:"east=false,north=true,south=true,west=false",5:"east=false,north=true,south=false,west=true",6:"east=false,north=true,south=true,west=true",7:"east=true,north=false,south=false,west=false",8:"east=true,north=false,south=false,west=false",9:"east=true,north=false,south=true,west=false",10:"east=true,north=false,south=false,west=true",11:"east=true,north=false,south=true,west=true",12:"east=true,north=true,south=false,west=false",13:"east=true,north=true,south=true,west=false",14:"east=true,north=true,south=false,west=true",15:"east=true,north=true,south=true,west=true"},"tripwire":{0:"attached=false,disarmed=false,powered=false",1:"attached=false,disarmed=false,powered=true",2:"attached=false,disarmed=false,powered=false",3:"attached=false,disarmed=false,powered=true",4:"attached=true,disarmed=false,powered=false",5:"attached=true,disarmed=false,powered=true",6:"attached=true,disarmed=false,powered=false",7:"attached=true,disarmed=false,powered=true",8:"attached=false,disarmed=true,powered=false",9:"attached=false,disarmed=true,powered=true",10:"attached=false,disarmed=true,powered=false",11:"attached=false,disarmed=true,powered=true",12:"attached=true,disarmed=true,powered=false",13:"attached=true,disarmed=true,powered=true",14:"attached=true,disarmed=true,powered=false",15:"attached=true,disarmed=true,powered=true"},"tripwire_hook":{0:"attached=false,facing=south,powered=false",1:"attached=false,facing=west,powered=false",2:"attached=false,facing=north,powered=false",3:"attached=false,facing=east,powered=false",4:"attached=true,facing=south,powered=false",5:"attached=true,facing=west,powered=false",6:"attached=true,facing=north,powered=false",7:"attached=true,facing=east,powered=false",8:"attached=false,facing=south,powered=true",9:"attached=false,facing=west,powered=true",10:"attached=false,facing=north,powered=true",11:"attached=false,facing=east,powered=true",12:"attached=true,facing=south,powered=true",13:"attached=true,facing=west,powered=true",14:"attached=true,facing=north,powered=true",15:"attached=true,facing=east,powered=true"},"unpowered_comparator":{0:"facing=south,mode=compare,powered=false",1:"facing=west,mode=compare,powered=false",2:"facing=north,mode=compare,powered=false",3:"facing=east,mode=compare,powered=false",4:"facing=south,mode=subtract,powered=false",5:"facing=west,mode=subtract,powered=false",6:"facing=north,mode=subtract,powered=false",7:"facing=east,mode=subtract,powered=false",8:"facing=south,mode=compare,powered=true",9:"facing=west,mode=compare,powered=true",10:"facing=north,mode=compare,powered=true",11:"facing=east,mode=compare,powered=true",12:"facing=south,mode=subtract,powered=true",13:"facing=west,mode=subtract,powered=true",14:"facing=north,mode=subtract,powered=true",15:"facing=east,mode=subtract,powered=true"},"powered_comparator":{0:"facing=south,mode=compare,powered=false",1:"facing=west,mode=compare,powered=false",2:"facing=north,mode=compare,powered=false",3:"facing=east,mode=compare,powered=false",4:"facing=south,mode=subtract,powered=false",5:"facing=west,mode=subtract,powered=false",6:"facing=north,mode=subtract,powered=false",7:"facing=east,mode=subtract,powered=false",8:"facing=south,mode=compare,powered=true",9:"facing=west,mode=compare,powered=true",10:"facing=north,mode=compare,powered=true",11:"facing=east,mode=compare,powered=true",12:"facing=south,mode=subtract,powered=true",13:"facing=west,mode=subtract,powered=true",14:"facing=north,mode=subtract,powered=true",15:"facing=east,mode=subtract,powered=true"},"dark_oak_fence_gate":{0:"facing=south,open=false,powered=false",1:"facing=west,open=false,powered=false",2:"facing=north,open=false,powered=false",3:"facing=east,open=false,powered=false",4:"facing=south,open=true,powered=false",5:"facing=west,open=true,powered=false",6:"facing=north,open=true,powered=false",7:"facing=east,open=true,powered=false",8:"facing=south,open=false,powered=true",9:"facing=west,open=false,powered=true",10:"facing=north,open=false,powered=true",11:"facing=east,open=false,powered=true",12:"facing=south,open=true,powered=true",13:"facing=west,open=true,powered=true",14:"facing=north,open=true,powered=true",15:"facing=east,open=true,powered=true"},"double_stone_slab2":{0:"seamless=false,variant=red_sandstone",1:"seamless=false,variant=red_sandstone",2:"seamless=false,variant=red_sandstone",3:"seamless=false,variant=red_sandstone",4:"seamless=false,variant=red_sandstone",5:"seamless=false,variant=red_sandstone",6:"seamless=false,variant=red_sandstone",7:"seamless=false,variant=red_sandstone",8:"seamless=true,variant=red_sandstone",9:"seamless=true,variant=red_sandstone",10:"seamless=true,variant=red_sandstone",11:"seamless=true,variant=red_sandstone",12:"seamless=true,variant=red_sandstone",13:"seamless=true,variant=red_sandstone",14:"seamless=true,variant=red_sandstone",15:"seamless=true,variant=red_sandstone"},"acacia_fence_gate":{0:"facing=south,open=false,powered=false",1:"facing=west,open=false,powered=false",2:"facing=north,open=false,powered=false",3:"facing=east,open=false,powered=false",4:"facing=south,open=true,powered=false",5:"facing=west,open=true,powered=false",6:"facing=north,open=true,powered=false",7:"facing=east,open=true,powered=false",8:"facing=south,open=false,powered=true",9:"facing=west,open=false,powered=true",10:"facing=north,open=false,powered=true",11:"facing=east,open=false,powered=true",12:"facing=south,open=true,powered=true",13:"facing=west,open=true,powered=true",14:"facing=north,open=true,powered=true",15:"facing=east,open=true,powered=true"},"jungle_fence_gate":{0:"facing=south,open=false,powered=false",1:"facing=west,open=false,powered=false",2:"facing=north,open=false,powered=false",3:"facing=east,open=false,powered=false",4:"facing=south,open=true,powered=false",5:"facing=west,open=true,powered=false",6:"facing=north,open=true,powered=false",7:"facing=east,open=true,powered=false",8:"facing=south,open=false,powered=true",9:"facing=west,open=false,powered=true",10:"facing=north,open=false,powered=true",11:"facing=east,open=false,powered=true",12:"facing=south,open=true,powered=true",13:"facing=west,open=true,powered=true",14:"facing=north,open=true,powered=true",15:"facing=east,open=true,powered=true"},"spruce_fence_gate":{0:"facing=south,open=false,powered=false",1:"facing=west,open=false,powered=false",2:"facing=north,open=false,powered=false",3:"facing=east,open=false,powered=false",4:"facing=south,open=true,powered=false",5:"facing=west,open=true,powered=false",6:"facing=north,open=true,powered=false",7:"facing=east,open=true,powered=false",8:"facing=south,open=false,powered=true",9:"facing=west,open=false,powered=true",10:"facing=north,open=false,powered=true",11:"facing=east,open=false,powered=true",12:"facing=south,open=true,powered=true",13:"facing=west,open=true,powered=true",14:"facing=north,open=true,powered=true",15:"facing=east,open=true,powered=true"},"birch_fence_gate":{0:"facing=south,open=false,powered=false",1:"facing=west,open=false,powered=false",2:"facing=north,open=false,powered=false",3:"facing=east,open=false,powered=false",4:"facing=south,open=true,powered=false",5:"facing=west,open=true,powered=false",6:"facing=north,open=true,powered=false",7:"facing=east,open=true,powered=false",8:"facing=south,open=false,powered=true",9:"facing=west,open=false,powered=true",10:"facing=north,open=false,powered=true",11:"facing=east,open=false,powered=true",12:"facing=south,open=true,powered=true",13:"facing=west,open=true,powered=true",14:"facing=north,open=true,powered=true",15:"facing=east,open=true,powered=true"},"fence_gate":{0:"facing=south,open=false,powered=false",1:"facing=west,open=false,powered=false",2:"facing=north,open=false,powered=false",3:"facing=east,open=false,powered=false",4:"facing=south,open=true,powered=false",5:"facing=west,open=true,powered=false",6:"facing=north,open=true,powered=false",7:"facing=east,open=true,powered=false",8:"facing=south,open=false,powered=true",9:"facing=west,open=false,powered=true",10:"facing=north,open=false,powered=true",11:"facing=east,open=false,powered=true",12:"facing=south,open=true,powered=true",13:"facing=west,open=true,powered=true",14:"facing=north,open=true,powered=true",15:"facing=east,open=true,powered=true"},"iron_trapdoor":{0:"facing=north,half=bottom,open=false",1:"facing=south,half=bottom,open=false",2:"facing=west,half=bottom,open=false",3:"facing=east,half=bottom,open=false",4:"facing=north,half=bottom,open=true",5:"facing=south,half=bottom,open=true",6:"facing=west,half=bottom,open=true",7:"facing=east,half=bottom,open=true",8:"facing=north,half=bottom,open=false",9:"facing=south,half=top,open=false",10:"facing=west,half=top,open=false",11:"facing=east,half=top,open=false",12:"facing=north,half=top,open=true",13:"facing=south,half=top,open=true",14:"facing=west,half=top,open=true",15:"facing=east,half=top,open=true"},"trapdoor":{0:"facing=north,half=bottom,open=false",1:"facing=south,half=bottom,open=false",2:"facing=west,half=bottom,open=false",3:"facing=east,half=bottom,open=false",4:"facing=north,half=bottom,open=true",5:"facing=south,half=bottom,open=true",6:"facing=west,half=bottom,open=true",7:"facing=east,half=bottom,open=true",8:"facing=north,half=bottom,open=false",9:"facing=south,half=top,open=false",10:"facing=west,half=top,open=false",11:"facing=east,half=top,open=false",12:"facing=north,half=top,open=true",13:"facing=south,half=top,open=true",14:"facing=west,half=top,open=true",15:"facing=east,half=top,open=true"},"double_plant":{0:"facing=north,half=lower,variant=sunflower",1:"facing=north,half=lower,variant=syringa",2:"facing=north,half=lower,variant=double_grass",3:"facing=north,half=lower,variant=double_fern",4:"facing=north,half=lower,variant=double_rose",5:"facing=north,half=lower,variant=paeonia",6:"facing=north,half=lower,variant=sunflower",7:"facing=north,half=lower,variant=sunflower",8:"facing=north,half=upper",9:"facing=north,half=upper",10:"facing=north,half=upper",11:"facing=north,half=upper",12:"facing=north,half=upper",13:"facing=north,half=upper",14:"facing=north,half=upper",15:"facing=north,half=upper"},"stone_slab2":{0:"half=bottom,variant=red_sandstone",1:"half=bottom,variant=red_sandstone",2:"half=bottom,variant=red_sandstone",3:"half=bottom,variant=red_sandstone",4:"half=bottom,variant=red_sandstone",5:"half=bottom,variant=red_sandstone",6:"half=bottom,variant=red_sandstone",7:"half=bottom,variant=red_sandstone",8:"half=top,variant=red_sandstone",9:"half=top,variant=red_sandstone",10:"half=top,variant=red_sandstone",11:"half=top,variant=red_sandstone",12:"half=top,variant=red_sandstone",13:"half=top,variant=red_sandstone",14:"half=top,variant=red_sandstone",15:"half=top,variant=red_sandstone"},"double_stone_slab":{0:"seamless=false,variant=stone",1:"seamless=false,variant=sandstone",2:"seamless=false,variant=wood_old",3:"seamless=false,variant=cobblestone",4:"seamless=false,variant=brick",5:"seamless=false,variant=stone_brick",6:"seamless=false,variant=nether_brick",7:"seamless=false,variant=quartz",8:"seamless=true,variant=stone",9:"seamless=true,variant=sandstone",10:"seamless=true,variant=wood_old",11:"seamless=true,variant=cobblestone",12:"seamless=true,variant=brick",13:"seamless=true,variant=stone_brick",14:"seamless=true,variant=nether_brick",15:"seamless=true,variant=quartz"},"repeating_command_block":{0:"conditional=false,facing=down",1:"conditional=false,facing=up",2:"conditional=false,facing=north",3:"conditional=false,facing=south",4:"conditional=false,facing=west",5:"conditional=false,facing=east",6:"conditional=false,facing=down",7:"conditional=false,facing=up",8:"conditional=true,facing=down",9:"conditional=true,facing=up",10:"conditional=true,facing=north",11:"conditional=true,facing=south",12:"conditional=true,facing=west",13:"conditional=true,facing=east",14:"conditional=true,facing=down",15:"conditional=true,facing=up"},"chain_command_block":{0:"conditional=false,facing=down",1:"conditional=false,facing=up",2:"conditional=false,facing=north",3:"conditional=false,facing=south",4:"conditional=false,facing=west",5:"conditional=false,facing=east",6:"conditional=false,facing=down",7:"conditional=false,facing=up",8:"conditional=true,facing=down",9:"conditional=true,facing=up",10:"conditional=true,facing=north",11:"conditional=true,facing=south",12:"conditional=true,facing=west",13:"conditional=true,facing=east",14:"conditional=true,facing=down",15:"conditional=true,facing=up"},"command_block":{0:"conditional=false,facing=down",1:"conditional=false,facing=up",2:"conditional=false,facing=north",3:"conditional=false,facing=south",4:"conditional=false,facing=west",5:"conditional=false,facing=east",6:"conditional=false,facing=down",7:"conditional=false,facing=up",8:"conditional=true,facing=down",9:"conditional=true,facing=up",10:"conditional=true,facing=north",11:"conditional=true,facing=south",12:"conditional=true,facing=west",13:"conditional=true,facing=east",14:"conditional=true,facing=down",15:"conditional=true,facing=up"},"bed":{0:"facing=south,part=foot",1:"facing=west,part=foot",2:"facing=north,part=foot",3:"facing=east,part=foot",4:"facing=south,part=foot",5:"facing=west,part=foot",6:"facing=north,part=foot",7:"facing=east,part=foot",8:"facing=south,occupied=false,part=head",9:"facing=west,occupied=false,part=head",10:"facing=north,occupied=false,part=head",11:"facing=east,occupied=false,part=head",12:"facing=south,occupied=true,part=head",13:"facing=west,occupied=true,part=head",14:"facing=north,occupied=true,part=head",15:"facing=east,occupied=true,part=head"},"stone_slab":{0:"half=bottom,variant=stone",1:"half=bottom,variant=sandstone",2:"half=bottom,variant=wood_old",3:"half=bottom,variant=cobblestone",4:"half=bottom,variant=brick",5:"half=bottom,variant=stone_brick",6:"half=bottom,variant=nether_brick",7:"half=bottom,variant=quartz",8:"half=top,variant=stone",9:"half=top,variant=sandstone",10:"half=top,variant=wood_old",11:"half=top,variant=cobblestone",12:"half=top,variant=brick",13:"half=top,variant=stone_brick",14:"half=top,variant=nether_brick",15:"half=top,variant=stone"},"purpur_slab":{0:"half=bottom,variant=default",1:"half=bottom,variant=default",2:"half=bottom,variant=default",3:"half=bottom,variant=default",4:"half=bottom,variant=default",5:"half=bottom,variant=default",6:"half=bottom,variant=default",7:"half=bottom,variant=default",8:"half=top,variant=default",9:"half=top,variant=default",10:"half=top,variant=default",11:"half=top,variant=default",12:"half=top,variant=default",13:"half=top,variant=default",14:"half=top,variant=default",15:"half=top,variant=default"},"lever":{0:"facing=down_x,powered=false",1:"facing=east,powered=false",2:"facing=west,powered=false",3:"facing=south,powered=false",4:"facing=north,powered=false",5:"facing=up_z,powered=false",6:"facing=up_x,powered=false",7:"facing=down_z,powered=false",8:"facing=down_x,powered=true",9:"facing=east,powered=true",10:"facing=west,powered=true",11:"facing=south,powered=true",12:"facing=north,powered=true",13:"facing=up_z,powered=true",14:"facing=up_x,powered=true",15:"facing=down_z,powered=true"},"wooden_button":{0:"facing=down,powered=false",1:"facing=east,powered=false",2:"facing=west,powered=false",3:"facing=south,powered=false",4:"facing=north,powered=false",5:"facing=up,powered=false",6:"facing=up,powered=false",7:"facing=up,powered=false",8:"facing=down,powered=true",9:"facing=east,powered=true",10:"facing=west,powered=true",11:"facing=south,powered=true",12:"facing=north,powered=true",13:"facing=up,powered=true",14:"facing=up,powered=true",15:"facing=up,powered=true"},"stone_button":{0:"facing=down,powered=false",1:"facing=east,powered=false",2:"facing=west,powered=false",3:"facing=south,powered=false",4:"facing=north,powered=false",5:"facing=up,powered=false",6:"facing=up,powered=false",7:"facing=up,powered=false",8:"facing=down,powered=true",9:"facing=east,powered=true",10:"facing=west,powered=true",11:"facing=south,powered=true",12:"facing=north,powered=true",13:"facing=up,powered=true",14:"facing=up,powered=true",15:"facing=up,powered=true"},"wooden_slab":{0:"half=bottom,variant=oak",1:"half=bottom,variant=spruce",2:"half=bottom,variant=birch",3:"half=bottom,variant=jungle",4:"half=bottom,variant=acacia",5:"half=bottom,variant=dark_oak",6:"half=bottom,variant=oak",7:"half=bottom,variant=oak",8:"half=top,variant=oak",9:"half=top,variant=spruce",10:"half=top,variant=birch",11:"half=top,variant=jungle",12:"half=top,variant=acacia",13:"half=top,variant=dark_oak",14:"half=top,variant=oak",15:"half=top,variant=oak"},"activator_rail":{0:"powered=false,shape=north_south",1:"powered=false,shape=east_west",2:"powered=false,shape=ascending_east",3:"powered=false,shape=ascending_west",4:"powered=false,shape=ascending_north",5:"powered=false,shape=ascending_south",8:"powered=true,shape=north_south",9:"powered=true,shape=east_west",10:"powered=true,shape=ascending_east",11:"powered=true,shape=ascending_west",12:"powered=true,shape=ascending_north",13:"powered=true,shape=ascending_south"},"detector_rail":{0:"powered=false,shape=north_south",1:"powered=false,shape=east_west",2:"powered=false,shape=ascending_east",3:"powered=false,shape=ascending_west",4:"powered=false,shape=ascending_north",5:"powered=false,shape=ascending_south",8:"powered=true,shape=north_south",9:"powered=true,shape=east_west",10:"powered=true,shape=ascending_east",11:"powered=true,shape=ascending_west",12:"powered=true,shape=ascending_north",13:"powered=true,shape=ascending_south"},"golden_rail":{0:"powered=false,shape=north_south",1:"powered=false,shape=east_west",2:"powered=false,shape=ascending_east",3:"powered=false,shape=ascending_west",4:"powered=false,shape=ascending_north",5:"powered=false,shape=ascending_south",8:"powered=true,shape=north_south",9:"powered=true,shape=east_west",10:"powered=true,shape=ascending_east",11:"powered=true,shape=ascending_west",12:"powered=true,shape=ascending_north",13:"powered=true,shape=ascending_south"},"skull":{0:"facing=down,nodrop=false",1:"facing=up,nodrop=false",2:"facing=north,nodrop=false",3:"facing=south,nodrop=false",4:"facing=west,nodrop=false",5:"facing=east,nodrop=false",6:"facing=down,nodrop=false",7:"facing=up,nodrop=false",8:"facing=down,nodrop=true",9:"facing=up,nodrop=true",10:"facing=north,nodrop=true",11:"facing=south,nodrop=true",12:"facing=west,nodrop=true",13:"facing=east,nodrop=true",14:"facing=down,nodrop=true",15:"facing=up,nodrop=true"},"red_sandstone_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"nether_brick_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"stone_brick_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"sandstone_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"dark_oak_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"acacia_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"jungle_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"purpur_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"quartz_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"spruce_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"birch_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"brick_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"stone_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"oak_stairs":{0:"facing=east,half=bottom",1:"facing=west,half=bottom",2:"facing=south,half=bottom",3:"facing=north,half=bottom",4:"facing=east,half=top",5:"facing=west,half=top",6:"facing=south,half=top",7:"facing=north,half=top",8:"facing=east,half=bottom",9:"facing=west,half=bottom",10:"facing=south,half=bottom",11:"facing=north,half=bottom",12:"facing=east,half=top",13:"facing=west,half=top",14:"facing=south,half=top",15:"facing=north,half=top"},"end_portal_frame":{0:"eye=false,facing=south",1:"eye=false,facing=west",2:"eye=false,facing=north",3:"eye=false,facing=east",4:"eye=true,facing=south",5:"eye=true,facing=west",6:"eye=true,facing=north",7:"eye=true,facing=east",8:"eye=false,facing=south",9:"eye=false,facing=west",10:"eye=false,facing=north",11:"eye=false,facing=east",12:"eye=true,facing=south",13:"eye=true,facing=west",14:"eye=true,facing=north",15:"eye=true,facing=east"},"leaves2":{0:"check_decay=false,decayable=true,variant=acacia",1:"check_decay=false,decayable=true,variant=dark_oak",4:"check_decay=false,decayable=false,variant=acacia",5:"check_decay=false,decayable=false,variant=dark_oak",8:"check_decay=true,decayable=true,variant=acacia",9:"check_decay=true,decayable=true,variant=dark_oak",12:"check_decay=true,decayable=false,variant=acacia",13:"check_decay=true,decayable=false,variant=dark_oak"},"log":{0:"axis=y,variant=oak",1:"axis=y,variant=spruce",2:"axis=y,variant=birch",3:"axis=y,variant=jungle",4:"axis=x,variant=oak",5:"axis=x,variant=spruce",6:"axis=x,variant=birch",7:"axis=x,variant=jungle",8:"axis=z,variant=oak",9:"axis=z,variant=spruce",10:"axis=z,variant=birch",11:"axis=z,variant=jungle",12:"axis=none,variant=oak",13:"axis=none,variant=spruce",14:"axis=none,variant=birch",15:"axis=none,variant=jungle"},"unpowered_repeater":{0:"delay=1,facing=south",1:"delay=1,facing=north",2:"delay=1,facing=west",3:"delay=1,facing=east",4:"delay=2,facing=south",5:"delay=2,facing=north",6:"delay=2,facing=west",7:"delay=2,facing=east",8:"delay=3,facing=south",9:"delay=3,facing=north",10:"delay=3,facing=west",11:"delay=3,facing=east",12:"delay=4,facing=south",13:"delay=4,facing=north",14:"delay=4,facing=west",15:"delay=4,facing=east"},"powered_repeater":{0:"delay=1,facing=south",1:"delay=1,facing=north",2:"delay=1,facing=west",3:"delay=1,facing=east",4:"delay=2,facing=south",5:"delay=2,facing=north",6:"delay=2,facing=west",7:"delay=2,facing=east",8:"delay=3,facing=south",9:"delay=3,facing=north",10:"delay=3,facing=west",11:"delay=3,facing=east",12:"delay=4,facing=south",13:"delay=4,facing=north",14:"delay=4,facing=west",15:"delay=4,facing=east"},"sticky_piston":{0:"extended=false,facing=down",1:"extended=false,facing=up",2:"extended=false,facing=north",3:"extended=false,facing=south",4:"extended=false,facing=west",5:"extended=false,facing=east",8:"extended=true,facing=down",9:"extended=true,facing=up",10:"extended=true,facing=north",11:"extended=true,facing=south",12:"extended=true,facing=west",13:"extended=true,facing=east"},"sapling":{0:"stage=0,type=oak",1:"stage=0,type=spruce",2:"stage=0,type=birch",3:"stage=0,type=jungle",4:"stage=0,type=acacia",5:"stage=0,type=dark_oak",6:"stage=0,type=oak",7:"stage=0,type=oak",8:"stage=1,type=oak",9:"stage=1,type=spruce",10:"stage=1,type=birch",11:"stage=1,type=jungle",12:"stage=1,type=acacia",13:"stage=1,type=dark_oak",14:"stage=1,type=oak",15:"stage=1,type=oak"},"piston":{0:"extended=false,facing=down",1:"extended=false,facing=up",2:"extended=false,facing=north",3:"extended=false,facing=south",4:"extended=false,facing=west",5:"extended=false,facing=east",8:"extended=true,facing=down",9:"extended=true,facing=up",10:"extended=true,facing=north",11:"extended=true,facing=south",12:"extended=true,facing=west",13:"extended=true,facing=east"},"brown_mushroom_block":{0:"variant=all_inside",1:"variant=north_west",2:"variant=north",3:"variant=north_east",4:"variant=west",5:"variant=center",6:"variant=east",7:"variant=south_west",8:"variant=south",9:"variant=south_east",10:"variant=stem",11:"variant=all_inside",12:"variant=all_inside",13:"variant=all_inside",14:"variant=all_outside",15:"variant=all_stem"},"red_mushroom_block":{0:"variant=all_inside",1:"variant=north_west",2:"variant=north",3:"variant=north_east",4:"variant=west",5:"variant=center",6:"variant=east",7:"variant=south_west",8:"variant=south",9:"variant=south_east",10:"variant=stem",11:"variant=all_inside",12:"variant=all_inside",13:"variant=all_inside",14:"variant=all_outside",15:"variant=all_stem"},"piston_extension":{0:"facing=down,type=normal",1:"facing=up,type=normal",2:"facing=north,type=normal",3:"facing=south,type=normal",4:"facing=west,type=normal",5:"facing=east,type=normal",8:"facing=down,type=sticky",9:"facing=up,type=sticky",10:"facing=north,type=sticky",11:"facing=south,type=sticky",12:"facing=west,type=sticky",13:"facing=east,type=sticky"},"piston_head":{0:"facing=down,type=normal",1:"facing=up,type=normal",2:"facing=north,type=normal",3:"facing=south,type=normal",4:"facing=west,type=normal",5:"facing=east,type=normal",8:"facing=down,type=sticky",9:"facing=up,type=sticky",10:"facing=north,type=sticky",11:"facing=south,type=sticky",12:"facing=west,type=sticky",13:"facing=east,type=sticky"},"quartz_block":{0:"variant=default",1:"variant=chiseled",2:"variant=lines_y",3:"variant=lines_x",4:"variant=lines_z",5:"variant=default",6:"variant=default",7:"variant=default",8:"variant=default",9:"variant=default",10:"variant=default",11:"variant=default",12:"variant=default",13:"variant=default",14:"variant=default",15:"variant=default"},"jukebox":{0:"has_record=false",1:"has_record=true",2:"has_record=true",3:"has_record=true",4:"has_record=true",5:"has_record=true",6:"has_record=true",7:"has_record=true",8:"has_record=true",9:"has_record=true",10:"has_record=true",11:"has_record=true",12:"has_record=true",13:"has_record=true",14:"has_record=true",15:"has_record=true"},"tallgrass":{0:"type=dead_bush",1:"type=tall_grass",2:"type=fern",3:"type=dead_bush",4:"type=dead_bush",5:"type=dead_bush",6:"type=dead_bush",7:"type=dead_bush",8:"type=dead_bush",9:"type=dead_bush",10:"type=dead_bush",11:"type=dead_bush",12:"type=dead_bush",13:"type=dead_bush",14:"type=dead_bush",15:"type=dead_bush"},"anvil":{0:"damage=0,facing=south",1:"damage=0,facing=west",2:"damage=0,facing=north",3:"damage=0,facing=east",4:"damage=1,facing=south",5:"damage=1,facing=west",6:"damage=1,facing=north",7:"damage=1,facing=east",8:"damage=2,facing=south",9:"damage=2,facing=west",10:"damage=2,facing=north",11:"damage=2,facing=east"},"double_wooden_slab":{0:"variant=oak",1:"variant=spruce",2:"variant=birch",3:"variant=jungle",4:"variant=acacia",5:"variant=dark_oak",6:"variant=oak",7:"variant=oak",8:"variant=oak",9:"variant=spruce",10:"variant=birch",11:"variant=jungle",12:"variant=acacia",13:"variant=dark_oak",14:"variant=oak",15:"variant=oak"},"tnt":{0:"explode=false",1:"explode=true",2:"explode=false",3:"explode=true",4:"explode=false",5:"explode=true",6:"explode=false",7:"explode=true",8:"explode=false",9:"explode=true",10:"explode=false",11:"explode=true",12:"explode=false",13:"explode=true",14:"explode=false",15:"explode=true"},"stained_hardened_clay":{0:"color=white",1:"color=orange",2:"color=magenta",3:"color=light_blue",4:"color=yellow",5:"color=lime",6:"color=pink",7:"color=gray",8:"color=silver",9:"color=cyan",10:"color=purple",11:"color=blue",12:"color=brown",13:"color=green",14:"color=red",15:"color=black"},"trapped_chest":{0:"facing=north",1:"facing=north",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=north",7:"facing=north",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=north",13:"facing=north",14:"facing=north",15:"facing=south"},"ender_chest":{0:"facing=north",1:"facing=north",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=north",7:"facing=north",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=north",13:"facing=north",14:"facing=north",15:"facing=south"},"lit_furnace":{0:"facing=north",1:"facing=north",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=north",7:"facing=north",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=north",13:"facing=north",14:"facing=north",15:"facing=south"},"wall_banner":{0:"facing=north",1:"facing=north",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=north",7:"facing=north",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=north",13:"facing=north",14:"facing=north",15:"facing=south"},"light_blue_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"planks":{0:"variant=oak",1:"variant=spruce",2:"variant=birch",3:"variant=jungle",4:"variant=acacia",5:"variant=dark_oak",6:"variant=oak",7:"variant=oak",8:"variant=oak",9:"variant=oak",10:"variant=oak",11:"variant=oak",12:"variant=oak",13:"variant=oak",14:"variant=oak",15:"variant=oak"},"stained_glass_pane":{0:"color=white",1:"color=orange",2:"color=magenta",3:"color=light_blue",4:"color=yellow",5:"color=lime",6:"color=pink",7:"color=gray",8:"color=silver",9:"color=cyan",10:"color=purple",11:"color=blue",12:"color=brown",13:"color=green",14:"color=red",15:"color=black"},"wall_sign":{0:"facing=north",1:"facing=north",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=north",7:"facing=north",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=north",13:"facing=north",14:"facing=north",15:"facing=south"},"furnace":{0:"facing=north",1:"facing=north",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=north",7:"facing=north",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=north",13:"facing=north",14:"facing=north",15:"facing=south"},"lit_pumpkin":{0:"facing=south",1:"facing=west",2:"facing=north",3:"facing=east",4:"facing=south",5:"facing=west",6:"facing=north",7:"facing=east",8:"facing=south",9:"facing=west",10:"facing=north",11:"facing=east",12:"facing=south",13:"facing=west",14:"facing=north",15:"facing=east"},"magenta_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"concrete_powder":{0:"color=white",1:"color=orange",2:"color=magenta",3:"color=light_blue",4:"color=yellow",5:"color=lime",6:"color=pink",7:"color=gray",8:"color=silver",9:"color=cyan",10:"color=purple",11:"color=blue",12:"color=brown",13:"color=green",14:"color=red",15:"color=black"},"ladder":{0:"facing=north",1:"facing=north",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=north",7:"facing=north",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=north",13:"facing=north",14:"facing=north",15:"facing=south"},"orange_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"purple_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"silver_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"yellow_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"black_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"brown_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"chest":{0:"facing=north",1:"facing=north",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=north",7:"facing=north",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=north",13:"facing=north",14:"facing=north",15:"facing=south"},"green_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"stained_glass":{0:"color=white",1:"color=orange",2:"color=magenta",3:"color=light_blue",4:"color=yellow",5:"color=lime",6:"color=pink",7:"color=gray",8:"color=silver",9:"color=cyan",10:"color=purple",11:"color=blue",12:"color=brown",13:"color=green",14:"color=red",15:"color=black"},"white_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"blue_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"cyan_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"gray_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"lime_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"pink_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"cocoa":{0:"age=0,facing=south",1:"age=0,facing=west",2:"age=0,facing=north",3:"age=0,facing=east",4:"age=1,facing=south",5:"age=1,facing=west",6:"age=1,facing=north",7:"age=1,facing=east",8:"age=2,facing=south",9:"age=2,facing=west",10:"age=2,facing=north",11:"age=2,facing=east"},"pumpkin":{0:"facing=south",1:"facing=west",2:"facing=north",3:"facing=east",4:"facing=south",5:"facing=west",6:"facing=north",7:"facing=east",8:"facing=south",9:"facing=west",10:"facing=north",11:"facing=east",12:"facing=south",13:"facing=west",14:"facing=north",15:"facing=east"},"red_shulker_box":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"concrete":{0:"color=white",1:"color=orange",2:"color=magenta",3:"color=light_blue",4:"color=yellow",5:"color=lime",6:"color=pink",7:"color=gray",8:"color=silver",9:"color=cyan",10:"color=purple",11:"color=blue",12:"color=brown",13:"color=green",14:"color=red",15:"color=black"},"carpet":{0:"color=white",1:"color=orange",2:"color=magenta",3:"color=light_blue",4:"color=yellow",5:"color=lime",6:"color=pink",7:"color=gray",8:"color=silver",9:"color=cyan",10:"color=purple",11:"color=blue",12:"color=brown",13:"color=green",14:"color=red",15:"color=black"},"observer":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"wool":{0:"color=white",1:"color=orange",2:"color=magenta",3:"color=light_blue",4:"color=yellow",5:"color=lime",6:"color=pink",7:"color=gray",8:"color=silver",9:"color=cyan",10:"color=purple",11:"color=blue",12:"color=brown",13:"color=green",14:"color=red",15:"color=black"},"end_rod":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=north",9:"facing=south",10:"facing=west",11:"facing=east",12:"facing=down",13:"facing=up",14:"facing=north",15:"facing=south"},"dispenser":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=down",9:"facing=up",10:"facing=north",11:"facing=south",12:"facing=west",13:"facing=east",14:"facing=down",15:"facing=up"},"standing_banner":{0:"rotation=0",1:"rotation=1",2:"rotation=2",3:"rotation=3",4:"rotation=4",5:"rotation=5",6:"rotation=6",7:"rotation=7",8:"rotation=8",9:"rotation=9",10:"rotation=10",11:"rotation=11",12:"rotation=12",13:"rotation=13",14:"rotation=14",15:"rotation=15"},"dropper":{0:"facing=down",1:"facing=up",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",7:"facing=up",8:"facing=down",9:"facing=up",10:"facing=north",11:"facing=south",12:"facing=west",13:"facing=east",14:"facing=down",15:"facing=up"},"standing_sign":{0:"rotation=0",1:"rotation=1",2:"rotation=2",3:"rotation=3",4:"rotation=4",5:"rotation=5",6:"rotation=6",7:"rotation=7",8:"rotation=8",9:"rotation=9",10:"rotation=10",11:"rotation=11",12:"rotation=12",13:"rotation=13",14:"rotation=14",15:"rotation=15"},"farmland":{0:"moisture=0",1:"moisture=1",2:"moisture=2",3:"moisture=3",4:"moisture=4",5:"moisture=5",6:"moisture=6",7:"moisture=7",8:"moisture=0",9:"moisture=1",10:"moisture=2",11:"moisture=3",12:"moisture=4",13:"moisture=5",14:"moisture=6",15:"moisture=7"},"heavy_weighted_pressure_plate":{0:"power=0",1:"power=1",2:"power=2",3:"power=3",4:"power=4",5:"power=5",6:"power=6",7:"power=7",8:"power=8",9:"power=9",10:"power=10",11:"power=11",12:"power=12",13:"power=13",14:"power=14",15:"power=15"},"light_weighted_pressure_plate":{0:"power=0",1:"power=1",2:"power=2",3:"power=3",4:"power=4",5:"power=5",6:"power=6",7:"power=7",8:"power=8",9:"power=9",10:"power=10",11:"power=11",12:"power=12",13:"power=13",14:"power=14",15:"power=15"},"rail":{0:"shape=north_south",1:"shape=east_west",2:"shape=ascending_east",3:"shape=ascending_west",4:"shape=ascending_north",5:"shape=ascending_south",6:"shape=south_east",7:"shape=south_west",8:"shape=north_west",9:"shape=north_east"},"daylight_detector_inverted":{0:"power=0",1:"power=1",2:"power=2",3:"power=3",4:"power=4",5:"power=5",6:"power=6",7:"power=7",8:"power=8",9:"power=9",10:"power=10",11:"power=11",12:"power=12",13:"power=13",14:"power=14",15:"power=15"},"structure_block":{0:"mode=data",1:"mode=data",2:"mode=data",3:"mode=data",4:"mode=data",5:"mode=data",6:"mode=data",7:"mode=data",8:"mode=data",9:"mode=data",10:"mode=data",12:"mode=data",13:"mode=data",14:"mode=data",15:"mode=data"},"log2":{0:"axis=y,variant=acacia",1:"axis=y,variant=dark_oak",4:"axis=x,variant=acacia",5:"axis=x,variant=dark_oak",8:"axis=z,variant=acacia",9:"axis=z,variant=dark_oak",12:"axis=none,variant=acacia",13:"axis=none,variant=dark_oak"},"sponge":{0:"wet=false",1:"wet=true",2:"wet=false",3:"wet=true",4:"wet=false",5:"wet=true",6:"wet=false",7:"wet=true",8:"wet=false",9:"wet=true",10:"wet=false",11:"wet=true",12:"wet=false",13:"wet=true",14:"wet=false",15:"wet=true"},"daylight_detector":{0:"power=0",1:"power=1",2:"power=2",3:"power=3",4:"power=4",5:"power=5",6:"power=6",7:"power=7",8:"power=8",9:"power=9",10:"power=10",11:"power=11",12:"power=12",13:"power=13",14:"power=14",15:"power=15"},"redstone_wire":{0:"power=0",1:"power=1",2:"power=2",3:"power=3",4:"power=4",5:"power=5",6:"power=6",7:"power=7",8:"power=8",9:"power=9",10:"power=10",11:"power=11",12:"power=12",13:"power=13",14:"power=14",15:"power=15"},"flowing_water":{0:"level=0",1:"level=1",2:"level=2",3:"level=3",4:"level=4",5:"level=5",6:"level=6",7:"level=7",8:"level=8",9:"level=9",10:"level=10",11:"level=11",12:"level=12",13:"level=13",14:"level=14",15:"level=15"},"flowing_lava":{0:"level=0",1:"level=1",2:"level=2",3:"level=3",4:"level=4",5:"level=5",6:"level=6",7:"level=7",8:"level=8",9:"level=9",10:"level=10",11:"level=11",12:"level=12",13:"level=13",14:"level=14",15:"level=15"},"red_flower":{0:"variant=poppy",1:"variant=blue_orchid",2:"variant=allium",3:"variant=houstonia",4:"variant=red_tulip",5:"variant=orange_tulip",6:"variant=white_tulip",7:"variant=pink_tulip",8:"variant=oxeye_daisy"},"water":{0:"level=0",1:"level=1",2:"level=2",3:"level=3",4:"level=4",5:"level=5",6:"level=6",7:"level=7",8:"level=8",9:"level=9",10:"level=10",11:"level=11",12:"level=12",13:"level=13",14:"level=14",15:"level=15"},"lava":{0:"level=0",1:"level=1",2:"level=2",3:"level=3",4:"level=4",5:"level=5",6:"level=6",7:"level=7",8:"level=8",9:"level=9",10:"level=10",11:"level=11",12:"level=12",13:"level=13",14:"level=14",15:"level=15"},"hopper":{0:"facing=down",2:"facing=north",3:"facing=south",4:"facing=west",5:"facing=east",6:"facing=down",8:"facing=down",10:"facing=north",11:"facing=south",12:"facing=west",13:"facing=east",14:"facing=down"},"purpur_pillar":{0:"axis=y",1:"axis=y",2:"axis=y",3:"axis=y",4:"axis=x",5:"axis=x",6:"axis=x",7:"axis=x",8:"axis=z",9:"axis=z",10:"axis=z",11:"axis=z",12:"axis=y",13:"axis=y",14:"axis=y",15:"axis=y"},"bone_block":{0:"axis=y",1:"axis=y",2:"axis=y",3:"axis=y",4:"axis=x",5:"axis=x",6:"axis=x",7:"axis=x",8:"axis=z",9:"axis=z",10:"axis=z",11:"axis=z",12:"axis=y",13:"axis=y",14:"axis=y",15:"axis=y"},"hay_block":{0:"axis=y",1:"axis=y",2:"axis=y",3:"axis=y",4:"axis=x",5:"axis=x",6:"axis=x",7:"axis=x",8:"axis=z",9:"axis=z",10:"axis=z",11:"axis=z",12:"axis=y",13:"axis=y",14:"axis=y",15:"axis=y"},"portal":{0:"axis=x",1:"axis=x",2:"axis=z",3:"axis=x",4:"axis=x",5:"axis=x",6:"axis=z",7:"axis=x",8:"axis=x",9:"axis=x",10:"axis=z",11:"axis=x",12:"axis=x",13:"axis=x",14:"axis=z",15:"axis=x"},"cactus":{0:"age=0",1:"age=1",2:"age=2",3:"age=3",4:"age=4",5:"age=5",6:"age=6",7:"age=7",8:"age=8",9:"age=9",10:"age=10",11:"age=11",12:"age=12",13:"age=13",14:"age=14",15:"age=15"},"frosted_ice":{0:"age=0",1:"age=1",2:"age=2",3:"age=3",4:"age=3",5:"age=3",6:"age=3",7:"age=3",8:"age=3",9:"age=3",10:"age=3",11:"age=3",12:"age=3",13:"age=3",14:"age=3",15:"age=3"},"reeds":{0:"age=0",1:"age=1",2:"age=2",3:"age=3",4:"age=4",5:"age=5",6:"age=6",7:"age=7",8:"age=8",9:"age=9",10:"age=10",11:"age=11",12:"age=12",13:"age=13",14:"age=14",15:"age=15"},"fire":{0:"age=0",1:"age=1",2:"age=2",3:"age=3",4:"age=4",5:"age=5",6:"age=6",7:"age=7",8:"age=8",9:"age=9",10:"age=10",11:"age=11",12:"age=12",13:"age=13",14:"age=14",15:"age=15"},"snow_layer":{0:"age=1",1:"age=2",2:"age=3",3:"age=4",4:"age=5",5:"age=6",6:"age=7",7:"age=8",8:"age=1",9:"age=2",10:"age=3",11:"age=4",12:"age=5",13:"age=6",14:"age=7",15:"age=8"},"stone":{0:"variant=stone",1:"variant=granite",2:"variant=smooth_granite",3:"variant=diorite",4:"variant=smooth_diorite",5:"variant=andesite",6:"variant=smooth_andesite"},"monster_egg":{0:"variants=stone",1:"variants=cobblestone",2:"variants=stone_brick",3:"variants=mossy_stone",4:"variants=cracked_brick",5:"variants=chiseled_brick"},"stonebrick":{0:"variants=stonebrick",1:"variants=mossy_stonebrick",2:"variants=cracked_stonebrick",3:"variants=chiseled_stonebrick"},"unlit_redstone_torch":{0:"facing=up",1:"facing=east",2:"facing=west",3:"facing=south",4:"facing=north"},"red_sandstone":{0:"type=red_sandstone",1:"type=chiseled_red_sandstone",2:"type=smooth_red_sandstone"},"redstone_torch":{0:"facing=up",1:"facing=east",2:"facing=west",3:"facing=south",4:"facing=north"},"light_blue_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"pumpkin_stem":{0:"age=0",1:"age=1",2:"age=2",3:"age=3",4:"age=4",5:"age=5",6:"age=6",7:"age=7"},"prismarine":{0:"variant=prismarine",1:"variant=prismarine_bricks",2:"variant=dark_prismarine"},"magenta_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"melon_stem":{0:"age=0",1:"age=1",2:"age=2",3:"age=3",4:"age=4",5:"age=5",6:"age=6",7:"age=7"},"orange_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"yellow_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"silver_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"purple_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"white_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"brown_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"green_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"cake":{0:"bites=0",1:"bites=1",2:"bites=2",3:"bites=3",4:"bites=4",5:"bites=5",6:"bites=6"},"potatoes":{0:"age=0",1:"age=1",2:"age=2",3:"age=3",4:"age=4",5:"age=5",6:"age=6",7:"age=7"},"lime_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"pink_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"gray_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"cyan_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"blue_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"black_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"carrots":{0:"age=0",1:"age=1",2:"age=2",3:"age=3",4:"age=4",5:"age=5",6:"age=6",7:"age=7"},"red_glazed_terracotta":{0:"facing=north",1:"facing=south",2:"facing=east",3:"facing=west"},"torch":{0:"facing=up",1:"facing=east",2:"facing=west",3:"facing=south",4:"facing=north"},"wheat":{0:"age=0",1:"age=1",2:"age=2",3:"age=3",4:"age=4",5:"age=5",6:"age=6",7:"age=7"},"sandstone":{0:"type=sandstone",1:"type=chiseled_sandstone",2:"type=smooth_sandstone"},"chorus_flower":{0:"age=0",1:"age=1",2:"age=2",3:"age=3",4:"age=4",5:"age=5"},"cobblestone_wall":{0:"variant=cobblestone",1:"variant=mossy_cobblestone"},"dirt":{0:"variant=dirt",1:"variant=coarse_dirt",2:"variant=podzol"},"cauldron":{0:"level=0",1:"level=1",2:"level=2",3:"level=3"},"wooden_pressure_plate":{0:"powered=false",1:"powered=true"},"stone_pressure_plate":{0:"powered=false",1:"powered=true"},"nether_wart":{0:"age=0",1:"age=1",2:"age=2",3:"age=3"},"beetroots":{0:"age=0",1:"age=1",2:"age=2",3:"age=3"},"sand":{0:"type=sand",1:"type=red_sand"},"nether_brick_fence":{},"purpur_double_slab":{},"mossy_cobblestone":{},"nether_wart_block":{},"lit_redstone_lamp":{},"enchanting_table":{},"red_nether_brick":{},"lit_redstone_ore":{},"brown_mushroom":{},"crafting_table":{},"dark_oak_fence":{},"redstone_block":{},"structure_void":{},"diamond_block":{},"hardened_clay":{},"emerald_block":{},"redstone_lamp":{},"yellow_flower":{},"acacia_fence":{},"chorus_plant":{},"jungle_fence":{},"nether_brick":{},"purpur_block":{},"red_mushroom":{},"redstone_ore":{},"spruce_fence":{},"birch_fence":{},"brick_block":{},"diamond_ore":{},"cobblestone":{},"sea_lantern":{},"end_gateway":{},"mob_spawner":{},"lapis_block":{},"emerald_ore":{},"dragon_egg":{},"end_portal":{},"end_bricks":{},"flower_pot":{},"glass_pane":{},"gold_block":{},"coal_block":{},"grass_path":{},"iron_block":{},"packed_ice":{},"netherrack":{},"quartz_ore":{},"bookshelf":{},"end_stone":{},"glowstone":{},"iron_bars":{},"lapis_ore":{},"noteblock":{},"soul_sand":{},"waterlily":{},"deadbush":{},"gold_ore":{},"iron_ore":{},"coal_ore":{},"mycelium":{},"obsidian":{},"bedrock":{},"barrier":{},"beacon":{},"gravel":{},"fence":{},"glass":{},"grass":{},"magma":{},"melon":{},"slime":{},"clay":{},"snow":{},"air":{},"ice":{},"web":{}}
Globals.selectorRe = re.compile(r"^(?:@[rapes](?:\[(?:[a-z0-9_]+=!?[a-z0-9_:/-]+)(?:,[a-z0-9_]+=!?[a-z0-9_:/-]+)*\])?|[^@]+)$", re.I)
Globals.blockStateRe = re.compile(r"^(?:(?:[a-z_]+=[a-z0-9_]+)(?:,[a-z_]+=[a-z0-9_]+)*|default|\*)$")
Globals.scoreRe = re.compile(r"^score_(.{1,16}?)(_min)?$")
Globals.functionRe = re.compile(r"^.+?:[^/]+?(?:/[^/]+?)*$", re.I)
Globals.keyRe = re.compile(r"^(?:[a-z0-9]+|\"[a-z0-9]+\")$", re.I)
_list = list


for key in Globals.blockStates:
    for i in xrange(16):
        if i not in Globals.blockStates[key]:
            Globals.blockStates[key][i] = "default"


def escape(s):
    return s.replace("\\", "\\\\").replace("\"", "\\\"")


def unEscape(s):
    return s.replace("\\\\", "\\").replace("\\\"", "\"")


def canAt(data, *labels):
    for label in labels:
        if label in data and data[label][0] == '~':
            return True
    return False


def getKey(s):
    colon = s.find(':')
    if colon == -1:
        raise SyntaxError(u"No colon found after key: '{}'".format(s))
    key = s[:colon].strip()
    if not Globals.keyRe.match(key):
        raise SyntaxError(u"Invalid characters in key: '{}'".format(key))
    return key, s[colon+1:]


def getData(s):
    s = s.lstrip()
    if s[0] == '{':
        return getCompound(s[1:])
    elif s[0] == '[':
        return getList(s[1:])
    elif s[0] == '\"':
        return getQString(s[1:])
    elif s[0] in ('}', ']', ',', ':'):
        raise SyntaxError(u"Empty value")
    else:
        return getString(s)


def getString(s):
    ret = u""
    i = 0
    while True:
        if i == len(s):
            raise SyntaxError(u"Unbalanced brackets (more opened than closed)")
        if s[i] in (',', '}', ']'):
            return ret.rstrip(), s[i:]
        if s[i] in ('{', '[', '\"', ':'):
            raise SyntaxError(u"unquoted value can't have '{' or '[' or '\"' or : in them")
        ret += s[i]
        i += 1


def getQString(s):
    ret = u"\""
    skip = False
    i = 0
    while True:
        if i == len(s):
            raise SyntaxError(u"No closing quote found: '{}'".format(s))
        if skip:
            skip = False
        elif s[i] == '\\':
            skip = True
        elif s[i] == '\"':
            ret += '\"'
            break
        ret += s[i]
        i += 1
    s = s[i+1:].lstrip()
    if s[0] in (',', '}', ']'):
        return ret.rstrip(), s
    raise SyntaxError(u"Expected ',' or '}' or ']' but got: '{}'".format(s[0]))


def getList(s):
    ret = NBTList()
    if s[0] == "]":
            return ret, s[1:].lstrip()
    if s[0] == 'I' and s[1:].lstrip() == ';':
        s = s[s.find(';')+1:]
        ret = ["I;"]
    while True:
        data, s = getData(s)
        ret.append(data)
        if s[0] == ']':
            return ret, s[1:].lstrip()
        if s[0] == ',':
            s = s[1:].lstrip()
        else:
            raise SyntaxError(u"Expected ']' or ',' but got: \'{}\'".format(s[0]))


def signText(s):
    try:
        s = json.JSONDecoder().decode(unEscape(s[1:-1].strip()))
        walk(s)
        return u"\"{}\"".format(escape(json.JSONEncoder(separators=(',', ':')).encode(s)))
    except ValueError, e:
        return s


def getCompound(s):
    ret = NBTCompound()
    if s[0] == "}":
            return ret, s[1:].lstrip()
    while True:
        key, s = getKey(s)
        data, s = getData(s)
        if key == "Command":
            if data[0] == '"':
                ret[key] = u"\"{}\"".format(escape(unicode(decide(unEscape(data[1:-1])))))
            else:
                ret[key] = unicode(decide(data))
        elif key in ("Text1", "Text2", "Text3", "Text4"):
            ret[key] = signText(data)
        elif key == "pages":
            for i, page in enumerate(data.data):
                tmp = json.JSONDecoder().decode(unEscape(page[1:-1].strip()))
                walk(tmp)
                data.data[i] = u"\"{}\"".format(escape(unicode(json.JSONEncoder(separators=(',', ':')).encode(tmp))))
            ret[key] = data
        else:
            ret[key] = data

        if s[0] == '}':
            return ret, s[1:].lstrip()
        if s[0] == ',':
            s = s[1:].lstrip()
        else:
            raise SyntaxError(u"Expected '}' or ',' but got: \'{}\'".format(s[0]))


def block(data, setMode, nameLabel, stateLabel=None, nbtLabel=None):
    s = data[nameLabel].replace("minecraft:", "", 1)
    if setMode:
        if stateLabel in data:
            if data[stateLabel] == "-1":
                data[stateLabel] = "default"
            if data[stateLabel] != "default" and Globals.blockStates[data[nameLabel]][0] != data[stateLabel]:
                s += u"[{}]".format(data[stateLabel])
    else:
        if stateLabel in data:
            if data[stateLabel] == "-1":
                data[stateLabel] = "*"
            if data[stateLabel] != "*":
                s += u"[{}]".format(data[stateLabel])
    if nbtLabel in data:
        s += u"{}".format(data[nbtLabel])
    return s


def item(data, nameLabel, damageLabel=None, nbtLabel=None):
    s = data[nameLabel].replace("minecraft:", "", 1)
    if nbtLabel in data:
        if damageLabel in data and data[damageLabel] != '0':
            data[nbtLabel].data["Damage"] = data[damageLabel]
        return u"{}{}".format(s, data[nbtLabel])
    else:
        if damageLabel in data and data[damageLabel] != '0':
            return u"{}{{Damage:{}}}".format(s, data[damageLabel])
        else:
            return s


def selectorRange(data, low, high):
    if low in data and high in data and data[low] == data[high]:
        return data[low]

    ret = u".."
    if low in data:
        ret = data[low] + ret
    if high in data:
        ret += data[high]

    return ret


def futurizeSelector(data):
    ret = []
    for future, low, high in Globals.selectorArgsNew:
        if future != 'score':
            tmp = selectorRange(data, low, high)
            if tmp != "..":
                ret.append(u"{}={}".format(future, tmp))
        else:
            scores = []
            for key in data.keys():
                res = Globals.scoreRe.match(key)
                if res:
                    scores.append((res.group(1), res.group(2), data[key]))

            scores.sort()
            scores.append(' ')
            i = 0
            while i < len(scores) - 1:
                if scores[i][0] == scores[i+1][0]:
                    if scores[i][1] is None:
                        ret.append(u"score_{}={}".format(scores[i][0], selectorRange({0: scores[i+1][2], 1: scores[i][2]}, 0, 1)))
                    else:
                        ret.append(u"score_{}={}".format(scores[i][0], selectorRange({0: scores[i+1][2], 1: scores[i][2]}, 1, 0)))
                    i += 1
                elif scores[i][1] is None:
                    ret.append(u"score_{}=..{}".format(scores[i][0], scores[i][2]))
                else:
                    ret.append(u"score_{}={}..".format(scores[i][0], scores[i][2]))
                i += 1

    return ret


def isXp(s):
    s = s[:-1] if s[-1] == 'L' else s
    return isNumber(s)


def isCoord(s):
    s = s[1:] if s[0] == '~' else s
    return s == '' or isNumber(s)


def isNumber(s):
    if s.lower() == "nan":
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def walk(node):
    if type(node) == dict:
        for key, item in node.items():
            if type(item) is dict or type(item) is _list:
                walk(item)
            else:
                if key == "action" and item == "run_command" and "value" in node:
                    if node["value"][0] == '/':
                        node["value"] = u"/{}".format(decide(node["value"][1:]))

    else:
        for item in node:
            if type(item) is dict or type(item) is _list:
                walk(item)


def synt(caller, syntax):
    return u"{} {}".format(caller, " ".join(syntax))


def syntCount(syntax):
    total = 0
    for word in syntax:
        if word[0] == '<':
            total += 1
        else:
            return u"{}+".format(total)
    return unicode(total)


def array(a):
    return u"[\'{}\']".format(u"\', \'".join(map(unicode, a)))


def lex(caller, syntaxes, tokens):
    messages = u""
    for syntax in syntaxes:
        try:
            workTokens = tokens[:]
            for i, word in enumerate(syntax):
                if word[0] == '<':
                    if not len(workTokens) >= i+1:
                        raise SyntaxError(u"Not enough tokens: Syntax({}): '{}' Tokens({}): {}".format(syntCount(syntax), synt(caller, syntax), len(workTokens), array([caller] + workTokens)))
                elif word[0] == '[':
                    if not len(workTokens) >= i+1:
                        syntax = syntax[:i]
                        break
                else:
                    raise AssertionError(u"A Syntax '{}' is defined badly at Word '{}'.".format(synt(caller, syntax), word))

                if word[1] == '@':
                    workTokens[i] = Selector(workTokens[i])
                elif word[1] == '(':
                    if workTokens[i].lower() not in map(lambda x: x.lower(), word[2:].split('|')):
                        raise SyntaxError(u"Token: '{}' is not in the list: {}".format(workTokens[i], word[2:].split('|')))
                    workTokens[i] = word[2:].split('|')[map(lambda x: x.lower(), word[2:].split('|')).index(workTokens[i].lower())]
                elif word[1] == '*':
                    workTokens = workTokens[:i] + [u" ".join(workTokens[i:])]
                    break
                elif word[1] == '0':
                    if not isNumber(workTokens[i]):
                        raise SyntaxError(u"{} is not a number".format(workTokens[i]))
                elif word[1] == '~':
                    if not isCoord(workTokens[i]):
                        raise SyntaxError(u"{} is not a coordinate".format(workTokens[i]))
                elif word[1] == '%':
                    if not isXp(workTokens[i]):
                        raise SyntaxError(u"{} is not a valid xp format".format(workTokens[i]))
                elif word[1] == '=':
                    workTokens[i-1] = workTokens[i-1].replace("minecraft:", "", 1)
                    try:
                        workTokens[i] = int(workTokens[i])
                        if not -1 <= workTokens[i] <= 15:
                            raise SyntaxError(u"{} is outside of range -1..15".format(workTokens[i]))
                        if workTokens[i-1] not in Globals.blockStates:
                            raise SyntaxError(u"{} is not a valid block".format(tokens[i-1]))
                        workTokens[i] = Globals.blockStates[workTokens[i-1]][workTokens[i]] if workTokens[i] != -1 else "-1"
                    except ValueError:
                        if not Globals.blockStateRe.match(workTokens[i]):
                            raise SyntaxError(u"{} is not a valid block state format".format(workTokens[i]))
                elif word[1] == '{':
                    workTokens = workTokens[:i] + [u" ".join(workTokens[i:])]
                    if workTokens[i][0] != '{':
                        raise SyntaxError(u"Token '{}' is not valid NBT: Doesn't start with '{{'".format(workTokens[i]))
                    workTokens[i], rest = getCompound(workTokens[i][1:])
                    if len(rest) > 0:
                        raise SyntaxError(u"Token '{0}{1}' is not valid NBT: Trailing data found: {1}".format(workTokens[i], rest))
                    break
                elif word[1] == ':':
                    workTokens = workTokens[:i] + [u"".join(workTokens[i:])]
                    try:
                        workTokens[i] = json.JSONDecoder().decode(workTokens[i])
                        walk(workTokens[i])
                        break
                    except ValueError, e:
                        raise SyntaxError(u"Token '{}' is not valid JSON: {}".format(workTokens[i], e))
                elif word[1] == '.':
                    pass
                else:
                    raise AssertionError(u"A Syntax '{}' is defined badly at Word '{}'.".format(synt(caller, syntax), word))
            if len(syntax) != len(workTokens):
                raise SyntaxError(u"Too many tokens: Syntax({}): '{}' Tokens({}): {}".format(len(syntax)+1, synt(caller, syntax), len(workTokens)+1, array([caller] + workTokens)))
            return syntax, dict(zip(syntax, workTokens))
        except SyntaxError, e:
            messages += u"{}\n".format(e)
    raise SyntaxError(u"Tokens:\n{}\nDon't match any of Syntaxes:\n{}\nReasons:\n{}\n".format(array([caller] + tokens), "\n".join([synt(caller, syntax) for syntax in syntaxes]), messages))


def tokenize(raw):
    ret = []
    token = u""
    doubleQ = False
    singleQ = False
    skip = False
    for ch in raw:
        if skip:
            skip = False
            token += ch
            continue
        if ch == '\\':
            skip = True
            token += ch
            continue
        if ch == '\"':
            doubleQ = not doubleQ
        elif ch == '\'':
            singleQ = not singleQ
        elif ch == ' ' and not (singleQ or doubleQ):
            ret.append(token)
            token = u""
            continue
        token += ch
    ret.append(token)
    return ret


def decide(raw):
    Globals.commandCounter += 1
    tokens = filter(lambda x: x != '', tokenize(raw.strip()))
    if not tokens:
        raise SyntaxError("An empty string was provided")
    tokens[0] = tokens[0].replace("-", "_").replace("?", "help").replace("msg", "w")
    if tokens[0] == "tell":
        tokens[0] = 'w'

    if tokens[0][0] == '/':
        tokens[0] = tokens[0][1:]

    try:
        if len(tokens) == 1:
            return eval("{}()".format(tokens[0]))
        return eval(u"{}(tokens[1:])".format(tokens[0]))
    except NameError:
        raise SyntaxError(u"{} is not a Minecraft command".format(tokens[0]))
    except TypeError:
        if len(tokens) == 1:
            raise SyntaxError(u"{} needs arguments".format(tokens[0]))
        raise SyntaxError(u"{} doesn't take any arguments".format(tokens[0]))


class NBTCompound:
    def __init__(self):
        self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, item):
        return self.data[item]

    def __unicode__(self):
        return u"{{{}}}".format(u",".join([u"{}:{}".format(key, unicode(self.data[key])) for key in self.data.keys()]))


class NBTList:
    def __init__(self):
        self.data = []

    def append(self, value):
        self.data.append(value)

    def __unicode__(self):
        return u"[{}]".format(u",".join([unicode(data) for data in self.data]))


class Selector:
    def __init__(self, raw):
        self.raw = raw
        if not Globals.selectorRe.match(raw):
            raise SyntaxError(u"\'{}\' is not a valid selector".format(raw))
        self.data = dict()

        if raw[0] == '@':
            self.target = raw[1]
            self.playerName = False
            if len(raw) > 2:
                raw = raw[3:-1]
                for token in raw.split(','):
                    key, val = token.split('=')
                    self.data[key] = val

                for key in self.data.keys():
                    if not (Globals.scoreRe.match(key) or key in Globals.selectorArgs):
                        raise SyntaxError(u"\'@{}[{}]\' is not a valid selector because: \'{}\' is not valid selector argument".format(self.target, raw, key))
        else:
            self.target = raw
            self.playerName = True

        self.at = False
        for posArg in Globals.posArgs:
            if posArg in self.data:
                self.at = True
                break

    def __unicode__(self):
        if self.playerName:
            return unicode(self.target)
        if len(self.data.keys()) == 0:
            return u"@{}".format(self.target)

        try:
            if 'x' in self.data:
                self.data['x'] = int(self.data['x']) + 0.5
        except ValueError:
            raise SyntaxError(u"x\'s value in \'{}\' has to be integer".format(self.raw, key))
        try:
            if 'z' in self.data:
                self.data['z'] = int(self.data['z']) + 0.5
        except ValueError:
            raise SyntaxError(u"z\'s value in \'{}\' has to be integer".format(self.raw, key))

        if 'm' in self.data:
            if self.data['m'] == '0' or self.data['m'] == 's':
                self.data['m'] = "survival"
            elif self.data['m'] == '1' or self.data['m'] == 'c':
                self.data['m'] = "creative"
            elif self.data['m'] == '2' or self.data['m'] == 'a':
                self.data['m'] = "adventure"
            elif self.data['m'] == '3' or self.data['m'] == 'sp':
                self.data['m'] = "spectator"
            else:
                raise SyntaxError(u"m\'s value in \'{}\' has to be in 0|1|2|3".format(self.raw, key))

        if 'c' in self.data:
            try:
                tmp = int(self.data['c'])
                if tmp == 0:
                    del self.data['c']
                elif tmp < 0:
                    self.data['c'] = -tmp
                    self.data['sort'] = 'furthest'
            except ValueError:
                raise SyntaxError(u"c\'s value in \'{}\' has to be integer".format(self.raw, key))

        return u"@{}[{}]".format(self.target, u",".join(futurizeSelector(self.data)))

    def __repr__(self):
        return unicode(self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Master:
    def __init__(self):
        self.syntax, self.data = (), {}
        self.at, self.ass = False, False

    def __unicode__(self):
        s = unicode(self.__class__.__name__).replace("_", "-")
        for key in self.syntax:
            s += u" {}".format(self.data[key] if key[1] != ':' else json.JSONEncoder(separators=(',', ':')).encode(self.data[key]))
        return s


class advancement(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(grant|revoke", "<@player", "<(only|until|from|through", "<.advancement", "[.criterion"),
                    ("<(grant|revoke", "<@player", "<(everything"),
                    ("<(test", "<@player", "<.advancement", "[.criterion"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = True, True


class ban(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.name", "[*reason"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.ass = True


class ban_ip(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.address|name", "[*reason"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)


class blockdata(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x", "<~y", "<~z", "<{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at = canAt(self.data, "<~x", "<~y", "<~z")


class clear(Master):
    def __init__(self, tokens=None):
        Master.__init__(self)
        if tokens:
            syntaxes = (("<@player", "[.item", "[0data", "[0maxCount", "[{dataTag"), )
            self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
            self.at, self.ass = self.data["<@player"].at, True

    def __unicode__(self):
        s = u"clear {}".format(self.data["<@player"])
        if "[.item" in self.data:
            s += u" {}".format(item(self.data, "[.item", "[0data", "[{dataTag"))
            if "[0maxCount" in self.data:
                s += u" {}".format(self.data["[0maxCount"])
        return s


class clone(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z", "[(masked|replace", "[(force|move|normal"),
                    ("<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z", "<(filtered", "<(force|move|normal", "<.tileName", "[=dataValue"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at = canAt(self.data, "<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z")

    def __unicode__(self):
        s = u"clone {} {} {} {} {} {} {} {} {}".format(self.data["<~x1"], self.data["<~y1"], self.data["<~z1"], self.data["<~x2"], self.data["<~y2"], self.data["<~z2"], self.data["<~x"], self.data["<~y"], self.data["<~z"])
        if "<(filtered" in self.data:
            s += u" {} {}".format(block(self.data, False, "<.tileName", "[=dataValue"), self.data["<(force|move|normal"])
        else:
            for key in self.syntax[9:]:
                s += u" {}".format(self.data[key])
        return s


class debug(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(start|stop", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)


class defaultgamemode(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(0|1|2|3|s|c|a|sp|survival|creative|adventure|spectator", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)

    def __unicode__(self):
        s = "<(0|1|2|3|s|c|a|sp|survival|creative|adventure|spectator"
        if self.data[s] == '0' or self.data[s] == 's':
            self.data[s] = "survival"
        elif self.data[s] == '1' or self.data[s] == 'c':
            self.data[s] = "creative"
        elif self.data[s] == '2' or self.data[s] == 'a':
            self.data[s] = "adventure"
        elif self.data[s] == '3' or self.data[s] == 'sp':
            self.data[s] = "spectator"

        return u"defaultgamemode {}".format(self.data[s])


class deop(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True


class difficulty(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(0|1|2|3|p|e|n|h|peaceful|easy|normal|hard", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)

    def __unicode__(self):
        s = u"<(0|1|2|3|p|e|n|h|peaceful|easy|normal|hard"
        if self.data[s] == '0' or self.data[s] == 'p':
            self.data[s] = "peaceful"
        elif self.data[s] == '1' or self.data[s] == 'e':
            self.data[s] = "easy"
        elif self.data[s] == '2' or self.data[s] == 'n':
            self.data[s] = "normal"
        elif self.data[s] == '3' or self.data[s] == 'h':
            self.data[s] = "hard"

        return u"difficulty {}".format(self.data[s])


class effect(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "<(clear"),
                    ("<@player", "<.effect", "[0seconds", "[0amplifier", "[(true|false"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True

    def __unicode__(self):
        if self.syntax[1] == "<(clear":
            return u"effect clear {}".format(self.data["<@player"])
        s = u"effect give {} {}".format(self.data["<@player"], self.data["<.effect"])
        for key in self.syntax[2:]:
            s += u" {}".format(self.data[key])
        return s


class enchant(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "<.enchantment", "[0level"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True


class entitydata(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@entity", "<{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@entity"].at, True


class execute(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@entity", "<~x", "<~y", "<~z", "<(detect", "<~x2", "<~y2", "<~z2", "<.block", "<=dataValue", "<*command"),
                    ("<@entity", "<~x", "<~y", "<~z", "<*command"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.data["<*command"] = self.data["<*command"][1:] if self.data["<*command"][0] == '/' else self.data["<*command"]
        self.data["<*command"] = decide(self.data["<*command"])
        self.at, self.ass = self.data["<*command"].at or self.data["<@entity"].at, self.data["<*command"].ass

    def __unicode__(self):
        command = unicode(self.data["<*command"])
        self.at = False if command[:7] == "execute" else self.at
        s = u""
        if not '~' == self.data["<~x"] == self.data["<~y"] == self.data["<~z"]:
            s += u" offset {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"])
            self.at = True

        if "<(detect" in self.data:
            s += u" if block {} {} {} {}".format(self.data["<~x2"], self.data["<~y2"], self.data["<~z2"], block(self.data, False, "<.block", "<=dataValue"))
            self.at = True

        if self.at and self.ass:
            s = u"execute as {} at @s{}".format(self.data["<@entity"], s)
        elif self.at and not self.ass:
            s = u"execute at {}{}".format(self.data["<@entity"], s)
        else:
            s = u"execute as {}{}".format(self.data["<@entity"], s)

        if command[0] == '#':
            s = u"#~ {} {}".format(s, command[3:])
        else:
            if command[:7] == "execute":
                s += command[7:]
            else:
                s += u" then {}".format(command)

        return s


class fill(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<.block", "[=dataValue", "[(destroy|hollow|keep|outline", "[{dataTag"),
                    ("<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<.block", "<=dataValue", "<(replace", "[.replaceTileName", "[=replaceDataValue"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at = canAt(self.data, "<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2")

    def __unicode__(self):
        s = u"fill {} {} {} {} {} {}".format(self.data["<~x1"], self.data["<~y1"], self.data["<~z1"], self.data["<~x2"], self.data["<~y2"], self.data["<~z2"])
        if "<(replace" in self.data:
            s += u" {} replace".format(block(self.data, True, "<.block", "<=dataValue"))
            if "[.replaceTileName" in self.data:
                s += u" {}".format(block(self.data, False, "[.replaceTileName", "[=replaceDataValue"))
        else:
            s += u" {}".format(block(self.data, True, "<.block", "[=dataValue", "[{dataTag"))
            if "[(destroy|hollow|keep|outline" in self.data:
                s += u" {}".format(self.data["[(destroy|hollow|keep|outline"])
        return s


class function(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.function", ),
                    ("<.function", "<(if|unless", "<@selector"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        if not Globals.functionRe.match(self.data["<.function"]):
            raise SyntaxError("Invalid format of function name: {}".format(self.data["<.function"]))
        self.at, self.ass = True, True

    def __unicode__(self):
        if not "<(if|unless" in self.data:
            return u"function {}".format(self.data["<.function"])
        return u"execute {} entity {} then function {}".format(self.data["<(if|unless"], self.data["<@selector"], self.data["<.function"])


class gamemode(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(0|1|2|3|s|c|a|sp|survival|creative|adventure|spectator", "[@player"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        if "[@player" in self.data:
            self.at, self.ass = self.data["[@player"].at, True

    def __unicode__(self):
        s = "<(0|1|2|3|s|c|a|sp|survival|creative|adventure|spectator"
        if self.data[s] == '0' or self.data[s] == 's':
            self.data[s] = "survival"
        elif self.data[s] == '1' or self.data[s] == 'c':
            self.data[s] = "creative"
        elif self.data[s] == '2' or self.data[s] == 'a':
            self.data[s] = "adventure"
        elif self.data[s] == '3' or self.data[s] == 'sp':
            self.data[s] = "spectator"

        return u"gamemode {}{}".format(self.data[s], " {}".format(self.data["[@player"]) if len(self.syntax) == 2 else "")


class gamerule(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.rule", "[.value"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)

    def __unicode__(self):
        if self.data["<.rule"] not in Globals.gamerules:
            Globals.commentedOut = True
            return u"#~ {} ||| Custom gamerules are no longer supported".format(Master.__unicode__(self))
        return Master.__unicode__(self)


class give(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "<.item", "[0amount", "[0data", "[{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True

    def __unicode__(self):
        s = u"give {} {}".format(self.data["<@player"], item(self.data, "<.item", "[0data", "[{dataTag"))

        if "[0amount" in self.data:
            s += u" {}".format(self.data["[0amount"])
        return s


class help(Master):
    def __init__(self, tokens=None):
        Master.__init__(self)
        if tokens:
            syntaxes = (("<({}".format("|".join(Globals.commands + map(str, range(1, 9)))), ), )
            self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)


class kick(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "[*reason"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True


class kill(Master):
    def __init__(self, tokens=None):
        Master.__init__(self)
        if tokens:
            syntaxes = (("<@player", ), )
            self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True


class list(Master):
    def __init__(self, tokens=None):
        Master.__init__(self)
        if tokens:
            syntaxes = (("<(uuids", ), )
            self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)


class locate(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(EndCity|Fortress|Mansion|Mineshaft|Monument|Stronghold|Temple|Village", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)


class me(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<*action", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.ass = True


class op(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True


class pardon(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@name", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True


class pardon_ip(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.address", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)


class particle(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.name", "<~x", "<~y", "<~z", "<0xd", "<0yd", "<0zd", "<0speed", "[0count", "[.mode", "[@player", "[*params"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = True, "[@player" in self.data


class playsound(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.sound", "<(master|music|record|weather|block|hostile|neutral|player|ambient|voice", "<@player"),
                    ("<.sound", "<(master|music|record|weather|block|hostile|neutral|player|ambient|voice", "<@player", "<~x", "<~y", "<~z", "[0volume", "[0pitch", "[0minimumVolume"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = ("<~x" in self.data and canAt(self.data, "<~x", "<~y", "<~z")) or self.data["<@player"].at, True


class publish(Master):
    def __init__(self):
        Master.__init__(self)


class recipe(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(give|take", "<@player", "<.name"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True


class reload(Master):
    def __init__(self):
        Master.__init__(self)


class replaceitem(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(block", "<~x", "<~y", "<~z", "<.slot", "<.item", "[0amount", "[0data", "[{dataTag"),
                    ("<(entity", "<@selector", "<.slot", "<.item", "[0amount", "[0data", "[{dataTag"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = (canAt(self.data, "<~x", "<~y", "<~z"), False) if self.syntax == "<(block" else (self.data["<@selector"].at, True)

    def __unicode__(self):
        s = u"replaceitem"
        for word in self.syntax:
            if word == "<.item":
                break
            s += u" {}".format(self.data[word])
        s += u" {}".format(item(self.data, "<.item", "[0data", "[{dataTag"))

        if "[0amount" in self.data:
            s += u" {}".format(self.data["[0amount"])

        return s


class save_all(Master):
    def __init__(self, tokens=None):
        Master.__init__(self)
        if tokens:
            syntaxes = (("<(flush", ), )
            self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)


class save_off(Master):
    def __init__(self):
        Master.__init__(self)


class save_on(Master):
    def __init__(self):
        Master.__init__(self)


class say(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<*message", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.ass = True


class scoreboard(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(objectives", "<(list"),
                    ("<(objectives", "<(add", "<.name", "<.criteria", "[*display"),
                    ("<(objectives", "<(remove", "<.name"),
                    ("<(objectives", "<(setdisplay", "<(list|sidebar|belowName|sidebar.team.black|sidebar.team.dark_blue|sidebar.team.dark_green|sidebar.team.dark_aqua|sidebar.team.dark_red|sidebar.team.dark_purple|sidebar.team.gold|sidebar.team.gray|sidebar.team.dark_gray|sidebar.team.blue|sidebar.team.green|sidebar.team.aqua|sidebar.team.red|sidebar.team.light_purple|sidebar.team.yellow|sidebar.team.white", "[(objective"),

                    ("<(players", "<(list", "[@entity"),
                    ("<(players", "<(list", "[(*"),
                    ("<(players", "<(set|add|remove", "<@entity", "<.objective", "<0score", "[{dataTag"),
                    ("<(players", "<(set|add|remove", "<(*",      "<.objective", "<0score"),
                    ("<(players", "<(reset", "<@entity", "[.objective"),
                    ("<(players", "<(reset", "<(*",      "[.objective"),
                    ("<(players", "<(enable", "<@entity", "<.trigger"),
                    ("<(players", "<(enable", "<(*",      "<.trigger"),
                    ("<(players", "<(test", "<@entity", "<.objective", "<.min", "[.max"),
                    ("<(players", "<(test", "<(*",      "<.objective", "<.min", "[.max"),
                    ("<(players", "<(operation", "<@targetName", "<.targetObjective", "<(+=|-=|*=|/=|%=|=|<|>|><", "<@selector", "<.objective"),
                    ("<(players", "<(operation", "<(*",          "<.targetObjective", "<(+=|-=|*=|/=|%=|=|<|>|><", "<@selector", "<.objective"),
                    ("<(players", "<(operation", "<@targetName", "<.targetObjective", "<(+=|-=|*=|/=|%=|=|<|>|><", "<(*",        "<.objective"),

                    ("<(players", "<(tag", "<@entity", "<(add|remove", "<.tagName", "[{dataTag"),
                    ("<(players", "<(tag", "<(*",      "<(add|remove", "<.tagName"),
                    ("<(players", "<(tag", "<@entity", "<(list"),
                    ("<(players", "<(tag", "<(*",      "<(list"),

                    ("<(teams", "<(list", "[.teamname"),
                    ("<(teams", "<(add|join", "<.name", "[*displayName"),
                    ("<(teams", "<(remove|empty", "<.name"),
                    ("<(teams", "<(leave", "[*entities"),
                    ("<(teams", "<(option", "<.team", "<(color", "<(black|dark_blue|dark_green|dark_aqua|dark_red|dark_purple|gold|gray|dark_gray|blue|green|aqua|red|light_purple|yellow|white|reset"),
                    ("<(teams", "<(option", "<.team", "<(friendlyfire|seeFriendlyInvisibles", "<(true|false"),
                    ("<(teams", "<(option", "<.team", "<(nametagVisibility|deathMessageVisibility", "<(never|hideForOtherTeams|hideForOwnTeam|always"),
                    ("<(teams", "<(option", "<.team", "<(collisionRule", "<(always|never|pushOwnTeam|pushOtherTeams"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = False, False
        for word in self.syntax:
            if word[1] == '@' or word == "[*entities":
                self.at, self.ass = self.at or self.data[word].at, True

    def __unicode__(self):
        if "[{dataTag" in self.data and "<@entity" in self.data:
            selectorCopy = Selector(unicode(self.data["<@entity"]))
            selectorCopy.data["nbt"] = u"\"{}\"".format(escape(unicode(self.data["[{dataTag"])))
            s = u"scoreboard"
            for key in self.syntax[:-1]:
                s += u" {}".format(self.data[key] if key != "<@entity" else selectorCopy)
            return s
        else:
            return Master.__unicode__(self)


class seed(Master):
    def __init__(self):
        Master.__init__(self)


class setblock(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x", "<~y", "<~z", "<.block", "[=dataValue", "[(destroy|keep|replace", "[{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at = canAt(self.data, "<~x", "<~y", "<~z")

    def __unicode__(self):
        s = u"setblock {} {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"], block(self.data, True, "<.block", "[=dataValue", "[{dataTag"))
        if "[(destroy|keep|replace" in self.data:
            s += u" {}".format(self.data["[(destroy|keep|replace"])
        return s


class setidletimeout(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<0minutes", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)


class setworldspawn(Master):
    def __init__(self, tokens=None):
        Master.__init__(self)
        if tokens:
            syntaxes = (("<~x", "<~y", "<~z", ), )
            self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at = canAt(self.data, "<~x", "<~y", "<~z")


class spawnpoint(Master):
    def __init__(self, tokens=None):
        Master.__init__(self)
        if tokens:
            syntaxes = (("<@player", ),
                        ("<@player", "<~x", "<~y", "<~z"))
            self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = "<~x" not in self.data or canAt(self.data, "<~x", "<~y", "<~z"), True


class spreadplayers(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x", "<~z", "<0spreadDistance", "<0maxRange", "<(true|false", "<*player"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = True, True


class stats(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        self.stat = "<({}".format("|".join(Globals.statTags))
        syntaxes = (("<(block", "<~x", "<~y", "<~z", "<(clear", self.stat),
                    ("<(block", "<~x", "<~y", "<~z", "<(set", self.stat, "<@selector", "<.objective"),
                    ("<(entity", "<@selector2", "<(clear", self.stat),
                    ("<(entity", "<@selector2", "<(set", self.stat, "<@selector", "<.objective"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = True, True

    def __unicode__(self):
        Globals.commentedOut = True
        if "<(clear" in self.data:
            return u"#~ {} ||| Clearing a stat is no longer needed".format(Master.__unicode__(self))
        return u"#~ {} ||| Use \'execute store {} {} {} COMMAND\' on the commands that you want the stats from".format(Master.__unicode__(self), "success" if self.data[self.stat] == "SuccessCount" else "result", self.data["<@selector"], self.data["<.objective"])


class stop(Master):
    def __init__(self):
        Master.__init__(self)


class stopsound(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "[(master|music|record|weather|block|hostile|neutral|player|ambient|voice", "[.sound"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True


class summon(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.entity_name", ),
                    ("<.entity_name", "<~x", "<~y", "<~z", "[{dataTag"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at = "<~x" not in self.data or canAt(self.data, "<~x", "<~y", "<~z")


class teleport(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@target", "<~x", "<~y", "<~z"),
                    ("<@target", "<~x", "<~y", "<~z", "<~y-rot", "<~x-rot"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = canAt(self.data, "<~x", "<~y", "<~z", "<~y-rot", "<~x-rot"), True

        if self.data["<@target"] == Selector("@s"):
            self.syntax = self.syntax[1:]

    def __unicode__(self):
        return Master.__unicode__(self).replace("teleport", "tp", 1)


class tellraw(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "<:raw"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True


class testfor(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "[{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True

    def __unicode__(self):
        if "[{dataTag" in self.data:
            selectorCopy = Selector(unicode(self.data["<@player"]))
            selectorCopy.data["nbt"] = u"\"{}\"".format(escape(unicode(self.data["[{dataTag"])))

        return u"execute if entity {}".format(selectorCopy if "[{dataTag" in self.data else self.data["<@player"])


class testforblock(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x", "<~y", "<~z", "<.block", "[=dataValue", "[{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at = canAt(self.data, "<~x", "<~y", "<~z")

    def __unicode__(self):
        return u"execute if block {} {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"], block(self.data, False, "<.block", "[=dataValue", "[{dataTag"))


class testforblocks(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z", "[(all|masked"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at = canAt(self.data, "<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z")

    def __unicode__(self):
        return u"execute if blocks {} {} {} {} {} {} {} {} {} {}".format(self.data["<~x1"], self.data["<~y1"], self.data["<~z1"], self.data["<~x2"], self.data["<~y2"], self.data["<~z2"], self.data["<~x"], self.data["<~y"], self.data["<~z"], self.data["[(all|masked"] if "[(all|masked" in self.data else "all")


class time(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(add|set", "<0value"),
                    ("<(query", "<(daytime|gametime|day"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)


class title(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "<(clear|reset"),
                    ("<@player", "<(title|subtitle|actionbar", "<:raw"),
                    ("<@player", "<(times", "<0fadeIn", "<0stay", "<0fadeOut"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True


class toggledownfall(Master):
    def __init__(self):
        Master.__init__(self)

    def __unicode__(self):
        Globals.commentedOut = True
        return u"#~ toggledownfall ||| This command was removed"


class tp(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x", "<~y", "<~z"),
                    ("<~x", "<~y", "<~z", "<~yaw", "<~pitch"),
                    ("<@target", "[@destination"),
                    ("<@target", "<~x", "<~y", "<~z"),
                    ("<@target", "<~x", "<~y", "<~z", "<~yaw", "<~pitch"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = False if len(self.syntax) < 3 else canAt(self.data, "<~x", "<~y", "<~z", "<~yaw", "<~pitch"), True

    def __unicode__(self):
        if "<@target" not in self.data or (not self.data["<@target"].playerName and self.data["<@target"].target == 's') or "[@destination" in self.data:
            return Master.__unicode__(self)

        s = u"execute as {}{} teleport {} {} {}".format(self.data["<@target"], u" at @s" if self.at else u"", self.data["<~x"], self.data["<~y"], self.data["<~z"])

        if "<~yaw" in self.data:
            s += u" {} {}".format(self.data["<~yaw"], self.data["<~pitch"])

        return s


class trigger(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.objective", "<(add|set", "<0value"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.ass = True


class w(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "<*message"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = self.data["<@player"].at, True


class weather(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(clear|rain|thunder", "[0duration"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)


class whitelist(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(add|remove", "<@player"),
                    ("<(on|off|list|reload", ))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        if "<@player" in self.data:
            self.at, self.ass = self.data["<@player"].at, True


class worldborder(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(add|set", "<0distance", "[0time"),
                    ("<(center", "<~x", "<~z"),
                    ("<(damage", "<(amount", "<0damagePerBlock"),
                    ("<(damage", "<(buffer", "<0distance"),
                    ("<(get", ),
                    ("<(warning", "<(distance", "<0distance"),
                    ("<(warning", "<(time", "<0time"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at = "<~x" in self.data and canAt(self.data, "<~x", "<~z")


class xp(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<%amount", "[@player"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.at, self.ass = "[@player" in self.data and self.data["[@player"].at, True

    def __unicode__(self):
        if self.data["<%amount"][-1] == 'L':
            return u"experience add {} {} levels".format(self.data["[@player"], self.data["<%amount"][:-1])
        return u"experience add {} {}".format(self.data["[@player"], self.data["<%amount"])


if __name__ == "__main__":
    start = getTime()
    failedFiles = []
    commentedOutFiles = []
    tmpFiles = []
    manual = False
    Globals.fileCounter = 0

    def convertFile(fileName):
        Globals.fileCounter += 1
        with codecs.open(fileName, 'r', "utf-8") as f:
            lines = f.readlines()
        try:
            for lineNumber, line in enumerate(lines):
                line = line.rstrip()
                if len(line):
                    start = len(line) - len(line.lstrip())
                    if line[start] == '#':
                        continue
                    Globals.commentedOut = False
                    lines[lineNumber] = u"{}{}\n".format(line[:start], unicode(decide(line)))
                    if Globals.commentedOut:
                        commentedOutFiles.append((fileName, lineNumber))
        except SyntaxError as ex:
            print "File: {}\nLine {}:\n{}".format(fileName, lineNumber + 1, ex)
            return fileName
        with codecs.open(u"{}.TheAl_T".format(fileName), 'w', "utf-8") as f:
            f.writelines(lines)

    try:
        if sys.argv[1:]:
            for fileName in sys.argv[1:]:
                ret = convertFile(fileName)
                if ret:
                    failedFiles.append(ret)
                else:
                    tmpFiles.append(u"{}.TheAl_T".format(fileName))
        else:
            choice = raw_input("No filenames on the command line, entering menu:\n1 - Convert all files in this folder\n2 - Convert all files in this folder recursively\n3 - Do Data Pack stuff\n4 - Remove .TheAl_T files\nelse - Convert one command here\n\n")
            if choice.strip() in ('1', '2', '3', '4'):
                print ''
                if choice.strip() == '1':
                    for fileName in [f for f in os.listdir(u'.') if not os.path.isdir(f)]:
                        if fileName.endswith(".mcfunction"):
                            ret = convertFile(fileName)
                            if ret:
                                failedFiles.append(ret)
                            else:
                                tmpFiles.append(u"{}.TheAl_T".format(fileName))

                elif choice.strip() == '2':
                    for root, _, files in os.walk(u"."):
                        for fileName in files:
                            if fileName.endswith(".mcfunction"):
                                ret = convertFile(os.path.join(root, fileName))
                                if ret:
                                    failedFiles.append(ret)
                                else:
                                    tmpFiles.append(u"{}.TheAl_T".format(os.path.join(root, fileName)))

                elif choice.strip() == '3':
                    relative = u""
                    found = False
                    currDir = None
                    path = os.getcwdu().split(os.sep)
                    while len(path) >= 2:
                        relative += u"..{}".format(os.sep)
                        currDir = path.pop()
                        currDirFiles = [_ for _ in os.listdir(relative + currDir)]
                        if path[-1] == "saves" and all(map(lambda x: x in currDirFiles, ("advancements", "data", "DIM1", "DIM-1", "icon.png", "level.dat", "level.dat_old", "playerdata", "region", "session.lock", "stats"))):
                            print "Found world directory: " + currDir
                            os.chdir(u"{}{}".format(relative, currDir))
                            found = True
                            break

                    if not found:
                        found = 'y' == raw_input(u"Unable to find the world directory. If you are sure this: \'{}\' is a world directory, press \'y\' to continue: ".format(os.getcwdu())).lower()

                    if found:
                        with open("data{}pack.mcmeta".format(os.sep), 'w') as f:
                            f.write("{\n\t\"pack\":{\n\t\t\"pack_format\":3,\n\t\t\"description\":\"Made using TheAl_T\'s 1.12 to 1.13 converter\"\n\t}\n}\n")

                        for what in (u"advancements", u"functions", u"loot_tables"):
                            if os.path.isdir(u"data{}{}".format(os.sep, what)):
                                print u"Found {}".format(what)
                                for namespace in os.listdir(u"data{}{}".format(os.sep, what)):
                                    if os.path.isdir(u"data{0}{2}{0}{1}".format(os.sep, namespace, what)):
                                        if not os.path.isdir(u"data{0}{1}{0}{2}".format(os.sep, namespace, what)):
                                            os.makedirs(u"data{0}{1}{0}{2}".format(os.sep, namespace, what))
                                        for f in os.listdir(u"data{0}{2}{0}{1}".format(os.sep, namespace, what)):
                                            shutil.move(u"data{0}{2}{0}{1}{0}{3}".format(os.sep, namespace, what, f),
                                                        u"data{0}{1}{0}{2}".format(os.sep, namespace, what))
                                        os.removedirs(u"data{0}{2}{0}{1}".format(os.sep, namespace, what))

                        if os.path.isdir(u"structures"):
                            print u"Found structures"
                            if not os.path.isdir(u"data{0}minecraft{0}structures".format(os.sep)):
                                os.makedirs(u"data{0}minecraft{0}structures".format(os.sep))
                            for f in os.listdir(u"structures"):
                                shutil.move(u"structures{0}{1}".format(os.sep, f), u"data{0}minecraft{0}structures".format(os.sep))
                            os.rmdir(u"structures")

                    raw_input("\nDone\n\nPress Enter to exit...")
                    exit(0)

                else:
                    for root, _, files in os.walk(u"."):
                        for fileName in files:
                            if fileName.endswith(".TheAl_T"):
                                os.remove(os.path.join(root, fileName))
                    raw_input("\nDone\n\nPress Enter to exit...")
                    exit(0)
            else:
                manual = True
                print u"\n{}\n".format(decide(raw_input("Input your command here:\n")))
    except SyntaxError, e:
        print u"\n{}\n".format(e)

    if not manual:
        if failedFiles:
            for tmp in tmpFiles:
                os.remove(tmp)
            raw_input(u"List of files that failed: \"{}\"\n\nConverting aborted.\n\nPress Enter to exit...".format(u"\" \"".join(failedFiles)))
        else:
            for tmp in tmpFiles:
                os.remove(tmp[:-8])
                os.rename(tmp, tmp[:-8])
            if commentedOutFiles:
                print u"Some commands were commented out because they have to be converted manually:\n{}".format(u"\n".join(map(lambda x: u"File: {}, Line: {}".format(x[0], x[1]), commentedOutFiles)))
            raw_input("A total of {} commands, across {} files, was converted in {} seconds\n\nPress Enter to exit...".format(Globals.commandCounter, Globals.fileCounter, getTime() - start))
    else:
        raw_input("Press Enter to exit...")
