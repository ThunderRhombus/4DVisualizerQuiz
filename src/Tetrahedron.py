import math as m
import numpy
from Graph import Graph
from ThreeShape import ThreeShape

class Tetrahedron(ThreeShape):
    def __init__(self, size, ox, oy, oz):
        super().__init__(size)
        root = m.sqrt(3)
        self.v = [    (size, -size*root/3, -size*root/3),
                    (-size,-size*root/3,-size*root/3),
                    (0,size*root*2/3,-size*root/3),
                    (0,0,size*root*2/3)]    
    
        self.edges.add_link((0, 1))
        self.edges.add_link((1, 2))
        self.edges.add_link((2, 0))
        self.edges.add_link((0,3))
        self.edges.add_link((1,3))
        self.edges.add_link((2,3))
        
        self.faces.add_link((0, 1, 2))
        self.faces.add_link((0, 3, 4))
        self.faces.add_link((1, 4, 5))
        self.faces.add_link((2, 3, 5))
        

        for p in self.v:
            self.rv.append(p)


        
        
        

