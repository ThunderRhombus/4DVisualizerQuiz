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

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rotating Multi-Shape Scene")
clock = pygame.time.Clock()

size = 100
tuning = 0.1
ortho = 0.001
tess = Tesseract(size, ortho, 0, 0, 0, 0)
yaw = 0
pitch = 0
roll = 0
dip = 0
tuck = 0
skew = 0

dz = 1

yslider = Slider(50, HEIGHT - 40, 300, 16, -180, 180, yaw, "Yaw")
pslider = Slider(50, HEIGHT - 100, 300, 16, -180, 180, pitch, "Pitch")
rslider = Slider(50, HEIGHT - 160, 300, 16, -180, 180, roll, "Roll")
dslider = Slider(450, HEIGHT - 40, 300, 16, -180, 180, dip, "Dip")
tslider = Slider(450, HEIGHT - 100, 300, 16, -180, 180, tuck, "Tuck")
sslider = Slider(450, HEIGHT - 160, 300, 16, -180, 180, skew, "Skew")
font = pygame.font.SysFont(None, 24)



def render_shapes(shapes, screen, dz, tuning):
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
                d = round(((at[3] + e.at[3]))*tuning)
                r = g + d
                b = g - d
                pygame.draw.line(screen, (r,g-30,b),
                                 (WIDTH//2 + round(at[0]), HEIGHT//3 + round(at[1])),
                                 (WIDTH//2 + round(e.at[0]), HEIGHT//3 + round(e.at[1])),
                                 9)
                pygame.draw.line(screen, (r,g,b),
                                 (WIDTH//2 + round(at[0]), HEIGHT//3 + round(at[1])),
                                 (WIDTH//2 + round(e.at[0]), HEIGHT//3 + round(e.at[1])),
                                 5)
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


shapes = [tess]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        yslider.handle_event(event)
        pslider.handle_event(event)
        rslider.handle_event(event)
        dslider.handle_event(event)
        tslider.handle_event(event)
        sslider.handle_event(event)
    
    screen.fill((0, 0, 0))
    
    yaw = yslider.value
    pitch = pslider.value
    roll = rslider.value
    dip = dslider.value
    tuck = tslider.value
    skew = sslider.value

    for shape in shapes:
        shape.rotate(yaw, pitch, roll, dip, tuck, skew)
        
    render_shapes(shapes, screen, dz, tuning)

    
    yslider.draw(screen, font)
    pslider.draw(screen, font)
    rslider.draw(screen, font)
    dslider.draw(screen, font)
    tslider.draw(screen, font)
    sslider.draw(screen, font)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()