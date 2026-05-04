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
import os

random.seed(os.urandom(16))

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


TOTAL_QUIZ_QUESTIONS = 15

def log_debug(msg): print(f"[4D-DEBUG] {msg}", file=sys.stdout)
def log_error(msg):  print(f"[4D-ERROR] {msg}", file=sys.stderr)


# ============================================================
# Apps Script URL — single endpoint for both assign and submit
# ============================================================
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxn36iA-c-LsH8PXuRkAFV8-igNRG2XxAekVFVSSZxNkGSkDsjDQfpGg9_VB8ApdU9vNA/exec"

# REDO encoding: tutoanatime is stored as a NEGATIVE value for redo participants.
# The Apps Script / analysis code can detect is_redo by checking tutoanatime < 0.
# Actual tutoanatime magnitude is preserved (negated).
REDO_TUTOANATIME_SENTINEL = True   # flip sign of tutoanatime for redo users


def _is_valid_script_url(url):
    return (
        isinstance(url, str) and url
        and "/macros/s/" in url
        and url.endswith("/exec")
    )


def _parse_balancing_mode(text, exclude_wshells=False):
    """
    Parse the CSV balancing response.
    If exclude_wshells=True (redo participants), pick the least-used mode
    among Wireframe and CellHl only.
    """
    line = text.strip().strip('"\'').splitlines()[0].strip().strip('"\'')
    parts = [p.strip().strip('"\'') for p in line.split(",")]
    log_debug(f"Balancing CSV parts: {parts}")
    if len(parts) >= 5:
        w_cnt, s_cnt, c_cnt = int(parts[2]), int(parts[3]), int(parts[4])
    elif len(parts) >= 3:
        w_cnt, s_cnt, c_cnt = int(parts[0]), int(parts[1]), int(parts[2])
    else:
        raise ValueError(f"Expected 3 or 5+ CSV fields, got {len(parts)}: {parts}")

    if exclude_wshells:
        # Redo participants never get WShells; pick least-used of W/C
        counts = sorted([(w_cnt,"Wireframe"),(c_cnt,"CellHl")])
        chosen = counts[0][1]
        log_debug(f"Balancing (redo, no WShells): W={w_cnt}, C={c_cnt} -> {chosen}")
    else:
        counts = sorted([(w_cnt,"Wireframe"),(s_cnt,"WShells"),(c_cnt,"CellHl")])
        chosen = counts[0][1]
        log_debug(f"Balancing: W={w_cnt}, S={s_cnt}, C={c_cnt} -> {chosen}")
    return chosen


# ============================================================
# Timing data collector
# ============================================================
class TimingData:
    def __init__(self):
        self.session_start   = time.time()
        self.pretime         = 0.0
        self.tutoanatime     = 0.0   # negated for redo users (see encode_redo)
        self.tutoanstime     = 0.0
        self.tuto_result     = ""
        self.redo_feedback   = ""    # pre-quiz redo feedback (survey)
        self.postquiz_feedback = ""  # post-quiz experience feedback
        self.postquiz_model_feedback = "" # post-quiz visualisation/model feedback
        self.anatime         = [0.0] * TOTAL_QUIZ_QUESTIONS
        self.anstime         = [0.0] * TOTAL_QUIZ_QUESTIONS
        self.readtime        = [0.0, 0.0]
        self.options         = [""] * TOTAL_QUIZ_QUESTIONS
        self.acc             = [""] * TOTAL_QUIZ_QUESTIONS
        self.choice          = [""] * TOTAL_QUIZ_QUESTIONS
        self._ana_start      = None
        self._ans_start      = None
        self._tutoana_start  = None
        self._tutoans_start  = None
        self._read_start     = None
        self._read_idx       = None

    def mark_survey_done(self):
        self.pretime = round(time.time() - self.session_start, 2)

    def start_tuto_ana(self):  self._tutoana_start = time.time()
    def end_tuto_ana(self):
        if self._tutoana_start:
            self.tutoanatime = round(time.time() - self._tutoana_start, 2)

    def encode_redo(self):
        """Negate tutoanatime to encode redo presence. Safe to call multiple times."""
        if self.tutoanatime > 0:
            self.tutoanatime = -self.tutoanatime
        elif self.tutoanatime == 0:
            self.tutoanatime = -0.001  # sentinel for zero-duration edge case

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

    def record_answer(self, qi, chosen_label, is_correct, is_idk,
                      shape_name="", chosen_a4=None, correct_a4=None, correct_idx=None):
        def fmt3(t):
            if t is None: return "none"
            return f"({t[0]:.3f},{t[1]:.3f},{t[2]:.3f})"
        correct_str = f"correct:{fmt3(correct_a4)}"
        if is_idk:
            self.options[qi] = f"{shape_name}|{correct_str}|picked=IDK"
            self.choice[qi]  = chosen_label
            self.acc[qi]     = "Didn't know"
        elif is_correct:
            self.options[qi] = f"{shape_name}|{correct_str}|picked=O{correct_idx}"
            self.choice[qi]  = chosen_label
            self.acc[qi]     = "Correct"
        else:
            wrong_str = f"wrong_a4:{fmt3(chosen_a4)}"
            self.options[qi] = f"{shape_name}|{correct_str}|{wrong_str}|picked=O{correct_idx if is_correct else chosen_label}"
            self.choice[qi]  = chosen_label
            self.acc[qi]     = "Wrong"


# ============================================================
# Network helpers
# ============================================================

async def _get_request(url: str) -> str | None:
    try:
        if sys.platform == "emscripten":
            from js import window
            stamp = str(int(time.time() * 1000))
            result_key = f"__gas_result_{stamp}"
            window.eval(f"""
                window["{result_key}"] = "";
                fetch("{url}", {{redirect: "follow"}})
                    .then(function(r) {{ return r.text(); }})
                    .then(function(t) {{ window["{result_key}"] = t || "__EMPTY__"; }})
                    .catch(function(e) {{ window["{result_key}"] = "__FETCH_ERROR__:" + e; }});
            """)
            for _ in range(100):
                raw = str(window.eval(f'window["{result_key}"] || ""'))
                if raw:
                    log_debug(f"GET result ({url[:60]}): {raw[:120]}")
                    if raw.startswith("__FETCH_ERROR__") or raw == "__EMPTY__":
                        return None
                    return raw
                await asyncio.sleep(0.1)
            log_debug("GET timed out")
            return None

        import urllib.request
        with urllib.request.urlopen(url, timeout=8) as r:
            return r.read().decode("utf-8")

    except Exception as e:
        log_debug(f"GET failed: {e}")
        traceback.print_exc()
        return None


async def _fetch_balancing_text(is_redo=False):
    if not _is_valid_script_url(APPS_SCRIPT_URL):
        return None
    stamp = str(int(time.time() * 1000))
    redo_param = "&is_redo=true" if is_redo else ""
    url   = f"{APPS_SCRIPT_URL}?action=assign{redo_param}&_={stamp}"
    return await _get_request(url)


async def submit_full_session(td: TimingData, model: str,
                               origin: str, familiarity: int):
    if not _is_valid_script_url(APPS_SCRIPT_URL):
        log_error("submit_full_session: invalid Apps Script URL")
        return

    params = {
        "action":           "submit",
        "origin":           origin,
        "familiarity":      str(familiarity),
        "is_redo":          "true" if (td.redo_feedback or td.tutoanatime < 0) else "false",
        "redo_feedback":    td.redo_feedback,
        "tuto_result":      td.tuto_result,
        "pretime":          str(td.pretime),
        # tutoanatime is negative for redo users — encodes redo flag
        "tutoanatime":      str(td.tutoanatime),
        "tutoanstime":      str(td.tutoanstime),
        "model":            model,
        "postquiz_reading_feedback": td.postquiz_reading_feedback,
        "postquiz_model_feedback": td.postquiz_model_feedback,
    }
    for i in range(TOTAL_QUIZ_QUESTIONS):
        params[f"anatime_{i+1}"]  = str(td.anatime[i])
        params[f"anstime_{i+1}"]  = str(td.anstime[i])
        params[f"options_{i+1}"]  = td.options[i]
        params[f"acc_{i+1}"]      = td.acc[i]
        params[f"choice_{i+1}"]   = td.choice[i]
    params["readtime_1"] = str(td.readtime[0])
    params["readtime_2"] = str(td.readtime[1])

    url = APPS_SCRIPT_URL + "?" + urllib.parse.urlencode(params)
    log_debug(f"Submitting session, URL length = {len(url)}")
    result = await _get_request(url)
    if result and result.strip() == "ok":
        log_debug("Session submitted successfully")
    else:
        log_error(f"Session submission unexpected response: {result}")


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
                    p1 = self.axis.ov[n[0]]
                    p2 = self.axis.ov[n[1]]
                    pygame.draw.line(surface, (80, 80, 80),
                        (self._sx(surface, p1[0]), self._sy(surface, p1[1])),
                        (self._sx(surface, p2[0]), self._sy(surface, p2[1])), 1)
        for p in range(len(self.axis.ov)):
            text = self.axis.getText(p)
            if text and text.lower() != 'w':
                z = self.axis.ov[p][2]
                w = self.axis.ov[p][3]
                g_val = 127 + round(z * self.tuning)
                d_val = round((w+w) * self.tuning)
                r_c = max(0, min(255, int(g_val + d_val)))
                b_c = max(0, min(255, int(g_val - d_val)))
                g_c = max(0, min(255, int(g_val)))
                sx = self._sx(surface, self.axis.ov[p][0])
                sy = self._sy(surface, self.axis.ov[p][1])
                pygame.draw.circle(surface, (r_c, g_c, b_c), (sx, sy), 6)
                text_surf = self.font.render(text, True, (200, 200, 200))
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
# Interstitial text renderer
# ============================================================
def _wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current = []
    for word in words:
        test = " ".join(current + [word])
        if font.size(test)[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines if lines else [""]


def render_interstitial_text(screen, text, font, big_font, small_font,
                              WIDTH, HEIGHT, btn_continue, scroll_offset=0):
    MAX_W = min(WIDTH - 120, 860)
    COL_X = WIDTH // 2 - MAX_W // 2
    TOP_PAD = 40
    BTN_H   = btn_continue.rect.height + 32
    VIEWPORT_H = HEIGHT - BTN_H

    LINE_H_BIG   = big_font.get_height() + 4
    LINE_H_BODY  = font.get_height() + 3
    PARA_GAP     = 14

    paragraphs = text.split('\n')
    rendered_lines = []

    for pi, para in enumerate(paragraphs):
        para_strip = para.strip()
        if not para_strip:
            rendered_lines.append(None)
            continue
        use_big   = (pi == 0)
        use_small = para.startswith("  ") or para.startswith("\t")
        f   = big_font if use_big else (small_font if use_small else font)
        col = (255, 230, 80) if use_big else ((170, 200, 255) if use_small else (200, 200, 220))
        wrapped = _wrap_text(para_strip, f, MAX_W)
        for li, line in enumerate(wrapped):
            surf = f.render(line, True, col)
            rendered_lines.append((surf, use_big, li == 0 and pi > 0))

    total_h = TOP_PAD
    for entry in rendered_lines:
        if entry is None:
            total_h += PARA_GAP
        else:
            _, use_big, new_para = entry
            if new_para:
                total_h += PARA_GAP // 2
            total_h += LINE_H_BIG if use_big else LINE_H_BODY
    total_h += 20

    content_surf = pygame.Surface((WIDTH, max(total_h, VIEWPORT_H)))
    content_surf.fill((5, 5, 5))

    y = TOP_PAD
    for entry in rendered_lines:
        if entry is None:
            y += PARA_GAP
            continue
        surf, use_big, new_para = entry
        if new_para:
            y += PARA_GAP // 2
        lh = LINE_H_BIG if use_big else LINE_H_BODY
        content_surf.blit(surf, (COL_X + MAX_W // 2 - surf.get_width() // 2, y))
        y += lh

    max_scroll = max(0, total_h - VIEWPORT_H)
    scroll_offset = max(0, min(scroll_offset, max_scroll))

    screen.blit(content_surf, (0, 0), (0, scroll_offset, WIDTH, VIEWPORT_H))

    btn_continue.rect.topleft = (WIDTH // 2 - btn_continue.rect.width // 2, HEIGHT - BTN_H + 8)
    btn_continue.draw(screen, font)

    if max_scroll > 0:
        track_h = VIEWPORT_H - 20
        thumb_h = max(30, int(track_h * VIEWPORT_H / total_h))
        thumb_y = int((scroll_offset / max_scroll) * (track_h - thumb_h)) + 10
        pygame.draw.rect(screen, (60, 60, 80),   (WIDTH - 12, 10, 6, track_h), border_radius=3)
        pygame.draw.rect(screen, (140, 160, 220), (WIDTH - 12, thumb_y, 6, thumb_h), border_radius=3)

        if scroll_offset < max_scroll - 10:
            hint = small_font.render("scroll for more", True, (200, 200, 100))
            hint_rect = hint.get_rect(centerx=WIDTH // 2, y=VIEWPORT_H - hint.get_height() + 50)
            bg_rect = hint_rect.inflate(20, 6)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surf.fill((5, 5, 5, 180))
            screen.blit(bg_surf, bg_rect.topleft)
            screen.blit(hint, hint_rect)
    return max_scroll


# ============================================================
# Survey renderer — side-by-side two-column layout with scroll
# ============================================================
def render_survey(screen, font, big_font, small_font,
                  WIDTH, HEIGHT,
                  survey_source_radio, survey_fam_radio,
                  redo_section_enabled, redo_feedback_radio,
                  btn_redo_toggle, btn_survey_next,
                  scroll_offset, SURVEY_SOURCES):
    """
    Two-column layout:
      Left  column: Q1 (source) + optional redo section (toggled by a button)
      Right column: Q2 (familiarity)
    The Continue button is pinned to the bottom strip (screen-space rect).
    Returns current max_scroll.
    """
    BTN_H      = btn_survey_next.rect.height + 32
    VIEWPORT_H = HEIGHT - BTN_H

    PAD        = 40
    GAP        = 36
    COL_W      = (WIDTH - PAD * 2 - GAP) // 2
    LEFT_X     = PAD
    RIGHT_X    = PAD + COL_W + GAP
    LABEL_H    = font.get_height() + 8
    TOP_PAD    = 56
    GAP_SECT   = 20

    # --- compute column heights ---
    left_h = LABEL_H + survey_source_radio.total_height()
    # Redo toggle button
    left_h += GAP_SECT + btn_redo_toggle.rect.height
    if redo_section_enabled:
        left_h += GAP_SECT + LABEL_H + redo_feedback_radio.total_height()
    right_h = LABEL_H + survey_fam_radio.total_height()

    col_bottom = TOP_PAD + max(left_h, right_h)
    total_h    = col_bottom + 30

    # --- build content surface ---
    surf_h  = max(total_h, VIEWPORT_H)
    content = pygame.Surface((WIDTH, surf_h))
    content.fill((5, 5, 5))

    # Title
    t = big_font.render("A couple of quick questions before we begin", True, (220, 220, 255))
    content.blit(t, (WIDTH // 2 - t.get_width() // 2, 14))

    # ---- LEFT column ----
    q1_lbl = font.render("How did you hear about this study?", True, (200, 220, 255))
    content.blit(q1_lbl, (LEFT_X, TOP_PAD))
    survey_source_radio.x = LEFT_X
    survey_source_radio.y = TOP_PAD + LABEL_H
    survey_source_radio.w = COL_W
    survey_source_radio.draw(content, font)

    # Redo toggle button — position on content surface
    redo_toggle_y = TOP_PAD + LABEL_H + survey_source_radio.total_height() + GAP_SECT
    # We store the content-space rect for hit-testing (adjusted by scroll in event handler)
    btn_redo_toggle.rect.x = LEFT_X
    btn_redo_toggle.rect.y = redo_toggle_y
    btn_redo_toggle.draw(content, small_font)

    if redo_section_enabled:
        redo_q_y = redo_toggle_y + btn_redo_toggle.rect.height + GAP_SECT
        redo_lbl = font.render("How did the reading material affect you?", True, (255, 220, 120))
        content.blit(redo_lbl, (LEFT_X, redo_q_y))
        redo_feedback_radio.x = LEFT_X
        redo_feedback_radio.y = redo_q_y + LABEL_H
        redo_feedback_radio.w = COL_W
        redo_feedback_radio.draw(content, font)

    # ---- RIGHT column ----
    q2_lbl = font.render("Familiarity with 4D geometry / polytopes?", True, (200, 220, 255))
    content.blit(q2_lbl, (RIGHT_X, TOP_PAD))
    survey_fam_radio.x = RIGHT_X
    survey_fam_radio.y = TOP_PAD + LABEL_H
    survey_fam_radio.w = COL_W
    survey_fam_radio.draw(content, font)

    # Validation hint
    source_ok = survey_source_radio.selected is not None
    fam_ok    = survey_fam_radio.selected is not None
    redo_ok   = (not redo_section_enabled or redo_feedback_radio.selected is not None)
    if not (source_ok and fam_ok and redo_ok):
        if redo_section_enabled and not redo_ok:
            hint_str = "Please answer all questions to continue."
        else:
            hint_str = "Please answer both questions to continue."
        hint = small_font.render(hint_str, True, (255, 180, 80))
        content.blit(hint, (WIDTH // 2 - hint.get_width() // 2, col_bottom + 4))

    # --- scroll clamp ---
    max_scroll = max(0, total_h - VIEWPORT_H)
    scroll_offset = max(0, min(scroll_offset, max_scroll))

    # --- blit viewport ---
    screen.blit(content, (0, 0), (0, scroll_offset, WIDTH, VIEWPORT_H))

    # --- scrollbar ---
    if max_scroll > 0:
        track_h = VIEWPORT_H - 20
        thumb_h = max(30, int(track_h * VIEWPORT_H / total_h))
        thumb_y = int((scroll_offset / max_scroll) * (track_h - thumb_h)) + 10
        pygame.draw.rect(screen, (60, 60, 80),   (WIDTH - 12, 10, 6, track_h), border_radius=3)
        pygame.draw.rect(screen, (140, 160, 220), (WIDTH - 12, thumb_y, 6, thumb_h), border_radius=3)
        if scroll_offset < max_scroll - 10:
            hint2 = small_font.render("scroll for more ↓", True, (200, 200, 100))
            screen.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, VIEWPORT_H - 28))

    # --- pinned bottom strip: Continue button in SCREEN SPACE ---
    strip_y = VIEWPORT_H
    strip = pygame.Surface((WIDTH, BTN_H))
    strip.fill((5, 5, 5))
    pygame.draw.line(strip, (60, 60, 80), (0, 0), (WIDTH, 0), 1)
    # Draw the button on the strip surface at local coords, but keep rect in screen space
    btn_cx = WIDTH // 2 - btn_survey_next.rect.width // 2
    btn_cy_strip = 8   # local y on the strip
    # Update the rect to screen-space so handle_event works correctly
    btn_survey_next.rect.topleft = (btn_cx, strip_y + btn_cy_strip)
    # Draw offset onto strip
    saved_topleft = btn_survey_next.rect.topleft
    btn_survey_next.rect.topleft = (btn_cx, btn_cy_strip)
    btn_survey_next.draw(strip, font)
    btn_survey_next.rect.topleft = saved_topleft   # restore screen-space rect
    screen.blit(strip, (0, strip_y))

    return max_scroll


# ============================================================
# Post-quiz feedback renderer
# ============================================================
def render_postquiz(screen, font, big_font, small_font,
                    WIDTH, HEIGHT,
                    postquiz_reading_radio, postquiz_model_radio, btn_postquiz_next):
    screen.fill((5, 5, 5))

    title = big_font.render("Two last questions before free exploration", True, (255, 220, 80))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

    rg_w = min(460, WIDTH - 80)

    q1_lbl = font.render("How did the reading material affect you?", True, (200, 220, 255))
    screen.blit(q1_lbl, (WIDTH // 2 - q1_lbl.get_width() // 2, 96))
    postquiz_reading_radio.w = rg_w
    postquiz_reading_radio.x = WIDTH // 2 - rg_w // 2
    postquiz_reading_radio.y = 130
    postquiz_reading_radio.draw(screen, font)

    q2_y = postquiz_reading_radio.y + postquiz_reading_radio.total_height() + 34
    q2_lbl = font.render(
        "Overall, how would you rate your experience with this visualisation model?",
        True, (200, 220, 255))
    screen.blit(q2_lbl, (WIDTH // 2 - q2_lbl.get_width() // 2, q2_y))
    postquiz_model_radio.w = rg_w
    postquiz_model_radio.x = WIDTH // 2 - rg_w // 2
    postquiz_model_radio.y = q2_y + 34
    postquiz_model_radio.draw(screen, font)

    btn_postquiz_next.rect.topleft = (
        WIDTH // 2 - btn_postquiz_next.rect.width // 2,
        postquiz_model_radio.y + postquiz_model_radio.total_height() + 28
    )
    if postquiz_reading_radio.selected is None or postquiz_model_radio.selected is None:
        hint = small_font.render("Please answer both questions to continue.", True, (255, 180, 80))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2,
                           btn_postquiz_next.rect.y - 22))
    btn_postquiz_next.draw(screen, font)


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
        assigned_mode = "CellHl"
        mode          = assigned_mode
        is_redo       = False

        async def fetch_balancing_counts():
            nonlocal assigned_mode, mode
            try:
                text = await _fetch_balancing_text(is_redo)
                if not text:
                    pool = (["Wireframe","CellHl"] if is_redo
                            else ["Wireframe","WShells","CellHl"])
                    assigned_mode = mode = random.choice(pool)
                    log_debug(f"Balancing unavailable; random fallback -> {mode}")
                    return
                assigned_mode = mode = _parse_balancing_mode(text, exclude_wshells=is_redo)
            except Exception as e:
                log_debug(f"Balancing failed: {e}")
                traceback.print_exc()
                pool = (["Wireframe","CellHl"] if is_redo
                        else ["Wireframe","WShells","CellHl"])
                assigned_mode = mode = random.choice(pool)

        balancing_task = asyncio.create_task(fetch_balancing_counts())

        interstitial_text   = None
        interstitial_scroll = 0
        survey_scroll       = 0
        # redo section toggle state
        redo_section_enabled = False
        state               = "CONSENT"

        td = TimingData()

        survey_origin          = ""
        survey_familiarity_val = 1
        survey_source          = None
        survey_familiarity     = None

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

        show_three_axis = True
        show_4d_overlay = True

        free_shape_idx = 0
        read_counter   = 0

        renderers = {
            'Wireframe': WireframeRenderer(WIDTH, HEIGHT-300, a4=a4_correct),
            'WShells':  WShellRenderer  (WIDTH, HEIGHT-300, a4=a4_correct),
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
        FREE_MODES = ['Wireframe','WShells','CellHl']

        active_shape = None; axes_shape = None
        main_shapes  = []; cell_buttons = []; cell_colors = {}
        tutorial_cube = None; tutorial_shapes = []

        target_w = 0.0; opacity = 1.0
        feedback_text = ""; feedback_color = (255,255,255)
        mouse_history = [(0,0)]*5
        frame_count   = 0

        FREE_HUD = 170
        SLIDER_W = 160

        sliders = [
            Slider(0,0,SLIDER_W,"XW",-1.0,1.0,0.5),
            Slider(0,0,SLIDER_W,"YW",-1.0,1.0,0.0),
            Slider(0,0,SLIDER_W,"ZW",-1.0,1.0,0.0),
        ]
        def slider_a4(): return tuple(s.value for s in sliders)

        # ------------------------------------------------------------------
        # Survey widgets
        # ------------------------------------------------------------------
        SURVEY_SOURCES = ["School", "Blog or article", "Friend / Referral",
                          "Other", "DDS", "9470"]

        SURVEY_FAMILIARITY_OPTS = [
            "1 - Never heard of it", "2 - Heard of it", "3 - Some reading",
            "4 - Comfortable", "5 - Expert",
        ]

        FEEDBACK_OPTS = [
             "Helped significantly",
             "Helped somewhat",
             "Didn't help",
             "Confused me further",
        ]
        REDO_FEEDBACK_OPTS = FEEDBACK_OPTS
        POSTQUIZ_READING_FEEDBACK_OPTS = FEEDBACK_OPTS
        POSTQUIZ_MODEL_FEEDBACK_OPTS = [
            "Very clear and intuitive",
            "Mostly clear",
            "Neutral / unsure",
            "Somewhat confusing",
            "Very confusing"
        ]

        survey_source_radio   = RadioGroup(SURVEY_SOURCES,         0, 0, w=300, h=36, gap=6)
        survey_fam_radio      = RadioGroup(SURVEY_FAMILIARITY_OPTS, 0, 0, w=300, h=36, gap=6)
        redo_feedback_radio   = RadioGroup(REDO_FEEDBACK_OPTS,      0, 0, w=300, h=36, gap=6)
        postquiz_reading_radio        = RadioGroup(POSTQUIZ_READING_FEEDBACK_OPTS,  0, 0, w=420, h=38, gap=8)
        postquiz_model_radio        = RadioGroup(POSTQUIZ_MODEL_FEEDBACK_OPTS,  0, 0, w=420, h=38, gap=8)
        

        btn_survey_next       = ToggleButton(0, 0, 200, 44, "Continue ->", (80,160,80))
        btn_postquiz_next     = ToggleButton(0, 0, 220, 44, "Enter Free Mode ->", (80,160,80))
        # Redo toggle: sits on the content surface — label updates dynamically
        btn_redo_toggle       = ToggleButton(0, 0, 240, 34, "I am a Redo participant", (80, 100, 160))

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

        free_mode_btns = [
            ToggleButton(0,0,108,28,"Wireframe",(80,120,200)),
            ToggleButton(0,0,108,28,"WShells", (80,180,120)),
            ToggleButton(0,0,108,28,"CellHl",   (180,120,80)),
        ]
        btn_sliders_zero = ToggleButton(0,0,80,24,"Set to 0",(100,100,160))

        shape_dropdown    = Dropdown(0,0,160,28,SHAPE_NAMES,SHAPE_COLS)
        btn_toggle_origin = ToggleButton(0,0,125,28,"ThreeAxis: ON",(80,120,160))
        btn_toggle_waxis  = ToggleButton(0,0,125,28,"4D Origin: ON",(80,160,120))
        btn_toggle_origin.selected = True
        btn_toggle_waxis.selected  = True

        # ------------------------------------------------------------------
        # Layout helpers
        # ------------------------------------------------------------------
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
            bx = 90
            for b in free_mode_btns:
                b.rect.x = bx; b.rect.y = hud_top
                bx += b.rect.width + 6
            shape_dropdown.x = 90
            shape_dropdown.y = hud_top + 38
            btn_toggle_origin.rect.x = 90 + shape_dropdown.w + 12
            btn_toggle_origin.rect.y = hud_top + 38
            btn_toggle_waxis.rect.x  = btn_toggle_origin.rect.right + 8
            btn_toggle_waxis.rect.y  = hud_top + 38
            slider_x = WIDTH // 2 + 20
            row_h    = 44
            for i,s in enumerate(sliders):
                s.x = slider_x
                s.y = hud_top + i * row_h + row_h // 2
                s.w = min(SLIDER_W, WIDTH - slider_x - 340)
            last_s = sliders[-1]
            btn_sliders_zero.rect.x = last_s.x + last_s.w + 56
            btn_sliders_zero.rect.y = hud_top + row_h + (row_h // 2) - btn_sliders_zero.rect.height // 2

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
            sliders[0].value=0.5; sliders[1].value=0.0; sliders[2].value=0.0
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
            renderers['WShells'].a4 =a4_correct
            renderers['CellHl'].a4   =a4_correct
            q_start_time=time.time(); state="ANALYSIS"
            td.start_ana(question_index)
            for b in quiz_buttons+[btn_idk,btn_next,btn_ready]: b.selected=False

        # ------------------------------------------------------------------
        # Initial layouts
        # ------------------------------------------------------------------
        layout_quiz(); layout_free(); layout_consent()
        layout_tutorial()

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
                            layout_tutorial()

                        # ---- CONSENT ----
                        if state=="CONSENT":
                            btn_yes.handle_event(event); btn_no.handle_event(event)
                            if btn_yes.selected: btn_yes.selected=False; state="SURVEY"
                            if btn_no.selected:  btn_no.selected=False;  enter_free(from_quiz=False)

                        # ---- SURVEY ----
                        elif state=="SURVEY":
                            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
                                              pygame.MOUSEMOTION):
                                # Adjust position for scroll when hitting content-surface widgets
                                adj_pos = (event.pos[0], event.pos[1] + survey_scroll)
                                class _Adj:
                                    pass
                                adj = _Adj()
                                adj.type = event.type
                                adj.pos  = adj_pos
                                if hasattr(event, 'button'): adj.button = event.button

                                survey_source_radio.handle_event(adj)
                                survey_fam_radio.handle_event(adj)

                                # Redo toggle: btn_redo_toggle.rect is in content-space
                                # (set during render). Hit-test with scroll-adjusted pos.
                                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                    if btn_redo_toggle.rect.collidepoint(adj_pos):
                                        redo_section_enabled = not redo_section_enabled
                                        btn_redo_toggle.label = (
                                            "Redo participant (click to undo)"
                                            if redo_section_enabled
                                            else "I am a Redo participant"
                                        )
                                        if not redo_section_enabled:
                                            redo_feedback_radio.selected = None
                                        ev_consumed = True

                                if redo_section_enabled:
                                    redo_feedback_radio.handle_event(adj)

                            elif event.type == pygame.MOUSEWHEEL:
                                survey_scroll = max(0, survey_scroll - event.y * 30)
                                ev_consumed = True

                            # Continue button: rect is in SCREEN SPACE (set by render_survey)
                            btn_survey_next.handle_event(event)

                            if btn_survey_next.selected:
                                btn_survey_next.selected = False
                                source_ok = survey_source_radio.selected is not None
                                fam_ok    = survey_fam_radio.selected is not None
                                redo_ok   = (not redo_section_enabled or
                                             redo_feedback_radio.selected is not None)
                                if source_ok and fam_ok and redo_ok:
                                    survey_origin      = SURVEY_SOURCES[survey_source_radio.selected]
                                    survey_familiarity_val = survey_fam_radio.selected + 1
                                    survey_source      = survey_origin
                                    survey_familiarity = survey_familiarity_val
                                    is_redo            = redo_section_enabled

                                    if is_redo and redo_feedback_radio.selected is not None:
                                        td.redo_feedback = REDO_FEEDBACK_OPTS[redo_feedback_radio.selected]

                                    td.mark_survey_done()

                                    # Re-fetch balancing now that is_redo is known
                                    asyncio.create_task(fetch_balancing_counts())

                                    enter_tutorial()

                        # ---- TUTORIAL ----
                        elif state=="TUTORIAL":
                            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                                ui_rects=([btn_tutorial_ready.rect,btn_tutorial_next.rect]+
                                          [b.rect for b in tutorial_btns])
                                if not any(r.collidepoint(event.pos) for r in ui_rects):
                                    tutorial_dragging=True; tutorial_lastx=event.pos[0]
                                    vp_centre_y=(HEIGHT-300)//2
                                    tutorial_drag_inverted=(event.pos[1]<vp_centre_y)
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
                                    td.end_tuto_ana()
                                    # Encode redo flag into tutoanatime sign AFTER measuring
                                    if is_redo:
                                        td.encode_redo()
                                    td.start_tuto_ans()
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
                                    btn_tutorial_next.selected=False
                                    state="INTERSTITIAL"; interstitial_text=None
                                    interstitial_scroll = 0

                        # ---- INTERSTITIAL ----
                        elif state=="INTERSTITIAL":
                            btn_continue.handle_event(event)
                            if btn_continue.selected:
                                btn_continue.selected=False
                                td.end_read()
                                setup_question()
                            if event.type == pygame.MOUSEWHEEL:
                                interstitial_scroll = max(0, interstitial_scroll - event.y * 30)
                                ev_consumed = True

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
                                    chosen_label = f"Option {i+1}"
                                    is_correct   = (i+1 == correct_idx)
                                    shape_name   = type(active_shape).__name__
                                    chosen_a4    = a4_variants[i+1]
                                    td.record_answer(
                                        question_index, chosen_label, is_correct, False,
                                        shape_name, chosen_a4, a4_correct, correct_idx
                                    )
                                    feedback_text  = ("CORRECT! Axis mapping matches."
                                                      if is_correct
                                                      else f"WRONG. Correct was Option {correct_idx}.")
                                    feedback_color = (100,255,100) if is_correct else (255,100,100)
                                    state="FEEDBACK"
                                    for ob in quiz_buttons+[btn_idk]: ob.selected=False
                                    btn.selected=True
                            btn_idk.handle_event(event)
                            if btn_idk.selected:
                                td.end_ans(question_index)
                                shape_name = type(active_shape).__name__
                                td.record_answer(
                                    question_index, "IDK", False, True,
                                    shape_name, None, a4_correct, correct_idx
                                )
                                feedback_text  = f"Correct was Option {correct_idx}."
                                feedback_color = (200,200,100)
                                state="FEEDBACK"
                                for ob in quiz_buttons: ob.selected=False
                                btn_idk.selected=True

                        # ---- FEEDBACK ----
                        elif state=="FEEDBACK":
                            btn_next.handle_event(event)
                            if btn_next.selected:
                                btn_next.selected=False; question_index+=1
                                if question_index>=TOTAL_QUIZ_QUESTIONS:
                                    state="POSTQUIZ"
                                    postquiz_reading_radio.selected = None
                                    postquiz_model_radio.selected = None
                                    btn_postquiz_next.selected = False
                                elif question_index%5==0:
                                    state="INTERSTITIAL"; interstitial_text=None
                                    interstitial_scroll = 0
                                    ri=question_index//5-1
                                    if ri<len(td.readtime): td.start_read(ri)
                                else:
                                    setup_question()

                        # ---- POST-QUIZ FEEDBACK ----
                        elif state=="POSTQUIZ":
                            postquiz_reading_radio.handle_event(event)
                            postquiz_model_radio.handle_event(event)
                            btn_postquiz_next.handle_event(event)
                            if (btn_postquiz_next.selected and postquiz_reading_radio.selected is not None and postquiz_model_radio.selected is not None):
                                btn_postquiz_next.selected = False
                                td.postquiz_reading_feedback = POSTQUIZ_FEEDBACK_OPTS[postquiz_radio.selected]
                                td.postquiz_model_feedback = POSTQUIZ_FEEDBACK_OPTS[postquiz_radio.selected]
                                asyncio.create_task(submit_full_session(
                                    td, mode, survey_origin, survey_familiarity_val))
                                enter_free(from_quiz=True)

                        # ---- FREE MODE ----
                        elif state=="FREE_MODE":
                            ev_consumed=any(s.handle_event(event) for s in sliders)
                            if not ev_consumed:
                                btn_sliders_zero.handle_event(event)
                                if btn_sliders_zero.selected:
                                    btn_sliders_zero.selected=False
                                    for s in sliders: s.value=0.0
                                    ev_consumed=True

                        # Shared free-mode controls
                        if state=="FREE_MODE" and not ev_consumed:
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

                        # ---- Viewport drag ----
                        slider_hot_now=any(s.is_dragging for s in sliders) or (state=="FREE_MODE" and ev_consumed)

                        if state not in ("TUTORIAL","SURVEY","POSTQUIZ"):
                            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                                if not slider_hot_now:
                                    all_ui=(quiz_buttons+cell_buttons+
                                            [btn_ready,btn_next,btn_continue,btn_idk,btn_no]+
                                            free_mode_btns+[btn_toggle_origin,btn_toggle_waxis])
                                    in_hud=(event.pos[1]>=HEIGHT-(FREE_HUD if state=="FREE_MODE" else 300))
                                    if not any(b.rect.collidepoint(event.pos) for b in all_ui) and not in_hud:
                                        dragging=True; lastx,lasty=event.pos; drag_start_pos=event.pos
                                        vp_h_now   = HEIGHT - 300
                                        vp_centre_y = vp_h_now // 2
                                        drag_inverted=False
                                        if axes_shape and hasattr(axes_shape,'ov') and hasattr(axes_shape,'getText'):
                                            z_screen_ys=[]
                                            for _pi in range(len(axes_shape.ov)):
                                                _lbl=axes_shape.getText(_pi)
                                                if _lbl and _lbl.lower()=='z':
                                                    z_screen_ys.append(vp_centre_y-round(axes_shape.ov[_pi][1]))
                                            if z_screen_ys:
                                                z_top=min(z_screen_ys)
                                                drag_inverted=(event.pos[1]>z_top)
                                            else:
                                                drag_inverted=(event.pos[1]>vp_centre_y)
                                        else:
                                            drag_inverted=(event.pos[1]>vp_centre_y)

                            elif event.type==pygame.MOUSEBUTTONUP and event.button==1:
                                if dragging:
                                    dragging=False
                                    mx,my=event.pos
                                    dist=math.hypot(mx-drag_start_pos[0],my-drag_start_pos[1])
                                    omx,omy=mouse_history[0]
                                    vx=-(mx-omx)/(xsens*2.5); vy=(my-omy)/(ysens*2.5)
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
                                yaw+=dx/xsens; roll+=(my-lasty)/ysens
                                lastx,lasty=mx,my; dr=dy=0

                            if event.type==pygame.MOUSEWHEEL and state not in ("TUTORIAL","INTERSTITIAL"):
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
                                    elif mode=='WShells': target_w+=event.y*10.0
                                    elif mode=='CellHl':   opacity=max(0.0,min(1.0,opacity+event.y*0.05))

                            if event.type==pygame.KEYDOWN and state not in ("SURVEY","CONSENT","TUTORIAL","INTERSTITIAL","POSTQUIZ"):
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
                        survey_scroll = render_survey(
                            screen, font, big_font, small_font,
                            WIDTH, HEIGHT,
                            survey_source_radio, survey_fam_radio,
                            redo_section_enabled, redo_feedback_radio,
                            btn_redo_toggle, btn_survey_next,
                            survey_scroll, SURVEY_SOURCES,
                        )

                    # ---- TUTORIAL ----
                    elif state=="TUTORIAL":
                        layout_tutorial()
                        y2,p2,r2=get_tutorial_angles(tutorial_mouse_yaw,tutorial_angle,0)

                        if tutorial_sub=="WATCH":
                            vp_w=WIDTH; vp_h=HEIGHT-300
                            vp=pygame.Surface((vp_w,max(1,vp_h))); vp.fill((0,0,0))
                            tutorial_cube.rotate(y2,p2,r2,0,0,0)
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
                            sub=small_font.render(
                                "The cube was spinning so that X swept into Z — find the indicator showing that.",
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
                                if correct:
                                    fb="Correct! X sweeps into Z — Option 1 shows the X axis moving."
                                    fb_col=(100,255,120)
                                elif tutorial_answer=="idk":
                                    fb="The answer is Option 1: X sweeps into Z, so the X indicator moves."
                                    fb_col=(200,200,100)
                                else:
                                    fb="Not quite — Option 1 is correct: the X axis sweeps into Z."
                                    fb_col=(255,120,100)
                                fs=font.render(fb,True,fb_col)
                                screen.blit(fs,(WIDTH//2-fs.get_width()//2,HEIGHT-165))
                                exp=small_font.render(
                                    "In the real quiz the 4D shape spins — pick the indicator whose axis motion matches.",
                                    True,(180,180,200))
                                screen.blit(exp,(WIDTH//2-exp.get_width()//2,HEIGHT-145))
                                for i,b in enumerate(tutorial_btns):
                                    b.draw(screen,font)
                                    if b.selected: pygame.draw.rect(screen,(255,255,100),b.rect,3,border_radius=6)
                                btn_tutorial_next.draw(screen,font)

                    # ---- INTERSTITIAL ----
                    elif state=="INTERSTITIAL":
                        if interstitial_text is None:
                            block_idx=question_index//5
                            try:
                                try:
                                    with open(f"texts/interval_{mode}_{block_idx}.txt") as f: interstitial_text=f.read()
                                except:
                                    with open(f"texts/interval_{block_idx}.txt") as f: interstitial_text=f.read()
                            except Exception:
                                interstitial_text=(f"Block {block_idx+1} of {TOTAL_QUIZ_QUESTIONS//5}"
                                      f"  --  {TOTAL_QUIZ_QUESTIONS} questions total\n\n"
                                      "Analyse each shape's 4D rotation before guessing.\n\n"
                                      "Click Continue when ready.")

                        max_scroll = render_interstitial_text(
                            screen, interstitial_text, font, big_font,
                            small_font, WIDTH, HEIGHT, btn_continue, interstitial_scroll)
                        interstitial_scroll = min(interstitial_scroll, max_scroll)

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
                                elif mode=='WShells': renderers['WShells'].render(vp,main_shapes,target_w)
                                elif mode=='CellHl':   renderers['CellHl'].render(vp,main_shapes,opacity,cellhl,cell_colors)
                        screen.blit(vp,(0,0))
                        pygame.draw.line(screen,(100,100,100),(0,HEIGHT-300),(WIDTH,HEIGHT-300),2)

                        screen.blit(font.render(f"Assigned Mode: {mode}",True,(200,200,200)),(20,20))
                        screen.blit(big_font.render(f"Question {question_index+1} / {TOTAL_QUIZ_QUESTIONS}",True,(255,255,100)),(20,60))

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

                    # ---- POST-QUIZ FEEDBACK ----
                    elif state=="POSTQUIZ":
                        render_postquiz(screen, font, big_font, small_font,
                                        WIDTH, HEIGHT, postquiz_reading_radio, postquiz_model_radio, btn_postquiz_next)

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
                            elif mode=='WShells': renderers['WShells'].render(vp,visible_shapes,target_w)
                            elif mode=='CellHl':   renderers['CellHl'].render(vp,visible_shapes,opacity,cellhl,cell_colors)

                        if show_4d_overlay:
                            osurf=pygame.Surface((140,140)); osurf.fill((0,0,0))
                            origin_renderer.render(osurf,yaw,0,roll,dips[0],tucks[0],skews[0],0.001)
                            vp.blit(osurf,(10,vp_h-140-10))

                        screen.blit(vp,(0,0))
                        pygame.draw.line(screen,(80,80,80),(0,vp_h),(WIDTH,vp_h),2)

                        title=big_font.render(f"Free Exploration  |  {SHAPE_NAMES[free_shape_idx]}  |  {mode}",True,(255,220,80))
                        screen.blit(title,(20,10))
                        screen.blit(font.render(f"Free Exploration",True,(160,160,160)),(20,48))

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
                        btn_sliders_zero.draw(screen,small_font)

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