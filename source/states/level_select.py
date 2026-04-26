__author__ = 'Rao Hamza Bilal'

import pygame as pg
from ..core import constants as c
from ..core import engine
from ..states.user_select import load_profiles, get_user_scores

# ── card grid layout ──────────────────────────────────────────
_COLS      = 3
_ROWS      = 3
_CARD_W    = 195
_CARD_H    = 115
_H_GAP     = 18
_V_GAP     = 16
_GRID_TOP  = 88    # y where the grid starts

# ── colours ───────────────────────────────────────────────────
_COL_LOCKED_BG     = ( 50,  50,  55)
_COL_LOCKED_BOR    = ( 80,  80,  85)
_COL_LOCKED_TXT    = (100, 100, 105)
_COL_UNLOCKED_BG   = ( 25,  75,  30)
_COL_UNLOCKED_BOR  = ( 70, 160,  70)
_COL_DONE_BG       = ( 20,  60,  20)
_COL_DONE_BOR      = (210, 175,  50)   # gold
_COL_HOVER_TINT    = ( 30,  30,  30)   # added to bg on hover
_COL_WHITE         = (235, 235, 235)
_COL_GOLD          = (255, 210,  50)
_COL_GRAY          = (120, 120, 120)
_COL_GREEN         = ( 90, 220,  90)

# ── bottom bar buttons ─────────────────────────────────────────
_BAR_H    = 52
_BTN_W    = 160
_BTN_H    = 36
_BTN_GAP  = 20
_BTN_BORDER = (180, 140, 50)

_BACK_BTN  = {"label": "Main Menu",   "action": c.MAIN_MENU,
               "bg": (90, 60, 15), "hover": (130, 90, 25), "txt": (255, 220, 100)}
_BOARD_BTN = {"label": "Leaderboard", "action": c.LEADERBOARD,
               "bg": (30, 60, 130), "hover": (50, 95, 185), "txt": (255, 255, 255)}


class LevelSelect(engine.State):
    def __init__(self):
        engine.State.__init__(self)

    # ── startup ───────────────────────────────────────────────
    def startup(self, current_time, persist):
        self.start_time = current_time
        self.persist    = persist
        self.game_info  = persist
        self.next       = c.MAIN_MENU
        self._hover_card   = -1
        self._hover_btn    = -1

        self._load_user_data()
        self._build_layout()
        self._setup_fonts()
        self._setup_bg()

    def _load_user_data(self):
        username = self.persist.get(c.CURRENT_USER, '')
        profiles = load_profiles()
        self._max_level  = 1
        self._user_scores = {}
        for p in profiles:
            if p['name'].lower() == username.lower():
                self._max_level   = p.get('level', 1)
                self._user_scores = p.get('scores', {})
                break

    def _build_layout(self):
        total_w = _COLS * _CARD_W + (_COLS - 1) * _H_GAP
        grid_x  = c.SCREEN_WIDTH // 2 - total_w // 2

        self._cards = []     # list of (pg.Rect, level_num)
        for row in range(_ROWS):
            for col in range(_COLS):
                lvl = row * _COLS + col + 1
                if lvl > c.MAX_LEVEL:
                    break
                rx = grid_x + col * (_CARD_W + _H_GAP)
                ry = _GRID_TOP + row * (_CARD_H + _V_GAP)
                self._cards.append((pg.Rect(rx, ry, _CARD_W, _CARD_H), lvl))

        # bottom bar buttons (centred)
        bar_y    = c.SCREEN_HEIGHT - _BAR_H
        total_bw = 2 * _BTN_W + _BTN_GAP
        bx       = c.SCREEN_WIDTH // 2 - total_bw // 2
        self._btn_back  = pg.Rect(bx,              bar_y + (_BAR_H - _BTN_H) // 2, _BTN_W, _BTN_H)
        self._btn_board = pg.Rect(bx + _BTN_W + _BTN_GAP, bar_y + (_BAR_H - _BTN_H) // 2, _BTN_W, _BTN_H)

    def _setup_fonts(self):
        pg.font.init()
        try:
            fp = c.STATS_FONT_PATH
            self.fnt_title = pg.font.Font(fp, 30)
            self.fnt_lvl   = pg.font.Font(fp, 28)
            self.fnt_score = pg.font.Font(fp, 16)
            self.fnt_lock  = pg.font.Font(fp, 15)
            self.fnt_btn   = pg.font.Font(fp, 18)
        except (IOError, AttributeError):
            self.fnt_title = pg.font.SysFont('arial', 30, bold=True)
            self.fnt_lvl   = pg.font.SysFont('arial', 28, bold=True)
            self.fnt_score = pg.font.SysFont('arial', 16)
            self.fnt_lock  = pg.font.SysFont('arial', 15)
            self.fnt_btn   = pg.font.SysFont('arial', 18, bold=True)

    def _setup_bg(self):
        try:
            raw = engine.GFX[c.MAIN_MENU_IMAGE]
            self._bg = pg.transform.smoothscale(raw, (c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        except Exception:
            self._bg = None
        dim = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pg.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        self._dim = dim

    # ── update ────────────────────────────────────────────────
    def update(self, surface, current_time, mouse_pos, mouse_click):
        real_pos = pg.mouse.get_pos()

        # Hover detection
        self._hover_card = -1
        for i, (rect, lvl) in enumerate(self._cards):
            if rect.collidepoint(real_pos) and lvl <= self._max_level:
                self._hover_card = i
                break

        self._hover_btn = -1
        if self._btn_back.collidepoint(real_pos):
            self._hover_btn = 0
        elif self._btn_board.collidepoint(real_pos):
            self._hover_btn = 1

        # Click handling
        if mouse_click and mouse_click[0]:
            if self._hover_card >= 0:
                _, lvl = self._cards[self._hover_card]
                self.persist[c.LEVEL_NUM] = lvl
                self.next = c.LEVEL
                self.done = True
                return
            if self._hover_btn == 0:
                self.next = c.MAIN_MENU
                self.done = True
                return
            if self._hover_btn == 1:
                self.persist[c.LEADERBOARD_ORIGIN] = c.LEVEL_SELECT
                self.next = c.LEADERBOARD
                self.done = True
                return

        self._draw(surface)

    # ── draw ──────────────────────────────────────────────────
    def _draw(self, surface):
        if self._bg:
            surface.blit(self._bg, (0, 0))
        else:
            surface.fill((20, 40, 20))
        surface.blit(self._dim, (0, 0))

        # Title
        title = self.fnt_title.render("SELECT LEVEL", True, _COL_GOLD)
        ts    = self.fnt_title.render("SELECT LEVEL", True, (0, 0, 0))
        tx    = c.SCREEN_WIDTH // 2 - title.get_width() // 2
        surface.blit(ts,    (tx + 2, 30 + 2))
        surface.blit(title, (tx,     30))

        # Cards
        for i, (rect, lvl) in enumerate(self._cards):
            self._draw_card(surface, rect, lvl, i == self._hover_card)

        # Bottom bar
        self._draw_bottom_bar(surface)

    def _draw_card(self, surface, rect, lvl, hovered):
        locked    = lvl > self._max_level
        score_val = self._user_scores.get(str(lvl), 0)
        done      = (not locked) and (score_val > 0)

        if locked:
            bg  = _COL_LOCKED_BG
            bor = _COL_LOCKED_BOR
        elif done:
            bg  = tuple(min(255, v + 15) for v in _COL_DONE_BG) if hovered else _COL_DONE_BG
            bor = _COL_DONE_BOR
        else:
            bg  = tuple(min(255, v + 15) for v in _COL_UNLOCKED_BG) if hovered else _COL_UNLOCKED_BG
            bor = _COL_UNLOCKED_BOR

        pg.draw.rect(surface, bg,  rect, border_radius=10)
        pg.draw.rect(surface, bor, rect, 2, border_radius=10)

        cx = rect.centerx
        cy = rect.centery

        if locked:
            # Level number (greyed)
            lvl_s = self.fnt_lvl.render(f"LEVEL  {lvl}", True, _COL_LOCKED_TXT)
            surface.blit(lvl_s, lvl_s.get_rect(center=(cx, cy - 12)))
            lk_s  = self.fnt_lock.render("LOCKED", True, _COL_LOCKED_TXT)
            surface.blit(lk_s,  lk_s.get_rect(center=(cx, cy + 22)))
        else:
            color = _COL_GOLD if done else _COL_WHITE
            lvl_s = self.fnt_lvl.render(f"LEVEL  {lvl}", True, color)
            surface.blit(lvl_s, lvl_s.get_rect(center=(cx, cy - 14)))

            if done:
                sc_s = self.fnt_score.render(f"Best Score:  {score_val}", True, _COL_GREEN)
                surface.blit(sc_s, sc_s.get_rect(center=(cx, cy + 22)))
            else:
                ns_s = self.fnt_score.render("Not Played", True, _COL_GRAY)
                surface.blit(ns_s, ns_s.get_rect(center=(cx, cy + 22)))

    def _draw_bottom_bar(self, surface):
        bar_rect = pg.Rect(0, c.SCREEN_HEIGHT - _BAR_H, c.SCREEN_WIDTH, _BAR_H)
        bar_surf = pg.Surface((c.SCREEN_WIDTH, _BAR_H), pg.SRCALPHA)
        bar_surf.fill((0, 0, 0, 160))
        surface.blit(bar_surf, bar_rect.topleft)

        for i, (btn_rect, meta) in enumerate(
                [( self._btn_back,  _BACK_BTN),
                 (self._btn_board, _BOARD_BTN)]):
            bg = meta['hover'] if self._hover_btn == i else meta['bg']
            pg.draw.rect(surface, bg,         btn_rect, border_radius=7)
            pg.draw.rect(surface, _BTN_BORDER, btn_rect, 2, border_radius=7)
            lbl  = self.fnt_btn.render(meta['label'], True, meta['txt'])
            shad = self.fnt_btn.render(meta['label'], True, (0, 0, 0))
            lx   = btn_rect.centerx - lbl.get_width()  // 2
            ly   = btn_rect.centery - lbl.get_height() // 2
            surface.blit(shad, (lx + 1, ly + 1))
            surface.blit(lbl,  (lx,     ly))