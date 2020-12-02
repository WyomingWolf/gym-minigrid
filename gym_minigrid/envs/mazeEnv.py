from gym_minigrid.minigrid import *
from gym_minigrid.register import register
import numpy as np

class MazeEnv(MiniGridEnv):
    """
    Empty grid environment, no obstacles, sparse reward
    """

    def __init__(
        self,
        size=3, # int(1-6); increase maze size
        limit=2, # int(1-size); increase room size
        lava_prob=0, # float(0-0.2); chance to add lava float(0-0.2)
        obstacle_level=0, # float(0-5); increase obstacles
        box2ball=0, # flaot(0-1) chance to convert box to ball
        door_prob=0, # float(0-0.5); chance to add doors
        lock_prob=0, # float(0-0.5); chance to add locked doors and keys
        wall_prob=1, # float(0-1); cahnce to keep wall
        agent_start_pos=(1,1),
        agent_start_dir=0,
        seed=0
    ):
        self.agent_start_pos = agent_start_pos
        self.agent_start_dir = agent_start_dir
        self.size = pow(2,size+1)+1
        self.limit = pow(2,limit)+1
        self.lava_prob = lava_prob
        self.obstacle_level = obstacle_level
        self.box2ball = box2ball
        self.door_prob = door_prob
        self.lock_prob = lock_prob
        self.wall_prob = wall_prob
        
        '''
        if self.door_level > 1:
            self.lock = True
        else:
            self.lock = False
        '''
        super().__init__(
            grid_size = self.size,
            max_steps = 4*self.size*self.size,
            seed = seed,
            # Set this to True for maximum speed
            see_through_walls=True
        )

    def _gen_grid(self, width, height):
        # Create an empty grid
        self.grid = Grid(width, height)

        # Generate the surrounding walls
        self.grid.wall_rect(0, 0, width, height)

        # Generate maze
        if self.limit < self.size:
            self._recursive_division(1, 1, self.size-2, self.limit, 0)

        # place moveable objeccts
        if self.obstacle_level > 0:
            num_obstacle = int(self.size*self.obstacle_level)
            for i in range(num_obstacle):
                # get position
                x = self._rand_int(0, int((self.size-1)/2))*2+1
                y = self._rand_int(0, int((self.size-1)/2))*2+1
                if (x > 1 or y > 1) and self.grid.get(x, y)==None: # can't populate agent start position
                    obj = Box
                    color = 'blue'
                    prob = self._rand_float(0,1) # change box to ball
                    if prob < self.box2ball:
                        obj = Ball
                        color = 'yellow'
                    self.put_obj(obj(color), x, y)

        # Place a goal square in the bottom-right corner
        self.put_obj(Goal(), width-2, height-2)

        # Place the agent
        if self.agent_start_pos is not None:
            self.agent_pos = self.agent_start_pos
            self.agent_dir = self.agent_start_dir
        else:
            self.place_agent()

        self.mission = "Reach green goal square"

    def _recursive_division(self, x, y, size, min, lvl):
        div = int((size-1)/2)

        # hoizontal wall
        # generate gap positions
        gap = self._rand_int(0, div+1)*2
        for i in range(size):
            if i%2==1:
                self.grid.set(x+i, y+div, Wall())
            else:
                if self.wall_prob > self._rand_float(0,1) and i!=gap:
                    self.grid.set(x+i, y+div, Wall())
                # add doors
                else:
                    if self.door_prob > self._rand_float(0,1):
                        self.grid.set(x+i, y+div, Door(color=self._rand_elem(COLOR_NAMES)))

        # vertical wall
        # generate gap positions
        if div > 2: 
            gap1 = self._rand_int(0, (div+1)/2)*2
            gap2 = self._rand_int(0, (div+1)/2)*2 + div + 1
        else:
            gap1 = 0
            gap2 = 2

        for i in range(size):
            if i%2==1:
                self.grid.set(x+div, y+i,  Wall())
            else:
                if self.wall_prob > self._rand_float(0,1) and i!=gap1 and i!=gap2:
                    self.grid.set(x+div, y+i,  Wall())
                # add doors
                else:
                    if self.door_prob > self._rand_float(0,1):
                        self.grid.set(x+div, y+i, Door(color=self._rand_elem(COLOR_NAMES)))

        '''
        # place keys
        if self.lock==True and size>3 and lvl!=0:
            color = COLOR_NAMES[(lvl-1)%6]
            kx = self._rand_int(0, div)*2
            ky = self._rand_int(0, div)*2
            while (kx==0 and ky==0) or self.grid.get(kx+x, ky+y)!=None:
                kx = self._rand_int(0, div)*2
                ky = self._rand_int(0, div)*2
                #print(self.grid.get(kx+x, ky+y)!=None)  

            if self.door_level == 2:
                self.put_obj(Key(color=color), kx+x, ky+y)
            else:
                self.put_obj(Box(color='red', contains=Key(color=color)), kx+x, ky+y)
                
                for i in range(3):
                    kx = self._rand_int(0, div)*2
                    ky = self._rand_int(0, div)*2
                    while (kx==0 and ky==0) or self.grid.get(kx+x, ky+y)!=None:
                        kx = self._rand_int(0, div)*2
                        ky = self._rand_int(0, div)*2
                        #print((kx==0 and ky==0) or self.grid.get(kx+x, ky+y)!=None)  
                        #print(self.grid.get(kx+x, ky+y))
                    self.put_obj(Box(color='red'), kx+x, ky+y)
            '''

        nlvl = lvl+1
        # recursion
        if size/2 > min:
            newSize = int((size-1)/2)
            self._recursive_division(x, y, newSize, min, nlvl)
            self._recursive_division(x+div+1, y, newSize, min, nlvl)
            self._recursive_division(x, y+div+1, newSize, min, nlvl)
            self._recursive_division(x+div+1, y+div+1, newSize, min, nlvl)
        elif self.limit != 1:
            newSize = int((size-1)/2)
            self._construct_room(x, y, newSize, lvl)
            self._construct_room(x+div+1, y, newSize, lvl)
            self._construct_room(x, y+div+1, newSize, lvl)
            self._construct_room(x+div+1, y+div+1, newSize, lvl)

    def _construct_room(self, x, y, size, lvl):
        div = int((size-1)/2)

        # Generate lava wall
        if self.lava_prob > self._rand_float(0,1):
            gap = self._rand_int(0, size)

            # randomize orientation
            dir = self._rand_bool()
            if dir == 0:
                for i in range(size):
                    if i != gap:
                        self.grid.set(x+i, y+div, Lava())
            else:
                for i in range(size):
                    if i != gap:
                        self.grid.set(x+div, y+i, Lava())  


# empty room
class EmptyEnv5x5(MazeEnv):
    def __init__(self, **kwargs):
        super().__init__(size=1, 
                         limit=3, 
                         lava_prob=0.2, 
                         **kwargs)

# simple maze
class MazeEnv9x9(MazeEnv):
    def __init__(self, **kwargs):
        super().__init__(size=2, 
                         lava_prob=0.2, 
                         **kwargs)

# medium maze with small rooms
class MazeEnv17x17EZ(MazeEnv):
    def __init__(self, **kwargs):
        super().__init__(size=3, 
                         limit=2, 
                         lava_prob=0.2, 
                         **kwargs)

# medium maze w/o rooms
class MazeEnv17x17(MazeEnv):
    def __init__(self, **kwargs):
        super().__init__(size=3,
                         door_prob=0.3, 
                         **kwargs)

# hard maze w/ small rooms
class MazeEnv33x33(MazeEnv):
    def __init__(self, **kwargs):
        super().__init__(size=4, 
                         **kwargs)

# large maze w/ large rooms
class MazeEnv65x65(MazeEnv):
    def __init__(self, **kwargs):
        super().__init__(size=5, 
                         lava_prob=0.1, 
                         obstacle_level=2.5,
                         box2ball=0.2,
                         door_prob=0.2,
                         wall_prob=0.9,
                         **kwargs)

register(
    id='MiniGrid-Maze-5x5-v1',
    entry_point='gym_minigrid.envs:EmptyEnv5x5'
)

register(
    id='MiniGrid-Maze-9x9-v1',
    entry_point='gym_minigrid.envs:MazeEnv9x9'
)

register(
    id='MiniGrid-Maze-17x17-v1',
    entry_point='gym_minigrid.envs:MazeEnv17x17'
)

register(
    id='MiniGrid-Maze-17x17-v2',
    entry_point='gym_minigrid.envs:MazeEnv17x17EZ'
)

register(
    id='MiniGrid-Maze-33x33-v1',
    entry_point='gym_minigrid.envs:MazeEnv33x33'
)

register(
    id='MiniGrid-Maze-65x65-v1',
    entry_point='gym_minigrid.envs:MazeEnv65x65'
)