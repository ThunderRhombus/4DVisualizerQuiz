import math as m
from Graph import Graph
from FourShape import FourShape

class ThreeAxis(FourShape):
    def __init__(self, size, ortho, ox, oy, oz):
        # We still inherit from FourShape to maintain compatibility with the 4D renderers
        # but we only define X, Y, and Z vertices.
        super().__init__(size, ortho)
        # O, X, Y, Z (W is hardcoded to 0)
        self.v = [
            (ox, oy, oz, 0),
            (size + ox, oy, oz, 0),
            (ox, size + oy, oz, 0),
            (ox, oy, size + oz, 0)
        ]
        self.hastext = True    
        self.text = [None, "x", "y", "z"]
    
        self.edges.add_link((0, 1)) # X axis
        self.edges.add_link((0, 2)) # Y axis
        self.edges.add_link((0, 3)) # Z axis

        for p in self.v:
            self.rv.append(p)
            self.ov.append(p)

    def rotate(self, yaw, pitch, roll, dip, tuck, skew):
        # Overriding rotate to IGNORE dip, tuck, skew (the 4D rotation)
        # This keeps the axis invariant to 4D morphing
        super().rotate(yaw, pitch, roll, 0, 0, 0)

    def getText(self, p):
        if p < len(self.text):
            return self.text[p]
        return None
