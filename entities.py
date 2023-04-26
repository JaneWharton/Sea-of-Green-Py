'''
    entities.py
    Sea of Green
'''

import esper
import components as cmp
import game

##class Gear_Propeller:
##    def __init__(self):
##        self.cost = 2
##        self.slots = 1
##        self.mobility = [0,0,0,
##                         1,0,1,
##                         0,0,0,]
##        self.utility = [0 for _ in range(9)]
        


def create_player(x=0,y=0,energyMax=64,airMax=64):
    world = game.world()
    ent = world.create_entity(
        cmp.Position(x,y),
        cmp.Image(2, COL_ACCENT, COL_BLACK),
        cmp.Human(),
        cmp.EnergyCapacity(energyMax,energyMax),
        cmp.AirCapacity(airMax,airMax),
        cmp.Mobility(),
        cmp.Modularity()
        )
    
