
from const import *


class Position:
    def __init__(self, x=0,y=0):
        self.x=x
        self.y=y

class Image:
    def __init__(self, char=0,fgcol=(0,0,0,),bgcol=(0,0,0,)):
        self.char = char
        self.fgcol = fgcol
        self.bgcol = bgcol
        
class Human: # controlled by human player
    def __init__(self):
        pass

class AI:
    def __init__(self, ai=None):
        self.ai = ai

class Actor: 
    def __init__(self, ap=0):
        self.ap=int(ap)      #action points (energy/potential to act)
        
class Name:
    def __init__(self, name=""):
        self.name=name
class Value:
    def __init__(self, value=1):
        self.value=value
class Mass:
    def __init__(self, mass=1):
        self.mass=mass

class GreaterForm: # when you power up, enhance to higher form
    def __init__(self, form=None):
        self.form=form
class LesserForm: # when you get damaged, change to lesser form
    def __init__(self, form=None):
        self.form=form

class Child:
    def __init__(self, parent):
        self.parent=parent
class Flags:
    def __init__(self, *args):
        self.flags=set()
        for arg in args:
            self.flags.add(arg)
            
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

class Creature:
    def __init__(self):
        pass
    
class LightSource:
    def __init__(self, lightID, light):
        self.lightID=lightID
        self.light=light # lights.Light object

        
class SenseSight:
    def __init__(self):
        self.fovID = -1
        self.sense = 200
##        self.events = []
class SenseHearing: # unimplemented... should we use this?
    def __init__(self):
        self.events = []
        self.sense = 200

# submarine

class OxygenTank:
    def __init__(self, tier=0):
        self.set_tier(tier)
    def set_tier(self, tier=0):
        self.tier = tier
        self.oxygen_max = OXYGEN_TIERS[tier][1]
        self.oxygen = self.oxygen_max
        self.cost = OXYGEN_TIERS[tier][0]
class Battery:
    def __init__(self, tier=0):
        self.set_tier(tier)
    def set_tier(self, tier=0):
        self.tier = tier
        self.energy_max = BATTERY_TIERS[tier][1]
        self.energy = self.energy_max
        self.cost = BATTERY_TIERS[tier][0]
class Engine:
    def __init__(self, tier=0):
        self.set_tier(tier)
    def set_tier(self, tier=0):
        self.tier = tier
        self.energy_turn = ENGINE_TIERS[tier][1]
        self.cost = ENGINE_TIERS[tier][0]
class Hull:
    def __init__(self, tier=0):
        self.set_tier(tier)
    def set_tier(self, tier=0):
        self.tier = tier
        self.hp_max = HULL_TIERS[tier][1]
        self.hp = self.hp_max
        self.cost = HULL_TIERS[tier][0]



# modules

class Modularity:
    def __init__(self):
        self.modules = []
        self.num_slots = 3
        self.upgrade_kits = 0
    



class StatusElec:
    def __init__(self, duration=1):
        self.duration = duration

















