import math as m
from Graph import Graph
from FourShape import FourShape

class WedgeCell(FourShape):
    """
    A 4D shape: triangular bipyramid (two tetrahedra sharing a triangle)
    suspended along W with two apex vertices at +W and -W.
    5 body vertices + 2 W-apices = 7 vertices.
    12 cells: each of the 6 bipyramid faces coned to the +W or -W apex.

    Body vertices:
      v0  +X side  (angle 0°   in XY plane, Z=0)
      v1  -X+Y     (angle 120°)
      v2  -X-Y     (angle 240°)
      v3  +Z apex  (0, 0, +Z)
      v4  -Z apex  (0, 0, -Z)

    The 6 bipyramid faces each span two ring verts + one Z-apex.
    Face labels use the two ring verts' XY directions and the Z-apex sign:
      ring edge 01 → between +X and -X+Y  → XY side "+X/-X+Y"
      ring edge 12 → between -X+Y and -X-Y → XY side "-X+Y/-X-Y" = roughly "-X"
      ring edge 20 → between -X-Y and +X  → XY side "-X-Y/+X"
    Shortened to the dominant XY direction of the face centroid:
      face (v0,v1) → centroid at (+0.25, +0.43) ≈ "+Y side"   → "+Y"
      face (v1,v2) → centroid at (-0.5,  0)      → "-X side"  → "-X"
      face (v2,v0) → centroid at (+0.25,-0.43) ≈ "-Y side"   → "-Y"
    Combined with +Z/-Z apex and +W/-W:
      e.g. "+W +Z+Y" = +W cap, upper (+Z) bipyramid face on the +Y side
    """

    cell_labels = [
        "+W +Z+Y",  "+W +Z-X",  "+W +Z-Y",   # +W, upper (Z+) faces
        "+W -Z+Y",  "+W -Z-X",  "+W -Z-Y",   # +W, lower (Z-) faces
        "-W +Z+Y",  "-W +Z-X",  "-W +Z-Y",   # -W, upper
        "-W -Z+Y",  "-W -Z-X",  "-W -Z-Y",   # -W, lower
    ]
    cell_colors = {
        0: (255,  80,  80),   1: (255, 100,  80),   2: (255, 120,  80),
        3: (255, 160,  60),   4: (255, 180,  60),   5: (255, 200,  60),
        6: ( 80, 140, 255),   7: ( 90, 160, 255),   8: (100, 180, 255),
        9: ( 80, 220, 200),  10: ( 90, 230, 210),  11: (100, 240, 220),
    }

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)

        s  = size
        r  = s * 1.1
        zt = s * 1.1
        zb = -s * 1.1
        w4 = s * 1.2

        self.v = []
        for k in range(3):
            ang = k * 2 * m.pi / 3
            self.v.append((r*m.cos(ang)+ox, r*m.sin(ang)+oy, oz, ow))
        self.v.append((ox, oy, zt+oz, ow))    # 3  +Z apex
        self.v.append((ox, oy, zb+oz, ow))    # 4  -Z apex
        self.v.append((ox, oy, oz,  w4+ow))   # 5  +W apex
        self.v.append((ox, oy, oz, -w4+ow))   # 6  -W apex

        edge_idx = {}

        def add_edge(a, b):
            k = (min(a,b), max(a,b))
            if k not in edge_idx:
                edge_idx[k] = len(edge_idx)
                self.edges.add_link(k)

        for k in range(3):
            add_edge(k, (k+1) % 3)
        for k in range(3):
            add_edge(k, 3)
            add_edge(k, 4)
        for i in range(5):
            add_edge(i, 5)
            add_edge(i, 6)
        add_edge(5, 6)

        def ei(a, b):
            k = (min(a,b), max(a,b))
            if k not in edge_idx:
                edge_idx[k] = len(edge_idx)
                self.edges.add_link(k)
            return edge_idx[k]

        face_idx = {}

        def add_face(a, b, c):
            k = tuple(sorted([a, b, c]))
            if k not in face_idx:
                face_idx[k] = len(face_idx)
                i, j, l = k
                self.faces.add_link((ei(i,j), ei(i,l), ei(j,l)))

        add_face(0, 1, 2)
        for k in range(3):
            add_face(k, (k+1)%3, 3)
            add_face(k, (k+1)%3, 4)
            add_face(k, 5, 6)
        add_face(3, 5, 6); add_face(4, 5, 6)

        all_wedge_edges = ([(k,(k+1)%3) for k in range(3)] +
                           [(k,3) for k in range(3)] +
                           [(k,4) for k in range(3)])
        for a, b in all_wedge_edges:
            add_face(a, b, 5)
            add_face(a, b, 6)
        for k in range(3):
            add_face(k, 3, 5); add_face(k, 3, 6)
            add_face(k, 4, 5); add_face(k, 4, 6)

        def fi(a, b, c):
            return face_idx[tuple(sorted([a, b, c]))]

        # Face slot order per label: k=0 → edge(0,1)/+Y, k=1 → edge(1,2)/-X, k=2 → edge(2,0)/-Y
        # Cells 0-2: +W upper (+Z apex = v3)
        for k in range(3):
            a, b = k, (k+1)%3
            self.cells.add_link((fi(a,b,3), fi(a,b,5), fi(a,3,5), fi(b,3,5)))
        # Cells 3-5: +W lower (-Z apex = v4)
        for k in range(3):
            a, b = k, (k+1)%3
            self.cells.add_link((fi(a,b,4), fi(a,b,5), fi(a,4,5), fi(b,4,5)))
        # Cells 6-8: -W upper
        for k in range(3):
            a, b = k, (k+1)%3
            self.cells.add_link((fi(a,b,3), fi(a,b,6), fi(a,3,6), fi(b,3,6)))
        # Cells 9-11: -W lower
        for k in range(3):
            a, b = k, (k+1)%3
            self.cells.add_link((fi(a,b,4), fi(a,b,6), fi(a,4,6), fi(b,4,6)))

        for p in self.v:
            self.rv.append(p)