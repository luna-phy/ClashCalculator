import BattleStrings, math

# enumeration for gag tracks
HEAL_TRACK = 0
TRAP_TRACK = 1
LURE_TRACK = 2
SOUND_TRACK = 3
SQUIRT_TRACK = 4
ZAP_TRACK = 5
THROW_TRACK = 6
DROP_TRACK = 7

# various prestige effects and constants
HEAL_SELF_FACTOR = 0.5

TRAP_EXE_BONUS = 0.3
TRAP_HEALTHY_BONUS = 0.2
TRAP_HEALTHY_THRESHOLD = 0.5

LURE_NORMAL_KB = 0.5
LURE_PRESTIGE_KB = 0.65

SOUND_PRESTIGE_BONUS_FROM_LV = 0.5

SQUIRT_PRESTIGE_DODGE_REDUC = 0.15

ZAP_PRESTIGE_BOUNCE = (3.0, 2.5, 2.0)
ZAP_NORMAL_BOUNCE = (3.0, 2.25, 1.5)

THROW_MARKED_BONUS = (0.08, 0.12, 0.16, 0.2)

DROP_PRESTIGE_BONUS_SOLO_ACC = 0.15
DROP_PRESTIGE_BONUS_COMBO = 0.1
DROP_COMBO_DAMAGE_SPREAD = (0.0, 0.2, 0.3, 0.4)

# gag information
GAG_COMBO_DAMAGE_SPREAD = (0.0, 0.2, 0.2, 0.2)
GAG_TRACK_ACCURACY = (
    (0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95),   # toon-up
    (1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00),   # trap
    (0.65, 0.65, 0.70, 0.70, 0.75, 0.75, 0.80, 0.80),   # lure
    (0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95),   # sound
    (0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95),   # squirt
    (0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30),   # zap
    (0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75),   # throw
    (0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50, 0.50)    # drop
)

accBonusFromTrack = lambda lv: (lv - 1) * 0.10
SUIT_DEFENSE = (-0.02, -0.05, -0.1, -0.15, -0.2, -0.25, -0.3, -0.35, -0.4, -0.45, -0.5, -0.55, -0.6, -0.65)

def getAccuracy(gag, gagTrack, suitLevel, stuns) -> float:
    pos = GAG_TRACK_VALUE[gagTrack].index(gag)
    propAcc = GAG_TRACK_ACCURACY[gagTrack][pos]
    trackExp = accBonusFromTrack(8) # TODO: add implementation

    if suitLevel > len(SUIT_DEFENSE):
        tgtDefense = SUIT_DEFENSE[-1]
    else:
        tgtDefense = SUIT_DEFENSE[suitLevel]

    bonus = 0.20 * stuns
    
    total = propAcc + trackExp + tgtDefense + bonus

    print('%f + %f + %f + %f' % (propAcc, trackExp, tgtDefense, bonus))
    

    if total > 0.95:
        total = 0.95
    if total < 0.0:
        total = 0.0
    print(round(total, 3))
    return round(total, 3)

# damage values, or lure rounds
GAG_TRACK_VALUE = (
    (8, 15, 26, 39, 50, 78, 95, 135),
    (20, 30, 45, 65, 90, 140, 200, 240),
    (2, 2, 3, 3, 4, 4, 5, 5),
    (4, 7, 11, 16, 21, 32, 50, 65),
    (4, 8, 12, 21, 30, 56, 80, 115),
    (4, 6, 10, 16, 24, 40, 66, 80),
    (8, 13, 20, 35, 50, 90, 130, 170),
    (12, 20, 35, 55, 80, 125, 180, 220)
)

def lowestRequired(track, damageToDeal):
    for gag in GAG_TRACK_VALUE[track]:
        if gag >= damageToDeal:
            return gag
    return -1

# the cost of using a specific gag, for each track - used in calculations to determine what plan is more cost-effective
# the reason for this is because gags of different tracks of the same level are weighted differently
# a piano is a tad more costly to use than an opera, for instance
GAG_TRACK_COST = (
    (1, 2, 3, 5, 8, 30, 80, 150),
    (1, 2, 3, 5, 8, 30, 80, 150),
    (1, 2, 3, 5, 8, 30, 80, 150),
    (1, 2, 3, 5, 8, 30, 80, 150),
    (1, 2, 3, 5, 8, 30, 80, 150),
    (1, 2, 3, 5, 8, 30, 80, 150),
    (1, 2, 3, 5, 8, 30, 80, 150),
    (2, 3, 4, 6, 9, 33, 88, 175)
)

# return true if a gag is single target, false otherwise
def isSingleTarget(track: int, level: int):
    return False if track is SOUND_TRACK or (track in (HEAL_TRACK, LURE_TRACK) and level % 2 == 1) else True

def scoreGags(track: int, gags: tuple) -> int:
    score = 0
    for gag in gags:
        pos = GAG_TRACK_VALUE[track].index(gag)
        score += GAG_TRACK_COST[track][pos]
    return score

# returns strings like Elephant Trunk, Elephant Trunk, Elephant Trunk, Foghorn
def localizeGags(track: int, gags: tuple) -> str:
    localized = ''
    for gag in gags:
        pos = GAG_TRACK_VALUE[track].index(gag)
        localized += BattleStrings.GAG_NAMES[track][pos] + ", "
    return localized[:-2]

# returns strings like 3 Elephant Trunk, 1 Foghorn
def localizeGagsConcise(track: int, gags: tuple) -> str:
    from collections import Counter
    co = Counter(gags)
    localized = ''
    for gag in list(co):
        pos = GAG_TRACK_VALUE[track].index(gag)
        localized += '%i %s' % (co[gag], BattleStrings.GAG_NAMES[track][pos]) + ', '
    return localized[:-2]

# enumeration for status conditions, suits start with 10, toons with 20
STATUS_SOAK = 10
STATUS_REG_LURE = 11
STATUS_PRES_LURE = 12
STATUS_MARKED = 13  # marked for laugh

MAX_TOONS = 4
MAX_SUITS = 4

# suit health formulas for regular cogs, operations analysts, and field specialists
suitHealthFromLevelDefault = lambda lv: (lv + 1) * (lv + 2)
suitHealthFromLevelDefense = lambda lv: (lv + 2) * (lv + 3) - 2
suitHealthFromLevelOffense = lambda lv: lv * (lv + 1) + 1