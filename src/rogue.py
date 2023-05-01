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
def run_refresh_managers(): # run every time ANY input is received
    Rogue.c_managers['refresh'].run()

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

def pocket(ent, item):
    world=Rogue.world
    grid_remove(item)
    give(ent, item)
    spendAP(ent, NRG_POCKET)
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
    return int( math.log2(plight)*0.5 + ( 40+sight - (dice.roll(20)+camo+dist) )//20)
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
    _type = world.component_for_entity(ent, cmp.Draw).char
    if world.has_component(ent, cmp.DeathFunction): # call destroy function
        world.component_for_entity(ent, cmp.DeathFunction).func(ent)
    make(ent, DEAD)
    clear_status_all(ent)
    
    # handle any dependencies shared by this entity before removing it #
    
    # unequip entity if it's currently being worn / held as an equip
    if world.has_component(ent, cmp.Equipped):
        compo = world.component_for_entity(ent, cmp.Equipped)
        deequip(compo.owner, compo.equipType)
        
    # drop entity's equipped items if applicable
    if world.has_component(ent, cmp.Body):
        deequip_all(ent)
    
    # remove entity from inventory if it's being carried
    if world.has_component(ent, cmp.Carried):
        compo = world.component_for_entity(ent, cmp.Carried)
        drop(compo.owner, ent)
        
    # drop entity's inventory if it's carrying anything
    if world.has_component(ent, cmp.Inventory):
        for tt in world.component_for_entity(ent, cmp.Inventory).data:
            drop(ent, tt)
    
    # remains #
    
    # creatures
    isCreature = world.has_component(ent, cmp.Creature)
    if isCreature:
        # create a corpse
        if dice.roll(100) < entities.corpse_recurrence_percent[_type]:
            create_corpse(ent)
    # inanimate things
    else:
        # burn to ashes
        if get_status(ent, cmp.StatusBurn):
            mat = world.component_for_entity(ent, cmp.Form).material
            if (mat==MAT_FLESH
                or mat==MAT_WOOD
                or mat==MAT_FUNGUS
                or mat==MAT_VEGGIE
                or mat==MAT_LEATHER
                ):
                create_ashes(ent)
    # end if
    
    # cleanup #
    release_entity(ent) #remove dead thing
# end def


    #----------------------#
    #        Events        #
    #----------------------#

#... (messages, sending messages to player based on what happens in game)



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

def register_entity(ent): # NOTE!! this no longer adds to grid.
    # initialize stats components
    create_moddedStats(ent) # is there a place this would belong better?
    make(ent,DIRTY_STATS)
def release_entity(ent):
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


    #-----------------#
    #    Equipment    #
    #-----------------#

def list_equipment(ent):
    lis = []
    body = Rogue.world.component_for_entity(ent, cmp.Body)
    # core
    if body.plan==BODYPLAN_HUMANOID:
        lis.append(body.slot.item)
        lis.append(body.core.front.slot.item)
        lis.append(body.core.back.slot.item)
        lis.append(body.core.hips.slot.item)
        lis.append(body.core.core.slot.item)
    else:
        raise Exception # TODO: differentiate with different body types
    # parts
    for cls, part in body.parts.items():
        if type(part)==cmp.BPC_Arms:
            for arm in part.arms:
                lis.append(arm.hand.held.item)
                lis.append(arm.hand.slot.item)
                lis.append(arm.arm.slot.item)
        elif type(part)==cmp.BPC_Legs:
            for leg in part.legs:
                lis.append(leg.foot.slot.item)
                lis.append(leg.leg.slot.item)
        elif type(part)==cmp.BPC_Heads:
            for head in part.heads:
                lis.append(head.mouth.held.item)
                lis.append(head.head.slot.item)
                lis.append(head.face.slot.item)
                lis.append(head.neck.slot.item)
                lis.append(head.eyes.slot.item)
                lis.append(head.ears.slot.item)
    while None in lis:
        lis.remove(None)
    return lis

def equip(ent,item,equipType): # equip an item in 'equipType' slot
    '''
        equip ent with item in the slot designated by equipType const
        (functions for held or worn items)
        return tuple: (result, compo,)
            where result is a negative value for failure, or 1 for success
            and compo is None or the item's equipable component if success
        
##                #TODO: add special effects; light, etc. How to??
            light: make the light a Child of the equipper
    '''
##    print("trying to equip {} to {}".format(fullname(item), fullname(ent)))
# init and failure checking #
    # first check that the entity can equip the item in the indicated slot.
    world = Rogue.world
    equipableConst = EQUIPABLE_CONSTS[equipType]
    eqcompo = _get_eq_compo(ent, equipType)
    holdtype=(equipType in cmp.EQ_BPS_HOLD) # holding type or armor type?

    if equipType==EQ_NONE:
        return (-100,None,) # NULL value for equip type
    if not world.has_component(item, equipableConst):
        return (-1,None,) # item can't be equipped in this slot
    if not eqcompo: # component selected. Does this component exist?
        return (-2,None,) # something weird happened
    if eqcompo.slot.covered:
        return (-3,None,) # already have something covering that slot
    if ( equipType==EQ_OFFHANDW and on(item, TWOHANDS)):
        return (-5,None,) # reject 2-h weapons not equipped in mainhand.
    equipable = world.component_for_entity(item, equipableConst)
    
    # ensure body type indicates presence of this body part
    # (TODO)
##    if EQTYPES_TO_BODYPARTS[equipType] in BODYPLAN_BPS[body.plan]:
##        ...

    # coverage #
    
    # figure out what additional slots the equipment covers, if any
    def __cov(ent, clis, flis, eqtype, cls): # cover additional body part
        for _com in findbps(ent, cls): # temporary
            if _com.slot.covered: # make sure you can't equip something if ...
                flis.append(_com) # ... any required slots are occupied.
            else:
                clis.append(_com)
    # end def
    clis = [] # success list - covered
    flis = [] # failure list
    
    # two hands
    # TODO : change logic so that you CAN wield 2-h weapon in 1-h
    # it's just that you get a big penalty for doing so.
##    if ( equipType==EQ_MAINHAND and on(item, TWOHANDS) ):
##        __cov(ent,clis,hlis,flis,equipType,cmp.BP_Hand) # Fixme: this covers ALL hands. 
    if equipType==EQ_FRONT:
        if equipable.coversBack: __cov(ent,clis,flis,equipType,cmp.BP_TorsoBack)
        if equipable.coversCore: __cov(ent,clis,flis,equipType,cmp.BP_TorsoCore)
        if equipable.coversHips: __cov(ent,clis,flis,equipType,cmp.BP_Hips)
    if equipType==EQ_MAINHEAD:
        if equipable.coversFace: __cov(ent,clis,flis,equipType,cmp.BP_Face)
        if equipable.coversNeck: __cov(ent,clis,flis,equipType,cmp.BP_Neck)
        if equipable.coversEyes: __cov(ent,clis,flis,equipType,cmp.BP_Eyes)
        if equipable.coversEars: __cov(ent,clis,flis,equipType,cmp.BP_Ears)
    if flis:
        return (-10, flis,) # failed to equip because the BPs in flis are already covered.
# /init #
    
        #-------------------------#
        # success! Equip the item #
        #-------------------------#
        
##    print("successfully equipped {} to {}".format(fullname(item), fullname(ent)))

    # remove item from the map and from agent's inventory if applicable
    grid_remove(item)
    if item in getinv(ent):
        take(ent, item)
##        print("taken {} from {}".format(fullname(item), fullname(ent)))
    # indicate that the item is equipped using components
    world.add_component(item, cmp.Child(ent))
    if holdtype:
        world.add_component(item, cmp.Held(ent, equipType))
    else:
        world.add_component(item, cmp.Equipped(ent, equipType))
    if world.has_component(item, cmp.Fitted):
        fitted=world.component_for_entity(item, cmp.Fitted)
        if fitted.entity==ent:
            armorfit = FIT_ARMOR_MAX
            heldfit = FIT_HELD_MAX
        else:
            armorfit = 0
            diff = abs(fitted.height - getbase(ent,'height'))//2
            heldfit = 0.5*FIT_HELD_MAX - diff*(FIT_HELD_MAX/FIT_ARMOR_MAX)
    else:
        armorfit = 0
        heldfit = 0
    
    # put it in the right slot (held or worn?)
    if holdtype: # held
        eqcompo.held.item = item
        eqcompo.held.fit = heldfit
# todo: function that adds these values to get how well you're gripping something.
    else: # worn
        eqcompo.slot.item = item
        eqcompo.slot.fit = armorfit
    
    eqcompo.slot.covered = True # cover this BP
    
    if ( (equipType==EQ_MAINLEG or equipType==EQ_OFFLEG)
         and equipable.coversBoth
        ):
        # for now just cover all legs (TEMPORARY OBV.)
        for leg in findbps(ent, cmp.BP_Leg):
            clis.append(leg)
    
    # cover
    eqcompo.slot.covers = tuple(clis)
    # cover the BPs
    for _com in clis:
        _com.slot.covered=True
    #
    
    make(ent, DIRTY_STATS)
    return (1,equipable,) # yey success
    
# end def

def remove_equipment(ent, item):
    ''' dewield or deequip (context sensitive) '''
    world = Rogue.world
    if world.has_component(item, cmp.Equipped):
        equipType=world.component_for_entity(item,cmp.Equipped).equipType
        deequip(ent, equipType)
    elif world.has_component(item, cmp.Held):
        equipType=world.component_for_entity(item,cmp.Held).equipType
        dewield(ent, equipType)
        
def deequip_all(ent): # TODO: test this (and thus all deequip funcs)
    body = Rogue.world.component_for_entity(ent, cmp.Body)
    
    # core
    if body.plan==BODYPLAN_HUMANOID:
        _deequipSlot(ent, body.slot)
        deequip(ent, EQ_FRONT)
        deequip(ent, EQ_BACK)
        deequip(ent, EQ_HIPS)
        deequip(ent, EQ_CORE)
    else:
        raise Exception # TODO: differentiate with different body types
    # parts
    for cls, part in body.parts.items():
        if type(part)==cmp.BPC_Arms:
            for arm in part.arms:
                _dewield(ent, arm.hand)
                _deequip(ent, arm.hand)
                _deequip(ent, arm.arm)
        elif type(part)==cmp.BPC_Legs:
            for leg in part.legs:
                _deequip(ent, leg.foot)
                _deequip(ent, leg.leg)
        elif type(part)==cmp.BPC_Heads:
            for head in part.heads:
                _dewield(ent, head.mouth)
                _deequip(ent, head.head)
                _deequip(ent, head.face)
                _deequip(ent, head.neck)
                _deequip(ent, head.eyes)
                _deequip(ent, head.ears)
    # end for
# end def
def deequip(ent,equipType):
    ''' remove worn equipment from slot 'equipType' (not held)
        return the item that was equipped there
            or None if failed to un-equip
    '''
    compo = _get_eq_compo(ent, equipType)
    if not compo:
        return None
    return _deequip(ent, compo)
# end def
def _deequip(ent, compo):
    ''' unequip the worn item in the component's wear slot (not held)
        consider coverage of other slots that may be affected
    '''
    # uncover the covered slot(s)
    for cc in compo.slot.covers:
        cc.slot.covered = False
    compo.slot.covers = ()
    
    return _deequipSlot(ent, compo.slot)
# end def
def _deequipSlot(ent, slot):
    ''' unequip the worn item from equip slot slot (not held)
        unconcerned with coverage of other slots
    '''
    world=Rogue.world
    item = slot.item
    if not item: #nothing equipped here
        return None
    
    world.remove_component(item, cmp.Child)
    world.remove_component(item, cmp.Equipped)
    slot.item = None
    slot.covered = False
    slot.fit = 0
    give(ent, item) # put item in inventory
    
    make(ent, DIRTY_STATS)
    return item
# end def

def dewield(ent,equipType): # for held items only (not worn)
    compo = _get_eq_compo(ent, equipType)
    if not compo:
        return None
    return _dewield(ent, compo)
# end def
def _dewield(ent, compo):
    world=Rogue.world
    item = compo.held.item
    if not item: #nothing equipped here
        return None
    
    world.remove_component(item, cmp.Child)
    world.remove_component(item, cmp.Held)
    compo.held.covered = False
    compo.held.item = None
    compo.held.fit = 0
    give(ent, item) # put item in inventory
    
    make(ent, DIRTY_STATS)
    return item
# end def

# build equipment and place in the world
def _initThing(ent):
    register_entity(ent)
    grid_insert(ent)
    givehp(ent) #give random quality based on dlvl?
def create_weapon(name,x,y,cond=1,mat=None):
    ent=entities.create_weapon(name,x,y,condition=cond,mat=mat)
    _initThing(ent)
    return ent

           


def _update_stats(ent): # PRIVATE, ONLY TO BE CALLED FROM getms(...)
    ''' calculate modified stats (ModdedStats component)
            building up from scratch (base stats from Stats component)
            add any modifiers from equipment, status effects, etc.
        return the ModdedStats component
        after this is called, you can access the ModdedStats component
            and it will contain the right value, until something significant
            updates which would change the calculation, at which point the
            DIRTY_STATS flag for that entity must be set to True.
        NOTE: this and ModdedStats component are private.
            Use the public interface "getms" to access modified stats.
    '''
    # NOTE: apply all penalties (w/ limits, if applicable) AFTER bonuses.
        # this is to ensure you don't end up with MORE during a
        #   penalty application; as in the case the value was negative
    
# init #----------------------------------------------------------------#
    
    world=Rogue.world
    base=world.component_for_entity(ent, cmp.Stats)
    modded=world.component_for_entity(ent, cmp.ModdedStats)

    # RESET all modded stats to their base
    for k,v in base.__dict__.items():
        modded.__dict__[k] = v


    
    
#~~~#---------------------------------------------------------------#~~~#
    #       FINAL        MULTIPLIERS       BEGIN       HERE         #
#~~~#---------------------------------------------------------------#~~~#
    
    #------------------------------------------------#
    #   Statuses that affect (non-attribute) stats   #
    #------------------------------------------------#
    
    
#~~~~~~~#--------------#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #   finalize   #
        #--------------#
    
    # final multipliers
    # apply mods -- mult mods
    
    # round values

    # cap values at their limits

##    print(" ** ~~~~ ran _update_stats.")

    # NOTE: resulting values can be negative, but this can be
    #   checked for, depending on the individual uses for each stat
    #   e.g. MSp cannot be below 1-5 or so for purposes of movement,
    #   Spd cannot be below 1, Dmg cannot be below 0,
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    assert(not on(ent, DIRTY_STATS)) # MUST NOT BE DIRTY OR ELSE A MAJOR PROBLEM EXISTS IN THE CODE. Before this is called, dirty_stats flag is removed. If it got reset during this function then we get infinite recursion of this expensive function.
    return modded
# end def


# create and initialize the ModdedStats component
def create_moddedStats(ent):
    world=Rogue.world
    modded=cmp.ModdedStats()
    base=world.component_for_entity(ent, cmp.Stats)
    for k in base.__dict__.keys():
        modded.__dict__.update({ k : 0 })
    world.add_component(ent, modded)
    make(ent, DIRTY_STATS)
    return modded







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

# manager listeners
class Manager_Listener: # listens for a result from a game state Manager.
    def alert(self, result): # after we get a result, purpose is finished.
        manager_listeners_remove(self) # delete the reference to self.
class Aim_Manager_Listener(Manager_Listener):
    def __init__(self, world, caller, shootfunc, *args, **kwargs):
        self.world=world
        self.caller=caller      # entity who is calling the shootfunc
        self.shootfunc=shootfunc # function that runs when you select viable target
        self.arglist=args     # arguments for the shootfunc function
        self.kwarglist=kwargs # keyword arguments "
    def alert(self, result):
        if type(result) is int: # we have an entity target
##            print(self.arglist)
##            print(self.kwarglist)
            self.shootfunc(
                self.caller, result,
                *self.arglist, **self.kwarglist
                )
        super(Aim_Manager_Listener, self).alert(result)

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
def get_direction():
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
    





