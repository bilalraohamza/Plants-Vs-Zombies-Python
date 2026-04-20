__author__ = 'Rao Hamza Bilal'

import random
from ..core import constants as c

class Map():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [[0 for x in range(self.width)] for y in range(self.height)]

    def is_valid(self, map_x, map_y):
        if (map_x < 0 or map_x >= self.width or
            map_y < 0 or map_y >= self.height):
            return False
        return True
    
    def is_movable(self, map_x, map_y):
        return (self.map[map_y][map_x] == c.MAP_EMPTY)
    
    def get_map_index(self, x, y):
        x -= c.MAP_OFFSET_X
        y -= c.MAP_OFFSET_Y
        return (x // c.GRID_X_SIZE, y // c.GRID_Y_SIZE)
    
    def get_map_grid_pos(self, map_x, map_y):
        return (map_x * c.GRID_X_SIZE + c.GRID_X_SIZE//2 + c.MAP_OFFSET_X,
                map_y * c.GRID_Y_SIZE + c.GRID_Y_SIZE//5 * 3 + c.MAP_OFFSET_Y)
    
    def set_map_grid_type(self, map_x, map_y, type):
        self.map[map_y][map_x] = type

    def get_random_map_index(self):
        map_x = random.randint(0, self.width-1)
        map_y = random.randint(0, self.height-1)
        return (map_x, map_y)

    def show_plant(self, x, y):
        pos = None
        map_x, map_y = self.get_map_index(x, y)
        if self.is_valid(map_x, map_y) and self.is_movable(map_x, map_y):
            pos = self.get_map_grid_pos(map_x, map_y)
        return pos

