import math as m
from Graph import Graph
from FourShape import FourShape

class SquareAntiprisma(FourShape):
    """
    A 4D shape: square antiprism suspended along the W axis.
    8 antiprism vertices + 2 W-apices = 10 vertices.
    Cells: 2 square-pyramid caps + 8 band tetrahedra (4 per W side).
    """
    
    cell_labels = []
    directions = ["Front", "Front-Right", "Right", "Back-Right", "Back", "Back-Left", "Left", "Front-Left"]
    cell_labels += ["+W Cap (Z+)", "+W Cap (Z-)"] + [f"+W {d}" for d in directions]
    cell_labels += ["-W Cap (Z+)", "-W Cap (Z-)"] + [f"-W {d}" for d in directions]

    cell_colors = {
        0: (255, 220,  80),   # +W caps
        1: (255, 180,  80),
        2: ( 80, 160, 255),   # -W caps
        3: (100, 140, 255),
    }
    # Band colors
    for i in range(4, 12):
        cell_colors[i] = (255, 120 + (i-4)*15, 80)
    for i in range(12, 20):
        cell_colors[i] = (80, 220, 200 - (i-12)*15)

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
                edges = []
                for i in range(len(v)):
                    edges.append(ei(v[i], v[(i+1)%len(v)]))
                self.faces.add_link(tuple(edges))

        add_face(0, 1, 2, 3)
        add_face(4, 5, 6, 7)

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

        def fi(*v):
            k = tuple(sorted(v))
            return face_idx[k]

        # Cell 0: +W side, Top Square Pyramid
        self.cells.add_link([fi(0,1,8), fi(1,2,8), fi(2,3,8), fi(3,0,8), fi(0,1,2,3)])
        # Cell 1: +W side, Bot Square Pyramid
        self.cells.add_link([fi(4,5,8), fi(5,6,8), fi(6,7,8), fi(7,4,8), fi(4,5,6,7)])
        
        # Cell 2: -W side, Top Square Pyramid
        self.cells.add_link([fi(0,1,9), fi(1,2,9), fi(2,3,9), fi(3,0,9), fi(0,1,2,3)])
        # Cell 3: -W side, Bot Square Pyramid
        self.cells.add_link([fi(4,5,9), fi(5,6,9), fi(6,7,9), fi(7,4,9), fi(4,5,6,7)])

        # Cells 4-11: +W side Band (8 tetrahedra)
        for tri in band_tris:
            a, b, c = tri
            self.cells.add_link((fi(a,b,c), fi(a,b,8), fi(b,c,8), fi(a,c,8)))
            
        # Cells 12-19: -W side Band (8 tetrahedra)
        for tri in band_tris:
            a, b, c = tri
            self.cells.add_link((fi(a,b,c), fi(a,b,9), fi(b,c,9), fi(a,c,9)))

        for p in self.v:
            self.rv.append(p)
