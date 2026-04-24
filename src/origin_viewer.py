import multiprocessing as mp

def run_origin_window(shared_arr):
    import pygame
    from src.wAxis import wAxis
    pygame.init()
    
    WIDTH, HEIGHT = 300, 300
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Isolated Origin Axis")
    clock = pygame.time.Clock()
    
    axis = wAxis(80, 0.001, 0, 0, 0, 0)
    font = pygame.font.SysFont(None, 24)
    tuning = 0.2
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        screen.fill((15, 15, 15))
        
        # Read synced state [yaw, pitch, roll, dip, tuck, skew, ortho]
        yaw, pitch, roll, dip, tuck, skew, ortho = shared_arr[:]
        axis.rotate(yaw, pitch, roll, dip, tuck, skew)
        axis.shrink(ortho)
        
        # Draw structural connecting structural layout lines 
        for v in axis.edges.adj:
            if v < 0:
                n = list(axis.edges.adj[v])
                if len(n) == 2:
                    p1 = axis.ov[n[0]]
                    p2 = axis.ov[n[1]]
                    c = (80, 80, 80)
                    pygame.draw.line(screen, c, 
                        (WIDTH//2 + round(p1[0]), HEIGHT//2 + round(p1[1])),
                        (WIDTH//2 + round(p2[0]), HEIGHT//2 + round(p2[1])), 2)

        # Draw dimensional nodes and floating UI text
        for p in range(len(axis.ov)):
            text = axis.getText(p)
            if text:
                z = axis.ov[p][2]
                w = axis.ov[p][3]
                
                g_val = 127 + round(z * tuning)
                d_val = round((w+w) * tuning)
                
                r_c = max(0, min(255, int(g_val + d_val)))
                b_c = max(0, min(255, int(g_val - d_val)))
                g_c = max(0, min(255, int(g_val)))
                
                sx = WIDTH//2 + round(axis.ov[p][0])
                sy = HEIGHT//2 + round(axis.ov[p][1])
                
                pygame.draw.circle(screen, (r_c, g_c, b_c), (sx, sy), 10)
                text_surf = font.render(text, True, (255, 255, 255))
                screen.blit(text_surf, (sx-5, sy-5))
                
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()

def spawn_origin_viewer():
    shared_arr = mp.Array('d', [0.0] * 7)
    p = mp.Process(target=run_origin_window, args=(shared_arr,))
    p.daemon = True
    p.start()
    return shared_arr
