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

try:
    from data import Globals
except ImportError:
    raise ImportError("Unable to import data library (data.py). Please make sure this file is in the same directory as this one (1_12to1_13.py)")
from time import time as get_time

import json, codecs, os, shutil

_map = map
if type(u"") is str:
    import builtins
    Globals.python = 3
    _list = builtins.list
    _map = builtins.map
    xrange = range
    raw_input = input
    os.getcwdu = os.getcwd
    map = lambda x, y: _list(_map(x, y))
    unicode = lambda x: x.__unicode__() if hasattr(x, '__unicode__') else str(x)
else:
    import __builtin__
    Globals.python = 2
    _list = __builtin__.list


def escape(s):
    return s.replace("\\", "\\\\").replace("\"", "\\\"")


def unEscape(s):
    return s.replace("\\\\", "\\").replace("\\\"", "\"")


def unEscapeJSON(s):
    result = u""
    escaped = False
    for ch in s:
        if ch == "\\":
            escaped = True
            continue
        if escaped and ch in ("\\", "n"):
            result += "\\"
        escaped = False
        result += ch
    return result


def noPrefix(s, prefix="minecraft:"):
    return s[len(prefix):] if s[:len(prefix)] == prefix else s


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
    result = u""
    i = 0
    while True:
        if i == len(s):
            raise SyntaxError(u"Unbalanced brackets (more opened than closed)")
        if s[i] in (',', '}', ']'):
            return result.rstrip(), s[i:]
        if s[i] in ('{', '[', '\"', ':'):
            raise SyntaxError(u"Unquoted value can't have '{{' or '[' or '\"' or : in them")
        result += s[i]
        i += 1


def getQString(s):
    result = u"\""
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
            result += '\"'
            break
        result += s[i]
        i += 1
    s = s[i+1:].lstrip()
    if s[0] in (',', '}', ']'):
        return result.rstrip(), s
    raise SyntaxError(u"Expected ',' or '}}' or ']' but got: '{}'".format(s[0]))


def getList(s):
    result = NBTList()
    if s[0] == "]":
            return result, s[1:].lstrip()
    if s[0] == 'I' and s[1:].lstrip() == ';':
        s = s[s.find(';')+1:]
        result = ["I;"]
    while True:
        data, s = getData(s)
        result.append(data)
        if s[0] == ']':
            return result, s[1:].lstrip()
        if s[0] == ',':
            s = s[1:].lstrip()
        else:
            raise SyntaxError(u"Expected ']' or ',' but got: '{}'".format(s[0]))


def signText(s):
    try:
        s = json.JSONDecoder().decode(unEscape(unEscapeJSON(s[1:-1].strip())))
        walk(s)
        return u"\"{}\"".format(escape(json.JSONEncoder(separators=(',', ':')).encode(s)))
    except ValueError:
        return s


def getCompound(s):
    result = NBTCompound()
    if s[0] == "}":
            return result, s[1:].lstrip()
    while True:
        key, s = getKey(s)
        data, s = getData(s)
        if key == "Command":
            if data[0] == '"':
                result[key] = u"\"{}\"".format(escape(unicode(decide(unEscape(data[1:-1])))))
            else:
                result[key] = unicode(decide(data))
        elif key in ("Text1", "Text2", "Text3", "Text4"):
            result[key] = signText(data)
        elif key == "pages":
            for i, page in enumerate(data.data):
                tmpJSON = json.JSONDecoder().decode(unEscape(page[1:-1].strip()))
                walk(tmpJSON)
                data.data[i] = u"\"{}\"".format(escape(unicode(json.JSONEncoder(separators=(',', ':')).encode(tmpJSON))))
            result[key] = data
        else:
            result[key] = data

        if s[0] == '}':
            return result, s[1:].lstrip()
        if s[0] == ',':
            s = s[1:].lstrip()
        else:
            raise SyntaxError(u"Expected '}}' or ',' but got: \'{}\'".format(s[0]))


def block(data, blockLabel, stateLabel=None, nbtLabel=None):
    userBlock = noPrefix(data[blockLabel])

    if userBlock not in Globals.data2states:
        raise SyntaxError(u"{} is not a valid block".format(userBlock))

    if stateLabel not in data:
        userStates = "default"
    else:
        userStates = data[stateLabel]
    try:
        userStates = int(userStates)
        if not 0 <= userStates <= 15:
            raise SyntaxError(u"{} is outside of range 0..15".format(userStates))
        if userStates in Globals.data2states[userBlock]:
            userStates = Globals.data2states[userBlock][userStates].split(",")
        else:
            userStates = ["default"]
    except ValueError:
        if not Globals.blockStateSetRe.match(userStates):
            raise SyntaxError(u"{} is not a valid block state format for setting a block".format(data[stateLabel]))
        userStates = userStates.split(",")

    if userStates != ["default"]:
        userStates = ["=".join(keyPair) for keyPair in dict(tuple(state.split("=", 1)) for state in userStates).items()]

    convDict = dict(Globals.blockStates[userBlock])
    userNBT = data[nbtLabel].copy() if nbtLabel in data else NBTCompound()
    userNBT.stripNumbers()
    result = ["", set(), userNBT]

    for key in sorted(convDict, key=lambda x: len(x) if x[:7] != "default" else len(x)+420, reverse=True):
        convFromStates, convFromNBTs = map(lambda x: x.split(",") if x else [], key.split("{"))
        convFromNBTs = dict(tuple(x.split(":", 1)) for x in convFromNBTs)
        if all(x in userStates for x in convFromStates) and all(x[0] in userNBT and userNBT[x[0]] == x[1] for x in convFromNBTs.items()):
            for state in convFromStates:
                userStates.remove(state)
            for nbt in convFromNBTs:
                del userNBT[nbt]
            convToBlock, convToStates = convDict[key].split("[")
            if convToBlock:
                result[0] = convToBlock
            if convToStates:
                result[1].update(convToStates.split(","))

    if userStates:
        if len(userStates) == 1:
            raise SyntaxError(u"{} is not a valid block state of {}".format(userStates[0], userBlock))
        raise SyntaxError(u"{} are not valid block states of {}".format(array(userStates), userBlock))

    if not result[0]:
        result[0] = convDict["default{"].split("[")[0]

    if userBlock == "skull" and result[0].find("wall") != -1:
        result[1] = [state for state in result[1] if state[:8] != "rotation"]

    return u"{}{}{}".format(result[0], u"[{}]".format(u",".join(sorted(result[1]))) if result[1] else u"", result[2] if result[2] else u"")


def blockTest(data, blockLabel, stateLabel=None, nbtLabel=None):
    userBlock = noPrefix(data[blockLabel])

    if userBlock not in Globals.data2states:
        raise SyntaxError(u"{} is not a valid block".format(userBlock))

    if stateLabel not in data or data[stateLabel] in ("*", "-1"):
        userStates = ""
    else:
        userStates = data[stateLabel]
    try:
        userStates = int(userStates)
        if not 0 <= userStates <= 15:
            raise SyntaxError(u"{} is outside of range -1..15".format(userStates))
        if userStates in Globals.data2states[userBlock]:
            userStates = Globals.data2states[userBlock][userStates].split(",")
        else:
            userStates = ["default"]
    except ValueError:
        if not Globals.blockStateTestRe.match(userStates):
            raise SyntaxError(u"{} is not a valid block state format".format(data[stateLabel]))
        userStates = userStates.split(",") if userStates else []

    convDict = dict(Globals.blockStates[userBlock])
    userNBT = data[nbtLabel].copy() if nbtLabel in data else NBTCompound()
    results = [set(), set(), userNBT]

    if userStates == ["default"]:
        data[stateLabel] = Globals.blockDefaults[userBlock]
        return blockTest(data, blockLabel, stateLabel, nbtLabel)

    if userBlock in ("double_stone_slab", "double_stone_slab2"):
        for key in convDict:
            if convDict[key][-1] != "[":
                convDict[key] = convDict[key].replace("[", "!") + "]["

    convStates, convNBTs = set(), set()
    for key in convDict:
        states, nbts = key.split("{", 1)
        if states:
            for statePair in states.split(","):
                convStates.update([statePair.split("=", 1)[0]])
        if nbts:
            for nbtPair in nbts.split(","):
                convNBTs.update([nbtPair.split(":", 1)[0]])

    userStates = dict(tuple(state.split("=")) for state in userStates)

    badStates = set(userStates).difference(convStates)
    if badStates:
        if len(badStates) == 1:
            raise SyntaxError(u"{} is not a valid block state of {}".format(_list(badStates)[0], userBlock))
        raise SyntaxError(u"{} are not valid block states of {}".format(array(badStates), userBlock))

    relevantStates, relevantNBTs = convStates.intersection(set(userStates)), convNBTs.intersection(set(userNBT))

    for key in convDict:
        if key[:7] == "default":
            continue
        convFromStates, convFromNBTs = map(lambda x: x.split(",") if x else [], key.split("{", 1))
        convFromStates = dict(tuple(x.split("=", 1)) for x in convFromStates)
        convFromNBTs = dict(tuple(x.split(":", 1)) for x in convFromNBTs)
        convToBlock, convToStates = convDict[key].split("[", 1)

        if userBlock == "double_stone_slab":
            if relevantStates == {"seamless", "variant"}:
                if "variant" in convFromStates and convFromStates["variant"] == userStates["variant"]:
                    if "seamless" in convFromStates and convFromStates["seamless"] == userStates["seamless"]:
                        results[0].update([convToBlock])
                    elif "seamless" not in convFromStates and userStates["seamless"] == "false":
                        results[0].update([convToBlock])
            elif relevantStates == {"variant"}:
                if "variant" in convFromStates and convFromStates["variant"] == userStates["variant"]:
                    results[0].update([convToBlock])
            elif relevantStates == {"seamless"}:
                if "seamless" in convFromStates and convFromStates["seamless"] == userStates["seamless"]:
                    results[0].update([convToBlock])
                elif "seamless" not in convFromStates and userStates["seamless"] == "false":
                    results[0].update([convToBlock])
            else:
                results[0].update([convToBlock])
            continue

        if userBlock == "flower_pot":
            if "legacy_data" in relevantStates:
                if "contents" in convFromStates:
                    continue
            elif "contents" in relevantStates and "legacy_data" in convFromStates:
                continue

        if not any(x in relevantStates for x in convFromStates) and not any(x in convFromNBTs for x in relevantNBTs):
            if convToBlock:
                results[0].update([convToBlock])
            if convToStates:
                results[1].update((tuple(x.split("=", 1)) for x in convToStates.split(",")))
        else:
            if all(x[0] in userStates and userStates[x[0]] == x[1] for x in convFromStates.items()) and \
               (not any(x in convFromNBTs for x in relevantNBTs) or
                 all(x[0] in userNBT and type(userNBT[x[0]]) in (unicode, str) and stripNBT(userNBT[x[0]]) == x[1] for x in convFromNBTs.items())):
                if convToBlock:
                    results[0].update([convToBlock])
                if convToStates:
                    results[1].update((tuple(x.split("=", 1)) for x in convToStates.split(",")))

    for nbt in relevantNBTs:
        del userNBT[nbt]

    if userBlock in ("double_stone_slab", "double_stone_slab2"):
        results[0] = _list(results[0])
        for i in xrange(len(results[0])):
            results[0][i] = results[0][i].replace("!", "[")
    elif userBlock == "skull" and "SkullType" in relevantNBTs:
            if len(results[0]) > 1:
                results[0] = [result for result in results[0] if result[:8] != "skeleton"]

    if not results[0]:
        left, right = convDict["default{"].split("[")
        results[0] = (left, )
        if not results[1] and right:
            results[1].update([tuple(right.split("=", 1))])

    removeStates = {}
    for state, value in results[1]:
        if state not in removeStates:
            removeStates[state] = 1
        else:
            removeStates[state] += 1
    resultStates = []
    for state, value in results[1]:
        if removeStates[state] == 1:
            resultStates.append(u"{}={}".format(state, value))
    results[1] = resultStates

    result = []
    for name in results[0]:
        if userBlock == "skull" and name.find("wall") != -1:
            state = sorted(state for state in results[1] if state[:8] != "rotation")
        else:
            state = sorted(results[1])
        result.append(u"{}{}{}".format(name, u"[{}]".format(u",".join(state)) if results[1] else u"", results[2] if results[2] else u""))
    return result


def item(data, nameLabel, damageLabel=None, nbtLabel=None):
    userItem = noPrefix(data[nameLabel])

    if userItem not in Globals.itemConvert:
        raise SyntaxError(u"{} is not a valid item".format(userItem))

    if damageLabel not in data or int(data[damageLabel]) < 0:
        userDamage = "0"
    else:
        userDamage = data[damageLabel]

    convDict = dict(Globals.itemConvert[userItem])
    userNBT = data[nbtLabel].copy() if nbtLabel in data else NBTCompound()
    userNBT.stripNumbers()
    result = [userItem, userNBT]

    if userItem in Globals.damagable:
        if userDamage != "0":
            userNBT["Damage"] = userDamage
    else:
        if userDamage in convDict:
            result[0] = convDict[userDamage]

        if userItem == "spawn_egg":
            if "EntityTag" in userNBT and "id" in userNBT["EntityTag"]:
                if userNBT["EntityTag"]["id"][0] == "\"":
                    entityFrom = noPrefix(userNBT["EntityTag"]["id"][1:-1])
                else:
                    entityFrom = userNBT["EntityTag"]["id"]

                if entityFrom not in Globals.spawnEggs:
                    raise SyntaxError(u"Invalid entity for a spawn egg: {}".format(entityFrom))

                result[0] = Globals.spawnEggs[entityFrom]
                del userNBT["EntityTag"]["id"]
                if not userNBT["EntityTag"]:
                    del userNBT["EntityTag"]
            else:
                raise SyntaxError(u"Empty spawn eggs were removed".format(userItem))

    return u"{}{}".format(result[0], result[1] if result[1] else u"")


def itemTest(data, nameLabel, damageLabel=None, nbtLabel=None):
    userItem = noPrefix(data[nameLabel])

    if userItem not in Globals.itemConvert:
        raise SyntaxError(u"{} is not a valid item".format(userItem))

    if damageLabel not in data or int(data[damageLabel]) < 0:
        userDamage = "-1"
    else:
        userDamage = data[damageLabel]

    convDict = dict(Globals.itemConvert[userItem])
    userNBT = data[nbtLabel].copy() if nbtLabel in data else NBTCompound()
    results = [[userItem], userNBT]

    if userItem in Globals.damagable:
        if userDamage not in ("-1", "0"):
            userNBT["Damage"] = userDamage

    else:
        if userDamage in convDict:
            results[0] = [convDict[userDamage]]
        elif userDamage == "0":
            results[0] = [userItem]
        elif userDamage == "-1":
            results[0] = _list(convDict.values())
            if "0" not in convDict:
                results[0].append(userItem)
        else:
            raise SyntaxError(u"{} is not a valid damage value for {}".format(userDamage, userItem))

        if userItem == "spawn_egg":
            if "EntityTag" in userNBT and "id" in userNBT["EntityTag"]:
                if userNBT["EntityTag"]["id"][0] == "\"":
                    entityFrom = noPrefix(userNBT["EntityTag"]["id"][1:-1])
                else:
                    entityFrom = userNBT["EntityTag"]["id"]

                if entityFrom not in Globals.spawnEggs:
                    raise SyntaxError(u"Invalid entity for a spawn egg: {}".format(entityFrom))

                results[0] = [Globals.spawnEggs[entityFrom]]
                del userNBT["EntityTag"]["id"]
                if not userNBT["EntityTag"]:
                    del userNBT["EntityTag"]
            else:
                results[0] = _list(Globals.spawnEggs.values())

    return [u"{}{}".format(name, results[1] if results[1] else u"") for name in sorted(results[0])]


def selectorRange(data, low, high):
    if low in data and high in data:
        if data[low] == data[high]:
            return data[low]
        try:
            if int(data[low]) > int(data[high]):
                raise SyntaxError(u"Value of {} ({}) can\'t be greater than value of {} ({})".format(low, data[low], high, data[high]))
        except ValueError:
            pass

    result = u".."
    if low in data:
        result = data[low] + result
    if high in data:
        result += data[high]

    return result


def futurizeSelector(data):
    result = []
    for future, low, high in Globals.selectorArgsNew:
        if future != 'scores':
            tmpRange = selectorRange(data, low, high)
            if tmpRange != "..":
                result.append(u"{}={}".format(future, tmpRange))
        else:
            scores = []
            for key in data.keys():
                res = Globals.scoreRe.match(key)
                if res:
                    if res.group(2):
                        scores.append((res.group(1), res.group(2), data[key]))
                    else:
                        scores.append((res.group(1), "", data[key]))

            scores.sort()
            scores.append(' ')
            i = 0
            scoreRet = u"scores={"
            while i < len(scores) - 1:
                if scores[i][0] == scores[i+1][0]:
                    key1, key2 = u"score_{}".format(scores[i][0]), u"score_{}_min".format(scores[i][0])
                    scoreRet += u"{}={},".format(scores[i][0], selectorRange({key1: scores[i+1][2], key2: scores[i][2]}, key1, key2))
                    i += 1
                elif not scores[i][1]:
                    scoreRet += u"{}=..{},".format(scores[i][0], scores[i][2])
                else:
                    scoreRet += u"{}={}..,".format(scores[i][0], scores[i][2])
                i += 1
            if scoreRet != "scores={":
                result.append(scoreRet[:-1] + u'}')
    return result


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


def constraints(data, rules):
    for label, (low, high) in rules.items():
        if label in data:
            if low == "*":
                low = -2147483648
            if high == "*":
                high = 2147483647
            valueType = type(low)
            try:
                if not (low <= valueType(data[label]) <= high):
                    if low == high:
                        raise SyntaxError(u"{} has to be equal to {}".format(label[2:], low))
                    else:
                        raise SyntaxError(u"{} has to be in range {}..{}".format(label[2:], low, high))
            except ValueError:
                raise SyntaxError(u"{} has to be {}".format(label[2:], u"float" if valueType == float else u"int"))


def walk(node):
    if type(node) == dict:
        for key, child in node.items():
            if type(child) is dict or type(child) is _list:
                walk(child)
            else:
                if key == "action" and child == "run_command" and "value" in node:
                    if node["value"][0] == '/':
                        command = decide(node["value"])
                        if not Globals.flags["multiLine"]:
                            node["value"] = u"/{}".format(command)
                        else:
                            Globals.messages.append(u"Unable to convert this command, {} would span multiple lines".format(node["value"]))
    else:
        for child in node:
            if type(child) is dict or type(child) is _list:
                walk(child)


def synt(caller, syntax):
    return u"{} {}".format(caller, u" ".join(syntax))


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
                    splitted = word[2:].split('|')
                    lowered = map(lambda x: x.lower(), splitted)
                    if workTokens[i].lower() not in lowered:
                        raise SyntaxError(u"Token: '{}' is not in the list: {}".format(workTokens[i], splitted))
                    workTokens[i] = splitted[lowered.index(workTokens[i].lower())]
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
                        workTokens[i] = json.JSONDecoder().decode(unEscapeJSON(workTokens[i]))
                        walk(workTokens[i])
                        break
                    except ValueError as ex:
                        raise SyntaxError(u"Token '{}' is not valid JSON: {}".format(workTokens[i], ex))
                elif word[1] == '.':
                    pass
                else:
                    raise AssertionError(u"A Syntax '{}' is defined badly at Word '{}'.\nThis means that I messed up, please send this message to me".format(synt(caller, syntax), word))
            if len(syntax) != len(workTokens):
                raise SyntaxError(u"Too many tokens: Syntax({}): '{}' Tokens({}): {}".format(len(syntax)+1, synt(caller, syntax), len(workTokens)+1, array([caller] + workTokens)))
            return syntax, dict(zip(syntax, workTokens))
        except SyntaxError as ex:
            messages += u"{}\n".format(ex)
    raise SyntaxError(u"Tokens:\n{}\nDon't match any of Syntaxes:\n{}\nReasons:\n{}\n".format(array([caller] + tokens), "\n".join([synt(caller, syntax) for syntax in syntaxes]), messages))


def tokenize(raw):
    tokens = []
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
            tokens.append(token)
            token = u""
            continue
        token += ch
    tokens.append(token)
    return tokens


def decide(raw):
    Globals.commandCounter += 1
    tokens = [x for x in tokenize(raw.strip()) if x != '']
    if not tokens:
        raise SyntaxError(u"An empty string was provided")

    command = tokens[0].lower()
    tokens[0] = tokens[0].lower().replace("?", "help").replace("msg", "w")
    if tokens[0] == "tell":
        tokens[0] = 'w'

    if tokens[0][0] == '/':
        tokens[0] = tokens[0][1:]

    if tokens[0] not in commandsMap:
        raise SyntaxError(u"{} is not a Minecraft command".format(command))

    try:
        if len(tokens) == 1:
            return commandsMap[tokens[0]]()
        return commandsMap[tokens[0]](tokens[1:])
    except TypeError:
        if len(tokens) == 1:
            raise SyntaxError(u"{} needs arguments".format(command))
        raise SyntaxError(u"{} doesn't take any arguments".format(command))


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


class Selector(object):  # ToDo https://bugs.mojang.com/browse/MC-121740
    def __init__(self, raw):
        self.raw = raw
        if not Globals.selectorRe.match(raw):
            raise SyntaxError(u"\'{}\' is not a valid selector".format(raw))
        self.data = dict()
        self.canAt = False

        if raw[0] != '@':
            self.target = raw
            self.playerName = True
        else:
            self.target = raw[1]
            self.playerName = False
            if len(raw[3:-1]) > 0:
                for token in raw[3:-1].split(','):
                    key, val = token.split('=')
                    if not len(val) and key not in ("team", "tag"):
                        raise SyntaxError(u"\'{}\' is not a valid selector because {}'s value is empty".format(raw, key))
                    self.data[key] = val

                for key in self.data:
                    if key in ('m', "type"):
                        self.data[key] = self.data[key].lower()
                    if not (Globals.scoreRe.match(key) or key in Globals.selectorArgs):
                        raise SyntaxError(u"\'{}\' is not a valid selector because: \'{}\' is not valid selector argument".format(raw, key))

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

            for key in ("rm", "r"):
                if key in self.data:
                    if int(self.data[key]) < 0:
                        self.data[key] = u"0"

            for key in ("rxm", "rx", "rym", "ry"):
                if key in self.data:
                    self.data[key] = unicode(((int(self.data[key])+180) % 360) - 180)

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
                tmpCount = int(self.data['c'])
                if tmpCount == 0 or (self.target == 'r' and tmpCount in (-1, 1)):
                    del self.data['c']
                elif tmpCount < 0:
                    self.data['c'] = str(-tmpCount)
                    if self.target != 'r':
                        self.data["sort"] = "furthest"
                else:
                    if self.target != 'r':
                        self.data["sort"] = "nearest"
            elif Globals.flags["strictSelector"] and self.target in ("a", "e"):
                self.data["sort"] = "nearest"

            if "type" in self.data:
                if self.data["type"][0] == "!":
                    test = self.data["type"][1:]
                else:
                    test = self.data["type"]

                if test not in Globals.summons and test != "player":
                    raise SyntaxError(u"\'{}\' is not valid entity type".format(self.data["type"]))

            for posArg in Globals.posArgs:
                if posArg in self.data:
                    self.canAt = True
                    break

            # validate ranges
            futurizeSelector(self.data)

    def __unicode__(self):
        if self.playerName:
            return u"{}".format(self.target)
        if len(self.data.keys()) == 0:
            return u"@{}".format(self.target)
        return u"@{}[{}]".format(self.target, u",".join(futurizeSelector(self.data)))

    def isSingle(self):
        if self.playerName or self.target in ("s", "p"):
            return True

        if "c" in self.data:
            return self.data["c"] in ("1", "-1")
        return self.target == "r"

    def __repr__(self):
        return self.__unicode__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.canAt == other.canAt and self.data == other.data and self.playerName == other.playerName and self.target == other.target
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    if Globals.python == 3:
        def __str__(self):
            return self.__unicode__()

    def copy(self):
        selectorCopy = Selector("tmp")
        selectorCopy.raw = self.raw
        selectorCopy.canAt = self.canAt
        selectorCopy.target = self.target
        selectorCopy.data = dict(self.data)
        selectorCopy.playerName = self.playerName
        return selectorCopy


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
            if self.data["<@player"].playerName:
                selectorCopy = Selector(u"@p[name={}]".format(self.data["<@player"]))
            else:
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

        if "[.item" in self.data:
            self.item = itemTest(self.data, "[.item", "[0data", "[{dataTag")
        constraints(self.data, {"[0data": (-1, "*"), "[0maxCount": (-1, "*")})

    def __unicode__(self):
        if "<@player" not in self.data:
            return u"clear"
        s = u"clear {}".format(self.data["<@player"])
        if "[.item" in self.data:
            count = u" {}".format(self.data["[0maxCount"]) if "[0maxCount" in self.data else u""
            if len(self.item) > 1:
                Globals.flags["multiLine"] = True
                Globals.messages.append(u"The splitting of this command ({}) "
                                        u"can produce different results if used with stats".format(Master.__unicode__(self)))
            return u"\n".join(u"{} {}{}".format(s, variant, count) for variant in sorted(self.item))
        return s


class clone(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z", "[(masked|replace", "[(force|move|normal"),
                    ("<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z", "<(filtered", "<(force|move|normal", "<.tileName", "[.dataValue"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt = canAt(self.data, "<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z")

        if "<(filtered" in self.data:
            self.block = blockTest(self.data, "<.tileName", "[.dataValue")

    def __unicode__(self):
        s = u"clone {} {} {} {} {} {} {} {} {}".format(self.data["<~x1"], self.data["<~y1"], self.data["<~z1"], self.data["<~x2"], self.data["<~y2"], self.data["<~z2"], self.data["<~x"], self.data["<~y"], self.data["<~z"])
        if "<(filtered" in self.data:
            replace = u" {}".format(self.data["<(force|move|normal"]) if self.data["<(force|move|normal"] != "normal" else u""
            if len(self.block) > 1:
                Globals.flags["multiLine"] = True
                Globals.messages.append(u"The splitting of this command ({}) "
                                        u"can produce different results if used with stats".format(Master.__unicode__(self)))
            return u"\n".join(u"{} filtered {}{}".format(s, variant, replace) for variant in sorted(self.block))
        else:
            for key in self.syntax[9:]:
                if self.data[key] != "normal":
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
        if self.data[s] in ('0', 's'):
            mode = "survival"
        elif self.data[s] in ('1', 'c'):
            mode = "creative"
        elif self.data[s] in ('2', 'a'):
            mode = "adventure"
        elif self.data[s] in ('3', 'sp'):
            mode = "spectator"
        else:
            mode = self.data[s]

        return u"defaultgamemode {}".format(mode)


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
        s = "<(0|1|2|3|p|e|n|h|peaceful|easy|normal|hard"
        if self.data[s] in ('0', 'p'):
            mode = "peaceful"
        elif self.data[s] in ('1', 'e'):
            mode = "easy"
        elif self.data[s] in ('2', 'n'):
            mode = "normal"
        elif self.data[s] in ('3', 'h'):
            mode = "hard"
        else:
            mode = self.data[s]

        return u"difficulty {}".format(mode)


class effect(Master):
    effects = "<({}".format("|".join(map(lambda x: "{}|{}".format(*x), Globals.effects.items())))

    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "<(clear"),
                    ("<@player", effect.effects, "[0seconds", "[0amplifier", "[(true|false"))
        if len(tokens) > 1:
            tokens[1] = noPrefix(tokens[1])
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@player"].canAt, True

        if self.syntax[-1] == "[(true|false" and self.data["[(true|false"] == 'false':
            self.syntax = self.syntax[:-1]

        if self.syntax[-1] == "[0amplifier" and self.data["[0amplifier"] == '0':
            self.syntax = self.syntax[:-1]

        if self.syntax[-1] == "[0seconds" and self.data["[0seconds"] == '30':
            self.syntax = self.syntax[:-1]

        constraints(self.data, {"[0seconds": (0, 1000000), "[0amplifier": (0, 255)})

    def __unicode__(self):
        if "<(clear" in self.data:
            return u"effect clear {}".format(self.data["<@player"])

        if "[0seconds" in self.data and self.data["[0seconds"] == "0":
            return u"effect clear {} {}".format(self.data["<@player"], self.data[effect.effects])

        s = u"effect give {} {}".format(self.data["<@player"], self.data[effect.effects])
        for key in self.syntax[2:]:
            s += u" {}".format(self.data[key])
        return s


class enchant(Master):
    enchants = "<({}".format("|".join(map(lambda x: "{}|{}".format(*x), Globals.enchants.items())))

    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", enchant.enchants, "[0level"), )
        if len(tokens) > 1:
            tokens[1] = noPrefix(tokens[1])
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@player"].canAt, True

        if self.data[enchant.enchants] in Globals.enchants:
            self.data[enchant.enchants] = Globals.enchants[self.data[enchant.enchants]]

        if "[0level" in self.data:
            constraints(self.data, {"[0level": (1, Globals.enchantLevels[self.data[enchant.enchants]])})
            if self.data["[0level"] == "1":
                self.syntax = self.syntax[:-1]


class entitydata(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@entity", "<{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@entity"].canAt, True

    def __unicode__(self):
        if self.data["<@entity"].isSingle():  # ToDo https://bugs.mojang.com/browse/MC-121807
            return u"data merge entity {} {}".format(self.data["<@entity"], self.data["<{dataTag"])
        return u"execute as {} run data merge entity @s {}".format(self.data["<@entity"], self.data["<{dataTag"])


class execute(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        # If the first syntax doesn't match, the second would, but would later fail (obviously) giving misleading error message
        if len(tokens) > 4 and tokens[4] == "detect":
            syntaxes = (("<@entity", "<~x", "<~y", "<~z", "<(detect", "<~x2", "<~y2", "<~z2", "<.block", "<.dataValue", "<*command"), )
        else:
            syntaxes = (("<@entity", "<~x", "<~y", "<~z", "<*command"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)

        self.data["<*command"] = self.data["<*command"][1:] if self.data["<*command"][0] == '/' else self.data["<*command"]
        self.data["<*command"] = decide(self.data["<*command"])

        self.canAt = self.data["<*command"].canAt or self.data["<@entity"].canAt
        self.canAs = not self.data["<@entity"].playerName and self.data["<@entity"].target == "s"

        if "<(detect" in self.data:
            self.canAt = True

            self.block = blockTest(self.data, "<.block", "<.dataValue")

    def __unicode__(self):
        Globals.flags["multiLine"] = False
        command = unicode(self.data["<*command"])
        if not Globals.flags["multiLine"]:
            if "<(detect" in self.data:
                return u"\n".join(self.toString(command, variant) for variant in sorted(self.block))
            return self.toString(command)
        if "<(detect" in self.data:
            return u"\n".join(u"\n".join(self.toString(line, variant) if line[0] != "#" else line for line in command.split("\n")) for variant in sorted(self.block))
        return u"\n".join(self.toString(line) if line[0] != "#" else line for line in command.split("\n"))

    def toString(self, command, variant=None):
        position = u""
        if not '~' == self.data["<~x"] == self.data["<~y"] == self.data["<~z"] and self.canAt:
            position = u" positioned {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"])

        detect = u""
        if "<(detect" in self.data:
            detect = u" if block {} {} {} {}".format(self.data["<~x2"], self.data["<~y2"], self.data["<~z2"], variant)

        if not self.data["<@entity"].playerName and self.data["<@entity"].target == "s":
            selectorArgs = len(self.data["<@entity"].data)

            if self.canAt:
                s = u"execute at {}".format(self.data["<@entity"])
                if position:
                    s += position
            else:
                if selectorArgs:
                    s = u"execute as {}".format(self.data["<@entity"])
                else:
                    s = u"execute"

            s += detect

            if command[:7] == "execute":
                new, old = s.split(" ")[-2:], command.split(" ", 3)[1:3]
                if new[0] == old[0] == "at" and new[1][:2] == old[1][:2] == "@s":
                    if new[1] == "@s":
                        s = s[:-6]
                    elif old[1] == "@s":
                        command = u"execute {}".format(command[14:])

            if s == u"execute":
                return command
        else:
            if self.canAt and self.data["<*command"].canAs:
                s = u"execute as {} at @s".format(self.data["<@entity"])
            elif self.canAt and not self.data["<*command"].canAs:
                s = u"execute at {}".format(self.data["<@entity"])
            else:
                s = u"execute as {}".format(self.data["<@entity"])
            s += position + detect

        if command[:7] == "execute":
            asat, target, rest = command.split(" ", 3)[1:]
            if asat == "at" and target[:2] == "@s":
                if target == "@s":
                    command = u"execute {}".format(rest)

        if command[0] == '#':
            if command[:10] == "#~ execute":
                s = u"#~ {} {}".format(s, command[11:])
            else:
                s = u"#~ {} run {}".format(s, command[3:])
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

        if "<(replace" in self.data:
            self.block = block(self.data, "<.block", "<.dataValue")
            if "[.replaceTileName" in self.data:
                self.replaceBlock = blockTest(self.data, "[.replaceTileName", "[.replaceDataValue")
        else:
            self.block = block(self.data, "<.block", "[.dataValue", "[{dataTag")

    def __unicode__(self):
        s = u"fill {} {} {} {} {} {}".format(self.data["<~x1"], self.data["<~y1"], self.data["<~z1"], self.data["<~x2"], self.data["<~y2"], self.data["<~z2"])
        if "<(replace" in self.data:
            s += u" {} replace".format(self.block)
            if "[.replaceTileName" in self.data:
                if len(self.replaceBlock) > 1:
                    Globals.flags["multiLine"] = True
                    Globals.messages.append(u"The splitting of this command ({}) "
                                            u"can produce different results if used with stats".format(Master.__unicode__(self)))
                return u"\n".join(u"{} {}".format(s, variant) for variant in sorted(self.replaceBlock))
        else:
            s += u" {}".format(self.block)
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
            raise SyntaxError(u"Invalid format of function name: {}".format(self.data["<.function"]))
        self.canAt, self.canAs = True, True

    def __unicode__(self):
        if "<(if|unless" not in self.data:
            return Master.__unicode__(self)

        if self.data["<@selector"] == Selector("@s"):
            if self.data["<(if|unless"] == "if":
                return u"function {}".format(self.data["<.function"])
            Globals.flags["commentedOut"] = True
            return u"#~ {} ||| unless @s will always fail".format(Master.__unicode__(self))
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
        if self.data[s] in ('0', 's'):
            mode = "survival"
        elif self.data[s] in ('1', 'c'):
            mode = "creative"
        elif self.data[s] in ('2', 'a'):
            mode = "adventure"
        elif self.data[s] in ('3', 'sp'):
            mode = "spectator"
        else:
            mode = self.data[s]

        return u"gamemode {}{}".format(mode, u" {}".format(self.data["[@player"]) if "[@player" in self.data else u"")


class gamerule(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.rule", "[.value"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.custom = True
        lowered = map(lambda x: x.lower(), Globals.gamerules)
        if self.data["<.rule"].lower() in lowered:
            self.data["<.rule"] = _list(Globals.gamerules)[lowered.index(self.data["<.rule"].lower())]
            self.custom = False

            if "[.value" in self.data:
                self.data["[.value"] = Globals.gamerules[self.data['<.rule']](self.data['[.value'])

    def __unicode__(self):
        if self.custom:
            Globals.flags["commentedOut"] = True
            return u"#~ {} ||| Custom gamerules are no longer supported".format(Master.__unicode__(self))
        # ToDo gameLoop
        return Master.__unicode__(self)


class give(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@player", "<.item", "[0amount", "[0data", "[{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = self.data["<@player"].canAt, True

        constraints(self.data, {"[0amount": (1, 64)})

        self.item = item(self.data, "<.item", "[0data", "[{dataTag")

    def __unicode__(self):
        s = u"give {} {}".format(self.data["<@player"], self.item)

        if "[0amount" in self.data and self.data["[0amount"] != "1":
            s += u" {}".format(self.data["[0amount"])
        return s


class help(Master):
    helps = "<({}".format("|".join(Globals.commands + map(str, xrange(1, 9))))

    def __init__(self, tokens=None):
        Master.__init__(self)
        if tokens:
            syntaxes = ((help.helps, ), )
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

    def __unicode__(self):
        if "<@player" not in self.data:
            return u"kill @s"
        return u"kill {}".format(self.data["<@player"])


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
        self.canAt = True

    def __unicode__(self):
        if self.data[self.syntax[0]] != "Temple":
            return Master.__unicode__(self)
        Globals.flags["multiLine"] = True
        Globals.messages.append(u"The splitting of this command ({}) "
                                u"can produce different results if used with stats".format(Master.__unicode__(self)))
        return u"locate {}".format(u"\nlocate ".join(('Desert_Pyramid', 'Igloo', 'Jungle_Pyramid', 'Swamp_Hut')))


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


class particle(Master):
    particles = "<({}".format("|".join(Globals.particles.keys()))

    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = ((particle.particles, "<~x", "<~y", "<~z", "<0xd", "<0yd", "<0zd", "<0speed", "[0count", "[.mode", "[@player", "[*params"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = True, "[@player" in self.data

        constraints(self.data, {"<0count": (0., "*")})

        if float(self.data["<0speed"]) < 0:
            self.data["<0speed"] = 0

        if self.syntax[-1] == "[*params":
            self.syntax = self.syntax[:-1]

        if self.syntax[-1] == "[@player" and self.data["[@player"] == Selector("@s"):
            self.syntax = self.syntax[:-1]
            self.canAs = False

        if "[.mode" in self.data:
            if self.data["[.mode"] != "force":
                self.data["[.mode"] = "normal"

            if self.syntax[-1] == "[.mode" and self.data["[.mode"] == "normal":
                self.syntax = self.syntax[:-1]

        if "[0count" not in self.data:
            self.data["[0count"] = "0"
            self.syntax = self.syntax + ("[0count", )

        if len(self.syntax) < 10 and self.data["<0xd"] == self.data["<0yd"] == self.data["<0zd"] == self.data["<0speed"] == "0" and self.data["[0count"] == "0":
            self.syntax = self.syntax[:4]

        if "[*params" in self.data:
            if self.data[particle.particles] in ("blockdust", "blockcrack", "fallingdust"):
                if len(self.data["[*params"].split(" ")) != 1:
                    raise SyntaxError(u"Only one param is allowed when using the {} particle".format(self.data[particle.particles]))
                try:
                    params = int(self.data["[*params"])
                except ValueError:
                    raise SyntaxError(u"The param '{}' must be an integer".format(self.data["[*params"]))

                modulo = params % 4096
                if modulo not in Globals.value2block:
                    raise SyntaxError(u"There is no block with block value {} ({} % 4096)".format(modulo, self.data["[*params"]))
                self.particleArg = block({"block": Globals.value2block[modulo], "state": str((params - modulo) // 4096)}, "block", "state")

            elif self.data[particle.particles] == "iconcrack":
                params = self.data["[*params"].split(" ")
                if len(params) > 2:
                    raise SyntaxError(u"Only up to two params allowed when using the iconcrack particle")
                try:
                    params = tuple(map(int, self.data["[*params"].split(" ")))
                except ValueError:
                    raise SyntaxError(u"The params '{}' and '{}' must be integers".format(*params))

                if params[0] < 256:
                    if params[0] not in Globals.value2block:
                        raise SyntaxError(u"There is no block with block value {}".format(params[0]))
                    self.particleArg = block({"block": Globals.value2block[params[0]], "state": unicode(params[1]) if len(params) == 2 else "0"}, "block", "state")
                else:
                    if params[0] not in Globals.value2item:
                        raise SyntaxError(u"There is no item with item value {}".format(params[0]))
                    self.particleArg = item({"item": Globals.value2item[params[0]], "damage": unicode(params[1]) if len(params) == 2 else "0"}, "item", "damage")

    def __unicode__(self):
        particleName = self.data[particle.particles]
        if Globals.particles[particleName] is None:
            Globals.flags["commentedOut"] = True
            return u"#~ {} ||| The particle {} was removed".format(Master.__unicode__(self), particleName)

        if particleName in ("blockdust", "blockcrack", "fallingdust", "iconcrack") and "[*params" in self.data:
            return u"particle {} {} {}".format(Globals.particles[particleName], self.particleArg, u" ".join(unicode(self.data[word]) for word in self.syntax[1:]))

        if self.data[particle.particles] in ("mobSpell", "mobSpellAmbient") and self.data["<0speed"] != "0" and self.data["[0count"] == "0":
            s = u"particle {} {} {} {} ".format(Globals.particles[particleName], self.data["<~x"], self.data["<~y"], self.data["<~z"])
            s += u" ".join(_map(self.number, _map(lambda x: float(self.data[x]) * float(self.data["<0speed"]), ("<0xd", "<0yd", "<0zd"))))
            return u"{} {}".format(s, u" ".join(unicode(self.data[word]) for word in self.syntax[7:]))

        if self.data[particle.particles] == "reddust" and self.data["<0speed"] != "0" and self.data["[0count"] == "0":
            return u"particle dust {} {} {} 1 {}".format(self.data["<0xd"], self.data["<0yd"], self.data["<0zd"], u" ".join(unicode(self.data[word]) for word in self.syntax[1:]))

        return u"particle {} {}".format(Globals.particles[particleName], u" ".join(unicode(self.data[word]) for word in self.syntax[1:]))

    @staticmethod
    def number(value):
        if value < 0:
            return "0"
        elif value > 1:
            return "1"
        if int(value) == value:
            return str(int(value))
        return str(value)


class playsound(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<.sound", "<(master|music|record|weather|block|hostile|neutral|player|ambient|voice", "<@player", "<~x", "<~y", "<~z", "[0volume", "[0pitch", "[0minimumVolume"),
                    ("<.sound", "<(master|music|record|weather|block|hostile|neutral|player|ambient|voice", "<@player"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = ("<~x" in self.data and canAt(self.data, "<~x", "<~y", "<~z")) or self.data["<@player"].canAt, True

        constraints(self.data, {"[0volume": (0., '*'), "[0pitch": (0., 2.), "[0minimumVolume": (0., 1.)})


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
    slots = "<({}".format("|".join(Globals.slots))

    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(block", "<~x", "<~y", "<~z", replaceitem.slots, "<.item", "[0amount", "[0data", "[{dataTag"),
                    ("<(entity", "<@selector", replaceitem.slots, "<.item", "[0amount", "[0data", "[{dataTag"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = (canAt(self.data, "<~x", "<~y", "<~z"), False) if self.syntax[0] == "<(block" else (self.data["<@selector"].canAt, True)

        constraints(self.data, {"[0amount": (1, 64)})
        self.item = item(self.data, "<.item", "[0data", "[{dataTag")

        self.data[replaceitem.slots] = noPrefix(self.data[replaceitem.slots], prefix="slot.")

    def __unicode__(self):
        s = u"replaceitem"

        for word in self.syntax[:self.syntax.index("<.item")]:
            s += u" {}".format(self.data[word])

        s += u" {}".format(self.item)

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

        for i in xrange(len(tokens)):
            try:
                if tokens[i][0] == "@":
                    tokens[i] = Selector(tokens[i])
                    self.canAt = self.canAt or tokens[i].canAt
            except SyntaxError:
                pass
        self.data["<*message"] = u" ".join(map(unicode, tokens))


class scoreboard(Master):
    sidebars = "<(list|sidebar|belowName|sidebar.team.{}".format("|sidebar.team.".join(Globals.colors))
    colorsKey = "<(reset|{}".format("|".join(Globals.colors))

    def __init__(self, tokens):
        Master.__init__(self)  # ToDo https://bugs.mojang.com/browse/MC-129892
        syntaxes = (("<(objectives", "<(list"),
                    ("<(objectives", "<(add", "<.objective", "<.criteria", "[*display"),
                    ("<(objectives", "<(remove", "<.objective"),
                    ("<(objectives", "<(setdisplay", scoreboard.sidebars, "[.objective"),

                    ("<(players", "<(list", "[@entity"),
                    ("<(players", "<(list", "[(*"),  # NOT working
                    ("<(players", "<(set|add|remove", "<@entity", "<.objective", "<0score", "[{dataTag"),
                    ("<(players", "<(set|add|remove", "<(*",      "<.objective", "<0score", "[{dataTag"),  # works WITHOUT dataTag
                    ("<(players", "<(reset", "<@entity", "[.objective"),
                    ("<(players", "<(reset", "<(*",      "[.objective"),  # works
                    ("<(players", "<(enable", "<@entity", "<.objective"),
                    ("<(players", "<(enable", "<(*",      "<.objective"),  # works
                    ("<(players", "<(test", "<@entity", "<.objective", "<.min", "[.max"),
                    ("<(players", "<(test", "<(*",      "<.objective", "<.min", "[.max"),  # NOT working
                    ("<(players", "<(operation", "<@targetName", "<.targetObjective", "<(+=|-=|*=|/=|%=|=|<|>|><", "<@selector", "<.objective"),
                    ("<(players", "<(operation", "<(*",          "<.targetObjective", "<(+=|-=|*=|/=|%=|=|<|>|><", "<@selector", "<.objective"),  # NOT working
                    ("<(players", "<(operation", "<@targetName", "<.targetObjective", "<(+=|-=|*=|/=|%=|=|<|>|><", "<(*",        "<.objective"),  # NOT working

                    ("<(players", "<(tag", "<@entity", "<(add|remove", "<.tagName", "[{dataTag"),
                    ("<(players", "<(tag", "<(*",      "<(add|remove", "<.tagName", "[{dataTag"),  # NOT working
                    ("<(players", "<(tag", "<@entity", "<(list"),
                    ("<(players", "<(tag", "<(*",      "<(list"),  # NOT working

                    ("<(teams", "<(list", "[.teamname"),
                    ("<(teams", "<(add", "<.name", "[*displayName"),
                    ("<(teams", "<(join", "<.name", "[*entities"),
                    ("<(teams", "<(remove|empty", "<.name"),
                    ("<(teams", "<(leave", "[*entities"),
                    ("<(teams", "<(option", "<.team", "<(color", scoreboard.colorsKey),
                    ("<(teams", "<(option", "<.team", "<(friendlyfire|seeFriendlyInvisibles", "<(true|false"),
                    ("<(teams", "<(option", "<.team", "<(nametagVisibility|deathMessageVisibility", "<(never|hideForOtherTeams|hideForOwnTeam|always"),
                    ("<(teams", "<(option", "<.team", "<(collisionRule", "<(always|never|pushOwnTeam|pushOtherTeams"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)

        constraints(self.data, {"<0score": ("*", "*")})

        if "<.criteria" in self.data:
            lowered = [x.lower() for x in Globals.criteria]
            if self.data["<.criteria"].lower() not in lowered:
                raise SyntaxError(u"'{}' is not a valid objective type".format(self.data["<.criteria"]))
            self.data["<.criteria"] = Globals.criteria[lowered.index(self.data["<.criteria"].lower())]

            if "[*display" in self.data and len(self.data["[*display"]) > 32:
                raise SyntaxError(u"'{}' is too long for an objective name (32 max)".format(self.data["[*display"]))

            criteria = self.data["<.criteria"]
            if "stat.mineBlock.minecraft." in criteria:
                self.criteria = [u"minecraft.mined:minecraft.{}".format(case) for case in sorted(blockTest({"block": criteria[25:]}, "block"))]
            elif "stat.craftItem.minecraft." in criteria:
                self.criteria = [u"minecraft.crafted:minecraft.{}".format(case) for case in sorted(itemTest({"item": criteria[25:]}, "item"))]
            elif "stat.useItem.minecraft." in criteria:
                self.criteria = [u"minecraft.used:minecraft.{}".format(case) for case in sorted(itemTest({"item": criteria[23:]}, "item"))]
            elif "stat.breakItem.minecraft." in criteria:
                self.criteria = [u"minecraft.broken:minecraft.{}".format(case) for case in sorted(itemTest({"item": criteria[25:]}, "item"))]
            elif "stat.pickup.minecraft." in criteria:
                self.criteria = [u"minecraft.picked_up:minecraft.{}".format(case) for case in sorted(itemTest({"item": criteria[22:]}, "item"))]
            elif "stat.drop.minecraft." in criteria:
                self.criteria = [u"minecraft.dropped:minecraft.{}".format(case) for case in sorted(itemTest({"item": criteria[20:]}, "item"))]
            elif "stat.killEntity." in criteria:
                self.criteria = [u"minecraft.killed:minecraft.{}".format(Globals.entityCriteria[criteria[16:]])]
            elif "stat.entityKilledBy." in criteria:
                self.criteria = [u"minecraft.killed_by:minecraft.{}".format(Globals.entityCriteria[criteria[20:]])]
            elif "stat." in criteria:
                self.criteria = [u"minecraft.custom:minecraft.{}".format(Globals.miscCriteria[criteria[5:]])]
            else:
                self.criteria = [self.data["<.criteria"]]
            self.data["<.criteria"] = u"{}"

        if "<.min" in self.data:
            rules = {}
            if self.data["<.min"] != "*":
                rules["<.min"] = ("*", "*")
            if "[.max" in self.data and self.data["[.max"] != "*":
                rules["[.max"] = ("*", "*")
            constraints(self.data, rules)

        if "[*entities" in self.data:
            self.data["[*entities"] = Selectors(self.data["[*entities"])

        for word in self.syntax:
            if word[1] == '@' or word == "[*entities":
                self.canAt, self.canAs = self.canAt or self.data[word].canAt, True

    def __unicode__(self):
        Globals.flags["multiLine"] = False
        if "<.criteria" not in self.data:
            return self.toString()

        if len(self.criteria) == 1:
            return self.toString().format(self.criteria[0])

        Globals.flags["multiLine"] = True
        Globals.messages.append(u"This command ({}) was split because the criteria was split. "
                                u"You need to split all the commands that refer to this objective".format(Master.__unicode__(self)))
        return u"\n".join(self.toString().format(criteria) for criteria in self.criteria)

    def toString(self):
        if any(map(lambda x: x[2] == '*', self.syntax)):
            if self.syntax[1] in ("<(list", "<(test", "<(operation", "<(tag") or "[{dataTag" in self.data:
                Globals.flags["commentedOut"] = True
                return u"#~ There is no way to convert \'{}\' because of the \'*\'".format(Master.__unicode__(self))

        if "<(test" in self.data:
            low = self.data["<.min"] if self.data["<.min"] != "*" else u"" if "[.max" in self.data else u"-2147483648"
            high = self.data["[.max"] if "[.max" in self.data and self.data["[.max"] != "*" else u""
            if low == high == u"":
                low = u"-2147483648"

            return u"execute if score {} {} matches {}..{}".format(self.data["<@entity"], self.data["<.objective"], low, high)

        if "<(list" in self.data and "[@entity" in self.data and not self.data["[@entity"].isSingle():
            Globals.flags["commentedOut"] = True
            return u"#~ The list option in \'{}\' no longer allows for selectors that can target multiple entities.".format(Master.__unicode__(self))

        end = len(self.syntax)
        if "[{dataTag" in self.data:
            if self.data["<@entity"].playerName:
                selectorCopy = Selector(u"@p[name={}]".format(self.data["<@entity"]))
            else:
                selectorCopy = self.data["<@entity"].copy()
            selectorCopy.data["nbt"] = unicode(self.data["[{dataTag"])
            end = -1
        elif "<@entity" in self.data:
            selectorCopy = self.data["<@entity"]
        else:
            selectorCopy = u"ThisWillNeverHappen"

        if "<(teams" in self.data:
            s = u"team"
            syntax = self.syntax[1:]
        elif "<(tag" in self.data:
            s = u"tag"
            syntax = self.syntax[2:end]
        else:
            s = u"scoreboard"
            syntax = self.syntax[:end]

        for key in syntax:
            s += u" {}".format(self.data[key] if key != "<@entity" else selectorCopy)
        return s


class seed(Master):
    def __init__(self):
        Master.__init__(self)


class setblock(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x", "<~y", "<~z", "<.block", "[.dataValue", "[(destroy|keep|replace", "[{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt = canAt(self.data, "<~x", "<~y", "<~z")

        self.block = block(self.data, "<.block", "[.dataValue", "[{dataTag")

    def __unicode__(self):
        s = u"setblock {} {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"], self.block)
        if "[(destroy|keep|replace" in self.data and self.data["[(destroy|keep|replace"] != "replace":
            s += u" {}".format(self.data["[(destroy|keep|replace"])
        return s


class setidletimeout(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<0minutes", ), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)

        constraints(self.data, {"<0minutes": (0, "*")})


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

        constraints(self.data, {"<0spreadDistance": (0., "*"), "<0maxRange": (float(self.data["<0spreadDistance"])+1, "*")})

        self.data["<*player"] = Selectors(self.data["<*player"])


class stats(Master):
    stat = "<({}".format("|".join(Globals.statTags))

    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(block", "<~x", "<~y", "<~z", "<(clear", stats.stat),
                    ("<(block", "<~x", "<~y", "<~z", "<(set", stats.stat, "<@selector", "<.objective"),
                    ("<(entity", "<@selector2", "<(clear", stats.stat),
                    ("<(entity", "<@selector2", "<(set", stats.stat, "<@selector", "<.objective"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)

    def __unicode__(self):
        Globals.flags["commentedOut"] = True
        if "<(clear" in self.data:
            return u"#~ {} ||| Clearing a stat is no longer needed".format(Master.__unicode__(self))
        if "<@selector2" in self.data:
            return u"#~ {} ||| Use \'execute as {} at @s store {} score {} {} run COMMAND\' on the commands that you want the stats from".format(
                Master.__unicode__(self), self.data["<@selector2"], "success" if self.data[stats.stat] == "SuccessCount" else "result", self.data["<@selector"], self.data["<.objective"])
        return u"#~ {} ||| Use \'execute store {} score {} {} run COMMAND\' on the commands that you want the stats from".format(
            Master.__unicode__(self), "success" if self.data[stats.stat] == "SuccessCount" else "result", self.data["<@selector"], self.data["<.objective"])


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
    summons = "<({}".format("|".join(Globals.summons))

    def __init__(self, tokens):
        Master.__init__(self)
        tokens[0] = noPrefix(tokens[0])
        syntaxes = ((summon.summons, ),
                    (summon.summons, "<~x", "<~y", "<~z", "[{dataTag"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt = "<~x" not in self.data or canAt(self.data, "<~x", "<~y", "<~z")

    def __unicode__(self):
        entity = self.data[summon.summons]
        if entity in Globals.summonMap:
            entity = Globals.summonMap[entity]

        result = u"summon {}".format(entity)
        for word in self.syntax[1:]:
            result += u" {}".format(self.data[word])

        return result


class teleport(Master):  # ToDo https://bugs.mojang.com/browse/MC-124686
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<@target", "<~x", "<~y", "<~z"),
                    ("<@target", "<~x", "<~y", "<~z", "<~yaw", "<~pitch"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = canAt(self.data, "<~x", "<~y", "<~z", "<~yaw", "<~pitch") or self.data["<@target"].canAt, True

        if "<~yaw" not in self.data and self.data["<@target"] == Selector("@s"):
            self.syntax = self.syntax[1:]


class tp(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x", "<~y", "<~z"),
                    ("<~x", "<~y", "<~z", "<~yaw", "<~pitch"),
                    ("<@target", "[@destination"),
                    ("<@target", "<~x", "<~y", "<~z"),
                    ("<@target", "<~x", "<~y", "<~z", "<~yaw", "<~pitch"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = canAt(self.data, "<~x", "<~y", "<~z", "<~yaw", "<~pitch"), True
        if "<@target" in self.data:
            self.canAt = self.canAt or self.data["<@target"].canAt

            if "[@destination" in self.data:
                if not self.data["[@destination"].isSingle():
                    raise SyntaxError(u"Destination (\'{}\') can only target one entity.".format(self.data["[@destination"]))
                self.canAt = self.canAt or self.data["[@destination"].canAt

    def __unicode__(self):
        if "<@target" not in self.data:
            if "<~yaw" in self.data:
                return Master.__unicode__(self).replace("tp", "teleport @s", 1)
            return Master.__unicode__(self).replace("tp", "teleport", 1)

        if len(self.syntax) > 1 and "<~yaw" not in self.data and self.data["<@target"] == Selector("@s"):
            return Master.__unicode__(self).replace("tp @s", "teleport", 1)

        if self.data["<@target"] == Selector("@s") or "<~x" not in self.data or not self.canAt:
            return Master.__unicode__(self).replace("tp", "teleport", 1)

        s = u"execute as {}".format(self.data["<@target"])

        if self.canAt:
            s += u" at @s"

        s += u" run teleport"

        if "<~yaw" in self.data:
            s += u" @s"

        s += u" {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"])

        if "<~yaw" in self.data:
            s += u" {} {}".format(self.data["<~yaw"], self.data["<~pitch"])

        return s


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
        if self.data["<@player"].playerName:
            if "[{dataTag" in self.data:
                selectorCopy = Selector(u"@p[name={}]".format(self.data["<@player"]))
            else:
                selectorCopy = self.data["<@player"]
        else:
            selectorCopy = self.data["<@player"].copy()
            if "c" not in self.data["<@player"].data and self.data["<@player"].target not in ('s', 'p'):
                selectorCopy.data['limit'] = "1"

        if "[{dataTag" in self.data:
            selectorCopy.data["nbt"] = unicode(self.data["[{dataTag"])
        return u"execute if entity {}".format(selectorCopy)


class testforblock(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x", "<~y", "<~z", "<.block", "[.dataValue", "[{dataTag"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt = canAt(self.data, "<~x", "<~y", "<~z")

        self.block = blockTest(self.data, "<.block", "[.dataValue", "[{dataTag")

    def __unicode__(self):
        if len(self.block) > 1:
            Globals.flags["multiLine"] = True
            Globals.messages.append(u"The splitting of this command ({}) "
                                    u"can produce different results if used with stats".format(Master.__unicode__(self)))
        return u"\n".join(u"execute if block {} {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"], variant) for variant in sorted(self.block))


class testforblocks(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z", "[(all|masked"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt = canAt(self.data, "<~x1", "<~y1", "<~z1", "<~x2", "<~y2", "<~z2", "<~x", "<~y", "<~z")

    def __unicode__(self):
        return u"execute if blocks {} {} {} {} {} {} {} {} {} {}".format(self.data["<~x1"], self.data["<~y1"], self.data["<~z1"], self.data["<~x2"], self.data["<~y2"], self.data["<~z2"], self.data["<~x"], self.data["<~y"], self.data["<~z"], self.data["[(all|masked"] if "[(all|masked" in self.data else u"all")


class time(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(add|set", "<0value"),
                    ("<(set", "<(day|night"),
                    ("<(query", "<(daytime|gametime|day"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)

        constraints(self.data, {"<0value": (1, "*")})


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
        Globals.flags["commentedOut"] = True
        return u"#~ toggledownfall ||| This command was removed"


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


class weather(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(clear|rain|thunder", "[0duration"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)

        constraints(self.data, {"[0duration": (1, 1000000)})

    def __unicode__(self):
        if "[0duration" not in self.data:
            Globals.messages.append(u"\'{}\' no longer has random duration. The duration is now 5 minutes".format(Master.__unicode__(self)))
        return Master.__unicode__(self)


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
                    ("<(damage", "<(amount|buffer", "<0value"),
                    ("<(warning", "<(distance|time", "<0value"),
                    ("<(get", ))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt = "<~x" in self.data and canAt(self.data, "<~x", "<~z")

        if "<(add|set" in self.data and self.data["<(add|set"] == "set":
            constraints(self.data, {"<0distance": (1., "*")})
        constraints(self.data, {"[0time": (0, "*"), "<0value": (0., "*")})


class xp(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<%amount", "[@player"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = "[@player" in self.data and self.data["[@player"].canAt, True

        if self.data["<%amount"][-1] != "L":
            constraints(self.data, {"<%amount": (0, "*")})
        else:
            constraints({"<%amount": self.data["<%amount"][:-1]}, {"<%amount": ("*", "*")})

    def __unicode__(self):
        player = self.data["[@player"] if "[@player" in self.data else Selector("@s")
        if self.data["<%amount"][-1] == 'L':
            return u"experience add {} {} levels".format(player, self.data["<%amount"][:-1])
        return u"experience add {} {}".format(player, self.data["<%amount"])


commandsMap = {command: eval(command.replace("-", "_")) for command in Globals.commands if command not in ("?", "msg", "tell")}


if __name__ == "__main__":
    import argparse

    failedFiles = []
    commentedOutFiles = []
    multiLineFiles = []
    tmpFiles = []
    Globals.fileCounter = 0

    def convertFile(fileName):
        Globals.fileCounter += 1
        with codecs.open(fileName, 'r', "utf-8") as f:
            lines = f.readlines()

        lineOffset, lineNumber = 0, 0
        try:
            for lineNumber, line in enumerate(lines):
                line = line.rstrip()
                if len(line):
                    start = len(line) - len(line.lstrip())
                    if line[start] == '#':
                        continue
                    Globals.reset()
                    lines[lineNumber] = u"{}{}\n".format(line[:start], unicode(decide(line)))

                    if Globals.flags["commentedOut"]:
                        commentedOutFiles.append((fileName, lineNumber + lineOffset + 1))
                    if Globals.flags["multiLine"]:
                        multiLineFiles.append((fileName, lineNumber + lineOffset + 1))
                    if Globals.messages:
                        lines[lineNumber] = line[:start] + u"".join(u"#~ {}\n".format(message) for message in Globals.messages) + lines[lineNumber][start:]
                    lines[lineNumber] = lines[lineNumber][:-1].replace(u"\n", u"\n{}".format(line[:start])) + u"\n"
                    lineOffset += lines[lineNumber].count("\n") - 1

        except SyntaxError as ex:
            print("File: {}\nLine {}:\n{}".format(fileName, lineNumber + lineOffset + 1, ex))
            return fileName
        with codecs.open(u"{}.TheAl_T".format(fileName), 'w', "utf-8") as f:
            f.writelines(lines)

    def findWorld():
        relative = u""
        path = os.getcwdu().split(os.sep)
        while len(path) >= 2:
            relative += u"..{}".format(os.sep)
            currDir = path.pop()
            target = os.path.join(relative, currDir)
            if "level.dat" in os.listdir(target):
                return os.path.abspath(target)
        return None

    def convertTree(target):
        for root, _, files in os.walk(target):
            for fileName in files:
                if fileName.endswith(".mcfunction"):
                    ret = convertFile(os.path.join(root, fileName))
                    if ret:
                        failedFiles.append(ret)
                    else:
                        tmpFiles.append(u"{}.TheAl_T".format(os.path.join(root, fileName)))

    args = argparse.ArgumentParser(description="Convert 1.12 Minecraft commands to 1.13")
    args.add_argument("--strict_selectors", action="store_true", help="Always sort selectors")
    args.add_argument("--menu", choices=("1", "2", "3", "4"), help="Used to access the menu from the CLI")
    args.add_argument("--files", nargs="+", metavar="FILE", help="Used to convert only specific files. Overrides --menu")
    args = args.parse_args()

    Globals.flags["strictSelector"] = args.strict_selectors

    try:
        if args.files:
            startTime = get_time()
            for fileName in args.files:
                if not os.path.isfile(fileName):
                    print(u"\'{}\' is not a file".format(fileName))
                    failedFiles.append(fileName)
                    continue

                ret = convertFile(fileName)
                if ret:
                    failedFiles.append(ret)
                else:
                    tmpFiles.append(u"{}.TheAl_T".format(fileName))
        else:
            world = findWorld()

            if args.menu:
                choice = args.menu
            else:
                choice = raw_input(u"Current folder: {}\n"
                                   u"1 - Convert all files in this folder only\n"
                                   u"2 - Convert all files in this folder and all sub-folders\n"
                                   u"3 - Convert world: {}\n"
                                   u"4 - Remove .TheAl_T files\n"
                                   u"else - One command to convert\n"
                                   u"\n"
                                   u"> ".format(os.getcwdu(), os.path.basename(world) if world else u"Unable to find, you will be prompted"))

            if choice.strip() not in ("1", "2", "3", "4"):
                try:
                    result = unicode(decide(choice))
                    print(u"\nOutput:\n")
                    if Globals.messages:
                        print(u"Messages:\n{}\n".format(u"\n".join(Globals.messages)))
                    print(u"{}\n".format(result))
                except SyntaxError as e:
                    print(u"\n{}\n".format(e))
                raw_input("Press Enter to exit...")
                exit()

            print("")
            startTime = get_time()
            if choice.strip() == "1":
                for fileName in (f for f in os.listdir(u".") if os.path.isfile(f)):
                    if fileName.endswith(".mcfunction"):
                        ret = convertFile(fileName)
                        if ret:
                            failedFiles.append(ret)
                        else:
                            tmpFiles.append(u"{}.TheAl_T".format(fileName))

            elif choice.strip() == "2":
                convertTree(u".")

            elif choice.strip() == "3":
                if not world:
                    print("Unable to find the world directory. Please provide a path to a folder containing level.dat: ")
                    world = raw_input(u"Current folder: {}\n> ".format(os.getcwdu()))
                    if not os.path.isdir(world):
                        print(u"\'{}\' is not a folder".format(world))
                        exit(-1)
                    os.chdir(world)
                    if not args.menu and raw_input(u"{} selected. Press y if you want to abort: ".format(os.getcwdu())).lower() == "y":
                        raw_input("\nAborting\n\nPress Enter to exit...")
                        exit()
                os.chdir(world)

                startTime = get_time()

                pack = u"datapacks{0}converted{0}".format(os.sep)
                if not os.path.isdir(pack):
                    os.makedirs(pack)
                with open(u"{}pack.mcmeta".format(pack), 'w') as f:
                    f.write("{\n\t\"pack\": {\n\t\t\"pack_format\": 1,\n\t\t\"description\": \"Made using TheAl_T\'s 1.12 to 1.13 converter\"\n\t}\n}\n")

                convertTree(u"data{}functions".format(os.sep))

                if failedFiles:
                    shutil.rmtree(u"datapacks")
                else:
                    for i in xrange(len(tmpFiles)):
                        tmp = tmpFiles[i].split(os.sep)
                        tmpFiles[i] = os.path.join(*(["datapacks", "converted", "data"] + tmp[2:3] + ['functions'] + tmp[3:]))

                    for what in (u"advancements", u"functions", u"loot_tables"):
                        if os.path.isdir(u"data{}{}".format(os.sep, what)):
                            print(u"Found {}".format(what))
                            fromDir = u"data{0}{1}{0}".format(os.sep, what)
                            for namespace in os.listdir(fromDir):
                                fromDirNamespace = u"{}{}{}".format(fromDir, namespace, os.sep)
                                if os.path.isdir(fromDirNamespace):
                                    toDir = u"datapacks{0}converted{0}data{0}{1}{0}{2}{0}".format(os.sep, namespace, what)
                                    if not os.path.isdir(toDir):
                                        os.makedirs(toDir)
                                    for f in os.listdir(fromDirNamespace):
                                        shutil.move(u"{}{}{}".format(fromDirNamespace, os.sep, f), toDir)
                                    os.removedirs(fromDirNamespace)

                    if os.path.isdir(u"structures"):
                        print(u"Found structures")
                        toDir = u"datapacks{0}converted{0}data{0}minecraft{0}structures{0}".format(os.sep)
                        if not os.path.isdir(toDir):
                            os.makedirs(toDir)
                        for f in os.listdir(u"structures"):
                            shutil.move(u"structures{}{}".format(os.sep, f), toDir)
                        os.rmdir(u"structures")
            else:
                for root, _, files in os.walk(u"."):
                    for fileName in files:
                        if fileName.endswith(".TheAl_T"):
                            os.remove(os.path.join(root, fileName))
                raw_input("\nDone\n\nPress Enter to exit...")
                exit()
    except SyntaxError as e:
        print(u"\n{}\n".format(e))

    if failedFiles:
        for tmp in tmpFiles:
            os.remove(tmp)
        raw_input(u"List of files that failed: \"{}\"\n\nConverting aborted.\n\nPress Enter to exit...".format(u"\" \"".join(failedFiles)))
    else:
        for tmp in tmpFiles:
            os.remove(tmp[:-8])
            os.rename(tmp, tmp[:-8])
        if commentedOutFiles:
            print(u"Some commands were commented out because they have to be converted manually or are no longer needed:\n{}\n"
                  u"".format(u"\n".join(u"\tFile: {}, Line: {}".format(*x) for x in commentedOutFiles)))
        if multiLineFiles:
            print(u"Some commands were split. They require manual attention:\n{}\n"
                  u"".format(u"\n".join(u"\tFile: {}, Line: {}".format(*x) for x in multiLineFiles)))
        raw_input(u"A total of {0} command{2}, across {1} file{2}, was converted in {3:.2f} seconds\n\nPress Enter to exit...".format(Globals.commandCounter, Globals.fileCounter, u"s" if Globals.fileCounter > 1 else u"", get_time() - startTime))
