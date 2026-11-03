WIDTH = 1000
HEIGHT = 680
FPS = 60

NUM_BOIDS = 300     #default number of boids(at first)
EDGE_MARGIN = 80

VISUAL_DIST = 70.0
PROTECTED_DIST = 26.0
JOIN_DIST = 32.0
ALERT_DIST = 135.0

WEIGHT_SEP = 0.28
WEIGHT_ALIGN = 0.04
WEIGHT_COH = 0.005
WEIGHT_EVADE = 0.45
WEIGHT_OBS = 0.65
WANDER = 0.06
EDGE_TURN = 0.45

BG_COLOR = (16, 20, 28)
PANEL_BG = (25, 32, 45)
PANEL_BORDER = (60, 75, 100)
TEXT_COLOR = (235, 242, 250)
MUTED_TEXT = (130, 145, 168)

BLUE = (65, 160, 255)
GREEN = (50, 210, 125)
ORANGE = (255, 150, 45)
RED = (250, 65, 65)

TRAIL_BLUE = (45, 110, 195)
TRAIL_GREEN = (35, 150, 85)
TRAIL_ORANGE = (195, 110, 35)
TRAIL_RED = (200, 50, 50)


class Rules:
    def __init__(self):
        self.sep = False
        self.align = False
        self.coh = False
        self.join = False
        self.evade = True
        self.avoid_obs = True