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


def try_import(name, fromlist):
    try:
        mod = __import__(name, fromlist=fromlist)
        print(f"OK: {name}", flush=True)
        return getattr(mod, fromlist[0])
    except Exception as e:
        print(f"FAIL: {name} — {e}", flush=True)
        traceback.print_exc()
        return None

Tesseract        = try_import('Tesseract',        ['Tesseract'])
Cube             = try_import('Cube',             ['Cube'])
Tetrahedron      = try_import('Tetrahedron',      ['Tetrahedron'])
ThreeAxis        = try_import('ThreeAxis',        ['ThreeAxis'])
FiveCell         = try_import('FiveCell',         ['FiveCell'])
SixteenCell      = try_import('SixteenCell',      ['SixteenCell'])
TriPrism         = try_import('TriPrism',         ['TriPrism'])
SquareAntiprisma = try_import('SquareAntiprisma', ['SquareAntiprisma'])
TetraBipyramid   = try_import('TetraBipyramid',   ['TetraBipyramid'])
WedgeCell        = try_import('WedgeCell',        ['WedgeCell'])
TutorialRenderer = try_import('MAINTutorial',     ['TutorialRenderer'])
WireframeRenderer= try_import('MAINWireframe',    ['WireframeRenderer'])
WShellRenderer   = try_import('MAINWShell',       ['WShellRenderer'])
_cellhl          = try_import('MAINCellHl',       ['CellHlRenderer'])
CellHlRenderer   = _cellhl
ToggleButton     = try_import('MAINCellHl',       ['ToggleButton'])
OriginRenderer   = try_import('OriginRenderer',   ['OriginRenderer'])

_CRITICAL = {
    'Tesseract': Tesseract, 'Cube': Cube, 'ThreeAxis': ThreeAxis,
    'TutorialRenderer': TutorialRenderer, 'WireframeRenderer': WireframeRenderer,
    'WShellRenderer': WShellRenderer, 'CellHlRenderer': CellHlRenderer,
    'ToggleButton': ToggleButton, 'OriginRenderer': OriginRenderer,
}
_FAILED_IMPORTS = [name for name, obj in _CRITICAL.items() if obj is None]

if _FAILED_IMPORTS:
    async def _show_error():
        pygame.init(); pygame.font.init()
        W, H = 900, 500
        screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("4D Visualizer – Import Error")
        font_big  = pygame.font.SysFont(None, 36)
        font_sm   = pygame.font.SysFont(None, 24)
        font_mono = pygame.font.SysFont("monospace", 20)
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: running = False
            screen.fill((10, 5, 20))
            t = font_big.render("Import Error – modules not found:", True, (255, 80, 80))
            screen.blit(t, (W//2 - t.get_width()//2, 40))
            for i, name in enumerate(_FAILED_IMPORTS):
                line = font_mono.render(f"  ✗  {name}", True, (255, 140, 60))
                screen.blit(line, (W//2 - 160, 100 + i*28))
            hint_lines = [
                "Make sure all .py module files are in the same folder as main.py",
                "and are included in your pygbag archive (visualizer4d.tar.gz).",
                "", "Expected files: Tesseract.py, Cube.py, Tetrahedron.py,",
                "ThreeAxis.py, FiveCell.py, SixteenCell.py, TriPrism.py,",
                "SquareAntiprisma.py, TetraBipyramid.py, WedgeCell.py,",
                "MAINTutorial.py, MAINWireframe.py, MAINWShell.py,",
                "MAINCellHl.py, OriginRenderer.py",
            ]
            y = 100 + len(_FAILED_IMPORTS)*28 + 30
            for line in hint_lines:
                s = font_sm.render(line, True, (160,160,180) if line else (0,0,0))
                screen.blit(s, (W//2 - s.get_width()//2, y)); y += 22
            pygame.display.flip(); clock.tick(30); await asyncio.sleep(0)
        pygame.quit()

    async def main_async():
        await _show_error()


TOTAL_QUIZ_QUESTIONS = 15

def log_debug(msg): print(f"[4D-DEBUG] {msg}", file=sys.stdout)
def log_error(msg):  print(f"[4D-ERROR] {msg}", file=sys.stderr)


# ============================================================
# Google Form
# HOW TO FIND ENTRY IDs:
#   1. Open your form → three-dot menu → "Get pre-filled link"
#   2. Fill a dummy value in every field → "Get link"
#   3. The URL contains ?entry.XXXXXXXXX=value for each field
#   4. Replace every REPLACE_* below with the real entry IDs
# ============================================================
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfXKygh8Wsv-MU_2u0bjt1eaExFICsbKm7SO-3a4s4O26NUPA/formResponse"

ENTRY_ORIGIN      = "entry.1314273606"
ENTRY_FAMILIARITY = "entry.441154203"
ENTRY_TUTO        = "entry.1880574806"
ENTRY_PRETIME     = "entry.645659725"
ENTRY_TUTOANATIME = "entry.1614115597"
ENTRY_TUTOANSTIME = "entry.1784483735"
ENTRY_MODEL       = "entry.668887448"

ENTRY_ANATIME = [
    "entry.355370598",  "entry.476768110",  "entry.626000791",  "entry.955976263",
    "entry.232825616",  "entry.2115909041", "entry.677281729",  "entry.1633786226",
    "entry.1335142925", "entry.1613074632", "entry.388610013",  "entry.158821835",
    "entry.77988818",   "entry.2061064430", "entry.1156148626",
]
ENTRY_ANSTIME = [
    "entry.768698020",  "entry.393448772",  "entry.1028203807", "entry.249457686",
    "entry.30999603",   "entry.2056975355", "entry.1462704473", "entry.1249863795",
    "entry.2029445584", "entry.1814780546", "entry.1528808670", "entry.29993410",
    "entry.1111111733", "entry.275793044",  "entry.1090488432",
]
ENTRY_READTIME= ["entry.1667660146", "entry.1444308924"]
ENTRY_OPTIONS = [
    "entry.1410714464", "entry.686195860",  "entry.1903582081", "entry.804227748",
    "entry.1552357830", "entry.985403343",  "entry.586354369",  "entry.1800343372",
    "entry.1753755800", "entry.1592964331", "entry.1488540948", "entry.1052334710",
    "entry.1647047385", "entry.1357756722", "entry.946570160",
]
ENTRY_ACC     = [
    "entry.1123870241", "entry.876441989",  "entry.107444736",  "entry.867773105",
    "entry.880663388",  "entry.167226558",  "entry.1839444534", "entry.1574794871",
    "entry.1105045680", "entry.1390440842", "entry.1808678547", "entry.20416211",
    "entry.2026122329", "entry.1113584818", "entry.764061028",
]
ENTRY_CHOICE  = [
    "entry.950980923",  "entry.2027806122", "entry.1679651366", "entry.639514842",
    "entry.1653941747", "entry.1251829575", "entry.1633190029", "entry.1044139991",
    "entry.1014351439", "entry.1714729522", "entry.1678345719", "entry.1045166073",
    "entry.279914678",  "entry.175768213",  "entry.2018112989",
]


# ============================================================
# Timing data collector
# ============================================================
class TimingData:
    def __init__(self):
        self.session_start = time.time()
        self.pretime       = 0.0
        self.tutoanatime   = 0.0
        self.tutoanstime   = 0.0
        self.tuto_result   = ""
        self.anatime       = [0.0] * TOTAL_QUIZ_QUESTIONS
        self.anstime       = [0.0] * TOTAL_QUIZ_QUESTIONS
        self.readtime      = [0.0, 0.0]
        self.options       = [""] * TOTAL_QUIZ_QUESTIONS
        self.acc           = [""] * TOTAL_QUIZ_QUESTIONS
        self.choice        = [""] * TOTAL_QUIZ_QUESTIONS
        self._ana_start    = None
        self._ans_start    = None
        self._tutoana_start= None
        self._tutoans_start= None
        self._read_start   = None
        self._read_idx     = None

    def mark_survey_done(self):
        self.pretime = round(time.time() - self.session_start, 2)

    def start_tuto_ana(self):  self._tutoana_start = time.time()
    def end_tuto_ana(self):
        if self._tutoana_start:
            self.tutoanatime = round(time.time() - self._tutoana_start, 2)

    def start_tuto_ans(self):  self._tutoans_start = time.time()
    def end_tuto_ans(self):
        if self._tutoans_start:
            self.tutoanstime = round(time.time() - self._tutoans_start, 2)

    def start_ana(self, qi):   self._ana_start = time.time()
    def end_ana(self, qi):
        if self._ana_start and 0 <= qi < TOTAL_QUIZ_QUESTIONS:
            self.anatime[qi] = round(time.time() - self._ana_start, 2)

    def start_ans(self, qi):   self._ans_start = time.time()
    def end_ans(self, qi):
        if self._ans_start and 0 <= qi < TOTAL_QUIZ_QUESTIONS:
            self.anstime[qi] = round(time.time() - self._ans_start, 2)

    def start_read(self, ri):
        self._read_start = time.time(); self._read_idx = ri

    def end_read(self):
        if self._read_start is not None and self._read_idx is not None:
            ri = self._read_idx
            if ri < len(self.readtime):
                self.readtime[ri] = round(time.time() - self._read_start, 2)

    def record_answer(self, qi, chosen_label, is_correct, is_idk, shape_name="", a4_variants=None, correct_idx=None):
        # options encodes question context: shape + all 5 presented a4 tuples + which was correct
        if a4_variants:
            variants_str = "|".join(
                f"O{i}:({v[0]:.3f},{v[1]:.3f},{v[2]:.3f})" for i, v in enumerate(a4_variants[1:], 1)
            )
            correct_str = f"|correct=O{correct_idx}" if correct_idx is not None else ""
            self.options[qi] = f"{shape_name}|{variants_str}{correct_str}"
        else:
            self.options[qi] = shape_name
        self.choice[qi]  = chosen_label
        if is_idk:         self.acc[qi] = "Didn't know"
        elif is_correct:   self.acc[qi] = "Correct"
        else:              self.acc[qi] = "Wrong"


# ============================================================
# Google Form submission helpers
# ============================================================
async def _post_form(data: dict):
    if any("REPLACE_" in k for k in data.keys()):
        log_debug("Form entry IDs not configured – skipping submission.")
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
            js.fetch(FORM_URL, to_js(opts))
        else:
            import urllib.request, threading
            enc = urllib.parse.urlencode(data).encode('utf-8')
            req = urllib.request.Request(FORM_URL, data=enc)
            def _send():
                try: urllib.request.urlopen(req, timeout=5)
                except Exception as e: log_error(f"Form submit error: {e}")
            threading.Thread(target=_send, daemon=True).start()
    except Exception as e:
        log_error(f"Failed to submit form: {e}")


async def submit_survey(td: TimingData, origin: str, familiarity: int):
    await _post_form({ENTRY_ORIGIN: origin, ENTRY_FAMILIARITY: str(familiarity)})


async def submit_full_session(td: TimingData, model: str,
                               origin: str, familiarity: int, user_id: int):
    data = {
        ENTRY_ORIGIN:      origin,
        ENTRY_FAMILIARITY: str(familiarity),
        ENTRY_TUTO:        td.tuto_result,
        ENTRY_PRETIME:     str(td.pretime),
        ENTRY_TUTOANATIME: str(td.tutoanatime),
        ENTRY_TUTOANSTIME: str(td.tutoanstime),
        ENTRY_MODEL:       model,
    }
    for i in range(TOTAL_QUIZ_QUESTIONS):
        data[ENTRY_ANATIME[i]] = str(td.anatime[i])
        data[ENTRY_ANSTIME[i]] = str(td.anstime[i])
        data[ENTRY_OPTIONS[i]] = td.options[i]
        data[ENTRY_ACC[i]]     = td.acc[i]
        data[ENTRY_CHOICE[i]]  = td.choice[i]
    for i in range(len(td.readtime)):
        data[ENTRY_READTIME[i]] = str(td.readtime[i])
    await _post_form(data)


# ============================================================
# TutorialOriginRenderer
# ============================================================
class TutorialOriginRenderer(OriginRenderer):
    def render(self, surface, yaw, pitch, roll, dip, tuck, skew, ortho):
        surface.fill((15, 15, 15))
        self.axis.rotate(yaw, pitch, roll, dip, tuck, skew)
        self.axis.shrink(ortho)
        for v in self.axis.edges.adj:
            if v < 0:
                n = list(self.axis.edges.adj[v])
                if len(n) == 2:
                    p1 = self.axis.ov[n[0]]; p2 = self.axis.ov[n[1]]
                    pygame.draw.line(surface, (80,80,80),
                        (self.WIDTH//2+round(p1[0]), self.HEIGHT//2+round(p1[1])),
                        (self.WIDTH//2+round(p2[0]), self.HEIGHT//2+round(p2[1])), 1)
        for p in range(len(self.axis.ov)):
            text = self.axis.getText(p)
            if text and text.lower() != 'w':
                z = self.axis.ov[p][2]; w = self.axis.ov[p][3]
                g_val = 127 + round(z * self.tuning)
                d_val = round((w+w) * self.tuning)
                r_c = max(0, min(255, int(g_val + d_val)))
                b_c = max(0, min(255, int(g_val - d_val)))
                g_c = max(0, min(255, int(g_val)))
                sx = self.WIDTH//2 + round(self.axis.ov[p][0])
                sy = self.HEIGHT//2 + round(self.axis.ov[p][1])
                pygame.draw.circle(surface, (r_c, g_c, b_c), (sx, sy), 6)
                text_surf = self.font.render(text, True, (200,200,200))
                surface.blit(text_surf, (sx-3, sy-6))


# ============================================================
# Draggable Slider
# ============================================================
class Slider:
    TRACK_H       = 4;  HANDLE_R = 9
    COLOR_TRACK   = (70, 70, 90);   COLOR_FILL    = (100, 160, 255)
    COLOR_HANDLE  = (200, 220, 255); COLOR_HANDLE_HOT = (255, 255, 120)
    COLOR_LABEL   = (180, 180, 200); COLOR_VALUE   = (220, 220, 255)

    def __init__(self, x, y, w, label, min_val, max_val, init_val):
        self.x=x; self.y=y; self.w=w; self.label=label
        self.min_val=float(min_val); self.max_val=float(max_val)
        self.value=float(init_val); self._drag=False

    def _val_to_px(self):
        t=(self.value-self.min_val)/(self.max_val-self.min_val)
        return int(self.x+t*self.w)

    def _px_to_val(self, px):
        t=max(0.0,min(1.0,(px-self.x)/self.w))
        return self.min_val+t*(self.max_val-self.min_val)

    def _hit(self, pos):
        return math.hypot(pos[0]-self._val_to_px(), pos[1]-self.y) <= self.HANDLE_R+4

    def _on_track(self, pos):
        return self.x<=pos[0]<=self.x+self.w and abs(pos[1]-self.y)<=self.HANDLE_R+6

    @property
    def is_dragging(self): return self._drag

    def handle_event(self, event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self._hit(event.pos) or self._on_track(event.pos):
                self.value=self._px_to_val(event.pos[0]); self._drag=True; return True
        elif event.type==pygame.MOUSEBUTTONUP and event.button==1:
            if self._drag: self._drag=False; return True
        elif event.type==pygame.MOUSEMOTION:
            if self._drag: self.value=self._px_to_val(event.pos[0]); return True
        return False

    def draw(self, surface, font):
        lbl=font.render(self.label,True,self.COLOR_LABEL)
        surface.blit(lbl,(self.x-lbl.get_width()-8,self.y-lbl.get_height()//2))
        pygame.draw.rect(surface,self.COLOR_TRACK,(self.x,self.y-self.TRACK_H//2,self.w,self.TRACK_H),border_radius=2)
        fw=self._val_to_px()-self.x
        if fw>0:
            pygame.draw.rect(surface,self.COLOR_FILL,(self.x,self.y-self.TRACK_H//2,fw,self.TRACK_H),border_radius=2)
        hx=self._val_to_px()
        col=self.COLOR_HANDLE_HOT if self._drag else self.COLOR_HANDLE
        pygame.draw.circle(surface,col,(hx,self.y),self.HANDLE_R)
        pygame.draw.circle(surface,(40,40,60),(hx,self.y),self.HANDLE_R,2)
        vs=font.render(f"{self.value:+.3f}",True,self.COLOR_VALUE)
        surface.blit(vs,(self.x+self.w+8,self.y-vs.get_height()//2))


# ============================================================
# Dropdown
# ============================================================
class Dropdown:
    BG=(40,40,60); BG_OPEN=(50,50,75); BG_HOT=(70,70,100)
    BG_SEL=(80,140,220); BORDER=(100,100,140); TEXT=(210,210,230); ARROW=(180,180,220)

    def __init__(self, x, y, w, h, options, colors=None):
        self.x,self.y,self.w,self.h=x,y,w,h
        self.options=options; self.colors=colors or {}
        self.selected=0; self.open=False; self._hover=-1

    def _header_rect(self): return pygame.Rect(self.x,self.y,self.w,self.h)
    def _item_rect(self,i): return pygame.Rect(self.x,self.y-(len(self.options)-i)*self.h,self.w,self.h)

    def handle_event(self, event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self._header_rect().collidepoint(event.pos):
                self.open=not self.open; return True
            if self.open:
                for i in range(len(self.options)):
                    if self._item_rect(i).collidepoint(event.pos):
                        self.selected=i; self.open=False; return "CHANGED"
                self.open=False; return True
        elif event.type==pygame.MOUSEMOTION and self.open:
            self._hover=-1
            for i in range(len(self.options)):
                if self._item_rect(i).collidepoint(event.pos): self._hover=i; return True
        return False

    def draw(self, surface, font):
        hr=self._header_rect()
        col=self.colors.get(self.selected,(120,120,180))
        hbg=tuple(min(255,int(c*0.4+20)) for c in col)
        pygame.draw.rect(surface,hbg,hr,border_radius=5)
        pygame.draw.rect(surface,self.BORDER,hr,1,border_radius=5)
        pygame.draw.rect(surface,col,(hr.x+4,hr.y+4,10,hr.h-8),border_radius=2)
        txt=font.render(self.options[self.selected],True,self.TEXT)
        surface.blit(txt,(hr.x+20,hr.centery-txt.get_height()//2))
        ax=hr.right-14; ay=hr.centery; d=4
        pts=[(ax-d,ay+d//2),(ax+d,ay+d//2),(ax,ay-d//2)] if self.open else [(ax-d,ay-d//2),(ax+d,ay-d//2),(ax,ay+d//2)]
        pygame.draw.polygon(surface,self.ARROW,pts)
        if self.open:
            for i,opt in enumerate(self.options):
                ir=self._item_rect(i)
                bg=self.BG_SEL if i==self.selected else (self.BG_HOT if i==self._hover else self.BG_OPEN)
                pygame.draw.rect(surface,bg,ir,border_radius=3)
                pygame.draw.rect(surface,self.BORDER,ir,1,border_radius=3)
                c=self.colors.get(i,(120,120,180))
                pygame.draw.rect(surface,c,(ir.x+4,ir.y+4,10,ir.h-8),border_radius=2)
                t=font.render(opt,True,self.TEXT)
                surface.blit(t,(ir.x+20,ir.centery-t.get_height()//2))

    @property
    def is_open(self): return self.open
    def close(self): self.open=False


# ============================================================
# Radio button group
# ============================================================
class RadioGroup:
    UNSEL_COL=(60,60,80); SEL_COL=(80,150,255); HOVER_COL=(90,90,110)
    TEXT_COL=(220,220,240); SEL_TEXT=(255,255,255)
    BORDER_COL=(120,120,160); SEL_BORDER=(140,180,255)

    def __init__(self, options, x, y, w=220, h=44, gap=10):
        self.options=options; self.x,self.y=x,y; self.w,self.h=w,h
        self.gap=gap; self.selected=None; self._hover=None

    def total_height(self): return len(self.options)*(self.h+self.gap)-self.gap
    def _rect(self,i): return pygame.Rect(self.x,self.y+i*(self.h+self.gap),self.w,self.h)

    def handle_event(self, event):
        if event.type==pygame.MOUSEMOTION:
            self._hover=None
            for i in range(len(self.options)):
                if self._rect(i).collidepoint(event.pos): self._hover=i
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for i in range(len(self.options)):
                if self._rect(i).collidepoint(event.pos): self.selected=i; return True
        return False

    def draw(self, surface, font):
        for i,opt in enumerate(self.options):
            r=self._rect(i); sel=(self.selected==i); hot=(self._hover==i)
            bg=self.SEL_COL if sel else (self.HOVER_COL if hot else self.UNSEL_COL)
            bc=self.SEL_BORDER if sel else self.BORDER_COL
            pygame.draw.rect(surface,bg,r,border_radius=8)
            pygame.draw.rect(surface,bc,r,2,border_radius=8)
            cx=r.x+18; cy=r.centery
            pygame.draw.circle(surface,bc,(cx,cy),8,2)
            if sel: pygame.draw.circle(surface,self.SEL_COL,(cx,cy),5)
            txt=font.render(opt,True,self.SEL_TEXT if sel else self.TEXT_COL)
            surface.blit(txt,(r.x+36,r.centery-txt.get_height()//2))


# ============================================================
# Main
# ============================================================
async def main_async():
    screen = None
    try:
        log_debug("Initialising pygame...")
        pygame.init(); pygame.font.init()

        WIDTH, HEIGHT = 1200, 800
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("4D Axis Quiz Platform")

        clock      = pygame.time.Clock()
        font       = pygame.font.SysFont(None, 24)
        big_font   = pygame.font.SysFont(None, 36)
        huge_font  = pygame.font.SysFont(None, 52)
        small_font = pygame.font.SysFont(None, 20)

        # ------------------------------------------------------------------
        # Session
        # ------------------------------------------------------------------
        user_id = random.randint(10000, 99999)  # Unique session ID
        assigned_mode = "CellHl"  # Default fallback
        
        # Background task to fetch balancing counts from spreadsheet (non-blocking)
        async def fetch_balancing_counts():
            """Background task to fetch balancing counts from spreadsheet."""
            nonlocal assigned_mode, mode
            try:
                if sys.platform == 'emscripten':
                    import js
                    BALANCING_URL = "https://docs.google.com/spreadsheets/d/1aDEtjzNG4zhUMsXh9k98M5nmLQAA96tAxrOQ60wC2lY/export?format=csv&gid=65633586"
                    resp = await js.fetch(BALANCING_URL)
                    if resp.ok:
                        text = await resp.text()
                        lines = text.strip().split('\n')
                        if lines:
                            first_line = lines[0]
                            # Parse CSV: handle quoted and unquoted values
                            parts = [p.strip().strip('"\'') for p in first_line.split(',')]
                            log_debug(f"Sheet raw line: {first_line}")
                            log_debug(f"Sheet parsed: {parts}")
                            
                            if len(parts) >= 5:
                                try:
                                    w_cnt = int(parts[2])
                                    s_cnt = int(parts[3])
                                    c_cnt = int(parts[4])
                                    counts = [(w_cnt, 'Wireframe'), (s_cnt, 'W-Shells'), (c_cnt, 'CellHl')]
                                    counts.sort(key=lambda x: x[0])
                                    new_mode = counts[0][1]
                                    # Update mode immediately (happens during startup)
                                    assigned_mode = new_mode
                                    mode = new_mode
                                    log_debug(f"Balancing fetched: W={w_cnt}, S={s_cnt}, C={c_cnt} → assigned {new_mode}")
                                except (ValueError, IndexError) as e:
                                    log_debug(f"Could not parse counts: {e}, using random")
                                    assigned_mode = random.choice(['Wireframe', 'W-Shells', 'CellHl'])
                                    mode = assigned_mode
                    else:
                        log_debug(f"Fetch failed with status {resp.status}, using random")
                        assigned_mode = random.choice(['Wireframe', 'W-Shells', 'CellHl'])
                        mode = assigned_mode
                else:
                    # Local desktop: use truly random (no seed)
                    assigned_mode = random.choice(['Wireframe', 'W-Shells', 'CellHl'])
                    mode = assigned_mode
                    log_debug(f"Local mode (random): {assigned_mode}")
            except Exception as e:
                log_debug(f"Balancing fetch background task failed: {e}")
                assigned_mode = random.choice(['Wireframe', 'W-Shells', 'CellHl'])
                mode = assigned_mode
        
        # Fire off the background fetch task immediately (non-blocking)
        balancing_task = asyncio.create_task(fetch_balancing_counts())
        
        state         = "CONSENT"

        # Timing
        td = TimingData()

        # Survey results (needed for final submit)
        survey_origin          = ""
        survey_familiarity_val = 1
        survey_source          = None
        survey_familiarity     = None

        # Tutorial state
        tutorial_sub           = "WATCH"
        tutorial_angle         = 0.0
        tutorial_paused        = False
        tutorial_speed         = 0.0
        tutorial_mouse_yaw     = 0.0
        tutorial_dragging      = False
        tutorial_lastx         = 0
        tutorial_drag_inverted = False
        tutorial_answered      = False
        tutorial_answer        = None
        TUTORIAL_CORRECT       = "xz"

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
        drag_inverted  = False
        paused         = False
        togglescroll   = True
        ortho          = 0.001

        show_three_axis = True   # ThreeAxis overlay inside viewport
        show_4d_overlay = True   # OriginRenderer corner window

        free_shape_idx = 0
        read_counter   = 0

        renderers = {
            'Wireframe': WireframeRenderer(WIDTH, HEIGHT-300, a4=a4_correct),
            'W-Shells':  WShellRenderer  (WIDTH, HEIGHT-300, a4=a4_correct),
            'CellHl':    CellHlRenderer  (WIDTH, HEIGHT-300, a4=a4_correct),
            'Tutorial':  TutorialRenderer(WIDTH, HEIGHT-300),
        }
        tutorial_origin_renderer = TutorialOriginRenderer(180, 180, size=50)
        origin_renderer          = OriginRenderer(180, 180, size=50)

        SHAPE_NAMES = ["Tesseract","5-Cell","16-Cell","Tri-Prism",
                       "Sq-Antiprism","Tetra-Bipyramid","Wedge-Cell"]
        SHAPE_COLS  = {
            0:(120,80,200),1:(200,80,120),2:(80,200,200),
            3:(200,150,80),4:(80,180,120),5:(150,120,200),6:(180,80,80)
        }
        FREE_MODES = ['Wireframe','W-Shells','CellHl']

        active_shape = None; axes_shape = None
        main_shapes  = []; cell_buttons = []; cell_colors = {}
        tutorial_cube = None; tutorial_shapes = []

        target_w = 0.0; opacity = 1.0
        feedback_text = ""; feedback_color = (255,255,255)
        mouse_history = [(0,0)]*5
        frame_count   = 0

        FREE_HUD = 170
        SLIDER_W = 220

        sliders = [
            Slider(0,0,SLIDER_W,"XW",-0.30,0.30,0.10),
            Slider(0,0,SLIDER_W,"YW",-0.30,0.30,0.05),
            Slider(0,0,SLIDER_W,"ZW",-0.30,0.30,0.02),
        ]
        def slider_a4(): return tuple(s.value for s in sliders)

        SURVEY_SOURCES     = ["School","Blog or article","Friend / Referral","Other"]
        SURVEY_FAMILIARITY_OPTS = ["1 - Never heard of it","2 - Heard of it","3 - Some reading",
                                   "4 - Comfortable","5 - Expert"]
        survey_source_radio = RadioGroup(SURVEY_SOURCES,        0,0,w=300,h=42,gap=8)
        survey_fam_radio    = RadioGroup(SURVEY_FAMILIARITY_OPTS,0,0,w=300,h=42,gap=8)
        btn_survey_next     = ToggleButton(0,0,200,44,"Continue ->",(80,160,80))

        btn_yes = ToggleButton(0,0,280,52,"Yes - I consent to participate",(70,170,70))
        btn_no  = ToggleButton(0,0,280,52,"No - take me to free exploration",(170,70,70))

        TUTORIAL_BTN_LABELS = ["Option 1: X-Z","Option 2: Y-Z","Option 3: I don't know"]
        TUTORIAL_BTN_KEYS   = ["xz","yz","idk"]
        TUTORIAL_BTN_COLS   = [(80,140,220),(80,180,120),(180,100,100)]
        tutorial_btns = [ToggleButton(0,0,200,38,TUTORIAL_BTN_LABELS[i],TUTORIAL_BTN_COLS[i])
                         for i in range(3)]
        btn_tutorial_ready = ToggleButton(0,0,200,42,"Ready to Answer ->",(80,160,220))
        btn_tutorial_next  = ToggleButton(0,0,200,42,"Start Quiz ->",(80,180,80))

        btn_ready    = ToggleButton(0,0,200,40,"Ready to Answer",(100,200,100))
        btn_next     = ToggleButton(0,0,200,40,"Next Question",(100,200,100))
        btn_continue = ToggleButton(0,0,200,40,"Continue",(100,200,100))
        quiz_buttons = [ToggleButton(0,0,160,30,f"Option {i+1}",(150,150,150)) for i in range(5)]
        btn_idk      = ToggleButton(0,0,160,30,"I Don't Know",(200,100,100))

        # Mode buttons — three side-by-side in the HUD
        free_mode_btns = [
            ToggleButton(0,0,108,28,"Wireframe",(80,120,200)),
            ToggleButton(0,0,108,28,"W-Shells", (80,180,120)),
            ToggleButton(0,0,108,28,"CellHl",   (180,120,80)),
        ]
        shape_dropdown    = Dropdown(0,0,160,28,SHAPE_NAMES,SHAPE_COLS)
        btn_toggle_origin = ToggleButton(0,0,125,28,"ThreeAxis: ON",(80,120,160))
        btn_toggle_waxis  = ToggleButton(0,0,125,28,"4D Origin: ON",(80,160,120))
        btn_toggle_origin.selected = True
        btn_toggle_waxis.selected  = True

        # ------------------------------------------------------------------
        # Layout helpers
        # ------------------------------------------------------------------
        def layout_survey():
            col_x=WIDTH//2-150; q1_y=180
            survey_source_radio.x=col_x; survey_source_radio.y=q1_y
            q2_y=q1_y+survey_source_radio.total_height()+60
            survey_fam_radio.x=col_x; survey_fam_radio.y=q2_y
            btn_survey_next.rect.topleft=(WIDTH//2-100, q2_y+survey_fam_radio.total_height()+30)

        def layout_tutorial():
            btn_tutorial_ready.rect.topleft=(WIDTH//2-100, HEIGHT-100)
            total_w=3*200+2*30; bx=WIDTH//2-total_w//2
            for i,b in enumerate(tutorial_btns):
                b.rect.x=bx+i*230; b.rect.y=HEIGHT-120
            btn_tutorial_next.rect.topleft=(WIDTH//2-100, HEIGHT-65)

        def layout_quiz():
            btn_ready.rect.topleft    =(WIDTH//2-100, HEIGHT-56)
            btn_next.rect.topleft     =(WIDTH//2-100, HEIGHT-44)
            btn_continue.rect.topleft =(WIDTH//2-100, HEIGHT-56)
            total_bw=6*160+5*14; bx=WIDTH//2-total_bw//2
            for i,b in enumerate(quiz_buttons):
                b.rect.x=bx+i*174; b.rect.y=HEIGHT-68
            btn_idk.rect.x=bx+5*174; btn_idk.rect.y=HEIGHT-68

        def layout_cell(vp_h=None):
            rx=WIDTH-100
            for idx,b in enumerate(cell_buttons):
                b.rect.x=rx; b.rect.y=40+idx*30

        def layout_consent():
            cx=WIDTH//2-140; cy=HEIGHT-160
            btn_yes.rect.topleft=(cx,cy)
            btn_no.rect.topleft =(cx,cy+68)

        def layout_free():
            hud_top = HEIGHT - FREE_HUD + 8

            # Row 0: Mode buttons, left-aligned at x=90
            bx = 90
            for b in free_mode_btns:
                b.rect.x = bx; b.rect.y = hud_top
                bx += b.rect.width + 6

            # Row 1: Shape dropdown, then toggle buttons
            shape_dropdown.x = 90
            shape_dropdown.y = hud_top + 38
            btn_toggle_origin.rect.x = 90 + shape_dropdown.w + 12
            btn_toggle_origin.rect.y = hud_top + 38
            btn_toggle_waxis.rect.x  = btn_toggle_origin.rect.right + 8
            btn_toggle_waxis.rect.y  = hud_top + 38

            # Sliders on the right half
            slider_x = WIDTH // 2 + 20
            row_h    = 44
            for i,s in enumerate(sliders):
                s.x = slider_x
                s.y = hud_top + i * row_h + row_h // 2
                s.w = min(SLIDER_W, WIDTH - slider_x - 340)

        def update_free_sel():
            for i,b in enumerate(free_mode_btns): b.selected=(FREE_MODES[i]==mode)
            shape_dropdown.selected=free_shape_idx

        # ------------------------------------------------------------------
        # Shape helpers
        # ------------------------------------------------------------------
        def make_pool(o):
            s=100
            constructors=[
                (Tesseract,       s,     "Tesseract"),
                (FiveCell,        1.5*s, "FiveCell"),
                (SixteenCell,     1.3*s, "SixteenCell"),
                (TriPrism,        1.1*s, "TriPrism"),
                (SquareAntiprisma,1.1*s, "SquareAntiprisma"),
                (TetraBipyramid,  1.1*s, "TetraBipyramid"),
                (WedgeCell,       1.1*s, "WedgeCell"),
            ]
            pool=[]
            for cls,size,name in constructors:
                try: pool.append(cls(size,o,0,0,0,0))
                except Exception as e:
                    print(f"[4D] make_pool: {name} failed — {e}",flush=True)
                    traceback.print_exc(); pool.append(None)
            return pool

        def build_cell_btns(shape):
            lbls=getattr(shape,'cell_labels',[]); colors=getattr(shape,'cell_colors',{})
            btns=[ToggleButton(0,0,100,25,lbl,colors.get(i,(150,150,150))) for i,lbl in enumerate(lbls)]
            return btns,colors

        def rebuild_free_shape():
            nonlocal active_shape,axes_shape,main_shapes,cell_buttons,cell_colors
            pool=make_pool(ortho)
            shape=pool[free_shape_idx] if free_shape_idx<len(pool) else None
            if shape is None:
                shape=next((p for p in pool if p is not None),None)
            if shape is None: print("[4D] ALL shapes failed",flush=True); return
            active_shape=shape
            try: axes_shape=ThreeAxis(60,ortho,0,0,0)
            except Exception as e: print(f"[4D] ThreeAxis — {e}",flush=True); axes_shape=None
            main_shapes=[s for s in [active_shape,axes_shape] if s is not None]
            active_shape.rotate(0,0,0,0,0,0)
            if axes_shape: axes_shape.rotate(0,0,0,0,0,0)
            cell_buttons,cell_colors=build_cell_btns(active_shape)

        def enter_free(from_quiz=True):
            nonlocal state,dips,tucks,skews,a4_correct
            state="FREE_MODE"
            dips[0]=tucks[0]=skews[0]=0.0
            sliders[0].value=0.10; sliders[1].value=0.05; sliders[2].value=0.02
            a4_correct=slider_a4(); rebuild_free_shape(); update_free_sel()

        def enter_tutorial():
            nonlocal state,tutorial_cube,tutorial_shapes
            nonlocal tutorial_sub,tutorial_angle,tutorial_paused,tutorial_speed
            nonlocal tutorial_mouse_yaw,tutorial_dragging,tutorial_lastx
            nonlocal tutorial_answered,tutorial_answer
            state="TUTORIAL"; tutorial_sub="WATCH"
            tutorial_angle=0.0; tutorial_mouse_yaw=0.0
            tutorial_paused=False; tutorial_speed=0.0
            tutorial_dragging=False; tutorial_answered=False; tutorial_answer=None
            for b in tutorial_btns: b.selected=False
            btn_tutorial_ready.selected=False; btn_tutorial_next.selected=False
            tutorial_cube=Cube(120,0.0001,0,0,0)
            tutorial_cube.rotate(0,0,0,0,0,0)
            tutorial_shapes=[tutorial_cube]
            td.start_tuto_ana()

        # ------------------------------------------------------------------
        # Quiz question setup
        # ------------------------------------------------------------------
        def setup_question():
            nonlocal a4_correct,a4_variants,correct_idx
            nonlocal active_shape,axes_shape,main_shapes
            nonlocal dips,tucks,skews,q_start_time,q_type
            nonlocal cell_buttons,cell_colors,state,ortho

            qi=question_index%5
            if qi in (0,1):
                val=random.choice([0.10,0.15,0.08]); lst=[0.0,0.0,0.0]
                lst[random.randint(0,2)]=val; a4_correct=tuple(lst); q_type="Easy"
            elif qi in (2,3):
                v1,v2=random.choice([0.10,0.15]),random.choice([0.05,0.08])
                lst=[v1,v2,0.0]; random.shuffle(lst); a4_correct=tuple(lst); q_type="Medium"
            else:
                a4_correct=(0.10,0.05,0.02); q_type="Hard"

            ortho=0.001; pool=make_pool(ortho)
            if qi in (0,2):       active_shape=pool[0]
            elif qi in (1,3,4):   active_shape=random.choice([p for p in pool[1:] if p is not None])
            else:                  active_shape=random.choice([p for p in pool if p is not None])

            axes_shape=ThreeAxis(75,ortho,0,0,0)
            main_shapes=[active_shape,axes_shape]
            active_shape.rotate(0,0,0,0,0,0); axes_shape.rotate(0,0,0,0,0,0)
            cell_buttons,cell_colors=build_cell_btns(active_shape)

            correct_idx=random.randint(1,5); a4_variants[0]=a4_correct

            def diff_ok(v1,v2):
                n1=math.sqrt(sum(a*a for a in v1)); n2=math.sqrt(sum(b*b for b in v2))
                if n1<1e-5 or n2<1e-5: return abs(n1-n2)>1e-5
                return abs(sum((a/n1)*(b/n2) for a,b in zip(v1,v2)))<0.95

            generated=[a4_correct]; pre_seeded={}
            if qi in (0,1):
                wrong=[i for i in range(1,6) if i!=correct_idx]
                nz=[i for i,x in enumerate(a4_correct) if abs(x)>1e-5][0]
                val=a4_correct[nz]; other=[i for i in range(3) if i!=nz]
                nv=[0.0,0.0,0.0]; nv[random.choice(other)]=random.choice([val,-val])
                pre_seeded[wrong[0]]=tuple(nv)

            for i in range(1,6):
                if i==correct_idx: a4_variants[i]=a4_correct
                elif i in pre_seeded:
                    a4_variants[i]=pre_seeded[i]; generated.append(pre_seeded[i])
                else:
                    placed=False
                    for _ in range(100):
                        vals=list(a4_correct)
                        for _ in range(random.randint(1,3)):
                            op=random.choice(['shuffle','negate','add'])
                            if op=='shuffle': random.shuffle(vals)
                            elif op=='negate': vals[random.randint(0,2)]*=-1
                            else: vals[random.randint(0,2)]+=random.choice([-0.05,0.05,-0.1,0.1])
                        cand=tuple(vals)
                        if all(diff_ok(cand,ex) for ex in generated):
                            a4_variants[i]=cand; generated.append(cand); placed=True; break
                    if not placed:
                        vals=list(a4_correct); vals[i%3]+=0.15+i*0.05
                        a4_variants[i]=tuple(vals); generated.append(tuple(vals))

            for i in range(6): dips[i]=tucks[i]=skews[i]=0.0
            renderers['Wireframe'].a4=a4_correct
            renderers['W-Shells'].a4 =a4_correct
            renderers['CellHl'].a4   =a4_correct
            q_start_time=time.time(); state="ANALYSIS"
            td.start_ana(question_index)
            for b in quiz_buttons+[btn_idk,btn_next,btn_ready]: b.selected=False

        # ------------------------------------------------------------------
        # Initial layouts
        # ------------------------------------------------------------------
        layout_quiz(); layout_free(); layout_consent()
        layout_survey(); layout_tutorial()

        # ==================================================================
        # Main loop
        # ==================================================================
        running = True
        while running:
            try:
                frame_count+=1
                mouse_history.append(pygame.mouse.get_pos())
                if len(mouse_history)>5: mouse_history.pop(0)

                slider_hot      = any(s.is_dragging for s in sliders)
                pending_shape_idx = None

                for event in pygame.event.get():
                    ev_consumed = False
                    try:
                        if event.type==pygame.QUIT: running=False

                        elif event.type==pygame.VIDEORESIZE:
                            WIDTH,HEIGHT=event.size
                            screen=pygame.display.set_mode((WIDTH,HEIGHT),pygame.RESIZABLE)
                            xsens=WIDTH/180; ysens=HEIGHT/180
                            for r in renderers.values(): r.WIDTH=WIDTH; r.HEIGHT=HEIGHT-300
                            layout_quiz(); layout_free(); layout_consent()
                            layout_survey(); layout_tutorial()

                        # ---- CONSENT ----
                        if state=="CONSENT":
                            btn_yes.handle_event(event); btn_no.handle_event(event)
                            if btn_yes.selected: btn_yes.selected=False; state="SURVEY"
                            if btn_no.selected:  btn_no.selected=False;  enter_free(from_quiz=False)

                        # ---- SURVEY ----
                        elif state=="SURVEY":
                            survey_source_radio.handle_event(event)
                            survey_fam_radio.handle_event(event)
                            btn_survey_next.handle_event(event)
                            if btn_survey_next.selected:
                                btn_survey_next.selected=False
                                if (survey_source_radio.selected is not None and
                                        survey_fam_radio.selected is not None):
                                    survey_origin          = SURVEY_SOURCES[survey_source_radio.selected]
                                    survey_familiarity_val = survey_fam_radio.selected+1
                                    survey_source          = survey_origin
                                    survey_familiarity     = survey_familiarity_val
                                    td.mark_survey_done()
                                    enter_tutorial()

                        # ---- TUTORIAL ----
                        elif state=="TUTORIAL":
                            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                                ui_rects=([btn_tutorial_ready.rect,btn_tutorial_next.rect]+
                                          [b.rect for b in tutorial_btns])
                                if not any(r.collidepoint(event.pos) for r in ui_rects):
                                    tutorial_dragging=True; tutorial_lastx=event.pos[0]
                                    vp_centre_y=(HEIGHT-300)//2
                                    tutorial_drag_inverted=(event.pos[1]>vp_centre_y)
                            elif event.type==pygame.MOUSEBUTTONUP and event.button==1:
                                tutorial_dragging=False
                            elif event.type==pygame.MOUSEMOTION and tutorial_dragging:
                                dx=event.pos[0]-tutorial_lastx
                                if tutorial_drag_inverted: dx=-dx
                                tutorial_mouse_yaw+=dx*(180/WIDTH); tutorial_lastx=event.pos[0]
                            if event.type==pygame.MOUSEWHEEL:
                                if tutorial_paused: tutorial_angle+=event.y*5.0
                                else: tutorial_speed=max(-8.0,min(8.0,tutorial_speed+event.y*0.3))
                            if event.type==pygame.KEYDOWN:
                                if event.key==pygame.K_SPACE: tutorial_paused=not tutorial_paused
                                elif event.key==pygame.K_r: tutorial_angle=0.0; tutorial_mouse_yaw=0.0

                            if tutorial_sub=="WATCH":
                                btn_tutorial_ready.handle_event(event)
                                if btn_tutorial_ready.selected:
                                    btn_tutorial_ready.selected=False
                                    td.end_tuto_ana(); td.start_tuto_ans()
                                    tutorial_sub="ANSWER"
                            elif tutorial_sub=="ANSWER" and not tutorial_answered:
                                for i,b in enumerate(tutorial_btns):
                                    b.handle_event(event)
                                    if b.selected:
                                        tutorial_answered=True; tutorial_answer=TUTORIAL_BTN_KEYS[i]
                                        td.end_tuto_ans()
                                        if tutorial_answer==TUTORIAL_CORRECT: td.tuto_result="Correct"
                                        elif tutorial_answer=="idk":           td.tuto_result="Didn't know"
                                        else:                                  td.tuto_result="Wrong"
                                        for ob in tutorial_btns: ob.selected=False
                                        b.selected=True
                            elif tutorial_sub=="ANSWER" and tutorial_answered:
                                btn_tutorial_next.handle_event(event)
                                if btn_tutorial_next.selected:
                                    btn_tutorial_next.selected=False; state="INTERSTITIAL"

                        # ---- INTERSTITIAL ----
                        elif state=="INTERSTITIAL":
                            btn_continue.handle_event(event)
                            if btn_continue.selected:
                                btn_continue.selected=False
                                td.end_read()
                                setup_question()

                        # ---- ANALYSIS ----
                        elif state=="ANALYSIS":
                            btn_ready.handle_event(event)
                            if btn_ready.selected:
                                btn_ready.selected=False
                                td.end_ana(question_index); td.start_ans(question_index)
                                state="ANSWERING"
                            if mode=='CellHl':
                                for b in cell_buttons: b.handle_event(event)

                        # ---- ANSWERING ----
                        elif state=="ANSWERING":
                            for i,btn in enumerate(quiz_buttons):
                                btn.handle_event(event)
                                if btn.selected:
                                    td.end_ans(question_index)
                                    chosen_label=f"Option {i+1}"; is_correct=(i+1==correct_idx)
                                    shape_name=getattr(active_shape,'__class__',type(active_shape)).__name__
                                    td.record_answer(question_index,chosen_label,is_correct,False,shape_name,a4_variants,correct_idx)
                                    feedback_text="CORRECT! Axis mapping matches." if is_correct else f"WRONG. Correct was Option {correct_idx}."
                                    feedback_color=(100,255,100) if is_correct else (255,100,100)
                                    state="FEEDBACK"
                                    for ob in quiz_buttons+[btn_idk]: ob.selected=False
                                    btn.selected=True
                            btn_idk.handle_event(event)
                            if btn_idk.selected:
                                td.end_ans(question_index)
                                shape_name=getattr(active_shape,'__class__',type(active_shape)).__name__
                                td.record_answer(question_index,"Option 6",False,True,shape_name,a4_variants,correct_idx)
                                feedback_text=f"Correct was Option {correct_idx}."; feedback_color=(200,200,100)
                                state="FEEDBACK"
                                for ob in quiz_buttons: ob.selected=False
                                btn_idk.selected=True

                        # ---- FEEDBACK ----
                        elif state=="FEEDBACK":
                            btn_next.handle_event(event)
                            if btn_next.selected:
                                btn_next.selected=False; question_index+=1
                                if question_index>=TOTAL_QUIZ_QUESTIONS:
                                    asyncio.create_task(submit_full_session(
                                        td, mode, survey_origin, survey_familiarity_val, user_id))
                                    enter_free(from_quiz=True)
                                elif question_index%5==0:
                                    state="INTERSTITIAL"
                                    ri=question_index//5-1
                                    if ri<len(td.readtime): td.start_read(ri)
                                else:
                                    setup_question()

                        # ---- FREE MODE ----
                        elif state=="FREE_MODE":
                            ev_consumed=any(s.handle_event(event) for s in sliders)

                        # Shared free-mode controls (also handle when not consumed)
                        if state=="FREE_MODE" and not ev_consumed:
                            # Close dropdown on outside click
                            if (event.type==pygame.MOUSEBUTTONDOWN and shape_dropdown.is_open and
                                    not pygame.Rect(shape_dropdown.x,
                                                    shape_dropdown.y-len(SHAPE_NAMES)*shape_dropdown.h,
                                                    shape_dropdown.w,
                                                    shape_dropdown.h*(len(SHAPE_NAMES)+1)
                                                    ).collidepoint(event.pos)):
                                shape_dropdown.close(); ev_consumed=True

                            if not ev_consumed:
                                for i,b in enumerate(free_mode_btns):
                                    b.handle_event(event)
                                    if b.selected and FREE_MODES[i]!=mode:
                                        mode=FREE_MODES[i]; update_free_sel()

                                drop_res=shape_dropdown.handle_event(event)
                                if drop_res:
                                    ev_consumed=True
                                    if drop_res=="CHANGED" and shape_dropdown.selected!=free_shape_idx:
                                        pending_shape_idx=shape_dropdown.selected

                                prev_origin=btn_toggle_origin.selected
                                btn_toggle_origin.handle_event(event)
                                if btn_toggle_origin.selected!=prev_origin:
                                    show_three_axis=btn_toggle_origin.selected
                                    btn_toggle_origin.label="ThreeAxis: ON" if show_three_axis else "ThreeAxis: OFF"
                                    ev_consumed=True

                                prev_waxis=btn_toggle_waxis.selected
                                btn_toggle_waxis.handle_event(event)
                                if btn_toggle_waxis.selected!=prev_waxis:
                                    show_4d_overlay=btn_toggle_waxis.selected
                                    btn_toggle_waxis.label="4D Origin: ON" if show_4d_overlay else "4D Origin: OFF"
                                    ev_consumed=True

                                if mode=='CellHl':
                                    for b in cell_buttons: b.handle_event(event)

                        # ---- Viewport drag (all non-tutorial states) ----
                        slider_hot_now=any(s.is_dragging for s in sliders) or (state=="FREE_MODE" and ev_consumed)

                        if state!="TUTORIAL":
                            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                                if not slider_hot_now:
                                    all_ui=(quiz_buttons+cell_buttons+
                                            [btn_ready,btn_next,btn_continue,btn_idk,btn_no]+
                                            free_mode_btns+[btn_toggle_origin,btn_toggle_waxis])
                                    in_hud=(event.pos[1]>=HEIGHT-(FREE_HUD if state=="FREE_MODE" else 300))
                                    if not any(b.rect.collidepoint(event.pos) for b in all_ui) and not in_hud:
                                        dragging=True; lastx,lasty=event.pos; drag_start_pos=event.pos

                                        # ---- Z-axis split line fix ----
                                        # The origin/axes_shape is drawn centred on the viewport,
                                        # so the viewport centre in screen coords is:
                                        #   vp_centre_y = (HEIGHT - HUD) // 2
                                        # The ov[] positions are relative to that centre.
                                        # We search axes_shape for the label "z" and convert to
                                        # screen-Y. We take the TOPMOST z-endpoint so that dragging
                                        # above it (above the +Z tip) doesn't invert — only dragging
                                        # below the +Z tip inverts.
                                        if state=="FREE_MODE":
                                            vp_h_now=HEIGHT-300
                                        vp_centre_y=vp_h_now//2   # screen-Y of the rendered origin

                                        drag_inverted=False  # default: no invert
                                        if axes_shape and hasattr(axes_shape,'ov') and hasattr(axes_shape,'getText'):
                                            z_screen_ys=[]
                                            for _pi in range(len(axes_shape.ov)):
                                                _lbl=axes_shape.getText(_pi)
                                                if _lbl and _lbl.lower()=='z':
                                                    # ov[i][1] is the Y offset FROM the viewport centre
                                                    z_screen_ys.append(vp_centre_y+round(axes_shape.ov[_pi][1]))
                                            if z_screen_ys:
                                                # Topmost z tip on screen (smallest screen-Y value)
                                                z_top=min(z_screen_ys)
                                                drag_inverted=(event.pos[1]<z_top)
                                            else:
                                                drag_inverted=(event.pos[1]<vp_centre_y)
                                        else:
                                            drag_inverted=(event.pos[1]<vp_centre_y)

                            elif event.type==pygame.MOUSEBUTTONUP and event.button==1:
                                if dragging:
                                    dragging=False
                                    mx,my=event.pos
                                    dist=math.hypot(mx-drag_start_pos[0],my-drag_start_pos[1])
                                    omx,omy=mouse_history[0]
                                    vx=-(mx-omx)/(xsens*2.5); vy=-(my-omy)/(ysens*2.5)
                                    if drag_inverted: vx=-vx
                                    if dist>15:
                                        if abs(vx)>abs(vy) and abs(vx)>0.1: dy=vx; dr=0
                                        elif abs(vy)>0.1: dr=vy; dy=0
                                        else: dr=dy=0
                                    else: dr=dy=0
                                else: dr=dy=0

                            elif event.type==pygame.MOUSEMOTION and dragging and not slider_hot_now:
                                mx,my=event.pos
                                dx=-mx+lastx
                                if drag_inverted: dx=-dx
                                yaw+=dx/xsens; roll-=(my-lasty)/ysens
                                lastx,lasty=mx,my; dr=dy=0

                            if event.type==pygame.MOUSEWHEEL and state not in ("TUTORIAL",):
                                if togglescroll:
                                    sv=-event.y*3
                                    if paused:
                                        if state in ("ANALYSIS","ANSWERING","FEEDBACK"):
                                            if all(v is not None for v in a4_variants):
                                                for i in range(6):
                                                    dips[i]=(dips[i]+sv*a4_variants[i][0])%360
                                                    tucks[i]=(tucks[i]+sv*a4_variants[i][1])%360
                                                    skews[i]=(skews[i]+sv*a4_variants[i][2])%360
                                        elif state=="FREE_MODE":
                                            dips[0]=(dips[0]+sv*a4_correct[0])%360
                                            tucks[0]=(tucks[0]+sv*a4_correct[1])%360
                                            skews[0]=(skews[0]+sv*a4_correct[2])%360
                                    d4+=sv
                                else:
                                    if mode=='Wireframe':  ortho=max(0,min(0.005,ortho+event.y*0.0002))
                                    elif mode=='W-Shells': target_w+=event.y*10.0
                                    elif mode=='CellHl':   opacity=max(0.0,min(1.0,opacity+event.y*0.05))

                            if event.type==pygame.KEYDOWN and state not in ("SURVEY","CONSENT","TUTORIAL"):
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

                # Apply pending dropdown shape change
                if pending_shape_idx is not None and pending_shape_idx!=free_shape_idx:
                    free_shape_idx=pending_shape_idx
                    rebuild_free_shape(); update_free_sel()

                # ------------------------------------------------------------------
                # Auto-spin update
                # ------------------------------------------------------------------
                if not paused:
                    yaw+=dy; roll+=dr
                    if state in ("ANALYSIS","ANSWERING","FEEDBACK"):
                        if all(v is not None for v in a4_variants):
                            for i in range(6):
                                dips[i]=(dips[i]+d4*a4_variants[i][0])%360
                                tucks[i]=(tucks[i]+d4*a4_variants[i][1])%360
                                skews[i]=(skews[i]+d4*a4_variants[i][2])%360
                    elif state=="FREE_MODE":
                        dips[0]=(dips[0]+d4*a4_correct[0])%360
                        tucks[0]=(tucks[0]+d4*a4_correct[1])%360
                        skews[0]=(skews[0]+d4*a4_correct[2])%360

                if state=="TUTORIAL" and not tutorial_paused:
                    tutorial_angle=(tutorial_angle+tutorial_speed)%360

                try:
                    # ==============================================================
                    # RENDER
                    # ==============================================================
                    screen.fill((5,5,5))

                    # ---- CONSENT ----
                    if state=="CONSENT":
                        layout_consent()
                        t=huge_font.render("4D Axis Quiz Platform",True,(220,220,255))
                        screen.blit(t,(WIDTH//2-t.get_width()//2,40))
                        lines=[
                            "This study investigates how people perceive 4-dimensional rotations",
                            "through different visual representations.",
                            "","Participation is voluntary and fully anonymous.",
                            "You will view 4D shapes and identify which axis-indicator",
                            "matches the shape's 4D spin.",
                            "","Response times and answers will be recorded.",
                            "No personally identifying information is collected.",
                            "","Would you like to take part?",
                        ]
                        LINE_H=24; y=40+t.get_height()+30
                        for line in lines:
                            s=small_font.render(line,True,(200,200,200))
                            screen.blit(s,(WIDTH//2-s.get_width()//2,y))
                            y+=LINE_H if line else LINE_H//2
                        btn_yes.draw(screen,font); btn_no.draw(screen,font)

                    # ---- SURVEY ----
                    elif state=="SURVEY":
                        layout_survey()
                        t=big_font.render("A couple of quick questions before we begin",True,(220,220,255))
                        screen.blit(t,(WIDTH//2-t.get_width()//2,60))
                        q1_lbl=font.render("How did you hear about this study?",True,(200,220,255))
                        screen.blit(q1_lbl,(survey_source_radio.x,survey_source_radio.y-30))
                        survey_source_radio.draw(screen,font)
                        q2_lbl=font.render("How familiar are you with 4D geometry / polytopes?",True,(200,220,255))
                        screen.blit(q2_lbl,(survey_fam_radio.x,survey_fam_radio.y-30))
                        survey_fam_radio.draw(screen,font)
                        needs_both=(survey_source_radio.selected is None or survey_fam_radio.selected is None)
                        if needs_both:
                            hint=small_font.render("Please answer both questions to continue.",True,(255,180,80))
                            screen.blit(hint,(WIDTH//2-hint.get_width()//2,btn_survey_next.rect.y-28))
                        btn_survey_next.draw(screen,font)

                    # ---- TUTORIAL ----
                    elif state=="TUTORIAL":
                        layout_tutorial()

                        def get_tutorial_angles(M_deg,Sp_deg,Sr_deg):
                            M,Sp,Sr=math.radians(M_deg),math.radians(Sp_deg),math.radians(Sr_deg)
                            r11=math.cos(M)*math.cos(Sp)
                            r12=math.cos(M)*math.sin(Sp)*math.sin(Sr)-math.sin(M)*math.cos(Sr)
                            r13=math.cos(M)*math.sin(Sp)*math.cos(Sr)+math.sin(M)*math.sin(Sr)
                            r21=math.sin(M)*math.cos(Sp)
                            r23=math.sin(M)*math.sin(Sp)*math.cos(Sr)-math.cos(M)*math.sin(Sr)
                            r33=math.cos(Sp)*math.cos(Sr)
                            p_rad=math.asin(max(-1.0,min(1.0,r13)))
                            cp=math.cos(p_rad)
                            if abs(cp)>1e-6:
                                r_rad=math.atan2(-r23,r33)
                                y_rad=math.atan2(-r12,r11)
                            else:
                                r_rad=0; y_rad=math.atan2(r21,math.cos(math.radians(Sp_deg))*math.cos(Sr))
                            return math.degrees(y_rad),math.degrees(p_rad),math.degrees(r_rad)

                        y,p,r=get_tutorial_angles(tutorial_mouse_yaw,tutorial_angle,0)

                        if tutorial_sub=="WATCH":
                            vp_w=WIDTH; vp_h=HEIGHT-300
                            vp=pygame.Surface((vp_w,max(1,vp_h))); vp.fill((0,0,0))
                            tutorial_cube.rotate(y,p,r,0,0,0)
                            renderers['Tutorial'].render(vp,tutorial_shapes)
                            ay,ap,ar=get_tutorial_angles(tutorial_mouse_yaw,0,0)
                            osurf=pygame.Surface((180,180)); osurf.set_colorkey((15,15,15))
                            tutorial_origin_renderer.render(osurf,ay,ap,ar,0,0,0,0.001)
                            vp.blit(osurf,(vp_w//2-90,vp_h//2-90))
                            screen.blit(vp,(0,0))
                            pygame.draw.line(screen,(80,80,80),(0,vp_h),(WIDTH,vp_h),2)
                            title=big_font.render("Tutorial: Understanding the Answer Options",True,(255,220,80))
                            screen.blit(title,(WIDTH//2-title.get_width()//2,10))
                            instr_lines=[
                                "This cube is rotating in XZ — X sweeps into Z (use scroll wheel to spin).",
                                "In the quiz you'll see a 4D shape — pick the indicator matching its rotation.",
                                "DRAG left/right to rotate  |  SCROLL: speed  |  SPACE: pause  |  R: reset",
                            ]
                            iy=vp_h+10
                            for line in instr_lines:
                                s=small_font.render(line,True,(200,200,200))
                                screen.blit(s,(WIDTH//2-s.get_width()//2,iy)); iy+=22
                            btn_tutorial_ready.draw(screen,font)

                        else:
                            screen.fill((5,5,5))
                            title=big_font.render("Which indicator matches the rotation you just saw?",True,(255,220,80))
                            screen.blit(title,(WIDTH//2-title.get_width()//2,14))
                            sub=small_font.render("The cube was spinning so that X swept into Z — find the indicator showing that.",
                                                  True,(180,180,200))
                            screen.blit(sub,(WIDTH//2-sub.get_width()//2,55))
                            ORIG_SIZE=180; gap=50
                            total_ind_w=3*ORIG_SIZE+2*gap; ox_start=WIDTH//2-total_ind_w//2; oy_base=80
                            indicator_params=[
                                get_tutorial_angles(tutorial_mouse_yaw,tutorial_angle,0),
                                get_tutorial_angles(tutorial_mouse_yaw,0,tutorial_angle),
                                get_tutorial_angles(tutorial_mouse_yaw,0,0),
                            ]
                            ind_labels=["Option 1: X -> Z","Option 2: Y -> Z","Option 3: I don't know"]
                            for i,(iy2,ip2,ir2) in enumerate(indicator_params):
                                ox2=ox_start+i*(ORIG_SIZE+gap)
                                os=pygame.Surface((ORIG_SIZE,ORIG_SIZE)); os.fill((10,10,20))
                                tutorial_origin_renderer.render(os,iy2,ip2,ir2,0,0,0,0.001)
                                screen.blit(os,(ox2,oy_base))
                                lbl=small_font.render(ind_labels[i],True,(180,180,200))
                                screen.blit(lbl,(ox2+ORIG_SIZE//2-lbl.get_width()//2,oy_base+ORIG_SIZE+4))
                            if not tutorial_answered:
                                for b in tutorial_btns: b.draw(screen,font)
                            else:
                                correct=(tutorial_answer==TUTORIAL_CORRECT)
                                if correct:       fb="Correct! X sweeps into Z — Option 1 shows the X axis moving."; fb_col=(100,255,120)
                                elif tutorial_answer=="idk": fb="The answer is Option 1: X sweeps into Z, so the X indicator moves."; fb_col=(200,200,100)
                                else:             fb="Not quite — Option 1 is correct: the X axis sweeps into Z."; fb_col=(255,120,100)
                                fs=font.render(fb,True,fb_col)
                                screen.blit(fs,(WIDTH//2-fs.get_width()//2,HEIGHT-165))
                                exp=small_font.render("In the real quiz the 4D shape spins — pick the indicator whose axis motion matches.",True,(180,180,200))
                                screen.blit(exp,(WIDTH//2-exp.get_width()//2,HEIGHT-145))
                                for i,b in enumerate(tutorial_btns):
                                    b.draw(screen,font)
                                    if b.selected: pygame.draw.rect(screen,(255,255,100),b.rect,3,border_radius=6)
                                btn_tutorial_next.draw(screen,font)

                    # ---- INTERSTITIAL ----
                    elif state=="INTERSTITIAL":
                        layout_quiz()
                        block_idx=question_index//5
                        try:
                            with open(f"interval_{mode}_{block_idx}.txt") as f: text=f.read()
                        except Exception:
                            text=(f"Block {block_idx+1} of {TOTAL_QUIZ_QUESTIONS//5}"
                                  f"  --  {TOTAL_QUIZ_QUESTIONS} questions total\n\n"
                                  "Analyse each shape's 4D rotation before guessing.\n\n"
                                  "Click Continue when ready.")
                        y_pos=HEIGHT//2-100
                        for line in text.split('\n'):
                            s=big_font.render(line,True,(255,255,255))
                            screen.blit(s,(WIDTH//2-s.get_width()//2,y_pos)); y_pos+=44
                        btn_continue.draw(screen,font)

                    # ---- QUIZ STATES ----
                    elif state in ("ANALYSIS","ANSWERING","FEEDBACK"):
                        layout_quiz()
                        vp=pygame.Surface((WIDTH,HEIGHT-300)); vp.fill((0,0,0))
                        if active_shape and axes_shape:
                            for sh in main_shapes:
                                sh.rotate(yaw,0,roll,dips[0],tucks[0],skews[0])
                                sh.shrink(ortho if mode=='Wireframe' else 0.001)
                            cellhl={i for i,b in enumerate(cell_buttons) if b.getsel()}
                            if state=="ANALYSIS":
                                if mode=='Wireframe':  renderers['Wireframe'].render(vp,main_shapes)
                                elif mode=='W-Shells': renderers['W-Shells'].render(vp,main_shapes,target_w)
                                elif mode=='CellHl':   renderers['CellHl'].render(vp,main_shapes,opacity,cellhl,cell_colors)
                        screen.blit(vp,(0,0))
                        pygame.draw.line(screen,(100,100,100),(0,HEIGHT-300),(WIDTH,HEIGHT-300),2)

                        screen.blit(font.render(f"Assigned Mode: {mode}  |  User ID: {user_id}",True,(200,200,200)),(20,20))
                        screen.blit(big_font.render(f"Question {question_index+1} / {TOTAL_QUIZ_QUESTIONS}",True,(255,255,100)),(20,60))

                        # Timing display hidden from user (recorded silently)

                        if mode=='CellHl':
                            layout_cell(); [b.draw(screen,font) for b in cell_buttons]

                        if state=="ANALYSIS":
                            btn_ready.draw(screen,font)
                            qt=big_font.render("Analyse the shape's rotation. Click 'Ready' when prepared to guess.",True,(255,255,255))
                            screen.blit(qt,(WIDTH//2-qt.get_width()//2,HEIGHT-200))
                        elif state in ("ANSWERING","FEEDBACK"):
                            ow5=5*170+4*10; ox5=WIDTH//2-ow5//2
                            for i in range(1,6):
                                os=pygame.Surface((170,170))
                                origin_renderer.render(os,yaw,0,roll,dips[i],tucks[i],skews[i],0.001)
                                pygame.draw.rect(os,(50,50,50),os.get_rect(),2)
                                screen.blit(os,(ox5+(i-1)*180,HEIGHT-280))
                                lbl=small_font.render(f"Option {i}",True,(160,160,180))
                                screen.blit(lbl,(ox5+(i-1)*180+85-lbl.get_width()//2,HEIGHT-285))
                            if state=="ANSWERING":
                                [b.draw(screen,font) for b in quiz_buttons]; btn_idk.draw(screen,font)
                            else:
                                fs=big_font.render(feedback_text,True,feedback_color)
                                screen.blit(fs,(WIDTH//2-fs.get_width()//2,HEIGHT-100))
                                btn_next.draw(screen,font)

                        ctrl_str=("4D Zoom" if mode=='Wireframe' else "Transparency" if mode=='CellHl' else "4D Slicing")
                        cy2=100
                        for line in ["Controls:","DRAG: Rotate 3D","SPACE: Pause/Unpause",
                                     "SCROLL: 4D Speed","SCROLL (Paused): Angle",
                                     f"CTRL+SCROLL: {ctrl_str}","R: Reset"]:
                            screen.blit(font.render(line,True,(200,255,200)),(20,cy2)); cy2+=25

                    # ---- FREE MODE ----
                    elif state=="FREE_MODE":
                        a4_correct=slider_a4()
                        vp_h=HEIGHT-FREE_HUD
                        vp=pygame.Surface((WIDTH,max(1,vp_h))); vp.fill((0,0,0))

                        visible_shapes=[active_shape]+([axes_shape] if show_three_axis and axes_shape else [])
                        if active_shape:
                            for sh in visible_shapes:
                                sh.rotate(yaw,0,roll,dips[0],tucks[0],skews[0])
                                sh.shrink(ortho if mode=='Wireframe' else 0.001)
                            cellhl={i for i,b in enumerate(cell_buttons) if b.getsel()}
                            if mode=='Wireframe':  renderers['Wireframe'].render(vp,visible_shapes)
                            elif mode=='W-Shells': renderers['W-Shells'].render(vp,visible_shapes,target_w)
                            elif mode=='CellHl':   renderers['CellHl'].render(vp,visible_shapes,opacity,cellhl,cell_colors)

                        if show_4d_overlay:
                            osurf=pygame.Surface((140,140)); osurf.fill((0,0,0))
                            origin_renderer.render(osurf,yaw,0,roll,dips[0],tucks[0],skews[0],0.001)
                            vp.blit(osurf,(10,vp_h-140-10))

                        screen.blit(vp,(0,0))
                        pygame.draw.line(screen,(80,80,80),(0,vp_h),(WIDTH,vp_h),2)

                        title=big_font.render(f"Free Exploration  |  {SHAPE_NAMES[free_shape_idx]}  |  {mode}",True,(255,220,80))
                        screen.blit(title,(20,10))
                        screen.blit(font.render(f"User ID: {user_id}",True,(160,160,160)),(20,48))

                        layout_free()
                        hud_top=HEIGHT-FREE_HUD+8
                        screen.blit(small_font.render("Mode:", True,(180,180,180)),(10,hud_top+7))
                        screen.blit(small_font.render("Shape:",True,(180,180,180)),(10,hud_top+44))

                        for b in free_mode_btns: b.draw(screen,small_font)
                        shape_dropdown.draw(screen,small_font)
                        btn_toggle_origin.draw(screen,small_font)
                        btn_toggle_waxis.draw(screen,small_font)

                        if mode=='CellHl':
                            layout_cell(); [b.draw(screen,font) for b in cell_buttons]

                        sh_lbl=small_font.render("4D Spin  (drag handles or click track)",True,(200,200,255))
                        screen.blit(sh_lbl,(sliders[0].x-10,hud_top+2))
                        for s in sliders: s.draw(screen,small_font)

                        ctrl_str=("4D Zoom" if mode=='Wireframe' else "Transparency" if mode=='CellHl' else "4D Slicing")
                        hints=["DRAG viewport: Rotate 3D  |  SPACE: Pause  |  R: Reset",
                               f"SCROLL: 4D global speed   |  CTRL+SCROLL: {ctrl_str}",
                               "Sliders set each 4D axis independently"]
                        for hi,h in enumerate(hints):
                            hs=small_font.render(h,True,(160,220,160))
                            screen.blit(hs,(WIDTH-hs.get_width()-12,hud_top+6+hi*22))

                except Exception as e:
                    log_error(f"Rendering error (frame {frame_count}): {e}")
                    traceback.print_exc()

                pygame.display.flip()
                clock.tick(60)
                await asyncio.sleep(0)

            except Exception as e:
                log_error(f"Frame loop error (frame {frame_count}): {e}")
                traceback.print_exc()

        try: pygame.quit()
        except Exception as e: log_error(f"Error during pygame.quit(): {e}")

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