import os
import pytesseract as ocr
import pyautogui as gui
from BattleActors import Suit
from PIL import Image
import cv2, math
import time

HEALTH_BAR_X = (920,), (790, 1050), (660, 920, 1180), (530, 790, 1050, 1310)
HEALTH_BAR_Y = 118

ocr.pytesseract.tesseract_cmd = os.environ["ProgramFiles(x86)"] + r'\Tesseract-OCR\tesseract'
CONFIG = '-c tessedit_char_whitelist=0123456789LevelS/.exe --psm 7'
FACTOR = 1.5


def grabSuitHealths(suitCount: int = 4) -> list:
    if not 0 < suitCount <= 4:
        print('Could not grab infos! (suitCount %i invalid)' % suitCount)
        for count in range(4):
            if os.path.exists('%ihp.png' % count):
                os.remove('%ihp.png' % count)
            if os.path.exists('%ilv.png' % count):
                os.remove('%ilv.png' % count)
        return []

    print('Attempting to grab suit infos (%i suit%s)...' % (suitCount, 's' if suitCount > 1 else ''))

    healths = [0 for suit in range(suitCount)]
    maxHealths = [0 for suit in range(suitCount)]
    levels = [0 for suit in range(suitCount)]
    isExec = [False for suit in range(suitCount)]

    for suit in range(suitCount):
        gui.screenshot('%ihp.png' % suit, region = (HEALTH_BAR_X[suitCount - 1][suit], HEALTH_BAR_Y, 128, 28))
        gui.screenshot('%ilv.png' % suit, region = (HEALTH_BAR_X[suitCount - 1][suit], HEALTH_BAR_Y - 24, 134, 20))

        one = cv2.imread("%ihp.png" % suit)
        one = cv2.resize(one, (math.ceil(256 * FACTOR),math.ceil(56 * FACTOR)), interpolation = cv2.INTER_CUBIC)
        gry = cv2.cvtColor(one, cv2.COLOR_BGR2GRAY)
        thr = cv2.threshold(gry, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        health = ocr.image_to_string(255 - thr, lang='eng',config=CONFIG)

        two = cv2.imread("%ilv.png" % suit)
        two = cv2.resize(two, (math.ceil(268 * FACTOR), math.ceil(40 * FACTOR)), interpolation = cv2.INTER_CUBIC)
        gry2 = cv2.cvtColor(two, cv2.COLOR_BGR2GRAY)
        thr2 = cv2.threshold(gry2, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        level = ocr.image_to_string(255 - thr2, lang='eng',config=CONFIG)

        if 'ex' in level:
            isExec[suit] = True

        newHp = newLv = newMhp = ''
        for char in level:
            if char.isdigit():
                newLv += char
            elif char == 'S':
                newLv += '5'

        isMhpMode = False
        for char in health:
            if char.isdigit():
                if isMhpMode:
                    newMhp += char
                else:
                    newHp += char
            elif char == '/' and newHp != '':
                isMhpMode = True
            elif char == 'S':   # hacky
                if isMhpMode:
                    newMhp += '5'
                else:
                    newHp += '5'

        print('health %i:%s' % (suitCount, health), 'level %i:%s' % (suitCount, level))

        if newHp != '' and newLv != '' and newMhp != '':
            healths[suit] = int(newHp)
            levels[suit] = int(newLv)
            maxHealths[suit] = int(newMhp)
        else:
            #cv2.imshow('%i - NumSuits %i - Health' % (suit + 1, suitCount), 255 - thr)
            #cv2.imshow('%i - NumSuits %i - Level' % (suit + 1, suitCount), 255 - thr2)
            print('Failed at suit %i (%s, %s, %s)' % (suit + 1, newHp, newLv, newMhp))
            print('Failed pass %i' % suitCount)
            return grabSuitHealths(suitCount - 1)

    suits = []
    for suit in range(suitCount):   # TODO: add OCR for suit names
        suits.append(Suit(healths[suit], maxHealths[suit], levels[suit], isExec[suit], 'Suit'))

    for count in range(4):
        if os.path.exists('%ihp.png' % count):
            os.remove('%ihp.png' % count)
        if os.path.exists('%ilv.png' % count):
            os.remove('%ilv.png' % count)

    return suits