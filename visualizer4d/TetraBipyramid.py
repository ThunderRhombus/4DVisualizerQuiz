import math as m
import numpy
from Graph import Graph
from FourShape import FourShape

class TetraBipyramid(FourShape):
    """
    A 4D bipyramid over a tetrahedron.
    4 equatorial (tet) vertices + 2 W-apices = 6 vertices.
    8 tetrahedral cells: each of the 4 tet faces extended to +W or -W apex.
    """

    # Ordered: +W cells first (top cap), then -W cells (bottom cap)
    # Each cell named by the tetrahedron face it wraps (three vertices of base tet)
    cell_labels = [
        "+W | face 1", "+W | face 2", "+W | face 3", "+W | face 4",
        "-W | face 1", "-W | face 2", "-W | face 3", "-W | face 4",
    ]
    cell_colors = {
        0: (255,  80,  80),    # +W cap cells — warm reds/oranges
        1: (255, 140,  60),
        2: (255, 200,  80),
        3: (220, 255,  80),
        4: ( 80, 160, 255),    # -W cap cells — cool blues
        5: ( 80, 100, 220),
        6: (120,  80, 255),
        7: (180,  80, 220),
    }

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)

        s  = size
        w4 = s * 1.1

        raw_tet = [
            ( 1,  1,  1),
            ( 1, -1, -1),
            (-1,  1, -1),
            (-1, -1,  1),
        ]
        edge_len = m.sqrt(sum((raw_tet[0][k] - raw_tet[1][k])**2 for k in range(3)))
        scale = (2 * s) / edge_len

        self.v = [
            (scale*p[0]+ox, scale*p[1]+oy, scale*p[2]+oz, ow)
            for p in raw_tet
        ]
        self.v.append((ox, oy, oz,  w4+ow))   # 4  +W apex
        self.v.append((ox, oy, oz, -w4+ow))   # 5  -W apex

        edge_idx = {}

        def add_edge(a, b):
            k = (min(a,b), max(a,b))
            if k not in edge_idx:
                edge_idx[k] = len(edge_idx)
                self.edges.add_link(k)

        for i in range(4):
            for j in range(i+1, 4):
                add_edge(i, j)
        for i in range(4):
            add_edge(i, 4)
            add_edge(i, 5)

        def ei(a, b):
            return edge_idx[(min(a,b), max(a,b))]

        face_idx = {}

        def add_face(a, b, c):
            k = tuple(sorted([a, b, c]))
            if k not in face_idx:
                face_idx[k] = len(face_idx)
                i, j, l = k
                self.faces.add_link((ei(i,j), ei(i,l), ei(j,l)))

        tet_faces = [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]
        for f in tet_faces:
            add_face(*f)
        for a, b, c in tet_faces:
            add_face(a, b, 4); add_face(a, c, 4); add_face(b, c, 4)
            add_face(a, b, 5); add_face(a, c, 5); add_face(b, c, 5)

        def fi(a, b, c):
            return face_idx[tuple(sorted([a, b, c]))]

        # +W cells first (cells 0-3), then -W cells (cells 4-7)
        for a, b, c in tet_faces:
            self.cells.add_link((fi(a,b,c), fi(a,b,4), fi(a,c,4), fi(b,c,4)))
        for a, b, c in tet_faces:
            self.cells.add_link((fi(a,b,c), fi(a,b,5), fi(a,c,5), fi(b,c,5)))

        for p in self.v:
            self.rv.append(p)