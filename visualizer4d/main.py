# --- START FILE ---

# /// script
# dependencies = ["pygame-ce","numpy"]
# ///

import pygame
import random
import asyncio
import sys
import traceback
import urllib.parse
import time
import math

print("STARTING MAIN.PY", flush=True)
print(f"Python version: {sys.version}", flush=True)

try:
    from Tesseract import Tesseract
    from Cube import Cube
    from Tetrahedron import Tetrahedron
    from ThreeAxis import ThreeAxis
    from FiveCell import FiveCell
    from SixteenCell import SixteenCell
    from MAINWireframe import WireframeRenderer
    from MAINWShell import WShellRenderer
    from MAINCellHl import CellHlRenderer, ToggleButton
    from OriginRenderer import OriginRenderer
except ImportError as e:
    print(f"[IMPORT_ERROR] Failed to import modules: {e}", file=sys.stderr)
    traceback.print_exc()
    raise

TOTAL_QUIZ_QUESTIONS = 15

def log_debug(msg):
    print(f"[4D-DEBUG] {msg}", file=sys.stdout)

def log_error(msg):
    print(f"[4D-ERROR] {msg}", file=sys.stderr)


# ============================================================
#  Draggable Slider
# ============================================================
class Slider:
    """
    Horizontal draggable slider.  value is in [min_val, max_val].
    x/y/w are updated by the layout helper each frame so resizing
    never breaks anything.
    """
    TRACK_H          = 4
    HANDLE_R         = 9
    COLOR_TRACK      = (70,  70,  90)
    COLOR_FILL       = (100, 160, 255)
    COLOR_HANDLE     = (200, 220, 255)
    COLOR_HANDLE_HOT = (255, 255, 120)
    COLOR_LABEL      = (180, 180, 200)
    COLOR_VALUE      = (220, 220, 255)

    def __init__(self, x, y, w, label, min_val, max_val, init_val):
        self.x       = x
        self.y       = y          # vertical centre of track
        self.w       = w          # track pixel width
        self.label   = label
        self.min_val = float(min_val)
        self.max_val = float(max_val)
        self.value   = float(init_val)
        self._drag   = False

    # ---- geometry ----
    def _val_to_px(self):
        t = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.x + t * self.w)

    def _px_to_val(self, px):
        t = max(0.0, min(1.0, (px - self.x) / self.w))
        return self.min_val + t * (self.max_val - self.min_val)

    def _hit(self, pos):
        hx = self._val_to_px()
        r  = self.HANDLE_R + 4
        return math.hypot(pos[0] - hx, pos[1] - self.y) <= r

    def _on_track(self, pos):
        return (self.x <= pos[0] <= self.x + self.w and
                abs(pos[1] - self.y) <= self.HANDLE_R + 6)

    # ---- public ----
    @property
    def is_dragging(self):
        return self._drag

    def handle_event(self, event):
        """Returns True if the event was consumed by this slider."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._hit(event.pos) or self._on_track(event.pos):
                self.value = self._px_to_val(event.pos[0])
                self._drag = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._drag:
                self._drag = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self._drag:
                self.value = self._px_to_val(event.pos[0])
                return True
        return False

    def draw(self, surface, font):
        # label (left of track)
        lbl = font.render(self.label, True, self.COLOR_LABEL)
        surface.blit(lbl, (self.x - lbl.get_width() - 8,
                           self.y - lbl.get_height() // 2))
        # track bg
        pygame.draw.rect(surface, self.COLOR_TRACK,
                         (self.x, self.y - self.TRACK_H//2,
                          self.w, self.TRACK_H), border_radius=2)
        # filled
        fw = self._val_to_px() - self.x
        if fw > 0:
            pygame.draw.rect(surface, self.COLOR_FILL,
                             (self.x, self.y - self.TRACK_H//2,
                              fw, self.TRACK_H), border_radius=2)
        # handle
        hx  = self._val_to_px()
        col = self.COLOR_HANDLE_HOT if self._drag else self.COLOR_HANDLE
        pygame.draw.circle(surface, col,    (hx, self.y), self.HANDLE_R)
        pygame.draw.circle(surface, (40,40,60), (hx, self.y), self.HANDLE_R, 2)
        # value (right of track)
        vs = font.render(f"{self.value:+.3f}", True, self.COLOR_VALUE)
        surface.blit(vs, (self.x + self.w + 8,
                          self.y - vs.get_height() // 2))


# ============================================================
#  Google Form submission
# ============================================================
async def submit_to_google_form(user_id, question_idx, mode, q_type,
                                correct, response_time, chosen_option):
    form_url = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/formResponse"
    data = {
        "entry.111111": str(user_id),
        "entry.222222": str(question_idx),
        "entry.333333": mode,
        "entry.444444": q_type,
        "entry.555555": str(correct),
        "entry.666666": str(round(response_time, 2)),
        "entry.777777": str(chosen_option),
    }
    log_debug(f"Submitting data: {data}")
    if "YOUR_FORM_ID" in form_url:
        log_debug("Form URL not set, skipping submission.")
        return
    try:
        if sys.platform == 'emscripten':
            import js
            from pyodide.ffi import to_js
            opts = {
                "method": "POST", "mode": "no-cors",
                "headers": {"Content-Type": "application/x-www-form-urlencoded"},
                "body": urllib.parse.urlencode(data),
            }
            js.fetch(form_url, to_js(opts))
        else:
            import urllib.request, threading
            enc = urllib.parse.urlencode(data).encode('utf-8')
            req = urllib.request.Request(form_url, data=enc)
            def _send():
                try: urllib.request.urlopen(req, timeout=5)
                except Exception as e: log_error(f"Submit error: {e}")
            threading.Thread(target=_send).start()
    except Exception as e:
        log_error(f"Failed to submit: {e}")


# ============================================================
#  Main
# ============================================================
async def main_async():
    screen = None
    try:
        log_debug("Initialising pygame...")
        print(">>> BEFORE pygame.init", flush=True)
        pygame.init()
        print(">>> AFTER pygame.init", flush=True)
        pygame.font.init()
        print(">>> AFTER pygame.font.init", flush=True)

        WIDTH, HEIGHT = 1200, 800
        try:
            log_debug(f"Creating display: {WIDTH}x{HEIGHT}")
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            pygame.display.set_caption("4D Axis Quiz Platform")
            log_debug("Display created successfully")
        except Exception as e:
            log_error(f"Display creation failed: {e}")
            traceback.print_exc()
            raise

        clock      = pygame.time.Clock()
        font       = pygame.font.SysFont(None, 24)
        big_font   = pygame.font.SysFont(None, 36)
        huge_font  = pygame.font.SysFont(None, 52)
        small_font = pygame.font.SysFont(None, 20)

        # ------------------------------------------------------------------
        # Session
        # ------------------------------------------------------------------
        user_id       = random.randint(10000, 99999)
        assigned_mode = random.choice(['Wireframe', 'W-Shells', 'CellHl'])
        mode          = assigned_mode
        # States: CONSENT | INTERSTITIAL | ANALYSIS | ANSWERING | FEEDBACK | FREE_MODE
        state         = "CONSENT"

        question_index = 0
        q_type         = ""
        q_start_time   = 0.0

        yaw = pitch = roll = 0.0
        a4_correct  = (0.10, 0.05, 0.02)
        correct_idx = 1
        a4_variants = [None] * 6
        dips  = [0.0] * 6
        tucks = [0.0] * 6
        skews = [0.0] * 6

        lastx, lasty   = WIDTH // 2, HEIGHT // 2
        drag_start_pos = (0, 0)
        dragging       = False
        xsens = WIDTH  / 180
        ysens = HEIGHT / 180
        dy = dr = d4 = 0.0
        paused       = False
        togglescroll = True
        ortho        = 0.001

        renderers = {
            'Wireframe': WireframeRenderer(WIDTH, HEIGHT - 300, a4=a4_correct),
            'W-Shells':  WShellRenderer  (WIDTH, HEIGHT - 300, a4=a4_correct),
            'CellHl':    CellHlRenderer  (WIDTH, HEIGHT - 300, a4=a4_correct),
        }
        origin_renderer = OriginRenderer(180, 180, size=50)

        SHAPE_NAMES = ["Tesseract", "5-Cell", "16-Cell"]
        FREE_MODES  = ['Wireframe', 'W-Shells', 'CellHl']
        free_shape_idx = 0

        active_shape = None
        axes_shape   = None
        main_shapes  = []
        cell_buttons = []
        cell_colors  = {}

        target_w = 0.0
        opacity  = 1.0
        feedback_text  = ""
        feedback_color = (255, 255, 255)
        mouse_history  = [(0, 0)] * 5
        frame_count    = 0

        # ------------------------------------------------------------------
        # Free-mode HUD constants
        # ------------------------------------------------------------------
        FREE_HUD = 210        # height of HUD strip at bottom in free mode
        SLIDER_W = 240        # track pixel width

        # ------------------------------------------------------------------
        # Sliders  (XW / YW / ZW  →  a4_correct components)
        # ------------------------------------------------------------------
        sliders = [
            Slider(0, 0, SLIDER_W, "XW", -0.30, 0.30, 0.10),
            Slider(0, 0, SLIDER_W, "YW", -0.30, 0.30, 0.05),
            Slider(0, 0, SLIDER_W, "ZW", -0.30, 0.30, 0.02),
        ]

        def slider_a4():
            return tuple(s.value for s in sliders)

        # ------------------------------------------------------------------
        # Consent buttons
        # ------------------------------------------------------------------
        ##btn_yes = ToggleButton(0, 0, 280, 52, "Yes – I consent to participate",   (70, 170, 70))
        btn_no  = ToggleButton(0, 0, 280, 52, "No – take me to free exploration", (170, 70,  70))

        # ------------------------------------------------------------------
        # Quiz buttons
        # ------------------------------------------------------------------
        btn_ready    = ToggleButton(0, 0, 200, 40, "Ready to Answer", (100, 200, 100))
        btn_next     = ToggleButton(0, 0, 200, 40, "Next Question",   (100, 200, 100))
        btn_continue = ToggleButton(0, 0, 200, 40, "Continue",        (100, 200, 100))
        quiz_buttons = [ToggleButton(0, 0, 170, 30, f"Option {i+1}", (150,150,150))
                        for i in range(5)]
        btn_idk = ToggleButton(0, 0, 170, 30, "I Don't Know", (200, 100, 100))

        # ------------------------------------------------------------------
        # Free-mode selector buttons
        # ------------------------------------------------------------------
        free_mode_btns = [
            ToggleButton(0, 0, 118, 30, "Wireframe", (80,  120, 200)),
            ToggleButton(0, 0, 118, 30, "W-Shells",  (80,  180, 120)),
            ToggleButton(0, 0, 118, 30, "CellHl",    (180, 120, 80)),
        ]
        free_shape_btns = [
            ToggleButton(0, 0, 102, 30, "Tesseract", (120, 80,  200)),
            ToggleButton(0, 0, 102, 30, "5-Cell",    (200, 80,  120)),
            ToggleButton(0, 0, 102, 30, "16-Cell",   (80,  200, 200)),
        ]

        # ------------------------------------------------------------------
        # Layout helpers
        # ------------------------------------------------------------------
        def layout_quiz():
            btn_ready.rect.topleft    = (WIDTH//2 - 100, HEIGHT - 100)
            btn_next.rect.topleft     = (WIDTH//2 - 100, HEIGHT - 80)
            btn_continue.rect.topleft = (WIDTH//2 - 100, HEIGHT - 100)
            total_bw = 6 * 170 + 5 * 20
            bx = WIDTH//2 - total_bw//2
            for i, b in enumerate(quiz_buttons):
                b.rect.x = bx + i * 190
                b.rect.y = HEIGHT - 80
            btn_idk.rect.x = bx + 5 * 190
            btn_idk.rect.y = HEIGHT - 80

        def layout_cell(vp_h=None):
            """Cell buttons pinned to right edge, below any title bar."""
            rx = WIDTH - 65
            for idx, b in enumerate(cell_buttons):
                b.rect.x = rx
                b.rect.y = 40 + idx * 30

        def layout_consent():
            cx = WIDTH  // 2 - 140
            # Pin buttons near the bottom of the screen, clear of all text
            cy = HEIGHT - 160
            ##btn_yes.rect.topleft = (cx, cy)
            btn_no.rect.topleft  = (cx, cy + 68)

        def layout_free():
            """
            HUD occupies the bottom FREE_HUD pixels.
            Left column:  mode/shape buttons.
            Right column: sliders.
            Far right:    hints.
            """
            hud_top = HEIGHT - FREE_HUD + 8

            # Mode buttons – row 0
            bx = 90
            for b in free_mode_btns:
                b.rect.x = bx; b.rect.y = hud_top
                bx += b.rect.width + 8

            # Shape buttons – row 1
            bx = 90
            for b in free_shape_btns:
                b.rect.x = bx; b.rect.y = hud_top + 42
                bx += b.rect.width + 8

            # Sliders – vertically centred in HUD, right of centre
            # Leave ~340 px on the far right for hints
            slider_x  = WIDTH // 2 + 40
            row_h     = (FREE_HUD - 20) // 3
            for i, s in enumerate(sliders):
                s.x = slider_x
                s.y = hud_top + i * row_h + row_h // 2
                s.w = min(SLIDER_W, WIDTH - slider_x - 360)   # shrink if narrow

        def update_free_sel():
            for i, b in enumerate(free_mode_btns):
                b.selected = (FREE_MODES[i] == mode)
            for i, b in enumerate(free_shape_btns):
                b.selected = (i == free_shape_idx)

        # ------------------------------------------------------------------
        # Shape helpers
        # ------------------------------------------------------------------
        def make_pool(o):
            s = 100
            return [Tesseract(s, o, 0,0,0,0),
                    FiveCell(2*s, o, 0,0,0,0),
                    SixteenCell(2*s, o, 0,0,0,0)]

        def build_cell_btns(shape):
            lbls   = getattr(shape, 'cell_labels', [])
            colors = getattr(shape, 'cell_colors', {})
            btns   = [ToggleButton(0,0,50,25,lbl,colors.get(i,(150,150,150)))
                      for i,lbl in enumerate(lbls)]
            return btns, colors

        def rebuild_free_shape():
            nonlocal active_shape, axes_shape, main_shapes, cell_buttons, cell_colors
            pool         = make_pool(ortho)
            active_shape = pool[free_shape_idx]
            axes_shape   = ThreeAxis(75, ortho, 0, 0, 0)
            main_shapes  = [active_shape, axes_shape]
            cell_buttons, cell_colors = build_cell_btns(active_shape)

        def enter_free(from_quiz=True):
            nonlocal state, dips, tucks, skews, a4_correct
            state = "FREE_MODE"
            dips[0] = tucks[0] = skews[0] = 0.0
            sliders[0].value = 0.10
            sliders[1].value = 0.05
            sliders[2].value = 0.02
            a4_correct = slider_a4()
            rebuild_free_shape()
            update_free_sel()
            log_debug(f"FREE_MODE  from_quiz={from_quiz}")

        # ------------------------------------------------------------------
        # Quiz question setup
        # ------------------------------------------------------------------
        def setup_question():
            nonlocal a4_correct, a4_variants, correct_idx
            nonlocal active_shape, axes_shape, main_shapes
            nonlocal dips, tucks, skews, q_start_time, q_type
            nonlocal cell_buttons, cell_colors, state, ortho

            qi = question_index % 5
            if qi in (0, 1):
                val = random.choice([0.10, 0.15, 0.08])
                lst = [0.0, 0.0, 0.0]
                lst[random.randint(0,2)] = val
                a4_correct = tuple(lst); q_type = "Easy"
            elif qi in (2, 3):
                v1,v2 = random.choice([0.10,0.15]), random.choice([0.05,0.08])
                lst = [v1, v2, 0.0]; random.shuffle(lst)
                a4_correct = tuple(lst); q_type = "Medium"
            else:
                a4_correct = (0.10, 0.05, 0.02); q_type = "Hard"

            ortho = 0.001
            pool  = make_pool(ortho)
            active_shape = pool[0] if qi==0 else random.choice(pool)
            axes_shape   = ThreeAxis(75, ortho, 0, 0, 0)
            main_shapes  = [active_shape, axes_shape]
            cell_buttons, cell_colors = build_cell_btns(active_shape)

            correct_idx    = random.randint(1, 5)
            a4_variants[0] = a4_correct

            def diff_ok(v1, v2):
                n1 = math.sqrt(sum(a*a for a in v1))
                n2 = math.sqrt(sum(b*b for b in v2))
                if n1<1e-5 or n2<1e-5: return abs(n1-n2)>1e-5
                return abs(sum((a/n1)*(b/n2) for a,b in zip(v1,v2))) < 0.95

            generated  = [a4_correct]
            pre_seeded = {}
            if qi in (0,1):
                wrong = [i for i in range(1,6) if i!=correct_idx]
                nz    = [i for i,x in enumerate(a4_correct) if abs(x)>1e-5][0]
                val   = a4_correct[nz]
                other = [i for i in range(3) if i!=nz]
                nv    = [0.0,0.0,0.0]
                nv[random.choice(other)] = random.choice([val,-val])
                pre_seeded[wrong[0]] = tuple(nv)

            for i in range(1,6):
                if i == correct_idx:
                    a4_variants[i] = a4_correct
                elif i in pre_seeded:
                    a4_variants[i] = pre_seeded[i]
                    generated.append(pre_seeded[i])
                else:
                    placed = False
                    for _ in range(100):
                        vals = list(a4_correct)
                        for _ in range(random.randint(1,3)):
                            op = random.choice(['shuffle','negate','add'])
                            if op=='shuffle': random.shuffle(vals)
                            elif op=='negate': vals[random.randint(0,2)] *= -1
                            else: vals[random.randint(0,2)] += random.choice([-0.05,0.05,-0.1,0.1])
                        cand = tuple(vals)
                        if all(diff_ok(cand,ex) for ex in generated):
                            a4_variants[i] = cand; generated.append(cand); placed=True; break
                    if not placed:
                        vals = list(a4_correct); vals[i%3] += 0.15+i*0.05
                        a4_variants[i] = tuple(vals); generated.append(tuple(vals))

            for i in range(6): dips[i]=tucks[i]=skews[i]=0.0
            renderers['Wireframe'].a4 = a4_correct
            renderers['W-Shells'].a4  = a4_correct
            renderers['CellHl'].a4    = a4_correct
            q_start_time = time.time()
            state = "ANALYSIS"
            for b in quiz_buttons+[btn_idk,btn_next,btn_ready]: b.selected=False

        # ------------------------------------------------------------------
        # Initial layouts
        # ------------------------------------------------------------------
        layout_quiz()
        layout_free()
        layout_consent()

        # ==================================================================
        # Main loop
        # ==================================================================
        running = True
        log_debug("Main game loop starting...")
        print(">>> ENTERING MAIN LOOP", flush=True)
        while running:
            try:
                frame_count += 1
                mouse_history.append(pygame.mouse.get_pos())
                if len(mouse_history) > 5: mouse_history.pop(0)

                slider_hot = any(s.is_dragging for s in sliders)

                for event in pygame.event.get():
                    try:
                        if event.type == pygame.QUIT:
                            running = False

                        elif event.type == pygame.VIDEORESIZE:
                            WIDTH, HEIGHT = event.size
                            screen = pygame.display.set_mode((WIDTH,HEIGHT), pygame.RESIZABLE)
                            xsens = WIDTH/180; ysens = HEIGHT/180
                            for r in renderers.values():
                                r.WIDTH=WIDTH; r.HEIGHT=HEIGHT-300
                            layout_quiz(); layout_free(); layout_consent()

                        # ---- CONSENT ----
                        if state == "CONSENT":
                            ##btn_yes.handle_event(event)
                            btn_no.handle_event(event)
                            ##if btn_yes.selected:
                            ##    btn_yes.selected = False
                            ##    state = "INTERSTITIAL"
                            if btn_no.selected:
                                btn_no.selected = False
                                enter_free(from_quiz=False)

                        # ---- INTERSTITIAL ----
                        elif state == "INTERSTITIAL":
                            btn_continue.handle_event(event)
                            if btn_continue.selected:
                                btn_continue.selected = False
                                setup_question()

                        # ---- ANALYSIS ----
                        elif state == "ANALYSIS":
                            btn_ready.handle_event(event)
                            if btn_ready.selected:
                                btn_ready.selected = False
                                state = "ANSWERING"
                            if mode == 'CellHl':
                                for b in cell_buttons: b.handle_event(event)

                        # ---- ANSWERING ----
                        elif state == "ANSWERING":
                            for i,btn in enumerate(quiz_buttons):
                                btn.handle_event(event)
                                if btn.selected:
                                    rt = time.time()-q_start_time
                                    ok = (i+1==correct_idx)
                                    feedback_text  = ("CORRECT! Axis mapping matches." if ok
                                                    else f"WRONG. Correct was Option {correct_idx}.")
                                    feedback_color = (100,255,100) if ok else (255,100,100)
                                    asyncio.create_task(submit_to_google_form(
                                        user_id,question_index+1,mode,q_type,ok,rt,f"Option {i+1}"))
                                    state = "FEEDBACK"
                            btn_idk.handle_event(event)
                            if btn_idk.selected:
                                rt = time.time()-q_start_time
                                feedback_text  = f"Correct was Option {correct_idx}."
                                feedback_color = (200,200,100)
                                asyncio.create_task(submit_to_google_form(
                                    user_id,question_index+1,mode,q_type,False,rt,"I Don't Know"))
                                state = "FEEDBACK"

                        # ---- FEEDBACK ----
                        elif state == "FEEDBACK":
                            btn_next.handle_event(event)
                            if btn_next.selected:
                                btn_next.selected = False
                                question_index += 1
                                if question_index >= TOTAL_QUIZ_QUESTIONS:
                                    enter_free(from_quiz=True)
                                elif question_index % 5 == 0:
                                    state = "INTERSTITIAL"
                                else:
                                    setup_question()

                        # ---- FREE MODE ----
                        elif state == "FREE_MODE":
                            # Sliders get first priority
                            consumed = any(s.handle_event(event) for s in sliders)
                            if not consumed:
                                for i,b in enumerate(free_mode_btns):
                                    b.handle_event(event)
                                    if b.selected and FREE_MODES[i]!=mode:
                                        mode=FREE_MODES[i]; update_free_sel()
                                for i,b in enumerate(free_shape_btns):
                                    b.handle_event(event)
                                    if b.selected and i!=free_shape_idx:
                                        free_shape_idx=i; rebuild_free_shape(); update_free_sel()
                                if mode=='CellHl':
                                    for b in cell_buttons: b.handle_event(event)

                        # ---- Viewport drag (blocked while any slider is active) ----
                        slider_hot = any(s.is_dragging for s in sliders)

                        if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                            if not slider_hot:
                                all_ui = (quiz_buttons+cell_buttons+
                                        [btn_ready,btn_next,btn_continue,btn_idk,btn_no]+
                                        free_mode_btns+free_shape_btns)
                                in_hud = (state=="FREE_MODE" and
                                        event.pos[1] >= HEIGHT-FREE_HUD)
                                if not any(b.rect.collidepoint(event.pos) for b in all_ui) and not in_hud:
                                    dragging=True; lastx,lasty=event.pos; drag_start_pos=event.pos

                        elif event.type == pygame.MOUSEBUTTONUP and event.button==1:
                            if dragging:
                                dragging=False
                                mx,my=event.pos
                                dist=math.hypot(mx-drag_start_pos[0],my-drag_start_pos[1])
                                omx,omy=mouse_history[0]
                                vx=(mx-omx)/(xsens*2.5); vy=(my-omy)/(ysens*2.5)
                                if dist>15:
                                    if abs(vx)>abs(vy) and abs(vx)>0.1: dy=vx; dr=0
                                    elif abs(vy)>0.1: dr=vy; dy=0
                                    else: dr=dy=0
                                else: dr=dy=0
                            else: dr=dy=0

                        elif event.type==pygame.MOUSEMOTION and dragging and not slider_hot:
                            mx,my=event.pos
                            yaw  -= (mx-lastx)/xsens
                            roll -= (my-lasty)/ysens
                            lastx,lasty=mx,my; dr=dy=0

                        if event.type==pygame.MOUSEWHEEL:
                            if togglescroll:
                                sv=-event.y*3
                                if paused:
                                    for i in range(6):
                                        dips[i]=(dips[i]+sv*a4_variants[i][0])%360
                                        tucks[i]=(tucks[i]+sv*a4_variants[i][1])%360
                                        skews[i]=(skews[i]+sv*a4_variants[i][2])%360
                                d4=sv
                            else:
                                if mode=='Wireframe': ortho=max(0,min(0.005,ortho+event.y*0.0002))
                                elif mode=='W-Shells': target_w+=event.y*10.0
                                elif mode=='CellHl':   opacity=max(0.0,min(1.0,opacity+event.y*0.05))

                        if event.type==pygame.KEYDOWN:
                            if event.key==pygame.K_SPACE: paused=not paused
                            elif event.key==pygame.K_r:
                                yaw=pitch=roll=0.0; dy=dr=d4=0.0
                                for i in range(6): dips[i]=tucks[i]=skews[i]=0.0
                            elif event.key==pygame.K_LCTRL: togglescroll=False
                        elif event.type==pygame.KEYUP:
                            if event.key==pygame.K_LCTRL: togglescroll=True
                    except Exception as e:
                        log_error(f"Event handling error (frame {frame_count}): {e}")
                        traceback.print_exc()
                try:
                    # ==============================================================
                    # RENDER
                    # ==============================================================
                    screen.fill((5,5,5))

                    # ---- CONSENT ----
                    if state == "CONSENT":
                        layout_consent()

                        # Title – anchored near top
                        t = huge_font.render("4D Axis Quiz Platform", True, (220,220,255))
                        screen.blit(t, (WIDTH//2 - t.get_width()//2, 40))

                        # Body text – small font, starts below title with fixed spacing
                        lines = [
                            "This study investigates how people perceive 4-dimensional rotations",
                            "through different visual representations.",
                            "",
                            "Participation is voluntary and fully anonymous.",
                            "You will view 4D shapes and identify which axis-indicator",
                            "matches the shape's 4D spin.",
                            "",
                            "Response times and answers will be recorded.",
                            "No personally identifying information is collected.",
                            "",
                            "Would you like to take part? (No Yes button, fixing stuff lol)",
                        ]
                        LINE_H = 24
                        y = 40 + t.get_height() + 30
                        for line in lines:
                            s = small_font.render(line, True, (200,200,200))
                            screen.blit(s, (WIDTH//2 - s.get_width()//2, y))
                            y += LINE_H if line else LINE_H // 2

                        ##btn_yes.draw(screen, font)
                        btn_no.draw(screen,  font)

                    # ---- INTERSTITIAL ----
                    elif state == "INTERSTITIAL":
                        block_idx = question_index // 5
                        try:
                            with open(f"interval_{block_idx}.txt") as f: text=f.read()
                        except Exception:
                            text=(f"Block {block_idx+1} of {TOTAL_QUIZ_QUESTIONS//5}"
                                f"  —  {TOTAL_QUIZ_QUESTIONS} questions total\n\n"
                                "Analyse each shape's 4D rotation before guessing.\n"
                                f"(Create 'interval_{block_idx}.txt' to customise this message)\n\n"
                                "Click Continue when ready.")
                        y = HEIGHT//2-100
                        for line in text.split('\n'):
                            s=big_font.render(line,True,(255,255,255))
                            screen.blit(s,(WIDTH//2-s.get_width()//2,y)); y+=44
                        btn_continue.draw(screen,font)

                    # ---- QUIZ STATES ----
                    elif state in ("ANALYSIS","ANSWERING","FEEDBACK"):
                        layout_quiz()
                        yaw-=dy; roll-=dr
                        if not paused:
                            for i in range(6):
                                dips[i]=(dips[i]+d4*a4_variants[i][0])%360
                                tucks[i]=(tucks[i]+d4*a4_variants[i][1])%360
                                skews[i]=(skews[i]+d4*a4_variants[i][2])%360

                        vp=pygame.Surface((WIDTH,HEIGHT-300)); vp.fill((0,0,0))
                        if active_shape and axes_shape:
                            for sh in main_shapes:
                                sh.rotate(yaw,0,roll,dips[0],tucks[0],skews[0])
                                sh.shrink(ortho if mode=='Wireframe' else 0.001)
                            cellhl={i for i,b in enumerate(cell_buttons) if b.getsel()}
                            if state=="ANALYSIS":
                                if mode=='Wireframe':   renderers['Wireframe'].render(vp,main_shapes)
                                elif mode=='W-Shells':  renderers['W-Shells'].render(vp,main_shapes,target_w)
                                elif mode=='CellHl':    renderers['CellHl'].render(vp,main_shapes,opacity,cellhl,cell_colors)
                        screen.blit(vp,(0,0))
                        pygame.draw.line(screen,(100,100,100),(0,HEIGHT-300),(WIDTH,HEIGHT-300),2)

                        screen.blit(font.render(f"Assigned Mode: {mode}  |  User ID: {user_id}",
                                                True,(200,200,200)),(20,20))
                        screen.blit(big_font.render(f"Question {question_index+1} / {TOTAL_QUIZ_QUESTIONS}",
                                                    True,(255,255,100)),(20,60))

                        if mode=='CellHl':
                            layout_cell(); [b.draw(screen,font) for b in cell_buttons]

                        if state=="ANALYSIS":
                            btn_ready.draw(screen,font)
                            qt=big_font.render("Analyse the shape's rotation. Click 'Ready' when prepared to guess.",
                                            True,(255,255,255))
                            screen.blit(qt,(WIDTH//2-qt.get_width()//2,HEIGHT-200))

                        elif state in ("ANSWERING","FEEDBACK"):
                            ow=5*180+4*10; ox=WIDTH//2-ow//2
                            for i in range(1,6):
                                os=pygame.Surface((180,180))
                                origin_renderer.render(os,yaw,0,roll,dips[i],tucks[i],skews[i],0.001)
                                pygame.draw.rect(os,(50,50,50),os.get_rect(),2)
                                screen.blit(os,(ox+(i-1)*190,HEIGHT-280))
                            if state=="ANSWERING":
                                [b.draw(screen,font) for b in quiz_buttons]
                                btn_idk.draw(screen,font)
                            else:
                                fs=big_font.render(feedback_text,True,feedback_color)
                                screen.blit(fs,(WIDTH//2-fs.get_width()//2,HEIGHT-120))
                                btn_next.draw(screen,font)

                        ctrl_str=("4D Zoom" if mode=='Wireframe' else
                                "Transparency" if mode=='CellHl' else "4D Slicing")
                        cy=100
                        for line in ["Controls:","DRAG: Rotate 3D","SPACE: Pause/Unpause",
                                    "SCROLL (Unpaused): 4D Speed","SCROLL (Paused): 4D Angle",
                                    f"CTRL+SCROLL: {ctrl_str}","R: Reset"]:
                            screen.blit(font.render(line,True,(200,255,200)),(20,cy)); cy+=25

                    # ---- FREE MODE ----
                    elif state=="FREE_MODE":
                        # Live-update a4 from sliders
                        a4_correct = slider_a4()

                        yaw-=dy; roll-=dr
                        if not paused:
                            dips[0]=(dips[0]+d4*a4_correct[0])%360
                            tucks[0]=(tucks[0]+d4*a4_correct[1])%360
                            skews[0]=(skews[0]+d4*a4_correct[2])%360

                        vp_h=HEIGHT-FREE_HUD
                        vp=pygame.Surface((WIDTH,max(1,vp_h))); vp.fill((0,0,0))
                        if active_shape and axes_shape:
                            for sh in main_shapes:
                                sh.rotate(yaw,0,roll,dips[0],tucks[0],skews[0])
                                sh.shrink(ortho if mode=='Wireframe' else 0.001)
                            cellhl={i for i,b in enumerate(cell_buttons) if b.getsel()}
                            if mode=='Wireframe':   renderers['Wireframe'].render(vp,main_shapes)
                            elif mode=='W-Shells':  renderers['W-Shells'].render(vp,main_shapes,target_w)
                            elif mode=='CellHl':    renderers['CellHl'].render(vp,main_shapes,opacity,cellhl,cell_colors)
                        screen.blit(vp,(0,0))
                        pygame.draw.line(screen,(80,80,80),(0,vp_h),(WIDTH,vp_h),2)

                        # ---- Live origin indicator (top-right of viewport) ----
                        ORIG_SIZE = 160
                        orig_surf = pygame.Surface((ORIG_SIZE, ORIG_SIZE))
                        orig_surf.fill((10, 10, 20))
                        origin_renderer.render(orig_surf, yaw, 0, roll,
                                            dips[0], tucks[0], skews[0], 0.001)
                        pygame.draw.rect(orig_surf, (80, 80, 100), orig_surf.get_rect(), 2)
                        ox = WIDTH - ORIG_SIZE - 12
                        oy = 10
                        screen.blit(orig_surf, (ox, oy))
                        lbl = small_font.render("Current 4D spin", True, (160, 160, 200))
                        screen.blit(lbl, (ox + ORIG_SIZE//2 - lbl.get_width()//2,
                                        oy + ORIG_SIZE + 3))

                        # viewport overlays
                        title=big_font.render(
                            f"Free Exploration  ·  {SHAPE_NAMES[free_shape_idx]}  ·  {mode}",
                            True,(255,220,80))
                        screen.blit(title,(20,10))
                        screen.blit(font.render(f"User ID: {user_id}",True,(160,160,160)),(20,48))

                        # ---- HUD ----
                        layout_free()
                        hud_top = HEIGHT - FREE_HUD + 8

                        # Left labels
                        screen.blit(small_font.render("Mode:",  True,(180,180,180)),(10,hud_top+7))
                        screen.blit(small_font.render("Shape:", True,(180,180,180)),(10,hud_top+49))

                        for b in free_mode_btns:  b.draw(screen,small_font)
                        for b in free_shape_btns: b.draw(screen,small_font)

                        if mode=='CellHl':
                            layout_cell(); [b.draw(screen,font) for b in cell_buttons]

                        # Slider header
                        sh=small_font.render("4D Spin  (drag handles or click track)",
                                            True,(200,200,255))
                        screen.blit(sh,(sliders[0].x-10, hud_top+2))

                        for s in sliders: s.draw(screen,small_font)

                        # Hints – far right, vertically centred in HUD
                        ctrl_str=("4D Zoom" if mode=='Wireframe' else
                                "Transparency" if mode=='CellHl' else "4D Slicing")
                        hints=[
                            "DRAG viewport: Rotate 3D  |  SPACE: Pause  |  R: Reset",
                            f"SCROLL: 4D global speed   |  CTRL+SCROLL: {ctrl_str}",
                            "Sliders set each 4D axis independently",
                        ]
                        for hi,h in enumerate(hints):
                            hs=small_font.render(h,True,(160,220,160))
                            screen.blit(hs,(WIDTH-hs.get_width()-12, hud_top+6+hi*22))
                except Exception as e:
                    log_error(f"Rendering error (frame {frame_count}): {e}")
                    traceback.print_exc()

                pygame.display.flip()
                clock.tick(60)
                await asyncio.sleep(0)
            except Exception as e:
                log_error(f"Frame loop error (frame {frame_count}): {e}")
                traceback.print_exc()

        try:
            pygame.quit()
            log_debug("Pygame quit successfully")
        except Exception as e:
            log_error(f"Error during pygame.quit(): {e}")

    except Exception as e:
        log_error(f"Critical error: {e}")
        traceback.print_exc()
        if screen is not None:
            try: pygame.quit()
            except Exception: pass
        raise


def main():
    asyncio.run(main_async())

if __name__ == '__main__':
    main()