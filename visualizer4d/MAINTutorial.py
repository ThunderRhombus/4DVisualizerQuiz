import pygame


class TutorialRenderer:
    """
    Wireframe renderer for the tutorial cube.
    Reads shape.ov (populated by FourShape.rotate) directly.
    Uses only x, y, z — ignores w so the cube looks purely 3D.
    """

    TUNING       = 0.25
    THICK_SHADOW = 8
    THICK_MAIN   = 4
    SHADOW_DROP  = 35

    def __init__(self, width: int, height: int):
        self.WIDTH  = width
        self.HEIGHT = height

    def render(self, screen: pygame.Surface, shapes: list) -> None:
        items = []

        for shape in shapes:
            ov = getattr(shape, 'ov', None)
            if not ov:
                continue

            # Edges
            for key in shape.edges.adj:
                if key >= 0:
                    continue
                neighbours = list(shape.edges.adj[key])
                if len(neighbours) != 2:
                    continue
                n0, n1 = neighbours[0], neighbours[1]
                if n0 >= len(ov) or n1 >= len(ov):
                    continue

                p1 = ov[n0]   # [x, y, z, w]
                p2 = ov[n1]

                N = 14 # Number of segments for gradient lines
                for i in range(N):
                    t1 = i / N
                    t2 = (i + 1) / N
                    ix1 = p1[0] * (1 - t1) + p2[0] * t1
                    iy1 = p1[1]*(1-t1) + p2[1]*t1
                    iz1 = p1[2]*(1-t1) + p2[2]*t1
                    ix2 = p1[0]*(1-t2) + p2[0]*t2
                    iy2 = p1[1]*(1-t2) + p2[1]*t2
                    iz2 = p1[2]*(1-t2) + p2[2]*t2
                    avg_z = (iz1 + iz2) / 2.0

                    g        = max(0, min(255, int(127 + avg_z * self.TUNING)))
                    g_shadow = max(0, min(255, g - self.SHADOW_DROP))
                    line_color = (g, g, g)
                    shadow_color = (g_shadow, g_shadow, g_shadow)

                    items.append({
                        'z': avg_z,
                        'p1': (self.WIDTH  // 2 + round(ix1),
                               self.HEIGHT // 2 + round(iy1)),
                        'p2': (self.WIDTH  // 2 + round(ix2),
                               self.HEIGHT // 2 + round(iy2)),
                        'c_shadow': shadow_color,
                        'c_main':   line_color,
                    })

        items.sort(key=lambda it: it['z'])

        for it in items:
            pygame.draw.line(screen, it['c_shadow'], it['p1'], it['p2'], self.THICK_SHADOW)
            pygame.draw.line(screen, it['c_main'],   it['p1'], it['p2'], self.THICK_MAIN)