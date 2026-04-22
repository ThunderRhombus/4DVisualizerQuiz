import pygame
import numpy
import math as m
from Tesseract import Tesseract
from Edge import Edge
from wAxis import wAxis

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fast Continuous Gradient Wireframe Scene")
clock = pygame.time.Clock()

size = 100
tuning = 0.2

ortho = 0.001
tess = Tesseract(size, ortho, 0, 0, 0, 0)
axis = wAxis(size * 2, ortho, 0, 0, 0, 0)
yaw = 0
pitch = 0
roll = 0
dip = 0
tuck = 0
skew = 0
mousex, mousey = WIDTH // 2, HEIGHT // 2
lastx, lasty = mousex, mousey
dragging = False
xsens, ysens = WIDTH/180, HEIGHT/180
vwheel = 0

dr = 0
dy = 0

dd = 0.1
dt = 0.0
ds = 0.0
a4 = (dd,dt,ds)
d4 = 0
paused = False
togglescroll = True

dz = 1


font = pygame.font.SysFont(None, 24)

def render_shapes(shapes, screen, tuning):
    lines_to_draw = []
    
    # 1. Edge interpolation to generate perfectly continuous lines with dynamic gradients
    for shape in shapes:
        edges = []
        for v in shape.edges.adj:
            if v < 0:
                n = list(shape.edges.adj[v])
                if len(n) == 2:
                    edges.append((n[0], n[1]))
                    
        for n0, n1 in edges:
            p1 = shape.ov[n0]
            p2 = shape.ov[n1]
            
            # Using 15 sub-segments completely eliminates patchiness while preserving dynamic color grading
            N = 15
            for i in range(N):
                t1 = i / float(N)
                t2 = (i + 1) / float(N)
                
                pt1 = [p1[j] * (1-t1) + p2[j] * t1 for j in range(4)]
                pt2 = [p1[j] * (1-t2) + p2[j] * t2 for j in range(4)]
                
                avg_z = (pt1[2] + pt2[2]) / 2.0
                
                g_val = 127 + (avg_z * tuning)
                d_val = (pt1[3] + pt2[3]) * tuning
                
                r = g_val + d_val
                b = g_val - d_val
                
                r_c = max(0, min(255, int(round(r))))
                g_c = max(0, min(255, int(round(g_val))))
                b_c = max(0, min(255, int(round(b))))
                g_shadow = max(0, min(255, int(round(g_val - 30))))
                
                lines_to_draw.append({
                    'z': avg_z,
                    'p1': (WIDTH//2 + round(pt1[0]), HEIGHT//2 + round(pt1[1])),
                    'p2': (WIDTH//2 + round(pt2[0]), HEIGHT//2 + round(pt2[1])),
                    'thickness_shadow': 9,
                    'thickness_main': 5,
                    'c_shadow': (r_c, g_shadow, b_c),
                    'c_main': (r_c, g_c, b_c)
                })

    # 2. Fast Painter's Algorithm replaces slow python loop scanning
    lines_to_draw.sort(key=lambda item: item['z'])
    
    # 3. Blitting
    for line in lines_to_draw:
        pygame.draw.line(screen, line['c_shadow'], line['p1'], line['p2'], line['thickness_shadow'])
        pygame.draw.line(screen, line['c_main'], line['p1'], line['p2'], line['thickness_main'])

    # 4. Render Origin Point Overlays isolated to ensure absolute top rendering
    for shape in shapes:
        if hasattr(shape, 'hastext') and shape.hastext:
            for p in range(len(shape.ov)):
                text = shape.getText(p)
                if text:
                    z = shape.ov[p][2]
                    w = shape.ov[p][3]
                    g_val = 127 + round(z * tuning)
                    d_val = round((w + w) * tuning)
                    
                    r_c = max(0, min(255, int(g_val + d_val)))
                    b_c = max(0, min(255, int(g_val - d_val)))
                    g_c = max(0, min(255, int(g_val)))
                    
                    sx = WIDTH//2 + round(shape.ov[p][0])
                    sy = HEIGHT//2 + round(shape.ov[p][1])
                    
                    pygame.draw.circle(screen, (r_c, g_c, b_c), (sx, sy), 10)
                    text_surf = font.render(text, True, (255, 255, 255))
                    screen.blit(text_surf, (sx - 5, sy - 5))

shapes = [tess, axis]
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            dragging = True
            lastx, lasty = event.pos
            mousex, mousey = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            vx = (mousex - lastx) / xsens
            vy = (mousey - lasty) / ysens
            if abs(vx) > abs(vy) and abs(vx) > 0.1:
                dy = vx
                dr = 0
            elif abs(vy) > 0.1:
                dr = vy
                dy = 0
            else:
                dr = 0
                dy = 0
        elif event.type == pygame.MOUSEMOTION and dragging:
            lastx, lasty = mousex, mousey
            mousex, mousey = event.pos
            yaw -= (mousex - lastx) / xsens
            roll -= (mousey - lasty) / ysens
            dr = 0
            dy = 0

        if event.type == pygame.MOUSEWHEEL:
            if togglescroll:
                vwheel = -event.y
                d4 = vwheel * 3
            else:
                ortho += event.y * 0.0002
                ortho = max(0, min(0.005, ortho))

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_LCTRL:
                togglescroll = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LCTRL:
                togglescroll = True

    screen.fill((0, 0, 0))
    
    yaw -= dy
    roll -= dr

    if not paused:
        dip += d4 * a4[0]
        tuck += d4 * a4[1]
        skew += d4 * a4[2]
        
        dip %= 360
        tuck %= 360
        skew %= 360

    for shape in shapes:
        shape.rotate(yaw, pitch, roll, dip, tuck, skew)
        shape.shrink(ortho)
        
    render_shapes(shapes, screen, tuning)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
