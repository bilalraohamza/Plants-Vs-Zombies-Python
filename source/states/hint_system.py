__author__ = 'Rao Hamza Bilal'

import os
import json
import math
import pygame as pg
from ..core import constants as c
from ..components.menu_bar import plant_name_list

# ============================================================
# FONTS
# Body  : Fredoka-Regular (user will add this file)
# Title : Fredoka-Bold    (already in project)
# Both fall back to Fredoka-Bold if Regular is not present yet.
# ============================================================
_FONT_REGULAR = os.path.join(c.FONTS_DIR, 'Fredoka-Regular.ttf')
_FONT_BOLD    = os.path.join(c.FONTS_DIR, 'Fredoka-Bold.ttf')

# ============================================================
# LAYOUT
# CHOOSE phase: hint box on the RIGHT strip (panel ends ~x=475)
# PLAY phase  : hint box at BOTTOM centre
# ============================================================
_RIGHT_X      = 482     # left edge of right-side box
_RIGHT_W      = 308     # fits inside 800px screen
_RIGHT_Y      = 92      # just below the top menu bar
_BOTTOM_W     = 500
_BOTTOM_MAR   = 14      # gap from bottom edge of screen

# Animation
_SLIDE_SPEED  = 25      # px per frame
_FADE_SPEED   = 10      # alpha per frame  (255/10 ≈ 25 frames ≈ 0.4 s)

# Colorkey used for the temp fade surface (must not appear in any drawn pixel)
_CKEY = (1, 2, 3)


# ============================================================
# SAVE / LOAD  tutorial-seen flag
# ============================================================

def _load_tutorial_seen(username):
    """Return True if this user has already completed the tutorial."""
    if not username:
        return False
    try:
        with open(c.SAVE_DATA_PATH) as f:
            data = json.load(f)
        for p in data.get('profiles', []):
            if p['name'].lower() == username.lower():
                return p.get('tutorial_seen', False)
    except (IOError, json.JSONDecodeError, KeyError):
        pass
    return False


def _save_tutorial_seen(username):
    """Persist tutorial_seen=True for this user profile."""
    if not username:
        return
    try:
        with open(c.SAVE_DATA_PATH) as f:
            data = json.load(f)
        for p in data.get('profiles', []):
            if p['name'].lower() == username.lower():
                p['tutorial_seen'] = True
                break
        os.makedirs(os.path.dirname(c.SAVE_DATA_PATH), exist_ok=True)
        with open(c.SAVE_DATA_PATH, 'w') as f:
            json.dump(data, f, indent=4)
    except (IOError, json.JSONDecodeError, KeyError):
        pass


# ============================================================
# VISUAL: pulsing ring around a highlighted element
# ============================================================

class _Ring:
    COLOR       = (55, 220, 75)
    WIDTH       = 3
    PULSE_SPEED = 3.2   # cycles per second

    def draw(self, surface, rect, current_time):
        if rect is None:
            return
        t      = current_time / 1000.0
        pulse  = (math.sin(t * self.PULSE_SPEED * math.pi * 2) + 1) / 2
        radius = int(max(rect.w, rect.h) // 2 + 10 + pulse * 7)
        alpha  = int(110 + pulse * 145)
        cx, cy = rect.centerx, rect.centery

        # soft glow
        gr   = radius + 10
        glow = pg.Surface((gr * 2, gr * 2), pg.SRCALPHA)
        pg.draw.circle(glow, (*self.COLOR, alpha // 4), (gr, gr), gr, 5)
        surface.blit(glow, (cx - gr, cy - gr))

        # sharp ring
        rr   = radius + 3
        ring = pg.Surface((rr * 2, rr * 2), pg.SRCALPHA)
        pg.draw.circle(ring, (*self.COLOR, alpha), (rr, rr), radius, self.WIDTH)
        surface.blit(ring, (cx - rr, cy - rr))


# ============================================================
# VISUAL: dashed connector line from box edge to target
# ============================================================

def _box_edge_point(box_rect, tx, ty):
    """Return the point on the box boundary along the line box_centre → (tx, ty)."""
    bx, by = box_rect.centerx, box_rect.centery
    dx, dy = tx - bx, ty - by
    if dx == 0 and dy == 0:
        return (bx, by)
    hw = box_rect.width  / 2.0
    hh = box_rect.height / 2.0
    if dx == 0:
        t = hh / abs(dy)
    elif dy == 0:
        t = hw / abs(dx)
    else:
        t = min(hw / abs(dx), hh / abs(dy))
    return (int(bx + dx * t), int(by + dy * t))


def _draw_connector(surface, box_rect, target_rect):
    """Dashed line + small arrowhead from box edge to target centre."""
    tx, ty = target_rect.centerx, target_rect.centery
    sx, sy = _box_edge_point(box_rect, tx, ty)

    dx, dy = tx - sx, ty - sy
    length = math.hypot(dx, dy)
    if length < 20:
        return

    # shorten end so it stops just before the ring
    stop = max(0, length - max(target_rect.w, target_rect.h) // 2 - 14)
    ux, uy = dx / length, dy / length

    COLOR  = (55, 220, 75, 180)
    DASH   = 7
    GAP    = 5

    # dashed line
    pos     = 0
    drawing = True
    while pos < stop:
        if drawing:
            ep  = min(pos + DASH, stop)
            p1  = (int(sx + ux * pos), int(sy + uy * pos))
            p2  = (int(sx + ux * ep),  int(sy + uy * ep))
            seg = pg.Surface((abs(p2[0]-p1[0]) + 2, abs(p2[1]-p1[1]) + 2), pg.SRCALPHA)
            # draw on a tiny SRCALPHA surface, then blit
            pg.draw.line(surface, COLOR, p1, p2, 2)
        pos    += DASH if drawing else GAP
        drawing = not drawing

    # arrowhead
    tip = (int(sx + ux * stop), int(sy + uy * stop))
    px, py = -uy, ux   # perpendicular
    sz = 7
    pts = [
        tip,
        (int(tip[0] - ux*sz + px*sz*0.5), int(tip[1] - uy*sz + py*sz*0.5)),
        (int(tip[0] - ux*sz - px*sz*0.5), int(tip[1] - uy*sz - py*sz*0.5)),
    ]
    pg.draw.polygon(surface, COLOR, pts)


# ============================================================
# VISUAL: the hint text box
# ============================================================

class _Box:
    PAD         = 12
    BG          = (12, 18, 30, 218)
    BORDER      = (55, 195, 75)
    TITLE_BG    = (22, 55, 28, 230)
    TITLE_COLOR = (130, 240, 140)
    TEXT_COLOR  = (235, 240, 230)
    SKIP_BG     = (160, 40,  40)
    SKIP_FG     = (255, 255, 255)

    def __init__(self):
        # Body: Fredoka-Regular (user will add); falls back to Bold
        try:
            self.body  = pg.font.Font(_FONT_REGULAR, 19)
        except (IOError, AttributeError):
            self.body  = pg.font.Font(_FONT_BOLD, 19)
        # Title: always Bold
        try:
            self.title = pg.font.Font(_FONT_BOLD, 14)
        except (IOError, AttributeError):
            self.title = pg.font.SysFont('arial', 14, bold=True)

    # ---- helpers ------------------------------------------------

    def _wrap(self, text, max_w):
        words, lines, cur = text.split(), [], ''
        for w in words:
            trial = (cur + ' ' + w).lstrip()
            if self.body.size(trial)[0] <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def _geometry(self, text, position):
        """Return (box_x_target, box_y_target, box_w, box_h, lines, title_h, line_h)."""
        box_w   = _RIGHT_W if position == 'right' else _BOTTOM_W
        inner_w = box_w - 2 * self.PAD
        lines   = self._wrap(text, inner_w)
        line_h  = self.body.get_linesize()
        title_h = self.title.get_linesize() + self.PAD + 4
        box_h   = title_h + len(lines) * line_h + self.PAD * 2

        if position == 'right':
            bx = _RIGHT_X
            by = _RIGHT_Y
        else:
            bx = c.SCREEN_WIDTH // 2 - box_w // 2
            by = c.SCREEN_HEIGHT - box_h - _BOTTOM_MAR

        return bx, by, box_w, box_h, lines, title_h, line_h

    # ---- public -------------------------------------------------

    def target_rect(self, text, position):
        """Return the pg.Rect where the box will sit when fully slid in."""
        bx, by, bw, bh, *_ = self._geometry(text, position)
        return pg.Rect(bx, by, bw, bh)

    def draw(self, surface, text, step_idx, total, position, off_x, off_y):
        """
        Draw the box at (target + offset).
        Returns (box_rect, skip_rect) in surface coordinates.
        """
        bx_t, by_t, bw, bh, lines, title_h, line_h = self._geometry(text, position)
        bx = bx_t + off_x
        by = by_t + off_y
        box_rect = pg.Rect(bx, by, bw, bh)

        # --- background ---
        bg = pg.Surface((bw, bh), pg.SRCALPHA)
        bg.fill(self.BG)
        surface.blit(bg, (bx, by))

        # --- border ---
        pg.draw.rect(surface, self.BORDER, box_rect, 2, border_radius=8)

        # --- title bar ---
        tb = pg.Surface((bw - 2, title_h), pg.SRCALPHA)
        tb.fill(self.TITLE_BG)
        surface.blit(tb, (bx + 1, by + 1))
        pg.draw.line(surface, self.BORDER,
                     (bx + 1,      by + title_h),
                     (bx + bw - 2, by + title_h), 1)

        # --- "HINT N / T" label ---
        label = f"HINT  {step_idx + 1} / {total}"
        ls    = self.title.render(label, True, self.TITLE_COLOR)
        surface.blit(ls, (bx + self.PAD,
                          by + (title_h - ls.get_height()) // 2))

        # --- Skip / X button (right side of title bar) ---
        sk_size  = title_h - 8
        skip_rect = pg.Rect(bx + bw - sk_size - 4, by + 4, sk_size, sk_size)
        pg.draw.rect(surface, self.SKIP_BG, skip_rect, border_radius=4)
        xs = self.title.render("X", True, self.SKIP_FG)
        surface.blit(xs, xs.get_rect(center=skip_rect.center))

        # --- body text ---
        ty = by + title_h + self.PAD
        for line in lines:
            ts = self.body.render(line, True, self.TEXT_COLOR)
            surface.blit(ts, (bx + self.PAD, ty))
            ty += line_h

        return box_rect, skip_rect


# ============================================================
# DATA: one hint step
# ============================================================

class HintStep:
    def __init__(self, text, highlight_getter=None,
                 completion_check=None, position='bottom'):
        self.text             = text
        self.highlight_getter = highlight_getter
        self.completion_check = completion_check or (lambda: False)
        self.position         = position


# ============================================================
# HINT SYSTEM  (main class)
# ============================================================

class HintSystem:
    """
    Full tutorial sequence for Level 1.

    Level integration:
        startup()  -> self.hint_system = HintSystem(self)  if level == 1 and not seen
        choose()   -> self.hint_system.update(current_time, mouse_pos, mouse_click)
        play()     -> self.hint_system.update(current_time, mouse_pos, mouse_click)
        draw()     -> self.hint_system.draw(surface, current_time)   [called last]
    """

    def __init__(self, level):
        self.level      = level
        self.active     = True
        self.step_index = 0

        self._ring      = _Ring()
        self._box       = _Box()
        self._steps     = self._build_steps()

        # Animation state: 'slide_in' | 'visible' | 'fade_out'
        self._anim      = 'slide_in'
        self._off_x     = 0.0
        self._off_y     = 0.0
        self._alpha     = 0

        # Cached rects for click detection (set each draw call)
        self._skip_rect = None
        self._box_rect  = None

        self._start_slide()

    # -------------------------------------------------------
    # Animation helpers
    # -------------------------------------------------------

    def _start_slide(self):
        """Initialise slide-in animation for the current step."""
        step = self.current_step
        if step is None:
            return
        self._anim  = 'slide_in'
        self._alpha = 0
        if step.position == 'right':
            # slide in from the right edge
            self._off_x = float(c.SCREEN_WIDTH - _RIGHT_X + _RIGHT_W)
            self._off_y = 0.0
        else:
            # slide up from the bottom
            self._off_x = 0.0
            self._off_y = float(c.SCREEN_HEIGHT)

    def _tick_animation(self):
        if self._anim == 'slide_in':
            step = self.current_step
            if step and step.position == 'right':
                self._off_x = max(0.0, self._off_x - _SLIDE_SPEED)
            else:
                self._off_y = max(0.0, self._off_y - _SLIDE_SPEED)
            self._alpha = min(255, self._alpha + _FADE_SPEED * 2)

            if self._off_x == 0.0 and self._off_y == 0.0 and self._alpha >= 255:
                self._alpha = 255
                self._anim  = 'visible'

        elif self._anim == 'fade_out':
            self._alpha = max(0, self._alpha - _FADE_SPEED)
            if self._alpha == 0:
                self.step_index += 1
                if self.step_index >= len(self._steps):
                    self._finish()
                else:
                    self._start_slide()

    # -------------------------------------------------------
    # Dismiss / finish
    # -------------------------------------------------------

    def _finish(self):
        self.active = False
        username = self.level.persist.get(c.CURRENT_USER, None)
        _save_tutorial_seen(username)

    # -------------------------------------------------------
    # Game-state helpers  (all guarded against missing attrs)
    # -------------------------------------------------------

    def _panel_rect(self):
        p = getattr(self.level, 'panel', None)
        return getattr(p, 'panel_rect', None)

    def _panel_sunflower_rect(self):
        p = getattr(self.level, 'panel', None)
        if p is None:
            return None
        for card in getattr(p, 'card_list', []):
            if plant_name_list[card.name_index] == c.SUNFLOWER:
                return card.rect
        return None

    def _panel_start_rect(self):
        p = getattr(self.level, 'panel', None)
        return getattr(p, 'button_rect', None)

    def _menubar_card_rect(self, plant_name):
        mb = getattr(self.level, 'menubar', None)
        if mb is None:
            return None
        for card in getattr(mb, 'card_list', []):
            if plant_name_list[card.name_index] == plant_name:
                return card.rect
        return None

    def _nearest_sun_rect(self):
        for sun in self.level.sun_group:
            return sun.rect
        return None

    def _first_car_rect(self):
        cars = getattr(self.level, 'cars', [])
        return cars[0].rect if cars else None

    def _has_plant(self, name):
        return any(p.name == name
                   for g in self.level.plant_groups for p in g)

    def _zombie_count(self):
        return sum(len(g) for g in self.level.zombie_groups)

    def _zombies_killed(self):
        return getattr(self.level, 'zombies_killed', 0)

    def _sun_value(self):
        mb = getattr(self.level, 'menubar', None)
        return mb.sun_value if mb else 0

    def _panel_selected_num(self):
        p = getattr(self.level, 'panel', None)
        return p.selected_num if p else 0

    def _panel_has_sunflower(self):
        p = getattr(self.level, 'panel', None)
        if p is None:
            return False
        return any(plant_name_list[card.name_index] == c.SUNFLOWER
                   for card in getattr(p, 'selected_cards', []))

    # -------------------------------------------------------
    # Build hint steps
    # -------------------------------------------------------

    def _build_steps(self):
        lv = self.level
        s  = []

        # ---- CHOOSE phase  (position='right') ----

        s.append(HintStep(
            text="Welcome! Click plant cards in the panel to add them to your loadout. You need 8 plants.",
            highlight_getter=self._panel_rect,
            completion_check=lambda: self._panel_selected_num() >= 1,
            position='right'
        ))
        s.append(HintStep(
            text="Always include Sunflower! She produces Sun over time, your main planting resource.",
            highlight_getter=self._panel_sunflower_rect,
            completion_check=self._panel_has_sunflower,
            position='right'
        ))
        s.append(HintStep(
            text="Fill all 8 slots, then press LET'S ROCK to start the level!",
            highlight_getter=self._panel_start_rect,
            completion_check=lambda: lv.state == c.PLAY,
            position='right'
        ))

        # ---- PLAY phase  (position='bottom') ----

        s.append(HintStep(
            text="Sun falls from the sky! Click it quickly to collect Sun, you need it to plant.",
            highlight_getter=self._nearest_sun_rect,
            completion_check=lambda: self._sun_value() >= 50,
            position='bottom'
        ))
        s.append(HintStep(
            text="You have 50 Sun! Click the Sunflower card then place it on the LEFT side of the lawn.",
            highlight_getter=lambda: self._menubar_card_rect(c.SUNFLOWER),
            completion_check=lambda: self._has_plant(c.SUNFLOWER),
            position='bottom'
        ))
        s.append(HintStep(
            text="Sunflower will produce extra Sun over time. Now add a Peashooter to shoot zombies!",
            highlight_getter=lambda: self._menubar_card_rect(c.PEASHOOTER),
            completion_check=lambda: self._has_plant(c.PEASHOOTER),
            position='bottom'
        ))
        s.append(HintStep(
            text="Each row has a Lawnmower as a last resort. If a zombie walks past it, that row loses its backup!",
            highlight_getter=self._first_car_rect,
            completion_check=lambda: self._zombie_count() >= 1,
            position='bottom'
        ))
        s.append(HintStep(
            text="Zombies are coming! Keep collecting Sun and planting in every row to hold the defense.",
            highlight_getter=None,
            completion_check=lambda: self._zombies_killed() >= 5,
            position='bottom'
        ))
        s.append(HintStep(
            text="You are doing great! Eliminate all zombies to complete the level. Good luck!",
            highlight_getter=None,
            completion_check=lambda: False,
            position='bottom'
        ))

        return s

    # -------------------------------------------------------
    # Public API
    # -------------------------------------------------------

    @property
    def current_step(self):
        return self._steps[self.step_index] if self.step_index < len(self._steps) else None

    def update(self, current_time, mouse_pos=None, mouse_click=None):
        """Call every frame from Level.choose() and Level.play()."""
        if not self.active:
            return

        # Feature 1: skip button click
        if (mouse_pos and mouse_click and mouse_click[0]
                and self._skip_rect
                and self._skip_rect.collidepoint(mouse_pos)):
            self._finish()
            return

        step = self.current_step
        if step is None:
            self._finish()
            return

        # Feature 4+5: tick animation / step transition
        self._tick_animation()

        # Advance step only when fully visible
        if self._anim == 'visible':
            try:
                if step.completion_check():
                    self._anim = 'fade_out'
            except Exception:
                pass

    def draw(self, surface, current_time):
        """Call at the END of Level.draw() so hints appear on top."""
        if not self.active:
            return

        # Feature 3: hide during pause
        if getattr(getattr(self.level, 'pause_menu', None), 'is_active', False):
            return

        step = self.current_step
        if step is None:
            return

        try:
            target = step.highlight_getter() if step.highlight_getter else None
        except Exception:
            target = None

        # Use a plain (non-SRCALPHA) surface + colorkey for global alpha fade
        temp = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        temp.set_colorkey(_CKEY)
        temp.fill(_CKEY)

        # 1. Ring around highlighted element
        self._ring.draw(temp, target, current_time)

        # 2. Hint box
        off_x = int(self._off_x)
        off_y = int(self._off_y)
        box_rect, skip_rect = self._box.draw(
            temp, step.text, self.step_index, len(self._steps),
            step.position, off_x, off_y
        )
        self._box_rect  = box_rect
        self._skip_rect = skip_rect   # stored for click detection in update()

        # 3. Feature 6: connector line (only once box has finished sliding in)
        if target and box_rect and off_x == 0 and off_y == 0:
            _draw_connector(temp, box_rect, target)

        # 4. Apply fade alpha to the whole composite
        temp.set_alpha(self._alpha)
        surface.blit(temp, (0, 0))