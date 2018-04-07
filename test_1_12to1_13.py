from unittest import TestCase, skip
from itertools import permutations
import random, inspect, atexit
converter = __import__("1_12to1_13")

if type(u"") is str:
    _map = map
    _filter = filter
    xrange = range
    raw_input = input
    map = lambda x, y: list(_map(x, y))
    filter = lambda x, y: list(_filter(x, y))
    unicode = lambda x: x.__unicode__() if hasattr(x, '__unicode__') else str(x)


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
    return [r'{ key : value ,secondKey :"secondValue", aNumber: 30, byte: 1b, short: 1s, comp:{aKey:aValue}, list:[wooo, weeee]}', "{}"]


@atexit.register
def total():
    print("Total assertions made: {}".format(TestBase.totalAssertions))


class TestBase(TestCase):
    classAssertions = 0
    totalAssertions = 0

    @classmethod
    def tearDownClass(cls):
        print("\n{} assertions in {}:\n".format(TestBase.classAssertions, cls.__name__))
        TestBase.classAssertions = 0

    def asserts(self):
        self.assertStat += 1
        TestBase.classAssertions += 1
        TestBase.totalAssertions += 1

    def setUp(self):
        self.assertStat = 0
        reload(converter)

    def assertStats(self):
        stack = inspect.stack()
        print("\t{} assertion{} made in {}".format(self.assertStat, 's' if self.assertStat != 1 else '', stack[1][0].f_code.co_name))

    def decide(self, raw):
        ret = converter.decide(raw)
        self.asserts()
        return ret

    def assertPass(self, _):
        self.asserts()
        
    def assertTrue(self, expr, msg=None):
        super(TestBase, self).assertTrue(expr, msg)
        self.asserts()
        
    def assertFalse(self, expr, msg=None):
        super(TestBase, self).assertFalse(expr, msg)
        self.asserts()

    def assertRaises(self, excClass, argument, isFunction=False):
        try:
            if isFunction:
                super(TestBase, self).assertRaises(excClass, argument)
            else:
                super(TestBase, self).assertRaises(excClass, lambda: self.decide(argument))
        except AssertionError:
            raise AssertionError("{} didn't throw {}".format(argument, excClass))

        self.asserts()

    def assertEqual(self, first, second, msg=None):
        super(TestBase, self).assertEqual(first, second, msg)
        self.asserts()


class Selector(TestBase):
    def test_syntax_ok(self):
        self.assertPass(converter.Selector("playerName"))
        self.assertPass(converter.Selector("player_name"))
        self.assertPass(converter.Selector("@a[]"))

        argPairs = (("x", "1"), ("y", "1"), ("z", "1"), ("dx", "1"), ("dy", "1"), ("dz", "1"), ("type", "Cow"),
                    ("type", "!Cow"), ("type", "player"), ("type", "!player"), ("lm", "1"), ("l", "1"), ("m", "1"),
                    ("m", "!0"), ("m", "a"), ("m", "sp"), ("m", "creative"), ("team", "blue"), ("team", ""),
                    ("team", "!"), ("team", "!blue"), ("score_won", "1"), ("score_won_min", "1"), ("name", "TheAl_T"),
                    ("tag", "inGame"), ("tag", "!inGame"), ("tag", ""), ("tag", "!"), ("rm", "1"), ("r", "1"),
                    ("rxm", "1"), ("rx", "1"), ("rym", "1"), ("ry", "1"), ("c", "-1"), ("c", "0"), ("c", "1"))

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

    @skip("Not implemented")
    def test_syntax_convert(self):
        tests = ((converter.decide(""), ""),
                 (converter.decide(""), ""),
                 (converter.decide(""), ""),
                 (converter.decide(""), ""),
                 (converter.decide(""), ""),
                 (converter.decide(""), ""),
                 (converter.decide(""), ""),
                 (converter.decide(""), ""))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()
        
    def test_is_single(self):
        self.assertTrue(converter.Selector("@p").isSingle())
        self.assertTrue(converter.Selector("@e[c=1]").isSingle())
        self.assertTrue(converter.Selector("@e[c=-1]").isSingle())
        self.assertTrue(converter.Selector("@a[c=1]").isSingle())
        self.assertTrue(converter.Selector("@a[c=-1]").isSingle())
        self.assertTrue(converter.Selector("@r").isSingle())
        self.assertTrue(converter.Selector("@s").isSingle())
        
        self.assertFalse(converter.Selector("@e").isSingle())
        self.assertFalse(converter.Selector("@e[c=2]").isSingle())
        self.assertFalse(converter.Selector("@e[c=-2]").isSingle())
        self.assertFalse(converter.Selector("@a").isSingle())
        self.assertFalse(converter.Selector("@a[c=2]").isSingle())
        self.assertFalse(converter.Selector("@a[c=-2]").isSingle())
        self.assertFalse(converter.Selector("@r[c=2]").isSingle())
        self.assertFalse(converter.Selector("@r[c=-2]").isSingle())


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
                 "advancement grant @s only adv_name crit ImNotSupposedToBeHere")
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
                 "advancement grant @s everything ImNotSupposedToBeHere")
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
                 "advancement test @s adv_name crit ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = ((converter.decide("advancement test @s adv_name crit"), "execute if entity @s[advancements={adv_name={crit=true}}]"),
                 (converter.decide("advancement test @s adv_name"), "execute if entity @s[advancements={adv_name=true}]"),
                 (converter.decide("advancement test Carl adv_name crit"), "execute if entity @p[name=Carl,advancements={adv_name={crit=true}}]"),
                 (converter.decide("advancement test Carl adv_name"), "execute if entity @p[name=Carl,advancements={adv_name=true}]"))
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
                 "blockdata 1 ~ ~3 {abc:def} ImNotSupposedToBeHere")
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
        perms = generate_perms(["clear", "@s", "stone", "1", "42", nbt()], optional=5)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("clear @c stone 1 42 {abc:def}",
                 "clear @s aaaaa 1 42 {abc:def}",
                 "clear @s stone -2 42 {abc:def}",
                 "clear @s stone 16 42 {abc:def}",
                 "clear @s stone a 42 {abc:def}",
                 "clear @s stone a -1 {abc:def}",
                 "clear @s stone 1 aa {abc:def}",
                 "clear @s stone 1 42 aaaaaaaaa",
                 "clear @s stone 1 42 {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    @skip("Not implemented")
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
        perms = generate_perms(["clone", coord(), coord(), coord(), coord(), coord(), coord(), coord(), coord(), coord(),
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
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace force ImNotSupposedToBeHere")
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
        perms = generate_perms(["clone", coord(), coord(), coord(), coord(), coord(), coord(), coord(), coord(), coord(),
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

    def test_syntax2_convert(self):
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
                 "effect @s aaaaa 10 10 true",
                 "effect @s speed -1 10 true",
                 "effect @s speed 1000001 10 true",
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
                 "enchant @s aaaaaaaaa a",
                 "enchant @s sharpness 0",
                 "enchant @s sharpness 6",
                 "enchant @s sharpness a",
                 "enchant @s sharpness 1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("enchant @s 0"), "enchant @s protection"),
                 (converter.decide("enchant @s 0 1"), "enchant @s protection"),
                 (converter.decide("enchant @s 0 2"), "enchant @s protection 2"),
                 (converter.decide("enchant @s protection"), "enchant @s protection"),
                 (converter.decide("enchant @s protection 1"), "enchant @s protection"),
                 (converter.decide("enchant @s protection 2"), "enchant @s protection 2"),
                
                 (converter.decide("enchant @s 1"), "enchant @s fire_protection"),
                 (converter.decide("enchant @s 1 1"), "enchant @s fire_protection"),
                 (converter.decide("enchant @s 1 2"), "enchant @s fire_protection 2"),
                 (converter.decide("enchant @s fire_protection"), "enchant @s fire_protection"),
                 (converter.decide("enchant @s fire_protection 1"), "enchant @s fire_protection"),
                 (converter.decide("enchant @s fire_protection 2"), "enchant @s fire_protection 2"),

                 (converter.decide("enchant @s 2"), "enchant @s feather_falling"),
                 (converter.decide("enchant @s 2 1"), "enchant @s feather_falling"),
                 (converter.decide("enchant @s 2 2"), "enchant @s feather_falling 2"),
                 (converter.decide("enchant @s feather_falling"), "enchant @s feather_falling"),
                 (converter.decide("enchant @s feather_falling 1"), "enchant @s feather_falling"),
                 (converter.decide("enchant @s feather_falling 2"), "enchant @s feather_falling 2"),

                 (converter.decide("enchant @s 3"), "enchant @s blast_protection"),
                 (converter.decide("enchant @s 3 1"), "enchant @s blast_protection"),
                 (converter.decide("enchant @s 3 2"), "enchant @s blast_protection 2"),
                 (converter.decide("enchant @s blast_protection"), "enchant @s blast_protection"),
                 (converter.decide("enchant @s blast_protection 1"), "enchant @s blast_protection"),
                 (converter.decide("enchant @s blast_protection 2"), "enchant @s blast_protection 2"),

                 (converter.decide("enchant @s 4"), "enchant @s projectile_protection"),
                 (converter.decide("enchant @s 4 1"), "enchant @s projectile_protection"),
                 (converter.decide("enchant @s 4 2"), "enchant @s projectile_protection 2"),
                 (converter.decide("enchant @s projectile_protection"), "enchant @s projectile_protection"),
                 (converter.decide("enchant @s projectile_protection 1"), "enchant @s projectile_protection"),
                 (converter.decide("enchant @s projectile_protection 2"), "enchant @s projectile_protection 2"),

                 (converter.decide("enchant @s 5"), "enchant @s respiration"),
                 (converter.decide("enchant @s 5 1"), "enchant @s respiration"),
                 (converter.decide("enchant @s 5 2"), "enchant @s respiration 2"),
                 (converter.decide("enchant @s respiration"), "enchant @s respiration"),
                 (converter.decide("enchant @s respiration 1"), "enchant @s respiration"),
                 (converter.decide("enchant @s respiration 2"), "enchant @s respiration 2"),

                 (converter.decide("enchant @s 6"), "enchant @s aqua_affinity"),
                 (converter.decide("enchant @s 6 1"), "enchant @s aqua_affinity"),
                 (converter.decide("enchant @s aqua_affinity"), "enchant @s aqua_affinity"),
                 (converter.decide("enchant @s aqua_affinity 1"), "enchant @s aqua_affinity"),

                 (converter.decide("enchant @s 7"), "enchant @s thorns"),
                 (converter.decide("enchant @s 7 1"), "enchant @s thorns"),
                 (converter.decide("enchant @s 7 2"), "enchant @s thorns 2"),
                 (converter.decide("enchant @s thorns"), "enchant @s thorns"),
                 (converter.decide("enchant @s thorns 1"), "enchant @s thorns"),
                 (converter.decide("enchant @s thorns 2"), "enchant @s thorns 2"),

                 (converter.decide("enchant @s 8"), "enchant @s depth_strider"),
                 (converter.decide("enchant @s 8 1"), "enchant @s depth_strider"),
                 (converter.decide("enchant @s 8 2"), "enchant @s depth_strider 2"),
                 (converter.decide("enchant @s depth_strider"), "enchant @s depth_strider"),
                 (converter.decide("enchant @s depth_strider 1"), "enchant @s depth_strider"),
                 (converter.decide("enchant @s depth_strider 2"), "enchant @s depth_strider 2"),

                 (converter.decide("enchant @s 9"), "enchant @s frost_walker"),
                 (converter.decide("enchant @s 9 1"), "enchant @s frost_walker"),
                 (converter.decide("enchant @s 9 2"), "enchant @s frost_walker 2"),
                 (converter.decide("enchant @s frost_walker"), "enchant @s frost_walker"),
                 (converter.decide("enchant @s frost_walker 1"), "enchant @s frost_walker"),
                 (converter.decide("enchant @s frost_walker 2"), "enchant @s frost_walker 2"),

                 (converter.decide("enchant @s 10"), "enchant @s binding_curse"),
                 (converter.decide("enchant @s 10 1"), "enchant @s binding_curse"),
                 (converter.decide("enchant @s binding_curse"), "enchant @s binding_curse"),
                 (converter.decide("enchant @s binding_curse 1"), "enchant @s binding_curse"),

                 (converter.decide("enchant @s 16"), "enchant @s sharpness"),
                 (converter.decide("enchant @s 16 1"), "enchant @s sharpness"),
                 (converter.decide("enchant @s 16 2"), "enchant @s sharpness 2"),
                 (converter.decide("enchant @s sharpness"), "enchant @s sharpness"),
                 (converter.decide("enchant @s sharpness 1"), "enchant @s sharpness"),
                 (converter.decide("enchant @s sharpness 2"), "enchant @s sharpness 2"),

                 (converter.decide("enchant @s 17"), "enchant @s smite"),
                 (converter.decide("enchant @s 17 1"), "enchant @s smite"),
                 (converter.decide("enchant @s 17 2"), "enchant @s smite 2"),
                 (converter.decide("enchant @s smite"), "enchant @s smite"),
                 (converter.decide("enchant @s smite 1"), "enchant @s smite"),
                 (converter.decide("enchant @s smite 2"), "enchant @s smite 2"),

                 (converter.decide("enchant @s 18"), "enchant @s bane_of_arthropods"),
                 (converter.decide("enchant @s 18 1"), "enchant @s bane_of_arthropods"),
                 (converter.decide("enchant @s 18 2"), "enchant @s bane_of_arthropods 2"),
                 (converter.decide("enchant @s bane_of_arthropods"), "enchant @s bane_of_arthropods"),
                 (converter.decide("enchant @s bane_of_arthropods 1"), "enchant @s bane_of_arthropods"),
                 (converter.decide("enchant @s bane_of_arthropods 2"), "enchant @s bane_of_arthropods 2"),

                 (converter.decide("enchant @s 19"), "enchant @s knockback"),
                 (converter.decide("enchant @s 19 1"), "enchant @s knockback"),
                 (converter.decide("enchant @s 19 2"), "enchant @s knockback 2"),
                 (converter.decide("enchant @s knockback"), "enchant @s knockback"),
                 (converter.decide("enchant @s knockback 1"), "enchant @s knockback"),
                 (converter.decide("enchant @s knockback 2"), "enchant @s knockback 2"),

                 (converter.decide("enchant @s 20"), "enchant @s fire_aspect"),
                 (converter.decide("enchant @s 20 1"), "enchant @s fire_aspect"),
                 (converter.decide("enchant @s 20 2"), "enchant @s fire_aspect 2"),
                 (converter.decide("enchant @s fire_aspect"), "enchant @s fire_aspect"),
                 (converter.decide("enchant @s fire_aspect 1"), "enchant @s fire_aspect"),
                 (converter.decide("enchant @s fire_aspect 2"), "enchant @s fire_aspect 2"),

                 (converter.decide("enchant @s 21"), "enchant @s looting"),
                 (converter.decide("enchant @s 21 1"), "enchant @s looting"),
                 (converter.decide("enchant @s 21 2"), "enchant @s looting 2"),
                 (converter.decide("enchant @s looting"), "enchant @s looting"),
                 (converter.decide("enchant @s looting 1"), "enchant @s looting"),
                 (converter.decide("enchant @s looting 2"), "enchant @s looting 2"),

                 (converter.decide("enchant @s 22"), "enchant @s sweeping"),
                 (converter.decide("enchant @s 22 1"), "enchant @s sweeping"),
                 (converter.decide("enchant @s 22 2"), "enchant @s sweeping 2"),
                 (converter.decide("enchant @s sweeping"), "enchant @s sweeping"),
                 (converter.decide("enchant @s sweeping 1"), "enchant @s sweeping"),
                 (converter.decide("enchant @s sweeping 2"), "enchant @s sweeping 2"),

                 (converter.decide("enchant @s 32"), "enchant @s efficiency"),
                 (converter.decide("enchant @s 32 1"), "enchant @s efficiency"),
                 (converter.decide("enchant @s 32 2"), "enchant @s efficiency 2"),
                 (converter.decide("enchant @s efficiency"), "enchant @s efficiency"),
                 (converter.decide("enchant @s efficiency 1"), "enchant @s efficiency"),
                 (converter.decide("enchant @s efficiency 2"), "enchant @s efficiency 2"),

                 (converter.decide("enchant @s 33"), "enchant @s silk_touch"),
                 (converter.decide("enchant @s 33 1"), "enchant @s silk_touch"),
                 (converter.decide("enchant @s silk_touch"), "enchant @s silk_touch"),
                 (converter.decide("enchant @s silk_touch 1"), "enchant @s silk_touch"),

                 (converter.decide("enchant @s 34"), "enchant @s unbreaking"),
                 (converter.decide("enchant @s 34 1"), "enchant @s unbreaking"),
                 (converter.decide("enchant @s 34 2"), "enchant @s unbreaking 2"),
                 (converter.decide("enchant @s unbreaking"), "enchant @s unbreaking"),
                 (converter.decide("enchant @s unbreaking 1"), "enchant @s unbreaking"),
                 (converter.decide("enchant @s unbreaking 2"), "enchant @s unbreaking 2"),

                 (converter.decide("enchant @s 35"), "enchant @s fortune"),
                 (converter.decide("enchant @s 35 1"), "enchant @s fortune"),
                 (converter.decide("enchant @s 35 2"), "enchant @s fortune 2"),
                 (converter.decide("enchant @s fortune"), "enchant @s fortune"),
                 (converter.decide("enchant @s fortune 1"), "enchant @s fortune"),
                 (converter.decide("enchant @s fortune 2"), "enchant @s fortune 2"),

                 (converter.decide("enchant @s 48"), "enchant @s power"),
                 (converter.decide("enchant @s 48 1"), "enchant @s power"),
                 (converter.decide("enchant @s 48 2"), "enchant @s power 2"),
                 (converter.decide("enchant @s power"), "enchant @s power"),
                 (converter.decide("enchant @s power 1"), "enchant @s power"),
                 (converter.decide("enchant @s power 2"), "enchant @s power 2"),

                 (converter.decide("enchant @s 49"), "enchant @s punch"),
                 (converter.decide("enchant @s 49 1"), "enchant @s punch"),
                 (converter.decide("enchant @s 49 2"), "enchant @s punch 2"),
                 (converter.decide("enchant @s punch"), "enchant @s punch"),
                 (converter.decide("enchant @s punch 1"), "enchant @s punch"),
                 (converter.decide("enchant @s punch 2"), "enchant @s punch 2"),

                 (converter.decide("enchant @s 50"), "enchant @s flame"),
                 (converter.decide("enchant @s 50 1"), "enchant @s flame"),
                 (converter.decide("enchant @s flame"), "enchant @s flame"),
                 (converter.decide("enchant @s flame 1"), "enchant @s flame"),

                 (converter.decide("enchant @s 51"), "enchant @s infinity"),
                 (converter.decide("enchant @s 51 1"), "enchant @s infinity"),
                 (converter.decide("enchant @s infinity"), "enchant @s infinity"),
                 (converter.decide("enchant @s infinity 1"), "enchant @s infinity"),

                 (converter.decide("enchant @s 61"), "enchant @s luck_of_the_sea"),
                 (converter.decide("enchant @s 61 1"), "enchant @s luck_of_the_sea"),
                 (converter.decide("enchant @s 61 2"), "enchant @s luck_of_the_sea 2"),
                 (converter.decide("enchant @s luck_of_the_sea"), "enchant @s luck_of_the_sea"),
                 (converter.decide("enchant @s luck_of_the_sea 1"), "enchant @s luck_of_the_sea"),
                 (converter.decide("enchant @s luck_of_the_sea 2"), "enchant @s luck_of_the_sea 2"),

                 (converter.decide("enchant @s 62"), "enchant @s lure"),
                 (converter.decide("enchant @s 62 1"), "enchant @s lure"),
                 (converter.decide("enchant @s 62 2"), "enchant @s lure 2"),
                 (converter.decide("enchant @s lure"), "enchant @s lure"),
                 (converter.decide("enchant @s lure 1"), "enchant @s lure"),
                 (converter.decide("enchant @s lure 2"), "enchant @s lure 2"),

                 (converter.decide("enchant @s 70"), "enchant @s mending"),
                 (converter.decide("enchant @s 70 1"), "enchant @s mending"),
                 (converter.decide("enchant @s mending"), "enchant @s mending"),
                 (converter.decide("enchant @s mending 1"), "enchant @s mending"),

                 (converter.decide("enchant @s 71"), "enchant @s vanishing_curse"),
                 (converter.decide("enchant @s 71 1"), "enchant @s vanishing_curse"),
                 (converter.decide("enchant @s vanishing_curse"), "enchant @s vanishing_curse"),
                 (converter.decide("enchant @s vanishing_curse 1"), "enchant @s vanishing_curse"))
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
        perms = generate_perms(["execute", "@s", coord(), coord(), coord(), "say hi"])
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
        tests = ((converter.decide("execute @e[name=Carl] 1 ~-1 1 toggledownfall"),
                                   "#~ execute as @e[name=Carl] run toggledownfall ||| This command was removed"),
                 (converter.decide("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 toggledownfall"),
                                   "#~ execute as @e[tag=Carl] as @e[name=Carl] run toggledownfall ||| This command was removed"),


                 # @s
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
        perms = generate_perms(["execute", "@s", coord(), coord(), coord(), "detect", coord(), coord(), coord(), "stone", "1", "say hi"])
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
                 "execute @s 1 ~-1 1 detect 1 ~-1 1 aaaaa 1 say hi",
                 "execute @s 1 ~-1 1 detect 1 ~-1 1 stone",
                 "execute @s 1 ~-1 1 detect 1 ~-1 1 stone a say hi",
                 "execute @s 1 ~-1 1 detect 1 ~-1 1 stone 16 say hi",
                 "execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1",
                 "execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 aaaaaa")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 toggledownfall"),
                                   "#~ execute at @e[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run toggledownfall ||| This command was removed"),
                 (converter.decide("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 toggledownfall"),
                                   "#~ execute at @e if block ~ ~ ~ diorite at @e[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run toggledownfall ||| This command was removed"),


                 # @s
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
        perms = generate_perms(["fill", coord(), coord(), coord(), coord(), coord(), coord(), "stone", "1",
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
                 "fill 1 ~-1 ~1 1 ~-1 ~1 aaaaa 1 hollow {abc:def}",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone a hollow {abc:def}",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone -1 hollow {abc:def}",
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
        perms = generate_perms(["fill", coord(), coord(), coord(), coord(), coord(), coord(), "stone", "1", "replace", "stone", "2"], optional=2)
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
                 "fill 1 ~-1 ~1 1 ~-1 ~1 aaaaa 1 replace stone 2",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone a replace stone 2",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone -1 replace stone 2",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 16 replace stone 2",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 aaaaaaa stone 2",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace aaaaa 2",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace stone a",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace stone -2",
                 "fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace stone 16",
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
        tests = ((converter.decide("function custom:example/test if @s"), "function custom:example/test"),
                 (converter.decide("function custom:example/test unless @s"), "#~ function custom:example/test unless @s ||| unless @s will always fail"),
                 (converter.decide("function custom:example/test if @e"), "execute if entity @e run function custom:example/test"),
                 (converter.decide("function custom:example/test unless @e"), "execute unless entity @e run function custom:example/test"))
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
                 "gamerule gameLoopFunction true ImNotSupposedToBeHere")
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
                 "give @s aaaaa 11 1 {abc:def}",
                 "give @s stone aa 1 {abc:def}",
                 "give @s stone 0 1 {abc:def}",
                 "give @s stone 65 1 {abc:def}",
                 "give @s stone 11 a {abc:def}",
                 "give @s stone 11 1 aaaaaaaaa",
                 "give @s stone 11 1 {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    @skip("Not implemented")
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
        perms = generate_perms([["help", "?"]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("aaaa", )
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("?"), "help"),
                 (converter.decide("help"), "help"),)
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms([["help", "?"], converter.Globals.commands+map(str, xrange(1, 9))])
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
        tests = [(converter.decide("{} {}".format(command, arg)), "help {}".format(arg)) for arg in converter.Globals.commands+map(str, xrange(1, 9)) for command in ("help", "?")]
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
        perms = ("kick", )
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
                 (converter.decide("kill"), "kill @s"))
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
        tests = ((converter.decide("locate Monument"), "locate Monument"),
                 (converter.decide("locate Mansion"), "locate Mansion"),
                 (converter.decide("locate Village"), "locate Village"),
                 (converter.decide("locate Mineshaft"), "locate Mineshaft"),
                 (converter.decide("locate Fortress"), "locate Fortress"),
                 (converter.decide("locate EndCity"), "locate EndCity"),
                 (converter.decide("locate Stronghold"), "locate Stronghold"),
                 (converter.decide("locate Temple"), "#~ The splitting of this command can produce different results if used with stats\n"
                                                     "locate Desert_Pyramid\nlocate Igloo\nlocate Jungle_Pyramid\nlocate Swamp_Hut"))
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
        perms = generate_perms(["particle", list(converter.Globals.particles.keys()), coord(), coord(), coord(), "1", "2", "3", "1", "10", "force", "@s"], optional=3)
        perms.update(generate_perms(["particle", ["blockdust", "blockcrack", "fallingdust", "reddust"], coord(), coord(), coord(), "1", "2", "3", "1", "10", "force", "@s", "1"], optional=4))
        perms.update(generate_perms(["particle", "iconcrack", coord(), coord(), coord(), "1", "2", "3", "1", "10", "force", "@s", "2 3"], optional=4))
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    @skip("Not implemented")
    def test_syntax1_nok(self):
        perms = ("",
                 "")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    @skip("Not implemented")
    def test_syntax1_convert(self):
        tests = ((converter.decide(""), ""), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class PlaySound(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["playsound", "sound", ["master", "music", "record", "weather", "block", "hostile", "neutral", "player", "ambient", "voice"], "@s"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("playsound",
                 "playsound sound",
                 "playsound sound aaaaaa @s",
                 "playsound sound master",
                 "playsound sound master @c",
                 "playsound sound master @s ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("playsound sound master @s"), "playsound sound master @s"),
                 (converter.decide("playsound sound music @s"), "playsound sound music @s"),
                 (converter.decide("playsound sound record @s"), "playsound sound record @s"),
                 (converter.decide("playsound sound weather @s"), "playsound sound weather @s"),
                 (converter.decide("playsound sound block @s"), "playsound sound block @s"),
                 (converter.decide("playsound sound hostile @s"), "playsound sound hostile @s"),
                 (converter.decide("playsound sound neutral @s"), "playsound sound neutral @s"),
                 (converter.decide("playsound sound player @s"), "playsound sound player @s"),
                 (converter.decide("playsound sound ambient @s"), "playsound sound ambient @s"),
                 (converter.decide("playsound sound voice @s"), "playsound sound voice @s"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["playsound", "sound", ["master", "music", "record", "weather", "block", "hostile", "neutral", "player", "ambient", "voice"], "@s", coord(), coord(), coord(), "0.5", "0.5", "0.5"], optional=3)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("playsound",
                 "playsound sound",
                 "playsound sound aaaaaa @s 1 ~-1 ~1 0.5 0.5 0.5",
                 "playsound sound master",
                 "playsound sound master @c 1 ~-1 ~1 0.5 0.5 0.5",
                 "playsound sound master @s a ~-1 ~1 0.5 0.5 0.5",
                 "playsound sound master @s 1",
                 "playsound sound master @s 1 aaa ~1 0.5 0.5 0.5",
                 "playsound sound master @s 1 ~-1",
                 "playsound sound master @s 1 ~-1 aa 0.5 0.5 0.5",
                 "playsound sound master @s 1 ~-1 ~1 aaa 0.5 0.5",
                 "playsound sound master @s 1 ~-1 ~1 -0.1 0.5 0.5",
                 "playsound sound master @s 1 ~-1 ~1 0.5 aaa 0.5",
                 "playsound sound master @s 1 ~-1 ~1 0.5 -0.1 0.5",
                 "playsound sound master @s 1 ~-1 ~1 0.5 2.1 0.5",
                 "playsound sound master @s 1 ~-1 ~1 0.5 0.5 aaa",
                 "playsound sound master @s 1 ~-1 ~1 0.5 0.5 -0.1",
                 "playsound sound master @s 1 ~-1 ~1 0.5 0.5 1.1",
                 "playsound sound master @s 1 ~-1 ~1 0.5 0.5 0.5 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("playsound sound master @s 1 ~-1 ~1 0.5"), "playsound sound master @s 1 ~-1 ~1 0.5"),
                 (converter.decide("playsound sound master @s 1 ~-1 ~1 0.5 0.6"), "playsound sound master @s 1 ~-1 ~1 0.5 0.6"),
                 (converter.decide("playsound sound master @s 1 ~-1 ~1 0.5 0.6 0.7"), "playsound sound master @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 (converter.decide("playsound sound music @s 1 ~-1 ~1 0.5"), "playsound sound music @s 1 ~-1 ~1 0.5"),
                 (converter.decide("playsound sound music @s 1 ~-1 ~1 0.5 0.6"), "playsound sound music @s 1 ~-1 ~1 0.5 0.6"),
                 (converter.decide("playsound sound music @s 1 ~-1 ~1 0.5 0.6 0.7"), "playsound sound music @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 (converter.decide("playsound sound record @s 1 ~-1 ~1 0.5"), "playsound sound record @s 1 ~-1 ~1 0.5"),
                 (converter.decide("playsound sound record @s 1 ~-1 ~1 0.5 0.6"), "playsound sound record @s 1 ~-1 ~1 0.5 0.6"),
                 (converter.decide("playsound sound record @s 1 ~-1 ~1 0.5 0.6 0.7"), "playsound sound record @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 (converter.decide("playsound sound weather @s 1 ~-1 ~1 0.5"), "playsound sound weather @s 1 ~-1 ~1 0.5"),
                 (converter.decide("playsound sound weather @s 1 ~-1 ~1 0.5 0.6"), "playsound sound weather @s 1 ~-1 ~1 0.5 0.6"),
                 (converter.decide("playsound sound weather @s 1 ~-1 ~1 0.5 0.6 0.7"), "playsound sound weather @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 (converter.decide("playsound sound block @s 1 ~-1 ~1 0.5"), "playsound sound block @s 1 ~-1 ~1 0.5"),
                 (converter.decide("playsound sound block @s 1 ~-1 ~1 0.5 0.6"), "playsound sound block @s 1 ~-1 ~1 0.5 0.6"),
                 (converter.decide("playsound sound block @s 1 ~-1 ~1 0.5 0.6 0.7"), "playsound sound block @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 (converter.decide("playsound sound hostile @s 1 ~-1 ~1 0.5"), "playsound sound hostile @s 1 ~-1 ~1 0.5"),
                 (converter.decide("playsound sound hostile @s 1 ~-1 ~1 0.5 0.6"), "playsound sound hostile @s 1 ~-1 ~1 0.5 0.6"),
                 (converter.decide("playsound sound hostile @s 1 ~-1 ~1 0.5 0.6 0.7"), "playsound sound hostile @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 (converter.decide("playsound sound neutral @s 1 ~-1 ~1 0.5"), "playsound sound neutral @s 1 ~-1 ~1 0.5"),
                 (converter.decide("playsound sound neutral @s 1 ~-1 ~1 0.5 0.6"), "playsound sound neutral @s 1 ~-1 ~1 0.5 0.6"),
                 (converter.decide("playsound sound neutral @s 1 ~-1 ~1 0.5 0.6 0.7"), "playsound sound neutral @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 (converter.decide("playsound sound player @s 1 ~-1 ~1 0.5"), "playsound sound player @s 1 ~-1 ~1 0.5"),
                 (converter.decide("playsound sound player @s 1 ~-1 ~1 0.5 0.6"), "playsound sound player @s 1 ~-1 ~1 0.5 0.6"),
                 (converter.decide("playsound sound player @s 1 ~-1 ~1 0.5 0.6 0.7"), "playsound sound player @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 (converter.decide("playsound sound ambient @s 1 ~-1 ~1 0.5"), "playsound sound ambient @s 1 ~-1 ~1 0.5"),
                 (converter.decide("playsound sound ambient @s 1 ~-1 ~1 0.5 0.6"), "playsound sound ambient @s 1 ~-1 ~1 0.5 0.6"),
                 (converter.decide("playsound sound ambient @s 1 ~-1 ~1 0.5 0.6 0.7"), "playsound sound ambient @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 (converter.decide("playsound sound voice @s 1 ~-1 ~1 0.5"), "playsound sound voice @s 1 ~-1 ~1 0.5"),
                 (converter.decide("playsound sound voice @s 1 ~-1 ~1 0.5 0.6"), "playsound sound voice @s 1 ~-1 ~1 0.5 0.6"),
                 (converter.decide("playsound sound voice @s 1 ~-1 ~1 0.5 0.6 0.7"), "playsound sound voice @s 1 ~-1 ~1 0.5 0.6 0.7"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Publish(TestBase):
    def test_syntax1_ok(self):
        perms = ["publish"]
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("aaaaaaa",
                 "publish ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("publish"), "publish"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Recipe(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["recipe", ["give", "take"], "@s", "recipeName"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("recipe",
                 "recipe aaaa @s recipeName",
                 "recipe give",
                 "recipe give @c recipeName",
                 "recipe give @s",
                 "recipe give @s recipeName ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("recipe give @s recipeName"), "recipe give @s recipeName"),
                 (converter.decide("recipe give @s *"), "recipe give @s *"),
                 (converter.decide("recipe take @s recipeName"), "recipe take @s recipeName"),
                 (converter.decide("recipe take @s *"), "recipe take @s *"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Reload(TestBase):
    def test_syntax1_ok(self):
        perms = ["reload"]
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("aaaaaa",
                 "reload ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("reload"), "reload"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class ReplaceItem(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["replaceitem", "block", coord(), coord(), coord(), list(converter.Globals.slots), "stone", "5", "1", "{abc:def}"], optional=3)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("replaceitem",
                 "replaceitem aaaaa 1 ~-1 ~1 slot.armor.chest stone 5 1 {abc:def}",
                 "replaceitem block",
                 "replaceitem block a ~-1 ~1 slot.armor.chest stone 5 1 {abc:def}",
                 "replaceitem block 1",
                 "replaceitem block 1 aaa ~1 slot.armor.chest stone 5 1 {abc:def}",
                 "replaceitem block 1 ~-1",
                 "replaceitem block 1 ~-1 aa slot.armor.chest stone 5 1 {abc:def}",
                 "replaceitem block 1 ~-1 ~1",
                 "replaceitem block 1 ~-1 ~1 aaaaaaaaaaaaaaaa stone 5 1 {abc:def}",
                 "replaceitem block 1 ~-1 ~1 slot.armor.chest",
                 "replaceitem block 1 ~-1 ~1 slot.armor.chest aaaaa 5 1 {abc:def}",
                 "replaceitem block 1 ~-1 ~1 slot.armor.chest stone a 1 {abc:def}",
                 "replaceitem block 1 ~-1 ~1 slot.armor.chest stone 0 1 {abc:def}",
                 "replaceitem block 1 ~-1 ~1 slot.armor.chest stone 65 1 {abc:def}",
                 "replaceitem block 1 ~-1 ~1 slot.armor.chest stone 5 a {abc:def}",
                 "replaceitem block 1 ~-1 ~1 slot.armor.chest stone 5 1 aaaaaaaaa",
                 "replaceitem block 1 ~-1 ~1 slot.armor.chest stone 5 1 {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    @skip("Not implemented")
    def test_syntax1_convert(self):
        tests = ((converter.decide(""), ""), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Save_all(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["save-all", "flush"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("save-all flush ImNotSupposedToBeHere", )
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("save-all"), "save-all"),
                 (converter.decide("save-all flush"), "save-all flush"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Save_off(TestBase):
    def test_syntax1_ok(self):
        perms = ["save-off"]
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("aaaaaaaa",
                 "save-off ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("save-off"), "save-off"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Save_on(TestBase):
    def test_syntax1_ok(self):
        perms = ["save-on"]
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("aaaaaaa",
                 "save-on ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("save-on"), "save-on"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Say(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["say", ["hi", "hi hi"]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("say", )
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("say hi"), "say hi"),
                 (converter.decide("say hi hi"), "say hi hi"),
                 (converter.decide("say hi @e[c=1]"), "say hi @e[limit=1,sort=nearest]"),
                 (converter.decide("say hi @e[k=1]"), "say hi @e[k=1]"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Scoreboard(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["scoreboard", "objectives", "list"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaaaaaaa list",
                 "scoreboard objectives",
                 "scoreboard objectives aaaa",
                 "scoreboard objectives list ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("scoreboard objectives list"), "scoreboard objectives list"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["scoreboard", "objectives", "add", "anObjective", converter.Globals.criteria, ["displayName", "display name"]], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaaaaaaa add anObjective dummy displayName",
                 "scoreboard objectives",
                 "scoreboard objectives aaa anObjective dummy displayName",
                 "scoreboard objectives add",
                 "scoreboard objectives add anObjective",
                 "scoreboard objectives add anObjective aaaaa displayName",
                 "scoreboard objectives add anObjective dummy aaaaabbbbbcccccdddddeeeeefffffggg")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    @skip("Not implemented")
    def test_syntax2_convert(self):
        tests = ((converter.decide(""), ""), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax3_ok(self):
        perms = generate_perms(["scoreboard", "objectives", "remove", "anObjective"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax3_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaaaaaaa remove anObjective",
                 "scoreboard objectives",
                 "scoreboard objectives aaaaaa anObjective",
                 "scoreboard objectives remove",
                 "scoreboard objectives remove anObjective ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = ((converter.decide("scoreboard objectives remove anObjective"), "scoreboard objectives remove anObjective"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    sidebars = ["list", "sidebar", "belowName"] + map(lambda x: "sidebar.team.{}".format(x), converter.Globals.colors)

    def test_syntax4_ok(self):
        perms = generate_perms(["scoreboard", "objectives", "setdisplay", Scoreboard.sidebars, "anObjective"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax4_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaaaaaaa setdisplay list anObjective",
                 "scoreboard objectives",
                 "scoreboard objectives aaaaaaaaaa list anObjective",
                 "scoreboard objectives setdisplay",
                 "scoreboard objectives setdisplay aaaa anObjective",
                 "scoreboard objectives setdisplay list anObjective ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax4_convert(self):
        tests = [(converter.decide("scoreboard objectives setdisplay {}{}".format(bar, option)), "scoreboard objectives setdisplay {}{}".format(bar, option)) for bar in Scoreboard.sidebars for option in ("", " anObjective")]
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax5_ok(self):
        perms = generate_perms(["scoreboard", "players", "list", ["@s", "*"]], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax5_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaaaa list @s",
                 "scoreboard players",
                 "scoreboard players aaaa @s",
                 "scoreboard players list @c",
                 "scoreboard players list @s ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax5_convert(self):
        tests = ((converter.decide("scoreboard players list"), "scoreboard players list"),
                 (converter.decide("scoreboard players list @s"), "scoreboard players list @s"),
                 (converter.decide("scoreboard players list *"), "#~ There is no way to convert \'scoreboard players list *\' because of the \'*\'"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax6_ok(self):
        perms = generate_perms(["scoreboard", "players", ["set", "add", "remove"], ["@s", "*"], "anObjective", "1", "{abc:def}"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax6_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaaaa set @s anObjective 1 {abc:def}",
                 "scoreboard aaaaaaa set * anObjective 1 {abc:def}",
                 "scoreboard players",
                 "scoreboard players aaa @s anObjective 1 {abc:def}",
                 "scoreboard players aaa * anObjective 1 {abc:def}",
                 "scoreboard players set",
                 "scoreboard players set @c anObjective 1 {abc:def}",
                 "scoreboard players set @s",
                 "scoreboard players set @s anObjective",
                 "scoreboard players set * anObjective",
                 "scoreboard players set @s anObjective a {abc:def}",
                 "scoreboard players set * anObjective a {abc:def}",
                 "scoreboard players set @s anObjective 1 aaaaaaaaa",
                 "scoreboard players set * anObjective 1 aaaaaaaaa",
                 "scoreboard players set @s anObjective 1 {abc:def} ImNotSupposedToBeHere",
                 "scoreboard players set * anObjective 1 {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax6_convert(self):
        tests = ((converter.decide("scoreboard players set @s anObjective 1"), "scoreboard players set @s anObjective 1"),
                 (converter.decide("scoreboard players set @s anObjective 1 {abc:def}"), "scoreboard players set @s[nbt={abc:def}] anObjective 1"),
                 (converter.decide("scoreboard players set Carl anObjective 1 {abc:def}"), "scoreboard players set @p[name=Carl,nbt={abc:def}] anObjective 1"),
                 (converter.decide("scoreboard players add @s anObjective 1"), "scoreboard players add @s anObjective 1"),
                 (converter.decide("scoreboard players add @s anObjective 1 {abc:def}"), "scoreboard players add @s[nbt={abc:def}] anObjective 1"),
                 (converter.decide("scoreboard players add Carl anObjective 1 {abc:def}"), "scoreboard players add @p[name=Carl,nbt={abc:def}] anObjective 1"),
                 (converter.decide("scoreboard players remove @s anObjective 1"), "scoreboard players remove @s anObjective 1"),
                 (converter.decide("scoreboard players remove @s anObjective 1 {abc:def}"), "scoreboard players remove @s[nbt={abc:def}] anObjective 1"),
                 (converter.decide("scoreboard players remove Carl anObjective 1 {abc:def}"), "scoreboard players remove @p[name=Carl,nbt={abc:def}] anObjective 1"),

                 (converter.decide("scoreboard players set * anObjective 1"), "scoreboard players set * anObjective 1"),
                 (converter.decide("scoreboard players set * anObjective 1 {abc:def}"), "#~ There is no way to convert \'scoreboard players set * anObjective 1 {abc:def}\' because of the \'*\'"),
                 (converter.decide("scoreboard players add * anObjective 1"), "scoreboard players add * anObjective 1"),
                 (converter.decide("scoreboard players add * anObjective 1 {abc:def}"), "#~ There is no way to convert \'scoreboard players add * anObjective 1 {abc:def}\' because of the \'*\'"),
                 (converter.decide("scoreboard players remove * anObjective 1"), "scoreboard players remove * anObjective 1"),
                 (converter.decide("scoreboard players remove * anObjective 1 {abc:def}"), "#~ There is no way to convert \'scoreboard players remove * anObjective 1 {abc:def}\' because of the \'*\'"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax7_ok(self):
        perms = generate_perms(["scoreboard", "players", "reset", ["@s", "*"], "anObjective"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax7_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaaaa reset @s anObjective",
                 "scoreboard aaaaaaa reset * anObjective",
                 "scoreboard players",
                 "scoreboard players aaaaa @s anObjective",
                 "scoreboard players aaaaa * anObjective",
                 "scoreboard players reset",
                 "scoreboard players reset @c anObjective",
                 "scoreboard players reset @s anObjective ImNotSupposedToBeHere",
                 "scoreboard players reset * anObjective ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax7_convert(self):
        tests = ((converter.decide("scoreboard players reset @s"), "scoreboard players reset @s"),
                 (converter.decide("scoreboard players reset @s anObjective"), "scoreboard players reset @s anObjective"),
                 (converter.decide("scoreboard players reset *"), "scoreboard players reset *"),
                 (converter.decide("scoreboard players reset * anObjective"), "scoreboard players reset * anObjective"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax8_ok(self):
        perms = generate_perms(["scoreboard", "players", "enable", ["@s", "*"], "anObjective"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax8_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaaaa enable @s anObjective",
                 "scoreboard aaaaaaa enable * anObjective",
                 "scoreboard players",
                 "scoreboard players aaaaaa @s anObjective",
                 "scoreboard players aaaaaa * anObjective",
                 "scoreboard players enable",
                 "scoreboard players enable @c anObjective",
                 "scoreboard players enable @s",
                 "scoreboard players enable @s anObjective ImNotSupposedToBeHere",
                 "scoreboard players enable * anObjective ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax8_convert(self):
        tests = ((converter.decide("scoreboard players enable @s anObjective"), "scoreboard players enable @s anObjective"),
                 (converter.decide("scoreboard players enable * anObjective"), "scoreboard players enable * anObjective"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax9_ok(self):
        perms = generate_perms(["scoreboard", "players", "test", ["@s", "*"], "anObjective", ["1", "*"], ["1", "*"]], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax9_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaaaa test @s anObjective 1 2",
                 "scoreboard aaaaaaa test * anObjective 1 2",
                 "scoreboard players",
                 "scoreboard players aaaa @s anObjective 1 2",
                 "scoreboard players aaaa * anObjective 1 2",
                 "scoreboard players test",
                 "scoreboard players test @c anObjective 1 2",
                 "scoreboard players test @s",
                 "scoreboard players test @s anObjective",
                 "scoreboard players test @s anObjective a 2",
                 "scoreboard players test * anObjective a 2",
                 "scoreboard players test @s anObjective 1 a",
                 "scoreboard players test * anObjective 1 a",
                 "scoreboard players test @s anObjective 1 2 ImNotSupposedToBeHere",
                 "scoreboard players test * anObjective 1 2 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax9_convert(self):
        tests = ((converter.decide("scoreboard players test @s anObjective 1"), "execute if score @s anObjective matches 1.."),
                 (converter.decide("scoreboard players test @s anObjective 1 *"), "execute if score @s anObjective matches 1.."),
                 (converter.decide("scoreboard players test @s anObjective 1 2"), "execute if score @s anObjective matches 1..2"),
                 (converter.decide("scoreboard players test @s anObjective * 2"), "execute if score @s anObjective matches ..2"),
                 (converter.decide("scoreboard players test @s anObjective * *"), "execute if score @s anObjective matches -2147483648.."),
                 (converter.decide("scoreboard players test @s anObjective *"), "execute if score @s anObjective matches -2147483648.."),
                 (converter.decide("scoreboard players test * anObjective 1 2"), "#~ There is no way to convert \'scoreboard players test * anObjective 1 2\' because of the \'*\'"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax10_ok(self):
        perms = generate_perms(["scoreboard", "players", "operation", "@s", "anObjective", ["+=", "-=", "*=", "/=", "%=", "=", "<", ">", "><"], "@s", "aObjective"])
        perms.update(generate_perms(["scoreboard", "players", "operation", "*", "anObjective", ["+=", "-=", "*=", "/=", "%=", "=", "<", ">", "><"], "@s", "aObjective"]))
        perms.update(generate_perms(["scoreboard", "players", "operation", "@s", "anObjective", ["+=", "-=", "*=", "/=", "%=", "=", "<", ">", "><"], "*", "aObjective"]))
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax10_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaaaa operation @s anObjective += @s aObjective",
                 "scoreboard aaaaaaa operation * anObjective += @s aObjective",
                 "scoreboard aaaaaaa operation @s anObjective += * aObjective",
                 "scoreboard players",
                 "scoreboard players aaaaaaaaa @s anObjective += @s aObjective",
                 "scoreboard players aaaaaaaaa * anObjective += @s aObjective",
                 "scoreboard players aaaaaaaaa @s anObjective += * aObjective",
                 "scoreboard players operation",
                 "scoreboard players operation @c anObjective += @s aObjective",
                 "scoreboard players operation @c anObjective += * aObjective",
                 "scoreboard players operation @s",
                 "scoreboard players operation @s anObjective",
                 "scoreboard players operation @s anObjective aa @s aObjective",
                 "scoreboard players operation * anObjective aa @s aObjective",
                 "scoreboard players operation @s anObjective aa * aObjective",
                 "scoreboard players operation @s anObjective +=",
                 "scoreboard players operation @s anObjective += @c aObjective",
                 "scoreboard players operation * anObjective += @c aObjective",
                 "scoreboard players operation @s anObjective += @s",
                 "scoreboard players operation @s anObjective += @s aObjective ImNotSupposedToBeHere",
                 "scoreboard players operation * anObjective += @s aObjective ImNotSupposedToBeHere",
                 "scoreboard players operation @s anObjective += * aObjective ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax10_convert(self):
        tests = ((converter.decide("scoreboard players operation @s anObjective += @s aObjective"), "scoreboard players operation @s anObjective += @s aObjective"),
                 (converter.decide("scoreboard players operation * anObjective += @s aObjective"), "#~ There is no way to convert \'scoreboard players operation * anObjective += @s aObjective\' because of the \'*\'"),
                 (converter.decide("scoreboard players operation @s anObjective += * aObjective"), "#~ There is no way to convert \'scoreboard players operation @s anObjective += * aObjective\' because of the \'*\'"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax11_ok(self):
        perms = generate_perms(["scoreboard", "players", "tag", ["@s", "*"], ["add", "remove"], "aTag", "{abc:def}"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax11_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaaaa tag @s add aTag {abc:def}",
                 "scoreboard aaaaaaa tag * add aTag {abc:def}",
                 "scoreboard players",
                 "scoreboard players aaa @s add aTag {abc:def}",
                 "scoreboard players aaa * add aTag {abc:def}",
                 "scoreboard players tag",
                 "scoreboard players tag @c add aTag {abc:def}",
                 "scoreboard players tag @s",
                 "scoreboard players tag @s aaa aTag {abc:def}",
                 "scoreboard players tag * aaa aTag {abc:def}",
                 "scoreboard players tag @s add",
                 "scoreboard players tag @s add aTag aaaaaaaaa",
                 "scoreboard players tag * add aTag aaaaaaaaa",
                 "scoreboard players tag @s add aTag {abc:def} ImNotSupposedToBeHere",
                 "scoreboard players tag * add aTag {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax11_convert(self):
        tests = ((converter.decide("scoreboard players tag @s add aTag"), "tag @s add aTag"),
                 (converter.decide("scoreboard players tag * add aTag"), "#~ There is no way to convert \'scoreboard players tag * add aTag\' because of the \'*\'"),
                 (converter.decide("scoreboard players tag @s add aTag {abc:def}"), "tag @s[nbt={abc:def}] add aTag"),
                 (converter.decide("scoreboard players tag * add aTag {abc:def}"), "#~ There is no way to convert \'scoreboard players tag * add aTag {abc:def}\' because of the \'*\'"),
                 (converter.decide("scoreboard players tag Carl add aTag {abc:def}"), "tag @p[name=Carl,nbt={abc:def}] add aTag"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax12_ok(self):
        perms = generate_perms(["scoreboard", "players", "tag", ["@s", "*"], "list"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax12_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaaaa tag @s list",
                 "scoreboard aaaaaaa tag * list",
                 "scoreboard players",
                 "scoreboard players aaa @s list",
                 "scoreboard players aaa * list",
                 "scoreboard players tag",
                 "scoreboard players tag @c list",
                 "scoreboard players tag @s",
                 "scoreboard players tag @s aaaa",
                 "scoreboard players tag * aaaa",
                 "scoreboard players tag @s list ImNotSupposedToBeHere",
                 "scoreboard players tag * list ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax12_convert(self):
        tests = ((converter.decide("scoreboard players tag @s list"), "tag @s list"),
                 (converter.decide("scoreboard players tag * list"), "#~ There is no way to convert \'scoreboard players tag * list\' because of the \'*\'"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax13_ok(self):
        perms = generate_perms(["scoreboard", "teams", "list", "aName"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax13_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaa list aName",
                 "scoreboard teams",
                 "scoreboard teams aaaa aName",
                 "scoreboard teams list aName ImNotSupposedToBeHere",
                 "scoreboard teams list aName ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax13_convert(self):
        tests = ((converter.decide("scoreboard teams list"), "team list"),
                 (converter.decide("scoreboard teams list aName"), "team list aName"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax14_ok(self):
        perms = generate_perms(["scoreboard", "teams", "add", "aName", ["TeamName", "Team name"]], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax14_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaa add aName TeamName",
                 "scoreboard teams",
                 "scoreboard teams aaa aName TeamName",
                 "scoreboard teams add")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax14_convert(self):
        tests = ((converter.decide("scoreboard teams add aName"), "team add aName"),
                 (converter.decide("scoreboard teams add aName TeamName"), "team add aName TeamName"),
                 (converter.decide("scoreboard teams add aName Team Name"), "team add aName Team Name"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax15_ok(self):
        perms = generate_perms(["scoreboard", "teams", "join", "aName", ["@s", "@s @e"]], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax15_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaa join aName @s",
                 "scoreboard teams",
                 "scoreboard teams aaaa aName @s",
                 "scoreboard teams join",
                 "scoreboard teams join aName @c",
                 "scoreboard teams join aName @s @c",
                 "scoreboard teams join aName @c @s")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax15_convert(self):
        tests = ((converter.decide("scoreboard teams join aName"), "team join aName"),
                 (converter.decide("scoreboard teams join aName @s"), "team join aName @s"),
                 (converter.decide("scoreboard teams join aName @s @e[c=1]"), "team join aName @s @e[limit=1,sort=nearest]"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax16_ok(self):
        perms = generate_perms(["scoreboard", "teams", ["remove", "empty"], "aName"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax16_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaa remove aName",
                 "scoreboard teams",
                 "scoreboard teams aaaaaa aName",
                 "scoreboard teams remove",
                 "scoreboard teams remove aName ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax16_convert(self):
        tests = ((converter.decide("scoreboard teams remove aName"), "team remove aName"),
                 (converter.decide("scoreboard teams empty aName"), "team empty aName"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax17_ok(self):
        perms = generate_perms(["scoreboard", "teams", "option", "aTeam", "color", ["reset"]+list(converter.Globals.colors)])
        perms.update(generate_perms(["scoreboard", "teams", "option", "aTeam", ["friendlyfire", "seeFriendlyInvisibles"], ["true", "false"]]))
        perms.update(generate_perms(["scoreboard", "teams", "option", "aTeam", ["nametagVisibility", "deathMessageVisibility"], ["never", "hideForOtherTeams", "hideForOwnTeam", "always"]]))
        perms.update(generate_perms(["scoreboard", "teams", "option", "aTeam", ["collisionRule"], ["always", "never", "pushOwnTeam", "pushOtherTeams"]]))
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax17_nok(self):
        perms = ("scoreboard",
                 "scoreboard aaaaa option aTeam color reset",
                 "scoreboard teams",
                 "scoreboard teams aaaaaa aTeam color reset",
                 "scoreboard teams option",
                 "scoreboard teams option aTeam",
                 "scoreboard teams option aTeam aaaaa reset",
                 "scoreboard teams option aTeam color",
                 "scoreboard teams option aTeam color aaaaa",
                 "scoreboard teams option aTeam color reset ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax17_convert(self):
        tests = ((converter.decide("scoreboard teams option aTeam color reset"), "team option aTeam color reset"),
                 (converter.decide("scoreboard teams option aTeam color aqua"), "team option aTeam color aqua"),
                 (converter.decide("scoreboard teams option aTeam color black"), "team option aTeam color black"),
                 (converter.decide("scoreboard teams option aTeam color blue"), "team option aTeam color blue"),
                 (converter.decide("scoreboard teams option aTeam color dark_aqua"), "team option aTeam color dark_aqua"),
                 (converter.decide("scoreboard teams option aTeam color dark_blue"), "team option aTeam color dark_blue"),
                 (converter.decide("scoreboard teams option aTeam color dark_gray"), "team option aTeam color dark_gray"),
                 (converter.decide("scoreboard teams option aTeam color dark_green"), "team option aTeam color dark_green"),
                 (converter.decide("scoreboard teams option aTeam color dark_purple"), "team option aTeam color dark_purple"),
                 (converter.decide("scoreboard teams option aTeam color dark_red"), "team option aTeam color dark_red"),
                 (converter.decide("scoreboard teams option aTeam color gold"), "team option aTeam color gold"),
                 (converter.decide("scoreboard teams option aTeam color gray"), "team option aTeam color gray"),
                 (converter.decide("scoreboard teams option aTeam color green"), "team option aTeam color green"),
                 (converter.decide("scoreboard teams option aTeam color light_purple"), "team option aTeam color light_purple"),
                 (converter.decide("scoreboard teams option aTeam color red"), "team option aTeam color red"),
                 (converter.decide("scoreboard teams option aTeam color white"), "team option aTeam color white"),
                 (converter.decide("scoreboard teams option aTeam color yellow"), "team option aTeam color yellow"),
                 (converter.decide("scoreboard teams option aTeam friendlyfire true"), "team option aTeam friendlyfire true"),
                 (converter.decide("scoreboard teams option aTeam friendlyfire false"), "team option aTeam friendlyfire false"),
                 (converter.decide("scoreboard teams option aTeam seeFriendlyInvisibles true"), "team option aTeam seeFriendlyInvisibles true"),
                 (converter.decide("scoreboard teams option aTeam seeFriendlyInvisibles false"), "team option aTeam seeFriendlyInvisibles false"),
                 (converter.decide("scoreboard teams option aTeam nametagVisibility never"), "team option aTeam nametagVisibility never"),
                 (converter.decide("scoreboard teams option aTeam nametagVisibility hideForOtherTeams"), "team option aTeam nametagVisibility hideForOtherTeams"),
                 (converter.decide("scoreboard teams option aTeam nametagVisibility hideForOwnTeam"), "team option aTeam nametagVisibility hideForOwnTeam"),
                 (converter.decide("scoreboard teams option aTeam nametagVisibility always"), "team option aTeam nametagVisibility always"),
                 (converter.decide("scoreboard teams option aTeam deathMessageVisibility never"), "team option aTeam deathMessageVisibility never"),
                 (converter.decide("scoreboard teams option aTeam deathMessageVisibility hideForOtherTeams"), "team option aTeam deathMessageVisibility hideForOtherTeams"),
                 (converter.decide("scoreboard teams option aTeam deathMessageVisibility hideForOwnTeam"), "team option aTeam deathMessageVisibility hideForOwnTeam"),
                 (converter.decide("scoreboard teams option aTeam deathMessageVisibility always"), "team option aTeam deathMessageVisibility always"),
                 (converter.decide("scoreboard teams option aTeam collisionRule always"), "team option aTeam collisionRule always"),
                 (converter.decide("scoreboard teams option aTeam collisionRule never"), "team option aTeam collisionRule never"),
                 (converter.decide("scoreboard teams option aTeam collisionRule pushOwnTeam"), "team option aTeam collisionRule pushOwnTeam"),
                 (converter.decide("scoreboard teams option aTeam collisionRule pushOtherTeams"), "team option aTeam collisionRule pushOtherTeams"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Seed(TestBase):
    def test_syntax1_ok(self):
        perms = ["seed"]
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("aaaa",
                 "seed ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("seed"), "seed"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class SetBlock(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["setblock", coord(), coord(), coord(), "stone", "1", ["destroy", "keep", "replace"], nbt()], optional=3)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("setblock",
                 "setblock a ~-1 ~1 stone 1 replace {abc:def}",
                 "setblock 1",
                 "setblock 1 aaa ~1 stone 1 replace {abc:def}",
                 "setblock 1 ~-1",
                 "setblock 1 ~-1 aa stone 1 replace {abc:def}",
                 "setblock 1 ~-1 ~1",
                 "setblock 1 ~-1 ~1 aaaaa 1 replace {abc:def}",
                 "setblock 1 ~-1 ~1 stone a replace {abc:def}",
                 "setblock 1 ~-1 ~1 stone -1 replace {abc:def}",
                 "setblock 1 ~-1 ~1 stone 16 replace {abc:def}",
                 "setblock 1 ~-1 ~1 stone * replace {abc:def}",
                 "setblock 1 ~-1 ~1 stone 1 aaaaaaa {abc:def}",
                 "setblock 1 ~-1 ~1 stone 1 replace aaaaaaaaa",
                 "setblock 1 ~-1 ~1 stone 1 replace {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("setblock 1 ~-1 ~1 stone"), "setblock 1 ~-1 ~1 stone"),
                 (converter.decide("setblock 1 ~-1 ~1 stone 1"), "setblock 1 ~-1 ~1 granite"),
                 (converter.decide("setblock 1 ~-1 ~1 stone 1 destroy"), "setblock 1 ~-1 ~1 granite destroy"),
                 (converter.decide("setblock 1 ~-1 ~1 stone 1 destroy {abc:def}"), "setblock 1 ~-1 ~1 granite{abc:def} destroy"),
                 (converter.decide("setblock 1 ~-1 ~1 stone 1 keep"), "setblock 1 ~-1 ~1 granite keep"),
                 (converter.decide("setblock 1 ~-1 ~1 stone 1 keep {abc:def}"), "setblock 1 ~-1 ~1 granite{abc:def} keep"),
                 (converter.decide("setblock 1 ~-1 ~1 stone 1 replace"), "setblock 1 ~-1 ~1 granite"),
                 (converter.decide("setblock 1 ~-1 ~1 stone 1 replace {abc:def}"), "setblock 1 ~-1 ~1 granite{abc:def}"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class SetIdleTimeout(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["setidletimeout", "10"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("setidletimeout",
                 "setidletimeout -1",
                 "setidletimeout aa",
                 "setidletimeout 10 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("setidletimeout 10"), "setidletimeout 10"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class SetWorldSpawn(TestBase):
    def test_syntax1_ok(self):
        perms = ["setworldspawn"]
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("aaaaaaaaaaaaa",
                 "setworldspawn ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("setworldspawn"), "setworldspawn"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["setworldspawn", "1", "~-1", "1"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("setworldspawn a ~-1 1",
                 "setworldspawn 1",
                 "setworldspawn 1 aaa 1",
                 "setworldspawn 1 ~-1",
                 "setworldspawn 1 ~-1 a",
                 "setworldspawn 1 ~-1 1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("setworldspawn 1 ~-1 1"), "setworldspawn 1 ~-1 1"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class SpawnPoint(TestBase):
    def test_syntax1_ok(self):
        perms = ["spawnpoint"]
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("aaaaaaaaaa", )
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("spawnpoint"), "spawnpoint"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["spawnpoint", "@s"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("spawnpoint @c",
                 "spawnpoint @s ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("spawnpoint @s"), "spawnpoint @s"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax3_ok(self):
        perms = generate_perms(["spawnpoint", "@s", coord(), coord(), coord()])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax3_nok(self):
        perms = ("spawnpoint @s 1",
                 "spawnpoint @s a ~-1 1",
                 "spawnpoint @s 1 ~-1",
                 "spawnpoint @s 1 aaa 1",
                 "spawnpoint @s 1 ~-1 a",
                 "spawnpoint @s 1 ~-1 1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = ((converter.decide("spawnpoint @s 1 ~-1 1"), "spawnpoint @s 1 ~-1 1"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class SpreadPlayers(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["spreadplayers", coord(), coord(), "1", "2", "true", "@s", "Carl"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("spreadplayers",
                 "spreadplayers a ~1 1 2 true @s Carl",
                 "spreadplayers 1",
                 "spreadplayers 1 aa 1 2 true @s Carl",
                 "spreadplayers 1 ~1",
                 "spreadplayers 1 ~1 a 2 true @s Carl",
                 "spreadplayers 1 ~1 -0.1 2 true @s Carl",
                 "spreadplayers 1 ~1 1",
                 "spreadplayers 1 ~1 1 a true @s Carl",
                 "spreadplayers 1 ~1 1 1 true @s Carl",
                 "spreadplayers 1 ~1 1 1.9 true @s Carl",
                 "spreadplayers 1 ~1 1 2",
                 "spreadplayers 1 ~1 1 2 aaaa @s Carl",
                 "spreadplayers 1 ~1 1 2 true",
                 "spreadplayers 1 ~1 1 2 true @c Carl",
                 "spreadplayers 1 ~1 1 2 true @s @c")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("spreadplayers 1 ~1 1 2 true @s"), "spreadplayers 1 ~1 1 2 true @s"),
                 (converter.decide("spreadplayers 1 ~1 1 2 true @s Carl"), "spreadplayers 1 ~1 1 2 true @s Carl"),
                 (converter.decide("spreadplayers 1 ~1 1 2 true @e[c=1] Carl"), "spreadplayers 1 ~1 1 2 true @e[limit=1,sort=nearest] Carl"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Stats(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["stats", "block", coord(), coord(), coord(), "clear", list(converter.Globals.statTags)])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("stats",
                 "stats aaaaa 1 ~-1 ~1 clear QueryResult",
                 "stats block",
                 "stats block a ~-1 ~1 clear QueryResult",
                 "stats block 1",
                 "stats block 1 aaa ~1 clear QueryResult",
                 "stats block 1 ~-1",
                 "stats block 1 ~-1 aa clear QueryResult",
                 "stats block 1 ~-1 ~1",
                 "stats block 1 ~-1 ~1 aaaaa QueryResult",
                 "stats block 1 ~-1 ~1 clear",
                 "stats block 1 ~-1 ~1 clear aaaaaaaaaaa",
                 "stats block 1 ~-1 ~1 clear QueryResult ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("stats block 1 ~-1 ~1 clear AffectedBlocks"), "#~ stats block 1 ~-1 ~1 clear AffectedBlocks ||| Clearing a stat is no longer needed"),
                 (converter.decide("stats block 1 ~-1 ~1 clear AffectedEntities"), "#~ stats block 1 ~-1 ~1 clear AffectedEntities ||| Clearing a stat is no longer needed"),
                 (converter.decide("stats block 1 ~-1 ~1 clear AffectedItems"), "#~ stats block 1 ~-1 ~1 clear AffectedItems ||| Clearing a stat is no longer needed"),
                 (converter.decide("stats block 1 ~-1 ~1 clear QueryResult"), "#~ stats block 1 ~-1 ~1 clear QueryResult ||| Clearing a stat is no longer needed"),
                 (converter.decide("stats block 1 ~-1 ~1 clear SuccessCount"), "#~ stats block 1 ~-1 ~1 clear SuccessCount ||| Clearing a stat is no longer needed"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["stats", "block", coord(), coord(), coord(), "set", list(converter.Globals.statTags), "@s", "anObjective"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("stats",
                 "stats aaaaa 1 ~-1 ~1 set QueryResult @s anObjective",
                 "stats block",
                 "stats block a ~-1 ~1 set QueryResult @s anObjective",
                 "stats block 1",
                 "stats block 1 aaa ~1 set QueryResult @s anObjective",
                 "stats block 1 ~-1",
                 "stats block 1 ~-1 aa set QueryResult @s anObjective",
                 "stats block 1 ~-1 ~1",
                 "stats block 1 ~-1 ~1 aaa QueryResult @s anObjective",
                 "stats block 1 ~-1 ~1 set",
                 "stats block 1 ~-1 ~1 set aaaaaaaaaaa @s anObjective",
                 "stats block 1 ~-1 ~1 set QueryResult",
                 "stats block 1 ~-1 ~1 set QueryResult @c anObjective",
                 "stats block 1 ~-1 ~1 set QueryResult @s",
                 "stats block 1 ~-1 ~1 set QueryResult @s anObjective ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("stats block 1 ~-1 ~1 set AffectedBlocks @s anObjective"),
                                   "#~ stats block 1 ~-1 ~1 set AffectedBlocks @s anObjective ||| Use \'execute store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 (converter.decide("stats block 1 ~-1 ~1 set AffectedEntities @s anObjective"),
                                   "#~ stats block 1 ~-1 ~1 set AffectedEntities @s anObjective ||| Use \'execute store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 (converter.decide("stats block 1 ~-1 ~1 set AffectedItems @s anObjective"),
                                   "#~ stats block 1 ~-1 ~1 set AffectedItems @s anObjective ||| Use \'execute store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 (converter.decide("stats block 1 ~-1 ~1 set QueryResult @s anObjective"),
                                   "#~ stats block 1 ~-1 ~1 set QueryResult @s anObjective ||| Use \'execute store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 (converter.decide("stats block 1 ~-1 ~1 set SuccessCount @s anObjective"),
                                   "#~ stats block 1 ~-1 ~1 set SuccessCount @s anObjective ||| Use \'execute store success score @s anObjective run COMMAND\' on the commands that you want the stats from"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax3_ok(self):
        perms = generate_perms(["stats", "entity", "@s", "clear", list(converter.Globals.statTags)])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax3_nok(self):
        perms = ("stats",
                 "stats aaaaaa @s clear QueryResult",
                 "stats entity",
                 "stats entity @c clear QueryResult",
                 "stats entity @s",
                 "stats entity @s aaaaa QueryResult",
                 "stats entity @s clear",
                 "stats entity @s clear aaaaaaaaaaa",
                 "stats entity @s clear QueryResult ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = ((converter.decide("stats entity @s clear AffectedBlocks"), "#~ stats entity @s clear AffectedBlocks ||| Clearing a stat is no longer needed"),
                 (converter.decide("stats entity @s clear AffectedEntities"), "#~ stats entity @s clear AffectedEntities ||| Clearing a stat is no longer needed"),
                 (converter.decide("stats entity @s clear AffectedItems"), "#~ stats entity @s clear AffectedItems ||| Clearing a stat is no longer needed"),
                 (converter.decide("stats entity @s clear QueryResult"), "#~ stats entity @s clear QueryResult ||| Clearing a stat is no longer needed"),
                 (converter.decide("stats entity @s clear SuccessCount"), "#~ stats entity @s clear SuccessCount ||| Clearing a stat is no longer needed"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax4_ok(self):
        perms = generate_perms(["stats", "entity", "@s", "set", list(converter.Globals.statTags), "@s", "anObjective"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax4_nok(self):
        perms = ("stats",
                 "stats aaaaaa @s set QueryResult @s anObjective",
                 "stats entity",
                 "stats entity @c set QueryResult @s anObjective",
                 "stats entity @s",
                 "stats entity @s aaa QueryResult @s anObjective",
                 "stats entity @s set",
                 "stats entity @s set aaaaaaaaaaa @s anObjective",
                 "stats entity @s set QueryResult",
                 "stats entity @s set QueryResult @c anObjective",
                 "stats entity @s set QueryResult @s",
                 "stats entity @s set QueryResult @s anObjective ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax4_convert(self):
        tests = ((converter.decide("stats entity @s set AffectedBlocks @s anObjective"),
                                   "#~ stats entity @s set AffectedBlocks @s anObjective ||| Use \'execute as @s at @s store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 (converter.decide("stats entity @s set AffectedEntities @s anObjective"),
                                   "#~ stats entity @s set AffectedEntities @s anObjective ||| Use \'execute as @s at @s store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 (converter.decide("stats entity @s set AffectedItems @s anObjective"),
                                   "#~ stats entity @s set AffectedItems @s anObjective ||| Use \'execute as @s at @s store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 (converter.decide("stats entity @s set QueryResult @s anObjective"),
                                   "#~ stats entity @s set QueryResult @s anObjective ||| Use \'execute as @s at @s store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 (converter.decide("stats entity @s set SuccessCount @s anObjective"),
                                   "#~ stats entity @s set SuccessCount @s anObjective ||| Use \'execute as @s at @s store success score @s anObjective run COMMAND\' on the commands that you want the stats from"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Stop(TestBase):
    def test_syntax1_ok(self):
        perms = ["stop"]
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("aaaa",
                 "stop ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("stop"), "stop"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Stopsound(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["stopsound", "@s", ["master", "music", "record", "weather", "block", "hostile", "neutral", "player", "ambient", "voice"], "aSound"], optional=2)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("stopsound",
                 "stopsound @c master aSound",
                 "stopsound @s aaaaaa aSound",
                 "stopsound @s master aSound ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("stopsound @s master aSound"), "stopsound @s master aSound"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Summon(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["summon", list(converter.Globals.summons)])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("summon",
                 "summon aaa",
                 "summon cow ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("summon cow"), "summon cow"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["summon", list(converter.Globals.summons), coord(), coord(), coord(), nbt()], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("summon",
                 "summon aaa 1 ~-1 ~1 {abc:def}",
                 "summon cow a ~-1 ~1 {abc:def}",
                 "summon cow 1",
                 "summon cow 1 aaa ~1 {abc:def}",
                 "summon cow 1 ~-1",
                 "summon cow 1 ~-1 a {abc:def}",
                 "summon cow 1 ~-1 ~1 aaaaaaaaa",
                 "summon cow 1 ~-1 ~1 {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("summon cow 1 ~-1 ~1"), "summon cow 1 ~-1 ~1"),
                 (converter.decide("summon cow 1 ~-1 ~1 {abc:def}"), "summon cow 1 ~-1 ~1 {abc:def}"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Teleport(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["teleport", "@s", coord(), coord(), coord()])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("teleport",
                 "teleport @c 1 ~-1 ~1",
                 "teleport @s",
                 "teleport @s a ~-1 ~1",
                 "teleport @s 1",
                 "teleport @s 1 aaa ~1",
                 "teleport @s 1 ~-1",
                 "teleport @s 1 ~-1 a",
                 "teleport @s 1 ~-1 ~1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("teleport @s 1 ~-1 ~1"), "teleport 1 ~-1 ~1"),
                 (converter.decide("teleport @e 1 ~-1 ~1"), "teleport @e 1 ~-1 ~1"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["teleport", "@s", coord(), coord(), coord(), coord(), coord()])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("teleport",
                 "teleport @c 1 ~-1 ~1 ~30 ~-60",
                 "teleport @s",
                 "teleport @s a ~-1 ~1 ~30 ~-60",
                 "teleport @s 1",
                 "teleport @s a ~-1 ~1 ~30 ~-60",
                 "teleport @s 1 ~-1",
                 "teleport @s 1 aaa ~1 ~30 ~-60",
                 "teleport @s 1 ~-1 aa ~30 ~-60",
                 "teleport @s 1 ~-1 ~1 aaa ~-60",
                 "teleport @s 1 ~-1 ~1 ~30",
                 "teleport @s 1 ~-1 ~1 ~30 aaaa",
                 "teleport @s 1 ~-1 ~1 ~30 ~-60 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("teleport @s 1 ~-1 ~1 ~30 ~-60"), "teleport 1 ~-1 ~1 ~30 ~-60"),
                 (converter.decide("teleport @e 1 ~-1 ~1 ~30 ~-60"), "teleport @e 1 ~-1 ~1 ~30 ~-60"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Tp(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["tp", coord(), coord(), coord()])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("tp",
                 "tp a ~-1 ~1",
                 "tp 1 aaa ~1",
                 "tp 1 ~-1 aa",
                 "tp 1 ~-1 ~1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("tp 1 ~-1 ~1"), "teleport 1 ~-1 ~1"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["tp", coord(), coord(), coord(), coord(), coord()])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("tp",
                 "tp a ~-1 ~1 ~30 ~-60",
                 "tp 1 aaa ~1 ~30 ~-60",
                 "tp 1 ~-1 aa ~30 ~-60",
                 "tp 1 ~-1 ~1 aaa ~-60",
                 "tp 1 ~-1 ~1 ~30 aaaa",
                 "tp 1 ~-1 ~1 ~30 ~-60 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("tp 1 ~-1 ~1 ~30 ~-60"), "teleport 1 ~-1 ~1 ~30 ~-60"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax3_ok(self):
        perms = generate_perms(["tp", "@e", ["@s", "@e[c=1]"]], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax3_nok(self):
        perms = ("tp",
                 "tp @c @s",
                 "tp @e @c",
                 "tp @s @e",
                 "tp @s @a",
                 "tp @e @s ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = ((converter.decide("tp @s"), "teleport @s"),
                 (converter.decide("tp @s @e[c=1]"), "teleport @e[limit=1,sort=nearest]"),
                 (converter.decide("tp @e @e[c=1]"), "teleport @e @e[limit=1,sort=nearest]"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax4_ok(self):
        perms = generate_perms(["tp", "@e", coord(), coord(), coord()])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax4_nok(self):
        perms = ("tp",
                 "tp @c 1 ~-1 ~1",
                 "tp @e a ~-1 ~1",
                 "tp @e 1 aaa ~1",
                 "tp @e 1 ~-1",
                 "tp @e 1 ~-1 aa",
                 "tp @e 1 ~-1 ~1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax4_convert(self):
        tests = ((converter.decide("tp @s 1 ~-1 ~1"), "teleport 1 ~-1 ~1"),
                 (converter.decide("tp @e 1 2 3"), "execute as @e teleport 1 2 3"),
                 (converter.decide("tp @e 1 ~-1 ~1"), "execute as @e at @s teleport 1 ~-1 ~1"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax5_ok(self):
        perms = generate_perms(["tp", "@e", coord(), coord(), coord(), coord(), coord()])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax5_nok(self):
        perms = ("tp",
                 "tp @c 1 ~-1 ~1 ~30 ~-60",
                 "tp @e a ~-1 ~1 ~30 ~-60",
                 "tp @e 1 aaa ~1 ~30 ~-60",
                 "tp @e 1 ~-1",
                 "tp @e 1 ~-1 aa ~30 ~-60",
                 "tp @e 1 ~-1 ~1 aaa ~-60",
                 "tp @e 1 ~-1 ~1 ~30",
                 "tp @e 1 ~-1 ~1 ~30 aaaa",
                 "tp @e 1 ~-1 ~1 ~30 ~-60 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax5_convert(self):
        tests = ((converter.decide("tp @s 1 ~-1 ~1 ~30 ~-60"), "teleport 1 ~-1 ~1 ~30 ~-60"),
                 (converter.decide("tp @e 1 2 3 30 -60"), "execute as @e teleport 1 2 3 30 -60"),
                 (converter.decide("tp @e 1 ~-1 ~1 ~30 ~-60"), "execute as @e at @s teleport 1 ~-1 ~1 ~30 ~-60"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Tellraw(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["tellraw", "@s", "{\"text\":\"hi\"}"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("tellraw",
                 "tellraw @c {\"text\":\"hi\"}",
                 "tellraw @s",
                 "tellraw @s aaaaaaaaaaaaaaaaa",
                 "tellraw @s {\"text\":\"hi\"} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("tellraw @s {\"text\":\"hi\"}"), "tellraw @s {\"text\":\"hi\"}"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Testfor(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["testfor", "@s", "{abc:def}"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("testfor",
                 "testfor @c {abc:def}",
                 "testfor @s aaaaaaaaa",
                 "testfor @s {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("testfor @s"), "execute if entity @s"),
                 (converter.decide("testfor @s {abc:def}"), "execute if entity @s[nbt={abc:def}]"),
                 (converter.decide("testfor Carl"), "execute if entity Carl"),
                 (converter.decide("testfor Carl {abc:def}"), "execute if entity @p[name=Carl,nbt={abc:def}]"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class TestforBlock(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["testforblock", coord(), coord(), coord(), "stone", "1", "{abc:def}"], optional=2)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("testforblock",
                 "testforblock a ~-1 1 stone 1 {abc:def}",
                 "testforblock 1",
                 "testforblock 1 aaa 1 stone 1 {abc:def}",
                 "testforblock 1 ~-1",
                 "testforblock 1 ~-1 a stone 1 {abc:def}",
                 "testforblock 1 ~-1 1",
                 "testforblock 1 ~-1 1 aaaaa 1 {abc:def}",
                 "testforblock 1 ~-1 1 stone a {abc:def}",
                 "testforblock 1 ~-1 1 stone 1 aaaaaaaaa",
                 "testforblock 1 ~-1 1 stone 1 {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("testforblock 1 ~-1 1 stone"), "execute if block 1 ~-1 1 stone"),
                 (converter.decide("testforblock 1 ~-1 1 stone 1"), "execute if block 1 ~-1 1 granite"),
                 (converter.decide("testforblock 1 ~-1 1 stone 1 {abc:def}"), "execute if block 1 ~-1 1 granite{abc:def}"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class TestforBlocks(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["testforblocks", coord(), coord(), coord(), coord(), coord(), coord(), coord(), coord(), coord(), ["all", "masked"]], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("testforblocks",
                 "testforblocks a ~-1 1 1 ~-1 1 1 ~-1 1 all",
                 "testforblocks 1",
                 "testforblocks 1 aaa 1 1 ~-1 1 1 ~-1 1 all",
                 "testforblocks 1 ~-1",
                 "testforblocks 1 ~-1 a 1 ~-1 1 1 ~-1 1 all",
                 "testforblocks 1 ~-1 1",
                 "testforblocks 1 ~-1 1 a ~-1 1 1 ~-1 1 all",
                 "testforblocks 1 ~-1 1 1",
                 "testforblocks 1 ~-1 1 1 aaa 1 1 ~-1 1 all",
                 "testforblocks 1 ~-1 1 1 ~-1",
                 "testforblocks 1 ~-1 1 1 ~-1 a 1 ~-1 1 all",
                 "testforblocks 1 ~-1 1 1 ~-1 1",
                 "testforblocks 1 ~-1 1 1 ~-1 1 a ~-1 1 all",
                 "testforblocks 1 ~-1 1 1 ~-1 1 1",
                 "testforblocks 1 ~-1 1 1 ~-1 1 1 aaa 1 all",
                 "testforblocks 1 ~-1 1 1 ~-1 1 1 ~-1",
                 "testforblocks 1 ~-1 1 1 ~-1 1 1 ~-1 a all",
                 "testforblocks 1 ~-1 1 1 ~-1 1 1 ~-1 1 aaa",
                 "testforblocks 1 ~-1 1 1 ~-1 1 1 ~-1 1 all ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("testforblocks 1 ~-1 1 1 ~-1 1 1 ~-1 1"), "execute if blocks 1 ~-1 1 1 ~-1 1 1 ~-1 1 all"),
                 (converter.decide("testforblocks 1 ~-1 1 1 ~-1 1 1 ~-1 1 all"), "execute if blocks 1 ~-1 1 1 ~-1 1 1 ~-1 1 all"),
                 (converter.decide("testforblocks 1 ~-1 1 1 ~-1 1 1 ~-1 1 masked"), "execute if blocks 1 ~-1 1 1 ~-1 1 1 ~-1 1 masked"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Time(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["time", ["add", "set"], "42"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("time",
                 "time aaa 42",
                 "time add",
                 "time add aa",
                 "time add 0",
                 "time add 42 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("time add 42"), "time add 42"),
                 (converter.decide("time set 42"), "time set 42"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["time", "set", ["day", "night"]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("time",
                 "time aaa day",
                 "time set",
                 "time set aaa",
                 "time set day ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("time set day"), "time set day"),
                 (converter.decide("time set night"), "time set night"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax3_ok(self):
        perms = generate_perms(["time", "query", ["daytime", "gametime", "day"]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax3_nok(self):
        perms = ("time",
                 "time aaaaa day",
                 "time query",
                 "time query aaa",
                 "time query day ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = ((converter.decide("time query day"), "time query day"),
                 (converter.decide("time query daytime"), "time query daytime"),
                 (converter.decide("time query gametime"), "time query gametime"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Title(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["title", "@s", ["clear", "reset"]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("title",
                 "title @c clear",
                 "title @s",
                 "title @s aaaaa",
                 "title @s clear ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("title @s clear"), "title @s clear"),
                 (converter.decide("title @s reset"), "title @s reset"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["title", "@s", ["title", "subtitle", "actionbar"], "{\"text\":\"hi\"}"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("title",
                 "title @c title {\"text\":\"hi\"}",
                 "title @s",
                 "title @s aaaaa {\"text\":\"hi\"}",
                 "title @s title",
                 "title @s title aaaaaaaaaaaaaaaaa",
                 "title @s title {\"text\":\"hi\"} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("title @s title {\"text\":\"hi\"}"), "title @s title {\"text\":\"hi\"}"),
                 (converter.decide("title @s subtitle {\"text\":\"hi\"}"), "title @s subtitle {\"text\":\"hi\"}"),
                 (converter.decide("title @s actionbar {\"text\":\"hi\"}"), "title @s actionbar {\"text\":\"hi\"}"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax3_ok(self):
        perms = generate_perms(["title", "@s", "times", "1", "2", "3"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax3_nok(self):
        perms = ("title",
                 "title @c times 1 2 3",
                 "title @s",
                 "title @s aaaaa 1 2 3",
                 "title @s times",
                 "title @s times a 2 3",
                 "title @s times 1",
                 "title @s times 1 a 3",
                 "title @s times 1 2",
                 "title @s times 1 2 a",
                 "title @s times 1 2 3 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = ((converter.decide("title @s times 1 2 3"), "title @s times 1 2 3"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class ToggleDownfall(TestBase):
    def test_syntax1_ok(self):
        perms = ["toggledownfall"]
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("aaaaaaaaaaaaaa",
                 "toggledownfall ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("toggledownfall"), "#~ toggledownfall ||| This command was removed"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Trigger(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["trigger", "anObjective", ["add", "set"], "0"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("trigger",
                 "trigger anObjective",
                 "trigger anObjective aaa 0",
                 "trigger anObjective add",
                 "trigger anObjective add a",
                 "trigger anObjective add 0 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("trigger anObjective add 0"), "trigger anObjective add 0"),
                 (converter.decide("trigger anObjective add 1"), "trigger anObjective"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class W(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["w", "@s", ["hi", "hi there!"]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("w",
                 "w @c hi",
                 "w @s",)
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("w @s hi"), "w @s hi"),
                 (converter.decide("msg @s hi"), "w @s hi"),
                 (converter.decide("tell @s hi"), "w @s hi"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Weather(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["weather", ["clear", "rain", "thunder"], "5"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("weather",
                 "weather aaaaa 1",
                 "weather clear 0",
                 "weather clear 1000001",
                 "weather clear 1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("weather clear"), "#~ 'weather clear' no longer has random duration. The duration is now 5 minutes\nweather clear"),
                 (converter.decide("weather rain"), "#~ 'weather rain' no longer has random duration. The duration is now 5 minutes\nweather rain"),
                 (converter.decide("weather thunder"), "#~ 'weather thunder' no longer has random duration. The duration is now 5 minutes\nweather thunder"),
                 (converter.decide("weather clear 1"), "weather clear 1"),
                 (converter.decide("weather rain 1"), "weather rain 1"),
                 (converter.decide("weather thunder 1"), "weather thunder 1"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class WhiteList(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["whitelist", ["add", "remove"], "@s"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("whitelist",
                 "whitelist aaa @s",
                 "whitelist add",
                 "whitelist add @c",
                 "whitelist add @s ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("whitelist add @s"), "whitelist add @s"),
                 (converter.decide("whitelist remove @s"), "whitelist remove @s"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["whitelist", ["on", "off", "list", "reload"]])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("whitelist",
                 "whitelist aa",
                 "whitelist on ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("whitelist on"), "whitelist on"),
                 (converter.decide("whitelist off"), "whitelist off"),
                 (converter.decide("whitelist list"), "whitelist list"),
                 (converter.decide("whitelist reload"), "whitelist reload"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class WorldBorder(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["worldborder", ["add", "set"], "1", "2"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("worldborder",
                 "worldborder aaa 1 2",
                 "worldborder add",
                 "worldborder add a 2",
                 "worldborder set 0 2",
                 "worldborder add 1 a",
                 "worldborder add 1 -1",
                 "worldborder add 1 2 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("weather clear 1"), "weather clear 1"),
                 (converter.decide("weather rain 1"), "weather rain 1"),
                 (converter.decide("weather thunder 1"), "weather thunder 1"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["worldborder", "center", coord(), coord()])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("worldborder",
                 "worldborder aaaaaa 1 ~2",
                 "worldborder center",
                 "worldborder center a ~2",
                 "worldborder center 1",
                 "worldborder center 1 aa",
                 "worldborder center 1 ~2 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = ((converter.decide("worldborder center 1 ~2"), "worldborder center 1 ~2"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax3_ok(self):
        perms = generate_perms(["worldborder", "damage", ["amount", "buffer"], "1"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax3_nok(self):
        perms = ("worldborder",
                 "worldborder aaaaaa amount 1",
                 "worldborder damage",
                 "worldborder damage aaaaaa 1",
                 "worldborder damage amount",
                 "worldborder damage amount a",
                 "worldborder damage amount -1",
                 "worldborder damage amount 1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = ((converter.decide("worldborder damage amount 1"), "worldborder damage amount 1"),
                 (converter.decide("worldborder damage buffer 1"), "worldborder damage buffer 1"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax4_ok(self):
        perms = generate_perms(["worldborder", "warning", ["distance", "time"], "1"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax4_nok(self):
        perms = ("worldborder",
                 "worldborder aaaaaaa distance 1",
                 "worldborder warning",
                 "worldborder warning aaaaaaaa 1",
                 "worldborder warning distance",
                 "worldborder warning distance a",
                 "worldborder warning distance -1",
                 "worldborder warning distance 1 ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax4_convert(self):
        tests = ((converter.decide("worldborder warning distance 1"), "worldborder warning distance 1"),
                 (converter.decide("worldborder warning time 1"), "worldborder warning time 1"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()

    def test_syntax5_ok(self):
        perms = generate_perms(["worldborder", "get"])
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax5_nok(self):
        perms = ("worldborder",
                 "worldborder aaa",
                 "worldborder get ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax5_convert(self):
        tests = ((converter.decide("worldborder get"), "worldborder get"), )
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()


class Xp(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["xp", ["1", "2L", "-2L"], "@s"], optional=1)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("xp",
                 "xp aa @s",
                 "xp 1l @s",
                 "xp -1 @s",
                 "xp 1L @c",
                 "xp 1L @s ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = ((converter.decide("xp 1"), "experience add @s 1"),
                 (converter.decide("xp 1 @p"), "experience add @p 1"),
                 (converter.decide("xp 1L"), "experience add @s 1 levels"),
                 (converter.decide("xp 1L @p"), "experience add @p 1 levels"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.assertStats()
