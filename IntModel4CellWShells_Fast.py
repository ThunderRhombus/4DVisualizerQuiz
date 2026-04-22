import pygame
import numpy as np
import math as m
from Tesseract import Tesseract
from Edge import Edge
from wAxis import wAxis

class ToggleButton:
    def __init__(self, x, y, w, h, label, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.selected = False
        self.base_color = color

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.selected = not self.selected

    def draw(self, surf, font):
        color = self.base_color if self.selected else (60, 60, 60)
        pygame.draw.rect(surf, color, self.rect)
        pygame.draw.rect(surf, (180, 180, 180), self.rect, 2)
        label_surf = font.render(self.label, True, (240, 240, 240))
        label_rect = label_surf.get_rect(center=self.rect.center)
        surf.blit(label_surf, label_rect)

    def getsel(self):
        return self.selected

# Advanced mathematical polygon cyclic sort for un-ordered planar face projections
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

def get_cell_edges(shape, cell_idx):
    try:
        cell_faces = shape.cells.neighbors(-cell_idx - 1)
    except (KeyError, AttributeError):
        return []
    unique_edges = set()
    for f in cell_faces:
        face_link = -f - 1
        for e_idx in shape.faces.adj[face_link]:
            unique_edges.add(e_idx)
    return list(unique_edges)

def get_edge_vertices(shape, e_idx):
    verts = [v for v in shape.edges.adj[-e_idx - 1] if v >= 0]
    return verts[0], verts[1]

def render_w_shells(shapes, screen, tuning, target_w, cellhl, cell_colors, WIDTH, HEIGHT, font):
    draw_list = []
    
    # 1. Provide a faint global wireframe for background architectural context
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
            avg_w = (p1[3] + p2[3]) / 2.0
            
            # Use original r-b gradient math to retain accurate coloring
            g_val = 127 + avg_z * tuning
            d_val = (avg_w * 2) * tuning
            
            r_c = max(0, min(255, int(g_val + d_val)))
            b_c = max(0, min(255, int(g_val - d_val)))
            g_c = max(0, min(255, int(g_val)))
            
            # Faint background alpha
            color = (r_c, max(0, g_c-30), b_c, 35)
            
            draw_list.append({
                'z': avg_z,
                'type': 'global_line',
                'p1': (WIDTH//2 + round(p1[0]), HEIGHT//2 + round(p1[1])),
                'p2': (WIDTH//2 + round(p2[0]), HEIGHT//2 + round(p2[1])),
                'color': color,
                'thickness': 2
            })
            
    # 2. Sweep localized W planes to generate layered translucent 3D solid shells
    w_shells_radius = 7 
    w_step = 10.0
    
    for shell_offset in range(-w_shells_radius, w_shells_radius + 1):
        W_slice = target_w + shell_offset * w_step
        dist = abs(shell_offset)
        max_dist = w_shells_radius
        
        # Mapping distance to opacity. Exactly at target_w = fully opaque.
        opacity_factor = 1.0 - (dist / float(max_dist + 1e-5))
        if opacity_factor <= 0: continue
        
        for shape in shapes:
            if not hasattr(shape, 'cells'): continue
            
            for current_cell_idx in list(cellhl):
                cell_edges = get_cell_edges(shape, current_cell_idx)
                
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
                            
                # Unique intersection points mapping
                unique_pts = []
                for p in intersection_pts:
                    if not any(sum(abs(p[j] - u[j]) for j in range(3)) < 1e-4 for u in unique_pts):
                        unique_pts.append(p)
                        
                # A 3D planar slice intersecting a 3D Cell (cuboid volume bounds) forms a strict convex 2D polygon!
                if len(unique_pts) >= 3:
                    vs_3d = [u[:3] for u in unique_pts]
                    sorted_idx = sort_coplanar_vertices(vs_3d)
                    
                    avg_z = sum(vs_3d[i][2] for i in sorted_idx) / len(sorted_idx)
                    ordered_pts_2d = [(WIDTH//2 + round(unique_pts[i][0]), HEIGHT//2 + round(unique_pts[i][1])) for i in sorted_idx]
                    
                    base_c = cell_colors.get(current_cell_idx, (180, 180, 180))
                    g_z = 127 + avg_z * tuning
                    intensity = max(0, min(255, g_z)) / 255.0
                    alpha = int(255 * opacity_factor)
                    
                    fill_color = (int(base_c[0]*intensity), int(base_c[1]*intensity), int(base_c[2]*intensity), alpha)
                    outline_alpha = min(255, int(alpha * 1.5))
                    outline_color = (int(base_c[0]*intensity), int(base_c[1]*intensity), int(base_c[2]*intensity), outline_alpha)
                    
                    draw_list.append({
                        'z': avg_z,
                        'type': 'poly',
                        'pts': ordered_pts_2d,
                        'color': fill_color,
                        'outline_color': outline_color
                    })
                    
    # Painter's Algorithm sorts all wireframes and multiple W-shells flawlessly together by Depth Z
    draw_list.sort(key=lambda item: item['z'])
    
    for item in draw_list:
        if item['type'] == 'global_line':
            p1 = item['p1']
            p2 = item['p2']
            min_x = min(p1[0], p2[0]) - 5
            max_x = max(p1[0], p2[0]) + 5
            min_y = min(p1[1], p2[1]) - 5
            max_y = max(p1[1], p2[1]) + 5
            w_bd = max_x - min_x
            h_bd = max_y - min_y
            if w_bd > 0 and h_bd > 0:
                tsurf = pygame.Surface((w_bd, h_bd), pygame.SRCALPHA)
                pygame.draw.line(tsurf, item['color'], (p1[0] - min_x, p1[1] - min_y), (p2[0] - min_x, p2[1] - min_y), item['thickness'])
                screen.blit(tsurf, (min_x, min_y))
                
        elif item['type'] == 'poly':
            pts = item['pts']
            min_x = min(p[0] for p in pts) - 2 # padding
            max_x = max(p[0] for p in pts) + 2
            min_y = min(p[1] for p in pts) - 2
            max_y = max(p[1] for p in pts) + 2
            w_bound = max_x - min_x
            h_bound = max_y - min_y
            if w_bound > 0 and h_bound > 0:
                target_surf = pygame.Surface((w_bound, h_bound), pygame.SRCALPHA)
                local_pts = [(p[0] - min_x, p[1] - min_y) for p in pts]
                pygame.draw.polygon(target_surf, item['color'], local_pts, 0)
                pygame.draw.polygon(target_surf, item['outline_color'], local_pts, 2)
                screen.blit(target_surf, (min_x, min_y))

    # Render isolated origins
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
                    
                    pygame.draw.circle(screen, (r_c, g_c, b_c), (WIDTH//2 + round(shape.ov[p][0]), HEIGHT//2 + round(shape.ov[p][1])), 10)
                    text_surf = font.render(text, True, (255, 255, 255))
                    screen.blit(text_surf, (WIDTH//2 + round(shape.ov[p][0]-5), HEIGHT//2 + round(shape.ov[p][1]-5)))

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4D Target-W Slicing Rendering Shells")
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
target_w = 0.0 # NEW explicit dynamic W-target

font = pygame.font.SysFont(None, 24)

cell_buttons = []
button_width = 30
button_height = 30
button_x = WIDTH - button_width - 20
button_y = 40
button_gap = 10
button_labels = ["+x", "-x", "+y", "-y", "+z", "-z", "+w", "-w"]
label_to_cell = {"+x": 4, "-x": 6, "+y": 5, "-y": 3, "+z": 7, "-z": 2, "+w": 1, "-w": 0}
cell_colors = {
    0: (150, 150, 0),
    1: (255, 255, 100),
    2: (0, 0, 150),
    3: (0, 150, 0),
    4: (255, 100, 100),
    5: (100, 255, 100),
    6: (150, 0, 0),
    7: (100, 100, 255),
}
for idx, label in enumerate(button_labels):
    y = button_y + idx * (button_height + button_gap)
    cell_idx = label_to_cell[label]
    cell_buttons.append(ToggleButton(button_x, y, button_width, button_height, label, cell_colors[cell_idx]))

running = True
while running:
    cells = set()
    for i in range(8):
        if cell_buttons[i].getsel(): cells.add(label_to_cell[button_labels[i]])

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
                target_w += event.y * 10.0 # Target explicit W translation via CTRL + Scroll!

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: paused = not paused
            if event.key == pygame.K_LCTRL: togglescroll = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LCTRL: togglescroll = True
        
        for button in cell_buttons:
            button.handle_event(event)
    
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
        
    render_w_shells(shapes, screen, tuning, target_w, cells, cell_colors, WIDTH, HEIGHT, font)

    for button in cell_buttons:
        button.draw(screen, font)
        
    instructions1 = font.render(f"CTRL + SCROLL to adjust Target W-Slice", True, (200, 200, 200))
    instructions2 = font.render(f"Target W: {target_w:.1f}", True, (255, 255, 100))
    screen.blit(instructions1, (20, HEIGHT - 60))
    screen.blit(instructions2, (20, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
