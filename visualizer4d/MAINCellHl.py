import pygame
import numpy as np
import math as m

class CellHlRenderer:
    def __init__(self, width, height, tuning=0.1, a4=(0.1, 0.0, 0.0)):
        self.WIDTH = width
        self.HEIGHT = height
        self.tuning = tuning
        self.a4 = a4
        self.font = pygame.font.SysFont(None, 24)

    def sort_coplanar_vertices(self, verts_3d):
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

    def get_face_vertices(self, shape, face_link):
        face_edges = list(shape.faces.adj[face_link])
        face_vertices_set = set()
        for e_idx in face_edges:
            for v in shape.edges.adj[-e_idx - 1]:
                if v >= 0: 
                    face_vertices_set.add(v)
        return list(face_vertices_set)

    def render(self, screen, shapes, opacity, cellhl, cell_colors):
        polygons_to_draw = []
                                
        for shape in shapes:
            for v in shape.edges.adj:
                if v < 0:
                    neighbors = list(shape.edges.adj[v])
                    if len(neighbors) == 2:
                        p1 = shape.ov[neighbors[0]]
                        p2 = shape.ov[neighbors[1]]
                        avg_z = (p1[2] + p2[2]) / 2.0
                        g = max(0, min(255, int(127 + avg_z * self.tuning)))
                        
                        polygons_to_draw.append({
                            'z': avg_z,
                            'type': 'line',
                            'p1': (self.WIDTH//2 + round(p1[0]), self.HEIGHT//2 + round(p1[1])),
                            'p2': (self.WIDTH//2 + round(p2[0]), self.HEIGHT//2 + round(p2[1])),
                            'c1': (max(0, g-30), max(0, g-30), max(0, g-30)),
                            'c2': (g, g, g)
                        })
                        
            if hasattr(shape, 'cells'):
                for current_cell_idx in list(cellhl):
                    try:
                        cell_faces = shape.cells.neighbors(-current_cell_idx - 1)
                    except (KeyError, AttributeError):
                        continue
                    
                    for cell_face_mapped in cell_faces:
                        face_link = -cell_face_mapped - 1
                        face_vertices = self.get_face_vertices(shape, face_link)
                        vs_3d = [shape.ov[idx][:3] for idx in face_vertices]
                        sorted_rel_idx = self.sort_coplanar_vertices(vs_3d)
                        
                        ordered_pts = []
                        avg_z = 0
                        for sv in sorted_rel_idx:
                            idx = face_vertices[sv]
                            ordered_pts.append((self.WIDTH//2 + round(shape.ov[idx][0]), self.HEIGHT//2 + round(shape.ov[idx][1])))
                            avg_z += shape.ov[idx][2]
                        avg_z /= len(face_vertices)
                        
                        g = max(0, min(255, int(127 + avg_z * self.tuning)))
                        base_c = cell_colors.get(current_cell_idx, (180, 180, 180))
                        intensity = g / 255.0
                        alpha = int(255 * opacity * 0.35) 
                        alpha = max(0, min(255, alpha))
                        color = (int(base_c[0]*intensity), int(base_c[1]*intensity), int(base_c[2]*intensity), alpha)
                        
                        polygons_to_draw.append({
                            'z': avg_z,
                            'type': 'poly',
                            'pts': ordered_pts,
                            'color': color
                        })
                        
        polygons_to_draw.sort(key=lambda item: item['z'])
        
        for item in polygons_to_draw:
            if item['type'] == 'line':
                pygame.draw.line(screen, item['c1'], item['p1'], item['p2'], 3)
                pygame.draw.line(screen, item['c2'], item['p1'], item['p2'], 1)
            elif item['type'] == 'poly':
                pts = item['pts']
                if len(pts) >= 3:
                    min_x = min(p[0] for p in pts)
                    max_x = max(p[0] for p in pts)
                    min_y = min(p[1] for p in pts)
                    max_y = max(p[1] for p in pts)
                    w_bound = max_x - min_x
                    h_bound = max_y - min_y
                    if w_bound > 0 and h_bound > 0:
                        target_surf = pygame.Surface((w_bound, h_bound), pygame.SRCALPHA)
                        local_pts = [(p[0] - min_x, p[1] - min_y) for p in pts]
                        pygame.draw.polygon(target_surf, item['color'], local_pts, 0)
                        screen.blit(target_surf, (min_x, min_y))
                        
        # 2. Collect Labels into the draw_list for Z-sorting
        draw_list = []
        final_text = []
        for shape in shapes:
            if getattr(shape, 'hastext', False):
                for p in range(len(shape.ov)):
                    text = shape.getText(p)
                    if text:
                        z = shape.ov[p][2]
                        w = shape.ov[p][3]
                        sx = self.WIDTH//2 + round(shape.ov[p][0])
                        sy = self.HEIGHT//2 + round(shape.ov[p][1])
                        
                        g_val = 127 + round(z * self.tuning)
                        d_val = round((w + w) * self.tuning)
                        r_c = max(0, min(255, int(g_val + d_val)))
                        b_c = max(0, min(255, int(g_val - d_val)))
                        g_c = max(0, min(255, int(g_val)))
                        
                        draw_list.append({
                            'z': z,
                            'type': 'circle',
                            'pos': (sx, sy),
                            'color': (r_c, g_c, b_c)
                        })
                        final_text.append({'text': text, 'pos': (sx, sy)})

        draw_list.sort(key=lambda x: x['z'])
        
        for item in draw_list:
            if item['type'] == 'poly':
                # ... (poly drawing)
                pts = item['pts']
                min_x, max_x = min(p[0] for p in pts) - 5, max(p[0] for p in pts) + 5
                min_y, max_y = min(p[1] for p in pts) - 5, max(p[1] for p in pts) + 5
                w_bd, h_bd = max_x - min_x, max_y - min_y
                if w_bd > 0 and h_bd > 0:
                    tsurf = pygame.Surface((w_bd, h_bd), pygame.SRCALPHA)
                    local_pts = [(p[0] - min_x, p[1] - min_y) for p in pts]
                    pygame.draw.polygon(tsurf, item['color'], local_pts, 0)
                    screen.blit(tsurf, (min_x, min_y))
            elif item['type'] == 'circle':
                pygame.draw.circle(screen, item['color'], item['pos'], 10)

        # Draw Labels on TOP
        for lbl in final_text:
            text_surf = self.font.render(lbl['text'], True, (255, 255, 255))
            screen.blit(text_surf, (lbl['pos'][0] - text_surf.get_width()//2, lbl['pos'][1] - text_surf.get_height()//2))

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

def main(a4=(0.1, 0.0, 0.0)):
    from Tesseract import Tesseract
    from origin_viewer import spawn_origin_viewer
    
    shared_arr = spawn_origin_viewer()
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Modular Cell Highlight Renderer")
    clock = pygame.time.Clock()

    renderer = CellHlRenderer(WIDTH, HEIGHT, a4=a4)
    tess = Tesseract(100, 0.001, 0, 0, 0, 0)
    shapes = [tess]
    
    opacity = 1.0
    yaw, pitch, roll, dip, tuck, skew = 0, 0, 0, 0, 0, 0
    dragging = False
    xsens, ysens = WIDTH/180, HEIGHT/180
    dy, dr = 0, 0
    d4 = 0
    paused = False
    togglescroll = True
    font = pygame.font.SysFont(None, 24)

    cell_buttons = []
    button_labels = ["+x", "-x", "+y", "-y", "+z", "-z", "+w", "-w"]
    label_to_cell = {"+x": 4, "-x": 6, "+y": 5, "-y": 3, "+z": 7, "-z": 2, "+w": 1, "-w": 0}
    cell_colors = {
        0: (150, 150, 0), 1: (255, 255, 100), 2: (0, 0, 150), 3: (0, 150, 0),
        4: (255, 100, 100), 5: (100, 255, 100), 6: (150, 0, 0), 7: (100, 100, 255),
    }
    for idx, label in enumerate(button_labels):
        cell_buttons.append(ToggleButton(WIDTH-50, 40 + idx*40, 30, 30, label, cell_colors[label_to_cell[label]]))

    running = True
    while running:
        cells = set()
        for i, label in enumerate(button_labels):
            if cell_buttons[i].getsel(): cells.add(label_to_cell[label])

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            for b in cell_buttons: b.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                dragging = True
                lastx, lasty = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                vx = (pygame.mouse.get_pos()[0] - lastx) / xsens
                vy = (pygame.mouse.get_pos()[1] - lasty) / ysens
                if abs(vx) > abs(vy) and abs(vx) > 0.1: dy = vx; dr = 0
                elif abs(vy) > 0.1: dr = vy; dy = 0
                else: dr, dy = 0, 0
            elif event.type == pygame.MOUSEMOTION and dragging:
                mx, my = event.pos
                yaw -= (mx - lastx) / xsens
                roll -= (my - lasty) / ysens
                lastx, lasty = mx, my
                dr, dy = 0, 0

            if event.type == pygame.MOUSEWHEEL:
                if togglescroll: d4 = -event.y * 3
                else: opacity = max(0.0, min(1.0, opacity + event.y * 0.05))

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
        
        renderer.render(screen, shapes, opacity, cells, cell_colors)
        for b in cell_buttons: b.draw(screen, font)

        shared_arr[:] = [yaw, pitch, roll, dip, tuck, skew, 0.001]
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == '__main__':
    main()
