import math as m
from Graph import Graph
from FourShape import FourShape

class Cube(FourShape):
    def __init__(self, size, ortho, ox, oy, oz):
        super().__init__(size, ortho)
        self.v = [    (-size + ox, -size + oy, -size + oz),
                    (size + ox, -size + oy, -size + oz),
                    (size + ox, size + oy, -size + oz),
                    (-size + ox, size + oy, -size + oz),
                    (-size + ox, -size + oy, size + oz),
                    (size + ox, -size + oy, size + oz),
                    (size + ox, size + oy, size + oz),
                    (-size + ox, size + oy, size + oz)]    
    
        self.edges.add_link((0, 1))
        self.edges.add_link((1, 2))
        self.edges.add_link((2, 3))
        self.edges.add_link((3, 0))
        self.edges.add_link((4, 5))
        self.edges.add_link((5, 6))
        self.edges.add_link((6, 7))
        self.edges.add_link((7, 4))
        self.edges.add_link((0, 4))
        self.edges.add_link((1, 5))
        self.edges.add_link((2, 6))
        self.edges.add_link((3, 7))
        
        self.faces.add_link((0, 1, 2, 3))
        self.faces.add_link((0, 4, 8, 9))
        self.faces.add_link((1, 5, 9, 10))
        self.faces.add_link((2, 6, 10, 11))
        self.faces.add_link((3, 7, 11, 8))
        self.faces.add_link((4, 5, 6, 7))

        for p in self.v:
            self.rv.append(p)


        
        
        
