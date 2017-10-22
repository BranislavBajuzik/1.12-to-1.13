# MCEdit Filter by TheAl_T
# planetminecraft.com/member/theal_t

# Block data value -> block state database by: Onnowhere youtube.com/onnowhere2

import json
from pymclevel import TAG_String
try:
    converter = __import__("1_12to1_13byTheAl_T")
except ImportError:
    converter = False

displayName = "1.12 to 1.13 by TheAl_T"

inputs = (
    ("Convert to 1.12 to 1.13:", "label"),
    ("", "label"),
    ("Important: Run this filter only once. If you run it on already converted commands, it wil fail, because 1.13 syntax is different than 1.12 (Because of the very reason you are using this filter)", "label"),
    ("The way this filter is intended to be used: Turn off Errors, filter, undo, look at the console, fix all errors, filter again and save.", "label"),
    ("", "label"),
    ("", "label"),
    ("Warnings will be printed to the console. They will NOT stop the execution of this script. If you want to do so, tick the next box.", "label"),
    ("Warnings", False),
    ("Errors will be printed to the console. They will stop the execution of this script. If you want to ignore them, un-tick the next box.", "label"),
    ("Errors", True)
)

statTags = ("AffectedBlocks", "AffectedEntities", "AffectedItems", "QueryResult", "SuccessCount")


def perform(level, box, options):
    if not converter:
        raise ImportError("Unable to import main library (1_12to1_13byTheAl_T.py). Please make sure this file is in the same directory as this filter")

    def validate(what, label):
        if "CommandStats" in e:
            s = ""
            tmp = {entry.name: entry.value for entry in e["CommandStats"].value}
            for stat in statTags:
                if stat+"Name" in tmp:
                    s += "execute store {} {} {} ".format("success" if stat == "SuccessCount" else "result", tmp[stat+"Name"], tmp[stat+"Objective"])
            what = s + what

        if len(what) > 32500:
            print "The command at [{}, {}, {}] is too long ({}) after conversion\n(more than 32 500 characters)\n".format(x, y, z, len(what))
            if options["Errors"]:
                raise AssertionError("The command at [{}, {}, {}] is too long ({}) after conversion\n(more than 32 500 characters)".format(x, y, z, len(what)))

        if converter.Globals.commentedOut:
            print "A command at [{}, {}, {}] was commented out because it has to be converted manually\n".format(x, y, z)
            if options["Warnings"]:
                raise AssertionError("A command at [{}, {}, {}] has to be converted manually".format(x, y, z))

        e[label] = TAG_String(what)
        chunk.dirty = True

    def fixCommand():
        command = e["Command"].value.strip()
        if command:
            try:
                converter.Globals.commentedOut = False
                command = unicode(converter.decide(command))
            except SyntaxError, ex:
                print u"Error in block at [{}, {}, {}]:\n{}".format(x, y, z, ex)
                if options["Errors"]:
                    raise SyntaxError(u"Error in block at [{}, {}, {}]:\n{}".format(x, y, z, ex.message))
            validate(command, "Command")

    for (chunk, _, _) in level.getChunkSlices(box):
        for e in chunk.Entities:
            x, y, z = map(lambda x: x.value, e["Pos"].value)
            if (x, y, z) in box and e["id"].value == "minecraft:commandblock_minecart":
                    fixCommand()

        for e in chunk.TileEntities:
            x, y, z = e["x"].value, e["y"].value, e["z"].value
            if (x, y, z) in box:
                if e["id"].value in ("minecraft:command_block", "minecraft:chain_command_block", "minecraft:repeating_command_block"):
                    fixCommand()

                if e["id"].value == "minecraft:sign":
                    for label in ("Text1", "Text2", "Text3", "Text4"):
                        try:
                            converter.Globals.commentedOut = False
                            s = json.JSONDecoder().decode(e[label].value.strip())
                            converter.walk(s)
                            s = json.JSONEncoder(separators=(',', ':')).encode(s)
                        except ValueError:
                            continue
                        except SyntaxError, ex:
                            print u"Error in sign at [{}, {}, {}]:\n{}".format(x, y, z, ex)
                            if options["Errors"]:
                                raise SyntaxError(u"Error in sign at [{}, {}, {}]:\n{}".format(x, y, z, ex.message))
                            continue
                        validate(s, label)
