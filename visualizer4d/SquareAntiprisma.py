import math as m
import numpy
from Graph import Graph
from FourShape import FourShape

class SquareAntiprisma(FourShape):
    """
    A 4D shape: square antiprism suspended along the W axis.
    8 antiprism vertices + 2 W-apices = 10 vertices.
    Cells: 2 square-pyramid caps + 8 band tetrahedra (4 per W side).
    """

    # Ordered: +W cap, -W cap, then +W band (4), then -W band (4)
    cell_labels = [
        "+W cap", "-W cap",
        "+W band 1", "+W band 2", "+W band 3", "+W band 4",
        "-W band 1", "-W band 2", "-W band 3", "-W band 4",
    ]
    cell_colors = {
        0: (255, 220,  80),   # +W cap  — gold
        1: ( 80, 160, 255),   # -W cap  — blue
        2: (255, 120,  80),   # +W band — orange family
        3: (255, 180,  80),
        4: (220, 255,  80),
        5: (140, 255, 100),
        6: ( 80, 220, 200),   # -W band — teal/purple family
        7: ( 80, 140, 255),
        8: (160,  80, 255),
        9: (220,  80, 200),
    }

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)

        s   = size
        r   = s * 0.9
        hz  = s * 0.55
        w4  = s * 1.05
        rot = m.pi / 4

        self.v = []
        for k in range(4):
            ang = k * m.pi / 2
            self.v.append((r*m.cos(ang)+ox, r*m.sin(ang)+oy,  hz+oz, ow))
        for k in range(4):
            ang = k * m.pi / 2 + rot
            self.v.append((r*m.cos(ang)+ox, r*m.sin(ang)+oy, -hz+oz, ow))
        self.v.append((ox, oy, oz,  w4+ow))   # 8  +W apex
        self.v.append((ox, oy, oz, -w4+ow))   # 9  -W apex

        edge_idx = {}

        def add_edge(a, b):
            k = (min(a,b), max(a,b))
            if k not in edge_idx:
                edge_idx[k] = len(edge_idx)
                self.edges.add_link(k)

        for k in range(4):
            add_edge(k, (k+1) % 4)
        for k in range(4):
            add_edge(4+k, 4 + (k+1) % 4)
        for k in range(4):
            add_edge(k, 4+k)
            add_edge(k, 4 + (k-1) % 4)
        for i in range(8):
            add_edge(i, 8)
            add_edge(i, 9)

        def ei(a, b):
            return edge_idx[(min(a,b), max(a,b))]

        face_idx = {}

        def add_face(a, b, c):
            k = tuple(sorted([a, b, c]))
            if k not in face_idx:
                face_idx[k] = len(face_idx)
                i, j, l = k
                self.faces.add_link((ei(i,j), ei(i,l), ei(j,l)))

        def add_quad(a, b, c, d):
            add_face(a, b, c)
            add_face(a, c, d)

        add_quad(0, 1, 2, 3)
        add_quad(4, 5, 6, 7)

        band_tris = []
        for k in range(4):
            t1 = (k, (k+1)%4, 4+k)
            t2 = ((k+1)%4, 4+(k+1)%4, 4+k)
            band_tris.append(t1)
            band_tris.append(t2)
        for tri in band_tris:
            add_face(*tri)

        for i in range(8):
            for j in range(i+1, 8):
                k = (min(i,j), max(i,j))
                if k in edge_idx:
                    add_face(i, j, 8)
                    add_face(i, j, 9)

        def fi(a, b, c):
            return face_idx[tuple(sorted([a, b, c]))]

        top_sq_tris = [(0,1,2),(0,2,3)]
        bot_sq_tris = [(4,5,6),(4,6,7)]

        # Cell 0: +W cap (pyramid over top square)
        cap_p_faces = [fi(*t) for t in top_sq_tris]
        for k in range(4):
            cap_p_faces.append(fi(k, (k+1)%4, 8))
        self.cells.add_link(cap_p_faces)

        # Cell 1: -W cap (pyramid over bottom square)
        cap_m_faces = [fi(*t) for t in bot_sq_tris]
        for k in range(4):
            cap_m_faces.append(fi(4+k, 4+(k+1)%4, 9))
        self.cells.add_link(cap_m_faces)

        # Cells 2-5: +W band (each pair of band triangles toward +W apex)
        for k in range(4):
            t_up   = (k, (k+1)%4, 4+k)
            t_down = ((k+1)%4, 4+(k+1)%4, 4+k)
            self.cells.add_link((
                fi(*t_up), fi(*t_down),
                fi(k, (k+1)%4, 8),
                fi(4+k, 4+(k+1)%4, 8),
            ))

        # Cells 6-9: -W band (same pairs toward -W apex)
        for k in range(4):
            t_up   = (k, (k+1)%4, 4+k)
            t_down = ((k+1)%4, 4+(k+1)%4, 4+k)
            self.cells.add_link((
                fi(*t_up), fi(*t_down),
                fi(k, (k+1)%4, 9),
                fi(4+k, 4+(k+1)%4, 9),
            ))

        for p in self.v:
            self.rv.append(p)
            self.ov.append(p)