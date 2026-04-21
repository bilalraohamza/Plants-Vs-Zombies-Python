__author__ = 'Rao Hamza Bilal'

import pygame as pg
from ..core import constants as c
from ..core import engine
from ..states.user_select import get_leaderboard

# ── colours ───────────────────────────────────────────────────
_GOLD    = (255, 210,  50)
_SILVER  = (200, 200, 210)
_BRONZE  = (205, 127,  50)
_WHITE   = (235, 235, 235)
_GRAY    = (160, 160, 160)
_GREEN   = ( 90, 220,  90)
_BG_ROW  = [( 30,  55,  30, 200), ( 20,  40,  20, 200)]   # alternating row bg (RGBA)

# ── table layout ──────────────────────────────────────────────
_TABLE_X  = 80
_TABLE_W  = c.SCREEN_WIDTH - 160
_ROW_H    = 48
_HDR_H    = 40
_TABLE_Y  = 120

_COL_WIDTHS = [60, 240, 180, 160]    # Rank | Name | Total Score | Levels Done
_COL_LABELS = ["RANK", "NAME", "TOTAL SCORE", "LEVELS DONE"]

# ── back button ───────────────────────────────────────────────
_BTN_W  = 160
_BTN_H  = 36
_BTN_BORDER = (180, 140, 50)


class Leaderboard(engine.State):
    def __init__(self):
        engine.State.__init__(self)

    def startup(self, current_time, persist):
        self.start_time = current_time
        self.persist    = persist
        self.game_info  = persist
        self.next       = c.LEVEL_SELECT
        self._hover_btn = False
        self._current_user = persist.get(c.CURRENT_USER, '').lower()

        self._board = get_leaderboard()
        self._setup_fonts()
        self._setup_bg()
        self._setup_btn()

    def _setup_fonts(self):
        pg.font.init()
        try:
            fp = c.STATS_FONT_PATH
            self.fnt_title = pg.font.Font(fp, 32)
            self.fnt_hdr   = pg.font.Font(fp, 17)
            self.fnt_row   = pg.font.Font(fp, 20)
            self.fnt_btn   = pg.font.Font(fp, 18)
        except (IOError, AttributeError):
            self.fnt_title = pg.font.SysFont('arial', 32, bold=True)
            self.fnt_hdr   = pg.font.SysFont('arial', 17, bold=True)
            self.fnt_row   = pg.font.SysFont('arial', 20, bold=True)
            self.fnt_btn   = pg.font.SysFont('arial', 18, bold=True)

    def _setup_bg(self):
        try:
            raw = engine.GFX[c.MAIN_MENU_IMAGE]
            self._bg = pg.transform.smoothscale(raw, (c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        except Exception:
            self._bg = None
        dim = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pg.SRCALPHA)
        dim.fill((0, 0, 0, 155))
        self._dim = dim

    def _setup_btn(self):
        self._btn = pg.Rect(
            c.SCREEN_WIDTH // 2 - _BTN_W // 2,
            c.SCREEN_HEIGHT - 55,
            _BTN_W, _BTN_H
        )

    # ── update ────────────────────────────────────────────────
    def update(self, surface, current_time, mouse_pos, mouse_click):
        real_pos = pg.mouse.get_pos()
        self._hover_btn = self._btn.collidepoint(real_pos)

        if mouse_click and mouse_click[0] and self._hover_btn:
            self.next = c.LEVEL_SELECT
            self.done = True
            return

        self._draw(surface)

    # ── draw ──────────────────────────────────────────────────
    def _draw(self, surface):
        if self._bg:
            surface.blit(self._bg, (0, 0))
        else:
            surface.fill((10, 25, 10))
        surface.blit(self._dim, (0, 0))

        self._draw_title(surface)
        self._draw_table(surface)
        self._draw_back_btn(surface)

    def _draw_title(self, surface):
        text   = "LEADERBOARD"
        shadow = self.fnt_title.render(text, True, (0, 0, 0))
        surf   = self.fnt_title.render(text, True, _GOLD)
        cx     = c.SCREEN_WIDTH // 2
        surface.blit(shadow, shadow.get_rect(center=(cx + 2, 52)))
        surface.blit(surf,   surf.get_rect(center=(cx,       50)))

    def _draw_table(self, surface):
        tx = _TABLE_X
        ty = _TABLE_Y

        # ── header row ──
        hdr_surf = pg.Surface((_TABLE_W, _HDR_H), pg.SRCALPHA)
        hdr_surf.fill((0, 0, 0, 180))
        surface.blit(hdr_surf, (tx, ty))
        pg.draw.rect(surface, _GOLD, (tx, ty, _TABLE_W, _HDR_H), 1)

        cx = tx
        for lbl, cw in zip(_COL_LABELS, _COL_WIDTHS):
            s = self.fnt_hdr.render(lbl, True, _GOLD)
            surface.blit(s, s.get_rect(center=(cx + cw // 2, ty + _HDR_H // 2)))
            cx += cw

        # ── data rows ──
        for idx, entry in enumerate(self._board):
            ry      = ty + _HDR_H + idx * _ROW_H
            is_me   = entry['name'].lower() == self._current_user

            row_bg  = pg.Surface((_TABLE_W, _ROW_H), pg.SRCALPHA)
            if is_me:
                row_bg.fill((40, 100, 40, 200))
            else:
                row_bg.fill(_BG_ROW[idx % 2])
            surface.blit(row_bg, (tx, ry))
            pg.draw.line(surface, (60, 80, 60),
                         (tx, ry + _ROW_H - 1), (tx + _TABLE_W, ry + _ROW_H - 1))

            # rank colour
            rank = idx + 1
            if   rank == 1: rank_col = _GOLD
            elif rank == 2: rank_col = _SILVER
            elif rank == 3: rank_col = _BRONZE
            else:           rank_col = _WHITE if not is_me else _GREEN

            txt_col = _GREEN if is_me else _WHITE

            cells = [
                (str(rank),                  rank_col),
                (entry['name'] + (" (You)" if is_me else ""), txt_col),
                (str(entry['total_score']),  txt_col),
                (str(entry['levels_done']),  txt_col),
            ]
            cx = tx
            for (text, color), cw in zip(cells, _COL_WIDTHS):
                s = self.fnt_row.render(text, True, color)
                surface.blit(s, s.get_rect(center=(cx + cw // 2, ry + _ROW_H // 2)))
                cx += cw

        # outer border
        total_h = _HDR_H + len(self._board) * _ROW_H
        pg.draw.rect(surface, _GOLD, (tx, ty, _TABLE_W, total_h), 2)

    def _draw_back_btn(self, surface):
        bg  = (50, 95, 185) if self._hover_btn else (30, 60, 130)
        pg.draw.rect(surface, bg,          self._btn, border_radius=7)
        pg.draw.rect(surface, _BTN_BORDER, self._btn, 2, border_radius=7)
        lbl  = self.fnt_btn.render("Level Select", True, (255, 255, 255))
        shad = self.fnt_btn.render("Level Select", True, (0, 0, 0))
        lx = self._btn.centerx - lbl.get_width()  // 2
        ly = self._btn.centery - lbl.get_height() // 2
        surface.blit(shad, (lx + 1, ly + 1))
        surface.blit(lbl,  (lx,     ly))