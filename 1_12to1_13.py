#! /usr/bin/env python
# coding=utf-8

# Made by TheAl_T
# HUGE thanks to Onnowhere for block state database and conversion and for testing and feedback

# TheAl_T: planetminecraft.com/member/theal_t
# Onnowhere: youtube.com/onnowhere2

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

Globals = type("Dummy", (object, ), {})
Globals.commandCounter = 0
Globals.commentedOut = False
Globals.posArgs = ("x", "y", "z", "dx", "dy", "dz", "r", "rm", "c")
Globals.statTags = ("AffectedBlocks", "AffectedEntities", "AffectedItems", "QueryResult", "SuccessCount")
Globals.selectorArgs = ("x", "y", "z", "dx", "dy", "dz", "type", "lm", "l", "m", "team", "score", "name", "tag", "nbt", "rm", "r", "rxm", "rx", "rym", "ry", "c")
Globals.selectorArgsNew = (("x", "x", "x"), ("y", "y", "y"), ("z", "z", "z"), ("dx", "dx", "dx"), ("dy", "dy", "dy"), ("dz", "dz", "dz"), ("type", "type", "type"), ("level", "lm", "l"), ("gamemode", "m", "m"), ("team", "team", "team"), ("scores", "score", "score"), ("name", "name", "name"), ("tag", "tag", "tag"), ("advancements", "advancements", "advancements"), ("nbt", "nbt", "nbt"), ("distance", "rm", "r"), ("x_rotation", "rxm", "rx"), ("y_rotation", "rym", "ry"), ("limit", "c", "c"), ("sort", "sort", "sort"))
Globals.gamerules = ("announceAdvancements", "commandBlockOutput", "disableElytraMovementCheck", "doDaylightCycle", "doEntityDrops", "doFireTick", "doLimitedCrafting", "doMobLoot", "doMobSpawning", "doTileDrops", "doWeatherCycle", "gameLoopFunction", "keepInventory", "logAdminCommands", "maxCommandChainLength", "maxEntityCramming", "mobGriefing", "naturalRegeneration", "randomTickSpeed", "reducedDebugInfo", "sendCommandFeedback", "showDeathMessages", "spawnRadius", "spectatorsGenerateChunks")
Globals.commands = ["advancement", "ban", "ban-ip", "blockdata", "clear", "clone", "debug", "defaultgamemode", "deop", "difficulty", "effect", "enchant", "entitydata", "execute", "fill", "function", "gamemode", "gamerule", "give", "help", "?", "kick", "kill", "list", "locate", "me", "msg", "op", "pardon", "pardon-ip", "particle", "playsound", "publish", "recipe", "reload", "replaceitem", "save-all", "save-off", "save-on", "say", "scoreboard", "seed", "setblock", "setidletimeout", "setworldspawn", "spawnpoint", "spreadplayers", "stats", "stop", "stopsound", "summon", "teleport", "tell", "tellraw", "testfor", "testforblock", "testforblocks", "time", "title", "toggledownfall", "tp", "trigger", "w", "weather", "whitelist", "worldborder", "xp"]
Globals.summons = ("item", "xp_orb", "area_effect_cloud", "leash_knot", "painting", "item_frame", "armor_stand", "evocation_fangs", "ender_crystal", "egg", "arrow", "snowball", "fireball", "small_fireball", "ender_pearl", "eye_of_ender_signal", "potion", "xp_bottle", "wither_skull", "fireworks_rocket", "spectral_arrow", "shulker_bullet", "dragon_fireball", "llama_spit", "tnt", "falling_block", "commandblock_minecart", "boat", "minecart", "chest_minecart", "furnace_minecart", "tnt_minecart", "hopper_minecart", "spawner_minecart", "elder_guardian", "wither_skeleton", "stray", "husk", "zombie_villager", "evocation_illager", "vex", "vindication_illager", "illusion_illager", "creeper", "skeleton", "spider", "giant", "zombie", "slime", "ghast", "zombie_pigman", "enderman", "cave_spider", "silverfish", "blaze", "magma_cube", "ender_dragon", "wither", "witch", "endermite", "guardian", "shulker", "skeleton_horse", "zombie_horse", "donkey", "mule", "bat", "pig", "sheep", "cow", "chicken", "squid", "wolf", "mooshroom", "snowman", "ocelot", "villager_golem", "horse", "rabbit", "polar_bear", "llama", "parrot", "villager", "lightning_bolt")
Globals.particles = ("angryVillager", "barrier", "blockcrack", "blockdust", "bubble", "cloud", "crit", "damageIndicator", "depthsuspend", "dragonbreath", "dripLava", "dripWater", "droplet", "enchantmenttable", "endRod", "explode", "fallingdust", "fireworksSpark", "flame", "footstep", "happyVillager", "heart", "hugeexplosion", "iconcrack", "instantSpell", "largeexplode", "largesmoke", "lava", "magicCrit", "mobappearance", "mobSpell", "mobSpellAmbient", "note", "portal", "reddust", "slime", "smoke", "snowballpoof", "snowshovel", "spell", "spit", "splash", "suspended", "sweepAttack", "take", "totem", "townaura", "wake", "witchMagic")
Globals.data2states = {
    "air": {},
    "stone": {
        0: "variant=stone",
        1: "variant=granite",
        2: "variant=smooth_granite",
        3: "variant=diorite",
        4: "variant=smooth_diorite",
        5: "variant=andesite",
        6: "variant=smooth_andesite"},
    "grass": {},
    "dirt": {
        0: "variant=dirt",
        1: "variant=coarse_dirt",
        2: "variant=podzol"},
    "cobblestone": {},
    "planks": {
        0: "variant=oak",
        1: "variant=spruce",
        2: "variant=birch",
        3: "variant=jungle",
        4: "variant=acacia",
        5: "variant=dark_oak",
        6: "variant=oak",
        7: "variant=oak",
        8: "variant=oak",
        9: "variant=oak",
        10: "variant=oak",
        11: "variant=oak",
        12: "variant=oak",
        13: "variant=oak",
        14: "variant=oak",
        15: "variant=oak"},
    "sapling": {
        0: "stage=0,type=oak",
        1: "stage=0,type=spruce",
        2: "stage=0,type=birch",
        3: "stage=0,type=jungle",
        4: "stage=0,type=acacia",
        5: "stage=0,type=dark_oak",
        6: "stage=0,type=oak",
        7: "stage=0,type=oak",
        8: "stage=1,type=oak",
        9: "stage=1,type=spruce",
        10: "stage=1,type=birch",
        11: "stage=1,type=jungle",
        12: "stage=1,type=acacia",
        13: "stage=1,type=dark_oak",
        14: "stage=1,type=oak",
        15: "stage=1,type=oak"},
    "bedrock": {},
    "flowing_water": {
        0: "level=0",
        1: "level=1",
        2: "level=2",
        3: "level=3",
        4: "level=4",
        5: "level=5",
        6: "level=6",
        7: "level=7",
        8: "level=8",
        9: "level=9",
        10: "level=10",
        11: "level=11",
        12: "level=12",
        13: "level=13",
        14: "level=14",
        15: "level=15"},
    "water": {
        0: "level=0",
        1: "level=1",
        2: "level=2",
        3: "level=3",
        4: "level=4",
        5: "level=5",
        6: "level=6",
        7: "level=7",
        8: "level=8",
        9: "level=9",
        10: "level=10",
        11: "level=11",
        12: "level=12",
        13: "level=13",
        14: "level=14",
        15: "level=15"},
    "flowing_lava": {
        0: "level=0",
        1: "level=1",
        2: "level=2",
        3: "level=3",
        4: "level=4",
        5: "level=5",
        6: "level=6",
        7: "level=7",
        8: "level=8",
        9: "level=9",
        10: "level=10",
        11: "level=11",
        12: "level=12",
        13: "level=13",
        14: "level=14",
        15: "level=15"},
    "lava": {
        0: "level=0",
        1: "level=1",
        2: "level=2",
        3: "level=3",
        4: "level=4",
        5: "level=5",
        6: "level=6",
        7: "level=7",
        8: "level=8",
        9: "level=9",
        10: "level=10",
        11: "level=11",
        12: "level=12",
        13: "level=13",
        14: "level=14",
        15: "level=15"},
    "sand": {
        0: "type=sand",
        1: "type=red_sand"},
    "gravel": {},
    "gold_ore": {},
    "iron_ore": {},
    "coal_ore": {},
    "log": {
        0: "axis=y,variant=oak",
        1: "axis=y,variant=spruce",
        2: "axis=y,variant=birch",
        3: "axis=y,variant=jungle",
        4: "axis=x,variant=oak",
        5: "axis=x,variant=spruce",
        6: "axis=x,variant=birch",
        7: "axis=x,variant=jungle",
        8: "axis=z,variant=oak",
        9: "axis=z,variant=spruce",
        10: "axis=z,variant=birch",
        11: "axis=z,variant=jungle",
        12: "axis=none,variant=oak",
        13: "axis=none,variant=spruce",
        14: "axis=none,variant=birch",
        15: "axis=none,variant=jungle"},
    "leaves": {
        0: "check_decay=false,decayable=true,variant=oak",
        1: "check_decay=false,decayable=true,variant=spruce",
        2: "check_decay=false,decayable=true,variant=birch",
        3: "check_decay=false,decayable=true,variant=jungle",
        4: "check_decay=false,decayable=false,variant=oak",
        5: "check_decay=false,decayable=false,variant=spruce",
        6: "check_decay=false,decayable=false,variant=birch",
        7: "check_decay=false,decayable=false,variant=jungle",
        8: "check_decay=true,decayable=true,variant=oak",
        9: "check_decay=true,decayable=true,variant=spruce",
        10: "check_decay=true,decayable=true,variant=birch",
        11: "check_decay=true,decayable=true,variant=jungle",
        12: "check_decay=true,decayable=false,variant=oak",
        13: "check_decay=true,decayable=false,variant=spruce",
        14: "check_decay=true,decayable=false,variant=birch",
        15: "check_decay=true,decayable=false,variant=jungle"},
    "sponge": {
        0: "wet=false",
        1: "wet=true",
        2: "wet=false",
        3: "wet=true",
        4: "wet=false",
        5: "wet=true",
        6: "wet=false",
        7: "wet=true",
        8: "wet=false",
        9: "wet=true",
        10: "wet=false",
        11: "wet=true",
        12: "wet=false",
        13: "wet=true",
        14: "wet=false",
        15: "wet=true"},
    "glass": {},
    "lapis_ore": {},
    "lapis_block": {},
    "dispenser": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=down",
        9: "facing=up",
        10: "facing=north",
        11: "facing=south",
        12: "facing=west",
        13: "facing=east",
        14: "facing=down",
        15: "facing=up"},
    "sandstone": {
        0: "type=sandstone",
        1: "type=chiseled_sandstone",
        2: "type=smooth_sandstone"},
    "noteblock": {},
    "bed": {
        0: "facing=south,part=foot",
        1: "facing=west,part=foot",
        2: "facing=north,part=foot",
        3: "facing=east,part=foot",
        4: "facing=south,part=foot",
        5: "facing=west,part=foot",
        6: "facing=north,part=foot",
        7: "facing=east,part=foot",
        8: "facing=south,occupied=false,part=head",
        9: "facing=west,occupied=false,part=head",
        10: "facing=north,occupied=false,part=head",
        11: "facing=east,occupied=false,part=head",
        12: "facing=south,occupied=true,part=head",
        13: "facing=west,occupied=true,part=head",
        14: "facing=north,occupied=true,part=head",
        15: "facing=east,occupied=true,part=head"},
    "golden_rail": {
        0: "powered=false,shape=north_south",
        1: "powered=false,shape=east_west",
        2: "powered=false,shape=ascending_east",
        3: "powered=false,shape=ascending_west",
        4: "powered=false,shape=ascending_north",
        5: "powered=false,shape=ascending_south",
        8: "powered=true,shape=north_south",
        9: "powered=true,shape=east_west",
        10: "powered=true,shape=ascending_east",
        11: "powered=true,shape=ascending_west",
        12: "powered=true,shape=ascending_north",
        13: "powered=true,shape=ascending_south"},
    "detector_rail": {
        0: "powered=false,shape=north_south",
        1: "powered=false,shape=east_west",
        2: "powered=false,shape=ascending_east",
        3: "powered=false,shape=ascending_west",
        4: "powered=false,shape=ascending_north",
        5: "powered=false,shape=ascending_south",
        8: "powered=true,shape=north_south",
        9: "powered=true,shape=east_west",
        10: "powered=true,shape=ascending_east",
        11: "powered=true,shape=ascending_west",
        12: "powered=true,shape=ascending_north",
        13: "powered=true,shape=ascending_south"},
    "sticky_piston": {
        0: "extended=false,facing=down",
        1: "extended=false,facing=up",
        2: "extended=false,facing=north",
        3: "extended=false,facing=south",
        4: "extended=false,facing=west",
        5: "extended=false,facing=east",
        8: "extended=true,facing=down",
        9: "extended=true,facing=up",
        10: "extended=true,facing=north",
        11: "extended=true,facing=south",
        12: "extended=true,facing=west",
        13: "extended=true,facing=east"},
    "web": {},
    "tallgrass": {
        0: "type=dead_bush",
        1: "type=tall_grass",
        2: "type=fern",
        3: "type=dead_bush",
        4: "type=dead_bush",
        5: "type=dead_bush",
        6: "type=dead_bush",
        7: "type=dead_bush",
        8: "type=dead_bush",
        9: "type=dead_bush",
        10: "type=dead_bush",
        11: "type=dead_bush",
        12: "type=dead_bush",
        13: "type=dead_bush",
        14: "type=dead_bush",
        15: "type=dead_bush"},
    "deadbush": {},
    "piston": {
        0: "extended=false,facing=down",
        1: "extended=false,facing=up",
        2: "extended=false,facing=north",
        3: "extended=false,facing=south",
        4: "extended=false,facing=west",
        5: "extended=false,facing=east",
        8: "extended=true,facing=down",
        9: "extended=true,facing=up",
        10: "extended=true,facing=north",
        11: "extended=true,facing=south",
        12: "extended=true,facing=west",
        13: "extended=true,facing=east"},
    "piston_head": {
        0: "facing=down,type=normal",
        1: "facing=up,type=normal",
        2: "facing=north,type=normal",
        3: "facing=south,type=normal",
        4: "facing=west,type=normal",
        5: "facing=east,type=normal",
        8: "facing=down,type=sticky",
        9: "facing=up,type=sticky",
        10: "facing=north,type=sticky",
        11: "facing=south,type=sticky",
        12: "facing=west,type=sticky",
        13: "facing=east,type=sticky"},
    "wool": {
        0: "color=white",
        1: "color=orange",
        2: "color=magenta",
        3: "color=light_blue",
        4: "color=yellow",
        5: "color=lime",
        6: "color=pink",
        7: "color=gray",
        8: "color=silver",
        9: "color=cyan",
        10: "color=purple",
        11: "color=blue",
        12: "color=brown",
        13: "color=green",
        14: "color=red",
        15: "color=black"},
    "piston_extension": {
        0: "facing=down,type=normal",
        1: "facing=up,type=normal",
        2: "facing=north,type=normal",
        3: "facing=south,type=normal",
        4: "facing=west,type=normal",
        5: "facing=east,type=normal",
        8: "facing=down,type=sticky",
        9: "facing=up,type=sticky",
        10: "facing=north,type=sticky",
        11: "facing=south,type=sticky",
        12: "facing=west,type=sticky",
        13: "facing=east,type=sticky"},
    "yellow_flower": {},
    "red_flower": {
        0: "type=poppy",
        1: "type=blue_orchid",
        2: "type=allium",
        3: "type=houstonia",
        4: "type=red_tulip",
        5: "type=orange_tulip",
        6: "type=white_tulip",
        7: "type=pink_tulip",
        8: "type=oxeye_daisy"},
    "brown_mushroom": {},
    "red_mushroom": {},
    "gold_block": {},
    "iron_block": {},
    "double_stone_slab": {
        0: "seamless=false,variant=stone",
        1: "seamless=false,variant=sandstone",
        2: "seamless=false,variant=wood_old",
        3: "seamless=false,variant=cobblestone",
        4: "seamless=false,variant=brick",
        5: "seamless=false,variant=stone_brick",
        6: "seamless=false,variant=nether_brick",
        7: "seamless=false,variant=quartz",
        8: "seamless=true,variant=stone",
        9: "seamless=true,variant=sandstone",
        10: "seamless=true,variant=wood_old",
        11: "seamless=true,variant=cobblestone",
        12: "seamless=true,variant=brick",
        13: "seamless=true,variant=stone_brick",
        14: "seamless=true,variant=nether_brick",
        15: "seamless=true,variant=quartz"},
    "stone_slab": {
        0: "half=bottom,variant=stone",
        1: "half=bottom,variant=sandstone",
        2: "half=bottom,variant=wood_old",
        3: "half=bottom,variant=cobblestone",
        4: "half=bottom,variant=brick",
        5: "half=bottom,variant=stone_brick",
        6: "half=bottom,variant=nether_brick",
        7: "half=bottom,variant=quartz",
        8: "half=top,variant=stone",
        9: "half=top,variant=sandstone",
        10: "half=top,variant=wood_old",
        11: "half=top,variant=cobblestone",
        12: "half=top,variant=brick",
        13: "half=top,variant=stone_brick",
        14: "half=top,variant=nether_brick",
        15: "half=top,variant=stone"},
    "brick_block": {},
    "tnt": {
        0: "explode=false",
        1: "explode=true",
        2: "explode=false",
        3: "explode=true",
        4: "explode=false",
        5: "explode=true",
        6: "explode=false",
        7: "explode=true",
        8: "explode=false",
        9: "explode=true",
        10: "explode=false",
        11: "explode=true",
        12: "explode=false",
        13: "explode=true",
        14: "explode=false",
        15: "explode=true"},
    "bookshelf": {},
    "mossy_cobblestone": {},
    "obsidian": {},
    "torch": {
        0: "facing=up",
        1: "facing=east",
        2: "facing=west",
        3: "facing=south",
        4: "facing=north"},
    "fire": {
        0: "age=0",
        1: "age=1",
        2: "age=2",
        3: "age=3",
        4: "age=4",
        5: "age=5",
        6: "age=6",
        7: "age=7",
        8: "age=8",
        9: "age=9",
        10: "age=10",
        11: "age=11",
        12: "age=12",
        13: "age=13",
        14: "age=14",
        15: "age=15"},
    "mob_spawner": {},
    "oak_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "chest": {
        0: "facing=north",
        1: "facing=north",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=north",
        7: "facing=north",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=north",
        13: "facing=north",
        14: "facing=north",
        15: "facing=south"},
    "redstone_wire": {
        0: "power=0",
        1: "power=1",
        2: "power=2",
        3: "power=3",
        4: "power=4",
        5: "power=5",
        6: "power=6",
        7: "power=7",
        8: "power=8",
        9: "power=9",
        10: "power=10",
        11: "power=11",
        12: "power=12",
        13: "power=13",
        14: "power=14",
        15: "power=15"},
    "diamond_ore": {},
    "diamond_block": {},
    "crafting_table": {},
    "wheat": {
        0: "age=0",
        1: "age=1",
        2: "age=2",
        3: "age=3",
        4: "age=4",
        5: "age=5",
        6: "age=6",
        7: "age=7"},
    "farmland": {
        0: "moisture=0",
        1: "moisture=1",
        2: "moisture=2",
        3: "moisture=3",
        4: "moisture=4",
        5: "moisture=5",
        6: "moisture=6",
        7: "moisture=7",
        8: "moisture=0",
        9: "moisture=1",
        10: "moisture=2",
        11: "moisture=3",
        12: "moisture=4",
        13: "moisture=5",
        14: "moisture=6",
        15: "moisture=7"},
    "furnace": {
        0: "facing=north",
        1: "facing=north",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=north",
        7: "facing=north",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=north",
        13: "facing=north",
        14: "facing=north",
        15: "facing=south"},
    "lit_furnace": {
        0: "facing=north",
        1: "facing=north",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=north",
        7: "facing=north",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=north",
        13: "facing=north",
        14: "facing=north",
        15: "facing=south"},
    "standing_sign": {
        0: "rotation=0",
        1: "rotation=1",
        2: "rotation=2",
        3: "rotation=3",
        4: "rotation=4",
        5: "rotation=5",
        6: "rotation=6",
        7: "rotation=7",
        8: "rotation=8",
        9: "rotation=9",
        10: "rotation=10",
        11: "rotation=11",
        12: "rotation=12",
        13: "rotation=13",
        14: "rotation=14",
        15: "rotation=15"},
    "wooden_door": {
        0: "facing=east,half=lower,hinge=left,open=false,powered=false",
        1: "facing=south,half=lower,hinge=left,open=false,powered=false",
        2: "facing=west,half=lower,hinge=left,open=false,powered=false",
        3: "facing=north,half=lower,hinge=left,open=false,powered=false",
        4: "facing=east,half=lower,hinge=left,open=true,powered=false",
        5: "facing=south,half=lower,hinge=left,open=true,powered=false",
        6: "facing=west,half=lower,hinge=left,open=true,powered=false",
        7: "facing=north,half=lower,hinge=left,open=true,powered=false",
        8: "half=upper,hinge=left,powered=false",
        9: "half=upper,hinge=right,powered=false",
        10: "half=upper,hinge=left,powered=true",
        11: "half=upper,hinge=right,powered=true",
        12: "half=upper,hinge=left,powered=false",
        13: "half=upper,hinge=right,powered=false",
        14: "half=upper,hinge=left,powered=true",
        15: "half=upper,hinge=right,powered=true"},
    "ladder": {
        0: "facing=north",
        1: "facing=north",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=north",
        7: "facing=north",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=north",
        13: "facing=north",
        14: "facing=north",
        15: "facing=south"},
    "rail": {
        0: "shape=north_south",
        1: "shape=east_west",
        2: "shape=ascending_east",
        3: "shape=ascending_west",
        4: "shape=ascending_north",
        5: "shape=ascending_south",
        6: "shape=south_east",
        7: "shape=south_west",
        8: "shape=north_west",
        9: "shape=north_east"},
    "stone_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "wall_sign": {
        0: "facing=north",
        1: "facing=north",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=north",
        7: "facing=north",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=north",
        13: "facing=north",
        14: "facing=north",
        15: "facing=south"},
    "lever": {
        0: "facing=down_x,powered=false",
        1: "facing=east,powered=false",
        2: "facing=west,powered=false",
        3: "facing=south,powered=false",
        4: "facing=north,powered=false",
        5: "facing=up_z,powered=false",
        6: "facing=up_x,powered=false",
        7: "facing=down_z,powered=false",
        8: "facing=down_x,powered=true",
        9: "facing=east,powered=true",
        10: "facing=west,powered=true",
        11: "facing=south,powered=true",
        12: "facing=north,powered=true",
        13: "facing=up_z,powered=true",
        14: "facing=up_x,powered=true",
        15: "facing=down_z,powered=true"},
    "stone_pressure_plate": {
        0: "powered=false",
        1: "powered=true"},
    "iron_door": {
        0: "facing=east,half=lower,hinge=left,open=false,powered=false",
        1: "facing=south,half=lower,hinge=left,open=false,powered=false",
        2: "facing=west,half=lower,hinge=left,open=false,powered=false",
        3: "facing=north,half=lower,hinge=left,open=false,powered=false",
        4: "facing=east,half=lower,hinge=left,open=true,powered=false",
        5: "facing=south,half=lower,hinge=left,open=true,powered=false",
        6: "facing=west,half=lower,hinge=left,open=true,powered=false",
        7: "facing=north,half=lower,hinge=left,open=true,powered=false",
        8: "half=upper,hinge=left,powered=false",
        9: "half=upper,hinge=right,powered=false",
        10: "half=upper,hinge=left,powered=true",
        11: "half=upper,hinge=right,powered=true",
        12: "half=upper,hinge=left,powered=false",
        13: "half=upper,hinge=right,powered=false",
        14: "half=upper,hinge=left,powered=true",
        15: "half=upper,hinge=right,powered=true"},
    "wooden_pressure_plate": {
        0: "powered=false",
        1: "powered=true"},
    "redstone_ore": {},
    "lit_redstone_ore": {},
    "unlit_redstone_torch": {
        0: "facing=up",
        1: "facing=east",
        2: "facing=west",
        3: "facing=south",
        4: "facing=north"},
    "redstone_torch": {
        0: "facing=up",
        1: "facing=east",
        2: "facing=west",
        3: "facing=south",
        4: "facing=north"},
    "stone_button": {
        0: "facing=down,powered=false",
        1: "facing=east,powered=false",
        2: "facing=west,powered=false",
        3: "facing=south,powered=false",
        4: "facing=north,powered=false",
        5: "facing=up,powered=false",
        6: "facing=up,powered=false",
        7: "facing=up,powered=false",
        8: "facing=down,powered=true",
        9: "facing=east,powered=true",
        10: "facing=west,powered=true",
        11: "facing=south,powered=true",
        12: "facing=north,powered=true",
        13: "facing=up,powered=true",
        14: "facing=up,powered=true",
        15: "facing=up,powered=true"},
    "snow_layer": {
        0: "layers=1",
        1: "layers=2",
        2: "layers=3",
        3: "layers=4",
        4: "layers=5",
        5: "layers=6",
        6: "layers=7",
        7: "layers=8",
        8: "layers=1",
        9: "layers=2",
        10: "layers=3",
        11: "layers=4",
        12: "layers=5",
        13: "layers=6",
        14: "layers=7",
        15: "layers=8"},
    "ice": {},
    "snow": {},
    "cactus": {
        0: "age=0",
        1: "age=1",
        2: "age=2",
        3: "age=3",
        4: "age=4",
        5: "age=5",
        6: "age=6",
        7: "age=7",
        8: "age=8",
        9: "age=9",
        10: "age=10",
        11: "age=11",
        12: "age=12",
        13: "age=13",
        14: "age=14",
        15: "age=15"},
    "clay": {},
    "reeds": {
        0: "age=0",
        1: "age=1",
        2: "age=2",
        3: "age=3",
        4: "age=4",
        5: "age=5",
        6: "age=6",
        7: "age=7",
        8: "age=8",
        9: "age=9",
        10: "age=10",
        11: "age=11",
        12: "age=12",
        13: "age=13",
        14: "age=14",
        15: "age=15"},
    "jukebox": {
        0: "has_record=false",
        1: "has_record=true",
        2: "has_record=true",
        3: "has_record=true",
        4: "has_record=true",
        5: "has_record=true",
        6: "has_record=true",
        7: "has_record=true",
        8: "has_record=true",
        9: "has_record=true",
        10: "has_record=true",
        11: "has_record=true",
        12: "has_record=true",
        13: "has_record=true",
        14: "has_record=true",
        15: "has_record=true"},
    "fence": {},
    "pumpkin": {
        0: "facing=south",
        1: "facing=west",
        2: "facing=north",
        3: "facing=east",
        4: "facing=south",
        5: "facing=west",
        6: "facing=north",
        7: "facing=east",
        8: "facing=south",
        9: "facing=west",
        10: "facing=north",
        11: "facing=east",
        12: "facing=south",
        13: "facing=west",
        14: "facing=north",
        15: "facing=east"},
    "netherrack": {},
    "soul_sand": {},
    "glowstone": {},
    "portal": {
        0: "axis=x",
        1: "axis=x",
        2: "axis=z",
        3: "axis=x",
        4: "axis=x",
        5: "axis=x",
        6: "axis=z",
        7: "axis=x",
        8: "axis=x",
        9: "axis=x",
        10: "axis=z",
        11: "axis=x",
        12: "axis=x",
        13: "axis=x",
        14: "axis=z",
        15: "axis=x"},
    "lit_pumpkin": {
        0: "facing=south",
        1: "facing=west",
        2: "facing=north",
        3: "facing=east",
        4: "facing=south",
        5: "facing=west",
        6: "facing=north",
        7: "facing=east",
        8: "facing=south",
        9: "facing=west",
        10: "facing=north",
        11: "facing=east",
        12: "facing=south",
        13: "facing=west",
        14: "facing=north",
        15: "facing=east"},
    "cake": {
        0: "bites=0",
        1: "bites=1",
        2: "bites=2",
        3: "bites=3",
        4: "bites=4",
        5: "bites=5",
        6: "bites=6"},
    "unpowered_repeater": {
        0: "delay=1,facing=south",
        1: "delay=1,facing=north",
        2: "delay=1,facing=west",
        3: "delay=1,facing=east",
        4: "delay=2,facing=south",
        5: "delay=2,facing=north",
        6: "delay=2,facing=west",
        7: "delay=2,facing=east",
        8: "delay=3,facing=south",
        9: "delay=3,facing=north",
        10: "delay=3,facing=west",
        11: "delay=3,facing=east",
        12: "delay=4,facing=south",
        13: "delay=4,facing=north",
        14: "delay=4,facing=west",
        15: "delay=4,facing=east"},
    "powered_repeater": {
        0: "delay=1,facing=south",
        1: "delay=1,facing=north",
        2: "delay=1,facing=west",
        3: "delay=1,facing=east",
        4: "delay=2,facing=south",
        5: "delay=2,facing=north",
        6: "delay=2,facing=west",
        7: "delay=2,facing=east",
        8: "delay=3,facing=south",
        9: "delay=3,facing=north",
        10: "delay=3,facing=west",
        11: "delay=3,facing=east",
        12: "delay=4,facing=south",
        13: "delay=4,facing=north",
        14: "delay=4,facing=west",
        15: "delay=4,facing=east"},
    "stained_glass": {
        0: "color=white",
        1: "color=orange",
        2: "color=magenta",
        3: "color=light_blue",
        4: "color=yellow",
        5: "color=lime",
        6: "color=pink",
        7: "color=gray",
        8: "color=silver",
        9: "color=cyan",
        10: "color=purple",
        11: "color=blue",
        12: "color=brown",
        13: "color=green",
        14: "color=red",
        15: "color=black"},
    "trapdoor": {
        0: "facing=north,half=bottom,open=false",
        1: "facing=south,half=bottom,open=false",
        2: "facing=west,half=bottom,open=false",
        3: "facing=east,half=bottom,open=false",
        4: "facing=north,half=bottom,open=true",
        5: "facing=south,half=bottom,open=true",
        6: "facing=west,half=bottom,open=true",
        7: "facing=east,half=bottom,open=true",
        8: "facing=north,half=bottom,open=false",
        9: "facing=south,half=top,open=false",
        10: "facing=west,half=top,open=false",
        11: "facing=east,half=top,open=false",
        12: "facing=north,half=top,open=true",
        13: "facing=south,half=top,open=true",
        14: "facing=west,half=top,open=true",
        15: "facing=east,half=top,open=true"},
    "monster_egg": {
        0: "variant=stone",
        1: "variant=cobblestone",
        2: "variant=stone_brick",
        3: "variant=mossy_brick",
        4: "variant=cracked_brick",
        5: "variant=chiseled_brick"},
    "stonebrick": {
        0: "variant=stonebrick",
        1: "variant=mossy_stonebrick",
        2: "variant=cracked_stonebrick",
        3: "variant=chiseled_stonebrick"},
    "brown_mushroom_block": {
        0: "variant=all_inside",
        1: "variant=north_west",
        2: "variant=north",
        3: "variant=north_east",
        4: "variant=west",
        5: "variant=center",
        6: "variant=east",
        7: "variant=south_west",
        8: "variant=south",
        9: "variant=south_east",
        10: "variant=stem",
        11: "variant=all_inside",
        12: "variant=all_inside",
        13: "variant=all_inside",
        14: "variant=all_outside",
        15: "variant=all_stem"},
    "red_mushroom_block": {
        0: "variant=all_inside",
        1: "variant=north_west",
        2: "variant=north",
        3: "variant=north_east",
        4: "variant=west",
        5: "variant=center",
        6: "variant=east",
        7: "variant=south_west",
        8: "variant=south",
        9: "variant=south_east",
        10: "variant=stem",
        11: "variant=all_inside",
        12: "variant=all_inside",
        13: "variant=all_inside",
        14: "variant=all_outside",
        15: "variant=all_stem"},
    "iron_bars": {},
    "glass_pane": {},
    "melon_block": {},
    "pumpkin_stem": {
        0: "age=0",
        1: "age=1",
        2: "age=2",
        3: "age=3",
        4: "age=4",
        5: "age=5",
        6: "age=6",
        7: "age=7"},
    "melon_stem": {
        0: "age=0",
        1: "age=1",
        2: "age=2",
        3: "age=3",
        4: "age=4",
        5: "age=5",
        6: "age=6",
        7: "age=7"},
    "vine": {
        0: "east=false,north=false,south=false,west=false",
        1: "east=false,north=false,south=true,west=false",
        2: "east=false,north=false,south=true,west=true",
        3: "east=false,north=true,south=false,west=false",
        4: "east=false,north=true,south=true,west=false",
        5: "east=false,north=true,south=false,west=true",
        6: "east=false,north=true,south=true,west=true",
        7: "east=true,north=false,south=false,west=false",
        8: "east=true,north=false,south=false,west=false",
        9: "east=true,north=false,south=true,west=false",
        10: "east=true,north=false,south=false,west=true",
        11: "east=true,north=false,south=true,west=true",
        12: "east=true,north=true,south=false,west=false",
        13: "east=true,north=true,south=true,west=false",
        14: "east=true,north=true,south=false,west=true",
        15: "east=true,north=true,south=true,west=true"},
    "fence_gate": {
        0: "facing=south,open=false,powered=false",
        1: "facing=west,open=false,powered=false",
        2: "facing=north,open=false,powered=false",
        3: "facing=east,open=false,powered=false",
        4: "facing=south,open=true,powered=false",
        5: "facing=west,open=true,powered=false",
        6: "facing=north,open=true,powered=false",
        7: "facing=east,open=true,powered=false",
        8: "facing=south,open=false,powered=true",
        9: "facing=west,open=false,powered=true",
        10: "facing=north,open=false,powered=true",
        11: "facing=east,open=false,powered=true",
        12: "facing=south,open=true,powered=true",
        13: "facing=west,open=true,powered=true",
        14: "facing=north,open=true,powered=true",
        15: "facing=east,open=true,powered=true"},
    "brick_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "stone_brick_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "mycelium": {},
    "waterlily": {},
    "nether_brick": {},
    "nether_brick_fence": {},
    "nether_brick_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "nether_wart": {
        0: "age=0",
        1: "age=1",
        2: "age=2",
        3: "age=3"},
    "enchanting_table": {},
    "brewing_stand": {
        0: "has_bottle_0=false,has_bottle_1=false,has_bottle_2=false",
        1: "has_bottle_0=true,has_bottle_1=false,has_bottle_2=false",
        2: "has_bottle_0=false,has_bottle_1=true,has_bottle_2=false",
        3: "has_bottle_0=true,has_bottle_1=true,has_bottle_2=false",
        4: "has_bottle_0=false,has_bottle_1=false,has_bottle_2=true",
        5: "has_bottle_0=true,has_bottle_1=false,has_bottle_2=true",
        6: "has_bottle_0=false,has_bottle_1=true,has_bottle_2=true",
        7: "has_bottle_0=true,has_bottle_1=true,has_bottle_2=true",
        8: "has_bottle_0=false,has_bottle_1=false,has_bottle_2=false",
        9: "has_bottle_0=true,has_bottle_1=false,has_bottle_2=false",
        10: "has_bottle_0=false,has_bottle_1=true,has_bottle_2=false",
        11: "has_bottle_0=true,has_bottle_1=true,has_bottle_2=false",
        12: "has_bottle_0=false,has_bottle_1=false,has_bottle_2=true",
        13: "has_bottle_0=true,has_bottle_1=false,has_bottle_2=true",
        14: "has_bottle_0=false,has_bottle_1=true,has_bottle_2=true",
        15: "has_bottle_0=true,has_bottle_1=true,has_bottle_2=true"},
    "cauldron": {
        0: "level=0",
        1: "level=1",
        2: "level=2",
        3: "level=3"},
    "end_portal": {},
    "end_portal_frame": {
        0: "eye=false,facing=south",
        1: "eye=false,facing=west",
        2: "eye=false,facing=north",
        3: "eye=false,facing=east",
        4: "eye=true,facing=south",
        5: "eye=true,facing=west",
        6: "eye=true,facing=north",
        7: "eye=true,facing=east",
        8: "eye=false,facing=south",
        9: "eye=false,facing=west",
        10: "eye=false,facing=north",
        11: "eye=false,facing=east",
        12: "eye=true,facing=south",
        13: "eye=true,facing=west",
        14: "eye=true,facing=north",
        15: "eye=true,facing=east"},
    "end_stone": {},
    "dragon_egg": {},
    "redstone_lamp": {},
    "lit_redstone_lamp": {},
    "double_wooden_slab": {
        0: "variant=oak",
        1: "variant=spruce",
        2: "variant=birch",
        3: "variant=jungle",
        4: "variant=acacia",
        5: "variant=dark_oak",
        6: "variant=oak",
        7: "variant=oak",
        8: "variant=oak",
        9: "variant=spruce",
        10: "variant=birch",
        11: "variant=jungle",
        12: "variant=acacia",
        13: "variant=dark_oak",
        14: "variant=oak",
        15: "variant=oak"},
    "wooden_slab": {
        0: "half=bottom,variant=oak",
        1: "half=bottom,variant=spruce",
        2: "half=bottom,variant=birch",
        3: "half=bottom,variant=jungle",
        4: "half=bottom,variant=acacia",
        5: "half=bottom,variant=dark_oak",
        6: "half=bottom,variant=oak",
        7: "half=bottom,variant=oak",
        8: "half=top,variant=oak",
        9: "half=top,variant=spruce",
        10: "half=top,variant=birch",
        11: "half=top,variant=jungle",
        12: "half=top,variant=acacia",
        13: "half=top,variant=dark_oak",
        14: "half=top,variant=oak",
        15: "half=top,variant=oak"},
    "cocoa": {
        0: "age=0,facing=south",
        1: "age=0,facing=west",
        2: "age=0,facing=north",
        3: "age=0,facing=east",
        4: "age=1,facing=south",
        5: "age=1,facing=west",
        6: "age=1,facing=north",
        7: "age=1,facing=east",
        8: "age=2,facing=south",
        9: "age=2,facing=west",
        10: "age=2,facing=north",
        11: "age=2,facing=east"},
    "sandstone_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "emerald_ore": {},
    "ender_chest": {
        0: "facing=north",
        1: "facing=north",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=north",
        7: "facing=north",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=north",
        13: "facing=north",
        14: "facing=north",
        15: "facing=south"},
    "tripwire_hook": {
        0: "attached=false,facing=south,powered=false",
        1: "attached=false,facing=west,powered=false",
        2: "attached=false,facing=north,powered=false",
        3: "attached=false,facing=east,powered=false",
        4: "attached=true,facing=south,powered=false",
        5: "attached=true,facing=west,powered=false",
        6: "attached=true,facing=north,powered=false",
        7: "attached=true,facing=east,powered=false",
        8: "attached=false,facing=south,powered=true",
        9: "attached=false,facing=west,powered=true",
        10: "attached=false,facing=north,powered=true",
        11: "attached=false,facing=east,powered=true",
        12: "attached=true,facing=south,powered=true",
        13: "attached=true,facing=west,powered=true",
        14: "attached=true,facing=north,powered=true",
        15: "attached=true,facing=east,powered=true"},
    "tripwire": {
        0: "attached=false,disarmed=false,powered=false",
        1: "attached=false,disarmed=false,powered=true",
        2: "attached=false,disarmed=false,powered=false",
        3: "attached=false,disarmed=false,powered=true",
        4: "attached=true,disarmed=false,powered=false",
        5: "attached=true,disarmed=false,powered=true",
        6: "attached=true,disarmed=false,powered=false",
        7: "attached=true,disarmed=false,powered=true",
        8: "attached=false,disarmed=true,powered=false",
        9: "attached=false,disarmed=true,powered=true",
        10: "attached=false,disarmed=true,powered=false",
        11: "attached=false,disarmed=true,powered=true",
        12: "attached=true,disarmed=true,powered=false",
        13: "attached=true,disarmed=true,powered=true",
        14: "attached=true,disarmed=true,powered=false",
        15: "attached=true,disarmed=true,powered=true"},
    "emerald_block": {},
    "spruce_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "birch_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "jungle_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "command_block": {
        0: "conditional=false,facing=down",
        1: "conditional=false,facing=up",
        2: "conditional=false,facing=north",
        3: "conditional=false,facing=south",
        4: "conditional=false,facing=west",
        5: "conditional=false,facing=east",
        6: "conditional=false,facing=down",
        7: "conditional=false,facing=up",
        8: "conditional=true,facing=down",
        9: "conditional=true,facing=up",
        10: "conditional=true,facing=north",
        11: "conditional=true,facing=south",
        12: "conditional=true,facing=west",
        13: "conditional=true,facing=east",
        14: "conditional=true,facing=down",
        15: "conditional=true,facing=up"},
    "beacon": {},
    "cobblestone_wall": {
        0: "variant=cobblestone",
        1: "variant=mossy_cobblestone"},
    "flower_pot": {},
    "carrots": {
        0: "age=0",
        1: "age=1",
        2: "age=2",
        3: "age=3",
        4: "age=4",
        5: "age=5",
        6: "age=6",
        7: "age=7"},
    "potatoes": {
        0: "age=0",
        1: "age=1",
        2: "age=2",
        3: "age=3",
        4: "age=4",
        5: "age=5",
        6: "age=6",
        7: "age=7"},
    "wooden_button": {
        0: "facing=down,powered=false",
        1: "facing=east,powered=false",
        2: "facing=west,powered=false",
        3: "facing=south,powered=false",
        4: "facing=north,powered=false",
        5: "facing=up,powered=false",
        6: "facing=up,powered=false",
        7: "facing=up,powered=false",
        8: "facing=down,powered=true",
        9: "facing=east,powered=true",
        10: "facing=west,powered=true",
        11: "facing=south,powered=true",
        12: "facing=north,powered=true",
        13: "facing=up,powered=true",
        14: "facing=up,powered=true",
        15: "facing=up,powered=true"},
    "skull": {
        0: "facing=down,nodrop=false",
        1: "facing=up,nodrop=false",
        2: "facing=north,nodrop=false",
        3: "facing=south,nodrop=false",
        4: "facing=west,nodrop=false",
        5: "facing=east,nodrop=false",
        6: "facing=down,nodrop=false",
        7: "facing=up,nodrop=false",
        8: "facing=down,nodrop=true",
        9: "facing=up,nodrop=true",
        10: "facing=north,nodrop=true",
        11: "facing=south,nodrop=true",
        12: "facing=west,nodrop=true",
        13: "facing=east,nodrop=true",
        14: "facing=down,nodrop=true",
        15: "facing=up,nodrop=true"},
    "anvil": {
        0: "damage=0,facing=south",
        1: "damage=0,facing=west",
        2: "damage=0,facing=north",
        3: "damage=0,facing=east",
        4: "damage=1,facing=south",
        5: "damage=1,facing=west",
        6: "damage=1,facing=north",
        7: "damage=1,facing=east",
        8: "damage=2,facing=south",
        9: "damage=2,facing=west",
        10: "damage=2,facing=north",
        11: "damage=2,facing=east"},
    "trapped_chest": {
        0: "facing=north",
        1: "facing=north",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=north",
        7: "facing=north",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=north",
        13: "facing=north",
        14: "facing=north",
        15: "facing=south"},
    "light_weighted_pressure_plate": {
        0: "power=0",
        1: "power=1",
        2: "power=2",
        3: "power=3",
        4: "power=4",
        5: "power=5",
        6: "power=6",
        7: "power=7",
        8: "power=8",
        9: "power=9",
        10: "power=10",
        11: "power=11",
        12: "power=12",
        13: "power=13",
        14: "power=14",
        15: "power=15"},
    "heavy_weighted_pressure_plate": {
        0: "power=0",
        1: "power=1",
        2: "power=2",
        3: "power=3",
        4: "power=4",
        5: "power=5",
        6: "power=6",
        7: "power=7",
        8: "power=8",
        9: "power=9",
        10: "power=10",
        11: "power=11",
        12: "power=12",
        13: "power=13",
        14: "power=14",
        15: "power=15"},
    "unpowered_comparator": {
        0: "facing=south,mode=compare,powered=false",
        1: "facing=west,mode=compare,powered=false",
        2: "facing=north,mode=compare,powered=false",
        3: "facing=east,mode=compare,powered=false",
        4: "facing=south,mode=subtract,powered=false",
        5: "facing=west,mode=subtract,powered=false",
        6: "facing=north,mode=subtract,powered=false",
        7: "facing=east,mode=subtract,powered=false",
        8: "facing=south,mode=compare,powered=true",
        9: "facing=west,mode=compare,powered=true",
        10: "facing=north,mode=compare,powered=true",
        11: "facing=east,mode=compare,powered=true",
        12: "facing=south,mode=subtract,powered=true",
        13: "facing=west,mode=subtract,powered=true",
        14: "facing=north,mode=subtract,powered=true",
        15: "facing=east,mode=subtract,powered=true"},
    "powered_comparator": {
        0: "facing=south,mode=compare,powered=false",
        1: "facing=west,mode=compare,powered=false",
        2: "facing=north,mode=compare,powered=false",
        3: "facing=east,mode=compare,powered=false",
        4: "facing=south,mode=subtract,powered=false",
        5: "facing=west,mode=subtract,powered=false",
        6: "facing=north,mode=subtract,powered=false",
        7: "facing=east,mode=subtract,powered=false",
        8: "facing=south,mode=compare,powered=true",
        9: "facing=west,mode=compare,powered=true",
        10: "facing=north,mode=compare,powered=true",
        11: "facing=east,mode=compare,powered=true",
        12: "facing=south,mode=subtract,powered=true",
        13: "facing=west,mode=subtract,powered=true",
        14: "facing=north,mode=subtract,powered=true",
        15: "facing=east,mode=subtract,powered=true"},
    "daylight_detector": {
        0: "power=0",
        1: "power=1",
        2: "power=2",
        3: "power=3",
        4: "power=4",
        5: "power=5",
        6: "power=6",
        7: "power=7",
        8: "power=8",
        9: "power=9",
        10: "power=10",
        11: "power=11",
        12: "power=12",
        13: "power=13",
        14: "power=14",
        15: "power=15"},
    "redstone_block": {},
    "quartz_ore": {},
    "hopper": {
        0: "facing=down",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        8: "facing=down",
        10: "facing=north",
        11: "facing=south",
        12: "facing=west",
        13: "facing=east",
        14: "facing=down"},
    "quartz_block": {
        0: "variant=default",
        1: "variant=chiseled",
        2: "variant=lines_y",
        3: "variant=lines_x",
        4: "variant=lines_z",
        5: "variant=default",
        6: "variant=default",
        7: "variant=default",
        8: "variant=default",
        9: "variant=default",
        10: "variant=default",
        11: "variant=default",
        12: "variant=default",
        13: "variant=default",
        14: "variant=default",
        15: "variant=default"},
    "quartz_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "activator_rail": {
        0: "powered=false,shape=north_south",
        1: "powered=false,shape=east_west",
        2: "powered=false,shape=ascending_east",
        3: "powered=false,shape=ascending_west",
        4: "powered=false,shape=ascending_north",
        5: "powered=false,shape=ascending_south",
        8: "powered=true,shape=north_south",
        9: "powered=true,shape=east_west",
        10: "powered=true,shape=ascending_east",
        11: "powered=true,shape=ascending_west",
        12: "powered=true,shape=ascending_north",
        13: "powered=true,shape=ascending_south"},
    "dropper": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=down",
        9: "facing=up",
        10: "facing=north",
        11: "facing=south",
        12: "facing=west",
        13: "facing=east",
        14: "facing=down",
        15: "facing=up"},
    "stained_hardened_clay": {
        0: "color=white",
        1: "color=orange",
        2: "color=magenta",
        3: "color=light_blue",
        4: "color=yellow",
        5: "color=lime",
        6: "color=pink",
        7: "color=gray",
        8: "color=silver",
        9: "color=cyan",
        10: "color=purple",
        11: "color=blue",
        12: "color=brown",
        13: "color=green",
        14: "color=red",
        15: "color=black"},
    "stained_glass_pane": {
        0: "color=white",
        1: "color=orange",
        2: "color=magenta",
        3: "color=light_blue",
        4: "color=yellow",
        5: "color=lime",
        6: "color=pink",
        7: "color=gray",
        8: "color=silver",
        9: "color=cyan",
        10: "color=purple",
        11: "color=blue",
        12: "color=brown",
        13: "color=green",
        14: "color=red",
        15: "color=black"},
    "leaves2": {
        0: "check_decay=false,decayable=true,variant=acacia",
        1: "check_decay=false,decayable=true,variant=dark_oak",
        4: "check_decay=false,decayable=false,variant=acacia",
        5: "check_decay=false,decayable=false,variant=dark_oak",
        8: "check_decay=true,decayable=true,variant=acacia",
        9: "check_decay=true,decayable=true,variant=dark_oak",
        12: "check_decay=true,decayable=false,variant=acacia",
        13: "check_decay=true,decayable=false,variant=dark_oak"},
    "log2": {
        0: "axis=y,variant=acacia",
        1: "axis=y,variant=dark_oak",
        4: "axis=x,variant=acacia",
        5: "axis=x,variant=dark_oak",
        8: "axis=z,variant=acacia",
        9: "axis=z,variant=dark_oak",
        12: "axis=none,variant=acacia",
        13: "axis=none,variant=dark_oak"},
    "acacia_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "dark_oak_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "slime": {},
    "barrier": {},
    "iron_trapdoor": {
        0: "facing=north,half=bottom,open=false",
        1: "facing=south,half=bottom,open=false",
        2: "facing=west,half=bottom,open=false",
        3: "facing=east,half=bottom,open=false",
        4: "facing=north,half=bottom,open=true",
        5: "facing=south,half=bottom,open=true",
        6: "facing=west,half=bottom,open=true",
        7: "facing=east,half=bottom,open=true",
        8: "facing=north,half=bottom,open=false",
        9: "facing=south,half=top,open=false",
        10: "facing=west,half=top,open=false",
        11: "facing=east,half=top,open=false",
        12: "facing=north,half=top,open=true",
        13: "facing=south,half=top,open=true",
        14: "facing=west,half=top,open=true",
        15: "facing=east,half=top,open=true"},
    "prismarine": {
        0: "variant=prismarine",
        1: "variant=prismarine_bricks",
        2: "variant=dark_prismarine"},
    "sea_lantern": {},
    "hay_block": {
        0: "axis=y",
        1: "axis=y",
        2: "axis=y",
        3: "axis=y",
        4: "axis=x",
        5: "axis=x",
        6: "axis=x",
        7: "axis=x",
        8: "axis=z",
        9: "axis=z",
        10: "axis=z",
        11: "axis=z",
        12: "axis=y",
        13: "axis=y",
        14: "axis=y",
        15: "axis=y"},
    "carpet": {
        0: "color=white",
        1: "color=orange",
        2: "color=magenta",
        3: "color=light_blue",
        4: "color=yellow",
        5: "color=lime",
        6: "color=pink",
        7: "color=gray",
        8: "color=silver",
        9: "color=cyan",
        10: "color=purple",
        11: "color=blue",
        12: "color=brown",
        13: "color=green",
        14: "color=red",
        15: "color=black"},
    "hardened_clay": {},
    "coal_block": {},
    "packed_ice": {},
    "double_plant": {
        0: "facing=north,half=lower,variant=sunflower",
        1: "facing=north,half=lower,variant=syringa",
        2: "facing=north,half=lower,variant=double_grass",
        3: "facing=north,half=lower,variant=double_fern",
        4: "facing=north,half=lower,variant=double_rose",
        5: "facing=north,half=lower,variant=paeonia",
        6: "facing=north,half=lower,variant=sunflower",
        7: "facing=north,half=lower,variant=sunflower",
        8: "facing=north,half=upper",
        9: "facing=north,half=upper",
        10: "facing=north,half=upper",
        11: "facing=north,half=upper",
        12: "facing=north,half=upper",
        13: "facing=north,half=upper",
        14: "facing=north,half=upper",
        15: "facing=north,half=upper"},
    "standing_banner": {
        0: "rotation=0",
        1: "rotation=1",
        2: "rotation=2",
        3: "rotation=3",
        4: "rotation=4",
        5: "rotation=5",
        6: "rotation=6",
        7: "rotation=7",
        8: "rotation=8",
        9: "rotation=9",
        10: "rotation=10",
        11: "rotation=11",
        12: "rotation=12",
        13: "rotation=13",
        14: "rotation=14",
        15: "rotation=15"},
    "wall_banner": {
        0: "facing=north",
        1: "facing=north",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=north",
        7: "facing=north",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=north",
        13: "facing=north",
        14: "facing=north",
        15: "facing=south"},
    "daylight_detector_inverted": {
        0: "power=0",
        1: "power=1",
        2: "power=2",
        3: "power=3",
        4: "power=4",
        5: "power=5",
        6: "power=6",
        7: "power=7",
        8: "power=8",
        9: "power=9",
        10: "power=10",
        11: "power=11",
        12: "power=12",
        13: "power=13",
        14: "power=14",
        15: "power=15"},
    "red_sandstone": {
        0: "type=red_sandstone",
        1: "type=chiseled_red_sandstone",
        2: "type=smooth_red_sandstone"},
    "red_sandstone_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "double_stone_slab2": {
        0: "seamless=false,variant=red_sandstone",
        1: "seamless=false,variant=red_sandstone",
        2: "seamless=false,variant=red_sandstone",
        3: "seamless=false,variant=red_sandstone",
        4: "seamless=false,variant=red_sandstone",
        5: "seamless=false,variant=red_sandstone",
        6: "seamless=false,variant=red_sandstone",
        7: "seamless=false,variant=red_sandstone",
        8: "seamless=true,variant=red_sandstone",
        9: "seamless=true,variant=red_sandstone",
        10: "seamless=true,variant=red_sandstone",
        11: "seamless=true,variant=red_sandstone",
        12: "seamless=true,variant=red_sandstone",
        13: "seamless=true,variant=red_sandstone",
        14: "seamless=true,variant=red_sandstone",
        15: "seamless=true,variant=red_sandstone"},
    "stone_slab2": {
        0: "half=bottom,variant=red_sandstone",
        1: "half=bottom,variant=red_sandstone",
        2: "half=bottom,variant=red_sandstone",
        3: "half=bottom,variant=red_sandstone",
        4: "half=bottom,variant=red_sandstone",
        5: "half=bottom,variant=red_sandstone",
        6: "half=bottom,variant=red_sandstone",
        7: "half=bottom,variant=red_sandstone",
        8: "half=top,variant=red_sandstone",
        9: "half=top,variant=red_sandstone",
        10: "half=top,variant=red_sandstone",
        11: "half=top,variant=red_sandstone",
        12: "half=top,variant=red_sandstone",
        13: "half=top,variant=red_sandstone",
        14: "half=top,variant=red_sandstone",
        15: "half=top,variant=red_sandstone"},
    "spruce_fence_gate": {
        0: "facing=south,open=false,powered=false",
        1: "facing=west,open=false,powered=false",
        2: "facing=north,open=false,powered=false",
        3: "facing=east,open=false,powered=false",
        4: "facing=south,open=true,powered=false",
        5: "facing=west,open=true,powered=false",
        6: "facing=north,open=true,powered=false",
        7: "facing=east,open=true,powered=false",
        8: "facing=south,open=false,powered=true",
        9: "facing=west,open=false,powered=true",
        10: "facing=north,open=false,powered=true",
        11: "facing=east,open=false,powered=true",
        12: "facing=south,open=true,powered=true",
        13: "facing=west,open=true,powered=true",
        14: "facing=north,open=true,powered=true",
        15: "facing=east,open=true,powered=true"},
    "birch_fence_gate": {
        0: "facing=south,open=false,powered=false",
        1: "facing=west,open=false,powered=false",
        2: "facing=north,open=false,powered=false",
        3: "facing=east,open=false,powered=false",
        4: "facing=south,open=true,powered=false",
        5: "facing=west,open=true,powered=false",
        6: "facing=north,open=true,powered=false",
        7: "facing=east,open=true,powered=false",
        8: "facing=south,open=false,powered=true",
        9: "facing=west,open=false,powered=true",
        10: "facing=north,open=false,powered=true",
        11: "facing=east,open=false,powered=true",
        12: "facing=south,open=true,powered=true",
        13: "facing=west,open=true,powered=true",
        14: "facing=north,open=true,powered=true",
        15: "facing=east,open=true,powered=true"},
    "jungle_fence_gate": {
        0: "facing=south,open=false,powered=false",
        1: "facing=west,open=false,powered=false",
        2: "facing=north,open=false,powered=false",
        3: "facing=east,open=false,powered=false",
        4: "facing=south,open=true,powered=false",
        5: "facing=west,open=true,powered=false",
        6: "facing=north,open=true,powered=false",
        7: "facing=east,open=true,powered=false",
        8: "facing=south,open=false,powered=true",
        9: "facing=west,open=false,powered=true",
        10: "facing=north,open=false,powered=true",
        11: "facing=east,open=false,powered=true",
        12: "facing=south,open=true,powered=true",
        13: "facing=west,open=true,powered=true",
        14: "facing=north,open=true,powered=true",
        15: "facing=east,open=true,powered=true"},
    "dark_oak_fence_gate": {
        0: "facing=south,open=false,powered=false",
        1: "facing=west,open=false,powered=false",
        2: "facing=north,open=false,powered=false",
        3: "facing=east,open=false,powered=false",
        4: "facing=south,open=true,powered=false",
        5: "facing=west,open=true,powered=false",
        6: "facing=north,open=true,powered=false",
        7: "facing=east,open=true,powered=false",
        8: "facing=south,open=false,powered=true",
        9: "facing=west,open=false,powered=true",
        10: "facing=north,open=false,powered=true",
        11: "facing=east,open=false,powered=true",
        12: "facing=south,open=true,powered=true",
        13: "facing=west,open=true,powered=true",
        14: "facing=north,open=true,powered=true",
        15: "facing=east,open=true,powered=true"},
    "acacia_fence_gate": {
        0: "facing=south,open=false,powered=false",
        1: "facing=west,open=false,powered=false",
        2: "facing=north,open=false,powered=false",
        3: "facing=east,open=false,powered=false",
        4: "facing=south,open=true,powered=false",
        5: "facing=west,open=true,powered=false",
        6: "facing=north,open=true,powered=false",
        7: "facing=east,open=true,powered=false",
        8: "facing=south,open=false,powered=true",
        9: "facing=west,open=false,powered=true",
        10: "facing=north,open=false,powered=true",
        11: "facing=east,open=false,powered=true",
        12: "facing=south,open=true,powered=true",
        13: "facing=west,open=true,powered=true",
        14: "facing=north,open=true,powered=true",
        15: "facing=east,open=true,powered=true"},
    "spruce_fence": {},
    "birch_fence": {},
    "jungle_fence": {},
    "dark_oak_fence": {},
    "acacia_fence": {},
    "spruce_door": {
        0: "facing=east,half=lower,hinge=left,open=false,powered=false",
        1: "facing=south,half=lower,hinge=left,open=false,powered=false",
        2: "facing=west,half=lower,hinge=left,open=false,powered=false",
        3: "facing=north,half=lower,hinge=left,open=false,powered=false",
        4: "facing=east,half=lower,hinge=left,open=true,powered=false",
        5: "facing=south,half=lower,hinge=left,open=true,powered=false",
        6: "facing=west,half=lower,hinge=left,open=true,powered=false",
        7: "facing=north,half=lower,hinge=left,open=true,powered=false",
        8: "half=upper,hinge=left,powered=false",
        9: "half=upper,hinge=right,powered=false",
        10: "half=upper,hinge=left,powered=true",
        11: "half=upper,hinge=right,powered=true",
        12: "half=upper,hinge=left,powered=false",
        13: "half=upper,hinge=right,powered=false",
        14: "half=upper,hinge=left,powered=true",
        15: "half=upper,hinge=right,powered=true"},
    "birch_door": {
        0: "facing=east,half=lower,hinge=left,open=false,powered=false",
        1: "facing=south,half=lower,hinge=left,open=false,powered=false",
        2: "facing=west,half=lower,hinge=left,open=false,powered=false",
        3: "facing=north,half=lower,hinge=left,open=false,powered=false",
        4: "facing=east,half=lower,hinge=left,open=true,powered=false",
        5: "facing=south,half=lower,hinge=left,open=true,powered=false",
        6: "facing=west,half=lower,hinge=left,open=true,powered=false",
        7: "facing=north,half=lower,hinge=left,open=true,powered=false",
        8: "half=upper,hinge=left,powered=false",
        9: "half=upper,hinge=right,powered=false",
        10: "half=upper,hinge=left,powered=true",
        11: "half=upper,hinge=right,powered=true",
        12: "half=upper,hinge=left,powered=false",
        13: "half=upper,hinge=right,powered=false",
        14: "half=upper,hinge=left,powered=true",
        15: "half=upper,hinge=right,powered=true"},
    "jungle_door": {
        0: "facing=east,half=lower,hinge=left,open=false,powered=false",
        1: "facing=south,half=lower,hinge=left,open=false,powered=false",
        2: "facing=west,half=lower,hinge=left,open=false,powered=false",
        3: "facing=north,half=lower,hinge=left,open=false,powered=false",
        4: "facing=east,half=lower,hinge=left,open=true,powered=false",
        5: "facing=south,half=lower,hinge=left,open=true,powered=false",
        6: "facing=west,half=lower,hinge=left,open=true,powered=false",
        7: "facing=north,half=lower,hinge=left,open=true,powered=false",
        8: "half=upper,hinge=left,powered=false",
        9: "half=upper,hinge=right,powered=false",
        10: "half=upper,hinge=left,powered=true",
        11: "half=upper,hinge=right,powered=true",
        12: "half=upper,hinge=left,powered=false",
        13: "half=upper,hinge=right,powered=false",
        14: "half=upper,hinge=left,powered=true",
        15: "half=upper,hinge=right,powered=true"},
    "acacia_door": {
        0: "facing=east,half=lower,hinge=left,open=false,powered=false",
        1: "facing=south,half=lower,hinge=left,open=false,powered=false",
        2: "facing=west,half=lower,hinge=left,open=false,powered=false",
        3: "facing=north,half=lower,hinge=left,open=false,powered=false",
        4: "facing=east,half=lower,hinge=left,open=true,powered=false",
        5: "facing=south,half=lower,hinge=left,open=true,powered=false",
        6: "facing=west,half=lower,hinge=left,open=true,powered=false",
        7: "facing=north,half=lower,hinge=left,open=true,powered=false",
        8: "half=upper,hinge=left,powered=false",
        9: "half=upper,hinge=right,powered=false",
        10: "half=upper,hinge=left,powered=true",
        11: "half=upper,hinge=right,powered=true",
        12: "half=upper,hinge=left,powered=false",
        13: "half=upper,hinge=right,powered=false",
        14: "half=upper,hinge=left,powered=true",
        15: "half=upper,hinge=right,powered=true"},
    "dark_oak_door": {
        0: "facing=east,half=lower,hinge=left,open=false,powered=false",
        1: "facing=south,half=lower,hinge=left,open=false,powered=false",
        2: "facing=west,half=lower,hinge=left,open=false,powered=false",
        3: "facing=north,half=lower,hinge=left,open=false,powered=false",
        4: "facing=east,half=lower,hinge=left,open=true,powered=false",
        5: "facing=south,half=lower,hinge=left,open=true,powered=false",
        6: "facing=west,half=lower,hinge=left,open=true,powered=false",
        7: "facing=north,half=lower,hinge=left,open=true,powered=false",
        8: "half=upper,hinge=left,powered=false",
        9: "half=upper,hinge=right,powered=false",
        10: "half=upper,hinge=left,powered=true",
        11: "half=upper,hinge=right,powered=true",
        12: "half=upper,hinge=left,powered=false",
        13: "half=upper,hinge=right,powered=false",
        14: "half=upper,hinge=left,powered=true",
        15: "half=upper,hinge=right,powered=true"},
    "end_rod": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "chorus_plant": {},
    "chorus_flower": {
        0: "age=0",
        1: "age=1",
        2: "age=2",
        3: "age=3",
        4: "age=4",
        5: "age=5"},
    "purpur_block": {},
    "purpur_pillar": {
        0: "axis=y",
        1: "axis=y",
        2: "axis=y",
        3: "axis=y",
        4: "axis=x",
        5: "axis=x",
        6: "axis=x",
        7: "axis=x",
        8: "axis=z",
        9: "axis=z",
        10: "axis=z",
        11: "axis=z",
        12: "axis=y",
        13: "axis=y",
        14: "axis=y",
        15: "axis=y"},
    "purpur_stairs": {
        0: "facing=east,half=bottom",
        1: "facing=west,half=bottom",
        2: "facing=south,half=bottom",
        3: "facing=north,half=bottom",
        4: "facing=east,half=top",
        5: "facing=west,half=top",
        6: "facing=south,half=top",
        7: "facing=north,half=top",
        8: "facing=east,half=bottom",
        9: "facing=west,half=bottom",
        10: "facing=south,half=bottom",
        11: "facing=north,half=bottom",
        12: "facing=east,half=top",
        13: "facing=west,half=top",
        14: "facing=south,half=top",
        15: "facing=north,half=top"},
    "purpur_double_slab": {},
    "purpur_slab": {
        0: "half=bottom,variant=default",
        1: "half=bottom,variant=default",
        2: "half=bottom,variant=default",
        3: "half=bottom,variant=default",
        4: "half=bottom,variant=default",
        5: "half=bottom,variant=default",
        6: "half=bottom,variant=default",
        7: "half=bottom,variant=default",
        8: "half=top,variant=default",
        9: "half=top,variant=default",
        10: "half=top,variant=default",
        11: "half=top,variant=default",
        12: "half=top,variant=default",
        13: "half=top,variant=default",
        14: "half=top,variant=default",
        15: "half=top,variant=default"},
    "end_bricks": {},
    "beetroots": {
        0: "age=0",
        1: "age=1",
        2: "age=2",
        3: "age=3"},
    "grass_path": {},
    "end_gateway": {},
    "repeating_command_block": {
        0: "conditional=false,facing=down",
        1: "conditional=false,facing=up",
        2: "conditional=false,facing=north",
        3: "conditional=false,facing=south",
        4: "conditional=false,facing=west",
        5: "conditional=false,facing=east",
        6: "conditional=false,facing=down",
        7: "conditional=false,facing=up",
        8: "conditional=true,facing=down",
        9: "conditional=true,facing=up",
        10: "conditional=true,facing=north",
        11: "conditional=true,facing=south",
        12: "conditional=true,facing=west",
        13: "conditional=true,facing=east",
        14: "conditional=true,facing=down",
        15: "conditional=true,facing=up"},
    "chain_command_block": {
        0: "conditional=false,facing=down",
        1: "conditional=false,facing=up",
        2: "conditional=false,facing=north",
        3: "conditional=false,facing=south",
        4: "conditional=false,facing=west",
        5: "conditional=false,facing=east",
        6: "conditional=false,facing=down",
        7: "conditional=false,facing=up",
        8: "conditional=true,facing=down",
        9: "conditional=true,facing=up",
        10: "conditional=true,facing=north",
        11: "conditional=true,facing=south",
        12: "conditional=true,facing=west",
        13: "conditional=true,facing=east",
        14: "conditional=true,facing=down",
        15: "conditional=true,facing=up"},
    "frosted_ice": {
        0: "age=0",
        1: "age=1",
        2: "age=2",
        3: "age=3",
        4: "age=3",
        5: "age=3",
        6: "age=3",
        7: "age=3",
        8: "age=3",
        9: "age=3",
        10: "age=3",
        11: "age=3",
        12: "age=3",
        13: "age=3",
        14: "age=3",
        15: "age=3"},
    "magma": {},
    "nether_wart_block": {},
    "red_nether_brick": {},
    "bone_block": {
        0: "axis=y",
        1: "axis=y",
        2: "axis=y",
        3: "axis=y",
        4: "axis=x",
        5: "axis=x",
        6: "axis=x",
        7: "axis=x",
        8: "axis=z",
        9: "axis=z",
        10: "axis=z",
        11: "axis=z",
        12: "axis=y",
        13: "axis=y",
        14: "axis=y",
        15: "axis=y"},
    "structure_void": {},
    "observer": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "white_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "orange_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "magenta_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "light_blue_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "yellow_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "lime_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "pink_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "gray_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "silver_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "cyan_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "purple_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "blue_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "brown_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "green_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "red_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "black_shulker_box": {
        0: "facing=down",
        1: "facing=up",
        2: "facing=north",
        3: "facing=south",
        4: "facing=west",
        5: "facing=east",
        6: "facing=down",
        7: "facing=up",
        8: "facing=north",
        9: "facing=south",
        10: "facing=west",
        11: "facing=east",
        12: "facing=down",
        13: "facing=up",
        14: "facing=north",
        15: "facing=south"},
    "white_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "orange_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "magenta_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "light_blue_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "yellow_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "lime_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "pink_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "gray_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "silver_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "cyan_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "purple_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "blue_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "brown_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "green_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "red_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "black_glazed_terracotta": {
        0: "facing=north",
        1: "facing=south",
        2: "facing=east",
        3: "facing=west"},
    "concrete": {
        0: "color=white",
        1: "color=orange",
        2: "color=magenta",
        3: "color=light_blue",
        4: "color=yellow",
        5: "color=lime",
        6: "color=pink",
        7: "color=gray",
        8: "color=silver",
        9: "color=cyan",
        10: "color=purple",
        11: "color=blue",
        12: "color=brown",
        13: "color=green",
        14: "color=red",
        15: "color=black"},
    "concrete_powder": {
        0: "color=white",
        1: "color=orange",
        2: "color=magenta",
        3: "color=light_blue",
        4: "color=yellow",
        5: "color=lime",
        6: "color=pink",
        7: "color=gray",
        8: "color=silver",
        9: "color=cyan",
        10: "color=purple",
        11: "color=blue",
        12: "color=brown",
        13: "color=green",
        14: "color=red",
        15: "color=black"},
    "structure_block": {
        0: "mode=data",
        1: "mode=data",
        2: "mode=data",
        3: "mode=data",
        4: "mode=data",
        5: "mode=data",
        6: "mode=data",
        7: "mode=data",
        8: "mode=data",
        9: "mode=data",
        10: "mode=data",
        12: "mode=data",
        13: "mode=data",
        14: "mode=data",
        15: "mode=data"}
}
Globals.blockStates = {
    "air": {
        "default{": "air["},
    "stone": {
        "default{": "stone[",
        "variant=stone{": "stone[",
        "variant=granite{": "granite[",
        "variant=smooth_granite{": "polished_granite[",
        "variant=diorite{": "diorite[",
        "variant=smooth_diorite{": "polished_diorite[",
        "variant=andesite{": "andesite[",
        "variant=smooth_andesite{": "polished_andesite["},
    "grass": {
        "default{": "grass_block[",
        "snowy=true{": "grass_block[snowy=true",
        "snowy=false{": "grass_block[snowy=false"},
    "dirt": {
        "default{": "dirt[",
        "variant=dirt{": "dirt[",
        "variant=coarse_dirt{": "coarse_dirt[",
        "variant=podzol{": "podzol[",
        "snowy=true{": "[snowy=true",
        "snowy=false{": "[snowy=false"},
    "cobblestone": {
        "default{": "cobblestone["},
    "planks": {
        "default{": "oak_planks[",
        "variant=oak{": "oak_planks[",
        "variant=spruce{": "spruce_planks[",
        "variant=birch{": "birch_planks[",
        "variant=jungle{": "jungle_planks[",
        "variant=acacia{": "acacia_planks[",
        "variant=dark_oak{": "dark_oak_planks["},
    "sapling": {
        "default{": "oak_sapling[",
        "type=oak{": "oak_sapling[",
        "type=spruce{": "spruce_sapling[",
        "type=birch{": "birch_sapling[",
        "type=jungle{": "jungle_sapling[",
        "type=acacia{": "acacia_sapling[",
        "type=dark_oak{": "dark_oak_sapling[",
        "stage=0{": "[stage=0",
        "stage=1{": "[stage=1"},
    "bedrock": {
        "default{": "bedrock["},
    "flowing_water": {
        "default{": "flowing_water[",
        "level=0{": "[level=0",
        "level=1{": "[level=1",
        "level=2{": "[level=2",
        "level=3{": "[level=3",
        "level=4{": "[level=4",
        "level=5{": "[level=5",
        "level=6{": "[level=6",
        "level=7{": "[level=7",
        "level=8{": "[level=8",
        "level=9{": "[level=9",
        "level=10{": "[level=10",
        "level=11{": "[level=11",
        "level=12{": "[level=12",
        "level=13{": "[level=13",
        "level=14{": "[level=14",
        "level=15{": "[level=15"},
    "water": {
        "default{": "water[",
        "level=0{": "[level=0",
        "level=1{": "[level=1",
        "level=2{": "[level=2",
        "level=3{": "[level=3",
        "level=4{": "[level=4",
        "level=5{": "[level=5",
        "level=6{": "[level=6",
        "level=7{": "[level=7",
        "level=8{": "[level=8",
        "level=9{": "[level=9",
        "level=10{": "[level=10",
        "level=11{": "[level=11",
        "level=12{": "[level=12",
        "level=13{": "[level=13",
        "level=14{": "[level=14",
        "level=15{": "[level=15"},
    "flowing_lava": {
        "default{": "flowing_lava[",
        "level=0{": "[level=0",
        "level=1{": "[level=1",
        "level=2{": "[level=2",
        "level=3{": "[level=3",
        "level=4{": "[level=4",
        "level=5{": "[level=5",
        "level=6{": "[level=6",
        "level=7{": "[level=7",
        "level=8{": "[level=8",
        "level=9{": "[level=9",
        "level=10{": "[level=10",
        "level=11{": "[level=11",
        "level=12{": "[level=12",
        "level=13{": "[level=13",
        "level=14{": "[level=14",
        "level=15{": "[level=15"},
    "lava": {
        "default{": "lava[",
        "level=0{": "[level=0",
        "level=1{": "[level=1",
        "level=2{": "[level=2",
        "level=3{": "[level=3",
        "level=4{": "[level=4",
        "level=5{": "[level=5",
        "level=6{": "[level=6",
        "level=7{": "[level=7",
        "level=8{": "[level=8",
        "level=9{": "[level=9",
        "level=10{": "[level=10",
        "level=11{": "[level=11",
        "level=12{": "[level=12",
        "level=13{": "[level=13",
        "level=14{": "[level=14",
        "level=15{": "[level=15"},
    "sand": {
        "default{": "sand[",
        "type=sand{": "sand[",
        "type=red_sand{": "red_sand["},
    "gravel": {
        "default{": "gravel["},
    "gold_ore": {
        "default{": "gold_ore["},
    "iron_ore": {
        "default{": "iron_ore["},
    "coal_ore": {
        "default{": "coal_ore["},
    "log": {
        "default{": "oak_log[",
        "variant=oak,axis=none{": "oak_bark[",
        "variant=spruce,axis=none{": "spruce_bark[",
        "variant=birch,axis=none{": "birch_bark[",
        "variant=jungle,axis=none{": "jungle_bark[",
        "variant=oak{": "oak_log[",
        "variant=spruce{": "spruce_log[",
        "variant=birch{": "birch_log[",
        "variant=jungle{": "jungle_log[",
        "axis=x{": "[axis=x",
        "axis=y{": "[axis=y",
        "axis=z{": "[axis=z",
        "axis=none{": "oak_bark["},
    "leaves": {
        "default{": "oak_leaves[",
        "variant=oak{": "oak_leaves[",
        "variant=spruce{": "spruce_leaves[",
        "variant=birch{": "birch_leaves[",
        "variant=jungle{": "jungle_leaves[",
        "check_decay=true{": "[check_decay=true",
        "check_decay=false{": "[check_decay=false",
        "decayable=true{": "[decayable=true",
        "decayable=false{": "[decayable=false"},
    "sponge": {
        "default{": "sponge[",
        "wet=false{": "sponge[",
        "wet=true{": "wet_sponge["},
    "glass": {
        "default{": "glass["},
    "lapis_ore": {
        "default{": "lapis_ore["},
    "lapis_block": {
        "default{": "lapis_block["},
    "dispenser": {
        "default{": "dispenser[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down",
        "triggered=true{": "[triggered=true",
        "triggered=false{": "[triggered=false"},
    "sandstone": {
        "default{": "sandstone[",
        "type=sandstone{": "sandstone[",
        "type=chiseled_sandstone{": "chiseled_sandstone[",
        "type=smooth_sandstone{": "cut_sandstone["},
    "noteblock": {
        "default{": "note_block[",
        "{note:0": "[note=0",
        "{note:1": "[note=1",
        "{note:2": "[note=2",
        "{note:3": "[note=3",
        "{note:4": "[note=4",
        "{note:5": "[note=5",
        "{note:6": "[note=6",
        "{note:7": "[note=7",
        "{note:8": "[note=8",
        "{note:9": "[note=9",
        "{note:10": "[note=10",
        "{note:11": "[note=11",
        "{note:12": "[note=12",
        "{note:13": "[note=13",
        "{note:14": "[note=14",
        "{note:15": "[note=15",
        "{note:16": "[note=16",
        "{note:17": "[note=17",
        "{note:18": "[note=18",
        "{note:19": "[note=19",
        "{note:20": "[note=20",
        "{note:21": "[note=21",
        "{note:22": "[note=22",
        "{note:23": "[note=23",
        "{note:24": "[note=24",
        "{powered=1": "[powered=true",
        "{powered=0": "[powered=false"},
    "bed": {
        "default{": "red_bed[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "occupied=true{": "[occupied=true",
        "occupied=false{": "[occupied=false",
        "part=head{": "[part=head",
        "part=foot{": "[part=foot",
        "{color:0": "white_bed[",
        "{color:1": "orange_bed[",
        "{color:2": "magenta_bed[",
        "{color:3": "light_blue_bed[",
        "{color:4": "yellow_bed[",
        "{color:5": "lime_bed[",
        "{color:6": "pink_bed[",
        "{color:7": "gray_bed[",
        "{color:8": "light_gray_bed[",
        "{color:9": "cyan_bed[",
        "{color:10": "purple_bed[",
        "{color:11": "blue_bed[",
        "{color:12": "brown_bed[",
        "{color:13": "green_bed[",
        "{color:14": "red_bed[",
        "{color:15": "black_bed["},
    "golden_rail": {
        "default{": "powered_rail[",
        "powered=true{": "[powered=true",
        "powered=false{": "[powered=false",
        "shape=north_south{": "[shape=north_south",
        "shape=east_west{": "[shape=east_west",
        "shape=ascending_east{": "[shape=ascending_east",
        "shape=ascending_west{": "[shape=ascending_west",
        "shape=ascending_north{": "[shape=ascending_north",
        "shape=ascending_south{": "[shape=ascending_south"},
    "detector_rail": {
        "default{": "detector_rail[",
        "powered=true{": "[powered=true",
        "powered=false{": "[powered=false",
        "shape=north_south{": "[shape=north_south",
        "shape=east_west{": "[shape=east_west",
        "shape=ascending_east{": "[shape=ascending_east",
        "shape=ascending_west{": "[shape=ascending_west",
        "shape=ascending_north{": "[shape=ascending_north",
        "shape=ascending_south{": "[shape=ascending_south"},
    "sticky_piston": {
        "default{": "sticky_piston[",
        "extended=true{": "[extended=true",
        "extended=false{": "[extended=false",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "web": {
        "default{": "cobweb["},
    "tallgrass": {
        "default{": "grass[",
        "type=tall_grass{": "grass[",
        "type=dead_bush{": "dead_bush[",
        "type=fern{": "fern["},
    "deadbush": {
        "default{": "dead_bush["},
    "piston": {
        "default{": "piston[",
        "extended=true{": "[extended=true",
        "extended=false{": "[extended=false",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "piston_head": {
        "default{": "piston_head[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down",
        "short=true{": "[short=true",
        "short=false{": "[short=false",
        "type=normal{": "[type=normal",
        "type=sticky{": "[type=sticky"},
    "wool": {
        "default{": "white_wool[",
        "color=white{": "white_wool[",
        "color=orange{": "orange_wool[",
        "color=magenta{": "magenta_wool[",
        "color=light_blue{": "light_blue_wool[",
        "color=yellow{": "yellow_wool[",
        "color=lime{": "lime_wool[",
        "color=pink{": "pink_wool[",
        "color=gray{": "gray_wool[",
        "color=silver{": "light_gray_wool[",
        "color=cyan{": "cyan_wool[",
        "color=purple{": "purple_wool[",
        "color=blue{": "blue_wool[",
        "color=brown{": "brown_wool[",
        "color=green{": "green_wool[",
        "color=red{": "red_wool[",
        "color=black{": "black_wool["},
    "piston_extension": {
        "default{": "moving_piston[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down",
        "type=normal{": "[type=normal",
        "type=sticky{": "[type=sticky"},
    "yellow_flower": {
        "default{": "dandelion["},
    "red_flower": {
        "default{": "poppy[",
        "type=poppy{": "poppy[",
        "type=blue_orchid{": "blue_orchid[",
        "type=allium{": "allium[",
        "type=houstonia{": "azure_bluet[",
        "type=red_tulip{": "red_tulip[",
        "type=orange_tulip{": "orange_tulip[",
        "type=white_tulip{": "white_tulip[",
        "type=pink_tulip{": "pink_tulip[",
        "type=oxeye_daisy{": "oxeye_daisy["},
    "brown_mushroom": {
        "default{": "brown_mushroom["},
    "red_mushroom": {
        "default{": "red_mushroom["},
    "gold_block": {
        "default{": "gold_block["},
    "iron_block": {
        "default{": "iron_block["},
    "double_stone_slab": {
        "default{": "stone_slab[type=double",
        "seamless=true,variant=stone{": "smooth_stone[",
        "seamless=true,variant=sandstone{": "smooth_sandstone[",
        "seamless=true,variant=quartz{": "smooth_quartz[",
        "variant=stone{": "stone_slab[type=double",
        "variant=sandstone{": "sandstone_slab[type=double",
        "variant=wood_old{": "petrified_oak_slab[type=double",
        "variant=cobblestone{": "cobblestone_slab[type=double",
        "variant=brick{": "brick_slab[type=double",
        "variant=stone_brick{": "stone_brick_slab[type=double",
        "variant=nether_brick{": "nether_brick_slab[type=double",
        "variant=quartz{": "quartz_slab[type=double",
        "seamless=false{": "stone_slab[type=double",
        "seamless=true{": "smooth_stone["},
    "stone_slab": {
        "default{": "stone_slab[",
        "variant=stone{": "stone_slab[",
        "variant=sandstone{": "sandstone_slab[",
        "variant=wood_old{": "petrified_oak_slab[",
        "variant=cobblestone{": "cobblestone_slab[",
        "variant=brick{": "brick_slab[",
        "variant=stone_brick{": "stone_brick_slab[",
        "variant=nether_brick{": "nether_brick_slab[",
        "variant=quartz{": "quartz_slab[",
        "half=top{": "[type=top",
        "half=bottom{": "[type=bottom"},
    "brick_block": {
        "default{": "bricks["},
    "tnt": {
        "default{": "tnt[",
        "explode=false{": "tnt[",
        "explode=true{": "tnt["},
    "bookshelf": {
        "default{": "bookshelf["},
    "mossy_cobblestone": {
        "default{": "mossy_cobblestone["},
    "obsidian": {
        "default{": "obsidian["},
    "torch": {
        "default{": "torch[",
        "facing=up{": "torch[",
        "facing=north{": "wall_torch[facing=north",
        "facing=east{": "wall_torch[facing=east",
        "facing=south{": "wall_torch[facing=south",
        "facing=west{": "wall_torch[facing=west"},
    "fire": {
        "default{": "fire[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "age=3{": "[age=3",
        "age=4{": "[age=4",
        "age=5{": "[age=5",
        "age=6{": "[age=6",
        "age=7{": "[age=7",
        "age=8{": "[age=8",
        "age=9{": "[age=9",
        "age=10{": "[age=10",
        "age=11{": "[age=11",
        "age=12{": "[age=12",
        "age=13{": "[age=13",
        "age=14{": "[age=14",
        "age=15{": "[age=15",
        "up=true{": "[up=true",
        "up=false{": "[up=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "mob_spawner": {
        "default{": "mob_spawner["},
    "oak_stairs": {
        "default{": "oak_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "chest": {
        "default{": "chest[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "redstone_wire": {
        "default{": "redstone_wire[",
        "power=0{": "[power=0",
        "power=1{": "[power=1",
        "power=2{": "[power=2",
        "power=3{": "[power=3",
        "power=4{": "[power=4",
        "power=5{": "[power=5",
        "power=6{": "[power=6",
        "power=7{": "[power=7",
        "power=8{": "[power=8",
        "power=9{": "[power=9",
        "power=10{": "[power=10",
        "power=11{": "[power=11",
        "power=12{": "[power=12",
        "power=13{": "[power=13",
        "power=14{": "[power=14",
        "power=15{": "[power=15",
        "east=none{": "[east=none",
        "east=side{": "[east=side",
        "east=up{": "[east=up",
        "north=none{": "[north=none",
        "north=side{": "[north=side",
        "north=up{": "[north=up",
        "south=none{": "[south=none",
        "south=side{": "[south=side",
        "south=up{": "[south=up",
        "west=none{": "[west=none",
        "west=side{": "[west=side",
        "west=up{": "[west=up"},
    "diamond_ore": {
        "default{": "diamond_ore["},
    "diamond_block": {
        "default{": "diamond_block["},
    "crafting_table": {
        "default{": "crafting_table["},
    "wheat": {
        "default{": "wheat[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "age=3{": "[age=3",
        "age=4{": "[age=4",
        "age=5{": "[age=5",
        "age=6{": "[age=6",
        "age=7{": "[age=7"},
    "farmland": {
        "default{": "farmland[",
        "moisture=0{": "[moisture=0",
        "moisture=1{": "[moisture=1",
        "moisture=2{": "[moisture=2",
        "moisture=3{": "[moisture=3",
        "moisture=4{": "[moisture=4",
        "moisture=5{": "[moisture=5",
        "moisture=6{": "[moisture=6",
        "moisture=7{": "[moisture=7"},
    "furnace": {
        "default{": "furnace[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "lit_furnace": {
        "default{": "furnace[lit=true",
        "facing=north{": "furnace[lit=true,facing=north",
        "facing=east{": "furnace[lit=true,facing=east",
        "facing=south{": "furnace[lit=true,facing=south",
        "facing=west{": "furnace[lit=true,facing=west"},
    "standing_sign": {
        "default{": "sign[",
        "rotation=0{": "[rotation=0",
        "rotation=1{": "[rotation=1",
        "rotation=2{": "[rotation=2",
        "rotation=3{": "[rotation=3",
        "rotation=4{": "[rotation=4",
        "rotation=5{": "[rotation=5",
        "rotation=6{": "[rotation=6",
        "rotation=7{": "[rotation=7",
        "rotation=8{": "[rotation=8",
        "rotation=9{": "[rotation=9",
        "rotation=10{": "[rotation=10",
        "rotation=11{": "[rotation=11",
        "rotation=12{": "[rotation=12",
        "rotation=13{": "[rotation=13",
        "rotation=14{": "[rotation=14",
        "rotation=15{": "[rotation=15"},
    "wooden_door": {
        "default{": "oak_door[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=upper{": "[half=upper",
        "half=lower{": "[half=lower",
        "hinge=left{": "[hinge=left",
        "hinge=right{": "[hinge=right",
        "open=false{": "[open=false",
        "open=true{": "[open=true",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "ladder": {
        "default{": "ladder[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "rail": {
        "default{": "rail[",
        "shape=north_south{": "[shape=north_south",
        "shape=east_west{": "[shape=east_west",
        "shape=ascending_east{": "[shape=ascending_east",
        "shape=ascending_west{": "[shape=ascending_west",
        "shape=ascending_north{": "[shape=ascending_north",
        "shape=ascending_south{": "[shape=ascending_south",
        "shape=south_east{": "[shape=south_east",
        "shape=south_west{": "[shape=south_west",
        "shape=north_west{": "[shape=north_west",
        "shape=north_east{": "[shape=north_east"},
    "stone_stairs": {
        "default{": "cobblestone_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "wall_sign": {
        "default{": "wall_sign[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "lever": {
        "default{": "lever[",
        "facing=down_x{": "[face=ceiling,facing=west",
        "facing=east{": "[face=wall,facing=east",
        "facing=west{": "[face=wall,facing=west",
        "facing=south{": "[face=wall,facing=south",
        "facing=north{": "[face=wall,facing=north",
        "facing=up_z{": "[face=floor,facing=north",
        "facing=up_x{": "[face=floor,facing=west",
        "facing=down_z{": "[face=ceiling,facing=north",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "stone_pressure_plate": {
        "default{": "stone_pressure_plate[",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "iron_door": {
        "default{": "iron_door[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=upper{": "[half=upper",
        "half=lower{": "[half=lower",
        "hinge=left{": "[hinge=left",
        "hinge=right{": "[hinge=right",
        "open=false{": "[open=false",
        "open=true{": "[open=true",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "wooden_pressure_plate": {
        "default{": "oak_pressure_plate[",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "lit_redstone_ore": {
        "default{": "redstone_ore[lit=true"},
    "redstone_ore": {
        "default{": "redstone_ore["},
    "unlit_redstone_torch": {
        "default{": "redstone_torch[lit=false",
        "facing=up{": "redstone_torch[lit=false",
        "facing=north{": "redstone_wall_torch[lit=false,facing=north",
        "facing=east{": "redstone_wall_torch[lit=false,facing=east",
        "facing=south{": "redstone_wall_torch[lit=false,facing=south",
        "facing=west{": "redstone_wall_torch[lit=false,facing=west"},
    "redstone_torch": {
        "default{": "redstone_torch[",
        "facing=up{": "redstone_torch[",
        "facing=north{": "redstone_wall_torch[facing=north",
        "facing=east{": "redstone_wall_torch[facing=east",
        "facing=south{": "redstone_wall_torch[facing=south",
        "facing=west{": "redstone_wall_torch[facing=west"},
    "stone_button": {
        "default{": "stone_button[",
        "facing=down{": "[face=ceiling,facing=south",
        "facing=up{": "[face=floor,facing=north",
        "facing=east{": "[face=wall,facing=east",
        "facing=west{": "[face=wall,facing=west",
        "facing=south{": "[face=wall,facing=south",
        "facing=north{": "[face=wall,facing=north",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "snow_layer": {
        "default{": "snow[",
        "layers=1{": "[layers=1",
        "layers=2{": "[layers=2",
        "layers=3{": "[layers=3",
        "layers=4{": "[layers=4",
        "layers=5{": "[layers=5",
        "layers=6{": "[layers=6",
        "layers=7{": "[layers=7",
        "layers=8{": "[layers=8"},
    "ice": {
        "default{": "ice["},
    "snow": {
        "default{": "snow_block["},
    "cactus": {
        "default{": "cactus[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "age=3{": "[age=3",
        "age=4{": "[age=4",
        "age=5{": "[age=5",
        "age=6{": "[age=6",
        "age=7{": "[age=7",
        "age=8{": "[age=8",
        "age=9{": "[age=9",
        "age=10{": "[age=10",
        "age=11{": "[age=11",
        "age=12{": "[age=12",
        "age=13{": "[age=13",
        "age=14{": "[age=14",
        "age=15{": "[age=15"},
    "clay": {
        "default{": "clay["},
    "reeds": {
        "default{": "sugar_cane[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "age=3{": "[age=3",
        "age=4{": "[age=4",
        "age=5{": "[age=5",
        "age=6{": "[age=6",
        "age=7{": "[age=7",
        "age=8{": "[age=8",
        "age=9{": "[age=9",
        "age=10{": "[age=10",
        "age=11{": "[age=11",
        "age=12{": "[age=12",
        "age=13{": "[age=13",
        "age=14{": "[age=14",
        "age=15{": "[age=15"},
    "jukebox": {
        "default{": "jukebox[",
        "has_record=true{": "[has_record=true",
        "has_record=false{": "[has_record=false"},
    "fence": {
        "default{": "oak_fence[",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "pumpkin": {
        "default{": "carved_pumpkin[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "netherrack": {
        "default{": "netherrack["},
    "soul_sand": {
        "default{": "soul_sand["},
    "glowstone": {
        "default{": "glowstone["},
    "portal": {
        "default{": "portal[",
        "axis=x{": "[axis=x",
        "axis=z{": "[axis=z"},
    "lit_pumpkin": {
        "default{": "jack_o_lantern[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "cake": {
        "default{": "cake[",
        "bites=0{": "[bites=0",
        "bites=1{": "[bites=1",
        "bites=2{": "[bites=2",
        "bites=3{": "[bites=3",
        "bites=4{": "[bites=4",
        "bites=5{": "[bites=5",
        "bites=6{": "[bites=6"},
    "unpowered_repeater": {
        "default{": "repeater[",
        "delay=1{": "[delay=1",
        "delay=2{": "[delay=2",
        "delay=3{": "[delay=3",
        "delay=4{": "[delay=4",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "locked=false{": "[locked=false",
        "locked=true{": "[locked=true"},
    "powered_repeater": {
        "default{": "repeater[powered=true",
        "delay=1{": "[delay=1",
        "delay=2{": "[delay=2",
        "delay=3{": "[delay=3",
        "delay=4{": "[delay=4",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "locked=false{": "[locked=false",
        "locked=true{": "[locked=true"},
    "stained_glass": {
        "default{": "white_stained_glass[",
        "color=white{": "white_stained_glass[",
        "color=orange{": "orange_stained_glass[",
        "color=magenta{": "magenta_stained_glass[",
        "color=light_blue{": "light_blue_stained_glass[",
        "color=yellow{": "yellow_stained_glass[",
        "color=lime{": "lime_stained_glass[",
        "color=pink{": "pink_stained_glass[",
        "color=gray{": "gray_stained_glass[",
        "color=silver{": "light_gray_stained_glass[",
        "color=cyan{": "cyan_stained_glass[",
        "color=purple{": "purple_stained_glass[",
        "color=blue{": "blue_stained_glass[",
        "color=brown{": "brown_stained_glass[",
        "color=green{": "green_stained_glass[",
        "color=red{": "red_stained_glass[",
        "color=black{": "black_stained_glass["},
    "trapdoor": {
        "default{": "oak_trapdoor[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "open=true{": "[open=true",
        "open=false{": "[open=false"},
    "monster_egg": {
        "default{": "infested_stone[",
        "variant=stone{": "infested_stone[",
        "variant=cobblestone{": "infested_cobblestone[",
        "variant=stone_brick{": "infested_stone_bricks[",
        "variant=mossy_brick{": "infested_mossy_stone_bricks[",
        "variant=cracked_brick{": "infested_cracked_stone_bricks[",
        "variant=chiseled_brick{": "infested_chiseled_stone_bricks["},
    "stonebrick": {
        "default{": "stone_bricks[",
        "variant=stonebrick{": "stone_bricks[",
        "variant=mossy_stonebrick{": "mossy_stone_bricks[",
        "variant=cracked_stonebrick{": "cracked_stone_bricks[",
        "variant=chiseled_stonebrick{": "chiseled_stone_bricks["},
    "brown_mushroom_block": {
        "default{": "brown_mushroom_block[",
        "variant=all_inside{": "brown_mushroom_block[down=false,east=false,north=false,south=false,up=false,west=false",
        "variant=north_west{": "brown_mushroom_block[down=false,east=false,north=true,south=false,up=true,west=true",
        "variant=north{": "brown_mushroom_block[down=false,east=false,north=true,south=false,up=true,west=false",
        "variant=north_east{": "brown_mushroom_block[down=false,east=true,north=true,south=false,up=true,west=false",
        "variant=west{": "brown_mushroom_block[down=false,east=false,north=false,south=false,up=true,west=true",
        "variant=center{": "brown_mushroom_block[down=false,east=false,north=false,south=false,up=true,west=false",
        "variant=east{": "brown_mushroom_block[down=false,east=true,north=false,south=false,up=true,west=false",
        "variant=south_west{": "brown_mushroom_block[down=false,east=false,north=false,south=true,up=true,west=true",
        "variant=south{": "brown_mushroom_block[down=false,east=false,north=false,south=true,up=true,west=false",
        "variant=south_east{": "brown_mushroom_block[down=false,east=true,north=false,south=true,up=true,west=false",
        "variant=stem{": "mushroom_stem[down=false,east=true,north=true,south=true,up=false,west=true",
        "variant=all_outside{": "brown_mushroom_block[down=true,east=true,north=true,south=true,up=true,west=true",
        "variant=all_stem{": "mushroom_stem[down=false,east=false,north=false,south=false,up=false,west=false"},
    "red_mushroom_block": {
        "default{": "red_mushroom_block[",
        "variant=all_inside{": "red_mushroom_block[down=false,east=false,north=false,south=false,up=false,west=false",
        "variant=north_west{": "red_mushroom_block[down=false,east=false,north=true,south=false,up=true,west=true",
        "variant=north{": "red_mushroom_block[down=false,east=false,north=true,south=false,up=true,west=false",
        "variant=north_east{": "red_mushroom_block[down=false,east=true,north=true,south=false,up=true,west=false",
        "variant=west{": "red_mushroom_block[down=false,east=false,north=false,south=false,up=true,west=true",
        "variant=center{": "red_mushroom_block[down=false,east=false,north=false,south=false,up=true,west=false",
        "variant=east{": "red_mushroom_block[down=false,east=true,north=false,south=false,up=true,west=false",
        "variant=south_west{": "red_mushroom_block[down=false,east=false,north=false,south=true,up=true,west=true",
        "variant=south{": "red_mushroom_block[down=false,east=false,north=false,south=true,up=true,west=false",
        "variant=south_east{": "red_mushroom_block[down=false,east=true,north=false,south=true,up=true,west=false",
        "variant=stem{": "mushroom_stem[down=false,east=true,north=true,south=true,up=false,west=true",
        "variant=all_outside{": "red_mushroom_block[down=true,east=true,north=true,south=true,up=true,west=true",
        "variant=all_stem{": "mushroom_stem[down=false,east=false,north=false,south=false,up=false,west=false"},
    "iron_bars": {
        "default{": "iron_bars[",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "glass_pane": {
        "default{": "glass_pane[",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "melon_block": {
        "default{": "melon_block["},
    "pumpkin_stem": {
        "default{": "pumpkin_stem[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "age=3{": "[age=3",
        "age=4{": "[age=4",
        "age=5{": "[age=5",
        "age=6{": "[age=6",
        "age=7{": "[age=7",
        "facing=up{": "pumpkin_stem[",
        "facing=north{": "attached_pumpkin_stem[facing=north",
        "facing=east{": "attached_pumpkin_stem[facing=east",
        "facing=south{": "attached_pumpkin_stem[facing=south",
        "facing=west{": "attached_pumpkin_stem[facing=west"},
    "melon_stem": {
        "default{": "melon_stem[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "age=3{": "[age=3",
        "age=4{": "[age=4",
        "age=5{": "[age=5",
        "age=6{": "[age=6",
        "age=7{": "[age=7",
        "facing=up{": "melon_stem[",
        "facing=north{": "attached_melon_stem[facing=north",
        "facing=east{": "attached_melon_stem[facing=east",
        "facing=south{": "attached_melon_stem[facing=south",
        "facing=west{": "attached_melon_stem[facing=west"},
    "vine": {
        "default{": "vine[",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "up=true{": "[up=true",
        "up=false{": "[up=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "fence_gate": {
        "default{": "oak_fence_gate[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "in_wall=true{": "[in_wall=true",
        "in_wall=false{": "[in_wall=false",
        "open=true{": "[open=true",
        "open=false{": "[open=false",
        "powered=true{": "[powered=true",
        "powered=false{": "[powered=false"},
    "brick_stairs": {
        "default{": "brick_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "stone_brick_stairs": {
        "default{": "stone_brick_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "mycelium": {
        "default{": "mycelium[",
        "snowy=true{": "grass_block[snowy=true",
        "snowy=false{": "grass_block[snowy=false"},
    "waterlily": {
        "default{": "lily_pad["},
    "nether_brick": {
        "default{": "nether_bricks["},
    "nether_brick_fence": {
        "default{": "nether_brick_fence[",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "nether_brick_stairs": {
        "default{": "nether_brick_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "nether_wart": {
        "default{": "nether_wart[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "age=3{": "[age=3"},
    "enchanting_table": {
        "default{": "enchanting_table["},
    "brewing_stand": {
        "default{": "brewing_stand[",
        "has_bottle_0=true{": "[has_bottle_0=true",
        "has_bottle_0=false{": "[has_bottle_0=false",
        "has_bottle_1=true{": "[has_bottle_1=true",
        "has_bottle_1=false{": "[has_bottle_1=false",
        "has_bottle_2=true{": "[has_bottle_2=true",
        "has_bottle_2=false{": "[has_bottle_2=false"},
    "cauldron": {
        "default{": "cauldron[",
        "level=0{": "[level=0",
        "level=1{": "[level=1",
        "level=2{": "[level=2",
        "level=3{": "[level=3"},
    "end_portal": {
        "default{": "end_portal["},
    "end_portal_frame": {
        "default{": "end_portal_frame[",
        "eye=true{": "[eye=true",
        "eye=false{": "[eye=false",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "end_stone": {
        "default{": "end_stone["},
    "dragon_egg": {
        "default{": "dragon_egg["},
    "redstone_lamp": {
        "default{": "redstone_lamp["},
    "lit_redstone_lamp": {
        "default{": "redstone_lamp[lit=true"},
    "double_wooden_slab": {
        "default{": "oak_slab[type=double",
        "variant=oak{": "oak_slab[type=double",
        "variant=spruce{": "spruce_slab[type=double",
        "variant=birch{": "birch_slab[type=double",
        "variant=jungle{": "jungle_slab[type=double",
        "variant=acacia{": "acacia_slab[type=double",
        "variant=dark_oak{": "dark_oak_slab[type=double"},
    "wooden_slab": {
        "default{": "oak_slab[",
        "variant=oak{": "oak_slab[",
        "variant=spruce{": "spruce_slab[",
        "variant=birch{": "birch_slab[",
        "variant=jungle{": "jungle_slab[",
        "variant=acacia{": "acacia_slab[",
        "variant=dark_oak{": "dark_oak_slab[",
        "half=top{": "[type=top",
        "half=bottom{": "[type=bottom"},
    "cocoa": {
        "default{": "cocoa[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "sandstone_stairs": {
        "default{": "sandstone_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "emerald_ore": {
        "default{": "emerald_ore["},
    "ender_chest": {
        "default{": "ender_chest[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "tripwire_hook": {
        "default{": "tripwire_hook[",
        "attached=true{": "[attached=true",
        "attached=false{": "[attached=false",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "powered=true{": "[powered=true",
        "powered=false{": "[powered=false"},
    "tripwire": {
        "default{": "tripwire[",
        "attached=true{": "[attached=true",
        "attached=false{": "[attached=false",
        "disarmed=true{": "[disarmed=true",
        "disarmed=false{": "[disarmed=false",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false",
        "powered=true{": "[powered=true",
        "powered=false{": "[powered=false"},
    "emerald_block": {
        "default{": "emerald_block["},
    "spruce_stairs": {
        "default{": "spruce_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "birch_stairs": {
        "default{": "birch_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "jungle_stairs": {
        "default{": "jungle_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "command_block": {
        "default{": "command_block[",
        "conditional=true{": "[conditional=true",
        "conditional=false{": "[conditional=false",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "beacon": {
        "default{": "beacon["},
    "cobblestone_wall": {
        "default{": "cobblestone_wall[",
        "variant=cobblestone{": "cobblestone_wall[",
        "variant=mossy_cobblestone{": "mossy_cobblestone_wall[",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "up=true{": "[up=true",
        "up=false{": "[up=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "flower_pot": {
        "default{": "flower_pot[",
        "contents=oak_sapling{": "potted_oak_sapling[",
        "contents=spruce_sapling{": "potted_spruce_sapling[",
        "contents=birch_sapling{": "potted_birch_sapling[",
        "contents=jungle_sapling{": "potted_jungle_sapling[",
        "contents=acacia_sapling{": "potted_acacia_sapling[",
        "contents=dark_oak_sapling{": "potted_dark_oak_sapling[",
        "contents=fern{": "potted_fern[",
        "contents=dandelion{": "potted_dandelion[",
        "contents=poppy{": "potted_poppy[",
        "contents=blue_orchid{": "potted_blue_orchid[",
        "contents=allium{": "potted_allium[",
        "contents=houstonia{": "potted_azure_bluet[",
        "contents=red_tulip{": "potted_red_tulip[",
        "contents=orange_tulip{": "potted_orange_tulip[",
        "contents=white_tulip{": "potted_white_tulip[",
        "contents=pink_tulip{": "potted_pink_tulip[",
        "contents=oxeye_daisy{": "potted_oxeye_daisy[",
        "contents=mushroom_red{": "potted_red_mushroom[",
        "contents=mushroom_brown{": "potted_brown_mushroom[",
        "contents=dead_bush{": "potted_dead_bush[",
        "contents=cactus{": "potted_cactus[",
        "legacy_data=0{": "flower_pot[",
        "legacy_data=1{": "potted_poppy[",
        "legacy_data=2{": "potted_dandelion[",
        "legacy_data=3{": "potted_oak_sapling[",
        "legacy_data=4{": "potted_spruce_sapling[",
        "legacy_data=5{": "potted_birch_sapling[",
        "legacy_data=6{": "potted_jungle_sapling[",
        "legacy_data=7{": "potted_red_mushroom[",
        "legacy_data=8{": "potted_brown_mushroom[",
        "legacy_data=9{": "potted_cactus[",
        "legacy_data=10{": "potted_dead_bush[",
        "legacy_data=11{": "potted_fern[",
        "legacy_data=12{": "potted_acacia_sapling[",
        "legacy_data=13{": "potted_dark_oak_sapling[",
        "legacy_data=14{": "flower_pot[",
        "legacy_data=15{": "flower_pot["},
    "carrots": {
        "default{": "carrots[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "age=3{": "[age=3",
        "age=4{": "[age=4",
        "age=5{": "[age=5",
        "age=6{": "[age=6",
        "age=7{": "[age=7"},
    "potatoes": {
        "default{": "potatoes[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "age=3{": "[age=3",
        "age=4{": "[age=4",
        "age=5{": "[age=5",
        "age=6{": "[age=6",
        "age=7{": "[age=7"},
    "wooden_button": {
        "default{": "oak_button[",
        "facing=down{": "[face=ceiling,facing=south",
        "facing=up{": "[face=floor,facing=north",
        "facing=east{": "[face=wall,facing=east",
        "facing=west{": "[face=wall,facing=west",
        "facing=south{": "[face=wall,facing=south",
        "facing=north{": "[face=wall,facing=north",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "skull": {
        "default{": "skeleton_wall_skull[",
        "facing=down,{SkullType:0": "skeleton_skull[",
        "facing=up,{SkullType:0": "skeleton_skull[",
        "facing=north,{SkullType:0": "skeleton_wall_skull[facing=north",
        "facing=south,{SkullType:0": "skeleton_wall_skull[facing=south",
        "facing=west,{SkullType:0": "skeleton_wall_skull[facing=west",
        "facing=east,{SkullType:0": "skeleton_wall_skull[facing=east",
        "facing=down,{SkullType:1": "wither_skeleton_skull[",
        "facing=up,{SkullType:1": "wither_skeleton_skull[",
        "facing=north,{SkullType:1": "wither_skeleton_wall_skull[facing=north",
        "facing=south,{SkullType:1": "wither_skeleton_wall_skull[facing=south",
        "facing=west,{SkullType:1": "wither_skeleton_wall_skull[facing=west",
        "facing=east,{SkullType:1": "wither_skeleton_wall_skull[facing=east",
        "facing=down,{SkullType:2": "zombie_head[",
        "facing=up,{SkullType:2": "zombie_head[",
        "facing=north,{SkullType:2": "zombie_wall_head[facing=north",
        "facing=south,{SkullType:2": "zombie_wall_head[facing=south",
        "facing=west,{SkullType:2": "zombie_wall_head[facing=west",
        "facing=east,{SkullType:2": "zombie_wall_head[facing=east",
        "facing=down,{SkullType:3": "player_head[",
        "facing=up,{SkullType:3": "player_head[",
        "facing=north,{SkullType:3": "player_wall_head[facing=north",
        "facing=south,{SkullType:3": "player_wall_head[facing=south",
        "facing=west,{SkullType:3": "player_wall_head[facing=west",
        "facing=east,{SkullType:3": "player_wall_head[facing=east",
        "facing=down,{SkullType:4": "creeper_head[",
        "facing=up,{SkullType:4": "creeper_head[",
        "facing=north,{SkullType:4": "creeper_wall_head[facing=north",
        "facing=south,{SkullType:4": "creeper_wall_head[facing=south",
        "facing=west,{SkullType:4": "creeper_wall_head[facing=west",
        "facing=east,{SkullType:4": "creeper_wall_head[facing=east",
        "facing=down,{SkullType:5": "dragon_head[",
        "facing=up,{SkullType:5": "dragon_head[",
        "facing=north,{SkullType:5": "dragon_wall_head[facing=north",
        "facing=south,{SkullType:5": "dragon_wall_head[facing=south",
        "facing=west,{SkullType:5": "dragon_wall_head[facing=west",
        "facing=east,{SkullType:5": "dragon_wall_head[facing=east",
        "facing=down{": "skeleton_skull[",
        "facing=up{": "skeleton_skull[",
        "facing=north{": "skeleton_wall_skull[facing=north",
        "facing=south{": "skeleton_wall_skull[facing=south",
        "facing=west{": "skeleton_wall_skull[facing=west",
        "facing=east{": "skeleton_wall_skull[facing=east",
        "{Rot:0": "[rotation=0",
        "{Rot:1": "[rotation=1",
        "{Rot:2": "[rotation=2",
        "{Rot:3": "[rotation=3",
        "{Rot:4": "[rotation=4",
        "{Rot:5": "[rotation=5",
        "{Rot:6": "[rotation=6",
        "{Rot:7": "[rotation=7",
        "{Rot:8": "[rotation=8",
        "{Rot:9": "[rotation=9",
        "{Rot:10": "[rotation=10",
        "{Rot:11": "[rotation=11",
        "{Rot:12": "[rotation=12",
        "{Rot:13": "[rotation=13",
        "{Rot:14": "[rotation=14",
        "{Rot:15": "[rotation=15",
        "nodrop=true{": "[",
        "nodrop=false{": "["},
    "anvil": {
        "default{": "anvil[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "damage=0{": "anvil[",
        "damage=1{": "chipped_anvil[",
        "damage=2{": "damaged_anvil["},
    "trapped_chest": {
        "default{": "trapped_chest[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "light_weighted_pressure_plate": {
        "default{": "light_weighted_pressure_plate[",
        "power=0{": "[power=0",
        "power=1{": "[power=1",
        "power=2{": "[power=2",
        "power=3{": "[power=3",
        "power=4{": "[power=4",
        "power=5{": "[power=5",
        "power=6{": "[power=6",
        "power=7{": "[power=7",
        "power=8{": "[power=8",
        "power=9{": "[power=9",
        "power=10{": "[power=10",
        "power=11{": "[power=11",
        "power=12{": "[power=12",
        "power=13{": "[power=13",
        "power=14{": "[power=14",
        "power=15{": "[power=15"},
    "heavy_weighted_pressure_plate": {
        "default{": "heavy_weighted_pressure_plate[",
        "power=0{": "[power=0",
        "power=1{": "[power=1",
        "power=2{": "[power=2",
        "power=3{": "[power=3",
        "power=4{": "[power=4",
        "power=5{": "[power=5",
        "power=6{": "[power=6",
        "power=7{": "[power=7",
        "power=8{": "[power=8",
        "power=9{": "[power=9",
        "power=10{": "[power=10",
        "power=11{": "[power=11",
        "power=12{": "[power=12",
        "power=13{": "[power=13",
        "power=14{": "[power=14",
        "power=15{": "[power=15"},
    "unpowered_comparator": {
        "default{": "comparator[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "mode=compare{": "[mode=compare",
        "mode=subtract{": "[mode=subtract",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "powered_comparator": {
        "default{": "comparator[",
        "facing=north{": "[facing=south",
        "facing=east{": "[facing=west",
        "facing=south{": "[facing=north",
        "facing=west{": "[facing=east",
        "mode=compare{": "[mode=compare",
        "mode=subtract{": "[mode=subtract",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "daylight_detector": {
        "default{": "daylight_detector[",
        "power=0{": "[power=0",
        "power=1{": "[power=1",
        "power=2{": "[power=2",
        "power=3{": "[power=3",
        "power=4{": "[power=4",
        "power=5{": "[power=5",
        "power=6{": "[power=6",
        "power=7{": "[power=7",
        "power=8{": "[power=8",
        "power=9{": "[power=9",
        "power=10{": "[power=10",
        "power=11{": "[power=11",
        "power=12{": "[power=12",
        "power=13{": "[power=13",
        "power=14{": "[power=14",
        "power=15{": "[power=15"},
    "redstone_block": {
        "default{": "redstone_block["},
    "quartz_ore": {
        "default{": "nether_quartz_ore["},
    "hopper": {
        "default{": "hopper[",
        "enabled=true{": "[enabled=true",
        "enabled=false{": "[enabled=false",
        "facing=down{": "[facing=down",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "quartz_block": {
        "default{": "quartz_block[",
        "variant=default{": "quartz_block[",
        "variant=chiseled{": "chiseled_quartz_block[",
        "variant=lines_y{": "quartz_pillar[axis=y",
        "variant=lines_x{": "quartz_pillar[axis=x",
        "variant=lines_z{": "quartz_pillar[axis=z"},
    "quartz_stairs": {
        "default{": "quartz_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "activator_rail": {
        "default{": "activator_rail[",
        "shape=north_south{": "[shape=north_south",
        "shape=east_west{": "[shape=east_west",
        "shape=ascending_east{": "[shape=ascending_east",
        "shape=ascending_west{": "[shape=ascending_west",
        "shape=ascending_north{": "[shape=ascending_north",
        "shape=ascending_south{": "[shape=ascending_south",
        "shape=south_east{": "[shape=south_east",
        "shape=south_west{": "[shape=south_west",
        "shape=north_west{": "[shape=north_west",
        "shape=north_east{": "[shape=north_east"},
    "dropper": {
        "default{": "dropper[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down",
        "triggered=true{": "[triggered=true",
        "triggered=false{": "[triggered=false"},
    "stained_hardened_clay": {
        "default{": "white_terracotta[",
        "color=white{": "white_terracotta[",
        "color=orange{": "orange_terracotta[",
        "color=magenta{": "magenta_terracotta[",
        "color=light_blue{": "light_blue_terracotta[",
        "color=yellow{": "yellow_terracotta[",
        "color=lime{": "lime_terracotta[",
        "color=pink{": "pink_terracotta[",
        "color=gray{": "gray_terracotta[",
        "color=silver{": "light_gray_terracotta[",
        "color=cyan{": "cyan_terracotta[",
        "color=purple{": "purple_terracotta[",
        "color=blue{": "blue_terracotta[",
        "color=brown{": "brown_terracotta[",
        "color=green{": "green_terracotta[",
        "color=red{": "red_terracotta[",
        "color=black{": "black_terracotta["},
    "stained_glass_pane": {
        "default{": "white_stained_glass_pane[",
        "color=white{": "white_stained_glass_pane[",
        "color=orange{": "orange_stained_glass_pane[",
        "color=magenta{": "magenta_stained_glass_pane[",
        "color=light_blue{": "light_blue_stained_glass_pane[",
        "color=yellow{": "yellow_stained_glass_pane[",
        "color=lime{": "lime_stained_glass_pane[",
        "color=pink{": "pink_stained_glass_pane[",
        "color=gray{": "gray_stained_glass_pane[",
        "color=silver{": "light_gray_stained_glass_pane[",
        "color=cyan{": "cyan_stained_glass_pane[",
        "color=purple{": "purple_stained_glass_pane[",
        "color=blue{": "blue_stained_glass_pane[",
        "color=brown{": "brown_stained_glass_pane[",
        "color=green{": "green_stained_glass_pane[",
        "color=red{": "red_stained_glass_pane[",
        "color=black{": "black_stained_glass_pane[",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "leaves2": {
        "default{": "acacia_leaves[",
        "variant=acacia{": "acacia_leaves[",
        "variant=dark_oak{": "dark_oak_leaves[",
        "check_decay=true{": "[check_decay=true",
        "check_decay=false{": "[check_decay=false",
        "decayable=true{": "[decayable=true",
        "decayable=false{": "[decayable=false"},
    "log2": {
        "default{": "acacia_log[",
        "variant=acacia,axis=none{": "acacia_bark[",
        "variant=dark_oak,axis=none{": "dark_oak_bark[",
        "variant=acacia{": "acacia_log[",
        "variant=dark_oak{": "dark_oak_log[",
        "axis=x{": "[axis=x",
        "axis=y{": "[axis=y",
        "axis=z{": "[axis=z",
        "axis=none{": "acacia_bark["},
    "acacia_stairs": {
        "default{": "acacia_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "dark_oak_stairs": {
        "default{": "dark_oak_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "slime": {
        "default{": "slime_block["},
    "barrier": {
        "default{": "barrier["},
    "iron_trapdoor": {
        "default{": "iron_trapdoor[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "open=true{": "[open=true",
        "open=false{": "[open=false"},
    "prismarine": {
        "default{": "prismarine[",
        "variant=prismarine{": "prismarine[",
        "variant=prismarine_bricks{": "prismarine_bricks[",
        "variant=dark_prismarine{": "dark_prismarine["},
    "sea_lantern": {
        "default{": "sea_lantern["},
    "hay_block": {
        "default{": "hay_block[",
        "axis=y{": "[axis=y",
        "axis=x{": "[axis=x",
        "axis=z{": "[axis=z"},
    "carpet": {
        "default{": "white_carpet[",
        "color=white{": "white_carpet[",
        "color=orange{": "orange_carpet[",
        "color=magenta{": "magenta_carpet[",
        "color=light_blue{": "light_blue_carpet[",
        "color=yellow{": "yellow_carpet[",
        "color=lime{": "lime_carpet[",
        "color=pink{": "pink_carpet[",
        "color=gray{": "gray_carpet[",
        "color=silver{": "light_gray_carpet[",
        "color=cyan{": "cyan_carpet[",
        "color=purple{": "purple_carpet[",
        "color=blue{": "blue_carpet[",
        "color=brown{": "brown_carpet[",
        "color=green{": "green_carpet[",
        "color=red{": "red_carpet[",
        "color=black{": "black_carpet["},
    "hardened_clay": {
        "default{": "terracotta["},
    "coal_block": {
        "default{": "coal_block["},
    "packed_ice": {
        "default{": "packed_ice["},
    "double_plant": {
        "default{": "sunflower[half=lower",
        "variant=sunflower{": "sunflower[",
        "variant=syringa{": "lilac[",
        "variant=double_grass{": "tall_grass[",
        "variant=double_fern{": "large_fern[",
        "variant=double_rose{": "rose_bush[",
        "variant=paeonia{": "peony[",
        "half=upper{": "[half=upper",
        "half=lower{": "[half=lower",
        "facing=north{": "[",
        "facing=east{": "[",
        "facing=south{": "[",
        "facing=west{": "["},
    "standing_banner": {
        "default{": "black_banner[",
        "{Base:0": "black_banner[",
        "{Base:1": "red_banner[",
        "{Base:2": "green_banner[",
        "{Base:3": "brown_banner[",
        "{Base:4": "blue_banner[",
        "{Base:5": "purple_banner[",
        "{Base:6": "cyan_banner[",
        "{Base:7": "light_gray_banner[",
        "{Base:8": "gray_banner[",
        "{Base:9": "pink_banner[",
        "{Base:10": "lime_banner[",
        "{Base:11": "yellow_banner[",
        "{Base:12": "light_blue_banner[",
        "{Base:13": "magenta_banner[",
        "{Base:14": "orange_banner[",
        "{Base:15": "white_banner[",
        "rotation=0{": "[rotation=0",
        "rotation=1{": "[rotation=1",
        "rotation=2{": "[rotation=2",
        "rotation=3{": "[rotation=3",
        "rotation=4{": "[rotation=4",
        "rotation=5{": "[rotation=5",
        "rotation=6{": "[rotation=6",
        "rotation=7{": "[rotation=7",
        "rotation=8{": "[rotation=8",
        "rotation=9{": "[rotation=9",
        "rotation=10{": "[rotation=10",
        "rotation=11{": "[rotation=11",
        "rotation=12{": "[rotation=12",
        "rotation=13{": "[rotation=13",
        "rotation=14{": "[rotation=14",
        "rotation=15{": "[rotation=15"},
    "wall_banner": {
        "default{": "black_wall_banner[",
        "{Base:0": "black_wall_banner[",
        "{Base:1": "red_wall_banner[",
        "{Base:2": "green_wall_banner[",
        "{Base:3": "brown_wall_banner[",
        "{Base:4": "blue_wall_banner[",
        "{Base:5": "purple_wall_banner[",
        "{Base:6": "cyan_wall_banner[",
        "{Base:7": "light_gray_wall_banner[",
        "{Base:8": "gray_wall_banner[",
        "{Base:9": "pink_wall_banner[",
        "{Base:10": "lime_wall_banner[",
        "{Base:11": "yellow_wall_banner[",
        "{Base:12": "light_blue_wall_banner[",
        "{Base:13": "magenta_wall_banner[",
        "{Base:14": "orange_wall_banner[",
        "{Base:15": "white_wall_banner[",
        "rotation=0{": "[rotation=0",
        "rotation=1{": "[rotation=1",
        "rotation=2{": "[rotation=2",
        "rotation=3{": "[rotation=3",
        "rotation=4{": "[rotation=4",
        "rotation=5{": "[rotation=5",
        "rotation=6{": "[rotation=6",
        "rotation=7{": "[rotation=7",
        "rotation=8{": "[rotation=8",
        "rotation=9{": "[rotation=9",
        "rotation=10{": "[rotation=10",
        "rotation=11{": "[rotation=11",
        "rotation=12{": "[rotation=12",
        "rotation=13{": "[rotation=13",
        "rotation=14{": "[rotation=14",
        "rotation=15{": "[rotation=15"},
    "daylight_detector_inverted": {
        "default{": "daylight_detector[inverted=true",
        "power=0{": "[power=0",
        "power=1{": "[power=1",
        "power=2{": "[power=2",
        "power=3{": "[power=3",
        "power=4{": "[power=4",
        "power=5{": "[power=5",
        "power=6{": "[power=6",
        "power=7{": "[power=7",
        "power=8{": "[power=8",
        "power=9{": "[power=9",
        "power=10{": "[power=10",
        "power=11{": "[power=11",
        "power=12{": "[power=12",
        "power=13{": "[power=13",
        "power=14{": "[power=14",
        "power=15{": "[power=15"},
    "red_sandstone": {
        "default{": "red_sandstone[",
        "type=red_sandstone{": "red_sandstone[",
        "type=chiseled_red_sandstone{": "chiseled_red_sandstone[",
        "type=smooth_red_sandstone{": "cut_red_sandstone["},
    "red_sandstone_stairs": {
        "default{": "red_sandstone_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "double_stone_slab2": {
        "default{": "red_sandstone_slab[type=double",
        "seamless=true,variant=red_sandstone{": "smooth_red_sandstone[",
        "seamless=false,variant=red_sandstone{": "red_sandstone_slab[type=double",
        "variant=red_sandstone{": "red_sandstone_slab[type=double",
        "seamless=false{": "red_sandstone_slab[type=double",
        "seamless=true{": "smooth_red_sandstone["},
    "stone_slab2": {
        "default{": "red_sandstone_slab[",
        "variant=red_sandstone{": "red_sandstone_slab[",
        "half=top{": "[type=top",
        "half=bottom{": "[type=bottom"},
    "spruce_fence_gate": {
        "default{": "spruce_fence_gate[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "in_wall=true{": "[in_wall=true",
        "in_wall=false{": "[in_wall=false",
        "open=true{": "[open=true",
        "open=false{": "[open=false",
        "powered=true{": "[powered=true",
        "powered=false{": "[powered=false"},
    "birch_fence_gate": {
        "default{": "birch_fence_gate[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "in_wall=true{": "[in_wall=true",
        "in_wall=false{": "[in_wall=false",
        "open=true{": "[open=true",
        "open=false{": "[open=false",
        "powered=true{": "[powered=true",
        "powered=false{": "[powered=false"},
    "jungle_fence_gate": {
        "default{": "jungle_fence_gate[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "in_wall=true{": "[in_wall=true",
        "in_wall=false{": "[in_wall=false",
        "open=true{": "[open=true",
        "open=false{": "[open=false",
        "powered=true{": "[powered=true",
        "powered=false{": "[powered=false"},
    "dark_oak_fence_gate": {
        "default{": "dark_oak_fence_gate[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "in_wall=true{": "[in_wall=true",
        "in_wall=false{": "[in_wall=false",
        "open=true{": "[open=true",
        "open=false{": "[open=false",
        "powered=true{": "[powered=true",
        "powered=false{": "[powered=false"},
    "acacia_fence_gate": {
        "default{": "acacia_fence_gate[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "in_wall=true{": "[in_wall=true",
        "in_wall=false{": "[in_wall=false",
        "open=true{": "[open=true",
        "open=false{": "[open=false",
        "powered=true{": "[powered=true",
        "powered=false{": "[powered=false"},
    "spruce_fence": {
        "default{": "spruce_fence[",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "birch_fence": {
        "default{": "birch_fence[",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "jungle_fence": {
        "default{": "jungle_fence[",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "dark_oak_fence": {
        "default{": "dark_oak_fence[",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "acacia_fence": {
        "default{": "acacia_fence[",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "spruce_door": {
        "default{": "spruce_door[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=upper{": "[half=upper",
        "half=lower{": "[half=lower",
        "hinge=left{": "[hinge=left",
        "hinge=right{": "[hinge=right",
        "open=false{": "[open=false",
        "open=true{": "[open=true",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "birch_door": {
        "default{": "birch_door[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=upper{": "[half=upper",
        "half=lower{": "[half=lower",
        "hinge=left{": "[hinge=left",
        "hinge=right{": "[hinge=right",
        "open=false{": "[open=false",
        "open=true{": "[open=true",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "jungle_door": {
        "default{": "jungle_door[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=upper{": "[half=upper",
        "half=lower{": "[half=lower",
        "hinge=left{": "[hinge=left",
        "hinge=right{": "[hinge=right",
        "open=false{": "[open=false",
        "open=true{": "[open=true",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "acacia_door": {
        "default{": "acacia_door[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=upper{": "[half=upper",
        "half=lower{": "[half=lower",
        "hinge=left{": "[hinge=left",
        "hinge=right{": "[hinge=right",
        "open=false{": "[open=false",
        "open=true{": "[open=true",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "dark_oak_door": {
        "default{": "dark_oak_door[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=upper{": "[half=upper",
        "half=lower{": "[half=lower",
        "hinge=left{": "[hinge=left",
        "hinge=right{": "[hinge=right",
        "open=false{": "[open=false",
        "open=true{": "[open=true",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "end_rod": {
        "default{": "end_rod[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "chorus_plant": {
        "default{": "chorus_plant[",
        "down=true{": "[down=true",
        "down=false{": "[down=false",
        "east=true{": "[east=true",
        "east=false{": "[east=false",
        "north=true{": "[north=true",
        "north=false{": "[north=false",
        "south=true{": "[south=true",
        "south=false{": "[south=false",
        "up=true{": "[up=true",
        "up=false{": "[up=false",
        "west=true{": "[west=true",
        "west=false{": "[west=false"},
    "chorus_flower": {
        "default{": "chorus_flower[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "age=3{": "[age=3",
        "age=4{": "[age=4",
        "age=5{": "[age=5"},
    "purpur_block": {
        "default{": "purpur_block["},
    "purpur_pillar": {
        "default{": "purpur_pillar[",
        "axis=y{": "[axis=y",
        "axis=x{": "[axis=x",
        "axis=z{": "[axis=z"},
    "purpur_stairs": {
        "default{": "purpur_stairs[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "half=top{": "[half=top",
        "half=bottom{": "[half=bottom",
        "shape=straight{": "[shape=straight",
        "shape=inner_left{": "[shape=inner_left",
        "shape=inner_right{": "[shape=inner_right",
        "shape=outer_left{": "[shape=outer_left",
        "shape=outer_right{": "[shape=outer_right"},
    "purpur_double_slab": {
        "default{": "purpur_slab[type=double"},
    "purpur_slab": {
        "default{": "purpur_slab[",
        "variant=default{": "purpur_slab[",
        "half=top{": "[type=top",
        "half=bottom{": "[type=bottom"},
    "end_bricks": {
        "default{": "end_stone_bricks["},
    "beetroots": {
        "default{": "beetroots[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "age=3{": "[age=3"},
    "grass_path": {
        "default{": "grass_path["},
    "end_gateway": {
        "default{": "end_gateway["},
    "repeating_command_block": {
        "default{": "repeating_command_block[",
        "conditional=true{": "[conditional=true",
        "conditional=false{": "[conditional=false",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "chain_command_block": {
        "default{": "chain_command_block[",
        "conditional=true{": "[conditional=true",
        "conditional=false{": "[conditional=false",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "frosted_ice": {
        "default{": "frosted_ice[",
        "age=0{": "[age=0",
        "age=1{": "[age=1",
        "age=2{": "[age=2",
        "age=3{": "[age=3"},
    "magma": {
        "default{": "magma_block["},
    "nether_wart_block": {
        "default{": "nether_wart_block["},
    "red_nether_brick": {
        "default{": "red_nether_bricks["},
    "bone_block": {
        "default{": "bone_block[",
        "axis=y{": "[axis=y",
        "axis=x{": "[axis=x",
        "axis=z{": "[axis=z"},
    "structure_void": {
        "default{": "structure_void["},
    "observer": {
        "default{": "observer[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down",
        "powered=false{": "[powered=false",
        "powered=true{": "[powered=true"},
    "white_shulker_box": {
        "default{": "white_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "orange_shulker_box": {
        "default{": "orange_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "magenta_shulker_box": {
        "default{": "magenta_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "light_blue_shulker_box": {
        "default{": "light_blue_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "yellow_shulker_box": {
        "default{": "yellow_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "lime_shulker_box": {
        "default{": "lime_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "pink_shulker_box": {
        "default{": "pink_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "gray_shulker_box": {
        "default{": "gray_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "silver_shulker_box": {
        "default{": "light_gray_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "cyan_shulker_box": {
        "default{": "cyan_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "purple_shulker_box": {
        "default{": "purple_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "blue_shulker_box": {
        "default{": "blue_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "brown_shulker_box": {
        "default{": "brown_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "green_shulker_box": {
        "default{": "green_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "red_shulker_box": {
        "default{": "red_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "black_shulker_box": {
        "default{": "black_shulker_box[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west",
        "facing=up{": "[facing=up",
        "facing=down{": "[facing=down"},
    "white_glazed_terracotta": {
        "default{": "white_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "orange_glazed_terracotta": {
        "default{": "orange_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "magenta_glazed_terracotta": {
        "default{": "magenta_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "light_blue_glazed_terracotta": {
        "default{": "light_blue_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "yellow_glazed_terracotta": {
        "default{": "yellow_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "lime_glazed_terracotta": {
        "default{": "lime_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "pink_glazed_terracotta": {
        "default{": "pink_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "gray_glazed_terracotta": {
        "default{": "gray_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "silver_glazed_terracotta": {
        "default{": "light_gray_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "cyan_glazed_terracotta": {
        "default{": "cyan_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "purple_glazed_terracotta": {
        "default{": "purple_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "blue_glazed_terracotta": {
        "default{": "blue_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "brown_glazed_terracotta": {
        "default{": "brown_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "green_glazed_terracotta": {
        "default{": "green_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "red_glazed_terracotta": {
        "default{": "red_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "black_glazed_terracotta": {
        "default{": "black_glazed_terracotta[",
        "facing=north{": "[facing=north",
        "facing=east{": "[facing=east",
        "facing=south{": "[facing=south",
        "facing=west{": "[facing=west"},
    "concrete": {
        "default{": "white_concrete[",
        "color=white{": "white_concrete[",
        "color=orange{": "orange_concrete[",
        "color=magenta{": "magenta_concrete[",
        "color=light_blue{": "light_blue_concrete[",
        "color=yellow{": "yellow_concrete[",
        "color=lime{": "lime_concrete[",
        "color=pink{": "pink_concrete[",
        "color=gray{": "gray_concrete[",
        "color=silver{": "light_gray_concrete[",
        "color=cyan{": "cyan_concrete[",
        "color=purple{": "purple_concrete[",
        "color=blue{": "blue_concrete[",
        "color=brown{": "brown_concrete[",
        "color=green{": "green_concrete[",
        "color=red{": "red_concrete[",
        "color=black{": "black_concrete["},
    "concrete_powder": {
        "default{": "white_concrete_powder[",
        "color=white{": "white_concrete_powder[",
        "color=orange{": "orange_concrete_powder[",
        "color=magenta{": "magenta_concrete_powder[",
        "color=light_blue{": "light_blue_concrete_powder[",
        "color=yellow{": "yellow_concrete_powder[",
        "color=lime{": "lime_concrete_powder[",
        "color=pink{": "pink_concrete_powder[",
        "color=gray{": "gray_concrete_powder[",
        "color=silver{": "light_gray_concrete_powder[",
        "color=cyan{": "cyan_concrete_powder[",
        "color=purple{": "purple_concrete_powder[",
        "color=blue{": "blue_concrete_powder[",
        "color=brown{": "brown_concrete_powder[",
        "color=green{": "green_concrete_powder[",
        "color=red{": "red_concrete_powder[",
        "color=black{": "black_concrete_powder["},
    "structure_block": {
        "default{": "structure_block[",
        "mode=data{": "[mode=data",
        "mode=save{": "[mode=save",
        "mode=load{": "[mode=load",
        "mode=corner{": "[mode=corner"},
}
Globals.selectorRe = re.compile(r"^(?:@[pears](?:\[(?:[a-z0-9_]+=(?:!?[a-z0-9_:/-]*)?(?:,[a-z0-9_]+=(?:!?[a-z0-9_:/-]*)?)*)?])?|[^@=\[\]*]+)$", re.I)
Globals.blockStateSetRe = re.compile(r"^(?:(?:[a-z_]+=[a-z0-9_]+)(?:,[a-z_]+=[a-z0-9_]+)*|default)$")
Globals.blockStateTestRe = re.compile(r"^(?:(?:[a-z_]+=[a-z0-9_]+)(?:,[a-z_]+=[a-z0-9_]+)*|default|\*)$")
Globals.scoreRe = re.compile(r"^score_(.{1,16}?)(_min)?$")
Globals.functionRe = re.compile(r"^.+?:[^/]+?(?:/[^/]+?)*$", re.I)
Globals.keyRe = re.compile(r"^(?:[a-z0-9]+|\"[a-z0-9]+\")$", re.I)
_list = list

Globals.python = 2
if type(u"") is str:
    Globals.python = 3
    _map = map
    _filter = filter
    xrange = range
    raw_input = input
    os.getcwdu = os.getcwd
    map = lambda x, y: _list(_map(x, y))
    filter = lambda x, y: _list(_filter(x, y))
    unicode = lambda x: x.__unicode__()


def escape(s):
    return s.replace("\\", "\\\\").replace("\"", "\\\"")


def unEscape(s):
    return s.replace("\\\\", "\\").replace("\\\"", "\"")


def noNamespace(s):
    return s[10:] if s[:10] == "minecraft:" else s


def canAt(data, *labels):
    for label in labels:
        if label in data and data[label][0] == "~":
            return True
    return False


def getKey(s):
    colon = s.find(':')
    if colon == -1:
        raise SyntaxError(u"No colon found after key: '{}'".format(s))
    key = s[:colon].strip()
    if not Globals.keyRe.match(key):
        raise SyntaxError(u"Invalid characters in key: '{}'".format(key))
    return key[1:-1] if key[0] == "\"" else key, s[colon+1:]


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
            raise SyntaxError(u"unquoted value can't have '{{' or '[' or '\"' or : in them")
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
    raise SyntaxError(u"Expected ',' or '}}' or ']' but got: '{}'".format(s[0]))


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
            raise SyntaxError(u"Expected ']' or ',' but got: '{}'".format(s[0]))


def signText(s):
    try:
        s = json.JSONDecoder().decode(unEscape(s[1:-1].strip()))
        walk(s)
        return u"\"{}\"".format(escape(json.JSONEncoder(separators=(',', ':')).encode(s)))
    except ValueError:
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
            raise SyntaxError(u"Expected '}}' or ',' but got: \'{}\'".format(s[0]))


def allBlocks(data, blockLabel, nbtLabel=None):
    0/0


def block(data, blockLabel, stateLabel=None, nbtLabel=None):
    block = noNamespace(data[blockLabel])

    if block not in Globals.data2states:
        raise SyntaxError(u"{} is not a valid block".format(block))

    if stateLabel not in data:
        userStates = "default"
    else:
        userStates = data[stateLabel]
    try:
        userStates = int(userStates)
        if not 0 <= userStates <= 15:
            raise SyntaxError(u"{} is outside of range 0..15".format(userStates))
        if userStates in Globals.data2states[block]:
            userStates = Globals.data2states[block][userStates].split(",")
        else:
            userStates = ["default"]
    except ValueError:
        if not Globals.blockStateSetRe.match(userStates):
            raise SyntaxError(u"{} is not a valid block state format".format(data[stateLabel]))
        userStates = userStates.split(",")

    if userStates != ["default"] and len(set(map(lambda x: x.split("=")[0], userStates))) != len(userStates):
        raise SyntaxError(u"Block states \'{}\' contain duplicates".format(",".join(userStates)))

    convDict = Globals.blockStates[block]
    userNBT = data[nbtLabel].copy() if nbtLabel in data else NBTCompound()
    ret = [convDict["default{"], [], userNBT]
    userNBT.stripNumbers()

    for key in sorted(convDict, key=lambda x: len(x) if x != "default{" else 420, reverse=True):
        convFromStates, convFromNBTs = map(lambda x: x.split(",") if x else [], key.split("{"))
        convFromNBTs = dict(map(lambda x: x.split(":", 1), convFromNBTs))
        if all(map(lambda x: x in userStates, convFromStates)) and all(map(lambda x: x[0] in userNBT and userNBT[x[0]] == x[1], convFromNBTs.items())):
            for state in convFromStates:
                userStates.remove(state)
            for nbt in convFromNBTs:
                del userNBT[nbt]
            convToBlock, convToStates = convDict[key].split("[")
            if convToBlock:
                ret[0] = convToBlock
            if convToStates:
                ret[1].extend(convToStates.split(","))

    if userStates:
        if len(userStates) == 1:
            raise SyntaxError(u"{} is not a valid block state of {}".format(userStates[0], block))
        raise SyntaxError(u"{} are not valid block states of {}".format(array(userStates), block))

    return u"{}{}{}".format(ret[0], u"[{}]".format(u",".join(ret[1])) if ret[1] else "", ret[2] if ret[2] else "")


def item(data, nameLabel, damageLabel=None, nbtLabel=None):
    s = noNamespace(data[nameLabel])
    if nbtLabel in data:
        if damageLabel in data and data[damageLabel] != '0':
            data[nbtLabel].data["Damage"] = data[damageLabel]
        return u"{}{}".format(s, data[nbtLabel] if data[nbtLabel].data != NBTCompound().data else "")
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
        if future != 'scores':
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
            scoreRet = u"scores={"
            while i < len(scores) - 1:
                if scores[i][0] == scores[i+1][0]:
                    if scores[i][1] is None:
                        scoreRet += u"{}={},".format(scores[i][0], selectorRange({0: scores[i+1][2], 1: scores[i][2]}, 0, 1))
                    else:
                        scoreRet += u"{}={},".format(scores[i][0], selectorRange({0: scores[i+1][2], 1: scores[i][2]}, 1, 0))
                    i += 1
                elif scores[i][1] is None:
                    scoreRet += u"{}=..{},".format(scores[i][0], scores[i][2])
                else:
                    scoreRet += u"{}={}..,".format(scores[i][0], scores[i][2])
                i += 1
            if scoreRet != "scores={":
                ret.append(scoreRet[:-1] + u'}')

    return ret


def isXp(s):
    s = s[:-1] if s[-1].lower() == 'l' else s
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
    return u"{}".format(total)


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
                    raise AssertionError(u"A Syntax '{}' is defined badly at Word '{}'.\nThis means that I messed up, please send this message to me".format(synt(caller, syntax), word))

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
                    except ValueError as e:
                        raise SyntaxError(u"Token '{}' is not valid JSON: {}".format(workTokens[i], e))
                elif word[1] == '.':
                    pass
                else:
                    raise AssertionError(u"A Syntax '{}' is defined badly at Word '{}'.".format(synt(caller, syntax), word))
            if len(syntax) != len(workTokens):
                raise SyntaxError(u"Too many tokens: Syntax({}): '{}' Tokens({}): {}".format(len(syntax)+1, synt(caller, syntax), len(workTokens)+1, array([caller] + workTokens)))
            return syntax, dict(zip(syntax, workTokens))
        except SyntaxError as ex:
            messages += u"{}\n".format(ex)
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
    tokens[0] = tokens[0].lower().replace("-", "_").replace("?", "help").replace("msg", "w")
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


def stripNBT(value, recursive=True):
    if type(value) not in (unicode, str):
        if recursive and type(value) in (NBTCompound, NBTList):
            value.stripNumbers()
        return value
    try:
        int(value)
        return value
    except ValueError:
        if value[-1] not in ("b", "s", "f", "d"):
            return value
    try:
        int(value[:-1])
        return value[:-1]
    except ValueError:
        if value[-1] not in ("f", "d"):
            return value
        if isNumber(value[:-1]):
            return value[:-1]
        return value


class NBTCompound(dict):
    def __init__(self, *args, **kw):
        super(NBTCompound, self).__init__(*args, **kw)

    def __unicode__(self):
        return u"{{{}}}".format(u",".join([u"{}:{}".format(key, self[key]) for key in self]))

    if Globals.python == 3:
        def __str__(self):
            return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()

    def copy(self):
        return NBTCompound(self)

    def stripNumbers(self):
        for key in self:
            self[key] = stripNBT(self[key])


class NBTList(object):
    def __init__(self):
        self.data = []

    def __unicode__(self):
        return u"[{}]".format(u",".join([unicode(data) for data in self.data]))

    if Globals.python == 3:
        def __str__(self):
            return self.__unicode__()

    def append(self, value):
        self.data.append(value)

    def stripNumbers(self):
        for i in xrange(len(self.data)):
            self.data[i] = stripNBT(self.data[i])


class Selector(object):
    def __init__(self, raw):
        self.raw = raw
        if not Globals.selectorRe.match(raw):
            raise SyntaxError(u"\'{}\' is not a valid selector".format(raw))
        self.data = dict()

        if raw[0] == '@':
            self.target = raw[1]
            self.playerName = False
            if len(raw[3:-1]) > 0:
                for token in raw[3:-1].split(','):
                    key, val = token.split('=')
                    if not len(val) and key not in ("team", "tag"):
                        raise SyntaxError(u"\'{}\' is not a valid selector because {}'s value is empty".format(raw, key))
                    self.data[key] = val

                for key in self.data.keys():
                    if key in ('m', "type"):
                        self.data[key] = self.data[key].lower()
                    if not (Globals.scoreRe.match(key) or key in Globals.selectorArgs):
                        raise SyntaxError(u"\'{}\' is not a valid selector because: \'{}\' is not valid selector argument".format(raw, key))
        else:
            self.target = raw
            self.playerName = True

        self.canAt = False
        for posArg in Globals.posArgs:
            if posArg in self.data:
                self.canAt = True
                break

        for key in ("x", "y", "z", "dx", "dy", "dz", "lm", "l", "rm", "r", "rxm", "rx", "rym", "ry", "c"):
            try:
                if key in self.data:
                    int(self.data[key])
            except ValueError:
                raise SyntaxError(u"Value of \'{}\' in \'{}\' has to be integer".format(key, self.raw))

        for key in self.data:
            if Globals.scoreRe.match(key):
                try:
                    int(self.data[key])
                except ValueError:
                    raise SyntaxError(u"Value of \'{}\' in \'{}\' has to be integer".format(key, self.raw))

        if 'x' in self.data:
            self.data['x'] = int(self.data['x']) + 0.5
        if 'z' in self.data:
            self.data['z'] = int(self.data['z']) + 0.5

        if 'm' in self.data:
            add = ''
            if self.data['m'][0] == '!':
                add = '!'
                self.data['m'] = self.data['m'][1:]
            if self.data['m'] in ("0", "s"):
                self.data['m'] = "survival"
            elif self.data['m'] in ("1", "c"):
                self.data['m'] = "creative"
            elif self.data['m'] in ("2", "a"):
                self.data['m'] = "adventure"
            elif self.data['m'] in ("3", "sp"):
                self.data['m'] = "spectator"
            elif self.data['m'] in ("survival", "creative", "adventure", "spectator"):
                pass
            else:
                raise SyntaxError(u"m\'s value in \'{}\' has to be in (!|)(0|1|2|3|s|c|a|sp|survival|creative|adventure|spectator)".format(self.raw))
            self.data['m'] = add + self.data['m']

        if self.target in ("p", "s"):
            if 'c' in self.data:
                del self.data['c']

        if 'c' in self.data:
            tmp = int(self.data['c'])
            if tmp == 0:
                del self.data['c']
            elif tmp < 0:
                self.data['c'] = -tmp
                if self.target != 'r':
                    self.data["sort"] = "furthest"
            else:
                if self.target in ('a', 'e'):
                    self.data["sort"] = "nearest"

        if "type" in self.data:
            if self.data["type"][0] == "!":
                test = self.data["type"][1:]
            else:
                test = self.data["type"]

            if test not in Globals.summons and test != "player":
                raise SyntaxError(u"\'{}\' is not valid entity type".format(self.data["type"]))

    def __unicode__(self):
        if self.playerName:
            return u"{}".format(self.target)
        if len(self.data.keys()) == 0:
            return u"@{}".format(self.target)
        return u"@{}[{}]".format(self.target, u",".join(futurizeSelector(self.data)))

    def __repr__(self):
        return self.__unicode__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    if Globals.python == 3:
        def __str__(self):
            return self.__unicode__()

    def copy(self):
        ret = Selector("tmp")
        ret.raw = self.raw
        ret.canAt = self.canAt
        ret.target = self.target
        ret.data = dict(self.data)
        ret.playerName = self.playerName
        return ret


class Selectors(object):
    def __init__(self, raw):
        self.selectors = map(Selector, raw.split(' '))
        self.canAt = any(map(lambda x: x.canAt, self.selectors))

    def __unicode__(self):
        return u" ".join(map(unicode, self.selectors))

    if Globals.python == 3:
        def __str__(self):
            return self.__unicode__()


class Master(object):
    def __init__(self):
        self.syntax, self.data = (), {}
        self.canAt, self.canAs = False, False

    def __unicode__(self):
        s = u"{}".format(self.__class__.__name__.replace("_", "-"))
        for key in self.syntax:
            s += u" {}".format(self.data[key] if key[1] != ':' else json.JSONEncoder(separators=(',', ':')).encode(self.data[key]))
        return s

    if Globals.python == 3:
        def __str__(self):
            return self.__unicode__()


class advancement(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(grant|revoke", "<@player", "<(only|until|from|through", "<.advancement", "[.criterion"),
                    ("<(grant|revoke", "<@player", "<(everything"),
                    ("<(test", "<@player", "<.advancement", "[.criterion"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = True, True

    def __unicode__(self):
        if "<(test" in self.data:
            selectorCopy = self.data["<@player"].copy()
            if "[.criterion" not in self.data:
                selectorCopy.data["advancements"] = u"{{{}=true}}".format(self.data["<.advancement"])
            else:
                selectorCopy.data["advancements"] = u"{{{}={{{}=true}}}}".format(self.data["<.advancement"], self.data["[.criterion"])

            return u"execute if entity {}".format(selectorCopy)

        return Master.__unicode__(self)


class ban(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.name", "[*reason"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAs = True


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
        self.canAt = canAt(self.data, "<~x", "<~y", "<~z")

    def __unicode__(self):
        return u"data merge block {} {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"], self.data["<{dataTag"])


class clear(Master):
    def __init__(self, tokens=None):
        Master.__init__(self)
        if tokens:
            syntaxes = (("<@player", "[.item", "[0data", "[0maxCount", "[{dataTag"), )
            self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
            self.canAt, self.canAs = self.data["<@player"].canAt, True

    def __unicode__(self):
        if "<@player" not in self.data:
            return u"clear"
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
                    ("<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z", "<(filtered", "<(force|move|normal", "<.tileName", "[.dataValue"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt = canAt(self.data, "<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z")

    def __unicode__(self):
        s = u"clone {} {} {} {} {} {} {} {} {}".format(self.data["<~x1"], self.data["<~y1"], self.data["<~z1"], self.data["<~x2"], self.data["<~y2"], self.data["<~z2"], self.data["<~x"], self.data["<~y"], self.data["<~z"])
        if "<(filtered" in self.data:
            s += u" filtered {} {}".format(block(self.data,"<.tileName", "[.dataValue", setMode=False), self.data["<(force|move|normal"])
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
        self.canAt, self.canAs = self.data["<@player"].canAt, True


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
        self.canAt, self.canAs = self.data["<@player"].canAt, True

    def __unicode__(self):
        if self.syntax[1] == "<(clear":
            return u"effect clear {}".format(self.data["<@player"])
        s = u"effect give {} {}".format(self.data["<@player"], self.data["<.effect"])
        for key in self.syntax[2:]:
            s += u" {}".format(self.data[key])
        return s


class enchant(Master):  # todo /modifyitem, syntax unknown
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "<.enchantment", "[0level"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@player"].canAt, True


class entitydata(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@entity", "<{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@entity"].canAt, True

    def __unicode__(self):
        return u"data merge entity {} {}".format(self.data["<@entity"], self.data["<{dataTag"])


class execute(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@entity", "<~x", "<~y", "<~z", "<(detect", "<~x2", "<~y2", "<~z2", "<.block", "<.dataValue", "<*command"),
                    ("<@entity", "<~x", "<~y", "<~z", "<*command"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.data["<*command"] = self.data["<*command"][1:] if self.data["<*command"][0] == '/' else self.data["<*command"]
        self.data["<*command"] = decide(self.data["<*command"])
        self.canAt, self.canAs = self.data["<*command"].canAt or self.data["<@entity"].canAt, self.data["<*command"].canAs

    def __unicode__(self):
        command = unicode(self.data["<*command"])
        self.canAt = False if command[:7] == "execute" else self.canAt
        s = u""
        if not '~' == self.data["<~x"] == self.data["<~y"] == self.data["<~z"]:
            s += u" offset {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"])
            self.canAt = True

        if "<(detect" in self.data:
            if self.data["<.dataValue"] in ("-1", "*"):
                coords = u" {} {} {} ".format(self.data["<~x2"], self.data["<~y2"], self.data["<~z2"])
                s += u" if block{}{}".format(coords, u" execute if block{}".format(coords).join(allBlocks(self.data, "<.block")))
            else:
                s += u" if block {} {} {} {}".format(self.data["<~x2"], self.data["<~y2"], self.data["<~z2"], block(self.data, "<.block", "<.dataValue", setMode=False))
            self.canAt = True

        if self.canAt and self.canAs:
            s = u"execute as {} at @s{}".format(self.data["<@entity"], s)
        elif self.canAt and not self.canAs:
            s = u"execute at {}{}".format(self.data["<@entity"], s)
        else:
            s = u"execute as {}{}".format(self.data["<@entity"], s)

        if command[0] == '#':
            s = u"#~ {} {}".format(s, command[3:])
        else:
            if command[:7] == "execute":
                s += command[7:]
            else:
                s += u" run {}".format(command)

        return s


class fill(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<.block", "[.dataValue", "[(destroy|hollow|keep|outline", "[{dataTag"),
                    ("<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<.block", "<.dataValue", "<(replace", "[.replaceTileName", "[.replaceDataValue"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt = canAt(self.data, "<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2")

    def __unicode__(self):
        s = u"fill {} {} {} {} {} {}".format(self.data["<~x1"], self.data["<~y1"], self.data["<~z1"], self.data["<~x2"], self.data["<~y2"], self.data["<~z2"])
        if "<(replace" in self.data:
            s += u" {} replace".format(block(self.data, "<.block", "<.dataValue"))
            if "[.replaceTileName" in self.data:
                s += u" {}".format(block(self.data, "[.replaceTileName", "[.replaceDataValue", setMode=False))
        else:
            s += u" {}".format(block(self.data, "<.block", "[.dataValue", "[{dataTag"))
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
        self.canAt, self.canAs = True, True

    def __unicode__(self):
        if "<(if|unless" not in self.data:
            return u"function {}".format(self.data["<.function"])
        return u"execute {} entity {} run function {}".format(self.data["<(if|unless"], self.data["<@selector"], self.data["<.function"])


class gamemode(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(0|1|2|3|s|c|a|sp|survival|creative|adventure|spectator", "[@player"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        if "[@player" in self.data:
            self.canAt, self.canAs = self.data["[@player"].canAt, True

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
        self.custom = True
        lowered = map(lambda x: x.lower(), Globals.gamerules)
        if self.data["<.rule"].lower() in lowered:
            self.data["<.rule"] = Globals.gamerules[lowered.index(self.data["<.rule"].lower())]
            self.custom = False

    def __unicode__(self):
        if self.custom:
            Globals.commentedOut = True
            return u"#~ {} ||| Custom gamerules are no longer supported".format(Master.__unicode__(self))
        return Master.__unicode__(self)


class give(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "<.item", "[0amount", "[0data", "[{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@player"].canAt, True

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
        self.canAt, self.canAs = self.data["<@player"].canAt, True


class kill(Master):
    def __init__(self, tokens=None):
        Master.__init__(self)
        self.canAt, self.canAs = False, True
        if tokens:
            syntaxes = (("<@player", ), )
            self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
            self.canAt = self.data["<@player"].canAt


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
        self.canAs = True


class op(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@player"].canAt, True


class pardon(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@player"].canAt, True


class pardon_ip(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.address", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)


class particle(Master):  # todo blockcrack
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<({}".format("|".join(Globals.particles)), "<~x", "<~y", "<~z", "<0xd", "<0yd", "<0zd", "<0speed", "[0count", "[.mode", "[@player", "[*params"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = True, "[@player" in self.data


class playsound(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.sound", "<(master|music|record|weather|block|hostile|neutral|player|ambient|voice", "<@player"),
                    ("<.sound", "<(master|music|record|weather|block|hostile|neutral|player|ambient|voice", "<@player", "<~x", "<~y", "<~z", "[0volume", "[0pitch", "[0minimumVolume"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = ("<~x" in self.data and canAt(self.data, "<~x", "<~y", "<~z")) or self.data["<@player"].canAt, True


class publish(Master):
    def __init__(self):
        Master.__init__(self)


class recipe(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(give|take", "<@player", "<.name"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@player"].canAt, True


class reload(Master):
    def __init__(self):
        Master.__init__(self)


class replaceitem(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(block", "<~x", "<~y", "<~z", "<.slot", "<.item", "[0amount", "[0data", "[{dataTag"),
                    ("<(entity", "<@selector", "<.slot", "<.item", "[0amount", "[0data", "[{dataTag"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = (canAt(self.data, "<~x", "<~y", "<~z"), False) if self.syntax == "<(block" else (self.data["<@selector"].canAt, True)

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
        self.canAs = True


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
                    ("<(teams", "<(add", "<.name", "[*displayName"),
                    ("<(teams", "<(join", "<.name", "[*entities"),
                    ("<(teams", "<(remove|empty", "<.name"),
                    ("<(teams", "<(leave", "[*entities"),
                    ("<(teams", "<(option", "<.team", "<(color", "<(black|dark_blue|dark_green|dark_aqua|dark_red|dark_purple|gold|gray|dark_gray|blue|green|aqua|red|light_purple|yellow|white|reset"),
                    ("<(teams", "<(option", "<.team", "<(friendlyfire|seeFriendlyInvisibles", "<(true|false"),
                    ("<(teams", "<(option", "<.team", "<(nametagVisibility|deathMessageVisibility", "<(never|hideForOtherTeams|hideForOwnTeam|always"),
                    ("<(teams", "<(option", "<.team", "<(collisionRule", "<(always|never|pushOwnTeam|pushOtherTeams"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        if "[*entities" in self.data:
            self.data["[*entities"] = Selectors(self.data["[*entities"])
        for word in self.syntax:
            if word[1] == '@' or word == "[*entities":
                self.canAt, self.canAs = self.canAt or self.data[word].canAt, True

    def __unicode__(self):  # todo FakePlayerName, *
        if "<(test" in self.data:
            if "<(*" in self.data:
                Globals.commentedOut = True
                return u"#~ There is no way to convert \'{}\' because of the \'*\'".format(Master.__unicode__(self))
            selectorCopy = self.data["<@entity"].copy()

            low, high = self.data["<.min"], self.data["[.max"] if "[.max" in self.data else u'*'

            if high == '*':
                selectorCopy.data[u"score_{}_min".format(self.data["<.objective"])] = low if low != '*' else "-2147483648"
            elif low == '*':
                selectorCopy.data[u"score_{}".format(self.data["<.objective"])] = high
            else:
                selectorCopy.data[u"score_{}_min".format(self.data["<.objective"])] = low
                selectorCopy.data[u"score_{}".format(self.data["<.objective"])] = high

            return u"execute if entity {}".format(selectorCopy)

        if "<(teams" in self.data:
            s = u"team"
            for key in self.syntax[1:]:
                s += u" {}".format(self.data[key])
            return s

        if "<(tag" in self.data:
            if "[{dataTag" in self.data:
                selectorCopy = self.data["<@entity"].copy()
                selectorCopy.data["nbt"] = unicode(self.data["[{dataTag"])
                end = -1
            else:
                selectorCopy = self.data["<@entity"]
                end = len(self.syntax)
            s = u"tag"
            for key in self.syntax[2:end]:
                s += u" {}".format(self.data[key] if key != "<@entity" else selectorCopy)
            return s

        if "[{dataTag" in self.data:
            selectorCopy = self.data["<@entity"].copy()
            selectorCopy.data["nbt"] = unicode(self.data["[{dataTag"])
            s = u"scoreboard"
            for key in self.syntax[:-1]:
                s += u" {}".format(self.data[key] if key != "<@entity" else selectorCopy)
            return s
        return Master.__unicode__(self)


class seed(Master):
    def __init__(self):
        Master.__init__(self)


class setblock(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x", "<~y", "<~z", "<.block", "[.dataValue", "[(destroy|keep|replace", "[{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt = canAt(self.data, "<~x", "<~y", "<~z")

    def __unicode__(self):
        s = u"setblock {} {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"], block(self.data, "<.block", "[.dataValue", "[{dataTag"))
        if "[(destroy|keep|replace" in self.data and self.data["[(destroy|keep|replace"] != "replace":
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
        self.canAt = canAt(self.data, "<~x", "<~y", "<~z")


class spawnpoint(Master):
    def __init__(self, tokens=None):
        Master.__init__(self)
        if tokens:
            syntaxes = (("<@player", ),
                        ("<@player", "<~x", "<~y", "<~z"))
            self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = "<~x" not in self.data or canAt(self.data, "<~x", "<~y", "<~z"), True


class spreadplayers(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x", "<~z", "<0spreadDistance", "<0maxRange", "<(true|false", "<*player"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = True, True


class stats(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        self.stat = "<({}".format("|".join(Globals.statTags))
        syntaxes = (("<(block", "<~x", "<~y", "<~z", "<(clear", self.stat),
                    ("<(block", "<~x", "<~y", "<~z", "<(set", self.stat, "<@selector", "<.objective"),
                    ("<(entity", "<@selector2", "<(clear", self.stat),
                    ("<(entity", "<@selector2", "<(set", self.stat, "<@selector", "<.objective"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = True, True

    def __unicode__(self):
        Globals.commentedOut = True
        if "<(clear" in self.data:
            return u"#~ {} ||| Clearing a stat is no longer needed".format(Master.__unicode__(self))
        return u"#~ {} ||| Use \'execute store {} score {} {} COMMAND\' on the commands that you want the stats from".format(Master.__unicode__(self), "success" if self.data[self.stat] == "SuccessCount" else "result", self.data["<@selector"], self.data["<.objective"])


class stop(Master):
    def __init__(self):
        Master.__init__(self)


class stopsound(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "[(master|music|record|weather|block|hostile|neutral|player|ambient|voice", "[.sound"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@player"].canAt, True


class summon(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        tokens[0] = noNamespace(tokens[0])
        entityName = "<({}".format("|".join(Globals.summons))
        syntaxes = ((entityName, ),
                    (entityName, "<~x", "<~y", "<~z", "[{dataTag"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt = "<~x" not in self.data or canAt(self.data, "<~x", "<~y", "<~z")


class teleport(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@target", "<~x", "<~y", "<~z"),
                    ("<@target", "<~x", "<~y", "<~z", "<~y-rot", "<~x-rot"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = canAt(self.data, "<~x", "<~y", "<~z", "<~y-rot", "<~x-rot"), True

        if self.data["<@target"] == Selector("@s"):
            self.syntax = self.syntax[1:]

    def __unicode__(self):
        return Master.__unicode__(self).replace("teleport", "tp", 1)


class tellraw(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "<:raw"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@player"].canAt, True


class testfor(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "[{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@player"].canAt, True

    def __unicode__(self):
        if "[{dataTag" in self.data:
            if self.data["<@player"].playerName:
                selectorCopy = Selector(u"@p[name={}]".format(self.data["<@player"]))
            else:
                selectorCopy = self.data["<@player"].copy()
            selectorCopy.data["nbt"] = unicode(self.data["[{dataTag"])
            return u"execute if entity {}".format(selectorCopy)
        return u"execute if entity {}".format(self.data["<@player"])


class testforblock(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x", "<~y", "<~z", "<.block", "[.dataValue", "[{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt = canAt(self.data, "<~x", "<~y", "<~z")

    def __unicode__(self):
        if "[.dataValue" in self.data and self.data["[.dataValue"] in ("-1", "*"):
            coords = u" {} {} {} ".format(self.data["<~x"], self.data["<~y"], self.data["<~z"])
            return u"execute if block{}{}".format(coords, u" execute if block{}".format(coords).join(allBlocks(self.data, "<.block", "[{dataTag", setMode=False)))

        return u"execute if block {} {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"], block(self.data, "<.block", "[.dataValue", "[{dataTag", setMode=False))


class testforblocks(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z", "[(all|masked"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt = canAt(self.data, "<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z")

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
        self.canAt, self.canAs = self.data["<@player"].canAt, True


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
        self.canAt, self.canAs = False if len(self.syntax) < 3 else canAt(self.data, "<~x", "<~y", "<~z", "<~yaw", "<~pitch"), True

    def __unicode__(self):  # todo tp @p @e
        if "<@target" not in self.data or (not self.data["<@target"].playerName and self.data["<@target"].target == 's') or "[@destination" in self.data:
            return Master.__unicode__(self)

        s = u"execute as {}{} teleport {} {} {}".format(self.data["<@target"], u" at @s" if self.canAt else u"", self.data["<~x"], self.data["<~y"], self.data["<~z"])

        if "<~yaw" in self.data:
            s += u" {} {}".format(self.data["<~yaw"], self.data["<~pitch"])

        return s


class trigger(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.objective", "<(add|set", "<0value"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAs = True

    def __unicode__(self):
        if self.data["<(add|set"] == "add" and self.data["<0value"] == '1':
            return u"trigger {}".format(self.data["<.objective"])
        return Master.__unicode__(self)


class w(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "<*message"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@player"].canAt, True


class weather(Master):  # todo warn if duration not specified (changed behaviour from random to 5 min)
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(clear|rain|thunder", "[0duration"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)

        if "[0duration" in self.data:
            Globals.weatherFlag = True


class whitelist(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(add|remove", "<@player"),
                    ("<(on|off|list|reload", ))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        if "<@player" in self.data:
            self.canAt, self.canAs = self.data["<@player"].canAt, True


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
        self.canAt = "<~x" in self.data and canAt(self.data, "<~x", "<~z")


class xp(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<%amount", "[@player"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = "[@player" in self.data and self.data["[@player"].canAt, True

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
                    # Globals.weatherFlag = False
                    lines[lineNumber] = u"{}{}\n".format(line[:start], unicode(decide(line)))
                    if Globals.commentedOut:
                        commentedOutFiles.append((fileName, lineNumber))
                    # if Gloals.weatherFlag:
        except SyntaxError as ex:
            print("File: {}\nLine {}:\n{}".format(fileName, lineNumber + 1, ex))
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
                print('')
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

                elif choice.strip() == '3':  # todo
                    relative = u""
                    found = False
                    currDir = None
                    path = os.getcwdu().split(os.sep)
                    while len(path) >= 2:
                        relative += u"..{}".format(os.sep)
                        currDir = path.pop()
                        currDirFiles = tuple(_ for _ in os.listdir(relative + currDir))
                        if path[-1] == "saves" and all(map(lambda x: x in currDirFiles, ("advancements", "data", "DIM1", "DIM-1", "icon.png", "level.dat", "level.dat_old", "playerdata", "region", "session.lock", "stats"))):
                            print("Found world directory: " + currDir)
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
                                print(u"Found {}".format(what))
                                for namespace in os.listdir(u"data{}{}".format(os.sep, what)):
                                    if os.path.isdir(u"data{0}{2}{0}{1}".format(os.sep, namespace, what)):
                                        if not os.path.isdir(u"data{0}{1}{0}{2}".format(os.sep, namespace, what)):
                                            os.makedirs(u"data{0}{1}{0}{2}".format(os.sep, namespace, what))
                                        for f in os.listdir(u"data{0}{2}{0}{1}".format(os.sep, namespace, what)):
                                            shutil.move(u"data{0}{2}{0}{1}{0}{3}".format(os.sep, namespace, what, f),
                                                        u"data{0}{1}{0}{2}".format(os.sep, namespace, what))
                                        os.removedirs(u"data{0}{2}{0}{1}".format(os.sep, namespace, what))

                        if os.path.isdir(u"structures"):
                            print(u"Found structures")
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
                print(u"\nOutput:\n{}\n".format(decide(raw_input("Input your command here:\n"))))
    except SyntaxError as e:
        print(u"\n{}\n".format(e))

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
                print(u"Some commands were commented out because they have to be converted manually:\n{}".format(u"\n".join(map(lambda x: u"File: {}, Line: {}".format(x[0], x[1]), commentedOutFiles))))
            raw_input("A total of {} commands, across {} files, was converted in {} seconds\n\nPress Enter to exit...".format(Globals.commandCounter, Globals.fileCounter, getTime() - start))
    else:
        raw_input("Press Enter to exit...")
