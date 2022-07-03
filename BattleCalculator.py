import math, itertools, BattleGlobals, BattleStrings
from BattleActors import Suit, FULL_TOON

# helper functions to print out things to console
def warn(string: str = ''):    
    return
    print("WARN: %s" % string)
def info(string: str = ''):
    return
    print("INFO: %s" % string)
def debug(string: str = ''):
    print("DEBUG: %s" % string)

class Battle:
    activeSuits = []
    activeToons = [FULL_TOON, FULL_TOON, FULL_TOON, FULL_TOON]
    successfulCombos = []
    MAX_COMBO_OUTPUT = 23   # the max amount of successful combos returned by calculate()

    def addSuit(self, suit: Suit):
        if len(self.activeSuits) >= BattleGlobals.MAX_SUITS:
            warn('Tried adding a suit, but we already had the max number of suits. Not adding.')
            return

        self.activeSuits.append(suit)
        info('Successfully added new suit to list.')

    def clearSuits(self):
        self.activeSuits.clear()

    def allUseSound(self, iteration: int = 0):
        funcName = 'All Sound'
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
            return funcName

        # sort combos by cost, rather than damage; some combos are more efficient despite not being the least damaging
        validCombos.sort(key = lambda combo: BattleGlobals.scoreGags(BattleGlobals.SOUND_TRACK, combo))
        return validCombos[iteration], BattleGlobals.getAccuracy(validCombos[iteration][-1], BattleGlobals.SOUND_TRACK, maxLevel - 1, 0), [-1 for toon in range(numToons)], BattleGlobals.scoreGags(BattleGlobals.SOUND_TRACK, validCombos[iteration]), [BattleGlobals.SOUND_TRACK] * numToons, funcName

    # sound with drops on individual suits
    def soundDrop(self, iteration: int = 0, numDrops: int = 1):
        funcName = 'Sound with %i Drop%s' % (numDrops, 's' if numDrops > 1 else '')
        numToons = len(self.activeToons)

        if numDrops >= numToons or numDrops > len(self.activeSuits):
            warn('Tried sound/drop combo without being able to sound? (Too many drops, needs at least one sound.)')
            return funcName

        maxLevel = max(self.activeSuits, key = lambda suit: suit.level).level

        # an int representing damage the sound(s) need to do in order to kill all but the drop target(s)
        soundDamageTarget = sorted(self.activeSuits, key = lambda suit: suit.currHP, reverse = True)[numDrops - len(self.activeSuits) if (numDrops - len(self.activeSuits) < 0) else -1].currHP
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
            warn('No valid combos')
            return funcName

        validCombos.sort(key = lambda combo: BattleGlobals.scoreGags(BattleGlobals.SOUND_TRACK, combo[:numToons - numDrops]) + BattleGlobals.scoreGags(BattleGlobals.DROP_TRACK, combo[numToons - numDrops:]))
        
        # the indices of the gag targets, the sounds have no target (-1)
        positions = [-1 for toon in range(numToons - numDrops)]
        # accuracy check for multiple gags time
        accuracy = 1.0
        accuracy *= BattleGlobals.getAccuracy(max(validCombos[iteration][:numToons - numDrops]), BattleGlobals.SOUND_TRACK, maxLevel, 0)
        for drop in range(numDrops):
            for suit in self.activeSuits:
                if suit.currHP == dropDamageTarget[drop]:
                    if validCombos[iteration][numToons - numDrops + drop] > 0:
                        acc = BattleGlobals.getAccuracy(validCombos[iteration][numToons - numDrops + drop], BattleGlobals.DROP_TRACK, suit.level, numToons - numDrops) + (BattleGlobals.DROP_PRESTIGE_BONUS_SOLO_ACC if self.activeToons[drop].hasPrestige(BattleGlobals.DROP_TRACK) else 0)
                        if acc > 0.95:
                            acc = 0.95
                        accuracy *= acc
                        positions.append(self.activeSuits.index(suit))
                    else:
                        # if a gag wasn't required, no target
                        positions.append(-1)
                    break      

        accuracy = round(accuracy, 3)

        return validCombos[iteration], accuracy, positions, BattleGlobals.scoreGags(BattleGlobals.SOUND_TRACK, validCombos[iteration][:numToons - numDrops]) + BattleGlobals.scoreGags(BattleGlobals.DROP_TRACK, validCombos[iteration][numToons - numDrops:]), [BattleGlobals.SOUND_TRACK] * (numToons - numDrops) + [BattleGlobals.DROP_TRACK] * (numDrops), funcName

    # sound with all drops on one cog, in contrast to just one on each cog
    def soundConsolidateDrops(self, iteration: int = 0, numDrops: int = 2):
        funcName = 'Sound with %i Drop%s on One Suit' % (numDrops, 's' if numDrops > 1 else '')
        numToons = len(self.activeToons)

        if numDrops >= numToons or len(self.activeSuits) < 2:
            warn('Tried sound/drop consolidated combo without being able to sound? (Too many drops.)')
            return funcName

        maxLevel = max(self.activeSuits, key = lambda suit: suit.level).level

        # since we're dropping only one cog, the sound target is the 2nd highest cog
        soundDamageTarget = sorted(self.activeSuits, key = lambda suit: suit.currHP)[-2].currHP
        presBonus = math.ceil(maxLevel * BattleGlobals.SOUND_PRESTIGE_BONUS_FROM_LV)

        dropTarget = max(self.activeSuits, key = lambda suit: suit.currHP).currHP

        soundCombos = list(itertools.combinations_with_replacement(BattleGlobals.GAG_TRACK_VALUE[BattleGlobals.SOUND_TRACK], numToons - numDrops))
        soundCombos.sort(key = lambda damages: sum(damages), reverse = True)

        # need two combinations lists because there are two calculations for combos here
        dropCombos = list(itertools.combinations_with_replacement(BattleGlobals.GAG_TRACK_VALUE[BattleGlobals.DROP_TRACK], numDrops))
        dropCombos.sort(key = lambda damages: sum(damages), reverse = True)

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

            # 2nd dimensional iterations, fuck this shit, probably causes slowdown or unneeded complexity but oh well
            # TODO: maybe fix this, idk lmao
            for drops in dropCombos:
                dropDamageTotal = sum(drops)

                dropComboMult = BattleGlobals.DROP_COMBO_DAMAGE_SPREAD[len(drops)]
                for toon in range(len(drops)):
                    if self.activeToons[toon].hasPrestige(BattleGlobals.DROP_TRACK):
                        dropComboMult += BattleGlobals.DROP_PRESTIGE_BONUS_COMBO

                dropDamageTotal *= 1.0 + dropComboMult
                dropDamageTotal = math.ceil(dropDamageTotal)

                if dropDamageTotal < dropTarget:
                    break

                validCombos.append(combo + drops)

        if not validCombos:
            warn('No valid combos')
            return funcName

        validCombos.sort(key = lambda combo: BattleGlobals.scoreGags(BattleGlobals.SOUND_TRACK, combo[:numToons - numDrops]) + BattleGlobals.scoreGags(BattleGlobals.DROP_TRACK, combo[numToons - numDrops:]))

        positions = [-1 for toon in range(numToons - numDrops)]

        accuracy = 1.0
        accuracy *= BattleGlobals.getAccuracy(max(validCombos[iteration][:numToons - numDrops]), BattleGlobals.SOUND_TRACK, maxLevel, 0)
        for drop in range(numDrops):
            for suit in self.activeSuits:
                if suit.currHP == dropTarget:
                    if validCombos[iteration][numToons - numDrops + drop] > 0:
                        acc = BattleGlobals.getAccuracy(validCombos[iteration][numToons - numDrops + drop], BattleGlobals.DROP_TRACK, suit.level, numToons - numDrops) + (BattleGlobals.DROP_PRESTIGE_BONUS_SOLO_ACC if self.activeToons[drop].hasPrestige(BattleGlobals.DROP_TRACK) else 0)
                        if acc > 0.95:
                            acc = 0.95
                        accuracy *= acc
                        positions.append(self.activeSuits.index(suit))
                    else:
                        positions.append(-1)
                    break      

        accuracy = round(accuracy, 3)

        return validCombos[iteration], accuracy, positions, BattleGlobals.scoreGags(BattleGlobals.SOUND_TRACK, validCombos[iteration][:numToons - numDrops]) + BattleGlobals.scoreGags(BattleGlobals.DROP_TRACK, validCombos[iteration][numToons - numDrops:]), [BattleGlobals.SOUND_TRACK] * (numToons - numDrops) + [BattleGlobals.DROP_TRACK] * (numDrops), funcName

    # the fucko function, big boy logic 
    def doubleZapCombo(self, iteration: int = 0, mode: str = "xx--", cross: bool = False):
        funcName = 'Double Zap (%s %s)' % (mode, 'Cross' if cross else 'Straight')
        numToons = len(self.activeToons)
        numPresZap = numPresSquirt = 0

        if numToons != 4:
            return funcName

        for toon in self.activeToons:
            if toon.hasPrestige(BattleGlobals.ZAP_TRACK):
                numPresZap += 1
            if toon.hasPrestige(BattleGlobals.SQUIRT_TRACK):
                numPresSquirt += 1

        # first, make sure the mode is even proper
        zapString = mode.lower()
        xCount = 0
        oCount = 0 # using o to mean -
        for char in zapString:
            if char not in ('x', '-'):
                warn('Incorrectly formatted zap combo (%s). Must use "x" or "-" notation.' % zapString)
                return funcName
            if char == 'x':
                xCount += 1
            if char == '-':
                oCount += 1

        if xCount + oCount != 4:
            warn('Incorrectly formatted zap combo (%s). Must use a combination of exactly 4 "x" and "-" total.')
            return funcName
        
        # next, truncate the expression if the set is only 3 cogs
        # turn xx-- into xx- if there's only 3 cogs, for instance
        # or -x-x into x-x if there's only 3 cogs

        # special case for if there's only 2 cogs
        if len(self.activeSuits) == 2:
            if zapString == "xx--":
                zapString = "x-"
            elif zapString == "--xx":
                zapString = "-x"
            else:
                zapString = "xx"

        if len(self.activeSuits) == 3:
            if zapString in ("xx--"):
                zapString = "xx-"
            elif zapString in ("x-x-", "-x-x", "x--x"):
                zapString = "x-x"
            elif zapString in ("-xx-", "--xx"):
                zapString = "-xx"
            else:
                warn('how the fuck')
                return funcName

        zapPaths = []

        # these zap modes do not change on cross or not cross
        if zapString == "x---":
            zapPaths.append([0, 1, 2, -1])
            zapPaths.append([0, -1, -1, -1])
        elif zapString == "-x--":
            zapPaths.append([1, 0, 2, -1])
            zapPaths.append([-1, 0, -1, 1])
        elif zapString == "--x-":
            zapPaths.append([2, 1, 0, -1])
            zapPaths.append([-1, -1, 0, 1])
        elif zapString == "---x":
            zapPaths.append([-1, 2, 1, 0])
            zapPaths.append([-1, -1, -1, 0])
        elif zapString == "x-":
            zapPaths.append([0, 1])
            zapPaths.append([0, -1])
        elif zapString == "-x":
            zapPaths.append([1, 0])
            zapPaths.append([-1, 0])
        
        if not zapPaths:
            if not cross:   # if not crossing, the right zap goes first
                # stupid bullshit
                # trust me, i hate doing this long yandere-dev type shit, but i'm not about to spend five million years on this one fucking method, lmao
                # TODO: maybe fix this shit idk

                # first handle the cases for 2 cogs
                if zapString == "xx":
                    zapPaths.append([1, 0])
                    zapPaths.append([0, 1])

                # next the ones for 3 cogs
                if zapString == "xx-":
                    zapPaths.append([1, 0, 2])
                    zapPaths.append([0, 1, -1])
                elif zapString == "x-x":
                    zapPaths.append([2, 1, 0])
                    zapPaths.append([0, -1, 1])
                elif zapString == "-xx":
                    zapPaths.append([2, 1, 0])
                    zapPaths.append([-1, 0, 1])

                # now the fuckos
                if zapString == "xx--":
                    zapPaths.append([1, 0, 2, -1])
                    zapPaths.append([0, 1, -1, 2])
                elif zapString == "x-x-":
                    zapPaths.append([2, 1, 0, -1])
                    zapPaths.append([0, -1, 1, 2])
                elif zapString == "-xx-":
                    zapPaths.append([2, 1, 0, -1])
                    zapPaths.append([-1, 0, 1, 2])
                elif zapString == "-x-x":
                    zapPaths.append([-1, 2, 1, 0])
                    zapPaths.append([1, 0, -1, -1])
                elif zapString == "--xx":
                    zapPaths.append([-1, 2, 1, 0])
                    zapPaths.append([1, -1, 0, -1])
                elif zapString == "x--x":
                    zapPaths.append([-1, 2, 1, 0])
                    zapPaths.append([0, -1, -1, -1])
            else:   # if crossing, the left zap goes first
                if zapString == "xx":
                    zapPaths.append([0, 1])
                    zapPaths.append([1, 0])

                if zapString == "xx-":
                    zapPaths.append([0, 1, 2])
                    zapPaths.append([1, 0, -1])
                elif zapString == "x-x":
                    zapPaths.append([0, 1, 2])
                    zapPaths.append([1, -1, 0])
                elif zapString == "-xx":
                    zapPaths.append([2, 0, 1])
                    zapPaths.append([-1, 1, 0])

                if zapString == "xx--":
                    zapPaths.append([0, 1, 2, -1])
                    zapPaths.append([-1, 0, -1, 1])
                elif zapString == "x-x-":
                    zapPaths.append([0, 1, 2, -1])
                    zapPaths.append([1, -1, 0, -1])
                elif zapString == "-xx-":
                    zapPaths.append([1, 0, 2, -1])
                    zapPaths.append([-1, 1, 0, 2])
                elif zapString == "-x-x":
                    zapPaths.append([1, 0, 2, -1])
                    zapPaths.append([-1, 1, -1, 0])
                elif zapString == "--xx":
                    zapPaths.append([2, 1, 0, -1])
                    zapPaths.append([-1, -1, 1, 0])
                elif zapString == "x--x":
                    zapPaths.append([0, 1, 2, -1])
                    zapPaths.append([-1, -1, -1, 0])

        if not zapPaths:
            warn("somehow ended with no zaps")
            return funcName

        zapCombos = list(itertools.combinations_with_replacement(BattleGlobals.GAG_TRACK_VALUE[BattleGlobals.ZAP_TRACK], 2))
        zapCombos.reverse()

        zapMultipliers = []
        for path in zapPaths:
            mult = []
            for node in path:
                if node == -1:
                    mult.append(0)
                else:
                    if numPresZap >= 2: # TODO: add checks for prestiges more effectively later
                        mult.append(BattleGlobals.ZAP_PRESTIGE_BOUNCE[node])
                    else:
                        mult.append(BattleGlobals.ZAP_NORMAL_BOUNCE[node])
            zapMultipliers.append(mult)
        
        validCombos = []
        for combo in zapCombos:
            baseDamage = [0 for target in range(len(self.activeSuits))]
            targetHealths = [suit.currHP for suit in self.activeSuits]

            for value in range(len(combo)):
                for target in range(len(baseDamage)):
                    baseDamage[target] += zapMultipliers[value][target] * combo[value]

            numAliveAfterZap = 0
            for suit in range(len(targetHealths)):
                targetHealths[suit] -= baseDamage[suit]

                if targetHealths[suit] > 0:
                    numAliveAfterZap += 1

            if numAliveAfterZap > 2:
                # if the zaps alone would leave more than two cogs alive, it is unviable (cannot squirt three targets)
                continue

            squirtCombo = []
            squirtPositions = []
            unviable = False
            if numAliveAfterZap:
                for suit in range(len(targetHealths)):
                    if targetHealths[suit] > 0:
                        if BattleGlobals.lowestRequired(BattleGlobals.SQUIRT_TRACK, targetHealths[suit]) != -1:
                            squirtCombo.append(BattleGlobals.lowestRequired(BattleGlobals.SQUIRT_TRACK, targetHealths[suit]))
                            squirtPositions.append(suit)
                        else:
                            unviable = True

            if unviable:
                continue

            if len(squirtCombo) < 2:
                for squirt in range(2 - len(squirtCombo)):
                    squirtCombo.append(4)
                    squirtPositions.append(1 if len(squirtCombo) == 0 else 2)

            # squirts with at just xx-- or --xx won't soak all cogs
            if (0 in squirtPositions and 1 in squirtPositions) or (2 in squirtPositions and 3 in squirtPositions):
                continue

            # can't have soak targets be the same
            if squirtPositions[0] == squirtPositions[1]:
                continue

            validCombos.append((combo[::-1] + tuple(squirtCombo), squirtPositions))

        if not validCombos:
            warn('No valid combos')
            return funcName

        validCombos.sort(key = lambda combo: BattleGlobals.scoreGags(BattleGlobals.ZAP_TRACK, combo[0][:2]) + BattleGlobals.scoreGags(BattleGlobals.SQUIRT_TRACK, combo[0][2:]))

        positions = []  # gag positions for all gags
        # get the zap positions first
        for path in range(2):
            for zap in range(len(zapPaths[path])):
                if zapPaths[path][zap] == 0:
                    positions.append(zap)

        positions.reverse() # we have to do this otherwise it will display the wrong order for the zaps
        positions.extend(validCombos[iteration][1]) # add the squirt positions

        accuracy = 1.0
        for squirt in range(2):
            if len(self.activeSuits) < 4:
                validCombos[iteration][1][squirt] -= 1
            if len(self.activeSuits) == 1:
                validCombos[iteration][1][squirt] = 0
            accuracy *= BattleGlobals.getAccuracy(validCombos[iteration][0][squirt + 2], BattleGlobals.SQUIRT_TRACK, self.activeSuits[validCombos[iteration][1][squirt]].level, 0)

        return validCombos[iteration][0], accuracy, positions, BattleGlobals.scoreGags(BattleGlobals.ZAP_TRACK, validCombos[iteration][0][:2]) + BattleGlobals.scoreGags(BattleGlobals.SQUIRT_TRACK, validCombos[iteration][0][2:]), [BattleGlobals.ZAP_TRACK] * 2 + [BattleGlobals.SQUIRT_TRACK] * 2, funcName

    # the syphon combo, needs 3 toons minimum, a 4th will drop
    def syphon(self, iteration: int = 0):
        funcName = 'Syphon'
        numToons = len(self.activeToons)

        if len(self.activeSuits) < 4:
            return funcName

        # the zap path + the squirt index
        zapPlans = (
            ((0, 1, 2, -1), 1), # Xxx-
            ((2, 1, 0, -1), 1), # xxX-
            ((-1, 0, 1, 2), 2), # -Xxx
            ((-1, 2, 1, 0), 2), # -xxX
            ((1, 0, 2, -1), 1), # xXx-
            ((-1, 1, 0, 2), 2), # -xXx            
        )

        zapFuncNames = (
            'Xxx-', 'xxX-', '-Xxx', '-xxX', 'xXx-', '-xXx'
        )

        maxLevel = max(self.activeSuits, key = lambda suit: suit.level).level
        presBonus = math.ceil(maxLevel * BattleGlobals.SOUND_PRESTIGE_BONUS_FROM_LV)

        sounds = BattleGlobals.GAG_TRACK_VALUE[BattleGlobals.SOUND_TRACK]
        zaps = BattleGlobals.GAG_TRACK_VALUE[BattleGlobals.ZAP_TRACK]
        squirts = BattleGlobals.GAG_TRACK_VALUE[BattleGlobals.SQUIRT_TRACK]

        workableSyphons = []
        for plan in zapPlans:
            mult = []
            for node in plan[0]:
                if node == -1:
                    mult.append(0)
                else:
                    if any(toon.hasPrestige(BattleGlobals.ZAP_TRACK) for toon in self.activeToons):
                        mult.append(BattleGlobals.ZAP_PRESTIGE_BOUNCE[node])
                    else:
                        mult.append(BattleGlobals.ZAP_NORMAL_BOUNCE[node])

            for sound in sounds:
                for squirt in squirts:
                    for zap in zaps:
                        healthTargets = [suit.currHP for suit in self.activeSuits]
                        zapDamage = [zap * mult[count] for count in range(len(healthTargets))]
                        
                        soundDamage = sound
                        if any(toon.hasPrestige(BattleGlobals.SOUND_TRACK) for toon in self.activeToons):
                            soundDamage += presBonus

                        squirtDamage = [(0 if count != plan[1] else squirt) for count in range(len(healthTargets))]

                        numTargetsAlive = 0
                        for target in range(len(healthTargets)):
                            healthTargets[target] -= zapDamage[target] + soundDamage + squirtDamage[target]
                
                            if healthTargets[target] > 0:
                                numTargetsAlive += 1
                        
                        # impossible to do combo if we can't drop the remaining cogs
                        # we can only drop one, so, more than one is not possible
                        if numTargetsAlive > 1:
                            continue

                        dropDamage = -1
                        dropTarget = -1
                        
                        # can't drop it if we don't have a toon to drop with
                        if numTargetsAlive > 0:
                            if numToons < 4:
                                continue

                            for target in range(len(healthTargets)):
                                if healthTargets[target] > 0:
                                    if BattleGlobals.lowestRequired(BattleGlobals.DROP_TRACK, healthTargets[target]) != -1:
                                        dropDamage = BattleGlobals.lowestRequired(BattleGlobals.DROP_TRACK, healthTargets[target])
                                        dropTarget = target
                                    else:
                                        # no drop exists powerful enough to kill final cog
                                        continue
                        
                        workableSyphons.append(((sound, zap, squirt, dropDamage), (-1, plan[0].index(0), plan[1], dropTarget), zapFuncNames[zapPlans.index(plan)]))

        workableSyphons.sort(key = lambda vals: BattleGlobals.scoreGags(BattleGlobals.SOUND_TRACK, (vals[0][0],)) + BattleGlobals.scoreGags(BattleGlobals.ZAP_TRACK, (vals[0][1],)) + BattleGlobals.scoreGags(BattleGlobals.SQUIRT_TRACK, (vals[0][2],)) + BattleGlobals.scoreGags(BattleGlobals.DROP_TRACK, (vals[0][3],)))

        accuracy = 1.0
        accuracy *= BattleGlobals.getAccuracy(workableSyphons[iteration][0][0], BattleGlobals.SOUND_TRACK, maxLevel, 0)
        accuracy *= BattleGlobals.getAccuracy(workableSyphons[iteration][0][2], BattleGlobals.SQUIRT_TRACK, self.activeSuits[workableSyphons[iteration][1][2]].level, 1)
        if numToons > 3:
            accuracy *= BattleGlobals.getAccuracy(workableSyphons[iteration][0][3], BattleGlobals.DROP_TRACK, self.activeSuits[workableSyphons[iteration][1][3]].level, 2)  # TODO: make the stun accurate depending on whether or not the zap helped stun for the drop

        accuracy = round(accuracy, 3)

        return workableSyphons[iteration][0], accuracy, workableSyphons[iteration][1], BattleGlobals.scoreGags(BattleGlobals.SOUND_TRACK, (workableSyphons[iteration][0][0],)) + BattleGlobals.scoreGags(BattleGlobals.ZAP_TRACK, (workableSyphons[iteration][0][1],)) + BattleGlobals.scoreGags(BattleGlobals.SQUIRT_TRACK, (workableSyphons[iteration][0][2],)) + BattleGlobals.scoreGags(BattleGlobals.DROP_TRACK, (workableSyphons[iteration][0][3],)), [BattleGlobals.SOUND_TRACK, BattleGlobals.ZAP_TRACK, BattleGlobals.SQUIRT_TRACK] + [BattleGlobals.DROP_TRACK] * (1 if numToons > 3 else 0), funcName + ' ' + workableSyphons[iteration][2]

    # just fucking use one of each gag on one each of the suits
    def allUseTrack(self, iteration: int = 0, track: int = BattleGlobals.DROP_TRACK):
        funcName = 'All %s' % BattleStrings.GAG_TRACK_NAMES[track]
        numToons = len(self.activeToons)

        if numToons == len(self.activeSuits):
            gags = []
            accuracy = 1.0
            for suit in range(len(self.activeSuits)):
                if BattleGlobals.lowestRequired(track, self.activeSuits[suit].currHP) != -1:
                    gags.append(BattleGlobals.lowestRequired(track, self.activeSuits[suit].currHP))
                    accuracy *= BattleGlobals.getAccuracy(BattleGlobals.lowestRequired(track, self.activeSuits[suit].currHP), track, self.activeSuits[suit].level, 0) + (BattleGlobals.DROP_PRESTIGE_BONUS_SOLO_ACC if (track == BattleGlobals.DROP_TRACK and self.activeToons[suit].hasPrestige(BattleGlobals.DROP_TRACK)) else 0)
                else:
                    return funcName
            
            accuracy = round(accuracy, 3)

            return gags, accuracy, [target for target in range(numToons)], BattleGlobals.scoreGags(track, gags), [track] * numToons, funcName
        elif len(self.activeSuits) == 1:
            combos = list(itertools.combinations_with_replacement(BattleGlobals.GAG_TRACK_VALUE[track], numToons))
            combos.sort(key = lambda damages: sum(damages), reverse = True) 

            validCombos = []
            for combo in combos:
                damage = sum(combo)
                if track == BattleGlobals.DROP_TRACK:
                    numPres = 0
                    for toon in self.activeToons:
                        if toon.hasPrestige(track):
                            numPres += 1
                    damage *= 1.0 + BattleGlobals.DROP_COMBO_DAMAGE_SPREAD[len(combo) - 1] + BattleGlobals.DROP_PRESTIGE_BONUS_COMBO * numPres
                else:
                    damage *= 1.0 + BattleGlobals.GAG_COMBO_DAMAGE_SPREAD[len(combo) - 1]
                damage = math.ceil(damage)

                if damage < self.activeSuits[0].currHP:
                    break

                validCombos.append(combo)

            if not validCombos:
                return funcName

            validCombos.sort(key = lambda combo: BattleGlobals.scoreGags(track, combo))
            return validCombos[iteration], BattleGlobals.getAccuracy(validCombos[iteration][-1], track, self.activeSuits[0].level - 1, 0), [0 for toon in range(numToons)], BattleGlobals.scoreGags(track, validCombos[iteration]), [track] * numToons, funcName
        elif len(self.activeSuits) == 2:
            # TODO: add implementation for splitting gags in half
            return funcName
        else:
            return funcName



    def localize(self, function: tuple):
        if type(function) is str:
            return '%s | No combos exist.' % function, -1

        gags, accuracy, position, cost, trackSpread, name = function

        pos = None
        if len(self.activeSuits) == 4:
            pos = BattleStrings.POSITIONS
        elif len(self.activeSuits) == 3:
            pos = BattleStrings.POSITIONS_THREE
        elif len(self.activeSuits) == 2:
            pos = BattleStrings.POSITIONS_TWO
        elif len(self.activeSuits) == 1:
            pos = BattleStrings.POSITIONS_ONE

        output = '%s | Success Rate: %.1f%% | Cost: %i | Gags: ' % (name, (accuracy * 100.0), cost) 
        for gag in range(len(gags)):
            output += '%s %s%s' % (BattleGlobals.localizeGag(trackSpread[gag], gags[gag]), pos[position[gag if gag >= 0 else 4]], ', ' if gag != len(gags) - 1 else '')

        return output, cost

    def localizeSubStr(self, function: tuple):
        if type(function) is str:
            return function, -1, -1

        gags, accuracy, position, cost, trackSpread, name = function

        pos = None
        if len(self.activeSuits) == 4:
            pos = BattleStrings.POSITIONS
        elif len(self.activeSuits) == 3:
            pos = BattleStrings.POSITIONS_THREE
        elif len(self.activeSuits) == 2:
            pos = BattleStrings.POSITIONS_TWO
        elif len(self.activeSuits) == 1:
            pos = BattleStrings.POSITIONS_ONE

        output = ''
        for gag in range(len(gags)):
            output += '%s %s%s' % (BattleGlobals.localizeGag(trackSpread[gag], gags[gag]), pos[position[gag if gag >= 0 else 4]], ', ' if gag != len(gags) - 1 else '')

        return name, accuracy, cost, gags, trackSpread, output

    def calculate(self, sort: bool = False, mode: bool = False) -> list:
        if not self.activeSuits:
            warn('No suits?')
            return []
        if not self.activeToons:
            warn('No toons?')
            return []
        
        if mode:
            loc = self.localizeSubStr
        else:
            loc = self.localize
        self.successfulCombos.append(loc(self.allUseSound()))
        self.successfulCombos.append(loc(self.allUseTrack(track = BattleGlobals.SQUIRT_TRACK)))
        self.successfulCombos.append(loc(self.allUseTrack(track = BattleGlobals.THROW_TRACK)))
        self.successfulCombos.append(loc(self.allUseTrack(track = BattleGlobals.DROP_TRACK)))

        for drop in range(1, len(self.activeToons)):
            self.successfulCombos.append(loc(self.soundDrop(numDrops = drop)))
            self.successfulCombos.append(loc(self.soundConsolidateDrops(numDrops = drop)))

        for zap in BattleStrings.ZAP_COMBOS:
            self.successfulCombos.append(loc(self.doubleZapCombo(mode = zap, cross = False)))
            self.successfulCombos.append(loc(self.doubleZapCombo(mode = zap, cross = True)))

        self.successfulCombos.append(loc(self.syphon()))
        
        if sort:
            self.successfulCombos.sort(key = lambda combo: combo[1] if not mode else combo[2])

        for combo in self.successfulCombos:
            if not mode:
                print(combo[0])

        toReturn = self.successfulCombos.copy()
        self.successfulCombos.clear()   # fuck you
        return toReturn
            