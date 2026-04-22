import pygame
import numpy as np
import math as m
from Tesseract import Tesseract
from Edge import Edge
from wAxis import wAxis

def sort_coplanar_vertices(verts_3d):
    if len(verts_3d) <= 2: return [i for i in range(len(verts_3d))]
    c = np.mean(verts_3d, axis=0)
    v0 = np.array(verts_3d[0]) - c
    u = v0 / (np.linalg.norm(v0) + 1e-9)
    v1 = np.array(verts_3d[1]) - c
    w = v1 - np.dot(v1, u) * u
    if np.linalg.norm(w) < 1e-5:
        v1 = np.array(verts_3d[2]) - c
        w = v1 - np.dot(v1, u) * u
    w = w / (np.linalg.norm(w) + 1e-9)
    angles = []
    for p in verts_3d:
        vec = np.array(p) - c
        angles.append(m.atan2(np.dot(vec, w), np.dot(vec, u)))
    return np.argsort(angles)

def get_edge_vertices(shape, e_idx):
    verts = [v for v in shape.edges.adj[-e_idx - 1] if v >= 0]
    return verts[0], verts[1]

def render_wireframe_wshells(shapes, screen, tuning, target_w, WIDTH, HEIGHT, font):
    draw_list = []
    
    # 1. Very Faint Global Wireframe
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
            avg_z = (p1[2] + p2[2]) / 2.0
            
            g_val = 127 + avg_z * tuning
            c_val = max(0, min(255, int(g_val)))
            color = (c_val, c_val, c_val, 65) # Increased outline visibility 
            
            draw_list.append({
                'z': avg_z,
                'p1': (WIDTH//2 + round(p1[0]), HEIGHT//2 + round(p1[1])),
                'p2': (WIDTH//2 + round(p2[0]), HEIGHT//2 + round(p2[1])),
                'color_main': color,
                'thickness': 2, # Made slightly thicker for structural clarity
                'type': 'global'
            })
            
    # 2. Solid W-Shells Slicing (Slicing 3D volume cells creates solid 2D flat geometric boundaries!)
    w_shells_radius = 9  # More layers effectively since we condense them locally!
    
    for shell_offset in range(-w_shells_radius, w_shells_radius + 1):
        # Progressively bigger steps: distance grows super-linearly allowing dense center mapping
        sign = 1 if shell_offset > 0 else (-1 if shell_offset < 0 else 0)
        W_slice = target_w + sign * (abs(shell_offset) ** 1.6) * 4.0
        
        # Steeper transparency curve using power scaling (drastic drop-off)
        dist_ratio = abs(shell_offset) / float(w_shells_radius)
        opacity_factor = (1.0 - dist_ratio) ** 3.0
        if opacity_factor <= 0.01: continue
        
        for shape in shapes:
            if not hasattr(shape, 'cells'): continue
            
            for c_link in shape.cells.adj:
                if c_link >= 0: continue
                
                cell_faces = list(shape.cells.adj[c_link])
                cell_edges = set()
                for f in cell_faces:
                    face_link = -f - 1
                    for e_idx in shape.faces.adj[face_link]:
                        cell_edges.add(e_idx)
                        
                intersection_pts = []
                
                for e_idx in cell_edges:
                    v1_idx, v2_idx = get_edge_vertices(shape, e_idx)
                    v1 = shape.ov[v1_idx]
                    v2 = shape.ov[v2_idx]
                    
                    if (v1[3] <= W_slice and v2[3] >= W_slice) or (v1[3] >= W_slice and v2[3] <= W_slice):
                        dw = v2[3] - v1[3]
                        if abs(dw) > 1e-7:
                            t = (W_slice - v1[3]) / dw
                            P = [v1[j]*(1-t) + v2[j]*t for j in range(4)]
                            intersection_pts.append(P)
                        else:
                            intersection_pts.append(v1)
                            intersection_pts.append(v2)
                            
                unique_pts = []
                for p in intersection_pts:
                    if not any(sum(abs(p[j] - u[j]) for j in range(3)) < 1e-4 for u in unique_pts):
                        unique_pts.append(p)
                        
                # Extrude solid polygon shell shapes 
                if len(unique_pts) >= 3:
                    vs_3d = [u[:3] for u in unique_pts]
                    sorted_idx = sort_coplanar_vertices(vs_3d)
                    
                    avg_z = sum(vs_3d[i][2] for i in sorted_idx) / len(sorted_idx)
                    avg_w = sum(unique_pts[i][3] for i in sorted_idx) / len(sorted_idx)
                    
                    g_val = 127 + avg_z * tuning
                    d_val = (avg_w * 2) * tuning
                    
                    r = max(0, min(255, int(g_val + d_val)))
                    b = max(0, min(255, int(g_val - d_val)))
                    g_c = max(0, min(255, int(g_val)))
                    
                    alpha = int(255 * opacity_factor * 0.8) # Solid local target center
                    
                    draw_list.append({
                        'z': avg_z,
                        'type': 'poly',
                        'pts': [(WIDTH//2 + round(unique_pts[i][0]), HEIGHT//2 + round(unique_pts[i][1])) for i in sorted_idx],
                        'color_main': (r, g_c, b, alpha),
                        'color_shadow': (r, max(0, g_c-30), b, min(255, alpha + 40))
                    })
                            
    # 3. Z-Sorting and Custom Alpha Surface Drawing 
    draw_list.sort(key=lambda item: item['z'])
    
    for item in draw_list:
        if item['type'] == 'global':
            p1, p2 = item['p1'], item['p2']
            min_x = min(p1[0], p2[0]) - 5
            max_x = max(p1[0], p2[0]) + 5
            min_y = min(p1[1], p2[1]) - 5
            max_y = max(p1[1], p2[1]) + 5
            w_bd = max_x - min_x
            h_bd = max_y - min_y
            if w_bd > 0 and h_bd > 0:
                tsurf = pygame.Surface((w_bd, h_bd), pygame.SRCALPHA)
                loc1, loc2 = (p1[0] - min_x, p1[1] - min_y), (p2[0] - min_x, p2[1] - min_y)
                pygame.draw.line(tsurf, item['color_main'], loc1, loc2, item['thickness'])
                screen.blit(tsurf, (min_x, min_y))
        
        elif item['type'] == 'poly':
            pts = item['pts']
            min_x = min(p[0] for p in pts) - 2
            max_x = max(p[0] for p in pts) + 2
            min_y = min(p[1] for p in pts) - 2
            max_y = max(p[1] for p in pts) + 2
            w_bd = max_x - min_x
            h_bd = max_y - min_y
            if w_bd > 0 and h_bd > 0:
                tsurf = pygame.Surface((w_bd, h_bd), pygame.SRCALPHA)
                local_pts = [(p[0] - min_x, p[1] - min_y) for p in pts]
                pygame.draw.polygon(tsurf, item['color_main'], local_pts, 0)
                screen.blit(tsurf, (min_x, min_y))
            
    # 4. Render origin circles dynamically on the surfaces
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
                    
                    cx = WIDTH//2 + round(shape.ov[p][0])
                    cy = HEIGHT//2 + round(shape.ov[p][1])
                    pygame.draw.circle(screen, (r_c, g_c, b_c), (cx, cy), 10)
                    text_surf = font.render(text, True, (255, 255, 255))
                    screen.blit(text_surf, (cx-5, cy-5))

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4D Target-W Slicing Wireframe Viewer")
clock = pygame.time.Clock()

size = 100
tuning = 0.2
ortho = 0.001
tess = Tesseract(size, ortho, 0, 0, 0, 0)
axis = wAxis(size * 2, ortho, 0, 0, 0, 0)
shapes = [tess, axis]

yaw, pitch, roll = 0, 0, 0
dip, tuck, skew = 0, 0, 0
mousex, mousey = WIDTH // 2, HEIGHT // 2
lastx, lasty = mousex, mousey
dragging = False
xsens, ysens = WIDTH/180, HEIGHT/180
vwheel = 0

dy, dr = 0, 0
a4 = (0.1, 0.0, 0.0)
d4 = 0
paused = False
togglescroll = True
target_w = 0.0

font = pygame.font.SysFont(None, 24)



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
            if dragging:
                dragging = False
                vx = (mousex - lastx) / xsens
                vy = (mousey - lasty) / ysens
                if abs(vx) > abs(vy) and abs(vx) > 0.1:
                    dy = vx; dr = 0
                elif abs(vy) > 0.1:
                    dr = vy; dy = 0
                else:
                    dr, dy = 0, 0
        elif event.type == pygame.MOUSEMOTION and dragging:
            lastx, lasty = mousex, mousey
            mousex, mousey = event.pos
            yaw -= (mousex - lastx) / xsens
            roll -= (mousey - lasty) / ysens
            dr, dy = 0, 0

        if event.type == pygame.MOUSEWHEEL:
            if togglescroll:
                vwheel = -event.y
                d4 = vwheel * 5
            else:
                target_w += event.y * 10.0 # Target W shift via CTRL + Scroll

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: paused = not paused
            if event.key == pygame.K_LCTRL: togglescroll = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LCTRL: togglescroll = True

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
        
    render_wireframe_wshells(shapes, screen, tuning, target_w, WIDTH, HEIGHT, font)


        
    instructions1 = font.render(f"CTRL + SCROLL to adjust Target W-Slice", True, (200, 200, 200))
    instructions2 = font.render(f"Target W: {target_w:.1f}", True, (255, 255, 100))
    screen.blit(instructions1, (20, HEIGHT - 180))
    screen.blit(instructions2, (20, HEIGHT - 150))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
