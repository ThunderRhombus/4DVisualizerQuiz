import math as m
import numpy
from Graph import Graph

class FourShape:
    def __init__(self, size, ortho):
        self.size = size
        self.v = [list()]    
        self.edges = Graph()
        self.faces = Graph()
        self.cells = Graph()
        self.o = ortho
        self.hastext = False
        self.text = []

        self.rv = []
        self.ov = []
    
    def rotate(self, yaw, pitch, roll, dip, tuck, skew):
        yaw = m.radians(yaw)
        pitch = m.radians(pitch)
        roll = m.radians(roll)
        dip = m.radians(dip)
        tuck = m.radians(tuck)
        skew = m.radians(skew)

        # Given User Definitions:
        # X = Heading (Depth into screen)
        # Z = Top (Upwards)
        # Pitch -> rotates around Y-W plane (in Z-X plane)
        # Yaw   -> rotates around Z-W plane (in X-Y plane)
        # Roll  -> rotates around X-W palane (in Z-Y plane)
        # Dip   -> rotates in the X-W plane
        # Tuck   -> rotates in the Z-W plane
        # Skew   -> rotates in the Y-W plane
        

        cp, sp = m.cos(pitch), m.sin(pitch)
        cy, sy = m.cos(yaw), m.sin(yaw)
        cr, sr = m.cos(roll), m.sin(roll)
        cd, sd = m.cos(dip), m.sin(dip)
        ct, st = m.cos(tuck), m.sin(tuck)
        cs, ss = m.cos(skew), m.sin(skew)

        # 3D Euler rotations embedded in 4D space (w unchanged)
        Rx = numpy.eye(4)
        Rx[1,1], Rx[1,2], Rx[2,1], Rx[2,2] = cr, -sr, sr, cr

        Ry = numpy.eye(4)
        Ry[0,0], Ry[0,2], Ry[2,0], Ry[2,2] = cp, sp, -sp, cp

        Rz = numpy.eye(4)
        Rz[0,0], Rz[0,1], Rz[1,0], Rz[1,1] = cy, -sy, sy, cy

        # 4D additional planes (X-W, Y-W, Z-W)
        R_xw = numpy.eye(4)
        R_xw[0,0], R_xw[0,3], R_xw[3,0], R_xw[3,3] = cd, -sd, sd, cd

        R_yw = numpy.eye(4)
        R_yw[1,1], R_yw[1,3], R_yw[3,1], R_yw[3,3] = cs, -ss, ss, cs

        R_zw = numpy.eye(4)
        R_zw[2,2], R_zw[2,3], R_zw[3,2], R_zw[3,3] = ct, -st, st, ct

        # Compose: apply 3D Euler first, then 4D warp rotations (order can be changed by use-case)
        A = Rx @ Ry @ Rz @ R_xw @ R_zw @ R_yw 

        self.rv = []
        for p in self.v:
            # allow 3D vector with implicit w=0
            x, y, z, w = p[0], p[1], p[2], p[3]
            p4 = numpy.array([x, y, z, w])
            self.rv.append(A @ p4)
        
        self.ov = []
        for p in self.rv:
            x, y, z, w = p[0], p[1], p[2], p[3]
            d = self.o*w
            x = x*(1+d)
            y = y*(1+d)
            z = z*(1+d)
            self.ov.append(numpy.array([x, y, z, w]))
    
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

    def shrink(self, ortho):
        self.o = ortho

    def getText(self, i):
        return self.text[i]
    
    


        
        
        

