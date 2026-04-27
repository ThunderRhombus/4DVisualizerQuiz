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

    # Ordered: W caps first (top/bottom), then the three lateral walls A/B/C
    cell_labels = ["+W cap", "-W cap", "wall A", "wall B", "wall C"]
    cell_colors = {
        0: (255, 220,  80),   # +W cap  — gold
        1: ( 80, 160, 255),   # -W cap  — sky blue
        2: (255, 100, 100),   # wall A  — red
        3: (100, 255, 120),   # wall B  — green
        4: (200,  80, 255),   # wall C  — purple
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
            try:
                return edge_idx[(min(a,b), max(a,b))]
            except KeyError:
                # If we need a diagonal for a face, we must add it as an edge
                k = (min(a,b), max(a,b))
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

        def fi(*v): return face_idx[tuple(sorted(v))]

        # Cells
        # Cell 0 & 1: Dipyramids over the triangular bases
        self.cells.add_link([fi(0,1,6), fi(1,2,6), fi(2,0,6), fi(0,1,7), fi(1,2,7), fi(2,0,7)])
        self.cells.add_link([fi(3,4,6), fi(4,5,6), fi(5,3,6), fi(3,4,7), fi(4,5,7), fi(5,3,7)])
        
        # Walls: Dipyramids over the rectangular side faces
        walls = [(0,1,4,3), (1,2,5,4), (2,0,3,5)]
        for w_v in walls:
            edges = [(w_v[i], w_v[(i+1)%4]) for i in range(4)]
            self.cells.add_link([fi(a,b,6) for a,b in edges] + [fi(a,b,7) for a,b in edges])

        for p in self.v:
            self.rv.append(p)