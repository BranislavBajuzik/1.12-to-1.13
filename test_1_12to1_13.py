from unittest import TestCase
from itertools import permutations
import random
import inspect
converter = __import__("1_12to1_13byTheAl_T")

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

    def assertPass(self, *args):
        self.asserts += 1

    def assertRaises(self, excClass, callableObj=None, *args, **kwargs):
        super(TestBase, self).assertRaises(excClass, callableObj)
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
            self.assertRaises(SyntaxError, lambda: converter.Selector(case))

        argPairs = (("x", "a"), ("y", "a"), ("z", "a"), ("dx", "a"), ("dy", "a"), ("dz", "a"), ("type", "bad"),
                    ("type", "!bad"), ("lm", "a"), ("l", "a"), ("m", "bad"), ("score_won", "a"), ("score_won_min", "a"),
                    ("rm", "a"), ("r", "a"), ("rxm", "a"), ("rx", "a"), ("rym", "a"), ("ry", "a"), ("c", "a"),
                    ("bad", "bad"), ("x", ""), ("y", ""), ("z", ""), ("dx", ""), ("dy", ""), ("dz", ""), ("type", ""),
                    ("type", ""), ("lm", ""), ("l", ""), ("m", ""), ("score_won", ""), ("score_won_min", ""),
                    ("name", ""), ("rm", ""), ("r", ""), ("rxm", ""), ("rx", ""), ("rym", ""), ("ry", ""), ("c", ""))

        for sType in ("p", "e", "a", "r", "s"):
            for n in (1, 2, 3):
                for argPairsPerm in permutations(argPairs, n):
                    self.assertRaises(SyntaxError, lambda: converter.Selector("@{}[{}]".format(sType, ",".join(map(lambda x: "{}={}".format(x[0], x[1]), argPairsPerm)))))
        self.assertStats()


class Advancement(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["advancement", ["grant", "revoke"], "@s", ["only", "until", "from", "through"], "adv_name", ["crit", ""]])
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
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax3_convert(self):
        tests = ((converter.decide("advancement test @s adv_name crit"), "execute if entity @s[advancements={adv_name={crit=true}}]"),
                 (converter.decide("advancement test @s adv_name"), "execute if entity @s[advancements={adv_name=true}]"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Ban(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["ban", "p_name", ["Because", "Because I said so", ""]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("ban",)
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
        perms = generate_perms(["ban-ip", "p_name", ["because", "Because I said so", ""]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("ban-ip",)
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
                 "clear @s minecraft:stone a 42 {abc:def}",
                 "clear @s minecraft:stone 1 aa {abc:def}",
                 "clear @s minecraft:stone 1 42 aaaaaaaaa")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("clear"), "clear"),
                 (converter.decide("clear @s"), "clear @s"),
                 (converter.decide("clear @s minecraft:stone"), "clear @s stone"),
                 (converter.decide("clear @s minecraft:stone 1"), "clear @s stone{Damage:1}"),
                 (converter.decide("clear @s minecraft:stone 1 42"), "clear @s stone{Damage:1} 42"),
                 (converter.decide("clear @s minecraft:stone 1 42 {abc:def}"), "clear @s stone{abc:def,Damage:1} 42"))
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
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
                                "filtered", ["force", "move", "normal"], "stone", ["1", ""]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered aaaaa stone 1",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered aaaaa stone a",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force stone 1 lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force stone 1"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone[variant=granite] force"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force stone"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone force"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered move stone 1"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone[variant=granite] move"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered move stone"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone move"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered normal stone 1"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone[variant=granite] normal"),
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
                 "debug start lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
                 "defaultgamemode 1 lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
                 "deop @s lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
                 "difficulty 1 lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
                 "effect @s speed aa 10 true",
                 "effect @s speed 10 aa true",
                 "effect @s speed 10 10 aaaa",
                 "effect @s speed 10 10 true lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("effect @s speed"), "effect give @s speed"),
                 (converter.decide("effect @s speed 11"), "effect give @s speed 11"),
                 (converter.decide("effect @s speed 11 22"), "effect give @s speed 11 22"),
                 (converter.decide("effect @s speed 11 22 true"), "effect give @s speed 11 22 true"),
                 (converter.decide("effect @s speed 11 22 false"), "effect give @s speed 11 22 false"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Enchant(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["enchant", "@s", "sharpness", ["1", ""]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("enchant",
                 "enchant @s",
                 "enchant @c sharpness 1",
                 "enchant @s sharpness a",
                 "enchant @s sharpness 1 lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
                 "entitydata @s {abc:def} lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("entitydata @s {abc:def}"), "data merge entity @s {abc:def}"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Execute(TestBase):  # ToDo k i l l  m e
    def test_syntax1_ok(self):
        self.assertTrue(False)
        perms = generate_perms(["", ""])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        self.assertTrue(False)
        perms = ("",
                 "")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax1_convert(self):
        self.assertTrue(False)
        tests = ((converter.decide(""), ""), )
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
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 aaaaaa {abc:def}",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 hollow aaaaaaaaa",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 hollow {abc:def} lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone[variant=granite]"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 destroy"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone[variant=granite] destroy"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 destroy {abc:def}"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone[variant=granite]{abc:def} destroy"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 hollow"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone[variant=granite] hollow"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 hollow {abc:def}"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone[variant=granite]{abc:def} hollow"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 keep"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone[variant=granite] keep"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 keep {abc:def}"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone[variant=granite]{abc:def} keep"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 outline"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone[variant=granite] outline"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 outline {abc:def}"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone[variant=granite]{abc:def} outline"))
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
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace stone 2 lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone[variant=granite] replace"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace stone"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone[variant=granite] replace stone"),
                 (converter.decide("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace stone 2"), "fill 1 ~-1 ~1 1 ~-1 ~1 stone[variant=granite] replace stone[variant=smooth_granite]"))
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
                 "function custom:example/test lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
                 "function custom:example/test if @s lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("function custom:example/test if @s"), "execute if entity @s run function custom:example/test"),
                 (converter.decide("function custom:example/test unless @s"), "execute unless entity @s run function custom:example/test"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class GameMode(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["gamemode", ["0", "1", "2", "3", "s", "c", "a", "sp", "survival", "creative", "adventure", "spectator"], ["@s", ""]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("gamemode",
                 "gamemode o @s",
                 "gamemode 1 @c",
                 "gamemode 1 @s lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
        perms = generate_perms(["gamerule", "gameLoopFunction", ["kappa", ""]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("gamerule",
                 "gamerule gameLoopFunction kappa lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("gamerule gameLoopFunction"), "gamerule gameLoopFunction"),
                 (converter.decide("gamerule gameLoopFunction kappa"), "gamerule gameLoopFunction kappa"),
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
                 "give @s stone 11 a {abc:def}",
                 "give @s stone 11 1 aaaaaaaaa",
                 "give @s stone 11 1 {abc:def} lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("give @s stone"), "give @s stone"),
                 (converter.decide("give @s stone 11"), "give @s stone 11"),
                 (converter.decide("give @s stone 11 1"), "give @s stone{Damage:1} 11"),
                 (converter.decide("give @s stone 11 1 {abc:def}"), "give @s stone{abc:def,Damage:1} 11"))
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
        perms = ("gamerule", )
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("help"), "help"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["help", converter.Globals.commands+map(str, range(1, 9))])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("help aaaa",
                 "help kill lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax2_convert(self):
        tests = [(converter.decide("help {}".format(arg)), "help {}".format(arg)) for arg in converter.Globals.commands+map(str, range(1, 9))]
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Kick(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["kick", "p_name", ["Because", "Because I said so", ""]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("ban",)
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
        perms = generate_perms(["kill", ["p_name", ""]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("kill @s lolo",)
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("kill p_name"), "kill p_name"),
                 (converter.decide("kill"), "kill"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class List(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["list", ["uuids", ""]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("list aaaaa",
                 "list uuids lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
                 "locate Temple lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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


class me(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["me", ["action", "more actions"]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("me", )
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("me action"), "me action"),
                 (converter.decide("me more actions"), "me more actions"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class op(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["op", "@s"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("op",
                 "op @s lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
                 "pardon @s lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
                 "pardon-ip 127.0.0.1 lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
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
            print perm
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        self.assertTrue(False)
        perms = ("",
                 "")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.assertStats()

    def test_syntax1_convert(self):
        self.assertTrue(False)
        tests = ((converter.decide(""), ""), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()
