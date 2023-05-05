'''

'''

import esper

from const import *
import components as cmp
import rogue as rog

#
# Actors processor
# and Action Queues processor
#
class ActorsProcessor(esper.Processor):
    def process(self):
        world=self.world

        # give AP to all actors
        for ent,actor in world.get_component(cmp.Actor):
            if rog.on(ent,DEAD):
                actor.ap=0
                continue
            actor.ap = 1 # temporary!
        
        # Action Queues
##        for ent, (qa, actor) in self.world.get_components(
##            cmp.DelayedAction, cmp.Actor ):
##            
##            # process interruptions and cancelled / paused jobs
##            if qa.interrupted:
##                ActionQueue._interrupt(ent, qa)
##                continue
##            if actor.ap <= 0:
##                continue
##            
##            # proceed with the job
##            # spend as much AP as we can / as we need
##            # automatically finishes the job if applicable
##            points = min(actor.ap, qa.ap)
##            ActionQueue._pay(ent, qa, actor, points)
        
        # If no Action Queued, then continue with turn as normal #
        
        # NPC / AI / computer turn
        for ent,(actor, _ai) in world.get_components(
            cmp.Actor, cmp.AI ):
##            print("ai func: ", _ai.func)
##            print("ent: ", world.component_for_entity(ent, cmp.Name).name)
            while actor.ap > 0:
                _ai.func(ent)
# end class


            
#
# Timers
#

class Timers:
    ID=0
    data={}
    @classmethod
    def add(self,t):
        _id=Timers.ID
        Timers.ID +=1
        Timers.data.update({_id : t})
        return _id
    @classmethod
    def remove(self,_id):
        Timers.data.remove(_id)

class TimersProcessor(esper.Processor):
    def process(self):
        removeList=[]
        for _id,t in Timers.data.items():
            t-=1
            if t<=0:
                removeList.append(_id)
            else:
                Timers.data.update({_id : t})
        for _id in removeList:
            Timers.remove(_id)

'''
timer=bt_managers['timers'].add(time)
return timer
'''


#
# Stats Upkeep processor
#

class UpkeepProcessor(esper.Processor):
    def process(self):
        # just query some components that match entities
        
        # oxygen depletion
        for ent, compo in self.world.get_component(cmp.OxygenTank):
            compo.oxygen -= 1
        # energy regen
        for ent, (engine,battery) in self.world.get_components(
            cmp.Engine, cmp.Battery):
            battery.energy = min(
                battery.energy_max, battery.energy + engine.energy_turn
                )
            
        # death #SHOULD THIS BE HANDLED HERE?
        for ent, compo in self.world.get_component(cmp.Hull):
            if compo.hp <= 0:
                rog.make(ent, DEAD)
# end class



#
# Status
#

class Status:
    @classmethod
    def add(self, ent, component, t=-1, q=None, firstVar=None):
        '''
            add a status if entity doesn't already have that status
            **MUST NOT set the DIRTY_STATS flag.
        '''
        world = rog.world()
        if world.has_component(ent, component): return False
        status_str = ""
        
        # message, attribute modifiers, aux. effects (based on status type)
        if component is cmp.StatusElec:
            status_str = " is electrified"
        if component is cmp.StatusStun:
            status_str = " is stunned"
        if component is cmp.StatusInked:
            status_str = " is inked"
        if component is cmp.StatusFear:
            status_str = " is afraid"
        if component is cmp.StatusWeak:
            status_str = " is weakened"
        if component is cmp.StatusFrenzied:
            status_str = " enters a frenzy"
        
        # TODO: events to display the messages
        # display only messages for Creature entities.
        name = world.component_for_entity(ent, cmp.Name)
        if (world.has_component(ent, cmp.Creature) and status_str):
            string = "{}{}".format(name.name, status_str)
            rog.msg(string) # TEMPORARY
        
        world.add_component(ent, component(t=t))
        return True
    # end def
        
    @classmethod
    def remove(self, ent, component):
        if not rog.world().has_component(ent, component):
            return False
        #if status_str:
            #"{}{}{}".format(TITLES[name.title], name.name, status_str)
        rog.world().remove_component(ent, component)
        return True
    # end def
    
    @classmethod
    def remove_all(self, ent): # TODO: finish this
        for status, component in cmp.STATUSES.items():
            if not rog.world().has_component(ent, component):
                continue
            #attribute modifiers
            #auxiliary effects
            #message
            rog.world().remove_component(ent, component)
    # end def
#
# Status Processor
#

# Processes statuses once per turn.

class StatusProcessor(esper.Processor):
    def process(self):
        world = self.world
        
        for ent, status in world.get_component(
            cmp.StatusElec ):
            status.timer -= 1
            if status.timer == 0:
                Status.remove(ent, cmp.StatusElec)
                continue
        for ent, status in world.get_component(
            cmp.StatusStun ):
            status.timer -= 1
            if status.timer == 0:
                Status.remove(ent, cmp.StatusStun)
                continue
        for ent, status in world.get_component(
            cmp.StatusInked ):
            status.timer -= 1
            if status.timer == 0:
                Status.remove(ent, cmp.StatusInked)
                continue
        for ent, status in world.get_component(
            cmp.StatusFear ):
            status.timer -= 1
            if status.timer == 0:
                Status.remove(ent, cmp.StatusFear)
                continue
        for ent, status in world.get_component(
            cmp.StatusWeak ):
            status.timer -= 1
            if status.timer == 0:
                Status.remove(ent, cmp.StatusWeak)
                continue
        for ent, status in world.get_component(
            cmp.StatusFrenzied ):
            status.timer -= 1
            if status.timer == 0:
                Status.remove(ent, cmp.StatusFrenzied)
                continue
# end class
