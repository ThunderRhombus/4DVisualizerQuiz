import pygame
import numpy
import math as m

class WireframeRenderer:
    def __init__(self, width, height, tuning=0.2, a4=(0.1, 0.0, 0.0)):
        self.WIDTH = width
        self.HEIGHT = height
        self.tuning = tuning
        self.a4 = a4
        self.font = pygame.font.SysFont(None, 24)

    def _sx(self, x): return self.WIDTH  // 2 + round(x)
    def _sy(self, y): return self.HEIGHT // 2 - round(y)   # Y-flip: up is positive

    def render(self, screen, shapes):
        items_to_draw = []
        final_text = []
    
        for shape in shapes:
            # 1. Labels & Circles
            if getattr(shape, 'hastext', False):
                for p in range(len(shape.ov)):
                    text = shape.getText(p)
                    if text:
                        z = shape.ov[p][2]
                        w = shape.ov[p][3]
                        pos = (self._sx(shape.ov[p][0]), self._sy(shape.ov[p][1]))
                        
                        g_val = 127 + round(z * self.tuning)
                        d_val = round((w + w) * self.tuning)
                        r_c = max(0, min(255, int(g_val + d_val)))
                        b_c = max(0, min(255, int(g_val - d_val)))
                        g_c = max(0, min(255, int(g_val)))
                        
                        items_to_draw.append({
                            'z': z,
                            'type': 'circle',
                            'pos': pos,
                            'color': (r_c, g_c, b_c)
                        })
                        final_text.append({'text': text, 'pos': pos})

            # 2. Edges
            edges = []
            for v in shape.edges.adj:
                if v < 0:
                    n = list(shape.edges.adj[v])
                    if len(n) == 2:
                        edges.append((n[0], n[1]))
                    
            for n0, n1 in edges:
                p1 = shape.ov[n0]
                p2 = shape.ov[n1]
            
                N = 15
                for i in range(N):
                    t1, t2 = i / float(N), (i + 1) / float(N)
                    pt1 = [p1[j] * (1-t1) + p2[j] * t1 for j in range(4)]
                    pt2 = [p1[j] * (1-t2) + p2[j] * t2 for j in range(4)]
                    avg_z = (pt1[2] + pt2[2]) / 2.0
                    g_val = 127 + (avg_z * self.tuning)
                    d_val = (pt1[3] + pt2[3]) * self.tuning
                    r, b = g_val + d_val, g_val - d_val
                    r_c = max(0, min(255, int(round(r))))
                    g_c = max(0, min(255, int(round(g_val))))
                    b_c = max(0, min(255, int(round(b))))
                    g_shadow = max(0, min(255, int(round(g_val - 30))))
                
                    items_to_draw.append({
                        'z': avg_z,
                        'type': 'line',
                        'p1': (self._sx(pt1[0]), self._sy(pt1[1])),
                        'p2': (self._sx(pt2[0]), self._sy(pt2[1])),
                        'thickness_shadow': 9,
                        'thickness_main': 5,
                        'c_shadow': (r_c, g_shadow, b_c),
                        'c_main': (r_c, g_c, b_c)
                    })

        items_to_draw.sort(key=lambda item: item['z'])
        for item in items_to_draw:
            if item['type'] == 'line':
                pygame.draw.line(screen, item['c_shadow'], item['p1'], item['p2'], item['thickness_shadow'])
                pygame.draw.line(screen, item['c_main'], item['p1'], item['p2'], item['thickness_main'])
            elif item['type'] == 'circle':
                pygame.draw.circle(screen, item['color'], item['pos'], 10)

        for lbl in final_text:
            text_surf = self.font.render(lbl['text'], True, (255, 255, 255))
            screen.blit(text_surf, (lbl['pos'][0] - text_surf.get_width()//2, lbl['pos'][1] - text_surf.get_height()//2))


def main(a4=(0.1, 0.0, 0.0)):
    from Tesseract import Tesseract
    from origin_viewer import spawn_origin_viewer
    
    shared_arr = spawn_origin_viewer()
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Modular Wireframe Renderer")
    clock = pygame.time.Clock()

    renderer = WireframeRenderer(WIDTH, HEIGHT, a4=a4)
    tess = Tesseract(100, 0.001, 0, 0, 0, 0)
    shapes = [tess]
    
    ortho = 0.001
    yaw, pitch, roll, dip, tuck, skew = 0, 0, 0, 0, 0, 0
    dragging = False
    xsens, ysens = WIDTH/180, HEIGHT/180
    dy, dr = 0, 0
    d4 = 0
    paused = False
    togglescroll = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                dragging = True
                lastx, lasty = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                vx = (pygame.mouse.get_pos()[0] - lastx) / xsens
                vy = (pygame.mouse.get_pos()[1] - lasty) / ysens
                if abs(vx) > abs(vy) and abs(vx) > 0.1:
                    dy = vx; dr = 0
                elif abs(vy) > 0.1:
                    dr = vy; dy = 0
                else:
                    dr, dy = 0, 0
            elif event.type == pygame.MOUSEMOTION and dragging:
                mx, my = event.pos
                yaw -= (mx - lastx) / xsens
                roll -= (my - lasty) / ysens
                lastx, lasty = mx, my
                dr, dy = 0, 0

            if event.type == pygame.MOUSEWHEEL:
                if togglescroll:
                    d4 = -event.y * 3
                else:
                    ortho = max(0, min(0.005, ortho + event.y * 0.0002))

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: paused = not paused
                if event.key == pygame.K_LCTRL: togglescroll = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LCTRL: togglescroll = True

        screen.fill((0, 0, 0))
        yaw -= dy
        roll -= dr

        if not paused:
            dip = (dip + d4 * a4[0]) % 360
            tuck = (tuck + d4 * a4[1]) % 360
            skew = (skew + d4 * a4[2]) % 360

        for shape in shapes:
            shape.rotate(yaw, pitch, roll, dip, tuck, skew)
            shape.shrink(ortho)
        
        renderer.render(screen, shapes)
        shared_arr[:] = [yaw, pitch, roll, dip, tuck, skew, ortho]
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == '__main__':
    main()