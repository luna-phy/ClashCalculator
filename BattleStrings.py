GAG_TRACK_NAMES = (
    'Toon-Up',
    'Trap',
    'Lure',
    'Sound',
    'Squirt',
    'Zap',
    'Throw',
    'Drop'
)

GAG_NAMES = (
    ('Feather', 'Megaphone', 'Lipstick', 'Bamboo Cane', 'Pixie Dust', 'Juggling Cubes', 'Confetti Cannon', 'High Dive'),
    ('Banana Peel', 'Rake', 'Springboard', 'Marbles', 'Quicksand', 'Trapdoor', 'Wrecking Ball', 'TNT'),
    ('$1 Bill', 'Small Magnet', '$5 Bill', 'Big Magnet', '$10 Bill', 'Hypno-Goggles', '$50 Bill', 'Presentation'),
    ('Kazoo', 'Bike Horn', 'Whistle', 'Bugle', 'Aoogah', 'Elephant Trunk', 'Foghorn', 'Opera Singer'),
    ('Squirting Flower', 'Glass of Water', 'Squirt Gun', 'Water Balloon', 'Seltzer Bottle', 'Fire Hose', 'Storm Cloud', 'Geyser'),
    ('Joybuzzer', 'Rug', 'Balloon', 'Kart Battery', 'Taser', 'Broken Television', 'Tesla Coil', 'Lightning'),
    ('Cupcake', 'Fruit Pie Slice', 'Cream Pie Slice', 'Birthday Cake Slice', 'Whole Fruit Pie', 'Whole Cream Pie', 'Birthday Cake', 'Wedding Cake'),
    ('Flower Pot', 'Sandbag', 'Bowling Ball', 'Anvil', 'Big Weight', 'Safe', 'Boulder', 'Grand Piano')
)

def localizeGag(gag, track) -> str:
    return GAG_NAMES[track][gag]

POSITIONS = (
    'Far Left',
    'Mid Left',
    'Mid Right',
    'Far Right',
    '(No Target)'
)

POSITIONS_THREE = (
    'Left',
    'Middle',
    'Right',
    '',
    '(No Target)'
)

POSITIONS_TWO = (
    'Left',
    'Right',
    'Left',
    'Right',
    '(No Target)'
)

POSITIONS_ONE = (
    'Middle',
    'Middle',
    'Middle',
    'Middle',
    '(No Target)'
)

FREE_SLOT = 'Any Gag'

ZAP_COMBOS = (
    'xx--',
    'x-x-',
    '-xx-',
    '-x-x',
    '--xx',
    'x--x'
)

# gui strings
GUIWindowTitle = 'shadoo robot'
GUIMsgBoxTitleNoCombo = 'No Combos'
GUIMsgBoxMessageNoCombo = 'No combos exist for this set.'
GUIMsgBoxTitleOCRError = 'OCR Error'
GUIMsgBoxMessageOCRError = 'There was an error fetching suit information through OCR.'
GUIDisplayTitle = 'bnuuy calculator'
GUIOCRButton = ':eye:'
GUICalcButton = 'calculate'
GUILevelLabel = 'Level:'
GUIHealthLabel = 'Current HP:'
GUIMaxHPLabel = 'Max HP:'
GUISuitHeader = 'Suit %i'
GUIExecutive = '.exe?'
GUIComboFrameNameLabel = '%s - Cost: %i - Success Rate: %.1f%%'