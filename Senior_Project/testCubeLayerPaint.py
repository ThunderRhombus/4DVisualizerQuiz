import pygame
import numpy
import math as m
from Cube import Cube
from Edge import Edge

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rotating Cube")
clock = pygame.time.Clock()

size = 100
tuning = 0.5
cube = Cube(size)
yaw = 0
pitch = 0
roll = 0
dz = 1
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))
    cube.rotate(yaw, pitch, roll)

    remaining_targets = set(range(len(cube.v)))
    remaining_count = [3,3,3,3,3,3,3,3]

    p = cube.get_hind_most()
    z = cube.rv[p][2]
    edges = []
    for i in cube.g.neighbors(p):
        edges.append(Edge(cube.rv[p], p, cube.rv[i], i))
    c = 127 + round(z*tuning)

    while len(remaining_targets) > 0:
        pygame.event.pump()
        if not edges:
            break
        c = 127 + round(z*tuning)
        edge_points = []
        current_edges = edges.copy()  # Create a copy of the list to avoid modification during iteration
        for e in current_edges:
            at = e.at.copy()
            e.move(dz)
            edge_points.append((WIDTH//2 + round(at[0]), HEIGHT//2 + round(at[1])))
            if e.at[2] == e.target[2]:
                edges.remove(e)
                remaining_count[e.source_index]-=1
                remaining_count[e.target_index]-=1
                if remaining_count[e.source_index] == 0:
                    remaining_targets.remove(e.source_index)
                if remaining_count[e.target_index] == 0:
                    remaining_targets.remove(e.target_index)
                for i in list(cube.g.neighbors(e.target_index)):
                    if i in remaining_targets:
                        edges.append(Edge(cube.rv[e.target_index], e.target_index, cube.rv[i], i))
                        current_edges.append(edges[-1])
        if len(edge_points) > 2:
            for i in range(len(edge_points)-1):
                point = edge_points[i]
                pygame.draw.line(screen, (c, c, c), (point[0], point[1]), (edge_points[i+1][0], edge_points[i+1][1]), 5+round(z/size))
        if len(edge_points) > 1:
            point = edge_points[-1]
            pygame.draw.line(screen, (c, c, c), (point[0], point[1]), (edge_points[0][0], edge_points[0][1]), 5+round(z/size))
        z+=dz

    yaw += 0.1
    pitch += 0.1
    roll += 0.1
    pygame.display.flip()
    clock.tick(60)
pygame.quit()