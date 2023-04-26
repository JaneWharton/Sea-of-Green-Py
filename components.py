

class Position:
    def __init__(self, x=0,y=0):
        self.x=x
        self.y=y

class Image:
    def __init__(self, keycode=0,fgcol=(0,0,0,),bgcol=(0,0,0,)):
        self.keycode = keycode
        self.fgcol = fgcol
        self.bgcol = bgcol
        
class Human: # controlled by human player
    def __init__(self, playerName=""):
        self.playerName = playerName

class AI:
    def __init__(self, ai=None):
        self.ai = ai

class GreaterForm: # when you power up, enhance to higher form
    def __init__(self, form=None):
        self.form=form
class LesserForm: # when you get damaged, change to lesser form
    def __init__(self, form=None):
        self.form=form

class EnergyCapacity:
    def __init__(self, energy=0, energyMax=0):
        self.energy=energy
        self.energyMax=energyMax
class AirCapacity:
    def __init__(self, air=0, airMax=0):
        self.air=air
        self.airMax=airMax

class Modularity:
    def __init__(self):
        self.modules = []
        self.num_slots = 3

class Mobility:
    def __init__(self, matrix=None):

        # matrix: how much energy it costs to move in given direction
        # If -1, you cannot move in that direction.
        if matrix:
            self.matrix = matrix
        else:
            self.matrix = [-1,-1,-1,
                           -1,-1,-1,
                           -1,-1,-1,]



class Gear_Propeller:
    __ID = GEAR_PROPELLER
    __COST = 1
    ENERGY = [8, 6, 4] # Level 0, 1, 2
    def __init__(self):
        self.level = 0
class Gear_BallastTank:
    __ID = GEAR_BALLASTTANK
    __COST = 1
    ENERGY = [6, 4, 3]
    def __init__(self):
        self.level = 0
class Gear_SonarPulse:
    __ID = GEAR_SONARPULSE
    __COST = 2
    ENERGY = [24, 28, 32]
    DAMAGE = [1, 1, 2]
    RADIUS = [3, 4, 5]
    def __init__(self):
        self.level = 0
class Gear_Torpedo:
    __ID = GEAR_TORPEDO
    __COST = 2
    ENERGY = [1, 1, 1]
    DAMAGE = [2, 2, 3]
    USES = [4, 8, 8]
    def __init__(self):
        self.level = 0
        self.quantity = self.USES[0]
class Gear_Mine:
    __ID = GEAR_MINE
    __COST = 2
    ENERGY = [0, 0, 0]
    DAMAGE = [2, 3, 4]
    USES = [6, 10, 14]
    def __init__(self):
        self.level = 0
        self.quantity = self.USES[0]
class Gear_DepthCharge:
    __ID = GEAR_DEPTHCHARGE
    __COST = 2
    ENERGY = [0, 0, 0]
    DAMAGE = [1, 2, 3]
    RADIUS = [3, 3, 3]
    USES = [2, 4, 6]
    TIMER = [5, 5, 5]
    def __init__(self):
        self.level = 0
        self.quantity = self.USES[0]
class Gear_GrapplingHook:
    __ID = GEAR_GRAPPLINGHOOK
    __COST = 8
    ENERGY = [12, 10, 8]
    DAMAGE = [1, 1, 1]
    RANGE = [5, 10, 15]
    def __init__(self):
        self.level = 0
class Gear_:
    __ID = 0
    __COST = 2
    def __init__(self):
        self.level = 1




















