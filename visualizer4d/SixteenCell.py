import math as m
from Graph import Graph
from FourShape import FourShape

class SixteenCell(FourShape):
    """
    The 16-cell (hexadecachoron) — dual of the tesseract.
    8 vertices at ±size on each axis, 24 edges, 32 triangular faces, 16 tetrahedral cells.

    Each cell occupies one of the 16 hyperoctants. A cell's label names
    the three non-W axes by their sign in that octant, prefixed by the W side.
    The fourth axis is always the W side given.  Example: "+W +X+Y+Z" is the
    cell in the octant where W>0, X>0, Y>0, Z>0.  These map directly to the
    four axes visible on the origin widget.
    """

    # Vertices: 0=+X 1=-X 2=+Y 3=-Y 4=+Z 5=-Z 6=+W 7=-W
    # antipodes: 0↔1, 2↔3, 4↔5, 6↔7
    # Each tetrahedral cell = 4 mutually non-antipodal vertices containing
    # exactly one from each antipodal pair.  The W-pair membership (+W=v6 / -W=v7)
    # gives the W label; the other three pairs give the XYZ signs.

    cell_labels = [
        # +W cells (contain v6=+W), 8 combos of ±X ±Y ±Z
        "+W+X+Y+Z", "+W+X+Y-Z", "+W+X-Y+Z", "+W+X-Y-Z",
        "+W-X+Y+Z", "+W-X+Y-Z", "+W-X-Y+Z", "+W-X-Y-Z",
        # -W cells (contain v7=-W)
        "-W+X+Y+Z", "-W+X+Y-Z", "-W+X-Y+Z", "-W+X-Y-Z",
        "-W-X+Y+Z", "-W-X+Y-Z", "-W-X-Y+Z", "-W-X-Y-Z",
    ]
    cell_colors = {
        0:  (255,  80,  80),  1:  (255, 140,  80),
        2:  (255, 200,  80),  3:  (200, 255,  80),
        4:  ( 80, 255, 120),  5:  ( 80, 255, 200),
        6:  ( 80, 180, 255),  7:  (140,  80, 255),
        8:  (200,  60,  60),  9:  (200, 120,  60),
        10: (180, 200,  60),  11: ( 60, 200,  60),
        12: ( 60, 200, 160),  13: ( 60, 140, 200),
        14: ( 60,  60, 200),  15: (120,  60, 200),
    }

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)

        s = size * 1.4   # boost so bounding sphere matches the Tesseract
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
        edge_idx = {}
        for i in range(8):
            for j in range(i+1, 8):
                if antipodes[i] != j:
                    edge_idx[(i,j)] = len(edge_idx)
                    self.edges.add_link((i, j))

        face_idx = {}
        def ei(a, b): return edge_idx[(min(a,b), max(a,b))]
        for i in range(8):
            for j in range(i+1, 8):
                if antipodes[i] == j: continue
                for k in range(j+1, 8):
                    if antipodes[i] == k or antipodes[j] == k: continue
                    t = (i, j, k)
                    face_idx[t] = len(face_idx)
                    self.faces.add_link((ei(i,j), ei(i,k), ei(j,k)))

        def fi(a, b, c): return face_idx[tuple(sorted([a, b, c]))]

        for i in range(8):
            for j in range(i+1, 8):
                if antipodes[i]==j: continue
                for k in range(j+1, 8):
                    if antipodes[i]==k or antipodes[j]==k: continue
                    for l in range(k+1, 8):
                        if antipodes[i]==l or antipodes[j]==l or antipodes[k]==l: continue
                        self.cells.add_link((
                            fi(i,j,k), fi(i,j,l), fi(i,k,l), fi(j,k,l),
                        ))

        for p in self.v:
            self.rv.append(p)