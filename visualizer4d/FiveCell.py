import math as m
from Graph import Graph
from FourShape import FourShape

class FiveCell(FourShape):
    """
    The 5-cell (pentachoron / 4-simplex).
    The simplest regular 4D polytope — the 4D analogue of the tetrahedron.
    5 vertices, 10 edges, 10 triangular faces, 5 tetrahedral cells.
    Each cell is named for the vertex it does NOT contain.
    """

    cell_labels = ["opp-A", "opp-B", "opp-C", "opp-D", "opp-E"]
    cell_colors = {
        0: (255, 100, 100),
        1: (100, 255, 100),
        2: (100, 100, 255),
        3: (255, 255, 100),
        4: (255, 150,  50),
    }

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)

        # 5 vertices of a regular 4-simplex, centred at origin.
        raw = [
            ( 1,  1,  1, -1/m.sqrt(5)),
            ( 1, -1, -1, -1/m.sqrt(5)),
            (-1,  1, -1, -1/m.sqrt(5)),
            (-1, -1,  1, -1/m.sqrt(5)),
            ( 0,  0,  0,  4/m.sqrt(5)),
        ]
        edge_len = m.sqrt(sum((raw[0][k]-raw[1][k])**2 for k in range(4)))
        scale = (2 * size) / edge_len

        self.v = [
            (scale*p[0] + ox, scale*p[1] + oy, scale*p[2] + oz, scale*p[3] + ow)
            for p in raw
        ]

        # 10 edges — every pair of vertices
        pairs = [(i, j) for i in range(5) for j in range(i+1, 5)]
        for a, b in pairs:
            self.edges.add_link((a, b))

        # 10 triangular faces — every triple of vertices
        triples = [(i, j, k) for i in range(5) for j in range(i+1, 5) for k in range(j+1, 5)]
        pair_idx = {(a, b): idx for idx, (a, b) in enumerate(pairs)}

        def edge_of(a, b):
            return pair_idx[(min(a,b), max(a,b))]

        for i, j, k in triples:
            self.faces.add_link((edge_of(i,j), edge_of(i,k), edge_of(j,k)))

        # 5 tetrahedral cells — cell n is opposite vertex n (omits vertex n)
        triple_idx = {(i,j,k): idx for idx,(i,j,k) in enumerate(triples)}

        def face_of(a, b, c):
            return triple_idx[tuple(sorted([a, b, c]))]

        for omit in range(5):
            verts = [v for v in range(5) if v != omit]
            i, j, k, l = verts
            self.cells.add_link((
                face_of(i, j, k),
                face_of(i, j, l),
                face_of(i, k, l),
                face_of(j, k, l),
            ))

        for p in self.v:
            self.rv.append(p)
