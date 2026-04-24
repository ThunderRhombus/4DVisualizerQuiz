import math as m
from Graph import Graph
from FourShape import FourShape

class SixteenCell(FourShape):
    """
    The 16-cell (hexadecachoron).
    The 4D cross-polytope — dual of the tesseract.
    8 vertices (±1 on each axis), 24 edges, 32 triangular faces, 16 tetrahedral cells.
    Every vertex connects to every other vertex EXCEPT its antipode.

    Cells are named by the octant they point into (+/- xyz combination),
    since each tetrahedral cell occupies one of the 16 hyperoctants.
    """

    cell_labels = [
        "+++", "++-", "+-+", "+--",
        "-++", "-+-", "--+", "---",
        "w+++", "w++-", "w+-+", "w+--",
        "w-++", "w-+-", "w--+", "w---",
    ]
    cell_colors = {
        0:  (255,  80,  80),
        1:  ( 80, 255,  80),
        2:  ( 80,  80, 255),
        3:  (255, 255,  80),
        4:  (255,  80, 255),
        5:  ( 80, 255, 255),
        6:  (200, 120,  80),
        7:  ( 80, 200, 120),
        8:  (120,  80, 200),
        9:  (200, 200,  80),
        10: ( 80, 200, 200),
        11: (200,  80, 200),
        12: (160, 160,  80),
        13: ( 80, 160, 160),
        14: (160,  80, 160),
        15: (200, 200, 200),
    }

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)

        s = size
        # 8 vertices: one positive and one negative on each of the 4 axes
        self.v = [
            ( s+ox,    oy,    oz,    ow),   # 0  +x
            (-s+ox,    oy,    oz,    ow),   # 1  -x
            (   ox,  s+oy,    oz,    ow),   # 2  +y
            (   ox, -s+oy,    oz,    ow),   # 3  -y
            (   ox,    oy,  s+oz,    ow),   # 4  +z
            (   ox,    oy, -s+oz,    ow),   # 5  -z
            (   ox,    oy,    oz,  s+ow),   # 6  +w
            (   ox,    oy,    oz, -s+ow),   # 7  -w
        ]

        # Antipodal pairs: (0,1), (2,3), (4,5), (6,7)
        antipodes = {0:1, 1:0, 2:3, 3:2, 4:5, 5:4, 6:7, 7:6}
        edge_set = []
        edge_idx = {}
        for i in range(8):
            for j in range(i+1, 8):
                if antipodes[i] != j:
                    edge_idx[(i,j)] = len(edge_set)
                    edge_set.append((i,j))
                    self.edges.add_link((i, j))

        # 32 triangular faces — every triangle whose 3 vertices are mutually non-antipodal
        face_set = []
        face_idx = {}
        for i in range(8):
            for j in range(i+1, 8):
                if antipodes[i] == j: continue
                for k in range(j+1, 8):
                    if antipodes[i] == k: continue
                    if antipodes[j] == k: continue
                    t = (i, j, k)
                    face_idx[t] = len(face_set)
                    face_set.append(t)
                    def ei(a, b): return edge_idx[(min(a,b), max(a,b))]
                    self.faces.add_link((ei(i,j), ei(i,k), ei(j,k)))

        # 16 tetrahedral cells — every set of 4 mutually non-antipodal vertices
        def fi(a, b, c): return face_idx[tuple(sorted([a, b, c]))]

        for i in range(8):
            for j in range(i+1, 8):
                if antipodes[i]==j: continue
                for k in range(j+1, 8):
                    if antipodes[i]==k: continue
                    if antipodes[j]==k: continue
                    for l in range(k+1, 8):
                        if antipodes[i]==l: continue
                        if antipodes[j]==l: continue
                        if antipodes[k]==l: continue
                        self.cells.add_link((
                            fi(i,j,k),
                            fi(i,j,l),
                            fi(i,k,l),
                            fi(j,k,l),
                        ))

        for p in self.v:
            self.rv.append(p)
