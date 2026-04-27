import math as m
import numpy
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
            return edge_idx[(min(a,b), max(a,b))]

        tri_faces   = [(0,1,2), (3,4,5)]
        rect_tris   = [
            (0,1,4),(0,3,4),
            (1,2,5),(1,4,5),
            (2,0,3),(2,5,3),
        ]
        susp_tris   = [(a,b,6) for a,b in prism_edges] + [(a,b,7) for a,b in prism_edges]

        face_idx = {}
        for tri_v in tri_faces + rect_tris + susp_tris:
            k = tuple(sorted(tri_v))
            if k not in face_idx:
                face_idx[k] = len(face_idx)
                i, j, l = k
                self.faces.add_link((ei(i,j), ei(i,l), ei(j,l)))

        def fi(a, b, c):
            return face_idx[tuple(sorted([a, b, c]))]

        def apex_cell(apex):
            faces_in = [fi(a, b, apex) for a, b in prism_edges]
            faces_in.append(fi(0, 1, 2))
            faces_in.append(fi(3, 4, 5))
            return faces_in

        # Cells ordered: +W cap, -W cap, then three walls
        self.cells.add_link(apex_cell(6))   # 0  +W cap
        self.cells.add_link(apex_cell(7))   # 1  -W cap

        rect_bands = [
            ((0,1,4,3), [(0,1),(1,4),(4,3),(3,0)]),
            ((1,2,5,4), [(1,2),(2,5),(5,4),(4,1)]),
            ((2,0,3,5), [(2,0),(0,3),(3,5),(5,2)]),
        ]
        for _, band_edges in rect_bands:
            faces_in = []
            for a, b in band_edges:
                faces_in.append(fi(a, b, 6))
                faces_in.append(fi(a, b, 7))
            faces_in.append(fi(0, 1, 2))
            faces_in.append(fi(3, 4, 5))
            self.cells.add_link(faces_in)   # 2, 3, 4

        for p in self.v:
            self.rv.append(p)
            self.ov.append(p)