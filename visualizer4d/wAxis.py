import math as m
import numpy
from Graph import Graph
from FourShape import FourShape

class wAxis(FourShape):
    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)
        self.v = [(ox,oy,oz,ow),(size + ox,oy,oz,ow),(ox,size + oy,oz,ow),(ox,oy,size + oz,ow),(ox,oy,oz,size + ow)]
        self.hastext = True    
        self.text = [("O"),("x"),("y"),("z"),("w")]
    
        self.edges.add_link((0, 1))
        self.edges.add_link((0, 2))
        self.edges.add_link((0, 3))
        self.edges.add_link((0, 4))

        for p in self.v:
            self.rv.append(p)


        
        
        

