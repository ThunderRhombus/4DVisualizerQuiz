import math as m
from Graph import Graph
from FourShape import FourShape

class FiveCell(FourShape):
    """
    The 5-cell (pentachoron / 4-simplex).
    5 vertices, 10 edges, 10 triangular faces, 5 tetrahedral cells.
    Each cell is the tetrahedron opposite one vertex.
    """

    # Each cell omits one vertex; labelled by the direction toward that vertex
    # as visible on the XYZ origin widget.
    #   omit v4 (+W apex)        → "-W"    (the base-tet cell)
    #   omit v0 (+X+Y+Z corner)  → "+X+Y"
    #   omit v1 (+X-Y-Z corner)  → "+X-Z"
    #   omit v2 (-X+Y-Z corner)  → "-X+Y"
    #   omit v3 (-X-Y+Z corner)  → "-X+Z"
    cell_labels = ["-W", "+X+Y", "+X-Z", "-X+Y", "-X+Z"]
    cell_colors = {
        0: (255, 220,  80),   # -W base tet  — gold
        1: (100, 200, 255),   # +X+Y corner  — sky blue
        2: (255, 100, 100),   # +X-Z corner  — red
        3: (100, 255, 140),   # -X+Y corner  — green
        4: (200,  80, 255),   # -X+Z corner  — purple
    }

    def __init__(self, size, ortho, ox, oy, oz, ow):
        super().__init__(size, ortho)

        raw = [
            ( 1,  1,  1, -1/m.sqrt(5)),
            ( 1, -1, -1, -1/m.sqrt(5)),
            (-1,  1, -1, -1/m.sqrt(5)),
            (-1, -1,  1, -1/m.sqrt(5)),
            ( 0,  0,  0,  4/m.sqrt(5)),
        ]
        edge_len = m.sqrt(sum((raw[0][k]-raw[1][k])**2 for k in range(4)))
        # Scale so the shape fills space comparably to the Tesseract (edge ~200 units)
        scale = (2 * size) / edge_len

        self.v = [
            (scale*p[0]+ox, scale*p[1]+oy, scale*p[2]+oz, scale*p[3]+ow)
            for p in raw
        ]

        pairs = [(i, j) for i in range(5) for j in range(i+1, 5)]
        for a, b in pairs:
            self.edges.add_link((a, b))

        triples = [(i, j, k) for i in range(5) for j in range(i+1, 5) for k in range(j+1, 5)]
        pair_idx = {(a, b): idx for idx, (a, b) in enumerate(pairs)}

        def edge_of(a, b):
            return pair_idx[(min(a,b), max(a,b))]

        for i, j, k in triples:
            self.faces.add_link((edge_of(i,j), edge_of(i,k), edge_of(j,k)))

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