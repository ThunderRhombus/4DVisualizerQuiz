import math as m
import numpy
from Graph import Graph
from ThreeShape import ThreeShape

class Origin(ThreeShape):
    def __init__(self, size, ox, oy, oz):
        super().__init__(size)
        self.v = [(ox,oy,oz),
                  (size + ox, oy, oz),
                  (ox, size + oy, oz),
                  (ox, oy, size + oz)]    
    
        self.edges.add_link((0, 1))
        self.edges.add_link((0, 2))
        self.edges.add_link((0, 3))

        for p in self.v:
            self.rv.append(p)


        
        
        

