import BattleCalculator
import OCRModule

class Driver:
    def __init__(self) -> None:
        self.battleCalc = BattleCalculator.Battle()
        self.ocr = OCRModule

    def run(self):
        suits = self.ocr.grabSuitHealths()

        if not suits:
            raise ValueError('No suits returned. Possible OCR Failure?')
        
        print('Adding Suits:')
        for suit in suits:
            self.battleCalc.addSuit(suit)
            
            print('HP: %i | MHP: %i | LV: %i' % (suit.currHP, suit.maxHP, suit.level))

        print('Performing Calculations:\n--------------------------------------')
        self.battleCalc.calculate(sort = True)

show = Driver()
show.run()