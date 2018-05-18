from unittest import TestCase
from itertools import permutations, combinations, product
import random, inspect, atexit
converter = __import__("1_12to1_13")

_map = map
if type(u"") is str:
    import importlib, builtins
    reload = importlib.reload
    xrange = range
    raw_input = input
    _map = builtins.map
    map = lambda x, y: list(_map(x, y))
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
        print("\t{} assertion{} made in {}.{}".format(self.assertStat, 's' if self.assertStat != 1 else '', self.__class__.__name__, inspect.stack()[1][0].f_code.co_name))

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

    def assertRaises(self, excClass, callableObj=None, *args, **kwargs):
        try:
            super(TestBase, self).assertRaises(excClass, callableObj, *args)
        except AssertionError:
            raise AssertionError("{}({}) didn't throw {}".format(callableObj.__name__, ", ".join(repr(arg) for arg in args), excClass.__name__))

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
        cases = ("@", "*", "=", "[", "]", "@c", "@a[", "@s]", "@a[c =3]", "@a][", "@a[c=1][", "@s[lm=2,l=1]",
                 "@s[score_a_min=2,score_a=1]", "@s[rm=2,r=1]", "@s[rxm=2,rx=1]", "@s[rym=2,ry=1]", "@s[rxm=-181,rx=-179]", "@s[rym=-181,ry=-179]")

        for case in cases:
            self.assertRaises(SyntaxError, converter.Selector, case)

        argPairs = (("x", "a"), ("y", "a"), ("z", "a"), ("dx", "a"), ("dy", "a"), ("dz", "a"), ("type", "bad"),
                    ("type", "!bad"), ("lm", "a"), ("l", "a"), ("m", "bad"), ("score_won", "a"), ("score_won_min", "a"),
                    ("rm", "a"), ("r", "a"), ("rxm", "a"), ("rx", "a"), ("rym", "a"), ("ry", "a"), ("c", "a"),
                    ("bad", "bad"), ("x", ""), ("y", ""), ("z", ""), ("dx", ""), ("dy", ""), ("dz", ""), ("type", ""),
                    ("type", ""), ("lm", ""), ("l", ""), ("m", ""), ("score_won", ""), ("score_won_min", ""),
                    ("name", ""), ("rm", ""), ("r", ""), ("rxm", ""), ("rx", ""), ("rym", ""), ("ry", ""), ("c", ""))

        for sType in ("p", "e", "a", "r", "s"):
            for n in (1, 2, 3):
                for argPairsPerm in permutations(argPairs, n):
                    self.assertRaises(SyntaxError, converter.Selector, "@{}[{}]".format(sType, ",".join(_map(lambda x: "{}={}".format(x[0], x[1]), argPairsPerm))))
        self.assertStats()

    def test_syntax_convert(self):
        argPairs = [(("x=1", "x=1.5"), ("x=-1", "x=-0.5")),
                    (("y=1", "y=1"), ),
                    (("z=1", "z=1.5"), ("z=-1", "z=-0.5")),
                    (("dx=1", "dx=1"), ),
                    (("dy=1", "dy=1"), ),
                    (("dz=1", "dz=1"), ),
                    (("type=Cow", "type=cow"), ("type=!cow", "type=!cow")),
                    (("lm=1", "level=1.."), ("l=1", "level=..1"), ("lm=0,l=1", "level=0..1"), ("lm=1,l=1", "level=1")),
                    (("m=1", "gamemode=creative"), ("m=!c", "gamemode=!creative")),
                    (("team=red", "team=red"), ("team=!red", "team=!red"), ("team=", "team="), ("team=!", "team=!")),
                    (("score_a=1", "scores={a=..1}"), ("score_a_min=1", "scores={a=1..}"), ("score_a_min=1,score_a=2", "scores={a=1..2}"),
                     ("score_a_min=1,score_a=1", "scores={a=1}"), ("score_a=1,score_b=2", "scores={a=..1,b=..2}"),
                     ("score_a=1,score_b=2,score_c_min=3,score_d=4,score_a_min=0,score_d_min=4", "scores={a=0..1,b=..2,c=3..,d=4}")),
                    (("name=Carl", "name=Carl"), ),
                    (("tag=abc", "tag=abc"), ("tag=!abc", "tag=!abc"), ("tag=", "tag="), ("tag=!", "tag=!")),
                    (("rm=1", "distance=1.."), ("r=1", "distance=..1"), ("rm=0,r=1", "distance=0..1"), ("rm=1,r=1", "distance=1")),
                    (("rxm=1", "x_rotation=1.."), ("rx=1", "x_rotation=..1"), ("rxm=0,rx=1", "x_rotation=0..1"), ("rxm=1,rx=1", "x_rotation=1")),
                    (("rym=1", "y_rotation=1.."), ("ry=1", "y_rotation=..1"), ("rym=0,ry=1", "y_rotation=0..1"), ("rym=1,ry=1", "y_rotation=1")),
                    (("c=1", "limit=1,sort=nearest"), ("c=-1", "limit=1,sort=furthest"))]

        for sType in ("e", "a", "r", "s", "p"):
            if sType == "r":
                argPairs.pop()
                c = [("@{}[c=1]", "@{}"), ("@{}[c=-1]", "@{}"), ("@{}[c=2]", "@{}[limit=2]"), ("@{}[c=-2]", "@{}[limit=2]")]
            elif sType in ("s", "p"):
                c = [("@{}[c=1]", "@{}"), ("@{}[c=-1]", "@{}"), ("@{}[c=2]", "@{}"), ("@{}[c=-2]", "@{}")]
            else:
                c = [("@{}[c=1]", "@{}[limit=1,sort=nearest]"), ("@{}[c=-1]", "@{}[limit=1,sort=furthest]"), ("@{}[c=2]", "@{}[limit=2,sort=nearest]"), ("@{}[c=-2]", "@{}[limit=2,sort=furthest]")]

            tests = [("@{}", "@{}"), ("@{}[]", "@{}"), ("@{}[c=0]", "@{}"),
                     ("@{}[r=-1]", "@{}[distance=..0]"), ("@{}[rm=-1]", "@{}[distance=0..]"), ("@{}[r=-1,rm=-1]", "@{}[distance=0]"),
                     ("@{}[rx=181]", "@{}[x_rotation=..-179]"), ("@{}[rx=-181]", "@{}[x_rotation=..179]"), ("@{}[rxm=181]", "@{}[x_rotation=-179..]"), ("@{}[rxm=-181]", "@{}[x_rotation=179..]"),
                     ("@{}[rx=181,rxm=-179]", "@{}[x_rotation=-179]"),
                     ("@{}[ry=181]", "@{}[y_rotation=..-179]"), ("@{}[ry=-181]", "@{}[y_rotation=..179]"), ("@{}[rym=181]", "@{}[y_rotation=-179..]"), ("@{}[rym=-181]", "@{}[y_rotation=179..]"),
                     ("@{}[ry=181,rym=-179]", "@{}[y_rotation=-179]")] + c
            tests = map(lambda test: (test[0].format(sType), test[1].format(sType)), tests)

            for n in (1, 2, 3):
                for argPairsComb in combinations(argPairs, n):
                    for argPairsProd in product(*argPairsComb):
                        before, after = zip(*argPairsProd)
                        realBefore = []
                        for args in before:
                            realBefore.extend(args.split(","))
                        random.shuffle(realBefore)
                        tests.append(("@{}[{}]".format(sType, ",".join(realBefore)), "@{}[{}]".format(sType, ",".join(after))))

            for before, after in tests:
                self.assertEqual(after, unicode(converter.Selector(before)), "source: \'{}\'".format(before))
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
        self.assertStats()


class Block(TestBase):
    def test_block_set_convert(self):
        tests = ((["minecraft:stone"], "stone"),
                 (["emerald_block", "0"], "emerald_block"),
                 (["stone", "variant=stone,variant=granite"], "granite"),

                 (["slime"], "slime_block"),
                 (["slime", "0"], "slime_block"),
                 (["slime", "default"], "slime_block"),
                 (["slime", "0", "{a:b}"], "slime_block{a:b}"),

                 (["lit_redstone_lamp"], "redstone_lamp[lit=true]"),
                 (["lit_redstone_lamp", "0"], "redstone_lamp[lit=true]"),
                 (["lit_redstone_lamp", "default"], "redstone_lamp[lit=true]"),
                 (["lit_redstone_lamp", "0", "{a:b}"], "redstone_lamp[lit=true]{a:b}"),

                 (["double_plant"], "sunflower"),
                 (["double_plant", "0"], "sunflower[half=lower]"),
                 (["double_plant", "default"], "sunflower"),
                 (["double_plant", "variant=syringa"], "lilac"),
                 (["double_plant", "variant=sunflower"], "sunflower"),
                 (["double_plant", "half=upper"], "sunflower[half=upper]"),
                 (["double_plant", "half=upper,variant=syringa"], "lilac[half=upper]"),

                 (["flower_pot"], "flower_pot"),
                 (["flower_pot", "0"], "flower_pot"),
                 (["flower_pot", "default"], "flower_pot"),
                 (["flower_pot", "contents=oak_sapling"], "potted_oak_sapling"),
                 (["flower_pot", "legacy_data=1"], "potted_poppy"),
                 (["flower_pot", "legacy_data=1,contents=oak_sapling"], "potted_poppy"),

                 (["stone"], "stone"),
                 (["stone", "0"], "stone"),
                 (["stone", "0", "{a:b}"], "stone{a:b}"),
                 (["stone", "1"], "granite"),
                 (["stone", "1", "{a:b}"], "granite{a:b}"),
                 (["stone", "default"], "stone"),
                 (["stone", "variant=stone"], "stone"),
                 (["stone", "variant=stone", "{a:b}"], "stone{a:b}"),
                 (["stone", "variant=granite"], "granite"),
                 (["stone", "variant=granite", "{a:b}"], "granite{a:b}"),

                 (["bed"], "red_bed"),
                 (["bed", "0"], "red_bed[facing=south,part=foot]"),
                 (["bed", "0", "{color:10}"], "purple_bed[facing=south,part=foot]"),
                 (["bed", "0", "{a:b}"], "red_bed[facing=south,part=foot]{a:b}"),
                 (["bed", "0", "{color:10,a:b}"], "purple_bed[facing=south,part=foot]{a:b}"),
                 (["bed", "default"], "red_bed"),
                 (["bed", "default", "{color:10}"], "purple_bed"),
                 (["bed", "default", "{a:b}"], "red_bed{a:b}"),
                 (["bed", "default", "{color:10,a:b}"], "purple_bed{a:b}"),
                 (["bed", "facing=north"], "red_bed[facing=north]"),
                 (["bed", "facing=north", "{color:10}"], "purple_bed[facing=north]"),
                 (["bed", "part=foot,facing=south,occupied=true"], "red_bed[facing=south,occupied=true,part=foot]"),
                 (["bed", "part=foot,facing=south,occupied=true", "{color:10}"], "purple_bed[facing=south,occupied=true,part=foot]"),

                 (["tallgrass"], "dead_bush"),
                 (["tallgrass", "type=tall_grass"], "grass"),
                 (["tallgrass", "type=dead_bush"], "dead_bush"),
                 (["tallgrass", "type=fern"], "fern"),

                 (["skull"], "skeleton_wall_skull"),
                 (["skull", "0"], "skeleton_skull"),
                 (["skull", "0", "{Rot:0}"], "skeleton_skull[rotation=0]"),
                 (["skull", "0", "{Rot:0,SkullType:4}"], "creeper_head[rotation=0]"),
                 (["skull", "2", "{Rot:0,SkullType:4}"], "creeper_wall_head[facing=north]"),
                 (["skull", "default"], "skeleton_wall_skull"),
                 (["skull", "default", "{SkullType:1}"], "wither_skeleton_wall_skull"),
                 (["skull", "default", "{SkullType:1,Rot:2}"], "wither_skeleton_wall_skull"),
                 (["skull", "facing=down"], "skeleton_skull"),
                 (["skull", "facing=down", "{SkullType:1}"], "wither_skeleton_skull"),
                 (["skull", "facing=down", "{SkullType:1,Rot:0}"], "wither_skeleton_skull[rotation=0]"),
                 (["skull", "facing=north"], "skeleton_wall_skull[facing=north]"),
                 (["skull", "facing=north", "{SkullType:1}"], "wither_skeleton_wall_skull[facing=north]"),
                 (["skull", "facing=north", "{SkullType:1,Rot:0}"], "wither_skeleton_wall_skull[facing=north]"),
                 (["skull", "nodrop=true"], "skeleton_wall_skull"),

                 (["double_stone_slab"], "stone_slab[type=double]"),
                 (["double_stone_slab", "0"], "stone_slab[type=double]"),
                 (["double_stone_slab", "8"], "smooth_stone"),
                 (["double_stone_slab", "default"], "stone_slab[type=double]"),
                 (["double_stone_slab", "seamless=true"], "smooth_stone"),
                 (["double_stone_slab", "variant=quartz"], "quartz_slab[type=double]"),
                 (["double_stone_slab", "seamless=true,variant=wood_old"], "petrified_oak_slab[type=double]"),
                 (["double_stone_slab", "seamless=false,variant=wood_old"], "petrified_oak_slab[type=double]"),
                 (["double_stone_slab", "seamless=true,variant=quartz"], "smooth_quartz"),
                 (["double_stone_slab", "seamless=false,variant=quartz"], "quartz_slab[type=double]"))
        for before, after in tests:
            if len(before) == 3:
                before[2] = converter.getCompound(before[2][1:])[0]
            pairs = tuple(zip(("block", "state", "nbt"), before))
            self.assertEqual(after, converter.block(dict(pairs), *tuple(zip(*pairs))[0]), "source: {}".format(before))
        self.assertStats()

    def test_block_set_nok(self):
        perms = (["aaa"],
                 ["bed", "-1"],
                 ["bed", "16"],
                 ["bed", "*"],
                 ["bed", "part="],
                 ["bed", "=foot"],
                 ["bed", "part"],
                 ["bed", "part=footfacing=south"],
                 ["bed", "part==south"],
                 ["bed", "part=foot,,facing=south"],
                 ["bed", "part=foot,"],
                 ["bed", ",facing=south"],
                 ["bed", "="],
                 ["bed", ","],
                 ["bed", ""],
                 ["bed", "a=b"],
                 ["bed", "part=a"],
                 ["bed", "a=foot"],
                 ["bed", "a=a,b=b"])
        for perm in perms:
            if len(perm) == 3:
                perm[2] = converter.getCompound(perm[2][1:])[0]
            pairs = tuple(zip(("block", "state", "nbt"), perm))
            self.assertRaises(SyntaxError, converter.block, dict(pairs), *tuple(zip(*pairs))[0])
        self.assertStats()

    def test_block_test_convert(self):
        tests = ((["minecraft:stone"], {"stone", "granite", "polished_granite", "diorite", "polished_diorite", "andesite", "polished_andesite"}),
                 (["emerald_block", "0"], {"emerald_block"}),
                 (["stone", "variant=stone,variant=granite"], {"granite"}),

                 (["slime"], {"slime_block"}),
                 (["slime", "0"], {"slime_block"}),
                 (["slime", "-1"], {"slime_block"}),
                 (["slime", "default"], {"slime_block"}),
                 (["slime", "0", "{a:b}"], {"slime_block{a:b}"}),

                 (["lit_redstone_lamp"], {"redstone_lamp[lit=true]"}),
                 (["lit_redstone_lamp", "0"], {"redstone_lamp[lit=true]"}),
                 (["lit_redstone_lamp", "-1"], {"redstone_lamp[lit=true]"}),
                 (["lit_redstone_lamp", "default"], {"redstone_lamp[lit=true]"}),
                 (["lit_redstone_lamp", "default", "{a:b}"], {"redstone_lamp[lit=true]{a:b}"}),

                 (["double_plant"], {"sunflower", "lilac", "tall_grass", "large_fern", "rose_bush", "peony"}),
                 (["double_plant", "0"], {"sunflower[half=lower]"}),
                 (["double_plant", "default"], {"sunflower[half=lower]"}),
                 (["double_plant", "variant=syringa"], {"lilac"}),
                 (["double_plant", "variant=sunflower"], {"sunflower"}),
                 (["double_plant", "half=upper"], {"sunflower[half=upper]", "lilac[half=upper]", "tall_grass[half=upper]", "large_fern[half=upper]", "rose_bush[half=upper]", "peony[half=upper]"}),
                 (["double_plant", "half=upper,variant=syringa"], {"lilac[half=upper]"}),

                 (["flower_pot"], {"flower_pot", "potted_oak_sapling", "potted_spruce_sapling", "potted_birch_sapling", "potted_jungle_sapling", "potted_acacia_sapling", "potted_dark_oak_sapling", "potted_fern", "potted_dandelion", "potted_poppy", "potted_blue_orchid", "potted_allium", "potted_azure_bluet", "potted_red_tulip", "potted_orange_tulip", "potted_white_tulip", "potted_pink_tulip", "potted_oxeye_daisy", "potted_red_mushroom", "potted_brown_mushroom", "potted_dead_bush", "potted_cactus"}),
                 (["flower_pot", "0"], {"flower_pot"}),
                 (["flower_pot", "default"], {"flower_pot"}),
                 (["flower_pot", "contents=oak_sapling"], {"potted_oak_sapling"}),
                 (["flower_pot", "legacy_data=1"], {"potted_poppy"}),
                 (["flower_pot", "legacy_data=1,contents=oak_sapling"], {"potted_poppy"}),

                 (["stone"], {"stone", "granite", "polished_granite", "diorite", "polished_diorite", "andesite", "polished_andesite"}),
                 (["stone", "*"], {"stone", "granite", "polished_granite", "diorite", "polished_diorite", "andesite", "polished_andesite"}),
                 (["stone", "-1"], {"stone", "granite", "polished_granite", "diorite", "polished_diorite", "andesite", "polished_andesite"}),
                 (["stone", "0"], {"stone"}),
                 (["stone", "0", "{a:b}"], {"stone{a:b}"}),
                 (["stone", "1"], {"granite"}),
                 (["stone", "1", "{a:b}"], {"granite{a:b}"}),
                 (["stone", "default"], {"stone"}),
                 (["stone", "variant=stone"], {"stone"}),
                 (["stone", "variant=stone", "{a:b}"], {"stone{a:b}"}),
                 (["stone", "variant=granite"], {"granite"}),
                 (["stone", "variant=granite", "{a:b}"], {"granite{a:b}"}),

                 (["bed"], {"white_bed", "orange_bed", "magenta_bed", "light_blue_bed", "yellow_bed", "lime_bed", "pink_bed", "gray_bed", "light_gray_bed", "cyan_bed", "purple_bed", "blue_bed", "brown_bed", "green_bed", "red_bed", "black_bed"}),
                 (["bed", "0"], {"white_bed[facing=south,part=foot]", "orange_bed[facing=south,part=foot]", "magenta_bed[facing=south,part=foot]", "light_blue_bed[facing=south,part=foot]", "yellow_bed[facing=south,part=foot]", "lime_bed[facing=south,part=foot]", "pink_bed[facing=south,part=foot]", "gray_bed[facing=south,part=foot]", "light_gray_bed[facing=south,part=foot]", "cyan_bed[facing=south,part=foot]", "purple_bed[facing=south,part=foot]", "blue_bed[facing=south,part=foot]", "brown_bed[facing=south,part=foot]", "green_bed[facing=south,part=foot]", "red_bed[facing=south,part=foot]", "black_bed[facing=south,part=foot]"}),
                 (["bed", "0", "{color:10}"], {"purple_bed[facing=south,part=foot]"}),
                 (["bed", "0", "{color:10s}"], {"purple_bed[facing=south,part=foot]"}),
                 (["bed", "0", "{a:b}"], {"white_bed[facing=south,part=foot]{a:b}", "orange_bed[facing=south,part=foot]{a:b}", "magenta_bed[facing=south,part=foot]{a:b}", "light_blue_bed[facing=south,part=foot]{a:b}", "yellow_bed[facing=south,part=foot]{a:b}", "lime_bed[facing=south,part=foot]{a:b}", "pink_bed[facing=south,part=foot]{a:b}", "gray_bed[facing=south,part=foot]{a:b}", "light_gray_bed[facing=south,part=foot]{a:b}", "cyan_bed[facing=south,part=foot]{a:b}", "purple_bed[facing=south,part=foot]{a:b}", "blue_bed[facing=south,part=foot]{a:b}", "brown_bed[facing=south,part=foot]{a:b}", "green_bed[facing=south,part=foot]{a:b}", "red_bed[facing=south,part=foot]{a:b}", "black_bed[facing=south,part=foot]{a:b}"}),
                 (["bed", "0", "{color:10,a:b}"], {"purple_bed[facing=south,part=foot]{a:b}"}),
                 (["bed", "default"], {"white_bed[facing=north,occupied=false,part=foot]", "orange_bed[facing=north,occupied=false,part=foot]", "magenta_bed[facing=north,occupied=false,part=foot]", "light_blue_bed[facing=north,occupied=false,part=foot]", "yellow_bed[facing=north,occupied=false,part=foot]", "lime_bed[facing=north,occupied=false,part=foot]", "pink_bed[facing=north,occupied=false,part=foot]", "gray_bed[facing=north,occupied=false,part=foot]", "light_gray_bed[facing=north,occupied=false,part=foot]", "cyan_bed[facing=north,occupied=false,part=foot]", "purple_bed[facing=north,occupied=false,part=foot]", "blue_bed[facing=north,occupied=false,part=foot]", "brown_bed[facing=north,occupied=false,part=foot]", "green_bed[facing=north,occupied=false,part=foot]", "red_bed[facing=north,occupied=false,part=foot]", "black_bed[facing=north,occupied=false,part=foot]"}),
                 (["bed", "default", "{color:10}"], {"purple_bed[facing=north,occupied=false,part=foot]"}),
                 (["bed", "default", "{a:b}"], {"white_bed[facing=north,occupied=false,part=foot]{a:b}", "orange_bed[facing=north,occupied=false,part=foot]{a:b}", "magenta_bed[facing=north,occupied=false,part=foot]{a:b}", "light_blue_bed[facing=north,occupied=false,part=foot]{a:b}", "yellow_bed[facing=north,occupied=false,part=foot]{a:b}", "lime_bed[facing=north,occupied=false,part=foot]{a:b}", "pink_bed[facing=north,occupied=false,part=foot]{a:b}", "gray_bed[facing=north,occupied=false,part=foot]{a:b}", "light_gray_bed[facing=north,occupied=false,part=foot]{a:b}", "cyan_bed[facing=north,occupied=false,part=foot]{a:b}", "purple_bed[facing=north,occupied=false,part=foot]{a:b}", "blue_bed[facing=north,occupied=false,part=foot]{a:b}", "brown_bed[facing=north,occupied=false,part=foot]{a:b}", "green_bed[facing=north,occupied=false,part=foot]{a:b}", "red_bed[facing=north,occupied=false,part=foot]{a:b}", "black_bed[facing=north,occupied=false,part=foot]{a:b}"}),
                 (["bed", "default", "{color:10,a:b}"], {"purple_bed[facing=north,occupied=false,part=foot]{a:b}"}),
                 (["bed", "facing=north"], {"white_bed[facing=north]", "orange_bed[facing=north]", "magenta_bed[facing=north]", "light_blue_bed[facing=north]", "yellow_bed[facing=north]", "lime_bed[facing=north]", "pink_bed[facing=north]", "gray_bed[facing=north]", "light_gray_bed[facing=north]", "cyan_bed[facing=north]", "purple_bed[facing=north]", "blue_bed[facing=north]", "brown_bed[facing=north]", "green_bed[facing=north]", "red_bed[facing=north]", "black_bed[facing=north]"}),
                 (["bed", "facing=north", "{color:10}"], {"purple_bed[facing=north]"}),
                 (["bed", "part=foot,facing=south,occupied=true"], {"white_bed[facing=south,occupied=true,part=foot]", "orange_bed[facing=south,occupied=true,part=foot]", "magenta_bed[facing=south,occupied=true,part=foot]", "light_blue_bed[facing=south,occupied=true,part=foot]", "yellow_bed[facing=south,occupied=true,part=foot]", "lime_bed[facing=south,occupied=true,part=foot]", "pink_bed[facing=south,occupied=true,part=foot]", "gray_bed[facing=south,occupied=true,part=foot]", "light_gray_bed[facing=south,occupied=true,part=foot]", "cyan_bed[facing=south,occupied=true,part=foot]", "purple_bed[facing=south,occupied=true,part=foot]", "blue_bed[facing=south,occupied=true,part=foot]", "brown_bed[facing=south,occupied=true,part=foot]", "green_bed[facing=south,occupied=true,part=foot]", "red_bed[facing=south,occupied=true,part=foot]", "black_bed[facing=south,occupied=true,part=foot]"}),
                 (["bed", "part=foot,facing=south,occupied=true", "{color:10}"], {"purple_bed[facing=south,occupied=true,part=foot]"}),

                 (["tallgrass"], {"grass", "dead_bush", "fern"}),
                 (["tallgrass", "0"], {"dead_bush"}),
                 (["tallgrass", "*"], {"grass", "dead_bush", "fern"}),
                 (["tallgrass", "-1"], {"grass", "dead_bush", "fern"}),
                 (["tallgrass", "default"], {"dead_bush"}),
                 (["tallgrass", "type=tall_grass"], {"grass"}),
                 (["tallgrass", "type=dead_bush"], {"dead_bush"}),
                 (["tallgrass", "type=fern"], {"fern"}),

                 (["skull"], {"skeleton_wall_skull", "wither_skeleton_wall_skull", "zombie_wall_head", "player_wall_head", "creeper_wall_head", "dragon_wall_head", "skeleton_skull", "wither_skeleton_skull", "zombie_head", "player_head", "creeper_head", "dragon_head"}),
                 (["skull", "-1"], {"skeleton_wall_skull", "wither_skeleton_wall_skull", "zombie_wall_head", "player_wall_head", "creeper_wall_head", "dragon_wall_head", "skeleton_skull", "wither_skeleton_skull", "zombie_head", "player_head", "creeper_head", "dragon_head"}),
                 (["skull", "*"], {"skeleton_wall_skull", "wither_skeleton_wall_skull", "zombie_wall_head", "player_wall_head", "creeper_wall_head", "dragon_wall_head", "skeleton_skull", "wither_skeleton_skull", "zombie_head", "player_head", "creeper_head", "dragon_head"}),
                 (["skull", "0"], {"skeleton_skull", "wither_skeleton_skull", "zombie_head", "player_head", "creeper_head", "dragon_head"}),
                 (["skull", "0", "{Rot:0}"], {"skeleton_skull[rotation=0]", "wither_skeleton_skull[rotation=0]", "zombie_head[rotation=0]", "player_head[rotation=0]", "creeper_head[rotation=0]", "dragon_head[rotation=0]"}),
                 (["skull", "0", "{Rot:0,SkullType:4}"], {"creeper_head[rotation=0]"}),
                 (["skull", "2", "{Rot:0,SkullType:4}"], {"creeper_wall_head[facing=north]"}),
                 (["skull", "default"], {"skeleton_wall_skull[facing=north]", "wither_skeleton_wall_skull[facing=north]", "zombie_wall_head[facing=north]", "player_wall_head[facing=north]", "creeper_wall_head[facing=north]", "dragon_wall_head[facing=north]"}),
                 (["skull", "default", "{Rot:0}"], {"skeleton_wall_skull[facing=north]", "wither_skeleton_wall_skull[facing=north]", "zombie_wall_head[facing=north]", "player_wall_head[facing=north]", "creeper_wall_head[facing=north]", "dragon_wall_head[facing=north]"}),
                 (["skull", "default", "{SkullType:1}"], {"wither_skeleton_wall_skull[facing=north]"}),
                 (["skull", "default", "{SkullType:1,Rot:2}"], {"wither_skeleton_wall_skull[facing=north]"}),
                 (["skull", "facing=down"], {"skeleton_skull", "wither_skeleton_skull", "zombie_head", "player_head", "creeper_head", "dragon_head"}),
                 (["skull", "facing=down", "{SkullType:1}"], {"wither_skeleton_skull"}),
                 (["skull", "facing=down", "{SkullType:1,Rot:0}"], {"wither_skeleton_skull[rotation=0]"}),
                 (["skull", "facing=down", "{Rot:0}"], {"skeleton_skull[rotation=0]", "wither_skeleton_skull[rotation=0]", "zombie_head[rotation=0]", "player_head[rotation=0]", "creeper_head[rotation=0]", "dragon_head[rotation=0]"}),
                 (["skull", "facing=north"], {"skeleton_wall_skull[facing=north]", "wither_skeleton_wall_skull[facing=north]", "zombie_wall_head[facing=north]", "player_wall_head[facing=north]", "creeper_wall_head[facing=north]", "dragon_wall_head[facing=north]"}),
                 (["skull", "facing=north", "{SkullType:1}"], {"wither_skeleton_wall_skull[facing=north]"}),
                 (["skull", "facing=north", "{SkullType:1,Rot:0}"], {"wither_skeleton_wall_skull[facing=north]"}),
                 (["skull", "nodrop=true"], {"skeleton_wall_skull", "wither_skeleton_wall_skull", "zombie_wall_head", "player_wall_head", "creeper_wall_head", "dragon_wall_head", "skeleton_skull", "wither_skeleton_skull", "zombie_head", "player_head", "creeper_head", "dragon_head"}),

                 (["double_stone_slab"], {"smooth_stone", "smooth_sandstone", "smooth_quartz", "petrified_oak_slab[type=double]", "cobblestone_slab[type=double]", "brick_slab[type=double]", "stone_brick_slab[type=double]", "nether_brick_slab[type=double]", "stone_slab[type=double]", "sandstone_slab[type=double]", "quartz_slab[type=double]"}),
                 (["double_stone_slab", "0"], {"stone_slab[type=double]"}),
                 (["double_stone_slab", "8"], {"smooth_stone"}),
                 (["double_stone_slab", "default"], {"stone_slab[type=double]"}),
                 (["double_stone_slab", "seamless=true"], {"smooth_stone", "smooth_sandstone", "smooth_quartz", "petrified_oak_slab[type=double]", "cobblestone_slab[type=double]", "brick_slab[type=double]", "stone_brick_slab[type=double]", "nether_brick_slab[type=double]"}),
                 (["double_stone_slab", "seamless=false"], {"stone_slab[type=double]", "sandstone_slab[type=double]", "quartz_slab[type=double]", "petrified_oak_slab[type=double]", "cobblestone_slab[type=double]", "brick_slab[type=double]", "stone_brick_slab[type=double]", "nether_brick_slab[type=double]"}),
                 (["double_stone_slab", "variant=quartz"], {"smooth_quartz", "quartz_slab[type=double]"}),
                 (["double_stone_slab", "seamless=true,variant=wood_old"], {"petrified_oak_slab[type=double]"}),
                 (["double_stone_slab", "seamless=false,variant=wood_old"], {"petrified_oak_slab[type=double]"}),
                 (["double_stone_slab", "seamless=true,variant=quartz"], {"smooth_quartz"}),
                 (["double_stone_slab", "seamless=false,variant=quartz"], {"quartz_slab[type=double]"}))
        for before, after in tests:
            if len(before) == 3:
                before[2] = converter.getCompound(before[2][1:])[0]
            pairs = tuple(zip(("block", "state", "nbt"), before))
            self.assertEqual(after, set(converter.blockTest(dict(pairs), *tuple(zip(*pairs))[0])), "source: {}".format(before))
        self.assertStats()

    def test_block_test_nok(self):
        perms = (["aaa"],
                 ["bed", "-2"],
                 ["bed", "16"],
                 ["bed", "part="],
                 ["bed", "=foot"],
                 ["bed", "part"],
                 ["bed", "part=footfacing=south"],
                 ["bed", "part==south"],
                 ["bed", "part=foot,,facing=south"],
                 ["bed", "part=foot,"],
                 ["bed", ",facing=south"],
                 ["bed", "="],
                 ["bed", ","],
                 ["bed", "a=b"],
                 ["bed", "a=foot"],
                 ["bed", "a=a,b=b"])
        for perm in perms:
            if len(perm) == 3:
                perm[2] = converter.getCompound(perm[2][1:])[0]
            pairs = tuple(zip(("block", "state", "nbt"), perm))
            self.assertRaises(SyntaxError, converter.blockTest, dict(pairs), *tuple(zip(*pairs))[0])
        self.assertStats()


class Item(TestBase):
    def test_item_set_convert(self):
        tests = ((["stone"], "stone"),
                 (["stone", "0"], "stone"),
                 (["stone", "1"], "granite"),
                 (["stone", "2"], "polished_granite"),
                 (["stone", "3"], "diorite"),
                 (["stone", "4"], "polished_diorite"),
                 (["stone", "5"], "andesite"),
                 (["stone", "6"], "polished_andesite"),
                 (["stone", "7"], "stone"),
                 (["stone", "-1"], "stone"),
                 (["stone", "0", "{abc:def}"], "stone{abc:def}"),

                 (["spawn_egg", "0", "{EntityTag:{id:bat}}"], "bat_spawn_egg"),
                 (["spawn_egg", "1", "{EntityTag:{id:bat}}"], "bat_spawn_egg"),
                 (["spawn_egg", "-1", "{EntityTag:{id:bat}}"], "bat_spawn_egg"),
                 (["spawn_egg", "0", "{EntityTag:{id:bat,a:b}}"], "bat_spawn_egg{EntityTag:{a:b}}"),
                 (["spawn_egg", "0", "{EntityTag:{id:bat},a:b}"], "bat_spawn_egg{a:b}"),

                 (["diamond_sword", "0"], "diamond_sword"),
                 (["diamond_sword", "-1"], "diamond_sword"),
                 (["diamond_sword", "1"], "diamond_sword{Damage:1}"),
                 (["diamond_sword", "1", "{a:b}"], "diamond_sword{a:b,Damage:1}"))
        for before, after in tests:
            if len(before) == 3:
                before[2] = converter.getCompound(before[2][1:])[0]
            pairs = tuple(zip(("block", "state", "nbt"), before))
            self.assertEqual(after, converter.item(dict(pairs), *tuple(zip(*pairs))[0]), "source: {}".format(before))
        self.assertStats()

    def test_item_set_nok(self):
        perms = (["aaa"],
                 ["spawn_egg", "0"],
                 ["spawn_egg", "0", "{EntityTag:{a:b}}"],
                 ["spawn_egg", "0", "{EntityTag:{id:b}}"],
                 ["spawn_egg", "0", "{a:b}"])
        for perm in perms:
            if len(perm) == 3:
                perm[2] = converter.getCompound(perm[2][1:])[0]
            pairs = tuple(zip(("block", "state", "nbt"), perm))
            self.assertRaises(SyntaxError, converter.item, dict(pairs), *tuple(zip(*pairs))[0])
        self.assertStats()

    def test_item_test_convert(self):
        tests = ((["stone"], {"stone", "granite", "polished_granite", "diorite", "polished_diorite", "andesite", "polished_andesite"}),
                 (["stone", "0"], {"stone"}),
                 (["stone", "1"], {"granite"}),
                 (["stone", "6"], {"polished_andesite"}),
                 (["stone", "-1"], {"stone", "granite", "polished_granite", "diorite", "polished_diorite", "andesite", "polished_andesite"}),
                 (["stone", "0", "{abc:def}"], {"stone{abc:def}"}),

                 (["spawn_egg", "0", "{EntityTag:{id:bat}}"], {"bat_spawn_egg"}),
                 (["spawn_egg", "-1"], {"bat_spawn_egg", "blaze_spawn_egg", "cave_spider_spawn_egg", "chicken_spawn_egg", "cow_spawn_egg", "creeper_spawn_egg", "donkey_spawn_egg", "elder_guardian_spawn_egg", "enderman_spawn_egg", "endermite_spawn_egg", "evocation_illager_spawn_egg", "ghast_spawn_egg", "guardian_spawn_egg", "horse_spawn_egg", "husk_spawn_egg", "llama_spawn_egg", "magma_cube_spawn_egg", "mooshroom_spawn_egg", "mule_spawn_egg", "ocelot_spawn_egg", "parrot_spawn_egg", "pig_spawn_egg", "polar_bear_spawn_egg", "rabbit_spawn_egg", "sheep_spawn_egg", "shulker_spawn_egg", "silverfish_spawn_egg", "skeleton_spawn_egg", "skeleton_horse_spawn_egg", "slime_spawn_egg", "spider_spawn_egg", "squid_spawn_egg", "stray_spawn_egg", "vex_spawn_egg", "villager_spawn_egg", "vindication_illager_spawn_egg", "witch_spawn_egg", "wither_skeleton_spawn_egg", "wolf_spawn_egg", "zombie_spawn_egg", "zombie_horse_spawn_egg", "zombie_pigman_spawn_egg", "zombie_villager_spawn_egg"}),
                 (["spawn_egg", "0"], {"bat_spawn_egg", "blaze_spawn_egg", "cave_spider_spawn_egg", "chicken_spawn_egg", "cow_spawn_egg", "creeper_spawn_egg", "donkey_spawn_egg", "elder_guardian_spawn_egg", "enderman_spawn_egg", "endermite_spawn_egg", "evocation_illager_spawn_egg", "ghast_spawn_egg", "guardian_spawn_egg", "horse_spawn_egg", "husk_spawn_egg", "llama_spawn_egg", "magma_cube_spawn_egg", "mooshroom_spawn_egg", "mule_spawn_egg", "ocelot_spawn_egg", "parrot_spawn_egg", "pig_spawn_egg", "polar_bear_spawn_egg", "rabbit_spawn_egg", "sheep_spawn_egg", "shulker_spawn_egg", "silverfish_spawn_egg", "skeleton_spawn_egg", "skeleton_horse_spawn_egg", "slime_spawn_egg", "spider_spawn_egg", "squid_spawn_egg", "stray_spawn_egg", "vex_spawn_egg", "villager_spawn_egg", "vindication_illager_spawn_egg", "witch_spawn_egg", "wither_skeleton_spawn_egg", "wolf_spawn_egg", "zombie_spawn_egg", "zombie_horse_spawn_egg", "zombie_pigman_spawn_egg", "zombie_villager_spawn_egg"}),
                 (["spawn_egg", "-1", "{EntityTag:{id:bat}}"], {"bat_spawn_egg"}),
                 (["spawn_egg", "0", "{EntityTag:{id:bat,a:b}}"], {"bat_spawn_egg{EntityTag:{a:b}}"}),
                 (["spawn_egg", "0", "{EntityTag:{id:bat},a:b}"], {"bat_spawn_egg{a:b}"}),

                 (["diamond_sword", "0"], {"diamond_sword"}),
                 (["diamond_sword", "-1"], {"diamond_sword"}),
                 (["diamond_sword", "1"], {"diamond_sword{Damage:1}"}),
                 (["diamond_sword", "1", "{a:b}"], {"diamond_sword{a:b,Damage:1}"}))
        for before, after in tests:
            if len(before) == 3:
                before[2] = converter.getCompound(before[2][1:])[0]
            pairs = tuple(zip(("block", "state", "nbt"), before))
            self.assertEqual(after, set(converter.itemTest(dict(pairs), *tuple(zip(*pairs))[0])), "source: {}".format(before))
        self.assertStats()

    def test_item_test_nok(self):
        perms = (["aaa"],
                 ["stone", "7"],
                 ["spawn_egg", "0", "{EntityTag:{id:b}}"])
        for perm in perms:
            if len(perm) == 3:
                perm[2] = converter.getCompound(perm[2][1:])[0]
            pairs = tuple(zip(("block", "state", "nbt"), perm))
            self.assertRaises(SyntaxError, converter.itemTest, dict(pairs), *tuple(zip(*pairs))[0])
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
                 "advancement grant @s only adv_name crit ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("advancement grant @s only adv_name crit", "advancement grant @s only adv_name crit"),
                 ("advancement grant @s from adv_name", "advancement grant @s from adv_name"),
                 ("advancement revoke @s from adv_name crit", "advancement revoke @s from adv_name crit"),
                 ("advancement grant @s only adv_name crit", "advancement grant @s only adv_name crit"),
                 ("advancement grant @s until adv_name", "advancement grant @s until adv_name"),
                 ("advancement revoke @s through adv_name crit", "advancement revoke @s through adv_name crit"),
                 ("advancement grant @s only adv_name", "advancement grant @s only adv_name"),
                 ("advancement revoke @s until adv_name crit", "advancement revoke @s until adv_name crit"),
                 ("advancement revoke @s through adv_name", "advancement revoke @s through adv_name"),
                 ("advancement grant @s through adv_name", "advancement grant @s through adv_name"),
                 ("advancement revoke @s from adv_name", "advancement revoke @s from adv_name"),
                 ("advancement revoke @s until adv_name", "advancement revoke @s until adv_name"),
                 ("advancement revoke @s only adv_name crit", "advancement revoke @s only adv_name crit"),
                 ("advancement grant @s from adv_name crit", "advancement grant @s from adv_name crit"),
                 ("advancement revoke @s only adv_name", "advancement revoke @s only adv_name"),
                 ("advancement grant @s through adv_name crit", "advancement grant @s through adv_name crit"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("advancement grant @s everything", "advancement grant @s everything"),
                 ("advancement revoke @s everything", "advancement revoke @s everything"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = (("advancement test @s adv_name crit", "execute if entity @s[advancements={adv_name={crit=true}}]"),
                 ("advancement test @s adv_name", "execute if entity @s[advancements={adv_name=true}]"),
                 ("advancement test Carl adv_name crit", "execute if entity @p[name=Carl,advancements={adv_name={crit=true}}]"),
                 ("advancement test Carl adv_name", "execute if entity @p[name=Carl,advancements={adv_name=true}]"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("ban p_name Because", "ban p_name Because"),
                 ("ban p_name Because I said so", "ban p_name Because I said so"),
                 ("ban p_name", "ban p_name"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("ban-ip p_name Because", "ban-ip p_name Because"),
                 ("ban-ip p_name Because I said so", "ban-ip p_name Because I said so"),
                 ("ban-ip p_name", "ban-ip p_name"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("blockdata 1 ~ ~3 {abc:def}", "data merge block 1 ~ ~3 {abc:def}"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
                 "clear @s stone a 42 {abc:def}",
                 "clear @s stone -2 42 {abc:def}",
                 "clear @s stone 42 42 {abc:def}",
                 "clear @s stone 1 aa {abc:def}",
                 "clear @s stone 1 42 aaaaaaaaa",
                 "clear @s stone 1 42 {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("clear", "clear"),
                 ("clear @s", "clear @s"),
                 ("clear @s stone", "#~ The splitting of this command (clear @s stone) can produce different results if used with stats\n"
                                    "clear @s andesite\n"
                                    "clear @s diorite\n"
                                    "clear @s granite\n"
                                    "clear @s polished_andesite\n"
                                    "clear @s polished_diorite\n"
                                    "clear @s polished_granite\n"
                                    "clear @s stone"),
                 ("clear @s stone 1", "clear @s granite"),
                 ("clear @s stone 1 42", "clear @s granite 42"),
                 ("clear @s stone 1 42 {abc:def}", "clear @s granite{abc:def} 42"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1", "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked", "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked force", "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked force"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked move", "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked move"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked normal", "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 masked"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace", "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace force", "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace force"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace move", "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace move"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace normal", "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 replace"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force stone 1", "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered granite force"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force stone", "#~ The splitting of this command (clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered force stone) can produce different results if used with stats\n"
                                                                           "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered andesite force\n"
                                                                           "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered diorite force\n"
                                                                           "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered granite force\n"
                                                                           "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered polished_andesite force\n"
                                                                           "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered polished_diorite force\n"
                                                                           "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered polished_granite force\n"
                                                                           "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone force"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered move stone 1", "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered granite move"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered move stone", "#~ The splitting of this command (clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered move stone) can produce different results if used with stats\n"
                                                                          "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered andesite move\n"
                                                                          "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered diorite move\n"
                                                                          "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered granite move\n"
                                                                          "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered polished_andesite move\n"
                                                                          "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered polished_diorite move\n"
                                                                          "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered polished_granite move\n"
                                                                          "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone move"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered normal stone 1", "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered granite"),
                 ("clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered normal stone", "#~ The splitting of this command (clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered normal stone) can produce different results if used with stats\n"
                                                                            "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered andesite\n"
                                                                            "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered diorite\n"
                                                                            "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered granite\n"
                                                                            "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered polished_andesite\n"
                                                                            "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered polished_diorite\n"
                                                                            "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered polished_granite\n"
                                                                            "clone 1 ~-1 ~1 1 ~-1 ~1 1 ~-1 ~1 filtered stone"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("debug start", "debug start"),
                 ("debug stop", "debug stop"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("defaultgamemode 0", "defaultgamemode survival"),
                 ("defaultgamemode 1", "defaultgamemode creative"),
                 ("defaultgamemode 2", "defaultgamemode adventure"),
                 ("defaultgamemode 3", "defaultgamemode spectator"),
                 ("defaultgamemode s", "defaultgamemode survival"),
                 ("defaultgamemode c", "defaultgamemode creative"),
                 ("defaultgamemode a", "defaultgamemode adventure"),
                 ("defaultgamemode sp", "defaultgamemode spectator"),
                 ("defaultgamemode survival", "defaultgamemode survival"),
                 ("defaultgamemode creative", "defaultgamemode creative"),
                 ("defaultgamemode adventure", "defaultgamemode adventure"),
                 ("defaultgamemode spectator", "defaultgamemode spectator"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("deop @s", "deop @s"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("difficulty 0", "difficulty peaceful"),
                 ("difficulty 1", "difficulty easy"),
                 ("difficulty 2", "difficulty normal"),
                 ("difficulty 3", "difficulty hard"),
                 ("difficulty p", "difficulty peaceful"),
                 ("difficulty e", "difficulty easy"),
                 ("difficulty n", "difficulty normal"),
                 ("difficulty h", "difficulty hard"),
                 ("difficulty peaceful", "difficulty peaceful"),
                 ("difficulty easy", "difficulty easy"),
                 ("difficulty normal", "difficulty normal"),
                 ("difficulty hard", "difficulty hard"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("effect @s clear", "effect clear @s"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("effect @s speed", "effect give @s speed"),
                 ("effect @s minecraft:speed", "effect give @s speed"),
                 ("effect @s speed 0", "effect clear @s speed"),
                 ("effect @s speed 11", "effect give @s speed 11"),
                 ("effect @s speed 11 22", "effect give @s speed 11 22"),
                 ("effect @s speed 11 22 true", "effect give @s speed 11 22 true"),
                 ("effect @s speed 30 0 false", "effect give @s speed"),
                 ("effect @s speed 11 0 false", "effect give @s speed 11"),
                 ("effect @s speed 11 22 false", "effect give @s speed 11 22"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("enchant @s minecraft:protection", "enchant @s protection"),
                 ("enchant @s 0", "enchant @s protection"),
                 ("enchant @s 0 1", "enchant @s protection"),
                 ("enchant @s 0 2", "enchant @s protection 2"),
                 ("enchant @s protection", "enchant @s protection"),
                 ("enchant @s protection 1", "enchant @s protection"),
                 ("enchant @s protection 2", "enchant @s protection 2"),
                
                 ("enchant @s 1", "enchant @s fire_protection"),
                 ("enchant @s 1 1", "enchant @s fire_protection"),
                 ("enchant @s 1 2", "enchant @s fire_protection 2"),
                 ("enchant @s fire_protection", "enchant @s fire_protection"),
                 ("enchant @s fire_protection 1", "enchant @s fire_protection"),
                 ("enchant @s fire_protection 2", "enchant @s fire_protection 2"),

                 ("enchant @s 2", "enchant @s feather_falling"),
                 ("enchant @s 2 1", "enchant @s feather_falling"),
                 ("enchant @s 2 2", "enchant @s feather_falling 2"),
                 ("enchant @s feather_falling", "enchant @s feather_falling"),
                 ("enchant @s feather_falling 1", "enchant @s feather_falling"),
                 ("enchant @s feather_falling 2", "enchant @s feather_falling 2"),

                 ("enchant @s 3", "enchant @s blast_protection"),
                 ("enchant @s 3 1", "enchant @s blast_protection"),
                 ("enchant @s 3 2", "enchant @s blast_protection 2"),
                 ("enchant @s blast_protection", "enchant @s blast_protection"),
                 ("enchant @s blast_protection 1", "enchant @s blast_protection"),
                 ("enchant @s blast_protection 2", "enchant @s blast_protection 2"),

                 ("enchant @s 4", "enchant @s projectile_protection"),
                 ("enchant @s 4 1", "enchant @s projectile_protection"),
                 ("enchant @s 4 2", "enchant @s projectile_protection 2"),
                 ("enchant @s projectile_protection", "enchant @s projectile_protection"),
                 ("enchant @s projectile_protection 1", "enchant @s projectile_protection"),
                 ("enchant @s projectile_protection 2", "enchant @s projectile_protection 2"),

                 ("enchant @s 5", "enchant @s respiration"),
                 ("enchant @s 5 1", "enchant @s respiration"),
                 ("enchant @s 5 2", "enchant @s respiration 2"),
                 ("enchant @s respiration", "enchant @s respiration"),
                 ("enchant @s respiration 1", "enchant @s respiration"),
                 ("enchant @s respiration 2", "enchant @s respiration 2"),

                 ("enchant @s 6", "enchant @s aqua_affinity"),
                 ("enchant @s 6 1", "enchant @s aqua_affinity"),
                 ("enchant @s aqua_affinity", "enchant @s aqua_affinity"),
                 ("enchant @s aqua_affinity 1", "enchant @s aqua_affinity"),

                 ("enchant @s 7", "enchant @s thorns"),
                 ("enchant @s 7 1", "enchant @s thorns"),
                 ("enchant @s 7 2", "enchant @s thorns 2"),
                 ("enchant @s thorns", "enchant @s thorns"),
                 ("enchant @s thorns 1", "enchant @s thorns"),
                 ("enchant @s thorns 2", "enchant @s thorns 2"),

                 ("enchant @s 8", "enchant @s depth_strider"),
                 ("enchant @s 8 1", "enchant @s depth_strider"),
                 ("enchant @s 8 2", "enchant @s depth_strider 2"),
                 ("enchant @s depth_strider", "enchant @s depth_strider"),
                 ("enchant @s depth_strider 1", "enchant @s depth_strider"),
                 ("enchant @s depth_strider 2", "enchant @s depth_strider 2"),

                 ("enchant @s 9", "enchant @s frost_walker"),
                 ("enchant @s 9 1", "enchant @s frost_walker"),
                 ("enchant @s 9 2", "enchant @s frost_walker 2"),
                 ("enchant @s frost_walker", "enchant @s frost_walker"),
                 ("enchant @s frost_walker 1", "enchant @s frost_walker"),
                 ("enchant @s frost_walker 2", "enchant @s frost_walker 2"),

                 ("enchant @s 10", "enchant @s binding_curse"),
                 ("enchant @s 10 1", "enchant @s binding_curse"),
                 ("enchant @s binding_curse", "enchant @s binding_curse"),
                 ("enchant @s binding_curse 1", "enchant @s binding_curse"),

                 ("enchant @s 16", "enchant @s sharpness"),
                 ("enchant @s 16 1", "enchant @s sharpness"),
                 ("enchant @s 16 2", "enchant @s sharpness 2"),
                 ("enchant @s sharpness", "enchant @s sharpness"),
                 ("enchant @s sharpness 1", "enchant @s sharpness"),
                 ("enchant @s sharpness 2", "enchant @s sharpness 2"),

                 ("enchant @s 17", "enchant @s smite"),
                 ("enchant @s 17 1", "enchant @s smite"),
                 ("enchant @s 17 2", "enchant @s smite 2"),
                 ("enchant @s smite", "enchant @s smite"),
                 ("enchant @s smite 1", "enchant @s smite"),
                 ("enchant @s smite 2", "enchant @s smite 2"),

                 ("enchant @s 18", "enchant @s bane_of_arthropods"),
                 ("enchant @s 18 1", "enchant @s bane_of_arthropods"),
                 ("enchant @s 18 2", "enchant @s bane_of_arthropods 2"),
                 ("enchant @s bane_of_arthropods", "enchant @s bane_of_arthropods"),
                 ("enchant @s bane_of_arthropods 1", "enchant @s bane_of_arthropods"),
                 ("enchant @s bane_of_arthropods 2", "enchant @s bane_of_arthropods 2"),

                 ("enchant @s 19", "enchant @s knockback"),
                 ("enchant @s 19 1", "enchant @s knockback"),
                 ("enchant @s 19 2", "enchant @s knockback 2"),
                 ("enchant @s knockback", "enchant @s knockback"),
                 ("enchant @s knockback 1", "enchant @s knockback"),
                 ("enchant @s knockback 2", "enchant @s knockback 2"),

                 ("enchant @s 20", "enchant @s fire_aspect"),
                 ("enchant @s 20 1", "enchant @s fire_aspect"),
                 ("enchant @s 20 2", "enchant @s fire_aspect 2"),
                 ("enchant @s fire_aspect", "enchant @s fire_aspect"),
                 ("enchant @s fire_aspect 1", "enchant @s fire_aspect"),
                 ("enchant @s fire_aspect 2", "enchant @s fire_aspect 2"),

                 ("enchant @s 21", "enchant @s looting"),
                 ("enchant @s 21 1", "enchant @s looting"),
                 ("enchant @s 21 2", "enchant @s looting 2"),
                 ("enchant @s looting", "enchant @s looting"),
                 ("enchant @s looting 1", "enchant @s looting"),
                 ("enchant @s looting 2", "enchant @s looting 2"),

                 ("enchant @s 22", "enchant @s sweeping"),
                 ("enchant @s 22 1", "enchant @s sweeping"),
                 ("enchant @s 22 2", "enchant @s sweeping 2"),
                 ("enchant @s sweeping", "enchant @s sweeping"),
                 ("enchant @s sweeping 1", "enchant @s sweeping"),
                 ("enchant @s sweeping 2", "enchant @s sweeping 2"),

                 ("enchant @s 32", "enchant @s efficiency"),
                 ("enchant @s 32 1", "enchant @s efficiency"),
                 ("enchant @s 32 2", "enchant @s efficiency 2"),
                 ("enchant @s efficiency", "enchant @s efficiency"),
                 ("enchant @s efficiency 1", "enchant @s efficiency"),
                 ("enchant @s efficiency 2", "enchant @s efficiency 2"),

                 ("enchant @s 33", "enchant @s silk_touch"),
                 ("enchant @s 33 1", "enchant @s silk_touch"),
                 ("enchant @s silk_touch", "enchant @s silk_touch"),
                 ("enchant @s silk_touch 1", "enchant @s silk_touch"),

                 ("enchant @s 34", "enchant @s unbreaking"),
                 ("enchant @s 34 1", "enchant @s unbreaking"),
                 ("enchant @s 34 2", "enchant @s unbreaking 2"),
                 ("enchant @s unbreaking", "enchant @s unbreaking"),
                 ("enchant @s unbreaking 1", "enchant @s unbreaking"),
                 ("enchant @s unbreaking 2", "enchant @s unbreaking 2"),

                 ("enchant @s 35", "enchant @s fortune"),
                 ("enchant @s 35 1", "enchant @s fortune"),
                 ("enchant @s 35 2", "enchant @s fortune 2"),
                 ("enchant @s fortune", "enchant @s fortune"),
                 ("enchant @s fortune 1", "enchant @s fortune"),
                 ("enchant @s fortune 2", "enchant @s fortune 2"),

                 ("enchant @s 48", "enchant @s power"),
                 ("enchant @s 48 1", "enchant @s power"),
                 ("enchant @s 48 2", "enchant @s power 2"),
                 ("enchant @s power", "enchant @s power"),
                 ("enchant @s power 1", "enchant @s power"),
                 ("enchant @s power 2", "enchant @s power 2"),

                 ("enchant @s 49", "enchant @s punch"),
                 ("enchant @s 49 1", "enchant @s punch"),
                 ("enchant @s 49 2", "enchant @s punch 2"),
                 ("enchant @s punch", "enchant @s punch"),
                 ("enchant @s punch 1", "enchant @s punch"),
                 ("enchant @s punch 2", "enchant @s punch 2"),

                 ("enchant @s 50", "enchant @s flame"),
                 ("enchant @s 50 1", "enchant @s flame"),
                 ("enchant @s flame", "enchant @s flame"),
                 ("enchant @s flame 1", "enchant @s flame"),

                 ("enchant @s 51", "enchant @s infinity"),
                 ("enchant @s 51 1", "enchant @s infinity"),
                 ("enchant @s infinity", "enchant @s infinity"),
                 ("enchant @s infinity 1", "enchant @s infinity"),

                 ("enchant @s 61", "enchant @s luck_of_the_sea"),
                 ("enchant @s 61 1", "enchant @s luck_of_the_sea"),
                 ("enchant @s 61 2", "enchant @s luck_of_the_sea 2"),
                 ("enchant @s luck_of_the_sea", "enchant @s luck_of_the_sea"),
                 ("enchant @s luck_of_the_sea 1", "enchant @s luck_of_the_sea"),
                 ("enchant @s luck_of_the_sea 2", "enchant @s luck_of_the_sea 2"),

                 ("enchant @s 62", "enchant @s lure"),
                 ("enchant @s 62 1", "enchant @s lure"),
                 ("enchant @s 62 2", "enchant @s lure 2"),
                 ("enchant @s lure", "enchant @s lure"),
                 ("enchant @s lure 1", "enchant @s lure"),
                 ("enchant @s lure 2", "enchant @s lure 2"),

                 ("enchant @s 70", "enchant @s mending"),
                 ("enchant @s 70 1", "enchant @s mending"),
                 ("enchant @s mending", "enchant @s mending"),
                 ("enchant @s mending 1", "enchant @s mending"),

                 ("enchant @s 71", "enchant @s vanishing_curse"),
                 ("enchant @s 71 1", "enchant @s vanishing_curse"),
                 ("enchant @s vanishing_curse", "enchant @s vanishing_curse"),
                 ("enchant @s vanishing_curse 1", "enchant @s vanishing_curse"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("entitydata @s {abc:def}", "data merge entity @s {abc:def}"),
                 ("entitydata @e[c=1] {abc:def}", "data merge entity @e[limit=1,sort=nearest] {abc:def}"),
                 ("entitydata @e {abc:def}", "execute as @e run data merge entity @s {abc:def}"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("execute @e[name=Carl] 1 ~-1 1 toggledownfall", "#~ execute as @e[name=Carl] run toggledownfall ||| This command was removed"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 toggledownfall", "#~ execute as @e[tag=Carl] as @e[name=Carl] run toggledownfall ||| This command was removed"),
                 ("execute Carl 1 ~-1 1 function abc:def", "execute as Carl at @s positioned 1 ~-1 1 run function abc:def"),
                 ("execute @e ~ ~ ~ locate temple", "#~ The splitting of this command (locate Temple) can produce different results if used with stats\n"
                                                    "execute at @e run locate Desert_Pyramid\n"
                                                    "execute at @e run locate Igloo\n"
                                                    "execute at @e run locate Jungle_Pyramid\n"
                                                    "execute at @e run locate Swamp_Hut"),


                 # @s
                 # not canAs and not canAt
                 ("execute @s ~ ~ ~ seed", "seed"),
                 ("execute @s[name=Carl] ~ ~ ~ seed", "execute as @s[name=Carl] run seed"),
                 ("execute @s 1 ~-1 1 seed", "seed"),
                 ("execute @s[name=Carl] 1 ~-1 1 seed", "execute as @s[name=Carl] run seed"),

                 ("execute @s ~ ~ ~ execute @s ~ ~ ~ seed", "seed"),
                 ("execute @s ~ ~ ~ execute @s[name=Carl] ~ ~ ~ seed", "execute as @s[name=Carl] run seed"),
                 ("execute @s ~ ~ ~ execute @s 1 ~-1 1 seed", "seed"),
                 ("execute @s ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 seed", "execute as @s[name=Carl] run seed"),

                 ("execute @s 1 ~-1 1 execute @s ~ ~ ~ seed", "seed"),
                 ("execute @s 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ seed", "execute as @s[name=Carl] run seed"),
                 ("execute @s 1 ~-1 1 execute @s 1 ~-1 1 seed", "seed"),
                 ("execute @s 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 seed", "execute as @s[name=Carl] run seed"),

                 ("execute @s[tag=Carl] ~ ~ ~ execute @s ~ ~ ~ seed", "execute as @s[tag=Carl] run seed"),
                 ("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] ~ ~ ~ seed", "execute as @s[tag=Carl] as @s[name=Carl] run seed"),
                 ("execute @s[tag=Carl] ~ ~ ~ execute @s 1 ~-1 1 seed", "execute as @s[tag=Carl] run seed"),
                 ("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 seed", "execute as @s[tag=Carl] as @s[name=Carl] run seed"),

                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s ~ ~ ~ seed", "execute as @s[tag=Carl] run seed"),
                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ seed", "execute as @s[tag=Carl] as @s[name=Carl] run seed"),
                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s 1 ~-1 1 seed", "execute as @s[tag=Carl] run seed"),
                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 seed", "execute as @s[tag=Carl] as @s[name=Carl] run seed"),

                 # canAs and not canAt
                 ("execute @s ~ ~ ~ say hi", "say hi"),
                 ("execute @s[name=Carl] ~ ~ ~ say hi", "execute as @s[name=Carl] run say hi"),
                 ("execute @s 1 ~-1 1 say hi", "say hi"),
                 ("execute @s[name=Carl] 1 ~-1 1 say hi", "execute as @s[name=Carl] run say hi"),

                 ("execute @s ~ ~ ~ execute @s ~ ~ ~ say hi", "say hi"),
                 ("execute @s ~ ~ ~ execute @s[name=Carl] ~ ~ ~ say hi", "execute as @s[name=Carl] run say hi"),
                 ("execute @s ~ ~ ~ execute @s 1 ~-1 1 say hi", "say hi"),
                 ("execute @s ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 say hi", "execute as @s[name=Carl] run say hi"),

                 ("execute @s 1 ~-1 1 execute @s ~ ~ ~ say hi", "say hi"),
                 ("execute @s 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ say hi", "execute as @s[name=Carl] run say hi"),
                 ("execute @s 1 ~-1 1 execute @s 1 ~-1 1 say hi", "say hi"),
                 ("execute @s 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 say hi", "execute as @s[name=Carl] run say hi"),

                 ("execute @s[tag=Carl] ~ ~ ~ execute @s ~ ~ ~ say hi", "execute as @s[tag=Carl] run say hi"),
                 ("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] ~ ~ ~ say hi", "execute as @s[tag=Carl] as @s[name=Carl] run say hi"),
                 ("execute @s[tag=Carl] ~ ~ ~ execute @s 1 ~-1 1 say hi", "execute as @s[tag=Carl] run say hi"),
                 ("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 say hi", "execute as @s[tag=Carl] as @s[name=Carl] run say hi"),

                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s ~ ~ ~ say hi", "execute as @s[tag=Carl] run say hi"),
                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ say hi", "execute as @s[tag=Carl] as @s[name=Carl] run say hi"),
                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s 1 ~-1 1 say hi", "execute as @s[tag=Carl] run say hi"),
                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 say hi", "execute as @s[tag=Carl] as @s[name=Carl] run say hi"),

                 # not canAs and canAt
                 ("execute @s ~ ~ ~ setblock ~ ~ ~ stone", "execute at @s run setblock ~ ~ ~ stone"),
                 ("execute @s[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone", "execute at @s[name=Carl] run setblock ~ ~ ~ stone"),
                 ("execute @s 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @s positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 ("execute @s[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @s[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 ("execute @s ~ ~ ~ execute @s ~ ~ ~ setblock ~ ~ ~ stone", "execute at @s run setblock ~ ~ ~ stone"),
                 ("execute @s ~ ~ ~ execute @s[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone", "execute at @s[name=Carl] run setblock ~ ~ ~ stone"),
                 ("execute @s ~ ~ ~ execute @s 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @s positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 ("execute @s ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @s[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 ("execute @s 1 ~-1 1 execute @s ~ ~ ~ setblock ~ ~ ~ stone", "execute at @s positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 ("execute @s 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone", "execute at @s positioned 1 ~-1 1 at @s[name=Carl] run setblock ~ ~ ~ stone"),
                 ("execute @s 1 ~-1 1 execute @s 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @s positioned 1 ~-1 1 positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 ("execute @s 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @s positioned 1 ~-1 1 at @s[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 ("execute @s[tag=Carl] ~ ~ ~ execute @s ~ ~ ~ setblock ~ ~ ~ stone", "execute at @s[tag=Carl] run setblock ~ ~ ~ stone"),
                 ("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone", "execute at @s[tag=Carl] at @s[name=Carl] run setblock ~ ~ ~ stone"),
                 ("execute @s[tag=Carl] ~ ~ ~ execute @s 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @s[tag=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 ("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @s[tag=Carl] at @s[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s ~ ~ ~ setblock ~ ~ ~ stone", "execute at @s[tag=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone", "execute at @s[tag=Carl] positioned 1 ~-1 1 at @s[name=Carl] run setblock ~ ~ ~ stone"),
                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @s[tag=Carl] positioned 1 ~-1 1 positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @s[tag=Carl] positioned 1 ~-1 1 at @s[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 # canAs and canAt
                 ("execute @s ~ ~ ~ function abc:def", "execute at @s run function abc:def"),
                 ("execute @s[name=Carl] ~ ~ ~ function abc:def", "execute at @s[name=Carl] run function abc:def"),
                 ("execute @s 1 ~-1 1 function abc:def", "execute at @s positioned 1 ~-1 1 run function abc:def"),
                 ("execute @s[name=Carl] 1 ~-1 1 function abc:def", "execute at @s[name=Carl] positioned 1 ~-1 1 run function abc:def"),

                 ("execute @s ~ ~ ~ execute @s ~ ~ ~ function abc:def", "execute at @s run function abc:def"),
                 ("execute @s ~ ~ ~ execute @s[name=Carl] ~ ~ ~ function abc:def", "execute at @s[name=Carl] run function abc:def"),
                 ("execute @s ~ ~ ~ execute @s 1 ~-1 1 function abc:def", "execute at @s positioned 1 ~-1 1 run function abc:def"),
                 ("execute @s ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 function abc:def", "execute at @s[name=Carl] positioned 1 ~-1 1 run function abc:def"),

                 ("execute @s 1 ~-1 1 execute @s ~ ~ ~ function abc:def", "execute at @s positioned 1 ~-1 1 run function abc:def"),
                 ("execute @s 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ function abc:def", "execute at @s positioned 1 ~-1 1 at @s[name=Carl] run function abc:def"),
                 ("execute @s 1 ~-1 1 execute @s 1 ~-1 1 function abc:def", "execute at @s positioned 1 ~-1 1 positioned 1 ~-1 1 run function abc:def"),
                 ("execute @s 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 function abc:def", "execute at @s positioned 1 ~-1 1 at @s[name=Carl] positioned 1 ~-1 1 run function abc:def"),

                 ("execute @s[tag=Carl] ~ ~ ~ execute @s ~ ~ ~ function abc:def", "execute at @s[tag=Carl] run function abc:def"),
                 ("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] ~ ~ ~ function abc:def", "execute at @s[tag=Carl] at @s[name=Carl] run function abc:def"),
                 ("execute @s[tag=Carl] ~ ~ ~ execute @s 1 ~-1 1 function abc:def", "execute at @s[tag=Carl] positioned 1 ~-1 1 run function abc:def"),
                 ("execute @s[tag=Carl] ~ ~ ~ execute @s[name=Carl] 1 ~-1 1 function abc:def", "execute at @s[tag=Carl] at @s[name=Carl] positioned 1 ~-1 1 run function abc:def"),

                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s ~ ~ ~ function abc:def", "execute at @s[tag=Carl] positioned 1 ~-1 1 run function abc:def"),
                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] ~ ~ ~ function abc:def", "execute at @s[tag=Carl] positioned 1 ~-1 1 at @s[name=Carl] run function abc:def"),
                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s 1 ~-1 1 function abc:def", "execute at @s[tag=Carl] positioned 1 ~-1 1 positioned 1 ~-1 1 run function abc:def"),
                 ("execute @s[tag=Carl] 1 ~-1 1 execute @s[name=Carl] 1 ~-1 1 function abc:def", "execute at @s[tag=Carl] positioned 1 ~-1 1 at @s[name=Carl] positioned 1 ~-1 1 run function abc:def"),

                 # @e
                 # not canAs and not canAt
                 ("execute @e ~ ~ ~ seed", "execute as @e run seed"),
                 ("execute @e[name=Carl] ~ ~ ~ seed", "execute as @e[name=Carl] run seed"),
                 ("execute @e 1 ~-1 1 seed", "execute as @e run seed"),
                 ("execute @e[name=Carl] 1 ~-1 1 seed", "execute as @e[name=Carl] run seed"),

                 ("execute @e ~ ~ ~ execute @e ~ ~ ~ seed", "execute as @e as @e run seed"),
                 ("execute @e ~ ~ ~ execute @e[name=Carl] ~ ~ ~ seed", "execute as @e as @e[name=Carl] run seed"),
                 ("execute @e ~ ~ ~ execute @e 1 ~-1 1 seed", "execute as @e as @e run seed"),
                 ("execute @e ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 seed", "execute as @e as @e[name=Carl] run seed"),

                 ("execute @e 1 ~-1 1 execute @e ~ ~ ~ seed", "execute as @e as @e run seed"),
                 ("execute @e 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ seed", "execute as @e as @e[name=Carl] run seed"),
                 ("execute @e 1 ~-1 1 execute @e 1 ~-1 1 seed", "execute as @e as @e run seed"),
                 ("execute @e 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 seed", "execute as @e as @e[name=Carl] run seed"),

                 ("execute @e[tag=Carl] ~ ~ ~ execute @e ~ ~ ~ seed", "execute as @e[tag=Carl] as @e run seed"),
                 ("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] ~ ~ ~ seed", "execute as @e[tag=Carl] as @e[name=Carl] run seed"),
                 ("execute @e[tag=Carl] ~ ~ ~ execute @e 1 ~-1 1 seed", "execute as @e[tag=Carl] as @e run seed"),
                 ("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 seed", "execute as @e[tag=Carl] as @e[name=Carl] run seed"),

                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e ~ ~ ~ seed", "execute as @e[tag=Carl] as @e run seed"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ seed", "execute as @e[tag=Carl] as @e[name=Carl] run seed"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e 1 ~-1 1 seed", "execute as @e[tag=Carl] as @e run seed"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 seed", "execute as @e[tag=Carl] as @e[name=Carl] run seed"),

                 # canAs and not canAt
                 ("execute @e ~ ~ ~ say hi", "execute as @e run say hi"),
                 ("execute @e[name=Carl] ~ ~ ~ say hi", "execute as @e[name=Carl] run say hi"),
                 ("execute @e 1 ~-1 1 say hi", "execute as @e run say hi"),
                 ("execute @e[name=Carl] 1 ~-1 1 say hi", "execute as @e[name=Carl] run say hi"),

                 ("execute @e ~ ~ ~ execute @e ~ ~ ~ say hi", "execute as @e as @e run say hi"),
                 ("execute @e ~ ~ ~ execute @e[name=Carl] ~ ~ ~ say hi", "execute as @e as @e[name=Carl] run say hi"),
                 ("execute @e ~ ~ ~ execute @e 1 ~-1 1 say hi", "execute as @e as @e run say hi"),
                 ("execute @e ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 say hi", "execute as @e as @e[name=Carl] run say hi"),

                 ("execute @e 1 ~-1 1 execute @e ~ ~ ~ say hi", "execute as @e as @e run say hi"),
                 ("execute @e 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ say hi", "execute as @e as @e[name=Carl] run say hi"),
                 ("execute @e 1 ~-1 1 execute @e 1 ~-1 1 say hi", "execute as @e as @e run say hi"),
                 ("execute @e 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 say hi", "execute as @e as @e[name=Carl] run say hi"),

                 ("execute @e[tag=Carl] ~ ~ ~ execute @e ~ ~ ~ say hi", "execute as @e[tag=Carl] as @e run say hi"),
                 ("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] ~ ~ ~ say hi", "execute as @e[tag=Carl] as @e[name=Carl] run say hi"),
                 ("execute @e[tag=Carl] ~ ~ ~ execute @e 1 ~-1 1 say hi", "execute as @e[tag=Carl] as @e run say hi"),
                 ("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 say hi", "execute as @e[tag=Carl] as @e[name=Carl] run say hi"),

                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e ~ ~ ~ say hi", "execute as @e[tag=Carl] as @e run say hi"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ say hi", "execute as @e[tag=Carl] as @e[name=Carl] run say hi"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e 1 ~-1 1 say hi", "execute as @e[tag=Carl] as @e run say hi"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 say hi", "execute as @e[tag=Carl] as @e[name=Carl] run say hi"),

                 # not canAs and canAt
                 ("execute @e ~ ~ ~ setblock ~ ~ ~ stone", "execute at @e run setblock ~ ~ ~ stone"),
                 ("execute @e[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone", "execute at @e[name=Carl] run setblock ~ ~ ~ stone"),
                 ("execute @e 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @e positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 ("execute @e[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @e[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 ("execute @e ~ ~ ~ execute @e ~ ~ ~ setblock ~ ~ ~ stone", "execute at @e at @e run setblock ~ ~ ~ stone"),
                 ("execute @e ~ ~ ~ execute @e[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone", "execute at @e at @e[name=Carl] run setblock ~ ~ ~ stone"),
                 ("execute @e ~ ~ ~ execute @e 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @e at @e positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 ("execute @e ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @e at @e[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 ("execute @e 1 ~-1 1 execute @e ~ ~ ~ setblock ~ ~ ~ stone", "execute at @e positioned 1 ~-1 1 at @e run setblock ~ ~ ~ stone"),
                 ("execute @e 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone", "execute at @e positioned 1 ~-1 1 at @e[name=Carl] run setblock ~ ~ ~ stone"),
                 ("execute @e 1 ~-1 1 execute @e 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @e positioned 1 ~-1 1 at @e positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 ("execute @e 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @e positioned 1 ~-1 1 at @e[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 ("execute @e[tag=Carl] ~ ~ ~ execute @e ~ ~ ~ setblock ~ ~ ~ stone", "execute at @e[tag=Carl] at @e run setblock ~ ~ ~ stone"),
                 ("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone", "execute at @e[tag=Carl] at @e[name=Carl] run setblock ~ ~ ~ stone"),
                 ("execute @e[tag=Carl] ~ ~ ~ execute @e 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @e[tag=Carl] at @e positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 ("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @e[tag=Carl] at @e[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e ~ ~ ~ setblock ~ ~ ~ stone", "execute at @e[tag=Carl] positioned 1 ~-1 1 at @e run setblock ~ ~ ~ stone"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ setblock ~ ~ ~ stone", "execute at @e[tag=Carl] positioned 1 ~-1 1 at @e[name=Carl] run setblock ~ ~ ~ stone"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @e[tag=Carl] positioned 1 ~-1 1 at @e positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 setblock ~ ~ ~ stone", "execute at @e[tag=Carl] positioned 1 ~-1 1 at @e[name=Carl] positioned 1 ~-1 1 run setblock ~ ~ ~ stone"),

                 # canAs and canAt
                 ("execute @e ~ ~ ~ function abc:def", "execute as @e at @s run function abc:def"),
                 ("execute @e[name=Carl] ~ ~ ~ function abc:def", "execute as @e[name=Carl] at @s run function abc:def"),
                 ("execute @e 1 ~-1 1 function abc:def", "execute as @e at @s positioned 1 ~-1 1 run function abc:def"),
                 ("execute @e[name=Carl] 1 ~-1 1 function abc:def", "execute as @e[name=Carl] at @s positioned 1 ~-1 1 run function abc:def"),

                 ("execute @e ~ ~ ~ execute @e ~ ~ ~ function abc:def", "execute at @e as @e at @s run function abc:def"),
                 ("execute @e ~ ~ ~ execute @e[name=Carl] ~ ~ ~ function abc:def", "execute at @e as @e[name=Carl] at @s run function abc:def"),
                 ("execute @e ~ ~ ~ execute @e 1 ~-1 1 function abc:def", "execute at @e as @e at @s positioned 1 ~-1 1 run function abc:def"),
                 ("execute @e ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 function abc:def", "execute at @e as @e[name=Carl] at @s positioned 1 ~-1 1 run function abc:def"),

                 ("execute @e 1 ~-1 1 execute @e ~ ~ ~ function abc:def", "execute at @e positioned 1 ~-1 1 as @e at @s run function abc:def"),
                 ("execute @e 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ function abc:def", "execute at @e positioned 1 ~-1 1 as @e[name=Carl] at @s run function abc:def"),
                 ("execute @e 1 ~-1 1 execute @e 1 ~-1 1 function abc:def", "execute at @e positioned 1 ~-1 1 as @e at @s positioned 1 ~-1 1 run function abc:def"),
                 ("execute @e 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 function abc:def", "execute at @e positioned 1 ~-1 1 as @e[name=Carl] at @s positioned 1 ~-1 1 run function abc:def"),

                 ("execute @e[tag=Carl] ~ ~ ~ execute @e ~ ~ ~ function abc:def", "execute at @e[tag=Carl] as @e at @s run function abc:def"),
                 ("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] ~ ~ ~ function abc:def", "execute at @e[tag=Carl] as @e[name=Carl] at @s run function abc:def"),
                 ("execute @e[tag=Carl] ~ ~ ~ execute @e 1 ~-1 1 function abc:def", "execute at @e[tag=Carl] as @e at @s positioned 1 ~-1 1 run function abc:def"),
                 ("execute @e[tag=Carl] ~ ~ ~ execute @e[name=Carl] 1 ~-1 1 function abc:def", "execute at @e[tag=Carl] as @e[name=Carl] at @s positioned 1 ~-1 1 run function abc:def"),

                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e ~ ~ ~ function abc:def", "execute at @e[tag=Carl] positioned 1 ~-1 1 as @e at @s run function abc:def"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] ~ ~ ~ function abc:def", "execute at @e[tag=Carl] positioned 1 ~-1 1 as @e[name=Carl] at @s run function abc:def"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e 1 ~-1 1 function abc:def", "execute at @e[tag=Carl] positioned 1 ~-1 1 as @e at @s positioned 1 ~-1 1 run function abc:def"),
                 ("execute @e[tag=Carl] 1 ~-1 1 execute @e[name=Carl] 1 ~-1 1 function abc:def", "execute at @e[tag=Carl] positioned 1 ~-1 1 as @e[name=Carl] at @s positioned 1 ~-1 1 run function abc:def"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 toggledownfall", "#~ execute at @e[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run toggledownfall ||| This command was removed"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 toggledownfall", "#~ execute at @e if block ~ ~ ~ diorite at @e[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run toggledownfall ||| This command was removed"),
                 ("execute Carl 1 ~-1 1 detect ~ ~-1 1 stone 1 function abc:def", "execute as Carl at @s positioned 1 ~-1 1 if block ~ ~-1 1 granite run function abc:def"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone -1 seed", "execute at @s if block ~ ~ ~ andesite run seed\n"
                                                                 "execute at @s if block ~ ~ ~ diorite run seed\n"
                                                                 "execute at @s if block ~ ~ ~ granite run seed\n"
                                                                 "execute at @s if block ~ ~ ~ polished_andesite run seed\n"
                                                                 "execute at @s if block ~ ~ ~ polished_diorite run seed\n"
                                                                 "execute at @s if block ~ ~ ~ polished_granite run seed\n"
                                                                 "execute at @s if block ~ ~ ~ stone run seed"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone * seed", "execute at @s if block ~ ~ ~ andesite run seed\n"
                                                                 "execute at @s if block ~ ~ ~ diorite run seed\n"
                                                                 "execute at @s if block ~ ~ ~ granite run seed\n"
                                                                 "execute at @s if block ~ ~ ~ polished_andesite run seed\n"
                                                                 "execute at @s if block ~ ~ ~ polished_diorite run seed\n"
                                                                 "execute at @s if block ~ ~ ~ polished_granite run seed\n"
                                                                 "execute at @s if block ~ ~ ~ stone run seed"),

                 # @s
                 # not canAs and not canAt
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 1 seed", "execute at @s if block ~ ~ ~ granite run seed"),
                 ("execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 seed", "execute at @s[name=Carl] if block ~ ~ ~ granite run seed"),
                 ("execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 seed", "execute at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),
                 ("execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 seed", "execute at @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),

                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s ~ ~ ~ detect ~ ~ ~ stone 1 seed", "execute at @s if block ~ ~ ~ diorite if block ~ ~ ~ granite run seed"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 seed", "execute at @s if block ~ ~ ~ diorite at @s[name=Carl] if block ~ ~ ~ granite run seed"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 seed", "execute at @s if block ~ ~ ~ diorite positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 seed", "execute at @s if block ~ ~ ~ diorite at @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),

                 # canAs and not canAt
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 1 say hi", "execute at @s if block ~ ~ ~ granite run say hi"),
                 ("execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 say hi", "execute at @s[name=Carl] if block ~ ~ ~ granite run say hi"),
                 ("execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi", "execute at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),
                 ("execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi", "execute at @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),

                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s ~ ~ ~ detect ~ ~ ~ stone 1 say hi", "execute at @s if block ~ ~ ~ diorite if block ~ ~ ~ granite run say hi"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 say hi", "execute at @s if block ~ ~ ~ diorite at @s[name=Carl] if block ~ ~ ~ granite run say hi"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi", "execute at @s if block ~ ~ ~ diorite positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi", "execute at @s if block ~ ~ ~ diorite at @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),

                 # not canAs and canAt
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone", "execute at @s if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 ("execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone", "execute at @s[name=Carl] if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 ("execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone", "execute at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),
                 ("execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone", "execute at @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),

                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone", "execute at @s if block ~ ~ ~ diorite if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone", "execute at @s if block ~ ~ ~ diorite at @s[name=Carl] if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone", "execute at @s if block ~ ~ ~ diorite positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone", "execute at @s if block ~ ~ ~ diorite at @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),

                 # canAs and canAt
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def", "execute at @s if block ~ ~ ~ granite run function abc:def"),
                 ("execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def", "execute at @s[name=Carl] if block ~ ~ ~ granite run function abc:def"),
                 ("execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def", "execute at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),
                 ("execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def", "execute at @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),

                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def", "execute at @s if block ~ ~ ~ diorite if block ~ ~ ~ granite run function abc:def"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def", "execute at @s if block ~ ~ ~ diorite at @s[name=Carl] if block ~ ~ ~ granite run function abc:def"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def", "execute at @s if block ~ ~ ~ diorite positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),
                 ("execute @s ~ ~ ~ detect ~ ~ ~ stone 3 execute @s[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def", "execute at @s if block ~ ~ ~ diorite at @s[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),

                 # @e
                 # not canAs and not canAt
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 1 seed", "execute at @e if block ~ ~ ~ granite run seed"),
                 ("execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 seed", "execute at @e[name=Carl] if block ~ ~ ~ granite run seed"),
                 ("execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 seed", "execute at @e positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),
                 ("execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 seed", "execute at @e[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),

                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e ~ ~ ~ detect ~ ~ ~ stone 1 seed", "execute at @e if block ~ ~ ~ diorite at @e if block ~ ~ ~ granite run seed"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 seed", "execute at @e if block ~ ~ ~ diorite at @e[name=Carl] if block ~ ~ ~ granite run seed"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 seed", "execute at @e if block ~ ~ ~ diorite at @e positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 seed", "execute at @e if block ~ ~ ~ diorite at @e[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run seed"),

                 # canAs and not canAt
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 1 say hi", "execute as @e at @s if block ~ ~ ~ granite run say hi"),
                 ("execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 say hi", "execute as @e[name=Carl] at @s if block ~ ~ ~ granite run say hi"),
                 ("execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi", "execute as @e at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),
                 ("execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi", "execute as @e[name=Carl] at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),

                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e ~ ~ ~ detect ~ ~ ~ stone 1 say hi", "execute at @e if block ~ ~ ~ diorite as @e at @s if block ~ ~ ~ granite run say hi"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 say hi", "execute at @e if block ~ ~ ~ diorite as @e[name=Carl] at @s if block ~ ~ ~ granite run say hi"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi", "execute at @e if block ~ ~ ~ diorite as @e at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 say hi", "execute at @e if block ~ ~ ~ diorite as @e[name=Carl] at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run say hi"),

                 # not canAs and canAt
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone", "execute at @e if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 ("execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone", "execute at @e[name=Carl] if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 ("execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone", "execute at @e positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),
                 ("execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone", "execute at @e[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),

                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone", "execute at @e if block ~ ~ ~ diorite at @e if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 setblock ~ ~ ~ stone", "execute at @e if block ~ ~ ~ diorite at @e[name=Carl] if block ~ ~ ~ granite run setblock ~ ~ ~ stone"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone", "execute at @e if block ~ ~ ~ diorite at @e positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 setblock ~ ~ ~ stone", "execute at @e if block ~ ~ ~ diorite at @e[name=Carl] positioned 1 ~-1 1 if block 1 ~-1 1 granite run setblock ~ ~ ~ stone"),

                 # canAs and canAt
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def", "execute as @e at @s if block ~ ~ ~ granite run function abc:def"),
                 ("execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def", "execute as @e[name=Carl] at @s if block ~ ~ ~ granite run function abc:def"),
                 ("execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def", "execute as @e at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),
                 ("execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def", "execute as @e[name=Carl] at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),

                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def", "execute at @e if block ~ ~ ~ diorite as @e at @s if block ~ ~ ~ granite run function abc:def"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] ~ ~ ~ detect ~ ~ ~ stone 1 function abc:def", "execute at @e if block ~ ~ ~ diorite as @e[name=Carl] at @s if block ~ ~ ~ granite run function abc:def"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def", "execute at @e if block ~ ~ ~ diorite as @e at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"),
                 ("execute @e ~ ~ ~ detect ~ ~ ~ stone 3 execute @e[name=Carl] 1 ~-1 1 detect 1 ~-1 1 stone 1 function abc:def", "execute at @e if block ~ ~ ~ diorite as @e[name=Carl] at @s positioned 1 ~-1 1 if block 1 ~-1 1 granite run function abc:def"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("fill 1 ~-1 ~1 1 ~-1 ~1 stone", "fill 1 ~-1 ~1 1 ~-1 ~1 stone"),
                 ("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1", "fill 1 ~-1 ~1 1 ~-1 ~1 granite"),
                 ("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 destroy", "fill 1 ~-1 ~1 1 ~-1 ~1 granite destroy"),
                 ("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 destroy {abc:def}", "fill 1 ~-1 ~1 1 ~-1 ~1 granite{abc:def} destroy"),
                 ("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 hollow", "fill 1 ~-1 ~1 1 ~-1 ~1 granite hollow"),
                 ("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 hollow {abc:def}", "fill 1 ~-1 ~1 1 ~-1 ~1 granite{abc:def} hollow"),
                 ("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 keep", "fill 1 ~-1 ~1 1 ~-1 ~1 granite keep"),
                 ("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 keep {abc:def}", "fill 1 ~-1 ~1 1 ~-1 ~1 granite{abc:def} keep"),
                 ("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 outline", "fill 1 ~-1 ~1 1 ~-1 ~1 granite outline"),
                 ("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 outline {abc:def}", "fill 1 ~-1 ~1 1 ~-1 ~1 granite{abc:def} outline"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace", "fill 1 ~-1 ~1 1 ~-1 ~1 granite replace"),
                 ("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace stone", "#~ The splitting of this command (fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace stone) can produce different results if used with stats\n"
                                                                  "fill 1 ~-1 ~1 1 ~-1 ~1 granite replace andesite\n"
                                                                  "fill 1 ~-1 ~1 1 ~-1 ~1 granite replace diorite\n"
                                                                  "fill 1 ~-1 ~1 1 ~-1 ~1 granite replace granite\n"
                                                                  "fill 1 ~-1 ~1 1 ~-1 ~1 granite replace polished_andesite\n"
                                                                  "fill 1 ~-1 ~1 1 ~-1 ~1 granite replace polished_diorite\n"
                                                                  "fill 1 ~-1 ~1 1 ~-1 ~1 granite replace polished_granite\n"
                                                                  "fill 1 ~-1 ~1 1 ~-1 ~1 granite replace stone"),
                 ("fill 1 ~-1 ~1 1 ~-1 ~1 stone 1 replace stone 2", "fill 1 ~-1 ~1 1 ~-1 ~1 granite replace polished_granite"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("function custom:example/test", "function custom:example/test"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("function custom:example/test if @s", "function custom:example/test"),
                 ("function custom:example/test unless @s", "#~ function custom:example/test unless @s ||| unless @s will always fail"),
                 ("function custom:example/test if @e", "execute if entity @e run function custom:example/test"),
                 ("function custom:example/test unless @e", "execute unless entity @e run function custom:example/test"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("gamemode 0", "gamemode survival"),
                 ("gamemode 1", "gamemode creative"),
                 ("gamemode 2", "gamemode adventure"),
                 ("gamemode 3", "gamemode spectator"),
                 ("gamemode 0 @s", "gamemode survival @s"),
                 ("gamemode 1 @s", "gamemode creative @s"),
                 ("gamemode 2 @s", "gamemode adventure @s"),
                 ("gamemode 3 @s", "gamemode spectator @s"),
                 ("gamemode s", "gamemode survival"),
                 ("gamemode c", "gamemode creative"),
                 ("gamemode a", "gamemode adventure"),
                 ("gamemode sp", "gamemode spectator"),
                 ("gamemode s @s", "gamemode survival @s"),
                 ("gamemode c @s", "gamemode creative @s"),
                 ("gamemode a @s", "gamemode adventure @s"),
                 ("gamemode sp @s", "gamemode spectator @s"),
                 ("gamemode survival", "gamemode survival"),
                 ("gamemode creative", "gamemode creative"),
                 ("gamemode adventure", "gamemode adventure"),
                 ("gamemode spectator", "gamemode spectator"),
                 ("gamemode survival @s", "gamemode survival @s"),
                 ("gamemode creative @s", "gamemode creative @s"),
                 ("gamemode adventure @s", "gamemode adventure @s"),
                 ("gamemode spectator @s", "gamemode spectator @s"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
        self.assertStats()


class GameRule(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["gamerule", ["announceAdvancements", "commandBlockOutput", "disableElytraMovementCheck", "doDaylightCycle", "doEntityDrops", "doFireTick", "doLimitedCrafting", "doMobLoot", "doMobSpawning", "doTileDrops", "doWeatherCycle", "keepInventory", "logAdminCommands", "mobGriefing", "naturalRegeneration", "reducedDebugInfo", "sendCommandFeedback", "showDeathMessages", "spectatorsGenerateChunks"], ["true", "false"]], optional=1)
        perms.update(generate_perms(["gamerule", ["maxCommandChainLength", "maxEntityCramming", "randomTickSpeed", "spawnRadius"], "42"], optional=1))
        perms.update(generate_perms(["gamerule", "gameLoopFunction", "main:main"], optional=1))
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("gamerule",
                 "gamerule aaaaaaaaaaaaaaaa"
                 "gamerule gameLoopFunction aaaaaaaaa"
                 "gamerule gameLoopFunction main:main ImNotSupposedToBeHere",

                 "gamerule announceAdvancements 42",
                 "gamerule commandBlockOutput 42",
                 "gamerule disableElytraMovementCheck 42",
                 "gamerule doDaylightCycle 42",
                 "gamerule doEntityDrops 42",
                 "gamerule doFireTick 42",
                 "gamerule doLimitedCrafting 42",
                 "gamerule doMobLoot 42",
                 "gamerule doMobSpawning 42",
                 "gamerule doTileDrops 42",
                 "gamerule doWeatherCycle 42",
                 "gamerule keepInventory 42",
                 "gamerule logAdminCommands 42",
                 "gamerule mobGriefing 42",
                 "gamerule naturalRegeneration 42",
                 "gamerule reducedDebugInfo 42",
                 "gamerule sendCommandFeedback 42",
                 "gamerule showDeathMessages 42",
                 "gamerule spectatorsGenerateChunks 42",

                 "gamerule maxCommandChainLength true",
                 "gamerule maxEntityCramming true",
                 "gamerule randomTickSpeed true",
                 "gamerule spawnRadius true")
        for perm in perms:
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("gamerule gameLoopFunction", "gamerule gameLoopFunction"),
                 ("gamerule sendcoMMandfeedback TrUe", "gamerule sendCommandFeedback true"),
                 ("gamerule gameloopFunction main:main", "gamerule gameLoopFunction main:main"),
                 ("gamerule custom", "#~ gamerule custom ||| Custom gamerules are no longer supported"),
                 ("gamerule custom val", "#~ gamerule custom val ||| Custom gamerules are no longer supported"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("give @s stone", "give @s stone"),
                 ("give @s stone 1", "give @s stone"),
                 ("give @s stone 11", "give @s stone 11"),
                 ("give @s stone 1 1", "give @s granite"),
                 ("give @s stone 11 1", "give @s granite 11"),
                 ("give @s stone 11 1 {abc:def}", "give @s granite{abc:def} 11"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("?", "help"),
                 ("help", "help"),)
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = [("{} {}".format(command, arg), "help {}".format(arg)) for arg in converter.Globals.commands+map(str, xrange(1, 9)) for command in ("help", "?")]
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("kick p_name Because", "kick p_name Because"),
                 ("kick p_name Because I said so", "kick p_name Because I said so"),
                 ("kick p_name", "kick p_name"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("kill p_name", "kill p_name"),
                 ("kill", "kill @s"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("list uuids", "list uuids"),
                 ("list", "list"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("locate Monument", "locate Monument"),
                 ("locate Mansion", "locate Mansion"),
                 ("locate Village", "locate Village"),
                 ("locate Mineshaft", "locate Mineshaft"),
                 ("locate Fortress", "locate Fortress"),
                 ("locate EndCity", "locate EndCity"),
                 ("locate Stronghold", "locate Stronghold"),
                 ("locate Temple", "#~ The splitting of this command (locate Temple) can produce different results if used with stats\n"
                                   "locate Desert_Pyramid\n"
                                   "locate Igloo\n"
                                   "locate Jungle_Pyramid\n"
                                   "locate Swamp_Hut"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("me action", "me action"),
                 ("me more actions", "me more actions"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("op @s", "op @s"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("pardon p_name", "pardon p_name"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("pardon-ip 127.0.0.1", "pardon-ip 127.0.0.1"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
        self.assertStats()


class Particle(TestBase):
    def test_syntax1_ok(self):
        perms = generate_perms(["particle", list(converter.Globals.particles.keys()), coord(), coord(), coord(), "1", "2", "3", "1", "10", "force", "@s"], optional=3)
        perms.update(generate_perms(["particle", ["blockdust", "blockcrack", "fallingdust", "reddust"], coord(), coord(), coord(), "1", "2", "3", "1", "10", "force", "@s", "1"], optional=4))
        perms.update(generate_perms(["particle", "iconcrack", coord(), coord(), coord(), "1", "2", "3", "1", "10", "force", "@s", "2", "3"], optional=5))
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax1_nok(self):
        perms = ("particle",
                 "particle aaaa 1 ~-1 ~1 1 2 3 0 10 force @s",
                 "particle wake",
                 "particle wake a ~-1 ~1 1 2 3 0 10 force @s",
                 "particle wake 1",
                 "particle wake 1 aaa ~1 1 2 3 0 10 force @s",
                 "particle wake 1 ~-1 ~1",
                 "particle wake 1 ~-1 aa 1 2 3 0 10 force @s",
                 "particle wake 1 ~-1 ~1 1",
                 "particle wake 1 ~-1 ~1 a 2 3 0 10 force @s",
                 "particle wake 1 ~-1 ~1 1 2",
                 "particle wake 1 ~-1 ~1 1 a 3 0 10 force @s",
                 "particle wake 1 ~-1 ~1 1 2 3",
                 "particle wake 1 ~-1 ~1 1 2 a 0 10 force @s",
                 "particle wake 1 ~-1 ~1 1 2 3 a 10 force @s",
                 "particle wake 1 ~-1 ~1 1 2 3 0 aa force @s",
                 "particle wake 1 ~-1 ~1 1 2 3 0 10 force @c",

                 "particle blockdust 1 ~-1 ~1 1 2 3 0 10 force @s a",
                 "particle blockdust 1 ~-1 ~1 1 2 3 0 10 force @s 256",
                 "particle blockdust 1 ~-1 ~1 1 2 3 0 10 force @s 1 1",

                 "particle iconcrack 1 ~-1 ~1 1 2 3 0 10 force @s a 1",
                 "particle iconcrack 1 ~-1 ~1 1 2 3 0 10 force @s 1 a",
                 "particle iconcrack 1 ~-1 ~1 1 2 3 0 10 force @s 1 1 1",
                 "particle iconcrack 1 ~-1 ~1 1 2 3 0 10 force @s 253 1",
                 "particle iconcrack 1 ~-1 ~1 1 2 3 0 10 force @s 1 454")
        for perm in perms:
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("particle take 1 ~-1 ~1 1 2 3 0", "#~ particle take 1 ~-1 ~1 1 2 3 0 0 ||| The particle take was removed"),
                 ("particle take 1 ~-1 ~1 0 0 0 0", "#~ particle take 1 ~-1 ~1 ||| The particle take was removed"),

                 ("particle wake 1 ~-1 ~1 0 0 0 0", "particle fishing 1 ~-1 ~1"),
                 ("particle wake 1 ~-1 ~1 1 2 3 0 10 normal @s", "particle fishing 1 ~-1 ~1 1 2 3 0 10"),
                 ("particle wake 1 ~-1 ~1 1 2 3 0 10 force @s", "particle fishing 1 ~-1 ~1 1 2 3 0 10 force"),
                 ("particle wake 1 ~-1 ~1 1 2 3 0 10 force @a", "particle fishing 1 ~-1 ~1 1 2 3 0 10 force @a"),
                 ("particle wake 1 ~-1 ~1 1 2 3 0 10 normal @a", "particle fishing 1 ~-1 ~1 1 2 3 0 10 normal @a"),
                 ("particle wake 1 ~-1 ~1 1 2 3 0 10 force @a 1", "particle fishing 1 ~-1 ~1 1 2 3 0 10 force @a"),

                 ("particle blockdust 1 ~-1 ~1 1 2 3 0 10 normal @s 1", "particle block stone 1 ~-1 ~1 1 2 3 0 10"),
                 ("particle blockdust 1 ~-1 ~1 0 0 0 0 0 normal @s 1", "particle block stone 1 ~-1 ~1"),
                 ("particle blockdust 1 ~-1 ~1 1 2 3 0 10 normal @s 4097", "particle block granite 1 ~-1 ~1 1 2 3 0 10"),

                 ("particle iconcrack 1 ~-1 ~1 1 2 3 0 10 normal @s 1", "particle item stone 1 ~-1 ~1 1 2 3 0 10"),
                 ("particle iconcrack 1 ~-1 ~1 0 0 0 0 0 normal @s 1", "particle item stone 1 ~-1 ~1"),
                 ("particle iconcrack 1 ~-1 ~1 1 2 3 0 10 normal @s 1 0", "particle item stone 1 ~-1 ~1 1 2 3 0 10"),
                 ("particle iconcrack 1 ~-1 ~1 1 2 3 0 10 normal @s 1 1", "particle item granite 1 ~-1 ~1 1 2 3 0 10"),
                 ("particle iconcrack 1 ~-1 ~1 1 2 3 0 10 normal @s 256", "particle item iron_shovel 1 ~-1 ~1 1 2 3 0 10"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("playsound sound master @s", "playsound sound master @s"),
                 ("playsound sound music @s", "playsound sound music @s"),
                 ("playsound sound record @s", "playsound sound record @s"),
                 ("playsound sound weather @s", "playsound sound weather @s"),
                 ("playsound sound block @s", "playsound sound block @s"),
                 ("playsound sound hostile @s", "playsound sound hostile @s"),
                 ("playsound sound neutral @s", "playsound sound neutral @s"),
                 ("playsound sound player @s", "playsound sound player @s"),
                 ("playsound sound ambient @s", "playsound sound ambient @s"),
                 ("playsound sound voice @s", "playsound sound voice @s"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("playsound sound master @s 1 ~-1 ~1 0.5", "playsound sound master @s 1 ~-1 ~1 0.5"),
                 ("playsound sound master @s 1 ~-1 ~1 0.5 0.6", "playsound sound master @s 1 ~-1 ~1 0.5 0.6"),
                 ("playsound sound master @s 1 ~-1 ~1 0.5 0.6 0.7", "playsound sound master @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 ("playsound sound music @s 1 ~-1 ~1 0.5", "playsound sound music @s 1 ~-1 ~1 0.5"),
                 ("playsound sound music @s 1 ~-1 ~1 0.5 0.6", "playsound sound music @s 1 ~-1 ~1 0.5 0.6"),
                 ("playsound sound music @s 1 ~-1 ~1 0.5 0.6 0.7", "playsound sound music @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 ("playsound sound record @s 1 ~-1 ~1 0.5", "playsound sound record @s 1 ~-1 ~1 0.5"),
                 ("playsound sound record @s 1 ~-1 ~1 0.5 0.6", "playsound sound record @s 1 ~-1 ~1 0.5 0.6"),
                 ("playsound sound record @s 1 ~-1 ~1 0.5 0.6 0.7", "playsound sound record @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 ("playsound sound weather @s 1 ~-1 ~1 0.5", "playsound sound weather @s 1 ~-1 ~1 0.5"),
                 ("playsound sound weather @s 1 ~-1 ~1 0.5 0.6", "playsound sound weather @s 1 ~-1 ~1 0.5 0.6"),
                 ("playsound sound weather @s 1 ~-1 ~1 0.5 0.6 0.7", "playsound sound weather @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 ("playsound sound block @s 1 ~-1 ~1 0.5", "playsound sound block @s 1 ~-1 ~1 0.5"),
                 ("playsound sound block @s 1 ~-1 ~1 0.5 0.6", "playsound sound block @s 1 ~-1 ~1 0.5 0.6"),
                 ("playsound sound block @s 1 ~-1 ~1 0.5 0.6 0.7", "playsound sound block @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 ("playsound sound hostile @s 1 ~-1 ~1 0.5", "playsound sound hostile @s 1 ~-1 ~1 0.5"),
                 ("playsound sound hostile @s 1 ~-1 ~1 0.5 0.6", "playsound sound hostile @s 1 ~-1 ~1 0.5 0.6"),
                 ("playsound sound hostile @s 1 ~-1 ~1 0.5 0.6 0.7", "playsound sound hostile @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 ("playsound sound neutral @s 1 ~-1 ~1 0.5", "playsound sound neutral @s 1 ~-1 ~1 0.5"),
                 ("playsound sound neutral @s 1 ~-1 ~1 0.5 0.6", "playsound sound neutral @s 1 ~-1 ~1 0.5 0.6"),
                 ("playsound sound neutral @s 1 ~-1 ~1 0.5 0.6 0.7", "playsound sound neutral @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 ("playsound sound player @s 1 ~-1 ~1 0.5", "playsound sound player @s 1 ~-1 ~1 0.5"),
                 ("playsound sound player @s 1 ~-1 ~1 0.5 0.6", "playsound sound player @s 1 ~-1 ~1 0.5 0.6"),
                 ("playsound sound player @s 1 ~-1 ~1 0.5 0.6 0.7", "playsound sound player @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 ("playsound sound ambient @s 1 ~-1 ~1 0.5", "playsound sound ambient @s 1 ~-1 ~1 0.5"),
                 ("playsound sound ambient @s 1 ~-1 ~1 0.5 0.6", "playsound sound ambient @s 1 ~-1 ~1 0.5 0.6"),
                 ("playsound sound ambient @s 1 ~-1 ~1 0.5 0.6 0.7", "playsound sound ambient @s 1 ~-1 ~1 0.5 0.6 0.7"),
                 ("playsound sound voice @s 1 ~-1 ~1 0.5", "playsound sound voice @s 1 ~-1 ~1 0.5"),
                 ("playsound sound voice @s 1 ~-1 ~1 0.5 0.6", "playsound sound voice @s 1 ~-1 ~1 0.5 0.6"),
                 ("playsound sound voice @s 1 ~-1 ~1 0.5 0.6 0.7", "playsound sound voice @s 1 ~-1 ~1 0.5 0.6 0.7"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("publish", "publish"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("recipe give @s recipeName", "recipe give @s recipeName"),
                 ("recipe give @s *", "recipe give @s *"),
                 ("recipe take @s recipeName", "recipe take @s recipeName"),
                 ("recipe take @s *", "recipe take @s *"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("reload", "reload"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("replaceitem block 1 ~-1 ~1 slot.armor.chest stone", "replaceitem block 1 ~-1 ~1 armor.chest stone"),
                 ("replaceitem block 1 ~-1 ~1 slot.armor.chest stone 5", "replaceitem block 1 ~-1 ~1 armor.chest stone 5"),
                 ("replaceitem block 1 ~-1 ~1 slot.armor.chest stone 5 1", "replaceitem block 1 ~-1 ~1 armor.chest granite 5"),
                 ("replaceitem block 1 ~-1 ~1 slot.armor.chest stone 5 1 {abc:def}", "replaceitem block 1 ~-1 ~1 armor.chest granite{abc:def} 5"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
        self.assertStats()

    def test_syntax2_ok(self):
        perms = generate_perms(["replaceitem", "entity", "@s", list(converter.Globals.slots), "stone", "5", "1", "{abc:def}"], optional=3)
        for perm in perms:
            self.decide(perm)
        self.assertStats()

    def test_syntax2_nok(self):
        perms = ("replaceitem",
                 "replaceitem aaaaaa @s slot.armor.chest stone 5 1 {abc:def}",
                 "replaceitem entity",
                 "replaceitem entity @c slot.armor.chest stone 5 1 {abc:def}",
                 "replaceitem entity @s",
                 "replaceitem entity @s aaaaaaaaaaaaaaaa stone 5 1 {abc:def}",
                 "replaceitem entity @s slot.armor.chest",
                 "replaceitem entity @s slot.armor.chest aaaaa 5 1 {abc:def}",
                 "replaceitem entity @s slot.armor.chest stone a 1 {abc:def}",
                 "replaceitem entity @s slot.armor.chest stone 5 a {abc:def}",
                 "replaceitem entity @s slot.armor.chest stone 5 1 aaaaaaaaa",
                 "replaceitem entity @s slot.armor.chest stone 5 1 {abc:def} ImNotSupposedToBeHere")
        for perm in perms:
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("replaceitem entity @s slot.armor.chest stone", "replaceitem entity @s armor.chest stone"),
                 ("replaceitem entity @s slot.armor.chest stone 5", "replaceitem entity @s armor.chest stone 5"),
                 ("replaceitem entity @s slot.armor.chest stone 5 1", "replaceitem entity @s armor.chest granite 5"),
                 ("replaceitem entity @s slot.armor.chest stone 5 1 {abc:def}", "replaceitem entity @s armor.chest granite{abc:def} 5"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("save-all", "save-all"),
                 ("save-all flush", "save-all flush"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("save-off", "save-off"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("save-on", "save-on"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("say hi", "say hi"),
                 ("say hi hi", "say hi hi"),
                 ("say hi @e[c=1]", "say hi @e[limit=1,sort=nearest]"),
                 ("say hi @e[k=1]", "say hi @e[k=1]"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("scoreboard objectives list", "scoreboard objectives list"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("scoreboard objectives add anObjective dummy", "scoreboard objectives add anObjective dummy"),
                 ("scoreboard objectives add anObjective DuMmY", "scoreboard objectives add anObjective dummy"),
                 ("scoreboard objectives add anObjective dummy displayName", "scoreboard objectives add anObjective dummy displayName"),

                 ("scoreboard objectives add anObjective stat.mineBlock.minecraft.tnt", "scoreboard objectives add anObjective minecraft.mined:minecraft.tnt"),
                 ("scoreboard objectives add anObjective stat.mineBlock.minecraft.stone", "#~ This command was split, because the criteria was split. You need to split all the scoreboards that refer to this objective\n"
                                                                                          "scoreboard objectives add anObjective minecraft.mined:minecraft.andesite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.mined:minecraft.diorite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.mined:minecraft.granite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.mined:minecraft.polished_andesite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.mined:minecraft.polished_diorite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.mined:minecraft.polished_granite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.mined:minecraft.stone"),

                 ("scoreboard objectives add anObjective stat.craftItem.minecraft.tnt", "scoreboard objectives add anObjective minecraft.crafted:minecraft.tnt"),
                 ("scoreboard objectives add anObjective stat.craftItem.minecraft.stone", "#~ This command was split, because the criteria was split. You need to split all the scoreboards that refer to this objective\n"
                                                                                          "scoreboard objectives add anObjective minecraft.crafted:minecraft.andesite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.crafted:minecraft.diorite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.crafted:minecraft.granite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.crafted:minecraft.polished_andesite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.crafted:minecraft.polished_diorite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.crafted:minecraft.polished_granite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.crafted:minecraft.stone"),

                 ("scoreboard objectives add anObjective stat.useItem.minecraft.tnt", "scoreboard objectives add anObjective minecraft.used:minecraft.tnt"),
                 ("scoreboard objectives add anObjective stat.useItem.minecraft.stone", "#~ This command was split, because the criteria was split. You need to split all the scoreboards that refer to this objective\n"
                                                                                          "scoreboard objectives add anObjective minecraft.used:minecraft.andesite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.used:minecraft.diorite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.used:minecraft.granite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.used:minecraft.polished_andesite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.used:minecraft.polished_diorite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.used:minecraft.polished_granite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.used:minecraft.stone"),

                 ("scoreboard objectives add anObjective stat.breakItem.minecraft.elytra", "scoreboard objectives add anObjective minecraft.broken:minecraft.elytra"),

                 ("scoreboard objectives add anObjective stat.pickup.minecraft.tnt", "scoreboard objectives add anObjective minecraft.picked_up:minecraft.tnt"),
                 ("scoreboard objectives add anObjective stat.pickup.minecraft.stone", "#~ This command was split, because the criteria was split. You need to split all the scoreboards that refer to this objective\n"
                                                                                          "scoreboard objectives add anObjective minecraft.picked_up:minecraft.andesite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.picked_up:minecraft.diorite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.picked_up:minecraft.granite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.picked_up:minecraft.polished_andesite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.picked_up:minecraft.polished_diorite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.picked_up:minecraft.polished_granite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.picked_up:minecraft.stone"),

                 ("scoreboard objectives add anObjective stat.drop.minecraft.tnt", "scoreboard objectives add anObjective minecraft.dropped:minecraft.tnt"),
                 ("scoreboard objectives add anObjective stat.drop.minecraft.stone", "#~ This command was split, because the criteria was split. You need to split all the scoreboards that refer to this objective\n"
                                                                                          "scoreboard objectives add anObjective minecraft.dropped:minecraft.andesite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.dropped:minecraft.diorite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.dropped:minecraft.granite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.dropped:minecraft.polished_andesite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.dropped:minecraft.polished_diorite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.dropped:minecraft.polished_granite\n"
                                                                                          "scoreboard objectives add anObjective minecraft.dropped:minecraft.stone"),

                 ("scoreboard objectives add anObjective stat.killEntity.ElderGuardian", "scoreboard objectives add anObjective minecraft.killed:minecraft.elder_guardian"),
                 ("scoreboard objectives add anObjective stat.entityKilledBy.ElderGuardian", "scoreboard objectives add anObjective minecraft.killed_by:minecraft.elder_guardian"),
                 ("scoreboard objectives add anObjective stat.animalsBred", "scoreboard objectives add anObjective minecraft.custom:minecraft.animals_bred"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = (("scoreboard objectives remove anObjective", "scoreboard objectives remove anObjective"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax4_convert(self):
        tests = [("scoreboard objectives setdisplay {}{}".format(bar, option), "scoreboard objectives setdisplay {}{}".format(bar, option)) for bar in Scoreboard.sidebars for option in ("", " anObjective")]
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax5_convert(self):
        tests = (("scoreboard players list", "scoreboard players list"),
                 ("scoreboard players list @s", "scoreboard players list @s"),
                 ("scoreboard players list *", "#~ There is no way to convert \'scoreboard players list *\' because of the \'*\'"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax6_convert(self):
        tests = (("scoreboard players set @s anObjective 1", "scoreboard players set @s anObjective 1"),
                 ("scoreboard players set @s anObjective 1 {abc:def}", "scoreboard players set @s[nbt={abc:def}] anObjective 1"),
                 ("scoreboard players set Carl anObjective 1 {abc:def}", "scoreboard players set @p[name=Carl,nbt={abc:def}] anObjective 1"),
                 ("scoreboard players add @s anObjective 1", "scoreboard players add @s anObjective 1"),
                 ("scoreboard players add @s anObjective 1 {abc:def}", "scoreboard players add @s[nbt={abc:def}] anObjective 1"),
                 ("scoreboard players add Carl anObjective 1 {abc:def}", "scoreboard players add @p[name=Carl,nbt={abc:def}] anObjective 1"),
                 ("scoreboard players remove @s anObjective 1", "scoreboard players remove @s anObjective 1"),
                 ("scoreboard players remove @s anObjective 1 {abc:def}", "scoreboard players remove @s[nbt={abc:def}] anObjective 1"),
                 ("scoreboard players remove Carl anObjective 1 {abc:def}", "scoreboard players remove @p[name=Carl,nbt={abc:def}] anObjective 1"),

                 ("scoreboard players set * anObjective 1", "scoreboard players set * anObjective 1"),
                 ("scoreboard players set * anObjective 1 {abc:def}", "#~ There is no way to convert \'scoreboard players set * anObjective 1 {abc:def}\' because of the \'*\'"),
                 ("scoreboard players add * anObjective 1", "scoreboard players add * anObjective 1"),
                 ("scoreboard players add * anObjective 1 {abc:def}", "#~ There is no way to convert \'scoreboard players add * anObjective 1 {abc:def}\' because of the \'*\'"),
                 ("scoreboard players remove * anObjective 1", "scoreboard players remove * anObjective 1"),
                 ("scoreboard players remove * anObjective 1 {abc:def}", "#~ There is no way to convert \'scoreboard players remove * anObjective 1 {abc:def}\' because of the \'*\'"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax7_convert(self):
        tests = (("scoreboard players reset @s", "scoreboard players reset @s"),
                 ("scoreboard players reset @s anObjective", "scoreboard players reset @s anObjective"),
                 ("scoreboard players reset *", "scoreboard players reset *"),
                 ("scoreboard players reset * anObjective", "scoreboard players reset * anObjective"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax8_convert(self):
        tests = (("scoreboard players enable @s anObjective", "scoreboard players enable @s anObjective"),
                 ("scoreboard players enable * anObjective", "scoreboard players enable * anObjective"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax9_convert(self):
        tests = (("scoreboard players test @s anObjective 1", "execute if score @s anObjective matches 1.."),
                 ("scoreboard players test @s anObjective 1 *", "execute if score @s anObjective matches 1.."),
                 ("scoreboard players test @s anObjective 1 2", "execute if score @s anObjective matches 1..2"),
                 ("scoreboard players test @s anObjective * 2", "execute if score @s anObjective matches ..2"),
                 ("scoreboard players test @s anObjective * *", "execute if score @s anObjective matches -2147483648.."),
                 ("scoreboard players test @s anObjective *", "execute if score @s anObjective matches -2147483648.."),
                 ("scoreboard players test * anObjective 1 2", "#~ There is no way to convert \'scoreboard players test * anObjective 1 2\' because of the \'*\'"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax10_convert(self):
        tests = (("scoreboard players operation @s anObjective += @s aObjective", "scoreboard players operation @s anObjective += @s aObjective"),
                 ("scoreboard players operation * anObjective += @s aObjective", "#~ There is no way to convert \'scoreboard players operation * anObjective += @s aObjective\' because of the \'*\'"),
                 ("scoreboard players operation @s anObjective += * aObjective", "#~ There is no way to convert \'scoreboard players operation @s anObjective += * aObjective\' because of the \'*\'"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax11_convert(self):
        tests = (("scoreboard players tag @s add aTag", "tag @s add aTag"),
                 ("scoreboard players tag * add aTag", "#~ There is no way to convert \'scoreboard players tag * add aTag\' because of the \'*\'"),
                 ("scoreboard players tag @s add aTag {abc:def}", "tag @s[nbt={abc:def}] add aTag"),
                 ("scoreboard players tag * add aTag {abc:def}", "#~ There is no way to convert \'scoreboard players tag * add aTag {abc:def}\' because of the \'*\'"),
                 ("scoreboard players tag Carl add aTag {abc:def}", "tag @p[name=Carl,nbt={abc:def}] add aTag"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax12_convert(self):
        tests = (("scoreboard players tag @s list", "tag @s list"),
                 ("scoreboard players tag * list", "#~ There is no way to convert \'scoreboard players tag * list\' because of the \'*\'"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax13_convert(self):
        tests = (("scoreboard teams list", "team list"),
                 ("scoreboard teams list aName", "team list aName"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax14_convert(self):
        tests = (("scoreboard teams add aName", "team add aName"),
                 ("scoreboard teams add aName TeamName", "team add aName TeamName"),
                 ("scoreboard teams add aName Team Name", "team add aName Team Name"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax15_convert(self):
        tests = (("scoreboard teams join aName", "team join aName"),
                 ("scoreboard teams join aName @s", "team join aName @s"),
                 ("scoreboard teams join aName @s @e[c=1]", "team join aName @s @e[limit=1,sort=nearest]"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax16_convert(self):
        tests = (("scoreboard teams remove aName", "team remove aName"),
                 ("scoreboard teams empty aName", "team empty aName"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax17_convert(self):
        tests = (("scoreboard teams option aTeam color reset", "team option aTeam color reset"),
                 ("scoreboard teams option aTeam color aqua", "team option aTeam color aqua"),
                 ("scoreboard teams option aTeam color black", "team option aTeam color black"),
                 ("scoreboard teams option aTeam color blue", "team option aTeam color blue"),
                 ("scoreboard teams option aTeam color dark_aqua", "team option aTeam color dark_aqua"),
                 ("scoreboard teams option aTeam color dark_blue", "team option aTeam color dark_blue"),
                 ("scoreboard teams option aTeam color dark_gray", "team option aTeam color dark_gray"),
                 ("scoreboard teams option aTeam color dark_green", "team option aTeam color dark_green"),
                 ("scoreboard teams option aTeam color dark_purple", "team option aTeam color dark_purple"),
                 ("scoreboard teams option aTeam color dark_red", "team option aTeam color dark_red"),
                 ("scoreboard teams option aTeam color gold", "team option aTeam color gold"),
                 ("scoreboard teams option aTeam color gray", "team option aTeam color gray"),
                 ("scoreboard teams option aTeam color green", "team option aTeam color green"),
                 ("scoreboard teams option aTeam color light_purple", "team option aTeam color light_purple"),
                 ("scoreboard teams option aTeam color red", "team option aTeam color red"),
                 ("scoreboard teams option aTeam color white", "team option aTeam color white"),
                 ("scoreboard teams option aTeam color yellow", "team option aTeam color yellow"),
                 ("scoreboard teams option aTeam friendlyfire true", "team option aTeam friendlyfire true"),
                 ("scoreboard teams option aTeam friendlyfire false", "team option aTeam friendlyfire false"),
                 ("scoreboard teams option aTeam seeFriendlyInvisibles true", "team option aTeam seeFriendlyInvisibles true"),
                 ("scoreboard teams option aTeam seeFriendlyInvisibles false", "team option aTeam seeFriendlyInvisibles false"),
                 ("scoreboard teams option aTeam nametagVisibility never", "team option aTeam nametagVisibility never"),
                 ("scoreboard teams option aTeam nametagVisibility hideForOtherTeams", "team option aTeam nametagVisibility hideForOtherTeams"),
                 ("scoreboard teams option aTeam nametagVisibility hideForOwnTeam", "team option aTeam nametagVisibility hideForOwnTeam"),
                 ("scoreboard teams option aTeam nametagVisibility always", "team option aTeam nametagVisibility always"),
                 ("scoreboard teams option aTeam deathMessageVisibility never", "team option aTeam deathMessageVisibility never"),
                 ("scoreboard teams option aTeam deathMessageVisibility hideForOtherTeams", "team option aTeam deathMessageVisibility hideForOtherTeams"),
                 ("scoreboard teams option aTeam deathMessageVisibility hideForOwnTeam", "team option aTeam deathMessageVisibility hideForOwnTeam"),
                 ("scoreboard teams option aTeam deathMessageVisibility always", "team option aTeam deathMessageVisibility always"),
                 ("scoreboard teams option aTeam collisionRule always", "team option aTeam collisionRule always"),
                 ("scoreboard teams option aTeam collisionRule never", "team option aTeam collisionRule never"),
                 ("scoreboard teams option aTeam collisionRule pushOwnTeam", "team option aTeam collisionRule pushOwnTeam"),
                 ("scoreboard teams option aTeam collisionRule pushOtherTeams", "team option aTeam collisionRule pushOtherTeams"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("seed", "seed"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("setblock 1 ~-1 ~1 stone", "setblock 1 ~-1 ~1 stone"),
                 ("setblock 1 ~-1 ~1 stone 1", "setblock 1 ~-1 ~1 granite"),
                 ("setblock 1 ~-1 ~1 stone 1 destroy", "setblock 1 ~-1 ~1 granite destroy"),
                 ("setblock 1 ~-1 ~1 stone 1 destroy {abc:def}", "setblock 1 ~-1 ~1 granite{abc:def} destroy"),
                 ("setblock 1 ~-1 ~1 stone 1 keep", "setblock 1 ~-1 ~1 granite keep"),
                 ("setblock 1 ~-1 ~1 stone 1 keep {abc:def}", "setblock 1 ~-1 ~1 granite{abc:def} keep"),
                 ("setblock 1 ~-1 ~1 stone 1 replace", "setblock 1 ~-1 ~1 granite"),
                 ("setblock 1 ~-1 ~1 stone 1 replace {abc:def}", "setblock 1 ~-1 ~1 granite{abc:def}"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("setidletimeout 10", "setidletimeout 10"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("setworldspawn", "setworldspawn"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("setworldspawn 1 ~-1 1", "setworldspawn 1 ~-1 1"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("spawnpoint", "spawnpoint"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("spawnpoint @s", "spawnpoint @s"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = (("spawnpoint @s 1 ~-1 1", "spawnpoint @s 1 ~-1 1"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("spreadplayers 1 ~1 1 2 true @s", "spreadplayers 1 ~1 1 2 true @s"),
                 ("spreadplayers 1 ~1 1 2 true @s Carl", "spreadplayers 1 ~1 1 2 true @s Carl"),
                 ("spreadplayers 1 ~1 1 2 true @e[c=1] Carl", "spreadplayers 1 ~1 1 2 true @e[limit=1,sort=nearest] Carl"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("stats block 1 ~-1 ~1 clear AffectedBlocks", "#~ stats block 1 ~-1 ~1 clear AffectedBlocks ||| Clearing a stat is no longer needed"),
                 ("stats block 1 ~-1 ~1 clear AffectedEntities", "#~ stats block 1 ~-1 ~1 clear AffectedEntities ||| Clearing a stat is no longer needed"),
                 ("stats block 1 ~-1 ~1 clear AffectedItems", "#~ stats block 1 ~-1 ~1 clear AffectedItems ||| Clearing a stat is no longer needed"),
                 ("stats block 1 ~-1 ~1 clear QueryResult", "#~ stats block 1 ~-1 ~1 clear QueryResult ||| Clearing a stat is no longer needed"),
                 ("stats block 1 ~-1 ~1 clear SuccessCount", "#~ stats block 1 ~-1 ~1 clear SuccessCount ||| Clearing a stat is no longer needed"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("stats block 1 ~-1 ~1 set AffectedBlocks @s anObjective", "#~ stats block 1 ~-1 ~1 set AffectedBlocks @s anObjective ||| Use \'execute store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 ("stats block 1 ~-1 ~1 set AffectedEntities @s anObjective", "#~ stats block 1 ~-1 ~1 set AffectedEntities @s anObjective ||| Use \'execute store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 ("stats block 1 ~-1 ~1 set AffectedItems @s anObjective", "#~ stats block 1 ~-1 ~1 set AffectedItems @s anObjective ||| Use \'execute store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 ("stats block 1 ~-1 ~1 set QueryResult @s anObjective", "#~ stats block 1 ~-1 ~1 set QueryResult @s anObjective ||| Use \'execute store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 ("stats block 1 ~-1 ~1 set SuccessCount @s anObjective", "#~ stats block 1 ~-1 ~1 set SuccessCount @s anObjective ||| Use \'execute store success score @s anObjective run COMMAND\' on the commands that you want the stats from"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = (("stats entity @s clear AffectedBlocks", "#~ stats entity @s clear AffectedBlocks ||| Clearing a stat is no longer needed"),
                 ("stats entity @s clear AffectedEntities", "#~ stats entity @s clear AffectedEntities ||| Clearing a stat is no longer needed"),
                 ("stats entity @s clear AffectedItems", "#~ stats entity @s clear AffectedItems ||| Clearing a stat is no longer needed"),
                 ("stats entity @s clear QueryResult", "#~ stats entity @s clear QueryResult ||| Clearing a stat is no longer needed"),
                 ("stats entity @s clear SuccessCount", "#~ stats entity @s clear SuccessCount ||| Clearing a stat is no longer needed"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax4_convert(self):
        tests = (("stats entity @s set AffectedBlocks @s anObjective", "#~ stats entity @s set AffectedBlocks @s anObjective ||| Use \'execute as @s at @s store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 ("stats entity @s set AffectedEntities @s anObjective", "#~ stats entity @s set AffectedEntities @s anObjective ||| Use \'execute as @s at @s store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 ("stats entity @s set AffectedItems @s anObjective", "#~ stats entity @s set AffectedItems @s anObjective ||| Use \'execute as @s at @s store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 ("stats entity @s set QueryResult @s anObjective", "#~ stats entity @s set QueryResult @s anObjective ||| Use \'execute as @s at @s store result score @s anObjective run COMMAND\' on the commands that you want the stats from"),
                 ("stats entity @s set SuccessCount @s anObjective", "#~ stats entity @s set SuccessCount @s anObjective ||| Use \'execute as @s at @s store success score @s anObjective run COMMAND\' on the commands that you want the stats from"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("stop", "stop"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("stopsound @s master aSound", "stopsound @s master aSound"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("summon cow", "summon cow"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("summon cow 1 ~-1 ~1", "summon cow 1 ~-1 ~1"),
                 ("summon cow 1 ~-1 ~1 {abc:def}", "summon cow 1 ~-1 ~1 {abc:def}"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("teleport @s 1 ~-1 ~1", "teleport 1 ~-1 ~1"),
                 ("teleport @e 1 ~-1 ~1", "teleport @e 1 ~-1 ~1"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("teleport @s 1 ~-1 ~1 ~30 ~-60", "teleport @s 1 ~-1 ~1 ~30 ~-60"),
                 ("teleport @e 1 ~-1 ~1 ~30 ~-60", "teleport @e 1 ~-1 ~1 ~30 ~-60"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("tp 1 ~-1 ~1", "teleport 1 ~-1 ~1"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("tp 1 ~-1 ~1 ~30 ~-60", "teleport 1 ~-1 ~1 ~30 ~-60"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = (("tp @s", "teleport @s"),
                 ("tp @s @e[c=1]", "teleport @e[limit=1,sort=nearest]"),
                 ("tp @e @e[c=1]", "teleport @e @e[limit=1,sort=nearest]"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax4_convert(self):
        tests = (("tp @s 1 ~-1 ~1", "teleport 1 ~-1 ~1"),
                 ("tp @e 1 2 3", "execute as @e run teleport 1 2 3"),
                 ("tp @e 1 ~-1 ~1", "execute as @e at @s run teleport 1 ~-1 ~1"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax5_convert(self):
        tests = (("tp @s 1 ~-1 ~1 ~30 ~-60", "teleport @s 1 ~-1 ~1 ~30 ~-60"),
                 ("tp @e 1 2 3 30 -60", "execute as @e run teleport 1 2 3 30 -60"),
                 ("tp @e 1 ~-1 ~1 ~30 ~-60", "execute as @e at @s run teleport 1 ~-1 ~1 ~30 ~-60"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("tellraw @s {\"text\":\"hi\"}", "tellraw @s {\"text\":\"hi\"}"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("testfor @s", "execute if entity @s"),
                 ("testfor @a", "execute if entity @a[limit=1]"),
                 ("testfor @s {abc:def}", "execute if entity @s[nbt={abc:def}]"),
                 ("testfor @e {abc:def}", "execute if entity @e[limit=1,nbt={abc:def}]"),
                 ("testfor Carl", "execute if entity Carl"),
                 ("testfor Carl {abc:def}", "execute if entity @p[name=Carl,nbt={abc:def}]"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("testforblock 1 ~-1 1 stone", "#~ The splitting of this command (testforblock 1 ~-1 1 stone) can produce different results if used with stats\n"
                                                "execute if block 1 ~-1 1 andesite\n"
                                                "execute if block 1 ~-1 1 diorite\n"
                                                "execute if block 1 ~-1 1 granite\n"
                                                "execute if block 1 ~-1 1 polished_andesite\n"
                                                "execute if block 1 ~-1 1 polished_diorite\n"
                                                "execute if block 1 ~-1 1 polished_granite\n"
                                                "execute if block 1 ~-1 1 stone"),
                 ("testforblock 1 ~-1 1 stone 1", "execute if block 1 ~-1 1 granite"),
                 ("testforblock 1 ~-1 1 stone 1 {abc:def}", "execute if block 1 ~-1 1 granite{abc:def}"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("testforblocks 1 ~-1 1 1 ~-1 1 1 ~-1 1", "execute if blocks 1 ~-1 1 1 ~-1 1 1 ~-1 1 all"),
                 ("testforblocks 1 ~-1 1 1 ~-1 1 1 ~-1 1 all", "execute if blocks 1 ~-1 1 1 ~-1 1 1 ~-1 1 all"),
                 ("testforblocks 1 ~-1 1 1 ~-1 1 1 ~-1 1 masked", "execute if blocks 1 ~-1 1 1 ~-1 1 1 ~-1 1 masked"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("time add 42", "time add 42"),
                 ("time set 42", "time set 42"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("time set day", "time set day"),
                 ("time set night", "time set night"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = (("time query day", "time query day"),
                 ("time query daytime", "time query daytime"),
                 ("time query gametime", "time query gametime"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("title @s clear", "title @s clear"),
                 ("title @s reset", "title @s reset"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("title @s title {\"text\":\"hi\"}", "title @s title {\"text\":\"hi\"}"),
                 ("title @s subtitle {\"text\":\"hi\"}", "title @s subtitle {\"text\":\"hi\"}"),
                 ("title @s actionbar {\"text\":\"hi\"}", "title @s actionbar {\"text\":\"hi\"}"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = (("title @s times 1 2 3", "title @s times 1 2 3"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("toggledownfall", "#~ toggledownfall ||| This command was removed"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("trigger anObjective add 0", "trigger anObjective add 0"),
                 ("trigger anObjective add 1", "trigger anObjective"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("w @s hi", "w @s hi"),
                 ("msg @s hi", "w @s hi"),
                 ("tell @s hi", "w @s hi"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("weather clear", "#~ 'weather clear' no longer has random duration. The duration is now 5 minutes\nweather clear"),
                 ("weather rain", "#~ 'weather rain' no longer has random duration. The duration is now 5 minutes\nweather rain"),
                 ("weather thunder", "#~ 'weather thunder' no longer has random duration. The duration is now 5 minutes\nweather thunder"),
                 ("weather clear 1", "weather clear 1"),
                 ("weather rain 1", "weather rain 1"),
                 ("weather thunder 1", "weather thunder 1"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("whitelist add @s", "whitelist add @s"),
                 ("whitelist remove @s", "whitelist remove @s"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("whitelist on", "whitelist on"),
                 ("whitelist off", "whitelist off"),
                 ("whitelist list", "whitelist list"),
                 ("whitelist reload", "whitelist reload"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("weather clear 1", "weather clear 1"),
                 ("weather rain 1", "weather rain 1"),
                 ("weather thunder 1", "weather thunder 1"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax2_convert(self):
        tests = (("worldborder center 1 ~2", "worldborder center 1 ~2"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax3_convert(self):
        tests = (("worldborder damage amount 1", "worldborder damage amount 1"),
                 ("worldborder damage buffer 1", "worldborder damage buffer 1"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax4_convert(self):
        tests = (("worldborder warning distance 1", "worldborder warning distance 1"),
                 ("worldborder warning time 1", "worldborder warning time 1"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax5_convert(self):
        tests = (("worldborder get", "worldborder get"), )
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
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
            self.assertRaises(SyntaxError, converter.decide, perm)
        self.assertStats()

    def test_syntax1_convert(self):
        tests = (("xp 1", "experience add @s 1"),
                 ("xp 1 @p", "experience add @p 1"),
                 ("xp 1L", "experience add @s 1 levels"),
                 ("xp 1L @p", "experience add @p 1 levels"))
        for before, after in tests:
            self.assertEqual(after, unicode(converter.decide(before)), "source: \'{}\'".format(before))
        self.assertStats()
