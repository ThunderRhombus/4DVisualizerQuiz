import pygame
import numpy
import math as m

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rotating Cube")
clock = pygame.time.Clock()

def draw_cube(a,b,c,size):
    v = [    (-size, -size, -size),
                    (size, -size, -size),
                    (size, size, -size),
                    (-size, size, -size),
                    (-size, -size, size),
                    (size, -size, size),
                    (size, size, size),
                    (-size, size, size)]    
    
    edges = [(0, 1), (1, 2), (2, 3), (3, 0),
             (4, 5), (5, 6), (6, 7), (7, 4),
             (0, 4), (1, 5), (2, 6), (3, 7)]
    yaw = m.radians(a)
    pitch = m.radians(b)
    roll = m.radians(c)

    rv = []
    A = numpy.array([[m.cos(yaw) * m.cos(pitch), m.cos(yaw) * m.sin(pitch) * m.sin(roll) - m.sin(yaw) * m.cos(roll), m.cos(yaw) * m.sin(pitch) * m.cos(roll) + m.sin(yaw) * m.sin(roll)],
                     [m.sin(yaw) * m.cos(pitch), m.sin(yaw) * m.sin(pitch) * m.sin(roll) + m.cos(yaw) * m.cos(roll), m.sin(yaw) * m.sin(pitch) * m.cos(roll) - m.cos(yaw) * m.sin(roll)],
                     [-m.sin(pitch), m.cos(pitch) * m.sin(roll), m.cos(pitch) * m.cos(roll)]])
    
    for p in v:
        rv.append(numpy.dot(A, p))

    for edge in edges:
        start = rv[edge[0]]
        end = rv[edge[1]]
        grad_line(start[0] + WIDTH//2, start[1] + HEIGHT//2, start[2],
                  end[0] + WIDTH//2, end[1] + HEIGHT//2, end[2], 50, 31)

def grad_line(x1,y1,z1,x2,y2,z2,res,alpha):
    xc = x1
    yc = y1
    dx = x2 - x1
    dy = y2 - y1
    zc = z1 * 100/400
    zf = z2 * 100/400
    dz = zf - zc
    length = m.sqrt(dx**2 + dy**2)
    if length == 0:
        return []
    t=1/res
    for i in range(res):
        c = 127 + round(zc + ((t * dz)/2))
        if(screen.get_at((round(xc), round(yc)))[0] < c+10 and screen.get_at((round(xc + t * dx), round(yc + t * dy)))[0] <= c+10) and screen.get_at((round(xc - t * dx), round(yc - t * dy)))[0] < c+10:
            pygame.draw.line(screen, (c,c,c,alpha), (round(xc), round(yc)), (round(xc + t * dx), round(yc + t * dy)), 5)
        xc = xc + t * dx
        yc = yc + t * dy
        zc = zc + t * dz
        

angle = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))
    draw_cube(angle, angle, angle, 100)
    angle += 0.1
    pygame.display.flip()
    clock.tick(60)
pygame.quit()