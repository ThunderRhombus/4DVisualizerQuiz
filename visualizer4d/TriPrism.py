import math as m
from Graph import Graph
from FourShape import FourShape

class TriPrism(FourShape):
    """
    A 4D shape: triangular prism suspended along W axis.
    6 prism vertices + 2 W-apices = 8 vertices.
    5 cells: 2 tetrahedral caps (over each triangular end-face) +
             3 square-pyramid cells (one per rectangular face).
    """

    cell_labels = [
        "+W Cap (Z+)", "+W Cap (Z-)", "-W Cap (Z+)", "-W Cap (Z-)",
        "+W Front Wall", "+W Left Wall", "+W Right Wall",
        "-W Front Wall", "-W Left Wall", "-W Right Wall"
    ]
    cell_colors = {
        0: (255, 220,  80),
        1: (255, 180,  80),
        2: ( 80, 160, 255),
        3: (100, 140, 255),
        4: (255, 100, 100),
        5: (100, 255, 120),
        6: (200,  80, 255),
        7: (200,  60,  60),
        8: ( 60, 200,  60),
        9: (120,  60, 200),
    }

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)

        s  = size
        h  = s * 0.866
        w4 = s * 1.0
        hz = s * 0.6

        tri = [
            ( s,       0,      0),
            (-s * 0.5,  h,     0),
            (-s * 0.5, -h,     0),
        ]
        self.v = []
        for tx, ty, _ in tri:
            self.v.append((tx+ox, ty+oy,  hz+oz, ow))   # top ring  0-2
        for tx, ty, _ in tri:
            self.v.append((tx+ox, ty+oy, -hz+oz, ow))   # bottom ring 3-5
        self.v.append((ox, oy, oz,  w4+ow))   # 6  +W apex
        self.v.append((ox, oy, oz, -w4+ow))   # 7  -W apex

        prism_edges = [
            (0,1),(1,2),(2,0),      # top triangle
            (3,4),(4,5),(5,3),      # bottom triangle
            (0,3),(1,4),(2,5),      # verticals
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
                edges = []
                for i in range(len(verts)):
                    edges.append(ei(verts[i], verts[(i+1)%len(verts)]))
                self.faces.add_link(tuple(edges))

        # Base triangles
        add_face((0, 1, 2)); add_face((3, 4, 5))
        # Side rectangles
        add_face((0, 1, 4, 3)); add_face((1, 2, 5, 4)); add_face((2, 0, 3, 5))
        # Suspension triangles
        for a, b in prism_edges:
            add_face((a, b, 6)); add_face((a, b, 7))

        def fi(*v):
            k = tuple(sorted(v))
            return face_idx[k]

        # Boundary Cells: Pyramid over every face of the prism to each W-apex
        
        # Base Triangles (0,1,2) and (3,4,5) to +W (6) and -W (7)
        # Cell 0: +W Top Tri
        self.cells.add_link((fi(0,1,2), fi(0,1,6), fi(1,2,6), fi(2,0,6)))
        # Cell 1: +W Bot Tri
        self.cells.add_link((fi(3,4,5), fi(3,4,6), fi(4,5,6), fi(5,3,6)))
        # Cell 2: -W Top Tri
        self.cells.add_link((fi(0,1,2), fi(0,1,7), fi(1,2,7), fi(2,0,7)))
        # Cell 3: -W Bot Tri
        self.cells.add_link((fi(3,4,5), fi(3,4,7), fi(4,5,7), fi(5,3,7)))

        # Rectangular Walls to +W (6) and -W (7)
        walls = [(0,1,4,3), (1,2,5,4), (2,0,3,5)]
        # Cells 4-6: +W walls
        for w_v in walls:
            e_pairs = [(w_v[i], w_v[(i+1)%4]) for i in range(4)]
            self.cells.add_link([fi(*w_v)] + [fi(a,b,6) for a,b in e_pairs])
        # Cells 7-9: -W walls
        for w_v in walls:
            e_pairs = [(w_v[i], w_v[(i+1)%4]) for i in range(4)]
            self.cells.add_link([fi(*w_v)] + [fi(a,b,7) for a,b in e_pairs])
            
        for p in self.v:
            self.rv.append(p)