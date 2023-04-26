
import esper


class Game:
    world = None
    
    @classmethod
    def create_world(cls):
        cls.world = esper.World()



def world():
    return Game.world
