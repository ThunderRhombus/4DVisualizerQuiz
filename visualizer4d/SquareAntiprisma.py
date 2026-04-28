import math as m
from Graph import Graph
from FourShape import FourShape

class SquareAntiprisma(FourShape):
    """
    A 4D shape: square antiprism suspended along the W axis.
    8 antiprism vertices + 2 W-apices = 10 vertices.
    20 cells: 4 square-pyramid caps + 16 band tetrahedra (8 per W-side).

    Top ring (Z+, axis-aligned): v0=+X, v1=+Y, v2=-X, v3=-Y   (0°/90°/180°/270°)
    Bot ring (Z-, rotated 45°):  v4=+X+Y, v5=-X+Y, v6=-X-Y, v7=+X-Y
    +W apex: v8    -W apex: v9

    Cap cells: square pyramid from top or bottom square to a W-apex.
      "+W +Z" = +W apex over the top (+Z) square  (axis-aligned square)
      "+W -Z" = +W apex over the bottom (-Z) square (45°-rotated square)
      "-W +Z", "-W -Z" similarly.

    Band tetrahedra: 8 triangular faces in the antiprism band, each coned to
    a W-apex.  Labelled by the XY centroid direction of that triangle:
      k=0 tri1 (v0,v1,v4)   → centroid ~+X+Y  → "+X+Y"
      k=0 tri2 (v1,v5,v4)   → centroid ~ +Y   → "+Y"
      k=1 tri1 (v1,v2,v5)   → centroid ~-X+Y  → "-X+Y"
      k=1 tri2 (v2,v6,v5)   → centroid ~ -X   → "-X"
      k=2 tri1 (v2,v3,v6)   → centroid ~-X-Y  → "-X-Y"
      k=2 tri2 (v3,v7,v6)   → centroid ~ -Y   → "-Y"
      k=3 tri1 (v3,v0,v7)   → centroid ~+X-Y  → "+X-Y"
      k=3 tri2 (v0,v4,v7)   → centroid ~ +X   → "+X"
    """

    _band_xy = ["+X+Y", "+Y", "-X+Y", "-X", "-X-Y", "-Y", "+X-Y", "+X"]

    cell_labels = (
        ["+W +Z", "+W -Z", "-W +Z", "-W -Z"] +
        [f"+W {d}" for d in _band_xy] +
        [f"-W {d}" for d in _band_xy]
    )
    cell_colors = {
        0: (255, 220,  80),   1: (255, 180,  80),
        2: ( 80, 160, 255),   3: (100, 140, 255),
    }
    for _i in range(4, 12):
        cell_colors[_i] = (255, 120 + (_i-4)*15, 80)
    for _i in range(12, 20):
        cell_colors[_i] = (80, 220, 200 - (_i-12)*15)

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)

        s   = size
        r   = s * 1.15
        hz  = s * 0.7
        w4  = s * 1.3
        rot = m.pi / 4

        self.v = []
        for k in range(4):                                   # top ring: 0°/90°/180°/270°
            ang = k * m.pi / 2
            self.v.append((r*m.cos(ang)+ox, r*m.sin(ang)+oy,  hz+oz, ow))
        for k in range(4):                                   # bot ring: 45°/135°/225°/315°
            ang = k * m.pi / 2 + rot
            self.v.append((r*m.cos(ang)+ox, r*m.sin(ang)+oy, -hz+oz, ow))
        self.v.append((ox, oy, oz,  w4+ow))                 # 8  +W apex
        self.v.append((ox, oy, oz, -w4+ow))                 # 9  -W apex

        edge_idx = {}

        def add_edge(a, b):
            k = (min(a,b), max(a,b))
            if k not in edge_idx:
                edge_idx[k] = len(edge_idx)
                self.edges.add_link(k)

        for k in range(4): add_edge(k, (k+1) % 4)           # top square
        for k in range(4): add_edge(4+k, 4 + (k+1) % 4)    # bot square
        for k in range(4):                                    # band
            add_edge(k, 4+k)
            add_edge(k, 4 + (k-1) % 4)
        for i in range(8):                                    # suspension
            add_edge(i, 8); add_edge(i, 9)

        def ei(a, b):
            k = (min(a,b), max(a,b))
            if k not in edge_idx:
                edge_idx[k] = len(edge_idx)
                self.edges.add_link(k)
            return edge_idx[k]

        face_idx = {}

        def add_face(*v):
            k = tuple(sorted(v))
            if k not in face_idx:
                face_idx[k] = len(face_idx)
                edges = [ei(v[i], v[(i+1)%len(v)]) for i in range(len(v))]
                self.faces.add_link(tuple(edges))

        add_face(0, 1, 2, 3)   # top square
        add_face(4, 5, 6, 7)   # bot square

        band_tris = []
        for k in range(4):
            t1 = (k, (k+1)%4, 4+k)
            t2 = ((k+1)%4, 4+(k+1)%4, 4+k)
            band_tris.append(t1); band_tris.append(t2)
        for tri in band_tris:
            add_face(*tri)

        for i in range(8):
            for j in range(i+1, 8):
                if (min(i,j), max(i,j)) in edge_idx:
                    add_face(i, j, 8)
                    add_face(i, j, 9)

        def fi(*v):
            return face_idx[tuple(sorted(v))]

        # Cells 0-3: cap pyramids
        self.cells.add_link([fi(0,1,8), fi(1,2,8), fi(2,3,8), fi(3,0,8), fi(0,1,2,3)])  # +W +Z
        self.cells.add_link([fi(4,5,8), fi(5,6,8), fi(6,7,8), fi(7,4,8), fi(4,5,6,7)])  # +W -Z
        self.cells.add_link([fi(0,1,9), fi(1,2,9), fi(2,3,9), fi(3,0,9), fi(0,1,2,3)])  # -W +Z
        self.cells.add_link([fi(4,5,9), fi(5,6,9), fi(6,7,9), fi(7,4,9), fi(4,5,6,7)])  # -W -Z

        # Cells 4-11: +W band tetrahedra (order matches _band_xy)
        for a, b, c in band_tris:
            self.cells.add_link((fi(a,b,c), fi(a,b,8), fi(b,c,8), fi(a,c,8)))
        # Cells 12-19: -W band tetrahedra
        for a, b, c in band_tris:
            self.cells.add_link((fi(a,b,c), fi(a,b,9), fi(b,c,9), fi(a,c,9)))

        for p in self.v:
            self.rv.append(p)