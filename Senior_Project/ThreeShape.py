import math as m
import numpy
from Graph import Graph

class ThreeShape:
    def __init__(self, size):
        self.size = size
        self.v = [list()]    
        self.edges = Graph()
        self.faces = Graph()

        self.rv = []
    
    def rotate(self, yaw, pitch, roll):
        yaw = m.radians(yaw)
        pitch = m.radians(pitch)
        roll = m.radians(roll)

        # Given User Definitions:
        # X = Heading (Depth into screen)
        # Z = Top (Upwards)
        # Pitch -> rotates around Y axis (in Z-X plane)
        # Yaw   -> rotates around Z axis (in X-Y plane)
        # Roll  -> rotates around X axis (in Z-Y plane)

        cp, sp = m.cos(pitch), m.sin(pitch)
        cy, sy = m.cos(yaw), m.sin(yaw)
        cr, sr = m.cos(roll), m.sin(roll)

        Rx = numpy.array([
            [1, 0, 0],
            [0, cr, -sr],
            [0, sr, cr]
        ])
        Ry = numpy.array([
            [cp, 0, sp],
            [0, 1, 0],
            [-sp, 0, cp]
        ])
        Rz = numpy.array([
            [cy, -sy, 0],
            [sy, cy, 0],
            [0, 0, 1]
        ])
        
        A = Rz @ Ry @ Rx
        self.rv = []
        for p in self.v:
            self.rv.append(numpy.dot(A, p))
    
    def get_hind_most(self):
        h = 0
        for i in range(1, len(self.rv)):
            if(self.rv[i][2] < self.rv[h][2]):
                h = i
        return h

    def get_next_targets(self, vfrom, vat):
        next_targets = []
        for vto in self.g.neighbors(vat):
            if(vto != vfrom):
                next_targets.append(vto)
        return next_targets
    
    


        
        
        

