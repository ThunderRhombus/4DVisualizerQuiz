import math as m
from Graph import Graph
from FourShape import FourShape

class TriPrism(FourShape):
    """
    A 4D shape: triangular prism suspended along W axis.
    6 prism vertices + 2 W-apices = 8 vertices.
    10 cells: 4 triangular caps + 6 rectangular wall cells.

    Prism layout:
      Top ring (Z+): v0 +X,  v1 -X+Y,  v2 -X-Y   (triangle in XY at Z=+hz)
      Bot ring (Z-): v3 +X,  v4 -X+Y,  v5 -X-Y   (same triangle at Z=-hz)
      +W apex: v6    -W apex: v7

    Cells:
      Triangle caps: each triangular face (top or bottom ring) × each W-apex.
        "+W +Z" = +W apex over the top (+Z) triangle
        "+W -Z" = +W apex over the bottom (-Z) triangle
        "-W +Z", "-W -Z" — same for -W side
      Rectangular walls: each of the 3 side rectangles × each W-apex.
        Wall names use the outward XY direction of that wall's midpoint:
          rect (v0,v1,v4,v3): midpoint at (0.25, +0.43) ≈ "+Y wall"  → "+W +Y"
          rect (v1,v2,v5,v4): midpoint at (-0.5, 0)     → "-X wall"  → "+W -X"
          rect (v2,v0,v3,v5): midpoint at (0.25,-0.43)  → "-Y wall"  → "+W -Y"
    """

    cell_labels = [
        "+W +Z", "+W -Z",
        "-W +Z", "-W -Z",
        "+W +Y", "+W -X", "+W -Y",
        "-W +Y", "-W -X", "-W -Y",
    ]
    cell_colors = {
        0: (255, 220,  80),   1: (255, 180,  80),
        2: ( 80, 160, 255),   3: (100, 140, 255),
        4: (255, 100, 100),   5: (100, 255, 120),
        6: (200,  80, 255),   7: (200,  60,  60),
        8: ( 60, 200,  60),   9: (120,  60, 200),
    }

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)

        s  = size
        w4 = s * 1.3
        hz = s * 0.8
        r  = s * 1.2   # triangle circumradius

        # Triangle verts: v0=+X, v1=-X+Y (120°), v2=-X-Y (240°)
        tri_xy = [
            ( r,              0           ),
            (-r * 0.5,  r * 0.866),
            (-r * 0.5, -r * 0.866),
        ]
        self.v = []
        for tx, ty in tri_xy:
            self.v.append((tx+ox, ty+oy,  hz+oz, ow))   # top ring  0-2
        for tx, ty in tri_xy:
            self.v.append((tx+ox, ty+oy, -hz+oz, ow))   # bot ring  3-5
        self.v.append((ox, oy, oz,  w4+ow))              # 6  +W apex
        self.v.append((ox, oy, oz, -w4+ow))              # 7  -W apex

        prism_edges = [
            (0,1),(1,2),(2,0),
            (3,4),(4,5),(5,3),
            (0,3),(1,4),(2,5),
        ]
        susp_edges = [(i,6) for i in range(6)] + [(i,7) for i in range(6)]

        edge_idx = {}
        for a, b in prism_edges + susp_edges:
            k = (min(a,b), max(a,b))
            if k not in edge_idx:
                edge_idx[k] = len(edge_idx)
                self.edges.add_link((k[0], k[1]))

        def ei(a, b):
            k = (min(a,b), max(a,b))
            if k not in edge_idx:
                edge_idx[k] = len(edge_idx)
                self.edges.add_link(k)
            return edge_idx[k]

        face_idx = {}
        def add_face(verts):
            k = tuple(sorted(verts))
            if k not in face_idx:
                face_idx[k] = len(face_idx)
                edges = [ei(verts[i], verts[(i+1)%len(verts)]) for i in range(len(verts))]
                self.faces.add_link(tuple(edges))

        add_face((0, 1, 2)); add_face((3, 4, 5))                 # tri caps
        add_face((0, 1, 4, 3)); add_face((1, 2, 5, 4)); add_face((2, 0, 3, 5))  # walls
        for a, b in prism_edges:
            add_face((a, b, 6)); add_face((a, b, 7))

        def fi(*v):
            return face_idx[tuple(sorted(v))]

        # Cells 0-1: +W over top/bot triangles
        self.cells.add_link((fi(0,1,2), fi(0,1,6), fi(1,2,6), fi(2,0,6)))   # +W +Z
        self.cells.add_link((fi(3,4,5), fi(3,4,6), fi(4,5,6), fi(5,3,6)))   # +W -Z
        # Cells 2-3: -W over top/bot triangles
        self.cells.add_link((fi(0,1,2), fi(0,1,7), fi(1,2,7), fi(2,0,7)))   # -W +Z
        self.cells.add_link((fi(3,4,5), fi(3,4,7), fi(4,5,7), fi(5,3,7)))   # -W -Z

        # Rectangular wall cells: +W walls then -W walls
        # Wall order matches label order: +Y wall (0,1,4,3), -X wall (1,2,5,4), -Y wall (2,0,3,5)
        walls = [(0,1,4,3), (1,2,5,4), (2,0,3,5)]
        for w_v in walls:
            e_pairs = [(w_v[i], w_v[(i+1)%4]) for i in range(4)]
            self.cells.add_link([fi(*w_v)] + [fi(a,b,6) for a,b in e_pairs])   # +W
        for w_v in walls:
            e_pairs = [(w_v[i], w_v[(i+1)%4]) for i in range(4)]
            self.cells.add_link([fi(*w_v)] + [fi(a,b,7) for a,b in e_pairs])   # -W

        for p in self.v:
            self.rv.append(p)