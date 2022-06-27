import BattleGlobals

class Suit:
    name = ""
    currHP = 10
    maxHP = 10
    level = 1
    isExecutive = False
    statusConditions = {}

    def __init__(self, currHP, maxHP, level, executive, name):
        self.currHP, self.maxHP, self.level, self.isExecutive, self.name = currHP, maxHP, level, executive, name

    def setHP(self, health: int):
        self.currHP = health

    def setMHP(self, health: int):
        self.maxHP = health

    def soak(self, soak: bool = True):
        self.statusConditions[BattleGlobals.STATUS_SOAK] = soak

    def lure(self, lure: bool = True, prestige: bool = False):
        self.statusConditions[BattleGlobals.STATUS_PRES_LURE if prestige else BattleGlobals.STATUS_REG_LURE] = lure

class Toon:
    name = ""
    currLaff = 15
    maxLaff = 15

    tracks = [False, False, False, False, False, False, False, False]
    prestiges = [False, False, False, False, False, False, False, False]

    def __init__(self, currLaff, maxLaff, tracks, prestiges):
        self.currLaff, self.maxLaff, self.tracks, self.prestiges = currLaff, maxLaff, tracks, prestiges

    def hasTrack(self, track: int) -> bool:
        return self.tracks[track]

    def hasPrestige(self, track: int) -> bool:
        return self.prestiges[track]

# debug filler for calculator, tells the calculator this toon has every possible gag, and every possible prestige
FULL_TOON = Toon(137, 137, [True, True, True, True, True, True, True, True], [True, True, True, True, True, True, True, True])