'''

'''

import tcod as libtcod

from const import *
import rogue as rog
import orangio as IO
import player
import game

def main():
    # init
    
    rog.Rogue.create_settings() # later controllers may depend on settings
    rog.Rogue.create_window()
    rog.Rogue.create_consoles()
    rog.Rogue.create_world()
    rog.Rogue.create_controller()
    rog.Rogue.create_data()
    rog.Rogue.create_map(ROOMW,ROOMH)
##    rog.Rogue.create_fov_maps()
    rog.Rogue.create_clock()
    rog.Rogue.create_updater()
    rog.Rogue.create_log()
##    rog.Rogue.create_savedGame() # TODO: learn/use Pickle.
    rog.Rogue.create_processors()
    rog.Rogue.create_perturn_managers()
    rog.Rogue.create_const_managers()
    rog.Rogue.create_const_entities()

    rog.init_keyBindings()
        
    #map generation
    rog.getmap(rog.dlvl()).init_specialGrids() # inits fov_map; do this before you init terrain
    rog.getmap(rog.dlvl()).init_terrain(TILE_WALL) # clear the map to all walls
    rog.getmap(rog.dlvl()).generate_dlvl(rog.dlvl())

    rog.game_set_state("normal")



    # init player

    # TESTING THIS IS ALL TEMPORARY!!!
    # temporary: find a position to place the player
    xpos = 15
    ypos = 15
    _borders = 10
    while rog.getmap(rog.dlvl()).tileat(xpos, ypos) == TILE_WALL:
        xpos +=1
        if xpos >= ROOMW - _borders:
            xpos = _borders
            ypos += 1
        if ypos >= ROOMH:
            print("~~ ! FATAL ERROR ! Failed to place player in the map!")
            break
        
    rog.Rogue.create_player(xpos, ypos) # create player
    pc = rog.pc()
    
    # TESTING
    # HELP THE PLAYER TO SEE
    rog.create_envlight(16)

    


    #-----------------------------------------------#
    #               # MAIN GAME LOOP #              #
    #-----------------------------------------------#


    while rog.game_is_running():

        pc = rog.pc()
        
        # manually close game #
        if libtcod.console_is_window_closed():
            rog.end()
        
        # defeat conditions #
        if rog.on(pc, DEAD):
            rog.game_set_state("game over")
        
        # get input #
        pcInput=IO.get_raw_input()
        pcAct=IO.handle_mousekeys(pcInput).items()
        
        # commands that are available from anywhere #
        player.commands_const(pc, pcAct)
        
        # Finally record game state after any/all changes #
        gameState=rog.game_state()
        
        
                        #----------#
                        #   PLAY   #
                        #----------#
                
        #
        # normal game play
        #
        if gameState == "normal":
            game.play(pc, pcAct)
        #
        # manager game states #
        #
        elif gameState == "manager":
            manager=rog.get_active_manager()
            manager.run(pcAct)
            if manager.result:
                rog.close_active_manager()
        #
        
        elif gameState == "game over":
            rog.msg("You died...")

    
    # end while
# end def

if __name__=="__main__":
    main()

