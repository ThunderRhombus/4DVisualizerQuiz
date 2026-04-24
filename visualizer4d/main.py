# /// script
# dependencies = ["pygame-ce","numpy"]
# ///

"""
4D Visualizer Quiz - Web Version (pygbag)
Main entry point for WebAssembly/Web deployment
"""

import sys
print("STARTING MAIN.PY", flush=True)
print(f"Python version: {sys.version}", flush=True)
import pygame
import random
import asyncio
import traceback

try:
    from Tesseract import Tesseract
    from Cube import Cube
    from Tetrahedron import Tetrahedron
    from ThreeAxis import ThreeAxis
    from MAINWireframe import WireframeRenderer
    from MAINWShell import WShellRenderer
    from MAINCellHl import CellHlRenderer, ToggleButton
    from OriginRenderer import OriginRenderer
except ImportError as e:
    print(f"[IMPORT_ERROR] Failed to import modules: {e}", file=sys.stderr)
    traceback.print_exc()
    raise


def log_debug(msg):
    """Send debug message to console"""
    print(f"[4D-DEBUG] {msg}", file=sys.stdout)


def log_error(msg):
    """Send error message to stderr"""
    print(f"[4D-ERROR] {msg}", file=sys.stderr)


class OriginAxisViewer:
    """Web-compatible origin axis viewer (replaces multiprocessing version)"""
    
    def __init__(self, size=60, width=300, height=300):
        self.width = width
        self.height = height
        self.size = size
        self.axis = None
        try:
            self.axis = self.__import_axis()
        except Exception as e:
            log_error(f"Failed to initialize axis: {e}")
            self.axis = None
    
    def __import_axis(self):
        from wAxis import wAxis
        return wAxis(self.size, 0.001, 0, 0, 0, 0)
    
    def render(self, screen, state):
        """Render the axis viewer to the given surface"""
        if not self.axis or not hasattr(screen, 'fill'):
            return
        
        try:
            yaw, pitch, roll, dip, tuck, skew, ortho = state
            
            screen.fill((15, 15, 15))
            pygame.draw.rect(screen, (60, 60, 60), screen.get_rect(), 1)
            
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
                        pygame.draw.line(screen, c,
                            (self.width//2 + round(p1[0]), self.height//2 + round(p1[1])),
                            (self.width//2 + round(p2[0]), self.height//2 + round(p2[1])), 2)
            
            # Draw dimensional nodes and floating UI text
            font = pygame.font.Font(None, 24)
            for p in range(len(self.axis.ov)):
                text = self.axis.getText(p)
                if text:
                    z = self.axis.ov[p][2]
                    w = self.axis.ov[p][3]
                    
                    g_val = 127 + round(z * 0.2)
                    d_val = round((w+w) * 0.2)
                    
                    r_c = max(0, min(255, int(g_val + d_val)))
                    b_c = max(0, min(255, int(g_val - d_val)))
                    g_c = max(0, min(255, int(g_val)))
                    
                    sx = self.width//2 + round(self.axis.ov[p][0])
                    sy = self.height//2 + round(self.axis.ov[p][1])
                    
                    pygame.draw.circle(screen, (r_c, g_c, b_c), (sx, sy), 10)
                    text_surf = font.render(text, True, (255, 255, 255))
                    screen.blit(text_surf, (sx-5, sy-5))
        except Exception as e:
            log_error(f"Error rendering origin axis: {e}")


async def main_async():
    """Main async loop with full error handling"""
    log_debug("ENTER main_async")
    print("ENTER main_async", flush=True)
    pygame_init_failed = False
    screen = None
    
    try:
        # Initialize pygame with error handling
        log_debug("Initializing pygame...")
        try:
            print(">>> BEFORE pygame.init", flush=True)
            pygame.init()
            print(">>> AFTER pygame.init", flush=True)
            pygame.font.init()
            print(">>> AFTER pygame.font.init", flush=True)
            
            log_debug("Pygame initialized successfully")
        except Exception as e:
            log_error(f"Pygame initialization failed: {e}")
            pygame_init_failed = True
            raise

        WIDTH, HEIGHT = 1200, 800
        
        # Set up display with error handling
        try:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("4D Visualizer Quiz")
            log_debug("Display initialized successfully")
        except Exception as e:
            log_error(f"Display initialization failed: {e}")
            raise
        
        # Initialize clock and fonts
        try:
            clock = pygame.time.Clock()
            pygame.font.init()
            font = pygame.font.Font(None, 24)
            log_debug("Clock and fonts initialized")
        except Exception as e:
            log_error(f"Clock/font initialization failed: {e}")
            raise

        # Interaction State
        yaw, pitch, roll = 0, 0, 0
        a4_correct = (0.1, 0.05, 0.02)
        
        # Angles for each of the 6 viewports (Main + 5 Origins)
        dips = [0.0] * 6
        tucks = [0.0] * 6
        skews = [0.0] * 6
        
        # a4 variants for the 5 options
        correct_idx = random.randint(1, 5)
        a4_variants = [None] * 6
        a4_variants[0] = a4_correct  # Main window
        
        for i in range(1, 6):
            if i == correct_idx:
                a4_variants[i] = a4_correct
            else:
                a4_variants[i] = (
                    random.uniform(0.05, 0.15),
                    random.uniform(0.02, 0.1),
                    random.uniform(0.01, 0.05)
                )

        mousex, mousey = 0, 0
        lastx, lasty = 0, 0
        drag_start_pos = (0, 0)
        dragging = False
        xsens, ysens = WIDTH/180, HEIGHT/180
        dy, dr = 0, 0
        curr_vx, curr_vy = 0, 0
        d4 = 0
        paused = False
        togglescroll = True
        
        # Initialize renderers with error handling
        log_debug("Initializing renderers...")
        try:
            wireframe_renderer = WireframeRenderer(WIDTH, HEIGHT, a4=a4_correct)
            wshell_renderer = WShellRenderer(WIDTH, HEIGHT, a4=a4_correct)
            cellhl_renderer = CellHlRenderer(WIDTH, HEIGHT, a4=a4_correct)
            log_debug("Renderers initialized")
        except Exception as e:
            log_error(f"Renderer initialization failed: {e}")
            raise

        # Initialize shapes with error handling
        log_debug("Initializing shapes...")
        try:
            tess = Tesseract(100, 0.001, 0, 0, 0, 0)
            shapes = [tess]
            log_debug("Shapes initialized")
        except Exception as e:
            log_error(f"Shape initialization failed: {e}")
            raise

        # Renderer specific settings
        target_w = 0.0
        opacity = 1.0
        
        # UI Elements
        mode_buttons = [
            ToggleButton(20, 20, 100, 30, "Wireframe", (100, 100, 255)),
            ToggleButton(130, 20, 100, 30, "W-Shells", (100, 255, 100)),
            ToggleButton(240, 20, 100, 30, "CellHl", (255, 100, 100))
        ]
        mode_buttons[0].selected = True

        # Origin axis viewer (web-compatible, no multiprocessing)
        origin_viewer = OriginAxisViewer(60, 300, 300)
        origin_state = [0, 0, 0, 0, 0, 0, 0.001]
        
        # Main loop
        running = True
        log_debug("Starting main event loop...")
        print(">>> ENTERING MAIN LOOP", flush=True)
        origin_surface = pygame.Surface((300, 300), pygame.SRCALPHA)
        while running:
              # Allow other tasks to run
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousex, mousey = pygame.mouse.get_pos()
                    lastx, lasty = mousex, mousey
                    drag_start_pos = (mousex, mousey)
                    dragging = True
                    
                    # Check button clicks
                    for btn in mode_buttons:
                        btn.handle_event(event)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging = False
                    mousex, mousey = pygame.mouse.get_pos()
                    
                    # Calculate drag velocity
                    dx = mousex - lastx
                    dy_temp = mousey - lasty
                    
                    if abs(dx) > 5:
                        curr_vx = dx / 5
                    if abs(dy_temp) > 5:
                        curr_vy = dy_temp / 5
                
                elif event.type == pygame.MOUSEMOTION and dragging:
                    mousex, mousey = pygame.mouse.get_pos()
                    dx = mousex - lastx
                    dy_temp = mousey - lasty
                    
                    dy += dx * xsens
                    dr += dy_temp * ysens
                    
                    lastx, lasty = mousex, mousey

                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        target_w = min(target_w + 10, 100)
                    elif event.y < 0:
                        target_w = max(target_w - 10, -100)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    if event.key == pygame.K_r:
                        yaw, pitch, roll = 0, 0, 0
                        dips = [0.0] * 6
                        tucks = [0.0] * 6
                        skews = [0.0] * 6
                        target_w = 0.0

            # Update rotation with momentum
            dy *= 0.95
            dr *= 0.95
            curr_vx *= 0.95
            curr_vy *= 0.95

            screen.fill((15, 15, 15))
            yaw -= dy
            roll -= dr

            # Update 4D angles
            if not paused:
                for i in range(6):
                    dips[i] = (dips[i] + d4 * a4_variants[i][0]) % 360
                    tucks[i] = (tucks[i] + d4 * a4_variants[i][1]) % 360
                    skews[i] = (skews[i] + d4 * a4_variants[i][2]) % 360
                d4 = (d4 + 1) % 360

            # Render main shapes
            for shape in shapes:
                shape.rotate(yaw, pitch, roll, dips[0], tucks[0], skews[0])
                shape.shrink(0.001)
            
            # Determine active renderer based on button state
            if mode_buttons[0].selected:
                wireframe_renderer.render(screen, shapes)
            elif mode_buttons[1].selected:
                wshell_renderer.render(screen, shapes, target_w)
            elif mode_buttons[2].selected:
                cellhl_renderer.render(screen, shapes, opacity, -1, {})

            # Draw UI buttons
            for btn in mode_buttons:
                btn.draw(screen, font)

            # Render origin axis viewer in top-right corner
            
            origin_surface.fill((0, 0, 0, 0))  # Transparent background
            origin_state = [yaw, pitch, roll, dips[0], tucks[0], skews[0], 0.001]
            origin_viewer.render(origin_surface, origin_state)
            screen.blit(origin_surface, (WIDTH - 300, 0))

            # Display instructions
            instructions = font.render("Drag: Rotate | Space: Pause | R: Reset | Scroll: W-axis", True, (200, 200, 200))
            screen.blit(instructions, (20, HEIGHT - 30))

            pygame.display.flip()
            clock.tick(60)
            await asyncio.sleep(0)

        log_debug("Main loop ended, shutting down...")
        
    except Exception as e:
        log_error(f"Fatal error in main_async: {e}")
        traceback.print_exc()
    finally:
        if screen is not None:
            pygame.quit()
            log_debug("Pygame quit successfully")

asyncio.run(main_async())
