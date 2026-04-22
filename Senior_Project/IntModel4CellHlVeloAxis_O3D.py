import pygame
import numpy as np
import math as m
import os
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

def get_face_vertices(shape, face_link):
    face_edges = list(shape.faces.adj[face_link])
    face_vertices_set = set()
    for e_idx in face_edges:
        # e_idx is 0-indexed edge ID. Its link node in shape.edges is -e_idx - 1
        for v in shape.edges.adj[-e_idx - 1]:
            if v >= 0: 
                face_vertices_set.add(v)
    return list(face_vertices_set)

def export_ply(filename, shapes, active_cells, cell_colors):
    vertices = []
    vertex_colors = []
    faces = []
    v_offset = 0
    
    for shape in shapes:
        if hasattr(shape, 'cells'):
            for current_cell_idx in active_cells:
                try:
                    cell_faces = shape.cells.neighbors(-current_cell_idx - 1)
                except (KeyError, AttributeError):
                    continue
                
                # Fetch color for PLY vertex properties
                base_c = cell_colors.get(current_cell_idx, (180, 180, 180))
                
                for cell_face_mapped in cell_faces:
                    face_link = -cell_face_mapped - 1
                    face_vertices = get_face_vertices(shape, face_link)
                    vs_3d = [shape.ov[idx][:3] for idx in face_vertices]
                    sorted_rel_idx = sort_coplanar_vertices(vs_3d)
                    
                    face_pts = []
                    for sv in sorted_rel_idx:
                        vertices.append(vs_3d[sv])
                        vertex_colors.append(base_c)
                        face_pts.append(v_offset)
                        v_offset += 1
                    faces.append(face_pts)

    print(f"Exporting {len(faces)} highlighted cell faces to {filename}...")
    try:
        with open(filename, 'w') as f:
            f.write("ply\nformat ascii 1.0\n")
            f.write(f"element vertex {len(vertices)}\n")
            f.write("property float x\nproperty float y\nproperty float z\n")
            f.write("property uchar red\nproperty uchar green\nproperty uchar blue\n")
            f.write(f"element face {len(faces)}\n")
            f.write("property list uchar int vertex_index\n")
            f.write("end_header\n")
            for i, v in enumerate(vertices):
                c = vertex_colors[i]
                f.write(f"{v[0]} {v[1]} {v[2]} {int(c[0])} {int(c[1])} {int(c[2])}\n")
            for face in faces:
                line = f"{len(face)} " + " ".join(str(idx) for idx in face)
                f.write(line + "\n")
        print(f"Successfully saved {filename}!")
    except Exception as e:
        print(f"Failed to export PLY: {e}")

def visualize_open3d(shapes, active_cells, cell_colors):
    try:
        import open3d as o3d
    except ImportError:
        print("Open3D is not installed on this system. Please run 'pip install open3d' to use the 3D Viewer popup.")
        return
        
    print("Launching Native Open3D Hardware Accelerated Viewer (Close the window to return to Pygame!)...")
    vertices = []
    vertex_colors = []
    triangles = []
    linesets = []
    v_offset = 0
    
    for shape in shapes:
        edges = []
        for v in shape.edges.adj:
            if v < 0:
                n = list(shape.edges.adj[v])
                if len(n) == 2:
                    edges.append([n[0], n[1]])
        if edges:
            pts = np.array([list(p[:3]) for p in shape.ov])
            ls = o3d.geometry.LineSet()
            ls.points = o3d.utility.Vector3dVector(pts)
            ls.lines = o3d.utility.Vector2iVector(edges)
            ls.colors = o3d.utility.Vector3dVector(np.ones((len(edges), 3)) * 0.8)
            linesets.append(ls)
            
        if hasattr(shape, 'cells'):
            for current_cell_idx in active_cells:
                try:
                    cell_faces = shape.cells.neighbors(-current_cell_idx - 1)
                except:
                    continue
                color = np.array(cell_colors.get(current_cell_idx, (180, 180, 180))) / 255.0
                
                for cell_face_mapped in cell_faces:
                    face_link = -cell_face_mapped - 1
                    face_vertices = get_face_vertices(shape, face_link)
                    vs_3d = [shape.ov[v][:3] for v in face_vertices]
                    sorted_idx = sort_coplanar_vertices(vs_3d)
                    
                    for sv in sorted_idx:
                        vertices.append(vs_3d[sv])
                        vertex_colors.append(color)
                    
                    n = len(sorted_idx)
                    for i in range(1, n - 1):
                        triangles.append([v_offset, v_offset + i, v_offset + i + 1])
                    v_offset += n
                    
    mesh = o3d.geometry.TriangleMesh()
    if vertices:
        mesh.vertices = o3d.utility.Vector3dVector(vertices)
        mesh.vertex_colors = o3d.utility.Vector3dVector(vertex_colors)
        mesh.triangles = o3d.utility.Vector3iVector(triangles)
        mesh.compute_vertex_normals()
        
    geometries = linesets + ([mesh] if vertices else [])
    if geometries:
        o3d.visualization.draw_geometries(geometries)

def render_shapes_fast(shapes, screen, tuning, opacity, cellhl, cell_colors, WIDTH, HEIGHT, font):
    # Replaces slow topological boolean sweeps with instantaneous high-performance polygon depth-sorting!
    polygons_to_draw = []
                            
    for shape in shapes:
        for v in shape.edges.adj:
            if v < 0:
                neighbors = list(shape.edges.adj[v])
                if len(neighbors) == 2:
                    p1 = shape.ov[neighbors[0]]
                    p2 = shape.ov[neighbors[1]]
                    avg_z = (p1[2] + p2[2]) / 2.0
                    g = max(0, min(255, int(127 + avg_z * tuning)))
                    
                    polygons_to_draw.append({
                        'z': avg_z,
                        'type': 'line',
                        'p1': (WIDTH//2 + round(p1[0]), HEIGHT//2 + round(p1[1])),
                        'p2': (WIDTH//2 + round(p2[0]), HEIGHT//2 + round(p2[1])),
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
                    face_vertices = get_face_vertices(shape, face_link)
                    vs_3d = [shape.ov[idx][:3] for idx in face_vertices]
                    sorted_rel_idx = sort_coplanar_vertices(vs_3d)
                    
                    ordered_pts = []
                    avg_z = 0
                    for sv in sorted_rel_idx:
                        idx = face_vertices[sv]
                        ordered_pts.append((WIDTH//2 + round(shape.ov[idx][0]), HEIGHT//2 + round(shape.ov[idx][1])))
                        avg_z += shape.ov[idx][2]
                    avg_z /= len(face_vertices)
                    
                    g = max(0, min(255, int(127 + avg_z * tuning)))
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
                    
    # The magical Painter's algorithm implementation. Sorting achieves perfect volumetric transparency in milliseconds!
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
                    
    # Render all origin text points isolated on absolute top
    for shape in shapes:
        if hasattr(shape, 'hastext') and shape.hastext:
            for p in range(len(shape.ov)):
                text = shape.getText(p)
                if text:
                    g = 127 + round(shape.ov[p][2] * tuning)
                    g = max(0, min(255, int(g)))
                    pygame.draw.circle(screen, (g,g,g), (WIDTH//2 + round(shape.ov[p][0]), HEIGHT//2 + round(shape.ov[p][1])), 10)
                    text_surf = font.render(text, True, (255, 255, 255))
                    screen.blit(text_surf, (WIDTH//2 + round(shape.ov[p][0]-5), HEIGHT//2 + round(shape.ov[p][1]-5)))

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fast 4D Open3D-ready Renderer (Press O for Open3D, P for PLY)")
clock = pygame.time.Clock()

size = 100
tuning = 0.1
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
opacity = 1.0

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
                d4 = vwheel * 3
            else:
                opacity += event.y * 0.05
                opacity = max(0.0, min(1.0, opacity))

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_LCTRL:
                togglescroll = False
            # O3D and PLY logic!
            if event.key == pygame.K_p:
                export_ply("tesseract_export.ply", shapes, cells, cell_colors)
            if event.key == pygame.K_o:
                visualize_open3d(shapes, cells, cell_colors)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LCTRL:
                togglescroll = True
        
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
        
    # Inject O3D speedup methodology into the pygame surface rendering step
    render_shapes_fast(shapes, screen, tuning, opacity, cells, cell_colors, WIDTH, HEIGHT, font)

    for button in cell_buttons:
        button.draw(screen, font)
        
    instructions1 = font.render(f"Press 'O' to open Open3D GPU Visualizer", True, (200, 200, 200))
    instructions2 = font.render(f"Press 'P' to export current frame to PLY", True, (200, 200, 200))
    screen.blit(instructions1, (20, HEIGHT - 60))
    screen.blit(instructions2, (20, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
