import os
import pytesseract as ocr
import pyautogui as gui
from BattleActors import Suit

HEALTH_BAR_X = (920,), (790, 1050), (660, 920, 1180), (530, 790, 1050, 1310)
HEALTH_BAR_Y = 118

ocr.pytesseract.tesseract_cmd = os.environ["ProgramFiles(x86)"] + r'\Tesseract-OCR\tesseract'

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

        health = ocr.image_to_string('%ihp.png' % suit)
        level = ocr.image_to_string('%ilv.png' % suit)

        if 'ex' in level:
            isExec[suit] = True

        newHp = newLv = newMhp = ''
        for char in level:
            if char.isdigit():
                newLv += char

        isMhpMode = False
        for char in health:
            if char.isdigit():
                if isMhpMode:
                    newMhp += char
                else:
                    newHp += char
            elif char == '/':
                isMhpMode = True

        if newHp != '' and newLv != '' and newMhp != '':
            healths[suit] = int(newHp)
            levels[suit] = int(newLv)
            maxHealths[suit] = int(newMhp)
        else:
            print(newHp, newLv, newMhp)
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