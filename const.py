'''
    const.py
'''

class Symbol:
    nextID = 1
    def __init__(self):
        self.ID = Symbol.nextID
        Symbol.nextID += 1
        
    def __key(self):
        return (self.attr_a, self.attr_b, self.attr_c)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, A):
            return self.__key() == other.__key()
        return NotImplemented
#end def




GEAR_PROPELLER = Symbol()
GEAR_BALLASTTANK = Symbol()
GEAR_SONARPULSE = Symbol()
GEAR_TORPEDO = Symbol()
GEAR_MINE = Symbol()
GEAR_DEPTHCHARGE = Symbol()
GEAR_GRAPPLINGHOOK = Symbol()

##ENGINE_NUCLEAR = Symbol()


OXYGEN_TIERS={
    # tier  : cost, oxygen max
    1       : (5,   80,),
    2       : (25,  160,),
    3       : (125, 320,),
    4       : (500, 640,),
    5       : (1500,1280,),
    6       : (3500,2560,),
}
BATTERY_TIERS={
    # tier  : cost, energy max
    1       : (5,   400,),
    2       : (20,  800,),
    3       : (100, 1600,),
    4       : (600, 3200,),
    5       : (3000,6400,),
    6       : (9999,12800,),
}
ENGINE_TIERS={
    # tier  : cost, +energy/turn
    1       : (10,  1,),
    2       : (40,  2,),
    3       : (360, 3,),
    4       : (960, 4,),
    5       : (3600,5,),
    6       : (8000,6,),
}


# move to different file
GEAR={
    # const             :( name, GearComponent, create script, equip script, use script
    GEAR_PROPELLER      :("Propeller", Gear_Propeller, create_gear_propeller, equip_propeller, None,),
    GEAR_BALLASTTANK    :("Ballast Tank", Gear_BallastTank, create_gear_ballast_tank, equip_ballast_tank, None,),
    GEAR_SONARPULSE     :("Sonar Pulse", Gear_SonarPulse, create_gear_sonar_pulse, None, use_sonar_pulse,),
    GEAR_TORPEDO        :("Torpedos", Gear_Torpedo, create_gear_torpedo, None, use_torpedo,),
    GEAR_MINE           :("Mines", Gear_Mine, create_gear_mine, None, use_mine,),
    GEAR_DEPTHCHARGE    :("Depth Charge", Gear_DepthCharge, create_gear_depth_charge, None, use_depth_charge,),
    GEAR_GRAPPLINGHOOK  :("Grappling Hook", Gear_GrapplingHook, create_gear_grappling_hook, None, use_grappling_hook,),
}
##ENGINES={
##    ENGINE_NUCLEAR      :("Thermonuclear Engine", 40, 2,),
##}



