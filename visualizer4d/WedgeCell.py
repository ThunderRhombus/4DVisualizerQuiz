import math as m
import numpy
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

    # Ordered: +W-side cells first, then -W-side, then equatorial belt
    cell_labels = [
        "+W | upper", "+W | lower",
        "-W | upper", "-W | lower",
        "belt A", "belt B", "belt C",
    ]
    cell_colors = {
        0: (255,  80,  80),   # +W upper — red
        1: (255, 160,  60),   # +W lower — orange
        2: ( 80, 140, 255),   # -W upper — blue
        3: ( 80, 220, 200),   # -W lower — teal
        4: (160, 255,  80),   # belt A   — lime
        5: (255, 255,  80),   # belt B   — yellow
        6: (200,  80, 255),   # belt C   — purple
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
            return edge_idx[(min(a,b), max(a,b))]

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

        # Cell 0: upper wedge tetra (0,1,2,3) toward +W
        self.cells.add_link((
            fi(0,1,2), fi(0,1,3), fi(0,2,3), fi(1,2,3),
            fi(0,1,5), fi(0,2,5), fi(1,2,5),
        ))
        # Cell 1: lower wedge tetra (0,1,2,4) toward +W
        self.cells.add_link((
            fi(0,1,2), fi(0,1,4), fi(0,2,4), fi(1,2,4),
            fi(0,1,5), fi(0,2,5), fi(1,2,5),
        ))
        # Cell 2: upper wedge toward -W
        self.cells.add_link((
            fi(0,1,2), fi(0,1,3), fi(0,2,3), fi(1,2,3),
            fi(0,1,6), fi(0,2,6), fi(1,2,6),
        ))
        # Cell 3: lower wedge toward -W
        self.cells.add_link((
            fi(0,1,2), fi(0,1,4), fi(0,2,4), fi(1,2,4),
            fi(0,1,6), fi(0,2,6), fi(1,2,6),
        ))
        # Cells 4-6: equatorial belt, one per equatorial edge
        for k in range(3):
            a, b = k, (k+1)%3
            self.cells.add_link((
                fi(a, b, 5),
                fi(a, b, 6),
                fi(*sorted([a, 5, 6])),
                fi(*sorted([b, 5, 6])),
            ))

        for p in self.v:
            self.rv.append(p)
            self.ov.append(p)