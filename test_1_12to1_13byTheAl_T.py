from unittest import TestCase
import random
import inspect
converter = __import__("1_12to1_13byTheAl_T")


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
        self.asses = 0
        reload(converter)

    def ass(self):
        stack = inspect.stack()
        print "\t{} assertion{} made in {}".format(self.asses, 's' if self.asses != 1 else '',
                                                   stack[1][0].f_code.co_name)

    def decide(self, raw):
        ret = converter.decide(raw)
        self.asses += 1
        return ret

    def assertRaises(self, excClass, callableObj=None, *args, **kwargs):
        super(TestBase, self).assertRaises(excClass, callableObj)
        self.asses += 1

    def assertEqual(self, first, second, msg=None):
        super(TestBase, self).assertEqual(first, second, msg)
        self.asses += 1


class Advancement(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["advancement", ["grant", "revoke"], "@s", ["only", "until", "from", "through"], "adv_name", ["crit", ""]])
        for perm in perms:
            self.decide(perm)
        self.ass()

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
        self.ass()

    def test_syntax2_ok(self):
        perms = generate_perms(["advancement", ["grant", "revoke"], "@s", "everything"])
        for perm in perms:
            self.decide(perm)
        self.ass()

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
        self.ass()

    def test_syntax3_ok(self):
        perms = generate_perms(["advancement", "test", "@s", "adv_name", ["crit", ""]])
        for perm in perms:
            self.decide(perm)
        self.ass()

    def test_syntax3_nok(self):
        perms = ("advancement",
                 "advancement test",
                 "advancement aaaa @s adv_name crit",
                 "advancement test @s",
                 "advancement test @c adv_name crit",
                 "advancement test @s adv_name crit lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.ass()


class Ban(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["ban", "p_name", ["because", "Because I said so", ""]])
        for perm in perms:
            self.decide(perm)
        self.ass()

    def test_syntax1_nok(self):
        perms = ("ban",)
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.ass()


class Ban_IP(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["ban-ip", "p_name", ["because", "Because I said so", ""]])
        for perm in perms:
            self.decide(perm)
        self.ass()

    def test_syntax1_nok(self):
        perms = ("ban-ip",)
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.ass()


class BlockData(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["blockdata", coord(), coord(), coord(), nbt()])
        for perm in perms:
             self.decide(perm)
        self.ass()

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
        self.ass()


class Clear(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["clear", "@s", "minecraft:stone", "1", "42", nbt()], optional=5)
        for perm in perms:
            self.decide(perm)
        self.ass()

    def test_syntax1_nok(self):
        perms = ("clear @c minecraft:stone 1 42 {abc:def}",
                 "clear @s minecraft:stone a 42 {abc:def}",
                 "clear @s minecraft:stone 1 aa {abc:def}",
                 "clear @s minecraft:stone 1 42 aaaaaaaaa")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.ass()

    def test_syntax1_convert(self):
        tests = ((converter.decide("clear"), "clear"),
                 (converter.decide("clear @s"), "clear @s"),
                 (converter.decide("clear @s minecraft:stone"), "clear @s stone"),
                 (converter.decide("clear @s minecraft:stone 1"), "clear @s stone{Damage:1}"),
                 (converter.decide("clear @s minecraft:stone 1 42"), "clear @s stone{Damage:1} 42"),
                 (converter.decide("clear @s minecraft:stone 1 42 {abc:def}"), "clear @s stone{abc:def,Damage:1} 42"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.ass()


class Clone(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["clone", "1", "~-1", "~1", "1", "~-1", "~1", "1", "~-1", "~1",
                                ["masked", "replace"], ["force", "move", "normal"]], optional=2)
        for perm in perms:
            self.decide(perm)
        self.ass()

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
        self.ass()

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
        self.ass()

    def test_syntax2_ok(self):
        perms = generate_perms(["clone", "1", "~-1", "~1", "1", "~-1", "~1", "1", "~-1", "~1",
                                "filtered", ["force", "move", "normal"], "stone", ["1", ""]])
        for perm in perms:
            self.decide(perm)
        self.ass()

    def test_syntax2_nok(self):
        perms = ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered aaaaa stone 1",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered aaaaa stone a",
                 "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force stone 1 lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.ass()

    def test_syntax2_convert(self):
        tests = ((converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force stone 1"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone[variant=granite] force"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force stone"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone force"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered move stone 1"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone[variant=granite] move"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered move stone"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone move"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered normal stone 1"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone[variant=granite] normal"),
                 (converter.decide("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered normal stone"), "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone normal"))
        for before, after in tests:
            self.assertEqual(unicode(before), after, r"'{}' != '{}'".format(unicode(before), after))
        self.ass()


class Debug(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["debug", ["start", "stop"]])
        for perm in perms:
            self.decide(perm)
        self.ass()

    def test_syntax1_nok(self):
        perms = ("debug",
                 "debug aaaaa",
                 "debug start lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.ass()


class DefaultGameMode(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["defaultgamemode", ["0", "1", "2", "3", "s", "c", "a", "sp", "survival", "creative", "adventure", "spectator"]])
        for perm in perms:
            self.decide(perm)
        self.ass()

    def test_syntax1_nok(self):
        perms = ("defaultgamemode",
                 "defaultgamemode aaa",
                 "defaultgamemode 1 lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.ass()

    def test_syntax2_convert(self):
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
        self.ass()


class Deop(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["deop", "@s"])
        for perm in perms:
            self.decide(perm)
        self.ass()

    def test_syntax1_nok(self):
        perms = ("deop",
                 "deop @c",
                 "deop @s lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.ass()


class Difficulty(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["difficulty", ["0", "1", "2", "3", "p", "e", "n", "h", "peaceful", "easy", "normal", "hard"]])
        for perm in perms:
            self.decide(perm)
        self.ass()

    def test_syntax1_nok(self):
        perms = ("difficulty",
                 "difficulty aaa",
                 "difficulty 1 lolo")
        for perm in perms:
            self.assertRaises(SyntaxError, lambda: self.decide(perm))
        self.ass()

    def test_syntax2_convert(self):
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
        self.ass()
