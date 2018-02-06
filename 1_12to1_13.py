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

from data import *
from time import time as getTime

import json, sys, codecs, os, shutil

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
            data[nbtLabel]["Damage"] = data[damageLabel]
        return u"{}{}".format(s, data[nbtLabel] if data[nbtLabel] != {} else "")
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


def constraints(data, rules):
    for label, (low, high) in rules.items():
        if label in data:
            if high == "*":
                high = 2147483647
            valueType = type(low)
            try:
                if not (low <= valueType(data[label]) <= high):
                    raise SyntaxError(u"\'{}\' has to be in range {}..{}".format(data[label], low, high))
            except ValueError:
                raise SyntaxError(u"\'{}\' has to be integer".format(data[label]))


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


class Selector(object):
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

                for key in self.data.keys():
                    if key in ('m', "type"):
                        self.data[key] = self.data[key].lower()
                    if not (Globals.scoreRe.match(key) or key in Globals.selectorArgs):
                        raise SyntaxError(u"\'{}\' is not a valid selector because: \'{}\' is not valid selector argument".format(raw, key))

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

        if "[.item" in self.data:
            item(self.data, "[.item", "[0data", "[{dataTag")
        constraints(self.data, {"[0maxCount": (0, "*")})

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

        if "<(filtered" in self.data:
            block(self.data, "<.tileName", "[.dataValue")  # todo -1, *

    def __unicode__(self):
        s = u"clone {} {} {} {} {} {} {} {} {}".format(self.data["<~x1"], self.data["<~y1"], self.data["<~z1"], self.data["<~x2"], self.data["<~y2"], self.data["<~z2"], self.data["<~x"], self.data["<~y"], self.data["<~z"])
        if "<(filtered" in self.data:
            s += u" filtered {} {}".format(block(self.data, "<.tileName", "[.dataValue"), self.data["<(force|move|normal"])  # todo -1, *
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

        constraints(self.data, {"[0seconds": (0, 1000000), "[0amplifier": (0, 255)})

    def __unicode__(self):
        if self.syntax[1] == "<(clear":
            return u"effect clear {}".format(self.data["<@player"])

        if "[0seconds" in self.data and self.data["[0seconds"] == "0":
            return u"effect clear {} {}".format(self.data["<@player"], self.data["<.effect"])

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

        constraints(self.data, {"[0level": (1, 5)})


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
        # If the first syntax doesn't match, the second would, but would later fail (obviously) giving misleading error message
        if len(tokens) > 4 and tokens[4] == "detect":
            syntaxes = (("<@entity", "<~x", "<~y", "<~z", "<(detect", "<~x2", "<~y2", "<~z2", "<.block", "<.dataValue", "<*command"), )
        else:
            syntaxes = (("<@entity", "<~x", "<~y", "<~z", "<*command"), )
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.s = not self.data["<@entity"].playerName and self.data["<@entity"].target == "s"

        self.data["<*command"] = self.data["<*command"][1:] if self.data["<*command"][0] == '/' else self.data["<*command"]
        self.data["<*command"] = decide(self.data["<*command"])

        self.canAt, self.canAs = self.data["<*command"].canAt or self.data["<@entity"].canAt, self.data["<*command"].canAs
        if "<(detect" in self.data:
            self.canAt = True

            block(self.data, "<.block", "<.dataValue")  # todo -1, *

    def __unicode__(self):
        command = unicode(self.data["<*command"])

        position = u""
        if not '~' == self.data["<~x"] == self.data["<~y"] == self.data["<~z"] and self.canAt:
            position = u" positioned {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"])

        detect = u""
        if "<(detect" in self.data:
            if self.data["<.dataValue"] in ("-1", "*"):
                coords = u" {} {} {} ".format(self.data["<~x2"], self.data["<~y2"], self.data["<~z2"])
                detect += u" if block{}{}".format(coords, u" execute if block{}".format(coords).join(block(self.data, "<.block")))  # todo -1, *
            else:
                detect += u" if block {} {} {} {}".format(self.data["<~x2"], self.data["<~y2"], self.data["<~z2"], block(self.data, "<.block", "<.dataValue"))  # todo -1, *

        if not self.data["<@entity"].playerName and self.data["<@entity"].target == "s":
            selectorArgs = len(self.data["<@entity"].data)

            if self.canAt and self.canAs:
                if position and selectorArgs:
                    s = u"execute as {}{}".format(self.data["<@entity"], position)
                elif position and not selectorArgs:
                    s = u"execute{}".format(position)
                elif not position and selectorArgs:
                    s = u"execute as {}".format(self.data["<@entity"])
                else:
                    s = u"execute"
            elif self.canAt and not self.canAs:
                if position and selectorArgs:
                    s = u"execute at {}{}".format(self.data["<@entity"], position)
                elif position and not selectorArgs:
                    s = u"execute{}".format(position)
                elif not position and selectorArgs:
                    s = u"execute at {}".format(self.data["<@entity"])
                else:
                    s = u"execute"
            else:
                if selectorArgs:
                    s = u"execute as {}".format(self.data["<@entity"])
                else:
                    s = u"execute"

            if detect:
                s += detect

            if s == u"execute":
                return command
        else:
            if self.canAt and self.canAs:
                s = u"execute as {} at @s".format(self.data["<@entity"])
            elif self.canAt and not self.canAs:
                s = u"execute at {}".format(self.data["<@entity"])
            else:
                s = u"execute as {}".format(self.data["<@entity"])
            s += position + detect

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

        if "<(replace" in self.data:
            block(self.data, "<.block", "<.dataValue")
            if "[.replaceTileName" in self.data:
                block(self.data, "[.replaceTileName", "[.replaceDataValue")  # todo -1, *
        else:
            block(self.data, "<.block", "[.dataValue", "[{dataTag")

    def __unicode__(self):
        s = u"fill {} {} {} {} {} {}".format(self.data["<~x1"], self.data["<~y1"], self.data["<~z1"], self.data["<~x2"], self.data["<~y2"], self.data["<~z2"])
        if "<(replace" in self.data:
            s += u" {} replace".format(block(self.data, "<.block", "<.dataValue"))
            if "[.replaceTileName" in self.data:
                s += u" {}".format(block(self.data, "[.replaceTileName", "[.replaceDataValue"))  # todo -1, *
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
            return Master.__unicode__(self)
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

        constraints(self.data, {"[0amount": (1, 64)})

    def __unicode__(self):
        s = u"give {} {}".format(self.data["<@player"], item(self.data, "<.item", "[0data", "[{dataTag"))

        if "[0amount" in self.data:
            s += u" {}".format(self.data["[0amount"])
        return s


class help(Master):
    def __init__(self, tokens=None):
        Master.__init__(self)
        if tokens:
            syntaxes = (("<({}".format("|".join(Globals.commands + map(str, xrange(1, 9)))), ), )
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
    def __init__(self, tokens):
        Master.__init__(self)
        syntaxes = (("<(block", "<~x", "<~y", "<~z", "<.slot", "<.item", "[0amount", "[0data", "[{dataTag"),
                    ("<(entity", "<@selector", "<.slot", "<.item", "[0amount", "[0data", "[{dataTag"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = (canAt(self.data, "<~x", "<~y", "<~z"), False) if self.syntax == "<(block" else (self.data["<@selector"].canAt, True)

        item(self.data, "<.item", "[0data", "[{dataTag")

    def __unicode__(self):
        s = u"replaceitem"

        for word in self.syntax[:self.syntax.index("<.item")]:
            s += u" {}".format(self.data[word])

        s += u" {}{}".format(item(self.data, "<.item", "[0data", "[{dataTag"), self.data["[0amount"] if "[0amount" in self.data else "")

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

        block(self.data, "<.block", "[.dataValue", "[{dataTag")

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

        constraints(self.data, {"<0spreadDistance": (0., "*"), "<0maxRange": (float(self.data["<0spreadDistance"])+1., "*")})

        self.data["<*player"] = Selectors(self.data["<*player"])


class stats(Master):
    def __init__(self, tokens):
        Master.__init__(self)
        self.statLabel = "<({}".format("|".join(Globals.statTags))
        syntaxes = (("<(block", "<~x", "<~y", "<~z", "<(clear", self.statLabel),
                    ("<(block", "<~x", "<~y", "<~z", "<(set", self.statLabel, "<@selector", "<.objective"),
                    ("<(entity", "<@selector2", "<(clear", self.statLabel),
                    ("<(entity", "<@selector2", "<(set", self.statLabel, "<@selector", "<.objective"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = True, True

    def __unicode__(self):
        Globals.commentedOut = True
        if "<(clear" in self.data:
            return u"#~ {} ||| Clearing a stat is no longer needed".format(Master.__unicode__(self))
        return u"#~ {} ||| Use \'execute store {} score {} {} run COMMAND\' on the commands that you want the stats from".format(Master.__unicode__(self), "success" if self.data[self.statLabel] == "SuccessCount" else "result", self.data["<@selector"], self.data["<.objective"])


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
                    ("<@target", "<~x", "<~y", "<~z", "<~yaw", "<~pitch"))
        self.syntax, self.data = lex(self.__class__.__name__, syntaxes, tokens)
        self.canAt, self.canAs = canAt(self.data, "<~x", "<~y", "<~z", "<~yaw", "<~pitch"), True

        if self.data["<@target"] == Selector("@s"):
            self.syntax = self.syntax[1:]

    def __unicode__(self):
        return Master.__unicode__(self).replace("teleport", "tp", 1)


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
            return u"execute if block{}{}".format(coords, u" execute if block{}".format(coords).join(block(self.data, "<.block", "[{dataTag")))  # todo -1, *

        return u"execute if block {} {} {} {}".format(self.data["<~x"], self.data["<~y"], self.data["<~z"], block(self.data, "<.block", "[.dataValue", "[{dataTag"))  # todo -1, *


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


commandsMap = {command: eval(command.replace("-", "_")) for command in Globals.commands if command not in ("?", "msg", "tell")}


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
            choice = raw_input("No filenames on the command line, entering menu:\n1 - Convert all files in this folder\n2 - Convert all files in this folder recursively\n3 - Do Data Pack stuff\n4 - Remove .TheAl_T files\nelse - Convert one command here\n\n> ")
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
