import pygame
import math as m
from wAxis import wAxis

class OriginRenderer:
    def __init__(self, width, height, size=60):
        self.WIDTH = width
        self.HEIGHT = height
        self.axis = wAxis(size, 0.001, 0, 0, 0, 0)
        self.font = pygame.font.SysFont(None, 20)
        self.tuning = 0.2

    def render(self, surface, yaw, pitch, roll, dip, tuck, skew, ortho):
        surface.fill((15, 15, 15))
        pygame.draw.rect(surface, (60, 60, 60), surface.get_rect(), 1)
        
        self.axis.rotate(yaw, pitch, roll, dip, tuck, skew)
        self.axis.shrink(ortho)
        
        # Draw structural lines
        for v in self.axis.edges.adj:
            if v < 0:
                n = list(self.axis.edges.adj[v])
                if len(n) == 2:
                    p1 = self.axis.ov[n[0]]
                    p2 = self.axis.ov[n[1]]
                    c = (80, 80, 80)
                    pygame.draw.line(surface, c, 
                        (self.WIDTH//2 + round(p1[0]), self.HEIGHT//2 + round(p1[1])),
                        (self.WIDTH//2 + round(p2[0]), self.HEIGHT//2 + round(p2[1])), 1)

        # Draw dimensional nodes and labels
        for p in range(len(self.axis.ov)):
            text = self.axis.getText(p)
            if text:
                z = self.axis.ov[p][2]
                w = self.axis.ov[p][3]
                
                g_val = 127 + round(z * self.tuning)
                d_val = round((w+w) * self.tuning)
                
                r_c = max(0, min(255, int(g_val + d_val)))
                b_c = max(0, min(255, int(g_val - d_val)))
                g_c = max(0, min(255, int(g_val)))
                
                sx = self.WIDTH//2 + round(self.axis.ov[p][0])
                sy = self.HEIGHT//2 + round(self.axis.ov[p][1])
                
                pygame.draw.circle(surface, (r_c, g_c, b_c), (sx, sy), 6)
                text_surf = self.font.render(text, True, (200, 200, 200))
                surface.blit(text_surf, (sx-4, sy-4))

def main():
    # Standalone test
    pygame.init()
    screen = pygame.display.set_mode((300, 300))
    renderer = OriginRenderer(300, 300)
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
        renderer.render(screen, 0, 0, 0, 0, 0, 0, 0.001)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == '__main__':
    main()
