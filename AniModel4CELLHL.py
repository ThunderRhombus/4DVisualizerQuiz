import pygame
import numpy
import math as m
from Tesseract import Tesseract
from Edge import Edge


class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial, label=""):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)
        self.min = min_val
        self.max = max_val
        self.value = float(initial)
        self.label = label
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._set_value_from_pos(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_value_from_pos(event.pos[0])

    def _set_value_from_pos(self, mx):
        t = (mx - self.x) / float(self.w)
        t = max(0.0, min(1.0, t))
        self.value = self.min + t * (self.max - self.min)

    def draw(self, surf, font):
        pygame.draw.rect(surf, (80, 80, 80), self.rect)
        t = (self.value - self.min) / float(self.max - self.min)
        handle_x = int(self.x + t * self.w)
        handle_y = self.y + self.h // 2
        pygame.draw.circle(surf, (200, 200, 200), (handle_x, handle_y), 10)
        label_surf = font.render(f"{self.label}: {self.value:.2f}", True, (220, 220, 220))
        surf.blit(label_surf, (self.x, self.y - 22))


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

    def toggle(self):
        self.selected = True



pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rotating Multi-Shape Scene")
clock = pygame.time.Clock()

size = 100
tuning = 0.1
ortho = 0.0002
tess = Tesseract(size, ortho, 0, 0, 0, 0)
yaw = 90
pitch = 20
roll = 10
dip = 0
tuck = 0
skew = 0
dr = 0.3
dt = 1.5

dz = 1

alphaslider = Slider(50, HEIGHT - 160, 150, 16, 0, 1, 0.5, "Opacity")
drslider = Slider(50, HEIGHT - 100, 150, 16, 0, 1, dr, "3D Rotation Speed")
dtslider = Slider(50, HEIGHT - 40, 150, 16, 0, 3, dt, "4D Rotation Speed")
font = pygame.font.SysFont(None, 24)

cells = set()
cell_buttons = []
button_width = 30
button_height = 30
button_x = WIDTH - button_width - 20
button_y = 40
button_gap = 10
button_labels = ["+x", "-x", "+y", "-y", "+z", "-z", "+w", "-w"]
label_to_cell = {"+x": 4, "-x": 6, "+y": 5, "-y": 3, "+z": 7, "-z": 2, "+w": 1, "-w": 0}
cell_colors = {
    0: (150, 150, 0),   # -w: Dark Yellow
    1: (255, 255, 100), # +w: Yellow
    2: (0, 0, 150),     # -z: Dark Blue
    3: (0, 150, 0),     # -y: Dark Green
    4: (255, 100, 100), # +x: Red
    5: (100, 255, 100), # +y: Green
    6: (150, 0, 0),     # -x: Dark Red
    7: (100, 100, 255), # +z: Blue
}
for idx, label in enumerate(button_labels):
    y = button_y + idx * (button_height + button_gap)
    cell_idx = label_to_cell[label]
    cell_buttons.append(ToggleButton(button_x, y, button_width, button_height, label, cell_colors[cell_idx]))
cell_buttons[7].toggle()


def render_shapes(shapes, screen, dz, tuning, alpha):
    shape_states = []
    min_z = 300
    for shape in shapes:
        remaining_vertices = set(range(len(shape.v)))
        zsortvert = sorted(range(len(shape.ov)), key=lambda i: shape.ov[i][2], reverse=True)
        if not zsortvert: continue
        p = zsortvert[-1]
        
        z = shape.ov[p][2]
        min_z = min(min_z, z)
        
        def branchpoint(p_idx, vleft, s=shape):
            newedges = set()
            if p_idx in vleft:
                for e in s.edges.neighbors(p_idx):
                    for n in s.edges.neighbors(e):
                        if n != p_idx and n in vleft:
                            newedges.add(Edge(list(s.ov[p_idx]), p_idx, list(s.ov[n]), n, e))
            return newedges

        edges = list(branchpoint(p, remaining_vertices))
        remaining_vertices.remove(p)
        shape_states.append({
            'shape': shape,
            'edges': edges,
            'remaining_vertices': remaining_vertices,
            'branchpoint': branchpoint,
            'z': z
        })

    current_z = min([s['z'] for s in shape_states])

    active = True
    while active:
        current_z += dz
        active = False
        
        g = 127 + round(current_z * tuning)

        for state in shape_states:
            if current_z < state['z']:
                active = True
                continue
                
            edges = state['edges']
            if edges:
                active = True
                
            i = 0
            while i < len(edges):
                e = edges[i]
                at = e.at.copy()
                e.moveto(current_z)
                color_val = max(0, min(255, g))
                pygame.draw.line(screen, (color_val, color_val, color_val),
                                 (WIDTH//2 + round(at[0]), HEIGHT//3 + round(at[1])),
                                 (WIDTH//2 + round(e.at[0]), HEIGHT//3 + round(e.at[1])),
                                 3)
                shadow_val = max(0, color_val - 30)
                pygame.draw.line(screen, (shadow_val, shadow_val, shadow_val),
                                 (WIDTH//2 + round(at[0]), HEIGHT//3 + round(at[1])),
                                 (WIDTH//2 + round(e.at[0]), HEIGHT//3 + round(e.at[1])),
                                 1)
                if numpy.array_equal(e.at, e.target):
                    edges.pop(i)
                    if e.target_index in state['remaining_vertices']:
                        newedges = state['branchpoint'](e.target_index, state['remaining_vertices'])
                        state['remaining_vertices'].remove(e.target_index)
                        edges.extend(newedges)
                    continue
                i += 1
        
            '''for shape in shapes:
            for v in shape.rv: 
            zc = 127 + round(v[2]*tuning)
            zc = max(0, min(255, zc))
            radius = 5 + round(v[2] / shape.size) if shape.size > 0 else 5
            radius = max(1, radius)
            pygame.draw.circle(screen, (zc, zc, zc), (WIDTH//2 + round(v[0]), HEIGHT//2 + round(v[1])), radius)'''
            shape = state['shape']
            cellhl = cells.copy()

            for current_cell_idx in list(cellhl):
                cell_faces = shape.cells.neighbors(-current_cell_idx - 1)
                layerpoly = []
                
                travedges = set()
                for edge in edges:
                    edge_idx = (-edge.link_index) - 1
                    if any((-f - 1) in cell_faces for f in shape.faces.neighbors(edge_idx)):
                        travedges.add(edge)
                        
                while len(travedges) >= 2:
                    curloop = []
                    startedge = travedges.pop()
                    edge_faces = shape.faces.neighbors((-startedge.link_index)-1)
                    valid_faces = [f for f in edge_faces if (-f - 1) in cell_faces]
                    if not valid_faces:
                        continue
                    face = valid_faces[0]
                    
                    neighbors = set()
                    for e in travedges:
                        if -e.link_index-1 in shape.faces.neighbors(face):
                            neighbors.add(e)
                            
                    if len(neighbors) > 1:
                        startpoint = startedge.source
                        curloop.append(startpoint)
                        curpoint = startedge.target
                        while not numpy.array_equal(startpoint, curpoint):
                            found_next = False
                            for e in list(neighbors):
                                if numpy.array_equal(e.source, curpoint):
                                    curloop.append(curpoint)
                                    curpoint = e.target
                                    neighbors.remove(e)
                                    if e in travedges: travedges.remove(e)
                                    found_next = True
                                    break
                                elif numpy.array_equal(e.target, curpoint):
                                    curloop.append(curpoint)
                                    curpoint = e.source
                                    neighbors.remove(e)
                                    if e in travedges: travedges.remove(e)
                                    found_next = True
                                    break
                            if not found_next:
                                break
                        curloop.append(startpoint)
                    else: 
                        if len(neighbors) > 0:
                            startpoint = startedge.at
                            curloop.append(startpoint)
                            curedge = neighbors.pop()
                            curpoint = curedge.at
                            
                            max_iters = len(edges) * 2
                            iters = 0
                            
                            while not numpy.array_equal(startpoint, curpoint) and iters < max_iters:
                                iters += 1
                                faces = shape.faces.neighbors(-curedge.link_index - 1)
                                valid_faces = {f for f in faces if (-f - 1) in cell_faces}
                                valid_faces.discard(face)
                                if len(valid_faces) == 0: break
                                face = valid_faces.pop()
                                
                                found_next = False
                                if -startedge.link_index-1 in shape.faces.neighbors(face):
                                    if curedge in travedges: travedges.remove(curedge)
                                    curloop.append(curpoint)
                                    curedge = startedge
                                    curpoint = curedge.at
                                    found_next = True
                                else:
                                    for e in travedges:
                                        if e != curedge and -e.link_index-1 in shape.faces.neighbors(face):
                                            if curedge in travedges: travedges.remove(curedge)
                                            curloop.append(curpoint)
                                            curedge = e
                                            curpoint = curedge.at
                                            found_next = True
                                            break
                                            
                                if not found_next:
                                    break
                            curloop.append(startpoint)
                    layerpoly.append(curloop)
                
                for loop in layerpoly:
                    if len(loop) > 2:
                        base = cell_colors.get(current_cell_idx, (180, 180, 180))
                        intensity = max(0.0, min(1.0, g / 255.0))
                        color = (int(base[0] * intensity), int(base[1] * intensity), int(base[2] * intensity), int(alpha))
                        
                        pts = [(WIDTH//2 + round(p[0]), HEIGHT//3 + round(p[1])) for p in loop]
                        min_x = min(p[0] for p in pts)
                        max_x = max(p[0] for p in pts)
                        min_y = min(p[1] for p in pts)
                        max_y = max(p[1] for p in pts)
                        
                        w_bound = max_x - min_x
                        h_bound = max_y - min_y
                        if w_bound > 0 and h_bound > 0:
                            target_surf = pygame.Surface((w_bound, h_bound), pygame.SRCALPHA)
                            local_pts = [(p[0] - min_x, p[1] - min_y) for p in pts]
                            pygame.draw.polygon(target_surf, color, local_pts, 0)
                            screen.blit(target_surf, (min_x, min_y))
                
                if current_cell_idx in cellhl:
                    cellhl.remove(current_cell_idx)

shapes = [tess]

running = True
while running:
    cells = set()
    if cell_buttons[0].getsel(): cells.add(4)
    if cell_buttons[1].getsel(): cells.add(6)
    if cell_buttons[2].getsel(): cells.add(5)
    if cell_buttons[3].getsel(): cells.add(3)
    if cell_buttons[4].getsel(): cells.add(7)
    if cell_buttons[5].getsel(): cells.add(2)
    if cell_buttons[6].getsel(): cells.add(1)
    if cell_buttons[7].getsel(): cells.add(0)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        alphaslider.handle_event(event)
        drslider.handle_event(event)
        dtslider.handle_event(event)
        for button in cell_buttons:
            button.handle_event(event)
    
    screen.fill((0, 0, 0))
    
    alpha = alphaslider.value
    dr = drslider.value
    dt = dtslider.value
    
    roll = roll + dr
    tuck = tuck + dt

    for shape in shapes:
        shape.rotate(yaw, pitch, roll, dip, tuck, skew)
        
    render_shapes(shapes, screen, dz, tuning, round(alpha*255))

    
    alphaslider.draw(screen, font)
    drslider.draw(screen, font)
    dtslider.draw(screen, font)
    for button in cell_buttons:
        button.draw(screen, font)

    pygame.display.flip()
    clock.tick(36)

pygame.quit()