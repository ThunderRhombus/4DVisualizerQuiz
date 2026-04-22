from pydoc import text

import pygame
import numpy
import math as m
from Tesseract import Tesseract
from Edge import Edge
from wAxis import wAxis

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

yslider = Slider(50, HEIGHT - 40, 300, 16, -180, 180, yaw, "Yaw")
pslider = Slider(50, HEIGHT - 100, 300, 16, -180, 180, pitch, "Pitch")
rslider = Slider(50, HEIGHT - 160, 300, 16, -180, 180, roll, "Roll")
dslider = Slider(450, HEIGHT - 40, 300, 16, -1, 1, dip, "XW Rotation Speed")
tslider = Slider(450, HEIGHT - 100, 300, 16, -1, 1, tuck, "ZW Rotation Speed")
sslider = Slider(450, HEIGHT - 160, 300, 16, -1, 1, skew, "YW Rotation Speed")
font = pygame.font.SysFont(None, 24)



def render_shapes(shapes, screen, dz, tuning):
    shape_states = []
    min_z = 300


    for shape in shapes:
        remaining_vertices = set(range(len(shape.v)))
        zsortvert = sorted(range(len(shape.ov)), key=lambda i: shape.ov[i][2], reverse=True)
        if not zsortvert: continue
        p = zsortvert[-1]
        if shape.hastext:
            text = shape.getText(p)
            g = 127 + round(shape.ov[p][2] * tuning)
            d = round(((shape.ov[p][3] + shape.ov[p][3]))*tuning)
            r = g + d
            b = g - d
            if text:
                pygame.draw.circle(screen, (r,g,b), (WIDTH//2 + round(shape.ov[p][0]), HEIGHT//2 + round(shape.ov[p][1])), 10)
                text_surf = font.render(text, True, (255, 255, 255))
                screen.blit(text_surf, (WIDTH//2 + round(shape.ov[p][0]-5), HEIGHT//2 + round(shape.ov[p][1]-5)))

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
            if not edges and state['remaining_vertices']:
                next_vertex_idx = min(
                    state['remaining_vertices'],
                    key=lambda idx: state['shape'].ov[idx][2]
                )
                if state['shape'].ov[next_vertex_idx][2] <= current_z:
                    newedges = state['branchpoint'](next_vertex_idx, state['remaining_vertices'])
                    state['remaining_vertices'].remove(next_vertex_idx)
                    edges.extend(newedges)
                    if state['shape'].hastext:
                        text = state['shape'].getText(next_vertex_idx)
                        if text:
                            pygame.draw.circle(screen, (g,g,g), (WIDTH//2 + round(state['shape'].ov[next_vertex_idx][0]), HEIGHT//2 + round(state['shape'].ov[next_vertex_idx][1])), 10)
                            text_surf = font.render(text, True, (255, 255, 255))
                            screen.blit(text_surf, (WIDTH//2 + round(state['shape'].ov[next_vertex_idx][0])-5, HEIGHT//2 + round(state['shape'].ov[next_vertex_idx][1])-5))
            
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
                                 (WIDTH//2 + round(at[0]), HEIGHT//2 + round(at[1])),
                                 (WIDTH//2 + round(e.at[0]), HEIGHT//2 + round(e.at[1])),
                                 9)
                pygame.draw.line(screen, (r,g,b),
                                 (WIDTH//2 + round(at[0]), HEIGHT//2 + round(at[1])),
                                 (WIDTH//2 + round(e.at[0]), HEIGHT//2 + round(e.at[1])),
                                 5)
                if numpy.array_equal(e.at, e.target):
                    edges.pop(i)
                    if e.target_index in state['remaining_vertices']:
                        newedges = state['branchpoint'](e.target_index, state['remaining_vertices'])
                        state['remaining_vertices'].remove(e.target_index)
                        edges.extend(newedges)
                        if state['shape'].hastext:
                            text = state['shape'].getText(e.target_index)
                            if text:
                                pygame.draw.circle(screen, (r,g,b), (WIDTH//2 + round(e.at[0]), HEIGHT//2 + round(e.at[1])), 10)
                                text_surf = font.render(text, True, (255, 255, 255))
                                screen.blit(text_surf, (WIDTH//2 + round(e.at[0])-5, HEIGHT//2 + round(e.at[1])-5))
                    continue
                i += 1
        
    '''for shape in shapes:
        for v in shape.rv: 
            zc = 127 + round(v[2]*tuning)
            zc = max(0, min(255, zc))
            radius = 5 + round(v[2] / shape.size) if shape.size > 0 else 5
            radius = max(1, radius)
            pygame.draw.circle(screen, (zc, zc, zc), (WIDTH//2 + round(v[0]), HEIGHT//2 + round(v[1])), radius)'''


shapes = [tess, axis]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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
                d4 = vwheel * 5
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
        
        # Wrap angles to prevent unbounded growth (0-360 range)
        dip = dip % 360
        tuck = tuck % 360
        skew = skew % 360

    for shape in shapes:
        shape.rotate(yaw, pitch, roll, dip, tuck, skew)
        shape.shrink(ortho)
        
    render_shapes(shapes, screen, dz, tuning)

   

    pygame.display.flip()
    clock.tick(60)

pygame.quit()