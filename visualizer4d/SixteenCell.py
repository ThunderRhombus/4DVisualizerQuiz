import math as m
from Graph import Graph
from FourShape import FourShape

class SixteenCell(FourShape):
    """
    The 16-cell (hexadecachoron) — dual of the tesseract.
    8 vertices (±1 on each axis), 24 edges, 32 triangular faces, 16 tetrahedral cells.
    Each tetrahedral cell occupies one hyperoctant.
    Labels reflect the signs of the three non-W axes in that octant,
    grouped by W sign: +W cells first, then -W cells.
    """

    # 16 cells = 8 +W-side octants + 8 -W-side octants
    # Label format: (W sign)(X sign)(Y sign)(Z sign)
    cell_labels = [
        "+W+X+Y", "+W+X-Y", "+W-X+Y", "+W-X-Y",
        "+W+X+Z", "+W+X-Z", "+W-X+Z", "+W-X-Z",
        "-W+X+Y", "-W+X-Y", "-W-X+Y", "-W-X-Y",
        "-W+X+Z", "-W+X-Z", "-W-X+Z", "-W-X-Z",
    ]
    cell_colors = {
        0:  (255,  80,  80),
        1:  (255, 160,  80),
        2:  (200, 255,  80),
        3:  ( 80, 255,  80),
        4:  ( 80, 255, 200),
        5:  ( 80, 200, 255),
        6:  ( 80,  80, 255),
        7:  (160,  80, 255),
        8:  (200,  60,  60),
        9:  (200, 120,  60),
        10: (160, 200,  60),
        11: ( 60, 200,  60),
        12: ( 60, 200, 160),
        13: ( 60, 160, 200),
        14: ( 60,  60, 200),
        15: (120,  60, 200),
    }

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)

        s = size
        self.v = [
            ( s+ox,    oy,    oz,    ow),   # 0  +X
            (-s+ox,    oy,    oz,    ow),   # 1  -X
            (   ox,  s+oy,    oz,    ow),   # 2  +Y
            (   ox, -s+oy,    oz,    ow),   # 3  -Y
            (   ox,    oy,  s+oz,    ow),   # 4  +Z
            (   ox,    oy, -s+oz,    ow),   # 5  -Z
            (   ox,    oy,    oz,  s+ow),   # 6  +W
            (   ox,    oy,    oz, -s+ow),   # 7  -W
        ]

        antipodes = {0:1, 1:0, 2:3, 3:2, 4:5, 5:4, 6:7, 7:6}
        edge_set = []
        edge_idx = {}
        for i in range(8):
            for j in range(i+1, 8):
                if antipodes[i] != j:
                    edge_idx[(i,j)] = len(edge_set)
                    edge_set.append((i,j))
                    self.edges.add_link((i, j))

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