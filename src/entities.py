'''
    entities.py
    Sea of Green
'''

import esper

from const import *
import components as cmp
import rogue as rog
import game


# Gear / Modules / Modularity

def add_module(ent, module):
    world=rog.world()
    compo = world.component_for_entity(ent, cmp.Modularity)
    if len(compo.modules) < compo.num_slots:
        compo.modules.append(module)
    else:
        print("FAILED TO ADD MODULE")
        rog.msg("Cannot add module; slot limit exceeded.")
            
class Gear_Screw: # permits left and right movement
    NAME = "Screw"
    __ID = GEAR_SCREW
    __COST = 50
    ENERGY = [8, 7, 6, 5] # Level 0, 1, 2, 3
    VOLUME = [48, 40, 32, 24]
    def __init__(self):
        self.level = 0
class Gear_BallastTank: # permits up and down movement
    NAME = "Ballast Tanks"
    __ID = GEAR_BALLASTTANK
    __COST = 50
    ENERGY = [7, 6, 5, 4]
    VOLUME = [6, 5, 4, 3]
    def __init__(self):
        self.level = 0
class Gear_PumpJet: # permits cardinal movement
    NAME = "Pump-Jets"
    __ID = GEAR_PUMPJET
    __COST = 200
    ENERGY = [10, 9, 8, 7] # Level 0, 1, 2, 3
    VOLUME = [12, 10, 8, 6]
    def __init__(self):
        self.level = 0
class Gear_ControlSurfaces: # permits diagonal movement
    NAME = "Control Surfaces"
    __ID = GEAR_CONTROLSURFACE
    __COST = 150
    ENERGY = [9, 8, 7, 6] # Level 0, 1, 2, 3
    VOLUME = [24, 20, 16, 12]
    def __init__(self):
        self.level = 0
class Gear_SonarPulse: # AOE damage around player;
                        # stuns some enemies; scares some enemies
    NAME = "Sonar Pulse"
    __ID = GEAR_SONARPULSE
    __COST = 100
    ENERGY = [40, 50, 60, 70]
    DAMAGE = [1, 1, 1, 1]
    RADIUS = [3, 4, 5, 6]
    VOLUME = [64, 80, 96, 108]
    DAMAGETYPE = DMG_SOUND
    def __init__(self):
        self.level = 0
class Gear_InkJet:  # Shoot ink in target cardinal direction, and move in the opposite direction
                    # Ink coats target, blinding them. Also obscures vision
    NAME = "Ink Jets"
    __ID = GEAR_INKCLOUD
    __COST = 150
    ENERGY = [6, 5, 4, 3]
    DAMAGE = [0, 0, 0, 1]
    MOVEMENT = [1, 1, 2, 3] # maximum amount of tiles you can move
    DURATION = [3, 6, 10, 15] # duration of ink cloud
    USES = [4, 8, 16, 32]
    VOLUME = [32, 24, 20, 18]
    def __init__(self):
        self.level = 0
class Gear_Torpedo: # create bubbles behind player; fire missile forward cardinal direction
    NAME = "Torpedos"
    __ID = GEAR_TORPEDO
    __COST = 100
    ENERGY = [1, 1, 1, 1]
    DAMAGE = [2, 2, 2, 2]
    USES = [4, 8, 12, 16]
    VOLUME = [120, 120, 120, 120]
    DAMAGETYPE = DMG_PHYSICAL
    def __init__(self):
        self.level = 0
        self.quantity = self.USES[0]
class Gear_SuperTorpedo: # create bubbles all along path of missile;
                         # fire missile forward cardinal direction
                         # destroys walls on contact
    NAME = "Super Torpedos"
    __ID = GEAR_TORPEDO
    __COST = 500
    ENERGY = [2, 2, 2, 2]
    DAMAGE = [4, 5, 6, 7]
    USES = [2, 3, 4, 5]
    VOLUME = [150, 150, 150, 150]
    DAMAGETYPE = DMG_PHYSICAL
    def __init__(self):
        self.level = 0
        self.quantity = self.USES[0]
class Gear_Mine: # move up one tile; drop single-target mine downward. Stuns on contact.
    NAME = "Mines"
    __ID = GEAR_MINE
    __COST = 150
    ENERGY = [0, 0, 0, 0]
    DAMAGE = [1, 1, 1, 1]
    USES = [10, 15, 20, 30]
    VOLUME = [80, 80, 80, 80]
    DAMAGETYPE = DMG_PHYSICAL
    def __init__(self):
        self.level = 0
        self.quantity = self.USES[0]
class Gear_DepthCharge: # drop powerful time bomb that detonates within a small blast radius
    NAME = "Depth Charges"
    __ID = GEAR_DEPTHCHARGE
    __COST = 300
    ENERGY = [0, 0, 0, 0]
    DAMAGE = [2, 2, 3, 3]
    RADIUS = [2, 2, 2, 3]
    USES = [2, 4, 6, 8]
    TIMER = [5, 5, 5]
    VOLUME = [100, 100, 120, 120]
    DAMAGETYPE = DMG_PHYSICAL
    def __init__(self):
        self.level = 0
        self.quantity = self.USES[0]
class Gear_Harpoon: # shoot missile forward cardinal direction
                    # pull target to player, or player to target based on mass
                    # moves up to X squares based on level
    NAME = "Harpoon"
    __ID = GEAR_HARPOON
    __COST = 500
    ENERGY = [32, 30, 28, 26]
    DAMAGE = [1, 1, 1, 1]
    RANGE = [5, 10, 20, 30]
    PULL = [2, 3, 4, 5]
    VOLUME = [60, 55, 50, 45]
    DAMAGETYPE = DMG_PHYSICAL
    def __init__(self):
        self.level = 0
class Gear_Electrifier: # shock adjacent target to left or right
    NAME = "Electrifier"
    __ID = GEAR_ELECTRIFIER
    __COST = 200
    ENERGY = [50, 60, 70, 80]
    DAMAGE = [2, 2, 3, 4]
    STUN = [3, 5, 6, 7]
    VOLUME = [48, 54, 60, 66]
    DAMAGETYPE = DMG_ELECTRIC
    def __init__(self):
        self.level = 0
class Gear_:
    NAME = ""
    __ID = 0
    __COST = 2
    ENERGY = [0, 0, 0, 0]
    def __init__(self):
        self.level = 1

    
