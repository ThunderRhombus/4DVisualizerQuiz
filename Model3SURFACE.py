import pygame
import numpy
import math as m
from Cube import Cube
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
pygame.display.set_caption("3D Surface Rectangles")
clock = pygame.time.Clock()

size = 100
tuning = 0.25
cube1 = Cube(size, 200, 0, 0)
cube2 = Cube(size, -200, 0, 0)
yaw = 0
pitch = 0
roll = 0
dz = 5

yslider = Slider(50, HEIGHT - 80, 200, 16, -180, 180, yaw, "Yaw")
pslider = Slider(300, HEIGHT - 80, 200, 16, -180, 180, pitch, "Pitch")
rslider = Slider(550, HEIGHT - 80, 200, 16, -180, 180, roll, "Roll")
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
        surface = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
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
                
            # Keep track of active edges and their original positions this tick
            edge_moves = []
            
            i = 0
            while i < len(edges):
                e = edges[i]
                at = e.at.copy()
                e.moveto(current_z)
                
                # We need the previous "at" and current "e.at" mapping
                edge_moves.append((e, at, e.at.copy()))
                
                if current_z >= e.target[2]:
                    edges.pop(i)
                    if e.target_index in state['remaining_vertices']:
                        newedges = state['branchpoint'](e.target_index, state['remaining_vertices'])
                        state['remaining_vertices'].remove(e.target_index)
                        edges.extend(newedges)
                    continue
                i += 1
                            
            shape = state['shape']
            
            # Reconstruct the moving edge pairs belonging to the same face to draw a moving surface boundary
            move_map = { (-em[0].link_index - 1): em for em in edge_moves }
            
            for face_idx in range(shape.faces.lastlink):
                face_link = -(face_idx + 1)
                if face_link not in shape.faces.adj: continue
                
                edges_of_face = shape.faces.neighbors(face_link)
                
                moved_in_face = [move_map[e_idx] for e_idx in edges_of_face if e_idx in move_map]
                
                if len(moved_in_face) >= 2:
                    points = []
                    for e_obj, at_pt, eat_pt in moved_in_face:
                        points.append((WIDTH//2 + round(at_pt[0]), HEIGHT//2 + round(at_pt[1])))
                        points.append((WIDTH//2 + round(eat_pt[0]), HEIGHT//2 + round(eat_pt[1])))
                        
                    # Remove duplicates to sanitize points (e.g. vertices)
                    points = list(set(points))
                    
                    if len(points) >= 3:
                        # Centroid tracking
                        cx = sum(p[0] for p in points) / len(points)
                        cy = sum(p[1] for p in points) / len(points)
                        
                        # Sort vertices clockwise by polar angle centered at centroid
                        points.sort(key=lambda p: m.atan2(p[1] - cy, p[0] - cx))
                        
                        # Draw generic polygon boundary handling sweep transitions like corners gracefully
                        pygame.draw.polygon(surface, (c, c, c), points, 0)
                        
                        # Thicker blended boundary to close fractional layout cracks from sweeping interpolation
                        pygame.draw.polygon(surface, (c, c, c), points, 3)
                        
                        contour_c = max(0, c - 20)
                        pygame.draw.polygon(surface, (contour_c, contour_c, contour_c), points, 1)
                    
        screen.blit(surface, (0,0))

shapes = [cube1, cube2]

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
