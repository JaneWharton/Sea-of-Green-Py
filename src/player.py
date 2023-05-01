'''
    player.py
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
    along with this program.  If not, see <https://Chargen.www.gnu.org/licenses/>

    TODO : finish up chargen function
    
'''

import os
import random
import tcod as libtcod

from const      import *
from colors     import COLORS as COL
import rogue    as rog
import components as cmp
import action
import debug
##import dice
import entities
import misc




#
#   init player object. Pass an entity into the function...
#

def init(pc):
    
    # register for sense events for the message log
##    rog.add_listener_sights(pc) # TODO: implement this... There is a distinction btn. Events object for regular listening events of sights/sounds, and also two more classes for sights seen and sounds heard by the player. These should probably work differently...
##    rog.add_listener_sounds(pc)
    rog.fov_init(pc)
    rog.view_center(pc)
    rog.givehp(pc)
    rog.givemp(pc)
#


#
#   constant commands
#   can be performed from anywhere in the main game loop
#

def commands_const(pc, pcAct):
    for act,arg in pcAct:        
        if act == "console":    debug.cmd_prompt(globals(), locals())
        elif act == "last cmd": debug.execute_last_cmd(globals(), locals()) 
        elif act == "quit game":rog.end()

def commands_pages(pc, pcAct):
    if rog.Rogue.menu_key_listener_is_paused():
        return
    for act,arg in pcAct:
        if act == "message history" :
            rog.routine_print_msgHistory()
            return
        if act == "character page" :
            rog.routine_print_charPage()
            return
        if act == "inventory" :
            print("inventory accessed!! Status: ", rog.Rogue.menu_key_listener_is_paused())
            action.inventory_pc(pc)
            return
        if act == "equipment" :
            action.equipment_pc(pc)
            return
        if act == "abilities" :
            action.abilities_pc(pc)
            return

#
#   commands
#

def _Update():
##    print("updated")
    rog.update_game()
    rog.update_fov(rog.pc())
##    rog.update_final()
    rog.update_hud()
def commands(pc, pcAct):
    world = rog.world()

    directional_command = 'move'
    
    for act,arg in pcAct:

##        print(act)
##        print(arg)
        
        rog.update_base()
        
        #----------------#
        # convert action #
        #----------------#
        
        if act =='context-dir':
            act=directional_command
##        if act =='context':
##            pass
        # moving using the menu move keys
        if (act =='menu-nav' and rog.game_state()=="normal"):
            act=directional_command
        
        
        #----------------#
        # perform action #
        #----------------#
#-----------MOUSE ACTION----------------------------#
        
        if act == 'lclick':
            mousex,mousey,z=arg
            if rog.wallat(mousex,mousey):
                return
            pos = world.component_for_entity(pc, cmp.Position)
            print("Left click unimplemented")
##            rog.path_compute(pc.path, pos.x,pos.y, rog.mapx(mousex), rog.mapy(mousey))
            #rog.occupation_set(pc,'path')

        elif act == 'rclick':
            pass
        
#------------OTHER ACTION--------------------------#
        
        elif act == 'help':
            rog.help()

        # "move-prompt" : True
        # prompt for a direction
        #   and then perform the move action in that direction
        elif act == 'move-prompt':
            pass

        # "attack-prompt" : True
        # prompt for a direction
        #   and then perform the attack action in that direction
        elif act == 'attack-prompt':
            pass
        
        # "move" : (x_change, y_change, z_change,)
        elif act == 'move':
            _Update()
            dx,dy,dz=arg
            pos = world.component_for_entity(pc, cmp.Position)
            actor = world.component_for_entity(pc, cmp.Actor)

            # wait
            if (dx==0 and dy==0):
                actor.ap = 0
                return

            can_move = False
            modular = world.component_for_entity(pc, cmp.Modularity)
            modules = []
            energy_cost = 0
            volume = 0
            permitted_directions = []
            for i in range(1, 4):
                modules.append(modular.modules.get(i, None))
            for module in modules:
                if module == None:
                    continue
                permitted_directions = module.MOVE_DIRECTIONS
                if ((dx,dy) in permitted_directions):
                    energy_cost = module.get_energy()
                    volume = module.get_volume()
                    can_move = True
                    break

            if not can_move:
                return
            
            xto=pos.x + dx
            yto=pos.y + dy

            # out of bounds
            if ( not rog.is_in_grid_x(xto) or not rog.is_in_grid_y(yto) ):
                return
            
            if not rog.solidat(xto,yto):
                # space is free, so we can move
                action.move(pc, dx,dy)

                     #TODO
                # expend energy
                print("energy: ", energy_cost)
                # make sound
                print("volume: ", volume)

                
            else:
                rog.alert("That space is occupied.")
        # end conditional
        
        # "attack" : (x, y, z,)
        elif act == 'use1':
            pass
        # end conditional

        # chat with closest speaking entity;
        #   if multiple good options, prompt for which one.
        elif act == "chat-context":
            action.chat_context(pc)
            _Update()
            return
        elif act == "target-prompt": #target entity + fire / throw / attack
            action.target_pc_generic(pc)
            _Update()
            return
        elif act == "get-prompt":
            action.pickup_pc(pc)
            _Update()
            return
        #
        #
        # special actions #
        #
        
        elif act == 'find player': #useful to immediately show where the player is
            pos = world.component_for_entity(pc, cmp.Position)
            rog.view_center_player()
            rog.update_game()
            rog.update_final()
            rog.game_update() #call all the updates
            rog.alert('press any key to continue...')
            rog.Input(rog.getx(pos.x), rog.gety(pos.y), mode='wait')
            rog.update_base()
            rog.alert('')
            return
        elif act == "look":
            pos = world.component_for_entity(pc, cmp.Position)
            rog.routine_look(pos.x,pos.y)
            return
        elif act == "move view":
            rog.routine_move_view()
            return
        elif act == "fixed view":
            rog.fixedViewMode_toggle()
            return  
        elif act == 'select':
            # TESTING
            print(rog.Input(0,0,20))
            return
        elif act == 'exit':
            return

    # end for
# end def



def _selectFromBigMenu():
    ''' run the big menu, return whether any char data has changed
    '''
    libtcod.console_clear(0)
    libtcod.console_clear(rog.con_final())
    _printChargenData()
    rog.refresh()
    _drawskills(0)
    _drawtraits(0)
    _choice = rog.menu( "character specs", Chargen.xx,10, Chargen.menu.keys() )
    if _choice == -1: # Esc
        Chargen.confirm = True
        return False
    selected=Chargen.menu.get(_choice, None)
    if not selected:
        print("Failure in _selectFromBigMenu()... information:")
        print("    selected: ", selected)
        print("    _choice: ", _choice)
        return False
    
    # selection successful.
    # figure out what type of option was selected
    if selected=="confirm":
        Chargen.confirm = True
    elif selected=="open-skills":
        Chargen.open_skills = True
    elif selected=="close-skills":
        Chargen.open_skills = False
    elif selected=="open-stats":
        Chargen.open_stats = True
    elif selected=="close-stats":
        Chargen.open_stats = False
    elif selected=="open-attributes":
        Chargen.open_attributes = True
    elif selected=="close-attributes":
        Chargen.open_attributes = False
    elif selected=="open-traits":
        Chargen.open_traits = True
    elif selected=="close-traits":
        Chargen.open_traits = False
    elif selected in Chargen.skilldict.values():
        return _select_skill(selected)
    elif selected in Chargen.statdict.values():
        return _select_stat(selected)
    elif selected in Chargen.attdict.values():
        return _select_attribute(selected)
    elif selected in Chargen.traitdict.values():
        return _select_trait(selected)
    
    return False
# end def




#
# Chargen
#
''' global data for use by character generation function '''
class Chargen:
    pass
def __init__Chargen():
    Chargen.pc = None # player character entity
    Chargen._name=""
    # menu position / window size
    Chargen.x1 = 0; Chargen.y1 = 22;
    Chargen.xx = 0; Chargen.yy = 3;
    Chargen.iy = 0;
    Chargen.ww = rog.window_w(); Chargen.hh = 5;
# end class


def chargen(sx, sy):
    ''' character generation function
    # Create and return the player Thing object,
    #   and get/set the starting conditions for the player
    # Arguments:
    #   sx, sy: starting position x, y of player entity
    '''
    # TODO: saving/loading game
    
    # init
    world = rog.world()
    __init__Chargen()   # init some global vars for use during chargen
    libtcod.console_clear(0)
    libtcod.console_clear(rog.con_game())
    libtcod.console_clear(rog.con_final())
    #
    
    # get character data from player input #
    
    # name
    ans=""
    while (not ans or ans=='0'):
        ans=rog.prompt(
            Chargen.x1,Chargen.y1,Chargen.ww,Chargen.hh,maxw=20,
            q="what is your name?", mode="text"
            )
    Chargen._name = ans
    _title = 0
    
    # print char data so far
    print("name chosen: ", Chargen._name)
    libtcod.console_clear(rog.con_final())
    #

    player_ent = world.create_entity(
        cmp.Creature(),
        cmp.Actor(),
        cmp.Name(Chargen._name),
        cmp.Position(sx,sy),
        cmp.Image(1, COL['accent'], COL['black']),
        cmp.Mass(MASS_PLAYER),
        cmp.Human(),
        cmp.Value(20),
        cmp.Mobility(),
        cmp.OxygenTank(0),
        cmp.Battery(0),
        cmp.Engine(0),
        cmp.Hull(0),
        cmp.SenseSight(),
        cmp.SenseHearing(),
        cmp.Flags(),
        cmp.Modularity()
        )
    rog.add_module(player_ent, 1, entities.Gear_Torpedo())
    rog.add_module(player_ent, 2, entities.Gear_Screw())
    rog.add_module(player_ent, 3, entities.Gear_BallastTank())
    
    return player_ent








