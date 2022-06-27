import math, itertools, BattleGlobals
from BattleActors import Suit, FULL_TOON

# helper functions to print out things to console
def warn(string: str = ''):
    print("Warning: %s" % string)
def info(string: str = ''):
    print("Info: %s" % string)
def debug(string: str = ''):
    print("Debug: %s" % string)

class Battle:
    verbose = False   # flag to print out debug statements

    activeSuits = [Suit(182, 182, 12, False, "Mr. Hollywood"), Suit(30, 30, 5, False, "Flunky"), Suit(90, 90, 8, False, "The Mingler")]
    activeToons = [FULL_TOON, FULL_TOON, FULL_TOON, FULL_TOON]

    def addSuit(self, suit: Suit):
        if len(self.activeSuits) >= BattleGlobals.MAX_SUITS:
            warn('Tried adding a suit, but we already had the max number of suits. Not adding.')
            return

        self.activeSuits.append(suit)
        info('Successfully added new suit to list.')

    def allUseSound(self, iteration: int = 0):
        numToons = len(self.activeToons)    # current toons in battle

        maxLevel = max(self.activeSuits, key = lambda suit: suit.level).level       # the highest level in the current set of suits
        maxHealth = max(self.activeSuits, key = lambda suit: suit.currHP).currHP    # the highest health in the current set of suits

        presBonus = math.ceil(maxLevel * BattleGlobals.SOUND_PRESTIGE_BONUS_FROM_LV)    # prestige bonus for each sound gag (not cumulative)

        soundCombos = list(itertools.combinations_with_replacement(BattleGlobals.GAG_TRACK_VALUE[BattleGlobals.SOUND_TRACK], numToons))
        soundCombos.sort(key = lambda damages: sum(damages), reverse = True)    # sort by total damage dealt, rather than sequentially by gags

        # next, get a new list of combos that function (i.e. kill the cogs)
        validCombos = []
        for combo in soundCombos:
            totalDamage = sum(combo)    # total base damage is the sum of all the sounds used

            for toon in range(len(combo)):
                if self.activeToons[toon].hasPrestige(BattleGlobals.SOUND_TRACK):
                    totalDamage += presBonus

            totalDamage *= 1.0 + BattleGlobals.GAG_COMBO_DAMAGE_SPREAD[len(combo) - 1]
            totalDamage = math.ceil(totalDamage)

            if totalDamage < maxHealth:
                break

            validCombos.append(combo)

        if not validCombos:
            return (-1), 0.0

        # sort combos by cost, rather than damage; some combos are more efficient despite not being the least damaging
        validCombos.sort(key = lambda combo: BattleGlobals.scoreGags(BattleGlobals.SOUND_TRACK, combo))
        return validCombos[iteration], BattleGlobals.getAccuracy(validCombos[iteration][-1], BattleGlobals.SOUND_TRACK, maxLevel - 1, 0)

    # sound with drops on individual suits
    def soundDrop(self, numDrops: int = 1, iteration: int = 0):
        numToons = len(self.activeToons)

        if numDrops >= numToons - 1 or numDrops > len(self.activeSuits) - 1:
            warn('Tried sound/drop combo without being able to sound? (Too many drops.)')
            return (-1), 0.0

        maxLevel = max(self.activeSuits, key = lambda suit: suit.level).level

        # an int representing damage the sound(s) need to do in order to kill all but the drop target(s)
        soundDamageTarget = sorted(self.activeSuits, key = lambda suit: suit.currHP, reverse = True)[numDrops - len(self.activeSuits)].currHP
        presBonus = math.ceil(maxLevel * BattleGlobals.SOUND_PRESTIGE_BONUS_FROM_LV)

        # a list of damage(s) needed to be done by the drop(s) after sounds have hit
        dropDamageTarget = [suit.currHP for suit in sorted(self.activeSuits, key = lambda suit: suit.currHP, reverse = True)[0:numDrops]]

        soundCombos = list(itertools.combinations_with_replacement(BattleGlobals.GAG_TRACK_VALUE[BattleGlobals.SOUND_TRACK], numToons - numDrops))
        soundCombos.sort(key = lambda damages: sum(damages), reverse = True)

        validCombos = []
        for combo in soundCombos:
            totalDamage = sum(combo)

            for toon in range(len(combo)):
                if self.activeToons[toon].hasPrestige(BattleGlobals.SOUND_TRACK):
                    totalDamage += presBonus

            totalDamage *= 1.0 + BattleGlobals.GAG_COMBO_DAMAGE_SPREAD[len(combo) - 1]
            totalDamage = math.ceil(totalDamage)

            if totalDamage < soundDamageTarget:
                break
            
            drops = dropDamageTarget.copy()
            dropCombo = []
            for drop in drops:
                drop -= totalDamage

                dropCombo.append(BattleGlobals.lowestRequired(BattleGlobals.DROP_TRACK, drop))

            validCombos.append(combo + tuple(dropCombo))

        if not validCombos:
            return (-1), 0.0

        validCombos.sort(key = lambda combo: BattleGlobals.scoreGags(BattleGlobals.SOUND_TRACK, combo[:numDrops]) + BattleGlobals.scoreGags(BattleGlobals.DROP_TRACK, combo[numDrops:]))
        
        # accuracy check for multiple gags time
        accuracy = 1.0
        accuracy *= BattleGlobals.getAccuracy(max(validCombos[iteration][:numDrops]), BattleGlobals.SOUND_TRACK, maxLevel, 0)
        for drop in range(numDrops):
            for suit in self.activeSuits:
                if suit.currHP in dropDamageTarget:
                    accuracy *= BattleGlobals.getAccuracy(validCombos[iteration][numDrops + drop], BattleGlobals.DROP_TRACK, suit.level, 1) + (BattleGlobals.DROP_PRESTIGE_BONUS_SOLO_ACC if self.activeToons[drop].hasPrestige(BattleGlobals.DROP_TRACK) else 0)
                    break
                warn('Accuracy check failed to find valid suit target for drop accuracy calculation.')
        
        accuracy = round(accuracy, 3)

        return validCombos[iteration], accuracy