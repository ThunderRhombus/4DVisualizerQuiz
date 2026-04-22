import pygame
import numpy
import math as m
from Cube import Cube
from Tetrahedron import Tetrahedron
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
tuning = 0.25
cube = Cube(size, 0, 0, 0)
##tetra = Tetrahedron(size, 0, 0, 0)
yaw = 0
pitch = 0
roll = 0
dz = 5

yslider = Slider(50, HEIGHT - 80, 300, 16, -180, 180, yaw, "Yaw")
pslider = Slider(450, HEIGHT - 80, 300, 16, -180, 180, pitch, "Pitch")
rslider = Slider(50, HEIGHT - 140, 300, 16, -180, 180, roll, "Roll")
font = pygame.font.SysFont(None, 24)

def render_shapes(shapes, screen, dz, tuning, yaw, pitch, roll):
    yaw_rad = m.radians(yaw)
    pitch_rad = m.radians(pitch)
    roll_rad = m.radians(roll)

    cp, sp = m.cos(pitch_rad), m.sin(pitch_rad)
    cy, sy = m.cos(yaw_rad), m.sin(yaw_rad)
    cr, sr = m.cos(roll_rad), m.sin(roll_rad)

    Rx = numpy.array([
        [1, 0, 0],
        [0, cr, -sr],
        [0, sr, cr]
    ])

    Ry = numpy.array([
        [cp, 0, sp],
        [0, 1, 0],
        [-sp, 0, cp]
    ])
    # Yaw (around Z)
    Rz = numpy.array([
        [cy, -sy, 0],
        [sy, cy, 0],
        [0, 0, 1]
    ])
    
    A = Rz @ Ry @ Rx
    min_z = 800
    
    shape_states = []
    
    for shape in shapes:
        remaining_vertices = set(range(len(shape.v)))
        zsortvert = sorted(range(len(shape.rv)), key=lambda i: shape.rv[i][2], reverse=True)
        if not zsortvert: continue
        p = zsortvert[-1]
        
        z = shape.rv[p][2]
        min_z = min(min_z, z)
        
        def branchpoint(p_idx, vleft, s=shape):
            newedges = set()
            if p_idx in vleft:
                for e in s.edges.neighbors(p_idx):
                    for n in s.edges.neighbors(e):
                        if n != p_idx and n in vleft:
                            newedges.add(Edge(list(s.rv[p_idx]), p_idx, list(s.rv[n]), n, e))
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
        
        c = 127 + round(current_z * tuning)
        c = max(0, min(255, c))

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
                pygame.draw.line(screen, (c, c+30, c),
                                 (WIDTH//2 + round(at[0]), HEIGHT//2 + round(at[1])),
                                 (WIDTH//2 + round(e.at[0]), HEIGHT//2 + round(e.at[1])),
                                 5)
                if numpy.array_equal(e.at, e.target):
                    edges.pop(i)
                    if e.target_index in state['remaining_vertices']:
                        newedges = state['branchpoint'](e.target_index, state['remaining_vertices'])
                        state['remaining_vertices'].remove(e.target_index)
                        edges.extend(newedges)
                    continue
                i += 1
                            
            travedges = set()
            for edge in edges: travedges.add(edge)
            layerpoly = []
            shape = state['shape']
            
            while len(travedges) > 2:
                curloop = []
                startedge = travedges.pop()
                face = shape.faces.neighbors((-startedge.link_index)-1).pop()
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
                        while not numpy.array_equal(startpoint, curpoint):
                            faces = shape.faces.neighbors(-curedge.link_index - 1)
                            faces.discard(face)
                            if len(faces) == 0: break
                            face = faces.pop()
                            
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
                    pygame.draw.polygon(screen, (c, c, c), [(WIDTH//2 + round(p[0]), HEIGHT//2 + round(p[1])) for p in loop], 0)
    '''for shape in shapes:
        for v in shape.rv:
            zc = 127 + round(v[2]*tuning)
            zc = max(0, min(255, zc))
            radius = 5 + round(v[2] / shape.size) if shape.size > 0 else 5
            radius = max(1, radius)
            pygame.draw.circle(screen, (zc, zc, zc), (WIDTH//2 + round(v[0]), HEIGHT//2 + round(v[1])), radius)'''


shapes = [cube]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        yslider.handle_event(event)
        pslider.handle_event(event)
        rslider.handle_event(event)
    
    screen.fill((0, 0, 0))
    
    yaw = yslider.value
    pitch = pslider.value
    roll = rslider.value

    for shape in shapes:
        shape.rotate(yaw, pitch, roll)
        
    render_shapes(shapes, screen, dz, tuning, yaw, pitch, roll)

    
    yslider.draw(screen, font)
    pslider.draw(screen, font)
    rslider.draw(screen, font)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()