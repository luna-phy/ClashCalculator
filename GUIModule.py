from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import BattleCalculator
import OCRModule
import BattleGlobals, BattleStrings
from BattleActors import Suit

class ScrollbarFrame(Frame):
    """
    Extends class tk.Frame to support a scrollable Frame 
    This class is independent from the widgets to be scrolled and 
    can be used to replace a standard tk.Frame
    """
    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent, **kwargs)

        # The Scrollbar, layout to the right
        vsb = Scrollbar(self, orient="vertical")
        vsb.pack(side="right", fill="y")

        # The Canvas which supports the Scrollbar Interface, layout to the left
        self.canvas = Canvas(self, borderwidth=0, background="#ffffff")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind the Scrollbar to the self.canvas Scrollbar Interface
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.configure(command=self.canvas.yview)

        # The Frame to be scrolled, layout into the canvas
        # All widgets to be scrolled have to use this Frame as parent
        self.scrolled_frame = Frame(self.canvas, background=self.canvas.cget('bg'))
        self.canvas.create_window((4, 4), window=self.scrolled_frame, anchor="nw")

        # Configures the scrollregion of the Canvas dynamically
        self.scrolled_frame.bind("<Configure>", self.on_configure)

    def on_configure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class GUI:
    HEADER_FONT = ('Impress BT', 32)
    SUBHEADER_FONT = ('Impress BT', 24)
    MAIN_FONT = ('Courier New', 18)
    DESC_FONT = ('Impress BT', 16)

    def __init__(self):
        self.window = Tk()
        self.window.title('shadoo robot')
        self.window.geometry('1250x700')

        self.battleCalc = BattleCalculator.Battle()
        self.ocr = OCRModule

        self.texts = [[''] * 3] * BattleGlobals.MAX_SUITS
        self.execs = [BooleanVar() for num in range(BattleGlobals.MAX_SUITS)]

        self.gagIcons = []

        for track in range(8):
            gags = []
            for gag in range(8):
                if BattleStrings.GAG_TRACK_NAMES[track] in ['Toon-Up', 'Trap', 'Lure']:
                    img = Image.open("resources/Unknown.png")
                else:
                    img = Image.open("resources/%s-%i.png" % (BattleStrings.GAG_TRACK_NAMES[track], gag))
                new_img = img.resize((80, 80))
                gags.append(ImageTk.PhotoImage(new_img))
            self.gagIcons.append(gags)

        self.buildGui(self.window)
        self.window.mainloop()

    def doOCR(self):
        suits = self.ocr.grabSuitHealths()

        if not suits:
            messagebox.showerror('OCR Error', 'There was an error fetching suit information through OCR.')
            return

        self.battleCalc.clearSuits()
        for suit in suits:
            self.battleCalc.addSuit(suit)

        for col in range(BattleGlobals.MAX_SUITS):
            if len(suits) > col:
                self.suitLevels[col].delete(0, END)
                self.suitLevels[col].insert(0, str(suits[col].level))
                self.suitHealth[col].delete(0, END)
                self.suitHealth[col].insert(0, str(suits[col].currHP))
                self.suitMaxHlt[col].delete(0, END)
                self.suitMaxHlt[col].insert(0, str(suits[col].maxHP))
                if suits[col].isExecutive:
                    self.execButton[col].select()
                else:
                    self.execButton[col].deselect()
            else:
                self.suitLevels[col].delete(0, END)
                self.suitHealth[col].delete(0, END)
                self.suitMaxHlt[col].delete(0, END)
                self.execButton[col].deselect()

    def calculate(self):
        self.battleCalc.clearSuits()

        for col in range(BattleGlobals.MAX_SUITS):
            if self.suitLevels[col].get().isdigit() and self.suitHealth[col].get().isdigit() and self.suitMaxHlt[col].get().isdigit():
                self.battleCalc.addSuit(Suit(int(self.suitHealth[col].get()), int(self.suitMaxHlt[col].get()), int(self.suitLevels[col].get()), self.execs[col].get(), ''))

        combos = self.battleCalc.calculate(sort = True, mode = True)

        if not combos:
            messagebox.showinfo('Null Combo', 'No combos exist for this set.')
            return

        currentIndex = -1
        for combo in range(self.battleCalc.MAX_COMBO_OUTPUT):
            self.comboFName[combo].config(text = '')
            self.comboFDetail[combo].config(text = '')

            for gag in range(4):
                self.comboGagIcons[combo][gag].config(image = self.gagIcons[0][0])

            if len(combos[combo]) <= 3:
                # if a failed combo
                continue
            else:
                currentIndex += 1
            self.comboFName[currentIndex].config(text = '%s - Cost: %i - Success Rate: %.1f%%' % (combos[combo][0], combos[combo][2], combos[combo][1] * 100))
            self.comboFDetail[currentIndex].config(text = combos[combo][5])

            for gag in range(len(combos[combo][3])):
                trackIndex = combos[combo][4][gag]
                if combos[combo][3][gag] != -1:
                    gagIndex = BattleGlobals.GAG_TRACK_VALUE[trackIndex].index(combos[combo][3][gag])
                else:
                    trackIndex = 0
                    gagIndex = 0
                
                self.comboGagIcons[currentIndex][gag].config(image = self.gagIcons[trackIndex][gagIndex])


    def buildGui(self, gui):
        self.title = Label(gui, text = 'bnuuy', font = GUI.HEADER_FONT)
        self.title.grid(column = 3, row = 0)

        self.genBt = Button(gui, text = ':eye:', command = self.doOCR, font = GUI.SUBHEADER_FONT)
        self.genBt.grid(column = 3, row = 1)

        self.calBt = Button(gui, text = 'calculate', command = self.calculate, font = GUI.SUBHEADER_FONT)
        self.calBt.grid(column = 4, row = 1)

        self.expLv = Label(gui, text = 'Level', font = GUI.MAIN_FONT)
        self.expLv.grid(column = 0, row = 3)

        self.expHP = Label(gui, text = 'HP', font = GUI.MAIN_FONT)
        self.expHP.grid(column = 0, row = 4)

        self.expMP = Label(gui, text = 'Max HP', font = GUI.MAIN_FONT)
        self.expMP.grid(column = 0, row = 5)

        self.suitHeader = [Label] * BattleGlobals.MAX_SUITS
        self.suitLevels = [Entry] * BattleGlobals.MAX_SUITS
        self.suitHealth = [Entry] * BattleGlobals.MAX_SUITS
        self.suitMaxHlt = [Entry] * BattleGlobals.MAX_SUITS
        self.execButton = [Checkbutton] * BattleGlobals.MAX_SUITS
        for col in range(BattleGlobals.MAX_SUITS):
            self.suitHeader[col] = Label(gui, text = 'suit %i' % (col + 1), font = GUI.SUBHEADER_FONT)
            self.suitHeader[col].grid(column = col + 1, row = 2)

            self.suitLevels[col] = Entry(gui, font = GUI.MAIN_FONT, textvariable = self.texts[col][0], width = 4)
            self.suitLevels[col].grid(column = col + 1, row = 3)

            self.suitHealth[col] = Entry(gui, font = GUI.MAIN_FONT, textvariable = self.texts[col][1], width = 4)
            self.suitHealth[col].grid(column = col + 1, row = 4)

            self.suitMaxHlt[col] = Entry(gui, font = GUI.MAIN_FONT, textvariable = self.texts[col][2], width = 4)
            self.suitMaxHlt[col].grid(column = col + 1, row = 5)
            self.execButton[col] = Checkbutton(gui, text = '.exe?', variable = self.execs[col])
            self.execButton[col].grid(column = col + 1, row = 6) 

        
        self.sbf = ScrollbarFrame(gui, width = 1150, height = 350)
        self.sbf.grid(column = 0, row = 7, columnspan = 5, rowspan= 2, padx = 25, pady = 25)
        self.sbf.pack_propagate(False)
        self.sbf.update()
        self.frame = self.sbf.scrolled_frame
        self.comboFrame = []
        self.comboFName = []
        self.comboFDetail = []
        self.comboGagIcons = []
        for comboDisplay in range(self.battleCalc.MAX_COMBO_OUTPUT):  
            self.comboFrame.append(LabelFrame(self.frame, bg = '#DDDDDD', width = 1125, height = 175))
            self.comboFrame[comboDisplay].grid(row = comboDisplay, column = 0)
            self.comboFrame[comboDisplay].grid_propagate(False)
            self.comboFName.append(Label(self.comboFrame[comboDisplay], text = '', font = GUI.SUBHEADER_FONT, bg = '#DDDDDD'))
            self.comboFName[comboDisplay].grid(row = 0, column = 0, columnspan = 2)
            self.comboFDetail.append(Label(self.comboFrame[comboDisplay], text = '', font = GUI.DESC_FONT, bg = '#DDDDDD'))
            self.comboFDetail[comboDisplay].grid(row = 1, column = 0, columnspan = 5)

            icons = []
            for gag in range(4):
                icons.append(Label(self.comboFrame[comboDisplay], width = 80, height = 80, image = self.gagIcons[0][0]))
                icons[gag].grid(row = 2, column = gag)
            self.comboGagIcons.append(icons)
               
                




a = GUI()