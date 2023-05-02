'''
    rogue.py
    Softly Into the Night, a sci-fi/Lovecraftian roguelike
    Copyright (C) 2020 Jacob Wharton.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>

    This file glues everything together.
'''

'''
    TODO: pickle to save state
    TODO: reproduceable pseudo random generator (state saved using pickle)
        https://stackoverflow.com/questions/5012560/how-to-query-seed-used-by-random-random
'''

import esper
import tcod as libtcod
import math
import time

from const import *
from colors import COLORS as COL
import components as cmp
import processors as proc
import orangio  as IO
import entities
import game
import lights
import managers
import maths
import misc
import player
import tilemap



    #----------------#
    # global objects #
    #----------------#
            
class Rogue:
    occupations={}
    et_managers={} #end of turn managers
    bt_managers={} #beginning of turn managers
    c_managers={} #const managers
    c_entities={} #const entities
    manager = None # current active game state manager
    manager_listeners = [] #
    fov_maps = []
    # boolean flags
    allow_warning_msp = True    # for warning prompt for very slow move speed
    _pause_menu_key_listener = False

    @classmethod
    def pause_menu_key_listener(cls):
        cls._pause_menu_key_listener = True
    @classmethod
    def resume_menu_key_listener(cls):
        cls._pause_menu_key_listener = False
    @classmethod
    def menu_key_listener_is_paused(cls):
        return cls._pause_menu_key_listener
    
    @classmethod
    def run_endTurn_managers(cls, pc):
        for v in cls.et_managers.values():
            v.run(pc)
    @classmethod
    def run_beginTurn_managers(cls, pc):
        for v in cls.bt_managers.values():
            v.run(pc)

    
##    @classmethod
##    def create_fov_maps(cls):
##        cls.fov_maps.append(cls.map.fov_map)
    @classmethod
    def create_settings(cls): # later controllers might depend on settings
        cls.settings = game.GlobalSettings()
        cls.settings.read() # go ahead and read/apply settings
        cls.settings.apply()
    @classmethod
    def create_world(cls):      cls.world = esper.World()
    @classmethod
    def create_controller(cls): cls.ctrl = game.Controller()
    @classmethod
    def create_window(cls):
        cls.window = game.Window(
            cls.settings.window_width, cls.settings.window_height
            )
    @classmethod
    def create_consoles(cls):
        cls.con = game.Console(window_w(),window_h())
    @classmethod
    def create_data(cls):       cls.data = game.GameData()
    @classmethod
    def create_map(cls, w, h):
        cls.map = tilemap.TileMap(w,h)
    @classmethod
    def create_clock(cls):      cls.clock = game.Clock()
    @classmethod
    def create_updater(cls):    cls.update = game.Update()
    @classmethod
    def create_view(cls):       cls.view = game.View(view_port_w(),view_port_h(), ROOMW,ROOMH)
    @classmethod
    def create_log(cls):        cls.log = game.MessageLog()
    @classmethod
    def create_savedGame(cls):  cls.savedGame = game.SavedGame()
    @classmethod
    def create_player(cls, sx,sy):
        cls.pc = player.chargen(sx, sy)
    @classmethod
    def create_processors(cls):
        #Processor class, priority (higher = processed first)
##        cls.world.add_processor(proc.MetersProcessor(), 101)
        cls.world.add_processor(proc.StatusProcessor(), 100)
        cls.world.add_processor(proc.UpkeepProcessor(), 93)
        cls.world.add_processor(proc.TimersProcessor(), 90)
            # AI function and queued actions processor
        cls.world.add_processor(proc.ActorsProcessor(), 50)
    
    @classmethod
    def create_perturn_managers(cls):
        '''
            constant, per-turn managers, ran each turn
        '''
        #ran at beginning of turn
            # (No managers run at beginning of turn currently.)
            
        #ran at end of turn (before player turn -- player turn is the very final thing to occur on any given turn)
            # None
            # Why were sights and sounds here? Bad idea.
    
    @classmethod
    def create_const_managers(cls):
        '''
            constant managers, manually ran
        '''
        cls.c_managers.update({'events' : managers.Manager_Events()})
            # todo: update event manager to account for sights, sounds, etc.
        cls.c_managers.update({'lights' : managers.Manager_Lights()})
        cls.c_managers.update({'fov' : managers.Manager_FOV()})
        cls.c_managers.update({'refresh' : managers.Manager_Refresh()})

    @classmethod
    def create_const_entities(cls):
        pass
        # stone wall
##        _ent_stone_wall = cls.world.create_entity(
##            cmp.Name("stone wall"),
##            cmp.Form(mat=MAT_STONE, shape=SHAPE_WALL),
##            cmp.Stats(hp=1000, arm=20, pro=24),
##            )
##        cls.c_entities.update({ENT_STONE_WALL : _ent_stone_wall})
    # end def
    
#/Rogue


    #----------------#
    #   Functions    #
    #----------------#


    # Rogue
def const_ent(ent): return Rogue.c_entities[ent]
def _ent_stone_wall(): return const_ent(ENT_STONE_WALL)
def run_refresh_manager(): # run every time ANY input is received
    Rogue.c_managers['refresh'].run()
def disable_refresh_manager():
    print("turn off")
    Rogue.c_managers['refresh'].disable()
def enable_refresh_manager():
    print("turn on again")
    Rogue.c_managers['refresh'].enable()

# global warning flags
def allow_warning_msp():
    return Rogue.allow_warning_msp
def reset_warning_msp():
    Rogue.allow_warning_msp = True
def expire_warning_msp():
    Rogue.allow_warning_msp = False
    

# global objects
def settings():     return Rogue.settings

# world
def world():    return Rogue.world

# player
def pc():       return Rogue.pc
def is_pc(ent): return (ent==Rogue.pc)

# log
def get_time(turn):
    tt = turn + STARTING_TIME
    day = 1 + tt // 86400
    hour = (tt // 3600) % 24
    minute = (tt // 60) % 60
    second = tt % 60
    return "D{},{:02d}:{:02d}:{:02d}".format(day, hour, minute, second)
def logNewEntry():
    Rogue.log.drawNew()
def msg(txt, col=None):
    if col is None: #default text color
        col=COL['white']
    Rogue.log.add(txt, str(get_time(get_turn())) )
def msg_clear():
    clr=libtcod.console_new(msgs_w(), msgs_h())
    libtcod.console_blit(clr, 0,0, msgs_w(),msgs_h(),  con_game(), 0,0)
    libtcod.console_delete(clr)

# game data
def dlvl():             return Rogue.data.dlvl() #current dungeon level of player
def level_up():         Rogue.data.dlvl_update(Rogue.data.dlvl() + 1)
def level_down():       Rogue.data.dlvl_update(Rogue.data.dlvl() - 1)
def level_set(lv):
    # TODO: code for loading / unloading levels into the map
    # unload current map from Rogue.map into the levels dict
    # load new map into Rogue.map from the levels dict
    # update dlvl
    Rogue.data.dlvl_update(lv)

# clock
def turn_pass():        Rogue.clock.turn_pass()
def get_turn():         return Rogue.clock.turn

# map
def tilefree(x,y):
    return Rogue.map.tilefree(x,y)
def getmap(z=None): # get TileMap obj for the corresponding dungeon level
    if z is None:
        z = dlvl()
    if z == dlvl():
        return Rogue.map
    else:
        level_set(z)
        return Rogue.map
def tile_get(x,y):          return Rogue.map.get_char(x,y)
def tile_height(x,y):       return Rogue.map.get_height(x,y)
def tile_change(x,y,char):
    updateNeeded=Rogue.map.tile_change(x,y,char)
    if updateNeeded:
        update_all_fovmaps()
def map_reset_lighting():   Rogue.map.grid_lighting_init()
def tile_lighten(x,y,value):Rogue.map.tile_lighten(x,y,value)
def tile_darken(x,y,value): Rogue.map.tile_darken(x,y,value)
def get_actual_light_value(x,y):
    return Rogue.map.get_light_value(x,y)
def get_perceived_light_value(x,y):
    return Rogue.map.get_perceived_light_value(x,y)

def grid_remove(ent): #remove thing from grid of things
    return Rogue.map.remove_thing(ent)
def grid_insert(ent): #add thing to the grid of things
    return Rogue.map.add_thing(ent)
def grid_fluids_insert(obj):    Rogue.map.grid_fluids[obj.x][obj.y].append(obj)
def grid_fluids_remove(obj):    Rogue.map.grid_fluids[obj.x][obj.y].remove(obj)
def increment_wave_functions():
    Rogue.map.increment_wave_functions()

# updater
def update_base():      Rogue.update.base()
#def update_pcfov():     Rogue.update.pcfov()
def update_game():      Rogue.update.game()
def update_msg():       Rogue.update.msg()
def update_hud():       Rogue.update.hud()
def update_final():     Rogue.update.final()
#apply all updates if applicable
def game_update():      Rogue.update.update()

# consoles
def con_game():             return Rogue.con.game
def con_final():            return Rogue.con.final

# controller
def end():                  Rogue.ctrl.end()
def game_state():           return Rogue.ctrl.state
def game_is_running():      return Rogue.ctrl.isRunning
def game_set_state(state="normal"):
    print("$---Game State changed from {} to {}".format(game_state(), state))
    Rogue.ctrl.set_state(state)
def game_resume_state():    return Rogue.ctrl.resume_state
def set_resume_state(state):Rogue.ctrl.set_resume_state(state)

# window
def window_w():         return Rogue.window.root.w
def window_h():         return Rogue.window.root.h
def view_port_x():      return Rogue.window.scene.x
def view_port_y():      return Rogue.window.scene.y
def view_port_w():      return Rogue.window.scene.w
def view_port_h():      return Rogue.window.scene.h
def hud_x():            return Rogue.window.hud.x
def hud_y():            return Rogue.window.hud.y
def hud_w():            return Rogue.window.hud.w
def hud_h():            return Rogue.window.hud.h
def msgs_x():           return Rogue.window.msgs.x
def msgs_y():           return Rogue.window.msgs.y
def msgs_w():           return Rogue.window.msgs.w
def msgs_h():           return Rogue.window.msgs.h
def set_hud_left():     Rogue.window.set_hud_left()
def set_hud_right():    Rogue.window.set_hud_right()


    # global return values. Functions can modify this as an additional
        #  "return" value list.
class Return:
    values=None
def globalreturn(*args): Return.values = args
def fetchglobalreturn():
    ret=Return.values
    Return.values=None
    return ret


# BITWISE OPERATORS ON BYTES OBJECT / BYTEARRAY

def AND(abytes, bbytes):
    return bytes([a & b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])
def NAND(abytes, bbytes):
    return NOT(AND(abytes, bbytes)) # OR(NOT, NOT)
def OR(abytes, bbytes):
    return bytes([a | b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])
def NOR(abytes, bbytes):
    return NOT(OR(abytes, bbytes))
def XOR(abytes, bbytes):
    return bytes([a ^ b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])
def NOT(abytes): # just XOR w/ mask full of 1's
    return XOR(abytes, bytes([255 for _ in range(len(abytes))]))
def GETBYTES(abytes):
    for byte in abytes:
        yield byte


    #------------------------#
    # functions from modules #
    #------------------------#

# orangio

def init_keyBindings():
    IO.init_keyBindings()


# game

def dbox(x,y,w,h,text='', wrap=True,border=0,margin=0,con=-1,disp='poly'):
    '''
        x,y,w,h     location and size
        text        display string
        border      border style. None = No border
        wrap        whether to use automatic word wrapping
        margin      inside-the-box text padding on top and sides
        con         console on which to blit textbox, should never be 0
                        -1 (default) : draw to con_game()
        disp        display mode: 'poly','mono'
    '''
    if con==-1: con=con_game()
    misc.dbox(x,y,w,h,text, wrap=wrap,border=border,margin=margin,con=con,disp=disp)
    
def makeConBox(w,h,text):
    con = libtcod.console_new(w,h)
    dbox(0,0, w,h, text, con=con, wrap=False,disp='mono')
    return con




    # printing functions #

#@debug.printr
def refresh():  # final to root and flush
    libtcod.console_blit(con_final(), 0,0,window_w(),window_h(),  0, 0,0)
    libtcod.console_flush()
#@debug.printr
def render_gameArea(pc) :
    con = Rogue.map.render_gameArea(pc, 0,0,ROOMW,ROOMH)
    libtcod.console_clear(con_game()) # WHY ARE WE DOING THIS?
    libtcod.console_blit(con, 0,0,ROOMW,ROOMH,
                         con_game(), view_port_x(),view_port_y())
#@debug.printr
def render_hud(pc) :
    con = misc.render_hud(hud_w(),hud_h(), pc, get_turn(), dlvl() )
    libtcod.console_blit(con,0,0,0,0, con_game(),hud_x(),hud_y())
def clear_final():
    libtcod.console_clear(con_final())
#@debug.printr
def blit_to_final(con,xs,ys, xdest=0,ydest=0): # window-sized blit to final
    libtcod.console_blit(con, xs,ys,window_w(),window_h(),
                         con_final(), xdest,ydest)
#@debug.printr
def alert(text=""):    # message that doesn't go into history
    dbox(msgs_x(),msgs_y(),msgs_w(),msgs_h(),text,wrap=False,border=None,con=con_final())
    refresh()



# Error checking
class ComponentException(Exception):
    ''' raised when an entity lacks an expected component. '''
    pass

def asserte(ent, condition, errorstring=""): # "ASSERT Entity"
    ''' ASSERT condition condition satisifed, else raise error
        and print ID info about the Entity ent.'''
    if not condition:
        # name
        if Rogue.world.has_component(ent, cmp.Name):
            entname="with name '{}'".format(
                Rogue.world.component_for_entity(ent, cmp.Name).name)
        else:
            entname="<NO NAME>"
        # position
        if Rogue.world.has_component(ent, cmp.Position):
            entposx=Rogue.world.component_for_entity(ent, cmp.Position).x
            entposy=Rogue.world.component_for_entity(ent, cmp.Position).y
        else:
            entposx = entposy = -1
        # message
        print("ERROR: rogue.py: function getms: entity {e} {n} at pos ({x},{y}) {err}".format(
            e=ent, n=entname, x=entposx, y=entposy, err=errorstring))
        raise ComponentException
# end def




    # "Fun"ctions #

def ceil(f): return math.ceil(f)
def line(x1,y1,x2,y2):
    for tupl in misc.Bresenham2D(x1,y1,x2,y2):
        yield tupl
def in_range(x1,y1,x2,y2,Range):
    return (maths.dist(x1,y1, x2,y2) <= Range + .34)
def around(f): # round with an added constant to nudge values ~0.5 up to 1 (attempt to get past some rounding errors)
    return round(f + 0.00001)
def about(f1, f2): # return True if the two floating point values are very close to the same value
    return (abs(f1-f2) < 0.00001)
def slt(f1, f2): # significantly less than (buffer against floating point errors)
    return (f1 + 0.00001 < f2)
def sgt(f1, f2): # significantly greater than (buffer against floating point errors)
    return (f1 - 0.00001 > f2)
def sign(n):
    if n>0: return 1
    if n<0: return -1
    return 0
def numberplace(i): # convert integer to numbering position / numbering place / number position / number place
    imod10 = i % 10
    imod100 = i % 100
    if (imod100 < 11 or imod100 > 13): # except *11, *12, *13 which end in "th"
        if imod10==1: return "{}st".format(i) # e.g. 21st
        if imod10==2: return "{}nd".format(i) # e.g. 172nd
        if imod10==3: return "{}rd".format(i) # e.g. 3rd
    return "{}th".format(i) # e.g. 212th


# component getters | parent / child functions
def getpos(ent):
    ''' # get parent position if applicable else self position
        Returns: Position component.
        Global Returns: whether or not the component belongs
            to a parent (True) or not (False)
    '''
    if Rogue.world.has_component(ent, cmp.Child):
        parent=Rogue.world.component_for_entity(ent, cmp.Child).parent
        globalreturn(True)
        return Rogue.world.component_for_entity(parent, cmp.Position)
    globalreturn(False)
    return Rogue.world.component_for_entity(ent, cmp.Position)
def getname(ent):
    return Rogue.world.component_for_entity(ent, cmp.Name).name
def getinv(ent):
    return Rogue.world.component_for_entity(ent, cmp.Inventory).data
def get_value(ent):
    return Rogue.world.component_for_entity(ent, cmp.Value).value

# tilemap
def thingat(x,y):       return Rogue.map.thingat(x,y) #entity at
def thingsat(x,y):      return Rogue.map.thingsat(x,y) #list
def inanat(x,y):        return Rogue.map.inanat(x,y) #inanimate entity at
def monat (x,y):        return Rogue.map.monat(x,y) #monster at
def solidat(x,y):       return Rogue.map.solidat(x,y) #solid entity at
def wallat(x,y):        return (not Rogue.map.get_nrg_cost_enter(x,y) ) #tile walldef fluidsat(x,y):      return Rogue.et_managers['fluids'].fluidsat(x,y) #list
def lightsat(x,y):      return Rogue.map.lightsat(x,y) #list
    # calculating cost to move across tiles
def cost_enter(x,y):    return Rogue.map.get_nrg_cost_enter(x,y)
def cost_leave(x,y):    return Rogue.map.get_nrg_cost_leave(x,y)
def cost_move(xf,yf,xt,yt,data):
    return Rogue.map.path_get_cost_movement(xf,yf,xt,yt,data)
    # checking for in bounds / out of bounds / outside of room boundary
def is_in_grid_x(x):    return (x>=0 and x<ROOMW)
def is_in_grid_y(y):    return (y>=0 and y<ROOMH)
def is_in_grid(x,y):    return (x>=0 and x<ROOMW and y>=0 and y<ROOMH)


    #------------------#
    # entity functions #
    #------------------#

def entity_exists(ent):
    return ent in world._entities.keys()

# getms: GET Modified Statistic (base stat + modifiers (permanent and conditional))
def getms(ent, _var): # NOTE: must set the DIRTY_STATS flag to true whenever any stats or stat modifiers change in any way! Otherwise the function will return an old value!
    world=Rogue.world
    asserte(ent,world.has_component(ent,cmp.ModdedStats),"has no ModdedStats component.")
    if on(ent, DIRTY_STATS): # dirty; re-calculate the stats first.
        makenot(ent, DIRTY_STATS) # make sure we don't get caught in infinite loop...
        modded=_update_stats(ent)
        return modded.__dict__[_var]
    return Rogue.world.component_for_entity(ent, cmp.ModdedStats).__dict__[_var]
def getbase(ent, _var): # get Base statistic
    return Rogue.world.component_for_entity(ent, cmp.Stats).__dict__[_var]
# SET Stat -- set stat stat to value val set base stat 
def sets(ent, stat, val):
    Rogue.world.component_for_entity(ent, cmp.Stats).__dict__[stat] = val
    make(ent, DIRTY_STATS)
# ALTer Stat -- change stat stat by val value
def alts(ent, stat, val):
    Rogue.world.component_for_entity(ent, cmp.Stats).__dict__[stat] += val
    make(ent, DIRTY_STATS)

# flags
        # set flags
def on(ent, flag):
    return flag in Rogue.world.component_for_entity(ent, cmp.Flags).flags
def make(ent, flag):
    Rogue.world.component_for_entity(ent, cmp.Flags).flags.add(flag)
def makenot(ent, flag):
    Rogue.world.component_for_entity(ent, cmp.Flags).flags.remove(flag)


# inventory give/take items
def give(ent,item):
    assert(Rogue.world.has_component(item, cmp.Encumberance))
    
    if get_status(item, cmp.StatusBurn):
        burn(ent, FIRE_BURN)
        cooldown(item)
    
    grid_remove(item)
    Rogue.world.component_for_entity(ent, cmp.Inventory).data.append(item)
    Rogue.world.add_component(item, cmp.Carried(ent))
    Rogue.world.add_component(item, cmp.Child(ent))
# end def

def take(ent,item):
##    print("taken!")
    Rogue.world.component_for_entity(ent, cmp.Inventory).data.remove(item)
    Rogue.world.remove_component(item, cmp.Carried)
    Rogue.world.remove_component(item, cmp.Child)
    if Rogue.world.has_component(item, cmp.Equipped):
        Rogue.world.remove_component(item, cmp.Equipped)
    if Rogue.world.has_component(item, cmp.Held):
        Rogue.world.remove_component(item, cmp.Held)

def add_module(ent, slot, module): # add gear module to Modularity component
    entities.add_module(ent, slot, module)
def remove_module(ent, slot): # remove gear module from Modularity component
    entities.remove_module(ent, slot)


def has_sight(ent):
    if (Rogue.world.has_component(ent, cmp.SenseSight) and not on(ent,BLIND)):
        return True
    else:
        return False
def has_hearing(ent):
    if (Rogue.world.has_component(ent, cmp.SenseHearing) and not on(ent,DEAF)):
        return True
    else:
        return False

def nudge(ent,xd,yd):
    pos=Rogue.world.component_for_entity(ent, cmp.Position)
    x = pos.x + xd
    y = pos.y + yd
    if getmap().tilefree(x,y):
        port(ent, x, y)
        return True
    return False
def port(ent,x,y):
    ''' move thing to absolute location, update grid and FOV
        do not check for a free space before moving
    '''
    grid_remove(ent)
    if not Rogue.world.has_component(ent, cmp.Position):
        Rogue.world.add_component(ent, cmp.Position())
    pos = Rogue.world.component_for_entity(ent, cmp.Position)
    pos.x=x; pos.y=y;
    grid_insert(ent)
    update_fov(ent) # is this necessary? It was commented out, but AI seems to have no way to set the flag to update its FOV.
    if Rogue.world.has_component(ent, cmp.LightSource):
        compo = Rogue.world.component_for_entity(ent, cmp.LightSource)
        compo.light.reposition(x, y)

def setAP(ent, val):
    actor=Rogue.world.component_for_entity(ent, cmp.Actor)
    actor.ap = val
def spendAP(ent, amt):
    actor=Rogue.world.component_for_entity(ent, cmp.Actor)
    actor.ap = max(0, actor.ap - amt)
    
def pocket(ent, item):
    world=Rogue.world
    grid_remove(item)
    give(ent, item)
    spendAP(ent, 1)
    if world.has_component(item, cmp.Position):
        world.remove_component(item, cmp.Position)
    
def drop(ent,item,dx=0,dy=0):   #remove item from ent's inventory, place it on ground nearby ent.
    world=Rogue.world
    make(ent, DIRTY_STATS)
    take(ent,item)
    entpos=world.component_for_entity(ent, cmp.Position)
    world.add_component(item, cmp.Position(entpos.x + dx, entpos.y + dy))
    grid_insert(item)

def givehp(ent,val=9999):
    stats = Rogue.world.component_for_entity(ent, cmp.Stats)
    stats.hp = min(getms(ent, 'hpmax'), stats.hp + val)
    make(ent,DIRTY_STATS)
def caphp(ent): # does not make stats dirty! Doing so is a huge glitch!
    stats = Rogue.world.component_for_entity(ent, cmp.Stats)
    stats.hp = min(stats.hp, getms(ent,'hpmax'))



# identifying
##def map_generate(Map,level): levels.generate(Map,level) #OLD OBSELETE
def look_identify_at(x,y):
    if in_view(Rogue.pc,x,y): # TODO: finish implementation
        pass
    desc="__IDENTIFY UNIMPLEMENTED__" #IDENTIFIER.get(asci,"???")
    return "{}{}".format(char, desc)

def visibility(ent, sight, plight, camo, dist) -> int: # calculate visibility level
    '''
    Parameters:
        ent    : viewer
        sight  : vision stat of viewer
        plight : perceived light level
        camo   : camoflauge of the target to see
        dist   : distance from viewer to target

        TODO: test this function's output
            (function logic has been altered)
    '''
    _sx = 4 if on(ent, NVISION) else 1
    return int( math.log2(plight)*0.5 + ( 40+sight - (misc.dice_roll(20)+camo+dist) )//20)
# end def

    
#damage hp
def damage(ent, dmg: int):
##    assert isinstance(dmg, int)
    if dmg <= 0: return
    make(ent,DIRTY_STATS)
    stats = Rogue.world.component_for_entity(ent, cmp.Stats)
    stats.hp -= dmg
    if stats.hp <= 0:
        kill(ent)
        return
    mat = Rogue.world.component_for_entity(ent, cmp.Form).material
    dt = getMatDT(mat)
    if dmg >= dt:
        kill(ent)
        return
# end def

  
def kill(ent): #remove a thing from the world
    if on(ent, DEAD): return
    world = Rogue.world
    _type = world.component_for_entity(ent, cmp.Image).char
    if world.has_component(ent, cmp.DeathFunction): # call destroy function
        world.component_for_entity(ent, cmp.DeathFunction).func(ent)
    make(ent, DEAD)
    clear_status_all(ent)
    
    # remains #
    isCreature = world.has_component(ent, cmp.Creature)
    if isCreature:
        # create a corpse
        if misc.dice_roll(100) < entities.corpse_recurrence_percent[_type]:
            create_corpse(ent)
    # inanimate things
    else:
        # create bubbles
        # TODO
        pass
    # end if
    
    # cleanup #
    release_entity(ent) #remove dead thing
# end def



    #----------------------#
    #        Events        #
    #----------------------#

# MESSAGES: TODOOOOO

def event_sight(x,y,text):
    if not text: return
    Rogue.c_managers['events'].add_sight(x,y,text)
def event_sound(x,y,data):
    if (not data): return
    volume,text1,text2=data
    Rogue.c_managers['events'].add_sound(x,y,text1,text2,volume)
# TODO: differentiate between 'events' and 'sights' / 'sounds' which are for PC entity only (right???)
def listen_sights(ent):     return  Rogue.c_managers['events'].get_sights(ent)
def add_listener_sights(ent):       Rogue.c_managers['events'].add_listener_sights(ent)
def remove_listener_sights(ent):    Rogue.c_managers['events'].remove_listener_sights(ent)
def clear_listen_events_sights(ent):Rogue.c_managers['events'].clear_sights(ent)
def listen_sounds(ent):     return  Rogue.c_managers['events'].get_sounds(ent)
def add_listener_sounds(ent):       Rogue.c_managers['events'].add_listener_sounds(ent)
def remove_listener_sounds(ent):    Rogue.c_managers['events'].remove_listener_sounds(ent)
def clear_listen_events_sounds(ent):Rogue.c_managers['events'].clear_sounds(ent)
def clear_listeners():              Rogue.c_managers['events'].clear()
    
##def listen_sights(ent):     return  Rogue.c_managers['sights'].get_sights(ent)
##def add_listener_sights(ent):       Rogue.c_managers['sights'].add_listener_sights(ent)
##def remove_listener_sights(ent):    Rogue.c_managers['sights'].remove_listener_sights(ent)
##def clear_listen_events_sights(ent):Rogue.c_managers['sights'].clear_sights(ent)
##def listen_sounds(ent):     return  Rogue.c_managers['sounds'].get_sounds(ent)
##def add_listener_sounds(ent):       Rogue.c_managers['sounds'].add_listener_sounds(ent)
##def remove_listener_sounds(ent):    Rogue.c_managers['sounds'].remove_listener_sounds(ent)
##def clear_listen_events_sounds(ent):Rogue.c_managers['sounds'].clear_sounds(ent)

def pc_listen_sights(): # these listener things for PC might need some serious work...
    pc=Rogue.pc
    lis=listen_sights(pc)
    if lis:
        for ev in lis:
            Rogue.c_managers['sights'].add(ev)
        manager_sights_run()
def pc_listen_sounds():
    pc=Rogue.pc
    lis=listen_sounds(pc)
    if lis:
        for ev in lis:
            Rogue.c_managers['sounds'].add(ev)
        manager_sounds_run()



    #----------------#
    #       FOV      #
    #----------------#

# TODO: test FOV for NPCs to make sure it works properly!!!
def getfovmap(mapID): return Rogue.map.fov_map# Rogue.fov_maps[mapID] #
def update_fov(ent):
    Rogue.c_managers['fov'].update(ent)
def run_fov_manager(ent):
    Rogue.c_managers['fov'].run(ent)
    
def _fov_init():  # normal type FOV map init -- just create the FOV map
    fovMap=libtcod.map_new(ROOMW,ROOMH)
    libtcod.map_copy(Rogue.map.fov_map,fovMap)  # get properties from Map
    return fovMap
def fov_init(ent):  # init fov for an entity
    if not Rogue.world.has_component(ent, cmp.SenseSight):
        return False
    compo=Rogue.world.component_for_entity(ent, cmp.SenseSight)
    compo.fovID=0 #_fov_init()
    return True
###@debug.printr
def fov_compute(ent):
##    print("computing fov for ent {}".format(ent))
    pos = Rogue.world.component_for_entity(ent, cmp.Position)
    senseSight = Rogue.world.component_for_entity(ent, cmp.SenseSight)
    sight = senseSight.sense
    getfovmap(senseSight.fovID).compute_fov(
        pos.x,pos.y, radius=sight, light_walls=True,
        algorithm=libtcod.FOV_RESTRICTIVE)
def update_fovmap_property(fovmap, x,y, value):
    libtcod.map_set_properties( fovmap, x,y,value,True)

# vision functions
def can_see(ent,x,y,sight=None): # circular FOV function
    run_fov_manager(ent) # compute entity's FOV if necessary
    world = Rogue.world
    light=get_perceived_light_value(x,y)
    if not on(ent,NVISION):
        light -= 3
    if light < 1:
        return False
##    if light >= BLINDING_LIGHT:
##        return False
    pos = world.component_for_entity(ent, cmp.Position)
    senseSight = world.component_for_entity(ent, cmp.SenseSight)
    if sight is None: sight=senseSight.sense
    dist = int(maths.dist(pos.x,pos.y, x,y))
    if ( getfovmap(senseSight.fovID).fov[y][x] and dist <= sight ): # <- circle-ize
        globalreturn(dist,light)
        return True
    return False
#

#copies Map 's fov data to all creatures - only do this when needed
#   also flag all creatures for updating their fov maps
def update_all_fovmaps():
    for ent, compo in Rogue.world.get_component(cmp.SenseSight):
        update_fov(ent)
##        fovMap=compo.fov_map
##        libtcod.map_copy(Rogue.map.fov_map, fovMap)






    #----------------#
    #     Things     #
    #----------------#

def release_entity(ent):
    print("released ", Rogue.world.component_for_entity(ent, cmp.Name).name)
    # do a bunch of precautionary stuff / remove entity from registers ...
    remove_listener_sights(ent) 
    remove_listener_sounds(ent)
    grid_remove(ent)
    # esper
    delete_entity(ent)
def delete_entity(ent):
    Rogue.world.delete_entity(ent)
def create_stuff(ID, x,y): # create & register an item from stuff list
    tt = entities.create_stuff(ID, x,y)
    register_entity(tt)
    return tt
def create_rawmat(ID, x,y): # create & register an item from raw materials
    tt = entities.create_rawmat(ID, x,y)
    register_entity(tt)
    return tt
def create_entity():
    return Rogue.world.create_entity()
##def create_entity_flagset(): # create an entity with a flagset
##    ent = Rogue.world.create_entity()
##    Rogue.world.add_component(ent, cmp.Flags) #flagset
##    return ent




    #  creature/monsters  #

def create_monster(typ,x,y,color=None): #init from entities.py
    ''' create a monster from the bestiary and initialize it '''
    if monat(x,y):
        return None #tile is occupied by a creature already.
    if color:
        ent = entities.create_monster(typ,x,y,color)
    else:
        ent = entities.create_monster(typ,x,y)
    register_entity(ent)
    grid_insert(ent)
    givehp(ent)
    givemp(ent)
    fov_init(ent)
    update_fov(ent)
    return ent

def create_corpse(ent):
    corpse = entities.convertTo_corpse(ent)
##    register_entity(corpse)
    return corpse


### build equipment and place in the world
##def _initThing(ent):
##    register_entity(ent)
##    grid_insert(ent)
##    givehp(ent) #give random quality based on dlvl?

def create_bubbles(x,y):
    ent=entities.create_bubbles(x,y)
    grid_insert(ent)
    return ent

def create_torpedo(x,y,direction,damage,dmgType):
    # TODO: update to allow multi-direction firing

    disable_refresh_manager()
    
    if direction==1:
        img = 10
    else:
        img = 12
    pos = cmp.Position(x,y)
    torpedo = Rogue.world.create_entity(
        pos,
        cmp.Name("torpedo"),
        cmp.Image(img, COL['accent'], COL['black']),
        cmp.Flags()
        )
    grid_insert(torpedo)
    while True:
        # torpedo move animation
        if not tilefree(pos.x,pos.y): #explode
            mon = monat(pos.x,pos.y)
            if mon:
                hurt(mon, damage, dmgType)
            # explosion animation
            animation_explosion(pos.x,pos.y)
            # create bubbles at site of explosion
            if not wallat(pos.x,pos.y):
                create_bubbles(pos.x,pos.y)
            release_entity(torpedo)
            break
        port(torpedo, pos.x + direction, pos.y)
##        time.sleep(0.05)
        update_game()
        update_base()
        update_final()
        game_update()
    update_game()
    update_base()
    update_final()
    enable_refresh_manager()


def animation_explosion(x,y):
    ent = Rogue.world.create_entity(
        cmp.Name("explosion"),
        cmp.Position(x,y),
        cmp.Image(ANIM_BOOM[1][0], COL['accent'], COL['black']),
        cmp.Animation(ANIM_BOOM[0], ANIM_BOOM[1]),
        cmp.Flags()
        )
    grid_insert(ent)
    animation = Rogue.world.component_for_entity(ent, cmp.Animation)
    while animation.index < len(ANIM_BOOM[1]) - 1:
        entities.animate(ent)
        time.sleep(1/animation.speed)
        update_game()
        update_base()
        update_final()
        game_update()
           







    #----------------#
    #    lights      #
    #----------------#

def list_lights(): return list(Rogue.c_managers["lights"].lights.values())
def create_light(x,y, value, owner=None): # value is range of the light.
    lumosity = value**lights.Light.LOGBASE
    light=lights.Light(x,y, lumosity, owner)
    light.fovID=0
    light.shine()
    lightID = Rogue.c_managers['lights'].add(light)
    if owner: # entity that has this Light object as a component
        # TODO: convert Light object / merge w/ LightSource compo, make functions global instead of member funcs (same for EnvLights) (low priority)
        if Rogue.world.has_component(owner, cmp.LightSource):
            compo = Rogue.world.component_for_entity(owner, cmp.LightSource)
            release_light(compo.lightID)
        Rogue.world.add_component(owner, cmp.LightSource(lightID, light))
    return lightID
def create_envlight(value, owner=None): # environment light
    light=lights.EnvLight(value, owner)
    light.shine()
    lightID = Rogue.c_managers['lights'].add_env(light)
    if owner:
        if Rogue.world.has_component(owner, cmp.LightSource):
            compo = Rogue.world.component_for_entity(owner, cmp.LightSource)
            release_envlight(compo.lightID)
        Rogue.world.add_component(owner, cmp.LightSource(lightID, light))
    return lightID

def release_light(lightID):
    light = Rogue.c_managers['lights'].get(lightID)
    light.unshine()
    if light.owner:
        Rogue.world.remove_component(light.owner, cmp.LightSource)
    Rogue.c_managers['lights'].remove(lightID)
def release_envlight(lightID):
    light = Rogue.c_managers['lights'].get_env(lightID)
    light.unshine()
    if light.owner:
        Rogue.world.remove_component(light.owner, cmp.LightSource)
    Rogue.c_managers['lights'].remove_env(lightID)






    #----------------#
    #    status      #
    #----------------#

#Status for being on fire separate from the fire entity and light entity.

def get_status(ent, statuscompo): #getstatus #status_get
    if Rogue.world.has_component(ent, statuscompo):
        return Rogue.world.component_for_entity(ent, statuscompo)
    else:
        return None
def set_status(ent, statuscompo, t=-1, q=None, target=None):
    '''
        # ent       = Thing object to set the status for
        # statuscompo   = status class (not an object instance)
        # t         = duration (-1 is the default duration for that status)
        # q         = quality (for specific statuses)
        # target    = entity target (for targeted statuses)
    '''
    proc.Status.add(ent, statuscompo, t, q, target)
def clear_status(ent, statuscompo):
    proc.Status.remove(ent, statuscompo)
def clear_status_all(ent):
    proc.Status.remove_all(ent)
def overwrite_status(ent, statuscompo, t=-1, q=1):
    ''' set or clear status depending on q / t
        overwrite existing status
    '''
    if (q and t!=0):
        status=get_status(ent, statuscompo)
        if status:
            clear_status(ent, statuscompo)
        set_status(ent, statuscompo, t=t, q=q)
    else:
        clear_status(ent, statuscompo)
def compound_status(ent, statuscompo, t=-1, q=1):
    ''' increment quality of a given status '''
    if (q and t!=0):
        status=get_status(ent, statuscompo)
        if status:
            nq = q + status.quality
            clear_status(ent, statuscompo)
        else:
            nq = q
        set_status(ent, statuscompo, t=t, q=nq)
# end def
  
    # elemental damage #
    
# RECursively apply ELEMent to all items touching/held/carried by the entity
def recelem(ent, func, dmg, *args, **kwargs):
    # apply to inventory items
    inv=Rogue.world.component_for_entity(ent, cmp.Inventory).data
##    invres=... # inventory resistance. Should backpack be a separate entity w/ its own inventory? Inventories combine into one?
    for item in inv:
        func(item, dmg, *args, **kwargs)
    # apply to the entity itself
    return func(ent, dmg, *args, **kwargs)
# INTENDED SYNTAX: (TODO: test to make sure this works before applying to all elements.)
def NEWburn(ent, dmg, maxTemp=999999):
    return recelem(ent, entities.burn, dmg, maxTemp)

def bleed(ent, dmg):
    return entities.bleed(ent, dmg)
def scare(ent, dmg):
    return entities.scare(ent, dmg)
def electrify(ent, dmg):
    return entities.electrify(ent, dmg)
    

    #-----------#
    #  actions  #
    #-----------#

def queue_action(ent, act):
    pass
    #Rogue.c_managers['actionQueue'].add(obj, act)




    #-----------#
    # Character #
    #-----------#

# gender name and pronouns
def get_gender_id(ent): # gender ID
    return Rogue.world.component_for_entity(ent, cmp.Gender).gender
def get_gender(ent): # gender name
    gender=Rogue.world.component_for_entity(ent, cmp.Gender).gender
    return _get_gender_name(gender)
def get_pronouns(ent): # gender pronouns
    gender=Rogue.world.component_for_entity(ent, cmp.Gender).gender
    return _get_pronouns(gender)
def get_pronoun_subject(ent): # "he, she", etc.
    return _get_pronoun_subject(get_pronouns(ent))
def get_pronoun_object(ent): # "him, her", etc.
    return _get_pronoun_object(get_pronouns(ent))
def get_pronoun_possessive(ent): # "his, her", etc.
    return _get_pronoun_possessive(get_pronouns(ent))
def get_pronoun_possessive2(ent): # "his, "hers", etc.
    return _get_pronoun_possessive2(get_pronouns(ent))
def get_pronoun_generic(ent): # "man, woman", etc.
    return _get_pronoun_generic(get_pronouns(ent))
def get_pronoun_polite(ent): # "sir, madam", etc.
    return _get_pronoun_polite(get_pronouns(ent))
def get_pronoun_informal(ent): # "guy, girl", etc.
    return _get_pronoun_informal(get_pronouns(ent))
def _get_pronoun_subject(pronouns): return pronouns[0]
def _get_pronoun_object(pronouns): return pronouns[1]
def _get_pronoun_possessive(pronouns): return pronouns[2]
def _get_pronoun_possessive2(pronouns): return pronouns[3]
def _get_pronoun_generic(pronouns): return pronouns[4]
def _get_pronoun_polite(pronouns): return pronouns[5]
def _get_pronoun_informal(pronouns): return pronouns[6]
def _get_gender_name(gender): return GENDERS[gender][0]
def _get_pronouns(gender): return GENDERS[gender][1]





    #----------#
    # managers #
    #----------#

def manager_listeners_alert(result):
    for listener in manager_listeners():
        listener.alert(result)
def manager_listeners(): return Rogue.manager_listeners
def manager_listeners_add(obj): Rogue.manager_listeners.append(obj)
def manager_listeners_remove(obj): Rogue.manager_listeners.remove(obj)

# 

def Input(x,y, w=1,h=1, default='',mode='text',insert=False):
    return IO.Input(x,y,w=w,h=h,default=default,mode=mode,insert=insert)

# constant managers #

def manager_sights_run():   Rogue.c_managers['sights'].run()
def manager_sounds_run():   Rogue.c_managers['sounds'].run()

# per-turn managers #

def register_timer(obj):    Rogue.bt_managers['timers'].add(obj)
def release_timer(obj):     Rogue.bt_managers['timers'].remove(obj)

# game state managers #

def get_active_manager():       return Rogue.manager
def close_active_manager():
    if Rogue.manager:
        manager_listeners_alert(Rogue.manager.result)
        Rogue.manager.close()
        Rogue.manager=None
def clear_active_manager():
    if Rogue.manager:
        Rogue.manager.set_result('exit')
        close_active_manager()

def routine_look(xs, ys):
    clear_active_manager()
    game_set_state("manager") #look
    Rogue.manager=managers.Manager_Look(
        xs, ys, Rogue.view, Rogue.map.get_map_state())
    alert("Look where? (<hjklyubn>, mouse; <select> to confirm)")
    Rogue.view.fixed_mode_disable()

def routine_move_view():
    clear_active_manager()
    game_set_state("manager") #move view
    Rogue.manager=managers.Manager_MoveView(
        Rogue.view, Rogue.map.get_map_state(),
        "Direction? (<hjklyubn>; <select> to center; <Esc> to save position)")
    Rogue.view.fixed_mode_disable()
    
def aim_find_target(xs, ys, selectfunc, *args, **kwargs):
    # selectfunc: the function that is ran when you select a valid target
    clear_active_manager()
    game_set_state("manager") #move view
    Rogue.manager=managers.Manager_AimFindTarget(
        xs, ys, Rogue.view, Rogue.map.get_map_state())
    Rogue.view.fixed_mode_disable()
    # listener -- handles the shooting
    listener = Aim_Manager_Listener(
        world(), Rogue.pc, selectfunc, *args, **kwargs)
    manager_listeners_add(listener)
    
def ability_dash(xs, ys, selectfunc, maxMove, *args, **kwargs):
    # selectfunc: the function that is ran when you select a valid target
    clear_active_manager()
    game_set_state("manager") #move view
    

    valid_tiles = [] # populate valid tiles list (todo)
    for i in range(-maxMove, maxMove + 1):
        if i==0:
            continue
        if tilefree(xs +i, ys):
            valid_tiles.append((xs + i, ys,))

    Rogue.manager=managers.Manager_SelectTile(
        xs, ys, Rogue.view, Rogue.map.get_map_state())
    Rogue.view.fixed_mode_disable()
    # listener -- handles the shooting
    listener = SelectTile_Manager_Listener(
        world(), Rogue.pc, selectfunc, valid_tiles=valid_tiles)
    manager_listeners_add(listener)

# Manager_PrintScroll
def help():
    clear_active_manager()
    game_set_state("manager") # help
    width   = window_w()
    height  = window_h()
    strng   = IO.render_help()
    nlines  = 1 + strng.count('\n')
    hud1h   = 3
    hud2h   = 3
    scroll  = makeConBox(width,1000,strng)
    top     = makeConBox(width,hud1h,"help")
    bottom  = makeConBox(width,hud2h,"<Up>, <Down>, <PgUp>, <PgDn>, <Home>, <End>; <select> to return")
    Rogue.manager = managers.Manager_PrintScroll(
        scroll,width,height, top,bottom, h1=hud1h,h2=hud2h,maxy=nlines)
# end def
def routine_print_msgHistory():
    clear_active_manager()
    game_set_state("manager") #message history
    width   = window_w()
    height  = window_h()
    strng   = Rogue.log.printall_get_wrapped_msgs()
    nlines  = 1 + strng.count('\n')
    hud1h   = 3
    hud2h   = 3
    scroll  = makeConBox(width,1000,strng)
    top     = makeConBox(width,hud1h,"message history")
    bottom  = makeConBox(width,hud2h,"<Up>, <Down>, <PgUp>, <PgDn>, <Home>, <End>; <select> to return")
    Rogue.manager = managers.Manager_PrintScroll(
        scroll,width,height, top,bottom, h1=hud1h,h2=hud2h,maxy=nlines)
# end def
def routine_print_charPage():
    clear_active_manager()
    game_set_state("manager") #character page
    width   = window_w()
    height  = window_h()
    strng   = misc.render_charpage_string(
        width, height, Rogue.pc, get_turn(), dlvl()
        )
    nlines  = 1 + strng.count('\n')
    hud1h   = 3
    hud2h   = 3
    scroll  = makeConBox(width,200,strng)
    top     = makeConBox(width,hud1h,"character data sheet")
    bottom  = makeConBox(width,hud2h,"<Up>, <Down>, <PgUp>, <PgDn>, <Home>, <End>; <select> to return")
    Rogue.manager = managers.Manager_PrintScroll(
        scroll,width,height, top,bottom, h1=hud1h,h2=hud2h,maxy=nlines)
# end def

#
# get direction
# player chooses a direction using key bindings or the mouse,
# returns a tuple or None
#
def get_direction(msg=""):
    alert(msg)
    while True:
        pcAct=IO.handle_mousekeys(IO.get_raw_input()).items()
        for act,arg in pcAct:
            if (act=="context-dir" or act=="move"):
                return arg
            if act=="exit":
                alert("")
                return None
            if act=="select":
                return (0,0,0,)
            if act=="lclick":
                mousex,mousey,z=arg
                pc=Rogue.pc
                dx=mousex - getx(pc.x)
                dy=mousey - gety(pc.y)
                if (dx >= -1 and dx <= 1 and dy >= -1 and dy <= 1):
                    return (dx,dy,0,)
# end def
    
#prompt
# show a message and ask the player for input
# Arguments:
#   x,y:        top-left position of the prompt box
#   w,h:        width, height of the prompt dbox
#   maxw:       maximum length of the response the player can give
#   q:          question to display in the prompt dbox
#   default:    text that is the default response
#   mode:       'text' or 'wait'
#   insert:     whether to begin in Insert mode for the response
#   border:     border style of the dbox
def prompt(x,y, w,h, maxw=1, q='', default='',mode='text',insert=False,border=0,wrap=True):
    #libtcod.console_clear(con_final())
    dbox(x,y,w,h,text=q,
        wrap=wrap,border=border,con=con_final(),disp='mono')
    result=""
    while (result==""):
        refresh()
        if mode=="wait":
            xf=x+w-1
            yf=y+h-1
        elif mode=="text":
            xf=x
            yf=y+h
        result = Input(xf,yf,maxw,1,default=default,mode=mode,insert=insert)
    return result

#menu
#this menu freezes time until input given.
# Arguments:
#   autoItemize: create keys for your keysItems iterable automagically
#   keysItems can be an iterable or a dict.
#       **If a dict, autoItemize MUST be set to False
#       dict allows you to customize what buttons correspond to which options
def menu(name, x,y, keysItems, autoItemize=True):
    manager=managers.Manager_Menu(name, x,y, window_w(),window_h(), keysItems=keysItems, autoItemize=autoItemize)
    result=None
    while result is None:
        manager.run()
        result=manager.result
    manager.close()
    if result == ' ': return None
    return manager.result
    
def adjacent_directions(_dir):
    return ADJACENT_DIRECTIONS.get(_dir, ((0,0,0,),(0,0,0,),) )
    





