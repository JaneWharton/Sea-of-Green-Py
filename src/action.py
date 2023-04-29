'''
    action.py
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
'''

# wrapper for things that creatures can do in the game
#   - actions cost energy
# PC actions are for the player object to give feedback
#   - (if you try to eat something inedible, it should say so, etc.)
#

import math

from const import *
import rogue as rog
import components as cmp
import misc
import maths
##import entities


dirStr=" <hjklyubn.>"

class Menu:
    pass



    # PC-specific actions first #


# pickup
# grab an item from the game world, removing it from the grid
def pickup_pc(pc):
    world = rog.world()
    pos = world.component_for_entity(pc, cmp.Position)
    pcx = pos.x
    pcy = pos.y
    rog.alert("Pick up what?{d}".format(d=dirStr))
    args=rog.get_direction()
    if not args:
        rog.alert()
        return False
    dx,dy,dz=args
    xx,yy = pcx + dx, pcy + dy
    
    things=rog.thingsat(xx,yy)
    if pc in things: #can't pick yourself up.
        things.remove(pc)

    choice=None
    if len(things) > 1:
        rog.alert("There are multiple things here. Pick up which item?")
        choices = [] #["all",] #should player be able to pickup multiple things at once? Maybe could be a delayed action?
        for thing in things:
            choices.append(thing)
        choice=rog.menu(
            "pick up", rog.view_port_x()+2, rog.view_port_y()+2, choices
            )
    else:
        if things:
            choice=things[0]

    if choice==-1:
        return False
    
    if (choice and choice != "all"):
        
        #thing is creature! You can't pick up creatures :( or can you...?
        if world.has_component(choice, cmp.Creature):
            rog.alert("You can't pick that up!")
            return False
        #thing is on fire, prompt user & burn persistent rogues
##        if rog.on(choice,FIRE):
##            answer=""
##            while True:
##                answer=rog.prompt(0,0,rog.window_w(),1,maxw=1,
##                    q="That thing is on fire! Are you sure? y/n",
##                    mode='wait',border=None)
##                answer=answer.lower()
##                if answer == "y" or answer == " " or answer == K_ENTER:
##                    rog.alert("You burn your hands!")
##                    rog.burn(pc, FIRE_BURN)
##                    rog.hurt(pc, FIRE_PAIN)
##                    rog.damage(pc, FIRE_DAMAGE)
##                    break
##                elif answer == "n" or answer == K_ESCAPE:
##                    return False
        # put in inventory
        pocketThing(pc, choice)
        
##    elif choice == "all": # TODO
##        for tt in things:
##            pocketThing(pc, tt)
        
    else:
        rog.alert("There is nothing there to pick up.")
        return False
    return True
# end def

def equipment_pc(pc):
    world=rog.world()
    assert(world.has_component(pc, cmp.Body))
    body = world.component_for_entity(pc, cmp.Body)
    x=0
    y=rog.view_port_y()
    equipment = {} # {'torso' : {name : (slot,eq_const,),},}
    
    # get core slots from body plan
    if body.plan==BODYPLAN_HUMANOID:
        # get all equipment from body
        equipment['torso'] = {
            'front':(body.core.front.slot,EQ_FRONT,),
            'back':(body.core.back.slot,EQ_BACK,),
            'core':(body.core.core.slot,EQ_CORE,),
            'hips':(body.core.hips.slot,EQ_HIPS,),
            'about':(body.slot,EQ_ABOUT,),
        }
    else:
        raise Exception #TODO: logic for other body types
    
    # get parts equipment
    for cls, part in body.parts.items():
        # what type of BP Container is this?
        if type(part)==cmp.BPC_Arms:
            equipment['arms'] = {}
            for i in range(len(part.arms)):
                arm=part.arms[i]
                n="{} ".format(BPINDEX[i])
                equipment['arms'].update( {
                    '{}hand (w)'.format(n) : (arm.hand.held,i+EQ_MAINHANDW,),
                    '{}hand'.format(n)     : (arm.hand.slot,i+EQ_MAINHAND,),
                    '{}arm'.format(n)      : (arm.arm.slot, i+EQ_MAINARM,),
                } )
        elif type(part)==cmp.BPC_Legs:
            equipment['legs'] = {}
            for i in range(len(part.legs)):
                leg=part.legs[i]
                n="{} ".format(BPINDEX[i])
                equipment['legs'].update( {
                    '{}foot'.format(n) : (leg.foot.slot,i+EQ_MAINFOOT,),
                    '{}leg'.format(n)  : (leg.leg.slot,i+EQ_MAINLEG,),
                } )
        elif type(part)==cmp.BPC_Heads:
            equipment['heads'] = {}
            for i in range(len(part.heads)):
                head=part.heads[i]
                n="{} ".format(rog.numberplace(i+1)) if i > 0 else ""
                equipment['heads'].update( {
                    '{}head'.format(n) : (head.head.slot,i+EQ_MAINHEAD,),
                    '{}face'.format(n) : (head.face.slot,i+EQ_MAINFACE,),
                    '{}neck'.format(n) : (head.neck.slot,i+EQ_MAINNECK,),
                    '{}eyes'.format(n) : (head.eyes.slot,i+EQ_MAINEYES,),
                    '{}ears'.format(n) : (head.ears.slot,i+EQ_MAINEARS,),
                } )
    # end for
    
    # init menu
    _TABS="... "
    data_i = 0
    data={} # for getting info about equipment slot for equipping/removing
    varia={}
    for k,v in equipment.items():
        varia["open_{}".format(k)] = False
    
##    rog.Rogue.pause_menu_key_listener()
    # run menu
    while True:
        menu={"return" : "return"}
        for k,v in equipment.items():
            if not v: continue
            if varia["open_{}".format(k)]:
                menu["- {}".format(k)] = "close_{}".format(k)
                for kk,vv in v.items():
                    slot,eq_const = vv
                    if slot.item:
                        itemname = rog.fullname(slot.item)
                    elif slot.covered:
                        itemname = "X"
                    else:
                        itemname = "-"
                    nkey = "{}{}: {}".format(_TABS,kk,itemname)
                    nval = "item_{}" if slot.item else "equip_{}"
                    nval = nval.format(data_i)
                    menu[nkey] = nval
                    data[data_i] = (slot, eq_const,)
                    data_i += 1
            else:
                menu["+ {}".format(k)] = "open_{}".format(k)
                
        opt=rog.menu("{}'s equipment".format(
            rog.gettitlename(pc)), x,y, menu.keys())
        
        if opt == -1: break
        selected=menu[opt]
        if "return" == selected: break
        # open / close submenus
        elif "open_" == selected[:5]:
            target = selected[5:]
            varia["open_{}".format(target)] = True
        elif "close_" == selected[:6]:
            target = selected[6:]
            varia["open_{}".format(target)] = False
        # equip item
        elif "equip_" == selected[:6]:
            data_id = int(selected[6:])
            slot, eq_const = data[data_id]
            item = _inventory_pc(pc)
            if slot.covered:
                alert("That slot is covered up by another piece of equipment!")
                break
            if item!=-1:
                equip_pc(pc, item, eq_const)
        # view item
        elif "item_" == selected[:5]:
            data_id = int(selected[5:])
            slot, eq_const = data[data_id]
            item = slot.item
            itemn = rog.fullname(item)
            menu_viewItem={
                "r" : "remove",
                "x" : "examine",
                }
            if world.has_component(item, cmp.Throwable):
                menu_viewItem['t'] = 'throw'
            if world.has_component(item, cmp.Usable):
                menu_viewItem['u'] = 'use'
            opt2=rog.menu(
                "{}".format(itemn.name), x,y,
                menu_viewItem, autoItemize=False
            )
            if opt2 == -1: break
            if opt2 == "use":
                use_pc(pc, item)
            elif opt2 == "remove":
                deequip_pc(pc, item)
            elif opt2 == "examine":
                examine_pc(pc, item)
            elif opt2 == "throw":
                target_pc_throw_item(pc, item)
    # end while
##    rog.Rogue.resume_menu_key_listener()
# end def


# abilities menu
def abilities_pc(pc):
    pass

# end def
def _process_selected_item_option(pc, selected, item, rmgcost=False):
    rmg=False
    if selected=='return':
        return
    elif selected == "remove":
        rmg=True
        deequip_pc(pc, item)
    elif selected == "drop":
        rmg=True
        drop_pc(pc, item)
    elif selected == "wear":
        rmg=True
        eq_type=rog.get_wear_type(pc, item)
        equip_pc(pc, item, eq_type)
    elif selected == "wield":
        rmg=True
        eq_type=rog.get_wield_type(pc, item) # TODO: make this func
        equip_pc(pc, item, eq_type)
    elif selected == "throw":
        rmg=True
        target_pc_throw_item(pc, item)
    elif selected == "eat":
        rmg=True
        eat_pc(pc, item)
    elif selected == "quaff":
        rmg=True
        quaff_pc(pc, item)
    elif selected == "use":
        rmg=True
        use_pc(pc, item)
    elif selected == "examine":
        rmg=True
        examine_pc(pc, item)
    # 
    if (rmgcost and rmg):
        rog.spendAP(pc, NRG_RUMMAGE)
# end def

# inventory menu
def inventory_pc(pc):
    ''' inventory menu with standard item viewing menu '''
    return inventory_pc_func(pc, _menu_item)
# end def
def inventory_pc_func(pc, func):
    ''' inventory menu with custom function for handling item '''
    item = _inventory_pc(pc)
    if item:
        return func(pc, item)
# end def
def _inventory_pc(pc):
    ''' inventory menu -> select an item from inventory '''
    world=rog.world()
    assert(world.has_component(pc, cmp.Inventory))
    pcInv = world.component_for_entity(pc, cmp.Inventory)
    x=rog.view_port_x()
    y=rog.view_port_y()
    selected=None
    item=None
    #   items menu
    item=rog.menu("{}'s inventory".format(
        rog.gettitlename(pc)), x,y, pcInv.data)
    return item
# end def
def _menu_item(pc, item):
    ''' viewing an item, menu for item interaction '''
    world = rog.world()
    selected=None
    if item != -1:
        itemn = rog.fullname(item)
        pos = world.component_for_entity(pc, cmp.Position)
        menu = _getMenuItems_item(item)
        opt=rog.menu(
            "{}".format(itemn.name), 1+rog.getx(pos.x),1+rog.gety(pos.y),
            menu, autoItemize=False
        )
        #print(opt)
        if opt == -1: return
        _process_selected_item_option(pc, opt, item, rmgcost=True)
    return (selected, item,)
# end def

def _getMenuItems_item(item) -> dict:
    ''' get a menu dict for an item -- using, throwing, dropping, etc. '''
    world = rog.world()
    keysItems={}
    #   get available actions for this item...
    
    if world.has_component(item, cmp.Equipped):
        keysItems.update({"r":"remove"})
    elif world.has_component(item, cmp.Held):
        keysItems.update({"r":"remove"})
        
    if world.has_component(item, cmp.Edible):
        keysItems.update({"e":"eat"})
    if world.has_component(item, cmp.Quaffable):
        keysItems.update({"q":"quaff"})
    if world.has_component(item, cmp.EquipableInHoldSlot):
        keysItems.update({"w":"wield"})
        # throwables - subset of equipables
        if world.has_component(item, cmp.Throwable):
            keysItems.update({"t":"throw"})
    if rog.has_wearable_component(item):
        keysItems.update({"W":"wear"})
    if world.has_component(item, cmp.Usable):
        keysItems.update({"u":"use"})
    if world.has_component(item, cmp.Openable):
        keysItems.update({"o":"open"})
    
    # generic
    keysItems.update({"x":"examine"})
    keysItems.update({"d":"drop"})
    #
    return keysItems
# end def

def drop_pc(pc,item):
    itemname=rog.fullname(item)
    rog.alert("Place {i} where?{d}".format(d=dirStr,i=itemname))
    args=rog.get_direction()
    if not args: return
    dx,dy,dz=args
    
    if not drop(pc, item, dx, dy):
        rog.alert("You can't put that there!")
    rog.update_game()
    rog.update_hud()

def open_pc(pc): # open or close
    # pick what to open/close
    rog.alert("Open/close what?{d}".format(d=dirStr))
    args=rog.get_direction()
    if not args: return
    dx,dy,dz=args
    pos = rog.world().component_for_entity(pc, cmp.Position)
    xto = pos.x + dx
    yto = pos.y + dy
    # do the open/close action
    success = openClose(pc, xto, yto)
    if not success:
        return
    rog.update_game()
    rog.update_hud()
##    rog.update_fov(pc) # updated by tile change func

def target_pc_generic(pc):
    ''' generic target function; target entity, then choose what to do '''
    def targetfunc(pc, ent):
        world=rog.world()
        tpos = world.component_for_entity(ent, cmp.Position)
        pos = world.component_for_entity(pc, cmp.Position)
        char = rog.getidchar(ent)
        menu={
            'a' : 'attack',
            's' : 'shoot',
            't' : 'throw',
            'x' : 'examine',
            }
        _menu={}
        for k,v in menu.items():
            _menu[v] = k
        opt=rog.menu(
            "targeting {}".format(char),
            rog.getx(tpos.x)+1,rog.gety(tpos.y),menu,
            autoItemize=False
            )
        if opt==-1:
            return
        choice=_menu[opt]
        # attack melee
        if choice=='a':
            fight_pc(pc, ent)
        # shoot / fire / loose arrow
        elif choice=='s':
            shoot_pc(pc, tpos.x, tpos.y)
        # throw weapon in main hand
        elif choice=='t':
            throw_pc(pc, tpos.x, tpos.y)
        # examine
        elif choice=='x':
            examine_pc(pc, ent)
    # end def
    target_pc(pc, targetfunc)
def target_pc(pc, func, *args, **kwargs):
    ''' target something then call func on it passsing in args,kwargs '''
    pos = rog.world().component_for_entity(pc, cmp.Position)
    rog.aim_find_target(pos.x, pos.y, func, *args, **kwargs)
# end def

def target_pc_throw_item(pc, item):
    ''' throw throwable item item at user-selected tile '''
    if rog.is_wielding_mainhand(pc):
        if rog.dominant_arm(pc).hand.held.item != item:
            rog.prompt(
                0,0,rog.window_w(),4,
                q="You are already wielding a different weapon in your dominant limb.",
                mode='wait'
                )
    target_pc(pc, throw_item_at, item=item)

def shoot_pc(pc, xdest, ydest) -> bool:
    marm=rog.dominant_arm(pc)
    if not marm:
        return False
    item = marm.hand.held.item
    if (not item or not rog.world().has_component(item,cmp.Shootable)):
        rog.prompt(
            0,0,rog.window_w(),4,
            q="You have nothing to shoot with.", mode='wait'
            )
        return False
    # success
    shoot(pc, xdest,ydest)
    return True
        
def throw_pc(pc, xdest, ydest) -> bool:
    wielding = rog.is_wielding_mainhand(pc)
    if not wielding:
        rog.prompt(
            0,0,rog.window_w(),4,
            q="Your dominant throwing limb wields no weapon.", mode='wait'
            )
        return False # failure
    # success
    throw(pc, xdest,ydest)
    return True

def fight_pc(pc, ent, tpos=None) -> bool:
    if tpos==None: tpos=rog.world().component_for_entity(ent,cmp.Position)
    if not rog.inreach(
        pos.x,pos.y, tpos.x,tpos.y,
        rog.getms(pc,'reach')//MULT_STATS
        ):
        rog.prompt(
            0,0,rog.window_w(),4,
            q="You can't reach that from here.", mode='wait'
            )
        return False # failure
    # success
    fight(pc, ent)
    return True
    
##def process_target(targeted):
##    
##    if targeted:
##        rog.alert("Target: {n} at ({x}, {y}) | x: strike / f: fire".format(
##            n=entname, x=pos.x,y=pos.y))
    
    

def examine_self_pc(pc):
    choices=['body (whole body)']
    
    ans=rog.menu(item=rog.menu("Examine what?".format(
        pcn.title,pcn.name), x,y, choices))

def equip_pc(pc, item, equipType):
    print("equipType: ", equipType)
    func, str1, str2 = _get_eq_data(equipType)

    # TODO: convert this to a queued action / get queued actions working!!
    
    result = func(pc, item) # try to equip
    
    # messages / alerts
    if result == 1:
        rog.update_hud()
        rog.update_final()
        rog.game_update()
    else:
        prep = "in" if str1=="wield" else "on" # preposition
        if result == -100:
            rog.alert("You can't {} that {} the {}.".format(str1,prep,str2))
        elif result == -101:
            rog.alert("You can't {} that {} the {}.".format(str1,prep,str2))
        elif result == -102:
            rog.alert("You are already {w}ing something in that {bp} slot.".format(w=str1, bp=str2))
# end def

def deequip_pc(pc, item):
    # TODO: AP action costs
    rog.remove_equipment(pc, item)
    rog.update_hud()
    rog.update_final()
    rog.game_update()

def examine_pc(pc, item):
    if rog.world().has_component(item, cmp.Description):
        descript=rog.world().component_for_entity(item, cmp.Description).description
        rog.alert(0,0,40,30, DESCRIPTIONS[descript])
    else:
        rog.alert(0,0,40,30, "<MISSING DESCRIPTION>")




#######################################################################
                    # Non-PC-specific actions #
#######################################################################


#wait
#just stand still and do nothing
#recover your Action Points to their maximum
def wait(ent):
    rog.setAP(ent, 0)
    rog.metabolism(ent, CALCOST_REST)
# end def

#use
#"use" an item, whatever that means for the specific item
# context-sensitive use action
def use(obj, item):
    pass

# equip
# try to put item in a specific slot; spend AP for success
def _equip(ent, item, equipType):
    result, compo = rog.equip(ent, item, equipType)
    if result == 1: # successfully equipped
        rog.spendAP(ent, compo.ap)
        w = EQ_TYPE_STRINGS[equipType][0]
        prep = EQ_TYPE_STRINGS[equipType][1]
        bp = EQ_TYPE_STRINGS[equipType][2]
        # example: "hobgoblin wield wet plastic knife"
        pos = world.component_for_entity(ent, cmp.Position)
        rog.event_sight(pos.x,pos.y, "{n} {w} {i}".format(
            n=rog.getname(ent), i=rog.fullname(item), w=w))
        # wordy text (idea: option for wordy or terse msg text)
        # example: "the hobgoblin wields the plastic knife in his mainhand"
##        rog.msg("{n} {w}s {i} {pre} {prn} {bp}".format(
##            n=rog.gettitlename(ent), i=rog.gettitlename(item),
##            w=w, prn=rog.get_pronoun_possessive(ent), pre=prep, bp=bp))
        
    return result
# end def

def pocketThing(ent, item): #entity puts item in its inventory
    world = rog.world()
    rog.pocket(ent, item)
    # messages
    pos = world.component_for_entity(ent, cmp.Position)
    rog.event_sight(pos.x,pos.y, "{n} pack {ni}.".format(
        n=rog.getname(ent), ni=rog.fullname(item)))
    rog.event_sound(pos.x,pos.y, SND_RUMMAGE)
    # over-encumbered message
    if rog.getms(ent, 'enc') >= rog.getms(ent, 'encmax'):
        rog.event_sight(pos.x,pos.y, "{n} overburdened.".format(
            n=rog.getname(ent)))
    rog.event_sound(pos.x,pos.y, SND_RUMMAGE)
    return True

def drop(ent, item, dx, dy):
    assert((abs(dx) <= 1 and abs(dy) <= 1))
    
    world = rog.world()
    pos = world.component_for_entity(ent, cmp.Position)
    
    if not rog.wallat(pos.x+dx,pos.y+dy):
    #   success, drop the item.
        rog.drop(ent,item, dx,dy)
        rog.spendAP(ent, NRG_RUMMAGE)
        pos = world.component_for_entity(ent, cmp.Position)
        rog.event_sight(pos.x,pos.y, "{n} drop {ni}.".format(
            n=rog.getname(ent), ni=rog.fullname(ent)))
        return True
    
    else: # failure
        return False
# end def


def move(ent,dx,dy, pace=-1, mx=1):  # actor locomotion
    '''
        move: generic actor locomotion
        Returns True if move was successful, else False
        Parameters:
            ent : entity that's moving
            dx  : change in x position
            dy  : change in y position
            pace: rate of movement (PACE_ const)
                    -1: use the current pace the actor is moving at
            mx  : AP/Calorie/Stamina cost multiplier value
    '''
    # init
    world = rog.world()
    pos = world.component_for_entity(ent, cmp.Position)
    xto = pos.x + dx
    yto = pos.y + dy
    terrainCost = rog.cost_move(pos.x, pos.y, xto, yto, None)
    if terrainCost == 0:
        return False        # 0 means we can't move there
    actor = world.component_for_entity(ent, cmp.Actor)
    
    # AP cost
    actor.ap -= 1
    
    # perform action
    rog.port(ent, xto, yto)
    return True


    #------------#
    #   COMBAT   #
    #------------#

def formatCombatResult(dm=0,ro=0,pn=0):
    return " (-{dm}|r{ro}|x{pn})".format(dm=_dmg,ro=roll,pn=pens)

##def _calc_bpdmg(pens,bonus,dmg,hpmax):
##    bpdmg = misc.dice_roll(6) - 6 + pens + bonus + (8*dmg//hpmax)
##    return max(0, min( BODY_DMG_PEN_BPS, bpdmg )) # constraints

def _calc_pens(pen, prot, arm):
    ''' calculate number of penetrations and the armor value '''
    pens=0
    while (pen-prot-(CMB_ROLL_PEN*pens) >= misc.dice_roll(CMB_ROLL_PEN)):
        pens += 1   # number of penetrations ++
    if pens<=0: # no need to calculate new armor value. Just return old.
        return (0, arm,)
    return (pens, rog.around(arm * (0.5**pens)),)

#
# strike
# hit an entity with your weapon (or limb)
#
class _StrikeReturn:
    def __init__(self,
                 hit,pens,trueDmg,killed,crit,rol,ctrd,
                 feelStrings,grazed,canreach
                 ):
        self.hit=hit
        self.pens=pens
        self.trueDmg=trueDmg
        self.killed=killed
        self.crit=crit
        self.rol=rol
        self.ctrd=ctrd
        self.feelStrings=feelStrings
        self.grazed=grazed
        self.canreach=canreach
# end class

def _strike(attkr,dfndr,aweap,dweap,
            adv=0,power=0, counterable=False,
            bptarget=None, targettype=None,
            apos=None, dpos=None):
    '''
        strike the target with your primary weapon or body part
            this in itself is not an action -- requires no AP
        (this is a helper function used by combat actions)

        adv         advantage to the attacker
        power       amount of power the attacker is putting into the attack
        counterable bool, can this strike be counter-striked?
        bptarget    None: aim for center mass. else a BP component object
        targettype  BP_ const indicates what type of BP is being targeted
        apos;dpos   Attacker Position component; Defender Position component
    '''
    # init
    hit=killed=crit=ctrd=grazed=canreach=False
    pens=trueDmg=rol=0
    feelStrings=[]
    
        # get the data we need
    world = rog.world()

    # components
    abody=world.component_for_entity(attkr, cmp.Body)
    dbody=world.component_for_entity(dfndr, cmp.Body)
    if not apos:
        apos = world.component_for_entity(attkr,cmp.Position)
    if not dpos:
        dpos = world.component_for_entity(dfndr,cmp.Position)

    # skill
    if (aweap and world.has_component(aweap,cmp.WeaponSkill)): # weapon skill
        skill=world.component_for_entity(aweap, cmp.WeaponSkill).skill
        skillLv=rog.getskill(attkr, skill)
    else: # boxing
        skill=SKL_BOXING
        skillLv=rog.getskill(attkr, SKL_BOXING)
    
    # attacker stats
    _str =  rog.getms(attkr,'str')//MULT_STATS
    asp =   max( MIN_ASP, rog.getms(attkr,'asp') )
    acc =   rog.getms(attkr,'atk')//MULT_STATS
    pen =   rog.getms(attkr,'pen')//MULT_STATS
    dmg =   max( 0, rog.getms(attkr,'dmg')//MULT_STATS )
    areach =rog.getms(attkr,'reach')//MULT_STATS
        # attacker's weapon stats
    if aweap:
        equipable = world.component_for_entity(aweap, cmp.EquipableInHoldSlot)
        weapforce = equipable.force
        aweap1mat = rog.world().component_for_entity(aweap, cmp.Form).material
    else:
        weapforce = 1
        aweap1mat = rog.world().component_for_entity(attkr, cmp.Form).material
        # force
    strmult = rog.att_str_mult_force(_str)
    _massm = max(0, 0.25 + power*0.25)
    massmult = _massm * rog.getms(attkr, 'mass')/MULT_MASS
    force = (power+1) * strmult * weapforce * massmult
    
    # defender stats
    dhpmax =rog.getms(dfndr,'hpmax')
    dv =    rog.getms(dfndr,'dfn')//MULT_STATS
    prot =  rog.getms(dfndr,'pro')//MULT_STATS
    arm =   rog.getms(dfndr,'arm')//MULT_STATS
    ctr =   rog.getms(dfndr,'ctr')//MULT_STATS
    dreach =rog.getms(dfndr,'reach')//MULT_STATS
    resphys = rog.getms(dfndr,'resphys')
        # defender's weapon stats
    # material
    if dweap:
        dweap1mat = rog.world().component_for_entity(dweap, cmp.Form).material
    else:
        dweap1mat = rog.world().component_for_entity(dfndr, cmp.Form).material

    # differences btn attacker and defender
##    dcm =   rog.getms(attkr,'height') - rog.getms(dfndr,'height')
##    dkg =   (rog.getms(attkr,'mass') - rog.getms(dfndr,'mass'))//MULT_MASS # only affects grappling, not fighting
    
    # advantages from stat differences
    # lesser reach has the advantage
    adv = dreach-areach
    
        # roll dice, calculate hit or miss
    rol = misc._roll(CMB_ROLL_ATK)
    
    if not rog.inreach(dpos.x,dpos.y, apos.x,apos.y, areach):
        canreach=False
        hitDie=0
    else:
        canreach=True
        hitDie = rol + acc + adv - dv
        
    if (rog.is_pc(dfndr) and rol==1): # when player is attacked, a roll of 1/20 always results in a miss.
        hit=False
    elif (rog.is_pc(attkr) and rol==20): # when player attacks, a roll of 20/20 always results in a hit.
        hit=True
    elif (hitDie >= 0): # normal hit roll, D&D "to-hit/AC"-style
        hit=True
    else: # miss
        hit=False
    
    # perform the attack
##    rog.flank(dfndr, 1) #TODO: flanking
    if hit:
        grazed = (hitDie==0)

        # counter-attack
        if (counterable
        and rog.inreach(dpos.x,dpos.y, apos.x,apos.y, dreach)
        and rog.on(dfndr,CANCOUNTER)
            ):
            if (misc.dice_roll(100) <= ctr):
                dweap = rog.dominant_arm(dfndr).hand.held.item
                ret=_strike(
                    dfndr, attkr, dweap, aweap,
                    power=0, counterable=False,
                    apos=dpos,dpos=apos
                    )
                rog.makenot(dfndr,CANCOUNTER)
                ctrd=True
        # end if
        
        # penetration (calculate armor effectiveness)
        if not grazed: # can't penetrate if you only grazed them
            pens, armor = _calc_pens(pen, prot, arm)
        else:
            armor = arm
        # end if
        
            #------------------#
            # calculate damage #
            #------------------#
        
        # physical damage
        
        if grazed:
            dmg = dmg*0.5
        resMult = 0.01*(100 - resphys)     # resistance multiplier
        rawDmg = dmg - armor
##        rmp = CMB_MDMGMIN + (CMB_MDMG*random.random()) # random multiplier -> variable damage
        
        # bonus damage (bonus to flesh, to armor, etc.)
##        dfndrArmored = False
##        if world.has_component(dfndr, cmp.EquipBody):
##            item=world.component_for_entity(dfndr, cmp.EquipBody).item
##            if item is not None:
##                if rog.on(item, ISHEAVYARMOR): # better way to do this?
##                    dfndrArmored = True
##        if dfndrArmored: # TODO: implement this and bonus to flesh!!!
##            if world.has_component(aweap, cmp.BonusDamageToArmor):
##                compo=world.component_for_entity(aweap, cmp.BonusDamageToArmor)
##                bonus = compo.dmg
##                rawDmg += bonus

        trueDmg = rog.around( max(0,rawDmg*resMult) ) #*rmp # apply modifiers
        
        # elemental damage
        if (aweap and world.has_component(aweap,cmp.ElementalDamageMelee)):
            elements=world.component_for_entity(aweap,cmp.ElementalDamageMelee).elements
        else:
            elements={}
        
        # extra critical damage: % based on Attack and Penetration
        # you need more atk and more pen than usual to score a crit.
        if (hitDie >= misc.dice_roll(20) and pen-prot >= 24 ):
            # critical hit!
            if skill:
                critMult = WEAPONCLASS_CRITDAMAGE[skill]
            else: # default crit damage
                critMult = WEAPONCLASS_CRITDAMAGE[0]
            # critical hits do a percentage of target's max HP in damage
            trueDmg += math.ceil(rog.getms(dfndr, 'hpmax')*critMult)
            crit=True
        # end if

            #--------------------#
            # body / gear damage #
            #--------------------#
        
        # TODO: pick body part to hit randomly based on parameters
        if bptarget:
            bptarget = bptarget # TEMPORARY
        else:
            bptarget = rog.findbps(dfndr, cmp.BP_TorsoFront)[0]  # TEMPORARY
        # end if
        
        # body damage
        # damage body part (and possibly inflict status)
        if trueDmg > 0:
            rog.attackbp(attkr, dfndr, bptarget, aweap, trueDmg, skill)
        
        # gear damage #
        gearitem = bptarget.slot.item
        if (gearitem and pens < GEAR_DMG_PEN_THRESHOLD):
            # the damage dealt to the gear is based on attacker's damage,
            # and the armor's AV; it has nothing to do with the stats of
            # the character who's wearing the gear.
            # Idea: could depend on armor-wearing skill of the wearer...
            geardmg = dmg - rog.getms(gearitem, 'arm')
            rog.damage(gearitem, geardmg)
##            if geardmg >= rog.material_damage_threshold(dweap1mat):
##                rog.breakitem(gearitem, aweap)
        # end if
        
            #-------------------------------------#
            # deal damage, physical and elemental #
            #-------------------------------------#
            
        rog.damage(dfndr, trueDmg)
        
        # TODO: SP damage
##        # sap some SP from defender;
##        rog.sap(dfndr, force*...)
        # TODO: force damage -> balance, knockdown, knockback, etc.
        
        for element, elemDmg in elements.items():
            # elemental damage affected by how well the attack connected
            if grazed:
                elemDmg = elemDmg * 0.5
            elif crit:
                elemDmg = elemDmg * 1.5
            # elements
            if element == ELEM_FIRE:
                rog.burn(dfndr, elemDmg)
                feelStrings.append("burns!")
            elif element == ELEM_BIO:
                rog.disease(dfndr, elemDmg)
            elif element == ELEM_ELEC:
                rog.electrify(dfndr, elemDmg)
                feelStrings.append("zaps!")                                                                                                                                                                                                                     # I love you Krishna
            elif element == ELEM_CHEM:
                rog.exposure(dfndr, elemDmg)
                feelStrings.append("stings!")
            elif element == ELEM_RADS:
                rog.irradiate(dfndr, elemDmg)
            elif element == ELEM_IRIT:
                rog.irritate(dfndr, elemDmg)
            elif element == ELEM_COLD:
                rog.frost(dfndr, elemDmg)
            elif element == ELEM_PAIN:
                # reduce pain if damage is low
                if trueDmg <= 0:
                    elemDmg = 1
                elif trueDmg <= 1:
                    elemDmg = elemDmg // 3
                elif trueDmg <= 2:
                    elemDmg = elemDmg // 2
                elif trueDmg <= 3:
                    elemDmg = elemDmg * 0.75
                rog.hurt(dfndr, elemDmg)
            elif element == ELEM_BLEED:
                if pens == 0: continue   # if failed to penetrate, no bleeding
                rog.bleed(dfndr, elemDmg)
            elif element == ELEM_RUST:
                if pens == 0: continue   # if failed to penetrate, continue
                rog.rust(dfndr, elemDmg)
            elif element == ELEM_ROT:
                if pens == 0: continue   # if failed to penetrate, continue
                rog.rot(dfndr, elemDmg)
            elif element == ELEM_WET:
                rog.wet(dfndr, elemDmg)
        # end if
        
        killed = rog.on(dfndr,DEAD) #...did we kill it?
    # end if
    #
    # return info for the message log
    return _StrikeReturn(
        hit,pens,trueDmg,killed,crit,rol,ctrd,feelStrings,grazed,
        canreach
        )
# end def

def fight(attkr,dfndr,adv=0,power=0, terse=True):
    '''
    Combat function. Engage in combat:
    # Arguments:
        # attkr:    attacker (entity initiating combat)
        # dfndr:    defender (entity being attacked by attacker)
        # adv:      advantage attacker has over defender (bonus to-hit)
        # power:    amount of umph to use in the attack
        # grap:     grappling attack? (if False, do a striking attack)
        
        TODO: implement this!
        # power:    how much force putting in the attack?
            -1== subpar: use less than adequate force (bad leverage)
            0 == standard: use muscles in the attacking limb(s) / torso
            1 == heavy hit: use muscles in whole body (offensive)
                *leaves those body parts unable to provide defense
                 until your next turn
    '''
    
##    TODO: when you attack, look at your weapon entity to get:
        #-material of weapon
        #-flags of weapon
        
    # setting up
    world = rog.world()
    aactor = world.component_for_entity(attkr, cmp.Actor)
    apos = world.component_for_entity(attkr, cmp.Position)
    dpos = world.component_for_entity(dfndr, cmp.Position)
    aname=rog.getname(attkr) if terse else rog.gettitlename(attkr)
    dname=rog.getname(dfndr) if terse else rog.gettitlename(dfndr)
        # weapons of the combatants (temporary ?)
    abody = world.component_for_entity(attkr, cmp.Body)
    dbody = world.component_for_entity(dfndr, cmp.Body)
    aarms = abody.parts.get(cmp.BPC_Arms, None)
    darms = dbody.parts.get(cmp.BPC_Arms, None)
    if aarms:
        aarm1 = aarms.arms[0]
        aarm2 = aarms.arms[1]
    else:
        aarm1=aarm2=None
    aweap1 = aarm1.hand.held.item if aarm1 else None
    aweap2 = aarm2.hand.held.item if aarm1 else None
    if darms:
        darm1 = darms.arms[0]
        darm2 = darms.arms[1]
    else:
        darm1=darm2=None
    dweap1 = darm1.hand.held.item if darm1 else None
    dweap2 = darm2.hand.held.item if darm1 else None
    #
    
    # ensure you have the proper amount of Stamina
    if aweap1:
        equipable = world.component_for_entity(aweap1, cmp.EquipableInHoldSlot)
        stamina_cost = equipable.stamina
    else:
        stamina_cost = STA_PUNCH # TODO: get from limb-weapon! (and implement limb-weapons!)
    if stamina_cost > rog.getms(attkr, "mp"):
        power=-1
    
    # counterability is affected by range/reach TODO!
##    dist=max(abs(apos.x - dpos.x), abs(apos.x - dpos.x))
##    if rog.inreach(areach1, dist):
##        counterable = True
##    else:
##        counterable = False
    counterable = True
    
    # strike!
    ret=_strike(
        attkr, dfndr, aweap1, dweap1,
        adv=adv, power=power, counterable=counterable,
        apos=apos,dpos=dpos
        )
    
    # AP cost
    asp = max(1, rog.getms(attkr, 'asp'))
    aactor.ap -= rog.around( NRG_ATTACK * AVG_SPD / asp )
    
    # stamina cost
    rog.sap(attkr, stamina_cost)
                 
    # metabolism
    rog.metabolism(attkr, CALCOST_HEAVYACTIVITY)
    
    # finishing up
    message = True # TEMPORARY!!!!
    a=aname
    n=dname
    x='.'
    ex=m=""
    dr="d{}".format(CMB_ROLL_ATK) #"d20"
        # make a message describing the fight
    if message:
        # TODO: make a more consise message, less detail about specific
        #   calculations
        # IDEA: show calculations/detail in the HUD (a la Cogmind)
        #   while messages are reserved for very simple observations.
        
        # TODO: show messages for grazed, crit, counter, ret.feelStrings
        if ret.canreach==False:
            rog.event_sight(
                dpos.x, dpos.y,
                "{a} strikes out at {n}, but cannot reach.".format(a=a,n=n)
            )
        if ret.hit==False:
            v="misses"
            if rog.is_pc(attkr):
                ex=" ({dr}:{ro})".format(dr=dr, ro=ret.rol)
        else: # hit
            if rog.is_pc(attkr):
                ex=" ({dm}x{p})".format( #{dr}:{ro}|
                    dm=ret.trueDmg, p=ret.pens ) #dr=dr, ro=ret.rol, 
            if ret.killed:
                v="kills"
            else:
                if ret.grazed:
                    v="grazes"
                else:
                    v = "*crits*" if ret.crit else "hits"
        if ret.ctrd:
            # TODO: more detailed counter message (i.e., " and ... counters (8x2)")
            m = " and {n} counters".format(n=n)
        rog.event_sight(
            dpos.x,dpos.y,
            "{a} {v} {n}{ex}{m}{x}".format(
                a=a,v=v,n=n,ex=ex,x=x,m=m )
        )
        rog.event_sound(dpos.x,dpos.y, SND_FIGHT)
#



def throw_item_at(ent, target, *args, **kwargs):
    pos=rog.world().component_for_entity(target,cmp.Position)
    item=kwargs['item']
    rog.equip(ent, item, EQ_MAINHANDW)
    throw(ent, pos.x,pos.y)
def throw(ent, xdest,ydest, power=0):
    world = rog.world()
    arm=rog.dominant_arm(ent)
    if not arm:
        return False
    weap = arm.hand.held.item
    if not weap:
        return False
    
    # get thrower's stats
    equipable = world.component_for_entity(weap, cmp.EquipableInHoldSlot)
    weapforce = equipable.force
    apos = world.component_for_entity(ent, cmp.Position)
    rng = rog.getms(ent, 'trng')
    atk = (rog.getms(ent, 'tatk') + rog.getms(ent, 'atk'))//MULT_STATS
    pen = (rog.getms(ent, 'tpen') + rog.getms(ent, 'pen'))//MULT_STATS
    dmg = (rog.getms(ent, 'tdmg') + rog.getms(ent, 'dmg'))//MULT_STATS
    _str = rog.getms(ent, 'str')//MULT_STATS
    
    # get the entity we're (trying to) target
    dfndr = rog.monat(xdest,ydest)
    
    if not dfndr:
        pass # attack ground (TODO)
    
    # calculate which tile to aim towards
    dist = rog.dist(apos.x,apos.y,xdest,ydest)
    if dist <= rng+0.3334: # add a margin of error
        tile = (xdest,ydest,)
    else:
        d1 = 2  # deviation of missile (temporary -- TODO: deviation increases based on distance)
        d2 = 3
        tile = (xdest+misc.dice_roll(d2)-d1, ydest+misc.dice_roll(d2)-d1,)
    tilepos = cmp.Position(tile[0], tile[1])
    
    # init -- prepare to throw
    rog.dewield(ent, EQ_MAINHANDW)
    prevx=apos.x
    prevy=apos.y
    strmult = rog.att_str_mult_force(_str)
    force = (power+1) * strmult * weapforce * rog.getms(weap, 'mass')/MULT_MASS
    
    # throw the item at dfndr at position tilepos
    missile_attack(
        ent, weap, apos, tilepos,
        dfndr=dfndr, force=force, rng=rng, atk=atk, dmg=dmg, pen=pen
        )
    return True # return success
# end def

def shoot(ent, xdest,ydest):
    pass

def missile_attack(
    attkr, ent, spos, dpos, dfndr=0,force=1,rng=0,atk=0,dmg=1,pen=0
    ):
    ''' use a line-drawing 'missile' to attack from a distance
        attkr: entity attacking
        ent: entity acting as a missile
        spos: start position
        dpos: destination position (not necessarily dfndr's position)
        dfndr: entity being attacked, if any
        force: momentum of the missile
        atk: missile's atk when/if it reaches target
        dmg: missile's dmg when/if it hits target
        pen: missile's pen when/if it hits target
    '''
    world=rog.world()
    hitDie=pens=roll=0
    land=breaks=None
    hit=False
    pos = world.component_for_entity(attkr, cmp.Position)
    dpos= world.component_for_entity(dfndr, cmp.Position)
    
    # draw line to target and try to attack
    for (xx,yy,) in rog.line(spos.x,spos.y, dpos.x,dpos.y):
        if land:
            break
        
        # collision with creature at this tile
        mon=rog.monat(xx,yy)
        if (not mon or mon == attkr):
            continue
        # get defender's stats
        monpos = world.component_for_entity(mon, cmp.Position)
        mdfn = rog.getms(mon, 'dfn')//MULT_STATS
        marm = rog.getms(mon, 'arm')//MULT_STATS
        mpro = rog.getms(mon, 'pro')//MULT_STATS
        mhpmax = rog.getms(mon, 'hpmax')
        #
        
        # by default, item lands at feet of monster.
        land=(monpos.x,monpos.y,)
        
        # is this our target? If not, incur penalty to accuracy
        if (mon != dfndr):
            # higher penalty the further we are from our original target
            atk -= int(10*rog.dist(xx,yy, dpos.x,dpos.y))

        # penalty to accuracy based on distance
        excessd = rog.dist(dpos.x,dpos.y, xx,yy) - rng
        if excessd:
            atk -= int(RNG_ATK_PENALTY*excessd)
        
        # roll to hit
        roll=misc.dice_roll(20)
        hitDie = roll + atk - mdfn
        if hitDie > 0:
            hit=True
            pens, armor = _calc_pens(pen, mpro, marm)
            _dmg = max(0, dmg - armor)
            if _dmg > 0:
                rog.collide(ent, 1, mon, _dmg, force)
                # bp damage (TODO: REFACTOR!!!)
##                if world.has_component(mon, cmp.Body):
##                    body = world.component_for_entity(mon, cmp.Body)
##                    bptarget = rog.randombp(body)
##                    skilltype = world.component_for_entity(
##                        ent, cmp.WeaponSkill).skill
##                    bpdmg = _calc_bpdmg(pens, 0, _dmg, mhpmax)
##                    dmgtype = rog.get_dmgtype(0, ent, skilltype)
##                    if world.has_component(ent, cmp.DamageTypeMelee):
##                        dtcompo=world.component_for_entity(ent,cmp.DamageTypeMelee)
##                        bpdmg += dtcompo.types[dmgtype]
##                    if bpdmg > 0:
##                        rog.damagebp(bptarget, dmgtype, bpdmg-1)
            # stick into target (TODO)
            break
        # end if
        
        # collision with wall
        elif rog.wallat(xx,yy):
            # TODO: ricochet
            land=(prevx,prevy,)
            rog.collide(ent, 1, rog.ent_wall(), 0, force)
        
        # range limit (add a tiny random deviation)
        elif rog.dist(dpos.x,dpos.y, xx,yy) > rng + misc.dice_roll(3):
            land=(xx,yy,)
        
        # remember previous tile, for collision purposes
        prevx=xx
        prevy=yy
    # end for
    
    # does the item land somewhere nearby or break?
    if breaks: # item breaks if possible else lands
        # if world.has_component(ent, cmp.Breakable):
        rog.port(ent, land[0],land[1]) #(TEMPORARY)
            #breakthing()
    elif land:
        rog.port(ent, land[0],land[1])
    else: # remove the item from the game world
        rog.kill(ent)
    
    # message
    if (attkr == rog.pc() and hit):
        result = formatCombatResult(dm=_dmg,ro=roll,pn=pens)
    else:
        result = ", missing"
        rog.event_sight(pos.x,pos.y, "{a} launch {i} at {d}{result}".format(
        a=rog.gettitlename(attkr),
        i=rog.gettitlename(ent),
        d=rog.gettitlename(dfndr),
        result=result))
# end def

    

#######################################################################
            # Multi-turn actions / delayed actions #
#######################################################################


#



# TODO: use this instead of old tilemap _draw_what_... func.
# this will also be used by AI function instead of existing code.
# returns a dict of all visible entities and how visible they are.
# from there we must remember those entities and, if an AI, choose
# what to do about it, or, if the player, identify the visible things.
# then for the player, draw the terrain around them and then draw the
# visible entities on top.
def _get_entities_in_view(viewer, sight):
    ''' get a list of the entities the viewer can see with sight sight
        Returns: {cmp.Position() : {entity : visibility}}
    '''
    world=rog.world()
    pos=world.component_for_entity(viewer, cmp.Position)
    w=rog.window_w()
    h=rog.window_h()
    seen={}
    #   visible entities can be identified by sight
    #   if unidentified and barely visible, you see a '?'
    #   if unidentified and visible, you can see their shape
    #   if partially identified, you can see their generic ID
    #   if identified, you can see their name
    #   if fully identified, you can see their stats
    
    for     x in range( max(0, pos.x-sight), min(w, pos.x+sight+1) ):
        for y in range( max(0, pos.y-sight), min(h, pos.y+sight+1) ):
##                print("tile at {} {} has light level {}".format(x ,y, self.get_light_value(x,y)))
            if (x==pos.x and y==pos.y):
                continue
            if not rog.can_see(viewer, x, y, sight):
                continue
            
            # get return data from rog.can_see
            ret=rog.fetchglobalreturn()
            if ret: # unpack
                dist, plight = ret
            
            ents=self.thingsat(x, y)
            
            if ents:
                charDiscover = None
                entDrawn = False
                
                for ent in ents:
                    # calculate visibility
                    camo = rog.getms(ent, 'camo')
                    visibility=rog.visibility(viewer,sight,plight,camo,dist)
##                    print('visibility: ',visibility)
##                    print('stats: s{}, l{}, c{}, d{}'.format(sight, plight, camo, dist))

                    if seen.get(Position(x,y), None):
                        seen[Position(x,y)].update({ent : visibility})
                    else:
                        seen.update({Position(x,y): {ent : visibility}})
                # end for
        # end for
    # end for
    return seen
# end def














# other actions #

#TODO: UPDATE THIS FUNCTION
def explosion(bomb):
    rog.msg("{t}{n} explode <UNIMPLEMENTED>".format(t=bomb.title, n=bomb.name))
    '''
    con=libtcod.console_new(ROOMW, ROOMH)
    fov=rog.fov_init()
    libtcod.map_compute_fov(
        fov, bomb.x,bomb.y, bomb.r,
        light_walls = True, algo=libtcod.FOV_RESTRICTIVE)
    for x in range(bomb.r*2 + 1):
        for y in range(bomb.r*2 + 1):
            xx=x + bomb.x - bomb.r
            yy=y + bomb.y - bomb.r
            if not libtcod.map_is_in_fov(fov, xx,yy):
                continue
            if not rog.is_in_grid(xx,yy): continue
            dist=maths.dist(bomb.x,bomb.y, xx,yy)
            if dist > bomb.r: continue
            
            thing=rog.thingat(xx, yy)
            if thing:
                if rog.on(thing,DEAD): continue
                
                if thing.isCreature:
                    decay=bomb.dmg/bomb.r
                    dmg= bomb.dmg - round(dist*decay) - thing.stats.get('arm')
                    rog.damage(thing, dmg)
                    if dmg==0: hitName="not damaged"
                    elif rog.on(thing,DEAD): hitName="killed"
                    else: hitName="hit"
                    rog.msg("{t}{n} is {h} by the blast.".format(
                        t=thing.title,n=thing.name,h=hitName) )
                else:
                    # explode any bombs caught in the blast
                    if (thing is not bomb
                            and hasattr(thing,'explode')
                            and dist <= bomb.r/2 ):
                        thing.timer=0
                        '''
