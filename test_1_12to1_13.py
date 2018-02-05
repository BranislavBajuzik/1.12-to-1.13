from unittest import TestCase
from itertools import permutations
import random
import inspect
converter = __import__("1_12to1_13")

if type(u"") is str:
    _map = map
    _filter = filter
    xrange = range
    raw_input = input
    map = lambda x, y: list(_map(x, y))
    filter = lambda x, y: list(_filter(x, y))
    unicode = lambda x: x.__unicode__()


def generate_perms(syntax, optional=0):
    ret = generate_perms_r(syntax)

    if optional:
        tmp = []
        for result in ret:
            for option in xrange(optional+1):
                tmp.append(result[:len(result)-option])
        ret = tmp

    return set(map(lambda x: " ".join(x), ret))


def generate_perms_r(syntax):
    ret = []
    for i, word in enumerate(syntax):
        if type(word) is list:
            for perm in word:
                ret.extend(generate_perms_r(syntax[:i] + [perm] + syntax[i+1:]))
            return ret
    return [syntax]


random.seed(42)
def coord():
    num = random.randint(-10000, 10000)
    return [str(num), "~{}".format(num), "~"]


def nbt():
    return [r'{ key : value ,secondKey :"secondValue", aNumber: 30, comp:{lolo:lala}, list:[wooo, weeee]}', "{}"]


class TestBase(TestCase):
    @classmethod
    def tearDownClass(cls):
        print "\n{}:\n".format(cls.__name__)

    def setUp(self):
        self.asserts = 0
        reload(converter)

    def assertStats(self):
        stack = inspect.stack()
        print "\t{} assertion{} made in {}".format(self.asserts, 's' if self.asserts != 1 else '',
                                                   stack[1][0].f_code.co_name)

    def decide(self, raw):
        ret = converter.decide(raw)
        self.asserts += 1
        return ret

    def assertPass(self, _):
        self.asserts += 1

    def assertRaises(self, excClass, argument, function=False):
        try:
            if function:
                super(TestBase, self).assertRaises(excClass, argument)
            else:
                super(TestBase, self).assertRaises(excClass, lambda: self.decide(argument))
        except AssertionError:
            raise AssertionError("{} didn't throw {}".format(argument, excClass))

        self.asserts += 1

    def assertEqual(self, first, second, msg=None):
        super(TestBase, self).assertEqual(first, second, msg)
        self.asserts += 1


class Selector(TestBase):
    def test_syntax_ok(self):
        self.assertPass(converter.Selector("playerName"))
        self.assertPass(converter.Selector("player_name"))
        self.assertPass(converter.Selector("@a[]"))

        argPairs = (("x", "1"), ("y", "1"), ("z", "1"), ("dx", "1"), ("dy", "1"), ("dz", "1"), ("type", "Cow"),
                    ("type", "!Cow"), ("lm", "1"), ("l", "1"), ("m", "1"), ("team", "blue"), ("team", ""), ("team", "!"),
                    ("team", "!blue"), ("score_won", "1"), ("score_won_min", "1"), ("name", "TheAl_T"),
                    ("tag", "inGame"), ("tag", "!inGame"), ("tag", ""), ("tag", "!"), ("rm", "1"), ("r", "1"),
                    ("rxm", "1"), ("rx", "1"), ("rym", "1"), ("ry", "1"), ("c", "1"))

        for sType in ("p", "e", "a", "r", "s"):
            for n in (1, 2, 3):
                for argPairsPerm in permutations(argPairs, n):
                    self.assertPass(converter.Selector("@{}[{}]".format(sType, ",".join(map(lambda x: "{}={}".format(x[0], x[1]), argPairsPerm)))))
        self.assertStats()

    def test_syntax_nok(self):
        cases = ("@", "*", "=", "[", "]", "@c", "@a[", "@s]", "@a[c =3]", "@a][", "@a[c=1][")

        for case in cases:
            self.assertRaises(SyntaxError, lambda: converter.Selector(case), True)

        argPairs = (("x", "a"), ("y", "a"), ("z", "a"), ("dx", "a"), ("dy", "a"), ("dz", "a"), ("type", "bad"),
                    ("type", "!bad"), ("lm", "a"), ("l", "a"), ("m", "bad"), ("score_won", "a"), ("score_won_min", "a"),
                    ("rm", "a"), ("r", "a"), ("rxm", "a"), ("rx", "a"), ("rym", "a"), ("ry", "a"), ("c", "a"),
                    ("bad", "bad"), ("x", ""), ("y", ""), ("z", ""), ("dx", ""), ("dy", ""), ("dz", ""), ("type", ""),
                    ("type", ""), ("lm", ""), ("l", ""), ("m", ""), ("score_won", ""), ("score_won_min", ""),
                    ("name", ""), ("rm", ""), ("r", ""), ("rxm", ""), ("rx", ""), ("rym", ""), ("ry", ""), ("c", ""))

        for sType in ("p", "e", "a", "r", "s"):
            for n in (1, 2, 3):
                for argPairsPerm in permutations(argPairs, n):
                    self.assertRaises(SyntaxError, lambda: converter.Selector("@{}[{}]".format(sType, ",".join(map(lambda x: "{}={}".format(x[0], x[1]), argPairsPerm)))), True)
        self.assertStats()


class Advancement(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["advancement", ["grant", "revoke"], "@s", ["only", "until", "from", "through"], "adv_name", "crit"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("advancement",
                 "advancement grant",
                 "advancement aaaaa @s only adv_name crit",
                 "advancement grant @s",
                 "advancement grant @c only adv_name crit",
                 "advancement grant @s only",
                 "advancement grant @s aaaa adv_name crit",
                 "advancement grant @s only adv_name crit lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("advancement grant @s only adv_name crit"), "advancement grant @s only adv_name crit"),
                 (converter.decide("advancement grant @s from adv_name"), "advancement grant @s from adv_name"),
                 (converter.decide("advancement revoke @s from adv_name crit"), "advancement revoke @s from adv_name crit"),
                 (converter.decide("advancement grant @s only adv_name crit"), "advancement grant @s only adv_name crit"),
                 (converter.decide("advancement grant @s until adv_name"), "advancement grant @s until adv_name"),
                 (converter.decide("advancement revoke @s through adv_name crit"), "advancement revoke @s through adv_name crit"),
                 (converter.decide("advancement grant @s only adv_name"), "advancement grant @s only adv_name"),
                 (converter.decide("advancement revoke @s until adv_name crit"), "advancement revoke @s until adv_name crit"),
                 (converter.decide("advancement revoke @s through adv_name"), "advancement revoke @s through adv_name"),
                 (converter.decide("advancement grant @s through adv_name"), "advancement grant @s through adv_name"),
                 (converter.decide("advancement revoke @s from adv_name"), "advancement revoke @s from adv_name"),
                 (converter.decide("advancement revoke @s until adv_name"), "advancement revoke @s until adv_name"),
                 (converter.decide("advancement revoke @s only adv_name crit"), "advancement revoke @s only adv_name crit"),
                 (converter.decide("advancement grant @s from adv_name crit"), "advancement grant @s from adv_name crit"),
                 (converter.decide("advancement revoke @s only adv_name"), "advancement revoke @s only adv_name"),
                 (converter.decide("advancement grant @s through adv_name crit"), "advancement grant @s through adv_name crit"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["advancement", ["grant", "revoke"], "@s", "everything"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("advancement",
                 "advancement grant",
                 "advancement bbbbb @s everything",
                 "advancement grant @s",
                 "advancement grant @c everything",
                 "advancement grant @s aaaaaaaaaa",
                 "advancement grant @s everything lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("advancement grant @s everything"), "advancement grant @s everything"),
                 (converter.decide("advancement revoke @s everything"), "advancement revoke @s everything"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax3_ok(self):
        perms = generate_perms(["advancement", "test", "@s", "adv_name", ["crit", ""]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax3_nok(self):
        perms = ("advancement",
                 "advancement test",
                 "advancement aaaa @s adv_name crit",
                 "advancement test @s",
                 "advancement test @c adv_name crit",
                 "advancement test @s adv_name crit lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = ((converter.decide("advancement test @s adv_name crit"), "execute if entity @s[advancements={adv_name={crit=true}}]"),
                 (converter.decide("advancement test @s adv_name"), "execute if entity @s[advancements={adv_name=true}]"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Ban(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["ban", "p_name", ["Because", "Because I said so"]], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("ban",)
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("ban p_name Because"), "ban p_name Because"),
                 (converter.decide("ban p_name Because I said so"), "ban p_name Because I said so"),
                 (converter.decide("ban p_name"), "ban p_name"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Ban_IP(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["ban-ip", "p_name", ["because", "Because I said so"]], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("ban-ip",)
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("ban-ip p_name Because"), "ban-ip p_name Because"),
                 (converter.decide("ban-ip p_name Because I said so"), "ban-ip p_name Because I said so"),
                 (converter.decide("ban-ip p_name"), "ban-ip p_name"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class BlockData(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["blockdata", coord(), coord(), coord(), nbt()])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("blockdata",
                 "blockdata 1",
                 "blockdata a ~ ~3 {abc:def}",
                 "blockdata 1 ~",
                 "blockdata 1 ~a ~3 {abc:def}",
                 "blockdata 1 ~ ~3",
                 "blockdata 1 ~ ~3a {abc:def}",
                 "blockdata 1 ~ ~3 aaaaa",
                 "blockdata 1 ~ ~3 {abc:def} lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("blockdata 1 ~ ~3 {abc:def}"), "data merge block 1 ~ ~3 {abc:def}"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Clear(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["clear", "@s", "minecraft:stone", "1", "42", nbt()], optional=5)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("clear @c minecraft:stone 1 42 {abc:def}",
                 "clear @s minecraft:stone -2 42 {abc:def}",
                 "clear @s minecraft:stone 16 42 {abc:def}",
                 "clear @s minecraft:stone a 42 {abc:def}",
                 "clear @s minecraft:stone a -1 {abc:def}",
                 "clear @s minecraft:stone 1 aa {abc:def}",
                 "clear @s minecraft:stone 1 42 aaaaaaaaa")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("clear"), "clear"),
                 (converter.decide("clear @s"), "clear @s"),
                 (converter.decide("clear @s minecraft:stone"), "clear @s stone"),
                 (converter.decide("clear @s minecraft:stone 1"), "clear @s granite"),
                 (converter.decide("clear @s minecraft:stone 1 42"), "clear @s granite 42"),
                 (converter.decide("clear @s minecraft:stone 1 42 {abc:def}"), "clear @s granite{abc:def} 42"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Clone(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["clone", "1", "~-1", "~1", "1", "~-1", "~1", "1", "~-1", "~1",
                                ["masked", "replace"], ["force", "move", "normal"]], optional=2)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("clone 1",
                 "clone a ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace force",
                 "clone 1 ~-1",
                 "clone 1 ~aa ~1 1 ~-1 ~1 1 ~-1 ~1 replace force",
                 "clone 1 ~-1 ~1",
                 "clone 1 ~-1 ~a 1 ~-1 ~1 1 ~-1 ~1 replace force",
                 "clone 1 ~-1 ~1 1",
                 "clone 1 ~-1 ~1 a ~-1 ~1 1 ~-1 ~1 replace force",
                 "clone 1 ~-1 ~1 1 ~-1",
                 "clone 1 ~-1 ~1 1 ~aa ~1 1 ~-1 ~1 replace force",
                 "clone 1 ~-1 ~1 1 ~-1 ~1",
                 "clone 1 ~-1 ~1 1 ~-1 ~a 1 ~-1 ~1 replace force",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 a ~-1 ~1 replace force",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~aa ~1 replace force",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~a replace force",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 aaaaaaa",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 aaaaaaa force",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace aaaaa",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace force lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked force"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked force"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked move"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked move"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked normal"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked normal"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace force"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace force"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace move"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace move"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace normal"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace normal"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["clone", "1", "~-1", "~1", "1", "~-1", "~1", "1", "~-1", "~1",
                                "filtered", ["force", "move", "normal"], "stone", "1"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered aaaaa stone 1",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered aaaaa stone a",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered aaaaa stone -2",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered aaaaa stone 16",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force stone 1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):  # todo What to do with blocks like wool
        tests = ((converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force stone 1"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered granite force"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force stone"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone force"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered move stone 1"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered granite move"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered move stone"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone move"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered normal stone 1"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered granite normal"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered normal stone"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone normal"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Debug(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["debug", ["start", "stop"]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("debug",
                 "debug aaaaa",
                 "debug start ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("debug start"), "debug start"),
                 (converter.decide("debug stop"), "debug stop"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class DefaultGameMode(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["defaultgamemode", ["0", "1", "2", "3", "s", "c", "a", "sp", "survival", "creative", "adventure", "spectator"]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("defaultgamemode",
                 "defaultgamemode aaa",
                 "defaultgamemode 1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("defaultgamemode 0"), "defaultgamemode survival"),
                 (converter.decide("defaultgamemode 1"), "defaultgamemode creative"),
                 (converter.decide("defaultgamemode 2"), "defaultgamemode adventure"),
                 (converter.decide("defaultgamemode 3"), "defaultgamemode spectator"),
                 (converter.decide("defaultgamemode s"), "defaultgamemode survival"),
                 (converter.decide("defaultgamemode c"), "defaultgamemode creative"),
                 (converter.decide("defaultgamemode a"), "defaultgamemode adventure"),
                 (converter.decide("defaultgamemode sp"), "defaultgamemode spectator"),
                 (converter.decide("defaultgamemode survival"), "defaultgamemode survival"),
                 (converter.decide("defaultgamemode creative"), "defaultgamemode creative"),
                 (converter.decide("defaultgamemode adventure"), "defaultgamemode adventure"),
                 (converter.decide("defaultgamemode spectator"), "defaultgamemode spectator"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Deop(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["deop", "@s"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("deop",
                 "deop @c",
                 "deop @s ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("deop @s"), "deop @s"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Difficulty(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["difficulty", ["0", "1", "2", "3", "p", "e", "n", "h", "peaceful", "easy", "normal", "hard"]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("difficulty",
                 "difficulty aaa",
                 "difficulty 1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("difficulty 0"), "difficulty peaceful"),
                 (converter.decide("difficulty 1"), "difficulty easy"),
                 (converter.decide("difficulty 2"), "difficulty normal"),
                 (converter.decide("difficulty 3"), "difficulty hard"),
                 (converter.decide("difficulty p"), "difficulty peaceful"),
                 (converter.decide("difficulty e"), "difficulty easy"),
                 (converter.decide("difficulty n"), "difficulty normal"),
                 (converter.decide("difficulty h"), "difficulty hard"),
                 (converter.decide("difficulty peaceful"), "difficulty peaceful"),
                 (converter.decide("difficulty easy"), "difficulty easy"),
                 (converter.decide("difficulty normal"), "difficulty normal"),
                 (converter.decide("difficulty hard"), "difficulty hard"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Effect(TestBase):
    def test_syntax1_ok(self):
        perms = ("effect @s clear", )
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("effect",
                 "effect @s",
                 "effect @c clear")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("effect @s clear"), "effect clear @s"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["effect", "@s", "speed", "10", "10", ["true", "false"]], optional=3)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("effect",
                 "effect @s",
                 "effect @c speed 10 10 true",
                 "effect @c speed -1 10 true",
                 "effect @c speed 1000001 10 true",
                 "effect @s speed aa 10 true",
                 "effect @s speed aa -1 true",
                 "effect @s speed aa 1000001 true",
                 "effect @s speed 10 aa true",
                 "effect @s speed 10 10 aaaa",
                 "effect @s speed 10 10 true ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("effect @s speed"), "effect give @s speed"),
                 (converter.decide("effect @s speed 0"), "effect clear @s speed"),
                 (converter.decide("effect @s speed 11"), "effect give @s speed 11"),
                 (converter.decide("effect @s speed 11 22"), "effect give @s speed 11 22"),
                 (converter.decide("effect @s speed 11 22 true"), "effect give @s speed 11 22 true"),
                 (converter.decide("effect @s speed 11 22 false"), "effect give @s speed 11 22 false"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Enchant(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["enchant", "@s", "sharpness", "1"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("enchant",
                 "enchant @s",
                 "enchant @c sharpness 1",
                 "enchant @s sharpness 0",
                 "enchant @s sharpness 6",
                 "enchant @s sharpness a",
                 "enchant @s sharpness 1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("enchant @s sharpness 1"), "enchant @s sharpness 1"),
                 (converter.decide("enchant @s sharpness"), "enchant @s sharpness"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class EntityData(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["entitydata", "@s", nbt()])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("entitydata",
                 "entitydata @s",
                 "entitydata @c {abc:def}",
                 "entitydata @s aaaaaaaaa",
                 "entitydata @s {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("entitydata @s {abc:def}"), "data merge entity @s {abc:def}"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Execute(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["execute", "@s", "1", "~-1", "1", "say hi"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("execute",
                 "execute @c 1 ~-1 1 say hi",
                 "execute @s",
                 "execute @s a ~-1 1 say hi",
                 "execute @s 1",
                 "execute @s 1 aaa 1 say hi",
                 "execute @s 1 ~-1",
                 "execute @s 1 ~-1 a say hi",
                 "execute @s 1 ~-1 1",
                 "execute @s 1 ~-1 1 aaaaaa")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (  # @s
                 # not canAs and not canAt
                 (converter.decide("execute @s ~ ~ ~ seed"),
                                   "seed"),
                 (converter.decide("execute @s[name=Carl] ~ ~ ~ seed"),
                                   "execute as @s[name=Carl] run seed"),
                 (converter.decide("execute @s 1 ~-1 1 seed"),
                                   "seed"),
                 (converter.decide("execute @s[name=Carl] 1 ~-1 1 seed"),
                                   "execute as @s[name=Carl] run seed"),

                 (converter.decide("execute @s ~ ~ ~ execute @s ~ ~ ~ seed"),
                                   "seed"),
                 (converter.decide("execute @s ~ ~ ~ execute @s[name=Carl] ~ ~ ~ seed"),
                                   "execute as @s[name=Carl] run seed"),
                 (converter.decide("execute @s ~ ~ ~ execute @s 1 ~-1 1 seed"),
                                   "seed"),
                 (converter.decide("execute @s ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 seed"),
                                   "execute as @s[name=Carl] run seed"),

                 (converter.decide("execute @s 1 ~-1 1 execute @s ~ ~ ~ seed"),
                                   "seed"),
                 (converter.decide("execute @s 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ seed"),
                                   "execute as @s[name=Carl] run seed"),
                 (converter.decide("execute @s 1 ~-1 1 execute @s 1 ~-1 1 seed"),
                                   "seed"),
                 (converter.decide("execute @s 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 seed"),
                                   "execute as @s[name=Carl] run seed"),

                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s ~ ~ ~ seed"),
                                   "execute as @s[tag=Carl] run seed"),
                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] ~ ~ ~ seed"),
                                   "execute as @s[tag=Carl] as @s[name=Carl] run seed"),
                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s 1 ~-1 1 seed"),
                                   "execute as @s[tag=Carl] run seed"),
                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 seed"),
                                   "execute as @s[tag=Carl] as @s[name=Carl] run seed"),

                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s ~ ~ ~ seed"),
                                   "execute as @s[tag=Carl] run seed"),
                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ seed"),
                                   "execute as @s[tag=Carl] as @s[name=Carl] run seed"),
                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s 1 ~-1 1 seed"),
                                   "execute as @s[tag=Carl] run seed"),
                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 seed"),
                                   "execute as @s[tag=Carl] as @s[name=Carl] run seed"),

                 # canAs and not canAt
                 (converter.decide("execute @s ~ ~ ~ say hi"),
                                   "say hi"),
                 (converter.decide("execute @s[name=Carl] ~ ~ ~ say hi"),
                                   "execute as @s[name=Carl] run say hi"),
                 (converter.decide("execute @s 1 ~-1 1 say hi"),
                                   "say hi"),
                 (converter.decide("execute @s[name=Carl] 1 ~-1 1 say hi"),
                                   "execute as @s[name=Carl] run say hi"),

                 (converter.decide("execute @s ~ ~ ~ execute @s ~ ~ ~ say hi"),
                                   "say hi"),
                 (converter.decide("execute @s ~ ~ ~ execute @s[name=Carl] ~ ~ ~ say hi"),
                                   "execute as @s[name=Carl] run say hi"),
                 (converter.decide("execute @s ~ ~ ~ execute @s 1 ~-1 1 say hi"),
                                   "say hi"),
                 (converter.decide("execute @s ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 say hi"),
                                   "execute as @s[name=Carl] run say hi"),

                 (converter.decide("execute @s 1 ~-1 1 execute @s ~ ~ ~ say hi"),
                                   "say hi"),
                 (converter.decide("execute @s 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ say hi"),
                                   "execute as @s[name=Carl] run say hi"),
                 (converter.decide("execute @s 1 ~-1 1 execute @s 1 ~-1 1 say hi"),
                                   "say hi"),
                 (converter.decide("execute @s 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 say hi"),
                                   "execute as @s[name=Carl] run say hi"),

                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s ~ ~ ~ say hi"),
                                   "execute as @s[tag=Carl] run say hi"),
                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] ~ ~ ~ say hi"),
                                   "execute as @s[tag=Carl] as @s[name=Carl] run say hi"),
                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s 1 ~-1 1 say hi"),
                                   "execute as @s[tag=Carl] run say hi"),
                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 say hi"),
                                   "execute as @s[tag=Carl] as @s[name=Carl] run say hi"),

                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s ~ ~ ~ say hi"),
                                   "execute as @s[tag=Carl] run say hi"),
                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ say hi"),
                                   "execute as @s[tag=Carl] as @s[name=Carl] run say hi"),
                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s 1 ~-1 1 say hi"),
                                   "execute as @s[tag=Carl] run say hi"),
                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 say hi"),
                                   "execute as @s[tag=Carl] as @s[name=Carl] run say hi"),

                 # not canAs and canAt
                 (converter.decide("execute @s ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @s[name=Carl] run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @s[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 (converter.decide("execute @s ~ ~ ~ execute @s ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s ~ ~ ~ execute @s[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @s[name=Carl] run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s ~ ~ ~ execute @s 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @s[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 (converter.decide("execute @s 1 ~-1 1 execute @s ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute positioned 1 ~-1 1 at @s[name=Carl] run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s 1 ~-1 1 execute @s 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute positioned 1 ~-1 1 positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute positioned 1 ~-1 1 at @s[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @s[tag=Carl] run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @s[tag=Carl] at @s[name=Carl] run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @s[tag=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @s[tag=Carl] at @s[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @s[tag=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @s[tag=Carl] positioned 1 ~-1 1 at @s[name=Carl] run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @s[tag=Carl] positioned 1 ~-1 1 positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @s[tag=Carl] positioned 1 ~-1 1 at @s[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 # canAs and canAt
                 (converter.decide("execute @s ~ ~ ~ function abc:def"),
                                   "function abc:def"),
                 (converter.decide("execute @s[name=Carl] ~ ~ ~ function abc:def"),
                                   "execute as @s[name=Carl] run function abc:def"),
                 (converter.decide("execute @s 1 ~-1 1 function abc:def"),
                                   "execute positioned 1 ~-1 1 run function abc:def"),
                 (converter.decide("execute @s[name=Carl] 1 ~-1 1 function abc:def"),
                                   "execute as @s[name=Carl] positioned 1 ~-1 1 run function abc:def"),

                 (converter.decide("execute @s ~ ~ ~ execute @s ~ ~ ~ function abc:def"),
                                   "function abc:def"),
                 (converter.decide("execute @s ~ ~ ~ execute @s[name=Carl] ~ ~ ~ function abc:def"),
                                   "execute as @s[name=Carl] run function abc:def"),
                 (converter.decide("execute @s ~ ~ ~ execute @s 1 ~-1 1 function abc:def"),
                                   "execute positioned 1 ~-1 1 run function abc:def"),
                 (converter.decide("execute @s ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 function abc:def"),
                                   "execute as @s[name=Carl] positioned 1 ~-1 1 run function abc:def"),

                 (converter.decide("execute @s 1 ~-1 1 execute @s ~ ~ ~ function abc:def"),
                                   "execute positioned 1 ~-1 1 run function abc:def"),
                 (converter.decide("execute @s 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ function abc:def"),
                                   "execute positioned 1 ~-1 1 as @s[name=Carl] run function abc:def"),
                 (converter.decide("execute @s 1 ~-1 1 execute @s 1 ~-1 1 function abc:def"),
                                   "execute positioned 1 ~-1 1 positioned 1 ~-1 1 run function abc:def"),
                 (converter.decide("execute @s 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 function abc:def"),
                                   "execute positioned 1 ~-1 1 as @s[name=Carl] positioned 1 ~-1 1 run function abc:def"),

                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s ~ ~ ~ function abc:def"),
                                   "execute as @s[tag=Carl] run function abc:def"),
                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] ~ ~ ~ function abc:def"),
                                   "execute as @s[tag=Carl] as @s[name=Carl] run function abc:def"),
                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s 1 ~-1 1 function abc:def"),
                                   "execute as @s[tag=Carl] positioned 1 ~-1 1 run function abc:def"),
                 (converter.decide("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 function abc:def"),
                                   "execute as @s[tag=Carl] as @s[name=Carl] positioned 1 ~-1 1 run function abc:def"),

                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s ~ ~ ~ function abc:def"),
                                   "execute as @s[tag=Carl] positioned 1 ~-1 1 run function abc:def"),
                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ function abc:def"),
                                   "execute as @s[tag=Carl] positioned 1 ~-1 1 as @s[name=Carl] run function abc:def"),
                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s 1 ~-1 1 function abc:def"),
                                   "execute as @s[tag=Carl] positioned 1 ~-1 1 positioned 1 ~-1 1 run function abc:def"),
                 (converter.decide("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 function abc:def"),
                                   "execute as @s[tag=Carl] positioned 1 ~-1 1 as @s[name=Carl] positioned 1 ~-1 1 run function abc:def"),

                 # @e
                 # not canAs and not canAt
                 (converter.decide("execute @e ~ ~ ~ seed"),
                                   "execute as @e run seed"),
                 (converter.decide("execute @e[name=Carl] ~ ~ ~ seed"),
                                   "execute as @e[name=Carl] run seed"),
                 (converter.decide("execute @e 1 ~-1 1 seed"),
                                   "execute as @e run seed"),
                 (converter.decide("execute @e[name=Carl] 1 ~-1 1 seed"),
                                   "execute as @e[name=Carl] run seed"),

                 (converter.decide("execute @e ~ ~ ~ execute @e ~ ~ ~ seed"),
                                   "execute as @e as @e run seed"),
                 (converter.decide("execute @e ~ ~ ~ execute @e[name=Carl] ~ ~ ~ seed"),
                                   "execute as @e as @e[name=Carl] run seed"),
                 (converter.decide("execute @e ~ ~ ~ execute @e 1 ~-1 1 seed"),
                                   "execute as @e as @e run seed"),
                 (converter.decide("execute @e ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 seed"),
                                   "execute as @e as @e[name=Carl] run seed"),

                 (converter.decide("execute @e 1 ~-1 1 execute @e ~ ~ ~ seed"),
                                   "execute as @e as @e run seed"),
                 (converter.decide("execute @e 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ seed"),
                                   "execute as @e as @e[name=Carl] run seed"),
                 (converter.decide("execute @e 1 ~-1 1 execute @e 1 ~-1 1 seed"),
                                   "execute as @e as @e run seed"),
                 (converter.decide("execute @e 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 seed"),
                                   "execute as @e as @e[name=Carl] run seed"),

                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e ~ ~ ~ seed"),
                                   "execute as @e[tag=Carl] as @e run seed"),
                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] ~ ~ ~ seed"),
                                   "execute as @e[tag=Carl] as @e[name=Carl] run seed"),
                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e 1 ~-1 1 seed"),
                                   "execute as @e[tag=Carl] as @e run seed"),
                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 seed"),
                                   "execute as @e[tag=Carl] as @e[name=Carl] run seed"),

                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e ~ ~ ~ seed"),
                                   "execute as @e[tag=Carl] as @e run seed"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ seed"),
                                   "execute as @e[tag=Carl] as @e[name=Carl] run seed"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e 1 ~-1 1 seed"),
                                   "execute as @e[tag=Carl] as @e run seed"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 seed"),
                                   "execute as @e[tag=Carl] as @e[name=Carl] run seed"),

                 # canAs and not canAt
                 (converter.decide("execute @e ~ ~ ~ say hi"),
                                   "execute as @e run say hi"),
                 (converter.decide("execute @e[name=Carl] ~ ~ ~ say hi"),
                                   "execute as @e[name=Carl] run say hi"),
                 (converter.decide("execute @e 1 ~-1 1 say hi"),
                                   "execute as @e run say hi"),
                 (converter.decide("execute @e[name=Carl] 1 ~-1 1 say hi"),
                                   "execute as @e[name=Carl] run say hi"),

                 (converter.decide("execute @e ~ ~ ~ execute @e ~ ~ ~ say hi"),
                                   "execute as @e as @e run say hi"),
                 (converter.decide("execute @e ~ ~ ~ execute @e[name=Carl] ~ ~ ~ say hi"),
                                   "execute as @e as @e[name=Carl] run say hi"),
                 (converter.decide("execute @e ~ ~ ~ execute @e 1 ~-1 1 say hi"),
                                   "execute as @e as @e run say hi"),
                 (converter.decide("execute @e ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 say hi"),
                                   "execute as @e as @e[name=Carl] run say hi"),

                 (converter.decide("execute @e 1 ~-1 1 execute @e ~ ~ ~ say hi"),
                                   "execute as @e as @e run say hi"),
                 (converter.decide("execute @e 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ say hi"),
                                   "execute as @e as @e[name=Carl] run say hi"),
                 (converter.decide("execute @e 1 ~-1 1 execute @e 1 ~-1 1 say hi"),
                                   "execute as @e as @e run say hi"),
                 (converter.decide("execute @e 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 say hi"),
                                   "execute as @e as @e[name=Carl] run say hi"),

                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e ~ ~ ~ say hi"),
                                   "execute as @e[tag=Carl] as @e run say hi"),
                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] ~ ~ ~ say hi"),
                                   "execute as @e[tag=Carl] as @e[name=Carl] run say hi"),
                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e 1 ~-1 1 say hi"),
                                   "execute as @e[tag=Carl] as @e run say hi"),
                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 say hi"),
                                   "execute as @e[tag=Carl] as @e[name=Carl] run say hi"),

                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e ~ ~ ~ say hi"),
                                   "execute as @e[tag=Carl] as @e run say hi"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ say hi"),
                                   "execute as @e[tag=Carl] as @e[name=Carl] run say hi"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e 1 ~-1 1 say hi"),
                                   "execute as @e[tag=Carl] as @e run say hi"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 say hi"),
                                   "execute as @e[tag=Carl] as @e[name=Carl] run say hi"),

                 # not canAs and canAt
                 (converter.decide("execute @e ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @e run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @e[name=Carl] run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @e positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @e[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 (converter.decide("execute @e ~ ~ ~ execute @e ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @e at @e run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e ~ ~ ~ execute @e[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @e at @e[name=Carl] run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e ~ ~ ~ execute @e 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @e at @e positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @e at @e[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 (converter.decide("execute @e 1 ~-1 1 execute @e ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @e positioned 1 ~-1 1 at @e run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @e positioned 1 ~-1 1 at @e[name=Carl] run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e 1 ~-1 1 execute @e 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @e positioned 1 ~-1 1 at @e positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @e positioned 1 ~-1 1 at @e[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @e[tag=Carl] at @e run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @e[tag=Carl] at @e[name=Carl] run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @e[tag=Carl] at @e positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @e[tag=Carl] at @e[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @e[tag=Carl] positioned 1 ~-1 1 at @e run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone"),
                                   "execute at @e[tag=Carl] positioned 1 ~-1 1 at @e[name=Carl] run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @e[tag=Carl] positioned 1 ~-1 1 at @e positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone"),
                                   "execute at @e[tag=Carl] positioned 1 ~-1 1 at @e[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 # canAs and canAt
                 (converter.decide("execute @e ~ ~ ~ function abc:def"),
                                   "execute as @e at @s run function abc:def"),
                 (converter.decide("execute @e[name=Carl] ~ ~ ~ function abc:def"),
                                   "execute as @e[name=Carl] at @s run function abc:def"),
                 (converter.decide("execute @e 1 ~-1 1 function abc:def"),
                                   "execute as @e at @s positioned 1 ~-1 1 run function abc:def"),
                 (converter.decide("execute @e[name=Carl] 1 ~-1 1 function abc:def"),
                                   "execute as @e[name=Carl] at @s positioned 1 ~-1 1 run function abc:def"),

                 (converter.decide("execute @e ~ ~ ~ execute @e ~ ~ ~ function abc:def"),
                                   "execute as @e at @s as @e at @s run function abc:def"),
                 (converter.decide("execute @e ~ ~ ~ execute @e[name=Carl] ~ ~ ~ function abc:def"),
                                   "execute as @e at @s as @e[name=Carl] at @s run function abc:def"),
                 (converter.decide("execute @e ~ ~ ~ execute @e 1 ~-1 1 function abc:def"),
                                   "execute as @e at @s as @e at @s positioned 1 ~-1 1 run function abc:def"),
                 (converter.decide("execute @e ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 function abc:def"),
                                   "execute as @e at @s as @e[name=Carl] at @s positioned 1 ~-1 1 run function abc:def"),

                 (converter.decide("execute @e 1 ~-1 1 execute @e ~ ~ ~ function abc:def"),
                                   "execute as @e at @s positioned 1 ~-1 1 as @e at @s run function abc:def"),
                 (converter.decide("execute @e 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ function abc:def"),
                                   "execute as @e at @s positioned 1 ~-1 1 as @e[name=Carl] at @s run function abc:def"),
                 (converter.decide("execute @e 1 ~-1 1 execute @e 1 ~-1 1 function abc:def"),
                                   "execute as @e at @s positioned 1 ~-1 1 as @e at @s positioned 1 ~-1 1 run function abc:def"),
                 (converter.decide("execute @e 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 function abc:def"),
                                   "execute as @e at @s positioned 1 ~-1 1 as @e[name=Carl] at @s positioned 1 ~-1 1 run function abc:def"),

                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e ~ ~ ~ function abc:def"),
                                   "execute as @e[tag=Carl] at @s as @e at @s run function abc:def"),
                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] ~ ~ ~ function abc:def"),
                                   "execute as @e[tag=Carl] at @s as @e[name=Carl] at @s run function abc:def"),
                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e 1 ~-1 1 function abc:def"),
                                   "execute as @e[tag=Carl] at @s as @e at @s positioned 1 ~-1 1 run function abc:def"),
                 (converter.decide("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 function abc:def"),
                                   "execute as @e[tag=Carl] at @s as @e[name=Carl] at @s positioned 1 ~-1 1 run function abc:def"),

                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e ~ ~ ~ function abc:def"),
                                   "execute as @e[tag=Carl] at @s positioned 1 ~-1 1 as @e at @s run function abc:def"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ function abc:def"),
                                   "execute as @e[tag=Carl] at @s positioned 1 ~-1 1 as @e[name=Carl] at @s run function abc:def"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e 1 ~-1 1 function abc:def"),
                                   "execute as @e[tag=Carl] at @s positioned 1 ~-1 1 as @e at @s positioned 1 ~-1 1 run function abc:def"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 function abc:def"),
                                   "execute as @e[tag=Carl] at @s positioned 1 ~-1 1 as @e[name=Carl] at @s positioned 1 ~-1 1 run function abc:def"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["execute", "@s", "1", "~-1", "1", "detect", "1", "~-1", "1", "stone", "1", "say hi"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("execute",
                 "execute @c 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi",
                 "execute @s",
                 "execute @s a ~-1 1 detect 1 ~-1 1 stone 1 say hi",
                 "execute @s 1",
                 "execute @s 1 aaa 1 detect 1 ~-1 1 stone 1 say hi",
                 "execute @s 1 ~-1",
                 "execute @s 1 ~-1 a detect 1 ~-1 1 stone 1 say hi",
                 "execute @s 1 ~-1 1",
                 "execute @s 1 ~-1 1 aaaaaa 1 ~-1 1 stone 1 say hi",
                 "execute @s 1 ~-1 1 detect",
                 "execute @s 1 ~-1 1 detect a ~-1 1 stone 1 say hi",
                 "execute @s 1 ~-1 1 detect 1",
                 "execute @s 1 ~-1 1 detect 1 aaa 1 stone 1 say hi",
                 "execute @s 1 ~-1 1 detect 1 ~-1",
                 "execute @s 1 ~-1 1 detect 1 ~-1 a stone 1 say hi",
                 "execute @s 1 ~-1 1 detect 1 ~-1 1",
                 "execute @s 1 ~-1 1 detect 1 ~-1 1 aaaaa",
                 "execute @s 1 ~-1 1 detect 1 ~-1 1 stone a say hi",
                 "execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1",
                 "execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 aaaaaa")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (  # @s
                 # not canAs and not canAt
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 1 seed"),
                                   "execute if block ~ ~ ~ granite run seed"),
                 (converter.decide("execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 seed"),
                                   "execute at @s[name=Carl] if block ~ ~ ~ granite run seed"),
                 (converter.decide("execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 seed"),
                                   "execute positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),
                 (converter.decide("execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 seed"),
                                   "execute at @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),

                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s ~ ~ ~ detect ~ ~ ~ stone 1 seed"),
                                   "execute if block ~ ~ ~ diorite if block ~ ~ ~ granite run seed"),
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 seed"),
                                   "execute if block ~ ~ ~ diorite at @s[name=Carl] if block ~ ~ ~ granite run seed"),
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 seed"),
                                   "execute if block ~ ~ ~ diorite positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 seed"),
                                   "execute if block ~ ~ ~ diorite at @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),

                 # canAs and not canAt
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 1 say hi"),
                                   "execute if block ~ ~ ~ granite run say hi"),
                 (converter.decide("execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 say hi"),
                                   "execute as @s[name=Carl] if block ~ ~ ~ granite run say hi"),
                 (converter.decide("execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi"),
                                   "execute positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),
                 (converter.decide("execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi"),
                                   "execute as @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),

                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s ~ ~ ~ detect ~ ~ ~ stone 1 say hi"),
                                   "execute if block ~ ~ ~ diorite if block ~ ~ ~ granite run say hi"),
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 say hi"),
                                   "execute if block ~ ~ ~ diorite as @s[name=Carl] if block ~ ~ ~ granite run say hi"),
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi"),
                                   "execute if block ~ ~ ~ diorite positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi"),
                                   "execute if block ~ ~ ~ diorite as @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),

                 # not canAs and canAt
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone"),
                                   "execute if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone"),
                                   "execute at @s[name=Carl] if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone"),
                                   "execute positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone"),
                                   "execute at @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),

                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone"),
                                   "execute if block ~ ~ ~ diorite if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone"),
                                   "execute if block ~ ~ ~ diorite at @s[name=Carl] if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone"),
                                   "execute if block ~ ~ ~ diorite positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone"),
                                   "execute if block ~ ~ ~ diorite at @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),

                 # canAs and canAt
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def"),
                                   "execute if block ~ ~ ~ granite run function abc:def"),
                 (converter.decide("execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def"),
                                   "execute as @s[name=Carl] if block ~ ~ ~ granite run function abc:def"),
                 (converter.decide("execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def"),
                                   "execute positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),
                 (converter.decide("execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def"),
                                   "execute as @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),

                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def"),
                                   "execute if block ~ ~ ~ diorite if block ~ ~ ~ granite run function abc:def"),
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def"),
                                   "execute if block ~ ~ ~ diorite as @s[name=Carl] if block ~ ~ ~ granite run function abc:def"),
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def"),
                                   "execute if block ~ ~ ~ diorite positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),
                 (converter.decide("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def"),
                                   "execute if block ~ ~ ~ diorite as @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),

                 # @e
                 # not canAs and not canAt
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 1 seed"),
                                   "execute at @e if block ~ ~ ~ granite run seed"),
                 (converter.decide("execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 seed"),
                                   "execute at @e[name=Carl] if block ~ ~ ~ granite run seed"),
                 (converter.decide("execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 seed"),
                                   "execute at @e positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),
                 (converter.decide("execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 seed"),
                                   "execute at @e[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),

                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e ~ ~ ~ detect ~ ~ ~ stone 1 seed"),
                                   "execute at @e if block ~ ~ ~ diorite at @e if block ~ ~ ~ granite run seed"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 seed"),
                                   "execute at @e if block ~ ~ ~ diorite at @e[name=Carl] if block ~ ~ ~ granite run seed"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 seed"),
                                   "execute at @e if block ~ ~ ~ diorite at @e positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 seed"),
                                   "execute at @e if block ~ ~ ~ diorite at @e[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),

                 # canAs and not canAt
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 1 say hi"),
                                   "execute as @e at @s if block ~ ~ ~ granite run say hi"),
                 (converter.decide("execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 say hi"),
                                   "execute as @e[name=Carl] at @s if block ~ ~ ~ granite run say hi"),
                 (converter.decide("execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi"),
                                   "execute as @e at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),
                 (converter.decide("execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi"),
                                   "execute as @e[name=Carl] at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),

                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e ~ ~ ~ detect ~ ~ ~ stone 1 say hi"),
                                   "execute as @e at @s if block ~ ~ ~ diorite as @e at @s if block ~ ~ ~ granite run say hi"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 say hi"),
                                   "execute as @e at @s if block ~ ~ ~ diorite as @e[name=Carl] at @s if block ~ ~ ~ granite run say hi"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi"),
                                   "execute as @e at @s if block ~ ~ ~ diorite as @e at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi"),
                                   "execute as @e at @s if block ~ ~ ~ diorite as @e[name=Carl] at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),

                 # not canAs and canAt
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone"),
                                   "execute at @e if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone"),
                                   "execute at @e[name=Carl] if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone"),
                                   "execute at @e positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone"),
                                   "execute at @e[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),

                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone"),
                                   "execute at @e if block ~ ~ ~ diorite at @e if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone"),
                                   "execute at @e if block ~ ~ ~ diorite at @e[name=Carl] if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone"),
                                   "execute at @e if block ~ ~ ~ diorite at @e positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone"),
                                   "execute at @e if block ~ ~ ~ diorite at @e[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),

                 # canAs and canAt
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def"),
                                   "execute as @e at @s if block ~ ~ ~ granite run function abc:def"),
                 (converter.decide("execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def"),
                                   "execute as @e[name=Carl] at @s if block ~ ~ ~ granite run function abc:def"),
                 (converter.decide("execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def"),
                                   "execute as @e at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),
                 (converter.decide("execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def"),
                                   "execute as @e[name=Carl] at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),

                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def"),
                                   "execute as @e at @s if block ~ ~ ~ diorite as @e at @s if block ~ ~ ~ granite run function abc:def"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def"),
                                   "execute as @e at @s if block ~ ~ ~ diorite as @e[name=Carl] at @s if block ~ ~ ~ granite run function abc:def"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def"),
                                   "execute as @e at @s if block ~ ~ ~ diorite as @e at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def"),
                                   "execute as @e at @s if block ~ ~ ~ diorite as @e[name=Carl] at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Fill(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["fill", "1", "~-1", "~1", "1", "~-1", "~1", "stone", "1",
                                ["destroy", "hollow", "keep", "outline"], nbt()], optional=3)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("fill",
                 "fill 1",
                 "fill a ~-1 ~1 1 ~-1 ~1 stone 1 hollow {abc:def}",
                 "fill 1 ~-1",
                 "fill 1 aaa ~1 1 ~-1 ~1 stone 1 hollow {abc:def}",
                 "fill 1 ~-1 ~1",
                 "fill 1 ~-1 aa 1 ~-1 ~1 stone 1 hollow {abc:def}",
                 "fill 1 ~-1 ~1 1",
                 "fill 1 ~-1 ~1 a ~-1 ~1 stone 1 hollow {abc:def}",
                 "fill 1 ~-1 ~1 1 ~-1",
                 "fill 1 ~-1 ~1 1 aaa ~1 stone 1 hollow {abc:def}",
                 "fill 1 ~-1 ~1 1 ~-1 ~1",
                 "fill 1 ~-1 ~1 1 ~-1 aa stone 1 hollow {abc:def}",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone a hollow {abc:def}",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone -2 hollow {abc:def}",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 16 hollow {abc:def}",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 aaaaaa {abc:def}",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 hollow aaaaaaaaa",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 hollow {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1"), "fill 1 ~-1 ~1 1 ~-1 ~1 granite"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 destroy"), "fill 1 ~-1 ~1 1 ~-1 ~1 granite destroy"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 destroy {abc:def}"), "fill 1 ~-1 ~1 1 ~-1 ~1 granite{abc:def} destroy"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 hollow"), "fill 1 ~-1 ~1 1 ~-1 ~1 granite hollow"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 hollow {abc:def}"), "fill 1 ~-1 ~1 1 ~-1 ~1 granite{abc:def} hollow"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 keep"), "fill 1 ~-1 ~1 1 ~-1 ~1 granite keep"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 keep {abc:def}"), "fill 1 ~-1 ~1 1 ~-1 ~1 granite{abc:def} keep"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 outline"), "fill 1 ~-1 ~1 1 ~-1 ~1 granite outline"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 outline {abc:def}"), "fill 1 ~-1 ~1 1 ~-1 ~1 granite{abc:def} outline"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["fill", "1", "~-1", "~1", "1", "~-1", "~1", "stone", "1", "replace", "stone", "2"], optional=2)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("fill",
                 "fill 1",
                 "fill a ~-1 ~1 1 ~-1 ~1 stone 1 replace stone 2",
                 "fill 1 ~-1",
                 "fill 1 aaa ~1 1 ~-1 ~1 stone 1 replace stone 2",
                 "fill 1 ~-1 ~1",
                 "fill 1 ~-1 aa 1 ~-1 ~1 stone 1 replace stone 2",
                 "fill 1 ~-1 ~1 1",
                 "fill 1 ~-1 ~1 a ~-1 ~1 stone 1 replace stone 2",
                 "fill 1 ~-1 ~1 1 ~-1",
                 "fill 1 ~-1 ~1 1 aaa ~1 stone 1 replace stone 2",
                 "fill 1 ~-1 ~1 1 ~-1 ~1",
                 "fill 1 ~-1 ~1 1 ~-1 aa stone 1 replace stone 2",
                 "fill 1 ~-1 ~1 1 ~-1 aa aaaaa 1 replace stone 2",
                 "fill 1 ~-1 ~1 1 ~-1 aa stone a replace stone 2",
                 "fill 1 ~-1 ~1 1 ~-1 aa stone -1 replace stone 2",
                 "fill 1 ~-1 ~1 1 ~-1 aa stone 16 replace stone 2",
                 "fill 1 ~-1 ~1 1 ~-1 aa stone 1 aaaaaaa stone 2",
                 "fill 1 ~-1 ~1 1 ~-1 aa stone 1 replace aaaaa 2",
                 "fill 1 ~-1 ~1 1 ~-1 aa stone 1 replace stone a",
                 "fill 1 ~-1 ~1 1 ~-1 aa stone 1 replace stone -2",
                 "fill 1 ~-1 ~1 1 ~-1 aa stone 1 replace stone 16",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace stone 2 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace"), "fill 1 ~-1 ~1 1 ~-1 ~1 granite replace"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace stone"), "fill 1 ~-1 ~1 1 ~-1 ~1 granite replace stone"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace stone 2"), "fill 1 ~-1 ~1 1 ~-1 ~1 granite replace polished_granite"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Function(TestBase):
    def test_syntax1_ok(self):
        perms = ("function custom:example/test", )
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("function",
                 "function aaaaaaaaaaaaaaaaaaa",
                 "function custom:example/test ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("function custom:example/test"), "function custom:example/test"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["function", "custom:example/test", ["if", "unless"], "@s"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("function",
                 "function aaaaaaaaaaaaaaaaaaa if @s",
                 "function custom:example/test if",
                 "function custom:example/test aa @s",
                 "function custom:example/test if @c",
                 "function custom:example/test if @s ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("function custom:example/test if @s"), "execute if entity @s run function custom:example/test"),
                 (converter.decide("function custom:example/test unless @s"), "execute unless entity @s run function custom:example/test"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class GameMode(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["gamemode", ["0", "1", "2", "3", "s", "c", "a", "sp", "survival", "creative", "adventure", "spectator"], "@s"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("gamemode",
                 "gamemode o @s",
                 "gamemode 1 @c",
                 "gamemode 1 @s ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("gamemode 0"), "gamemode survival"),
                 (converter.decide("gamemode 1"), "gamemode creative"),
                 (converter.decide("gamemode 2"), "gamemode adventure"),
                 (converter.decide("gamemode 3"), "gamemode spectator"),
                 (converter.decide("gamemode 0 @s"), "gamemode survival @s"),
                 (converter.decide("gamemode 1 @s"), "gamemode creative @s"),
                 (converter.decide("gamemode 2 @s"), "gamemode adventure @s"),
                 (converter.decide("gamemode 3 @s"), "gamemode spectator @s"),
                 (converter.decide("gamemode s"), "gamemode survival"),
                 (converter.decide("gamemode c"), "gamemode creative"),
                 (converter.decide("gamemode a"), "gamemode adventure"),
                 (converter.decide("gamemode sp"), "gamemode spectator"),
                 (converter.decide("gamemode s @s"), "gamemode survival @s"),
                 (converter.decide("gamemode c @s"), "gamemode creative @s"),
                 (converter.decide("gamemode a @s"), "gamemode adventure @s"),
                 (converter.decide("gamemode sp @s"), "gamemode spectator @s"),
                 (converter.decide("gamemode survival"), "gamemode survival"),
                 (converter.decide("gamemode creative"), "gamemode creative"),
                 (converter.decide("gamemode adventure"), "gamemode adventure"),
                 (converter.decide("gamemode spectator"), "gamemode spectator"),
                 (converter.decide("gamemode survival @s"), "gamemode survival @s"),
                 (converter.decide("gamemode creative @s"), "gamemode creative @s"),
                 (converter.decide("gamemode adventure @s"), "gamemode adventure @s"),
                 (converter.decide("gamemode spectator @s"), "gamemode spectator @s"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class GameRule(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["gamerule", "gameLoopFunction", "true"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("gamerule",
                 "gamerule gameLoopFunction kappa ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("gamerule gameLoopFunction"), "gamerule gameLoopFunction"),
                 (converter.decide("gamerule gameLoopFunction true"), "gamerule gameLoopFunction true"),
                 (converter.decide("gamerule custom"), "#~ gamerule custom ||| Custom gamerules are no longer supported"),
                 (converter.decide("gamerule custom val"), "#~ gamerule custom val ||| Custom gamerules are no longer supported"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Give(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["give", "@s", "stone", "11", "1", nbt()], optional=3)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("give",
                 "give @s",
                 "give @c stone 11 1 {abc:def}",
                 "give @s stone aa 1 {abc:def}",
                 "give @s stone 0 1 {abc:def}",
                 "give @s stone 65 1 {abc:def}",
                 "give @s stone 11 a {abc:def}",
                 "give @s stone 11 1 aaaaaaaaa",
                 "give @s stone 11 1 {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("give @s stone"), "give @s stone"),
                 (converter.decide("give @s stone 11"), "give @s stone 11"),
                 (converter.decide("give @s stone 11 1"), "give @s granite 11"),
                 (converter.decide("give @s stone 11 1 {abc:def}"), "give @s granite{abc:def} 11"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Help(TestBase):
    def test_syntax1_ok(self):
        perms = ["help"]
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("aaaa", )
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("help"), "help"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["help", converter.Globals.commands+map(str, xrange(1, 9))])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("help aaaa",
                 "help kill ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = [(converter.decide("help {}".format(arg)), "help {}".format(arg)) for arg in converter.Globals.commands+map(str, xrange(1, 9))]
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Kick(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["kick", "p_name", ["Because", "Because I said so"]], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("ban", )
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("kick p_name Because"), "kick p_name Because"),
                 (converter.decide("kick p_name Because I said so"), "kick p_name Because I said so"),
                 (converter.decide("kick p_name"), "kick p_name"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Kill(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["kill", "p_name"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("kill @s ImNotSupposedToBeHere",)
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("kill p_name"), "kill p_name"),
                 (converter.decide("kill"), "kill"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class List(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["list", "uuids"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("list aaaaa",
                 "list uuids ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("list uuids"), "list uuids"),
                 (converter.decide("list"), "list"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Locate(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["locate", ["EndCity", "Fortress", "Mansion", "Mineshaft", "Monument", "Stronghold", "Temple", "Village"]])
        for perm in perms:
            print perm
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("locate",
                 "locate aaaaaa",
                 "locate Temple ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("locate Temple"), "locate Temple"),
                 (converter.decide("locate Monument"), "locate Monument"),
                 (converter.decide("locate Mansion"), "locate Mansion"),
                 (converter.decide("locate Village"), "locate Village"),
                 (converter.decide("locate Mineshaft"), "locate Mineshaft"),
                 (converter.decide("locate Fortress"), "locate Fortress"),
                 (converter.decide("locate EndCity"), "locate EndCity"),
                 (converter.decide("locate Stronghold"), "locate Stronghold"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Me(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["me", ["action", "more actions"]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("me", )
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("me action"), "me action"),
                 (converter.decide("me more actions"), "me more actions"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Op(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["op", "@s"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("op",
                 "op @s ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("op @s"), "op @s"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Pardon(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["pardon", "p_name"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("pardon",
                 "pardon @s ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("pardon p_name"), "pardon p_name"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Pardon_IP(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["pardon-ip", "p_name"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("pardon-ip",
                 "pardon-ip 127.0.0.1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("pardon-ip 127.0.0.1"), "pardon-ip 127.0.0.1"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Particle(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["particle", list(converter.Globals.particles), "1", "~-1", "~1", "1", "2", "3", "1", "10", "force", "@s", ["params", "pa rams"]], optional=4)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        self.assertTrue(False)
        perms = ("",
                 "")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        self.assertTrue(False)
        tests = ((converter.decide(""), ""), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()
