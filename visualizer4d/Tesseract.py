import math as m
import numpy
from Graph import Graph
from FourShape import FourShape

class Tesseract(FourShape):

    cell_labels = ["-w", "+w", "-z", "-y", "+x", "+y", "-x", "+z"]
    cell_colors = {
        0: (150, 150, 0),
        1: (255, 255, 100),
        2: (0, 0, 150),
        3: (0, 150, 0),
        4: (255, 100, 100),
        5: (100, 255, 100),
        6: (150, 0, 0),
        7: (100, 100, 255),
    }

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)
        self.v = [    (-size + ox, -size + oy, -size + oz, -size + ow),
                    (size + ox, -size + oy, -size + oz, -size + ow),
                    (size + ox, size + oy, -size + oz, -size + ow),
                    (-size + ox, size + oy, -size + oz, -size + ow),
                    (-size + ox, -size + oy, size + oz, -size + ow),
                    (size + ox, -size + oy, size + oz, -size + ow),
                    (size + ox, size + oy, size + oz, -size + ow),
                    (-size + ox, size + oy, size + oz, -size + ow),
                    (-size + ox, -size + oy, -size + oz, size + ow),
                    (size + ox, -size + oy, -size + oz, size + ow),
                    (size + ox, size + oy, -size + oz, size + ow),
                    (-size + ox, size + oy, -size + oz, size + ow),
                    (-size + ox, -size + oy, size + oz, size + ow),
                    (size + ox, -size + oy, size + oz, size + ow),
                    (size + ox, size + oy, size + oz, size + ow),
                    (-size + ox, size + oy, size + oz, size + ow)]    
    
        self.edges.add_link((0, 1)) ##0
        self.edges.add_link((1, 2)) ##1
        self.edges.add_link((2, 3)) ##2
        self.edges.add_link((3, 0))
        self.edges.add_link((4, 5))
        self.edges.add_link((5, 6))
        self.edges.add_link((6, 7))
        self.edges.add_link((7, 4)) 
        self.edges.add_link((0, 4))
        self.edges.add_link((1, 5))
        self.edges.add_link((2, 6))
        self.edges.add_link((3, 7))

        self.edges.add_link((8, 9))
        self.edges.add_link((9, 10))
        self.edges.add_link((10, 11))
        self.edges.add_link((11, 8))
        self.edges.add_link((12, 13))
        self.edges.add_link((13, 14))
        self.edges.add_link((14, 15))
        self.edges.add_link((15, 12))
        self.edges.add_link((8, 12))
        self.edges.add_link((9, 13))
        self.edges.add_link((10, 14))
        self.edges.add_link((11, 15))
        
        self.edges.add_link((0, 8))
        self.edges.add_link((1, 9))
        self.edges.add_link((2, 10))
        self.edges.add_link((3, 11))
        self.edges.add_link((4, 12))
        self.edges.add_link((5, 13))
        self.edges.add_link((6, 14))
        self.edges.add_link((7, 15))

        self.faces.add_link((0, 1, 2, 3))
        self.faces.add_link((0, 4, 8, 9))
        self.faces.add_link((1, 5, 9, 10))
        self.faces.add_link((2, 6, 10, 11))
        self.faces.add_link((3, 7, 11, 8))
        self.faces.add_link((4, 5, 6, 7))

        self.faces.add_link((12, 13, 14, 15))
        self.faces.add_link((12, 16, 20, 21))
        self.faces.add_link((13, 17, 21, 22))
        self.faces.add_link((14, 18, 22, 23))
        self.faces.add_link((15, 19, 23, 20))
        self.faces.add_link((16, 17, 18, 19))

        self.faces.add_link((0, 24, 25, 12))
        self.faces.add_link((1, 13, 25, 26))
        self.faces.add_link((2, 26, 27, 14))
        self.faces.add_link((3, 24, 15, 27))
        self.faces.add_link((8, 28, 20, 24))
        self.faces.add_link((9, 29, 21, 25))
        self.faces.add_link((10, 30, 22, 26))
        self.faces.add_link((11, 31, 23, 27))
        self.faces.add_link((4, 29, 28, 16))
        self.faces.add_link((5, 29, 30, 17))
        self.faces.add_link((6, 30, 31, 18))
        self.faces.add_link((7, 31, 28, 19))

        self.cells.add_link((0, 1, 2, 3, 4, 5))       ## 0  -w
        self.cells.add_link((6, 7, 8, 9, 10, 11))      ## 1  +w
        self.cells.add_link((0, 6, 12, 13, 14, 15))    ## 2  -z
        self.cells.add_link((1, 7, 12, 16, 17, 20))    ## 3  -y
        self.cells.add_link((2, 8, 13, 17, 18, 21))    ## 4  +x
        self.cells.add_link((3, 9, 14, 18, 19, 22))    ## 5  +y
        self.cells.add_link((4, 10, 15, 19, 16, 23))   ## 6  -x
        self.cells.add_link((5, 20, 21, 22, 23, 11))   ## 7  +z

        for p in self.v:
            self.rv.append(p)
