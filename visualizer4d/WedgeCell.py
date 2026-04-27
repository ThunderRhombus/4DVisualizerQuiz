import math as m
from Graph import Graph
from FourShape import FourShape

class WedgeCell(FourShape):
    """
    A 4D shape: triangular bipyramid (two tetrahedra sharing a triangle)
    suspended along W with two apex vertices at +W and -W.
    5 body vertices + 2 W-apices = 7 vertices.
    7 cells: upper wedge × 2 W-sides, lower wedge × 2 W-sides,
             plus 3 equatorial belt cells (one per equatorial edge).
    """

    cell_labels = [
        "+W Top Front", "+W Top Left", "+W Top Right",
        "+W Bot Front", "+W Bot Left", "+W Bot Right",
        "-W Top Front", "-W Top Left", "-W Top Right",
        "-W Bot Front", "-W Bot Left", "-W Bot Right",
    ]
    cell_colors = {
        0: (255,  80,  80),
        1: (255, 100,  80),
        2: (255, 120,  80),
        3: (255, 160,  60),
        4: (255, 180,  60),
        5: (255, 200,  60),
        6: ( 80, 140, 255),
        7: ( 90, 160, 255),
        8: (100, 180, 255),
        9: ( 80, 220, 200),
        10: (90, 230, 210),
        11: (100, 240, 220),
    }

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)

        s  = size
        r  = s * 0.85
        zt = s * 0.9
        zb = -s * 0.9
        w4 = s * 1.0

        self.v = []
        for k in range(3):
            ang = k * 2 * m.pi / 3
            self.v.append((r*m.cos(ang)+ox, r*m.sin(ang)+oy, oz, ow))
        self.v.append((ox, oy, zt+oz, ow))    # 3  upper Z apex
        self.v.append((ox, oy, zb+oz, ow))    # 4  lower Z apex
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
        add_edge(5, 6) # Connect the two W apices

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
            # Faces spanning W apices
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

        # Cells: Pyramids from each of the 6 faces of the triangular bipyramid to W-apices
        # Base Faces: (0,1,3), (1,2,3), (2,0,3) - upper
        #             (0,1,4), (1,2,4), (2,0,4) - lower
        
        # Cells 0-2: +W Upper
        for k in range(3):
            a, b = k, (k+1)%3
            self.cells.add_link((fi(a,b,3), fi(a,b,5), fi(a,3,5), fi(b,3,5)))
        # Cells 3-5: +W Lower
        for k in range(3):
            a, b = k, (k+1)%3
            self.cells.add_link((fi(a,b,4), fi(a,b,5), fi(a,4,5), fi(b,4,5)))
        # Cells 6-8: -W Upper
        for k in range(3):
            a, b = k, (k+1)%3
            self.cells.add_link((fi(a,b,3), fi(a,b,6), fi(a,3,6), fi(b,3,6)))
        # Cells 9-11: -W Lower
        for k in range(3):
            a, b = k, (k+1)%3
            self.cells.add_link((fi(a,b,4), fi(a,b,6), fi(a,4,6), fi(b,4,6)))

        for p in self.v:
            self.rv.append(p)