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
import numpy as np
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
    print(f"[4D-DEBUG] {msg}", file=sys.stdout)


def log_error(msg):
    print(f"[4D-ERROR] {msg}", file=sys.stderr)


async def main_async():
    """Main async loop with full error handling"""
    pygame_init_failed = False
    screen = None
    running = False

    try:
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

        try:
            log_debug(f"Creating display: {WIDTH}x{HEIGHT}")
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("4D Axis Quiz Platform")
            log_debug("Display created successfully")
        except Exception as e:
            log_error(f"Display creation failed: {e}")
            raise

        try:
            clock = pygame.time.Clock()
            font = pygame.font.Font(None, 24)
            big_font = pygame.font.Font(None, 36)
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
                vals = list(a4_correct)
                perturbation_type = random.choice(['shuffle', 'negate', 'scale'])
                if perturbation_type == 'shuffle':
                    random.shuffle(vals)
                    if tuple(vals) == a4_correct: vals[0], vals[1] = vals[1], vals[0]
                elif perturbation_type == 'negate':
                    idx = random.randint(0, 2)
                    vals[idx] *= -1
                elif perturbation_type == 'scale':
                    idx = random.randint(0, 2)
                    vals[idx] *= random.choice([0.2, 3.0])
                a4_variants[i] = tuple(vals)

        mousex, mousey = WIDTH // 2, HEIGHT // 2
        lastx, lasty = mousex, mousey
        drag_start_pos = (0, 0)
        dragging = False
        xsens, ysens = WIDTH / 180, HEIGHT / 180
        dy, dr = 0, 0
        curr_vx, curr_vy = 0, 0
        d4 = 0
        paused = False
        togglescroll = True

        # Initialize renderers
        log_debug("Initializing renderers...")
        try:
            renderers = {
                'Wireframe': WireframeRenderer(WIDTH, HEIGHT - 250, a4=a4_correct),
                'W-Shells': WShellRenderer(WIDTH, HEIGHT - 250, a4=a4_correct),
                'CellHl': CellHlRenderer(WIDTH, HEIGHT - 250, a4=a4_correct)
            }
            mode = 'Wireframe'
            origin_renderer = OriginRenderer(200, 200, size=50)
            log_debug("Renderers initialized successfully")
        except Exception as e:
            log_error(f"Renderer initialization failed: {e}")
            raise

        # Initialize shapes
        log_debug("Initializing shapes...")
        try:
            ortho = 0.001
            main_shapes = [
                Tesseract(100, ortho, 0, 0, 0, 0),
                ThreeAxis(75, ortho, 0, 0, 0)
            ]
            log_debug("Shapes initialized successfully")
        except Exception as e:
            log_error(f"Shape initialization failed: {e}")
            raise

        # Renderer specific settings
        target_w = 0.0
        opacity = 1.0

        # Mode buttons
        mode_buttons = [
            ToggleButton(20, 20, 100, 30, "Wireframe", (100, 100, 255)),
            ToggleButton(130, 20, 100, 30, "W-Shells", (100, 255, 100)),
            ToggleButton(240, 20, 100, 30, "CellHl", (255, 100, 100))
        ]
        mode_buttons[0].selected = True

        # Quiz selection buttons
        quiz_buttons = []
        for i in range(5):
            quiz_buttons.append(ToggleButton(100 + i * 210, HEIGHT - 40, 200, 30, f"Option {i+1}", (150, 150, 150)))
        feedback_text = ""
        feedback_color = (255, 255, 255)
        mouse_history = [(0, 0)] * 5

        # Cell highlight buttons (CellHl mode only)
        button_labels = ["+x", "-x", "+y", "-y", "+z", "-z", "+w", "-w"]
        label_to_cell = {"+x": 4, "-x": 6, "+y": 5, "-y": 3, "+z": 7, "-z": 2, "+w": 1, "-w": 0}
        cell_colors = {
            0: (150, 150, 0), 1: (255, 255, 100), 2: (0, 0, 150), 3: (0, 150, 0),
            4: (255, 100, 100), 5: (100, 255, 100), 6: (150, 0, 0), 7: (100, 100, 255),
        }
        cell_buttons = []
        for idx, label in enumerate(button_labels):
            cell_buttons.append(
                ToggleButton(WIDTH - 50, 40 + idx * 40, 30, 30, label, cell_colors[label_to_cell[label]])
            )

        running = True
        frame_count = 0
        log_debug("Main game loop starting...")
        print(">>> ENTERING MAIN LOOP", flush=True)

        while running:
            try:
                frame_count += 1

                mouse_history.append(pygame.mouse.get_pos())
                if len(mouse_history) > 5: mouse_history.pop(0)

                for event in pygame.event.get():
                    try:
                        if event.type == pygame.QUIT:
                            running = False

                        # Mode buttons (radio behaviour)
                        for i, btn in enumerate(mode_buttons):
                            old_sel = btn.selected
                            btn.handle_event(event)
                            if btn.selected and not old_sel:
                                for j, other in enumerate(mode_buttons):
                                    if i != j: other.selected = False
                                mode = btn.label

                        # Cell buttons — only active in CellHl mode
                        if mode == 'CellHl':
                            for b in cell_buttons:
                                b.handle_event(event)
                        else:
                            for b in cell_buttons:
                                b.selected = False

                        # Quiz buttons
                        for i, btn in enumerate(quiz_buttons):
                            btn.handle_event(event)
                            if btn.selected:
                                if i + 1 == correct_idx:
                                    feedback_text = "CORRECT! This axis mapping matches the tesseract's rotation."
                                    feedback_color = (100, 255, 100)
                                else:
                                    feedback_text = "WRONG. Look closer at the dip/tuck/skew sync."
                                    feedback_color = (255, 100, 100)
                                btn.selected = False

                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if not any(b.rect.collidepoint(event.pos) for b in mode_buttons + quiz_buttons + cell_buttons):
                                dragging = True
                                lastx, lasty = event.pos
                                drag_start_pos = event.pos
                        elif event.type == pygame.MOUSEBUTTONUP:
                            if dragging:
                                dragging = False
                                mx, my = event.pos
                                total_dist = ((mx - drag_start_pos[0])**2 + (my - drag_start_pos[1])**2)**0.5
                                old_mx, old_my = mouse_history[0]
                                vx = (mx - old_mx) / (xsens * 2.5)
                                vy = (my - old_my) / (ysens * 2.5)
                                if total_dist > 15:
                                    if abs(vx) > abs(vy) and abs(vx) > 0.1: dy = vx; dr = 0
                                    elif abs(vy) > 0.1: dr = vy; dy = 0
                                    else: dr, dy = 0, 0
                                else: dr, dy = 0, 0
                            else: dr, dy = 0, 0

                        elif event.type == pygame.MOUSEMOTION and dragging:
                            mx, my = event.pos
                            vx_frame = (mx - lastx) / xsens
                            vy_frame = (my - lasty) / ysens
                            yaw -= vx_frame
                            roll -= vy_frame
                            lastx, lasty = mx, my
                            dr, dy = 0, 0

                        if event.type == pygame.MOUSEWHEEL:
                            if togglescroll:
                                scroll_val = -event.y * 3
                                if paused:
                                    for i in range(6):
                                        dips[i] = (dips[i] + scroll_val * a4_variants[i][0]) % 360
                                        tucks[i] = (tucks[i] + scroll_val * a4_variants[i][1]) % 360
                                        skews[i] = (skews[i] + scroll_val * a4_variants[i][2]) % 360
                                d4 = scroll_val
                            else:
                                if mode == 'Wireframe': ortho = max(0, min(0.005, ortho + event.y * 0.0002))
                                elif mode == 'W-Shells': target_w += event.y * 10.0
                                elif mode == 'CellHl': opacity = max(0.0, min(1.0, opacity + event.y * 0.05))

                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE: paused = not paused
                            if event.key == pygame.K_LCTRL: togglescroll = False
                        if event.type == pygame.KEYUP:
                            if event.key == pygame.K_LCTRL: togglescroll = True

                    except Exception as e:
                        log_error(f"Event handling error (frame {frame_count}): {e}")

                # Rendering
                try:
                    screen.fill((5, 5, 5))
                    yaw -= dy
                    roll -= dr
                    if not paused:
                        for i in range(6):
                            dips[i] = (dips[i] + d4 * a4_variants[i][0]) % 360
                            tucks[i] = (tucks[i] + d4 * a4_variants[i][1]) % 360
                            skews[i] = (skews[i] + d4 * a4_variants[i][2]) % 360

                    # Main viewport
                    main_surf = pygame.Surface((WIDTH, HEIGHT - 250))
                    main_surf.fill((0, 0, 0))
                    for shape in main_shapes:
                        shape.rotate(yaw, 0, roll, dips[0], tucks[0], skews[0])
                        if mode == 'Wireframe': shape.shrink(ortho)
                        else: shape.shrink(0.001)

                    cellhl = set()
                    for i, label in enumerate(button_labels):
                        if cell_buttons[i].getsel():
                            cellhl.add(label_to_cell[label])

                    if mode == 'Wireframe': renderers['Wireframe'].render(main_surf, main_shapes)
                    elif mode == 'W-Shells': renderers['W-Shells'].render(main_surf, main_shapes, target_w)
                    elif mode == 'CellHl': renderers['CellHl'].render(main_surf, main_shapes, opacity, cellhl, cell_colors)

                    screen.blit(main_surf, (0, 0))
                    pygame.draw.line(screen, (100, 100, 100), (0, HEIGHT - 250), (WIDTH, HEIGHT - 250), 2)

                    # 5 origin viewports
                    for i in range(1, 6):
                        origin_surf = pygame.Surface((200, 200))
                        origin_renderer.render(origin_surf, yaw, 0, roll, dips[i], tucks[i], skews[i], ortho)
                        screen.blit(origin_surf, (100 + (i - 1) * 210, HEIGHT - 240))

                    # UI overlays
                    for b in mode_buttons: b.draw(screen, font)
                    if mode == 'CellHl':
                        for b in cell_buttons: b.draw(screen, font)
                    for b in quiz_buttons: b.draw(screen, font)

                    q_text = big_font.render("Which origin axis matches the Tesseract's rotation logic?", True, (255, 255, 255))
                    screen.blit(q_text, (WIDTH // 2 - q_text.get_width() // 2, HEIGHT - 285))
                    f_surf = font.render(feedback_text, True, feedback_color)
                    screen.blit(f_surf, (WIDTH // 2 - f_surf.get_width() // 2, HEIGHT - 70))
                    instr = font.render("SCROLL to spin 4D axes | DRAG to rotate 3D | SPACE to pause | CTRL+SCROLL for mode options", True, (150, 150, 150))
                    screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 15))

                    pygame.display.flip()
                    clock.tick(60)

                except Exception as e:
                    log_error(f"Rendering error (frame {frame_count}): {e}")
                    traceback.print_exc()

                # REQUIRED for pygbag: hand control back to the browser
                await asyncio.sleep(0)

            except Exception as e:
                log_error(f"Frame loop error (frame {frame_count}): {e}")
                traceback.print_exc()

        log_debug(f"Game loop ended after {frame_count} frames")
        pygame.quit()
        log_debug("Pygame quit successfully")

    except Exception as e:
        log_error(f"Critical error in main_async: {e}")
        traceback.print_exc()
        if screen is not None:
            try:
                pygame.quit()
            except:
                pass
        raise


def main():
    asyncio.run(main_async())


if __name__ == '__main__':
    main()
