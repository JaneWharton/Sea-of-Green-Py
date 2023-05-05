
from const import *


class DeathFunction:
    def __init__(self, func):
        self.func=func

class Opaque: # obscures vision (NOT IMPLEMENTED)
    def __init__(self):
        pass

class Position:
    def __init__(self, x=0,y=0):
        self.x=x
        self.y=y

class Image:
    def __init__(self, char=0,fgcol=(0,0,0,),bgcol=(0,0,0,), priority=False):
        self.char = char
        self.fgcol = fgcol
        self.bgcol = bgcol
        self.priority = priority

class Animation:
    def __init__(self, speed=1, charList=[], looping=False):
        self.charList = charList
        self.index = 0
        self.speed = speed
        self.looping = looping
        
class Human: # controlled by human player
    def __init__(self):
        pass

class AI:
    def __init__(self, func=None):
        self.func = func

class Actor: 
    def __init__(self, ap=0):
        self.ap=int(ap)      #action points (energy/potential to act)
        
class Name:
    def __init__(self, name=""):
        self.name=name
class Value:
    # cost of goods,
    # amount of gold obtained when you kill enemy,
    # amount of gold player currently has on them
    def __init__(self, value=1):
        self.value=value
class Reward: # item gives you gold when you step on it
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

            # this only applies to NPCs:
            # matrix: If 0, you cannot move in that direction.
            # If >0, NPC can move more than 1 tile / turn.
            if matrix:
                self.matrix = matrix
            else:
                self.matrix = [0,0,0,
                               0,0,0,
                               0,0,0]

class Creature:
    def __init__(self):
        pass

class Mine:
    def __init__(self, damage=1, radius=0, timer=-1, volume=1):
        self.damage=damage
        self.radius=radius
        self.timer=timer
        self.volume=volume
    
class LightSource:
    def __init__(self, lightID, light):
        self.lightID=lightID
        self.light=light # lights.Light object

        
class SenseSight:
    def __init__(self, sense=30):
        self.fovID = -1
        self.sense = sense
##        self.events = []
class SenseHearing: # unimplemented... should we use this?
    def __init__(self, sense=30):
        self.events = []
        self.sense = sense

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


class HP:
    def __init__(self, hp_max=1):
        self.hp_max = hp_max
        self.hp = self.hp_max

# modules

class Modularity:
    def __init__(self):
        self.modules = {}
        self.num_slots = 3
        self.upgrade_kits = 0
    def get_module(self, index):
        return self.modules.get(index, None)



class Immune_Stun:
    def __init__(self):
        pass
class Immune_Fear:
    def __init__(self):
        pass
    
class Immune_Sound:
    def __init__(self):
        pass
class Resistant_Sound:
    def __init__(self):
        pass
class Weakness_Sound:
    def __init__(self):
        pass
class Immune_Physical:
    def __init__(self):
        pass
class Resistant_Physical:
    def __init__(self):
        pass
class Weakness_Physical:
    def __init__(self):
        pass
class Immune_Electricity:
    def __init__(self):
        pass
class Resistant_Electricity:
    def __init__(self):
        pass
class Weakness_Electricity:
    def __init__(self):
        pass
# no such thing as resistance or immunity to piercing damage
class Weakness_Piercing:
    def __init__(self):
        pass

class StatusElec:
    NAME = "electrified"
    def __init__(self, t=1):
        self.timer = t
class StatusStun:
    NAME = "stunned"
    def __init__(self, t=1):
        self.timer = t
class StatusInked:
    NAME = "inked"
    def __init__(self, t=1):
        self.timer = t
class StatusFear:
    NAME = "frightened"
    def __init__(self, t=1):
        self.timer = t
class StatusWeak:
    NAME = "weakened"
    def __init__(self, t=1):
        self.timer = t
class StatusFrenzied:
    NAME = "frenzied"
    def __init__(self, t=1):
        self.timer = t

STATUSES={
    "electrified" : StatusElec,
    "stunned" : StatusStun,
    "inked" : StatusInked,
    "frightened" : StatusFear,
    "weakened" : StatusWeak,
    "frenzied" : StatusFrenzied,
    }

















