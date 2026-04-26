__author__ = 'Rao Hamza Bilal'

import sys
import pygame as pg
from ..core import constants as c
from ..core import engine
from ..states.user_select import get_survival_leaderboard


# ── colour palette ────────────────────────────────────────────────────────────
_GOLD    = (255, 215,  50)
_SILVER  = (200, 200, 210)
_BRONZE  = (205, 127,  50)
_WHITE   = (235, 235, 235)
_GREEN   = ( 90, 220,  90)
_RED     = (220,  50,  50)
_GRAY    = (160, 160, 160)


# ── helper ────────────────────────────────────────────────────────────────────
def _fmt_time(ms):
    total_s = max(0, int(ms)) // 1000
    return f"{total_s // 60}:{total_s % 60:02d}"


def _blit_text(surface, font, text, color, cx, cy, shadow=True):
    if shadow:
        shad = font.render(text, True, (0, 0, 0))
        surface.blit(shad, shad.get_rect(center=(cx + 2, cy + 2)))
    surf = font.render(text, True, color)
    surface.blit(surf, surf.get_rect(center=(cx, cy)))


# =============================================================================
#  SURVIVAL GAME OVER SCREEN
# =============================================================================
class SurvivalGameOverScreen(engine.State):

    _BTN_W   = 128
    _BTN_H   = 38
    _BTN_GAP = 8

    # (label, target_state_or_action, bg_normal, bg_hover)
    _BTN_DEFS = [
        ("Retry",       c.SURVIVAL,             ( 30, 110,  30), ( 50, 155,  50)),
        ("Main Menu",   c.MAIN_MENU,             ( 90,  60,  15), (130,  90,  25)),
        ("Leaderboard", c.SURVIVAL_LEADERBOARD,  ( 40,  60, 130), ( 60,  90, 180)),
        ("Exit",        "exit",                  (130,  35,  35), (175,  55,  55)),
    ]

    def __init__(self):
        engine.State.__init__(self)
        self._hover = -1

    # ── startup ───────────────────────────────────────────────────────────────

    def startup(self, current_time, persist):
        self.start_time  = current_time
        self.persist     = persist
        self.game_info   = persist

        self.score          = persist.get(c.SURVIVAL_SCORE,         0)
        self.survival_ms    = persist.get(c.SURVIVAL_TIME,          0)
        self.zombies_killed = persist.get(c.ZOMBIES_KILLED,         0)
        self.sun_collected  = persist.get(c.SUN_COLLECTED,          0)
        self.plants_planted = persist.get(c.PLANTS_PLANTED,         0)
        self.is_best        = persist.get(c.SURVIVAL_SCORE_IS_BEST, False)
        self.beaten_users   = persist.get(c.SURVIVAL_BEATEN_USERS,  [])

        self._setup_fonts()
        self._setup_bg()
        self._setup_buttons()

        # Pop-up overlay shows when you beat a record
        self.popup_active    = self.is_best or bool(self.beaten_users)
        self.popup_dismissed = False
        self.popup_timer     = current_time
        self.POPUP_DURATION  = 5000          # Auto-dismiss after 5 s

    # ── font / bg helpers ─────────────────────────────────────────────────────

    def _setup_fonts(self):
        fp = c.STATS_FONT_PATH
        try:
            self.fnt_title  = pg.font.Font(fp, 40)
            self.fnt_large  = pg.font.Font(fp, 26)
            self.fnt_medium = pg.font.Font(fp, 21)
            self.fnt_small  = pg.font.Font(fp, 17)
            self.fnt_btn    = pg.font.Font(fp, 18)
            self.fnt_popup  = pg.font.Font(fp, 24)
        except Exception:
            self.fnt_title  = pg.font.SysFont('arial', 40, bold=True)
            self.fnt_large  = pg.font.SysFont('arial', 26, bold=True)
            self.fnt_medium = pg.font.SysFont('arial', 21, bold=True)
            self.fnt_small  = pg.font.SysFont('arial', 17, bold=True)
            self.fnt_btn    = pg.font.SysFont('arial', 18, bold=True)
            self.fnt_popup  = pg.font.SysFont('arial', 24, bold=True)

    def _setup_bg(self):
        raw = self.persist.get(c.LOSE_BACKGROUND)
        if raw:
            small      = pg.transform.smoothscale(raw,
                         (c.SCREEN_WIDTH // 3, c.SCREEN_HEIGHT // 3))
            self.bg    = pg.transform.smoothscale(small, c.SCREEN_SIZE)
        else:
            self.bg    = None
        self.dim       = pg.Surface(c.SCREEN_SIZE, pg.SRCALPHA)
        self.dim.fill((0, 0, 0, 160))

    def _setup_buttons(self):
        n       = len(self._BTN_DEFS)
        total_w = n * self._BTN_W + (n - 1) * self._BTN_GAP
        start_x = c.SCREEN_WIDTH // 2 - total_w // 2
        btn_y   = c.SCREEN_HEIGHT - 60

        self._btns = [
            pg.Rect(start_x + i * (self._BTN_W + self._BTN_GAP),
                    btn_y, self._BTN_W, self._BTN_H)
            for i in range(n)
        ]

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, surface, current_time, mouse_pos, mouse_click):
        self.current_time = current_time
        real_pos          = pg.mouse.get_pos()

        # Resolve hover
        self._hover = -1
        for i, btn in enumerate(self._btns):
            if btn.collidepoint(real_pos):
                self._hover = i

        # Auto-dismiss popup
        if self.popup_active and not self.popup_dismissed:
            if current_time - self.popup_timer > self.POPUP_DURATION:
                self.popup_dismissed = True

        if mouse_click and mouse_click[0]:
            if self.popup_active and not self.popup_dismissed:
                # First click dismisses popup, does not fire buttons yet
                self.popup_dismissed = True
            elif self._hover >= 0:
                label, target, *_ = self._BTN_DEFS[self._hover]
                if target == "exit":
                    pg.quit()
                    sys.exit()
                else:
                    self.next = target
                    self.done = True

        self._draw(surface)

    # ── draw ──────────────────────────────────────────────────────────────────

    def _draw(self, surface):
        if self.bg:
            surface.blit(self.bg, (0, 0))
        else:
            surface.fill((10, 10, 20))
        surface.blit(self.dim, (0, 0))

        cx = c.SCREEN_WIDTH // 2

        # ── main stats panel ──────────────────────────────────────────────────
        panel_w, panel_h = 520, 330
        panel_rect = pg.Rect(0, 0, panel_w, panel_h)
        panel_rect.center = (cx, c.SCREEN_HEIGHT // 2 - 25)

        panel_surf = pg.Surface((panel_w, panel_h), pg.SRCALPHA)
        pg.draw.rect(panel_surf, (15, 10, 25, 225),
                     panel_surf.get_rect(), border_radius=18)
        pg.draw.rect(panel_surf, (200, 50, 50, 255),
                     panel_surf.get_rect(), width=3, border_radius=18)
        surface.blit(panel_surf, panel_rect)

        py = panel_rect.top

        # Title
        _blit_text(surface, self.fnt_title, "GAME OVER",
                   (220, 50, 50), cx, py + 42)

        # Time survived
        _blit_text(surface, self.fnt_large,
                   f"Survived:  {_fmt_time(self.survival_ms)}",
                   _GOLD, cx, py + 103)

        # Score
        _blit_text(surface, self.fnt_large,
                   f"Score:  {self.score:,}",
                   _WHITE, cx, py + 145)

        # Stats row
        stats = (f"Zombies: {self.zombies_killed}"
                 f"   |   Sun: {self.sun_collected}"
                 f"   |   Plants: {self.plants_planted}")
        _blit_text(surface, self.fnt_small, stats, _GRAY, cx, py + 188)

        # NEW BEST badge
        extra_y = py + 228
        if self.is_best:
            _blit_text(surface, self.fnt_medium,
                       "NEW PERSONAL BEST!", _GOLD, cx, extra_y)
            extra_y += 36

        # Beaten users
        if self.beaten_users:
            names = ", ".join(self.beaten_users[:3])
            suffix = "..." if len(self.beaten_users) > 3 else "!"
            _blit_text(surface, self.fnt_small,
                       f"You beat: {names}{suffix}", _GREEN, cx, extra_y)

        # ── buttons ───────────────────────────────────────────────────────────
        border = (180, 140, 50)
        for i, (btn, (label, _, bg_n, bg_h)) in enumerate(
                zip(self._btns, self._BTN_DEFS)):
            bg = bg_h if i == self._hover else bg_n
            pg.draw.rect(surface, bg,     btn, border_radius=8)
            pg.draw.rect(surface, border, btn, 2, border_radius=8)
            lbl  = self.fnt_btn.render(label, True, _WHITE)
            shad = self.fnt_btn.render(label, True, (0, 0, 0))
            lx = btn.centerx - lbl.get_width()  // 2
            ly = btn.centery - lbl.get_height() // 2
            surface.blit(shad, (lx + 1, ly + 1))
            surface.blit(lbl,  (lx,     ly))

        # ── pop-up overlay ────────────────────────────────────────────────────
        if self.popup_active and not self.popup_dismissed:
            self._draw_popup(surface)

    def _draw_popup(self, surface):
        cx = c.SCREEN_WIDTH  // 2
        cy = c.SCREEN_HEIGHT // 2

        pw, ph = 420, 200
        pop    = pg.Surface((pw, ph), pg.SRCALPHA)
        pg.draw.rect(pop, (10, 50, 10, 245), pop.get_rect(), border_radius=16)
        pg.draw.rect(pop, (80, 220, 80, 255), pop.get_rect(), 3, border_radius=16)
        surface.blit(pop, pop.get_rect(center=(cx, cy)))

        content_y = cy - ph // 2 + 35

        if self.is_best:
            _blit_text(surface, self.fnt_popup,
                       "NEW PERSONAL BEST!", _GOLD, cx, content_y)
            content_y += 48

        if self.beaten_users:
            if len(self.beaten_users) == 1:
                msg = f"You beat {self.beaten_users[0]}!"
            else:
                names = " and ".join(self.beaten_users[:2])
                msg   = f"You beat {names}!"
            _blit_text(surface, self.fnt_medium, msg, _GREEN, cx, content_y)
            content_y += 36

        _blit_text(surface, self.fnt_small,
                   "Click anywhere to continue", _GRAY, cx, cy + ph // 2 - 28)


# =============================================================================
#  SURVIVAL LEADERBOARD
# =============================================================================

_TABLE_X = 80
_TABLE_W  = c.SCREEN_WIDTH - 160
_ROW_H    = 48
_HDR_H    = 40
_TABLE_Y  = 110

_COL_WIDTHS  = [60, 230, 170, 140, 40]    # Rank, Name, Best Score, Time, (pad)
_COL_LABELS  = ["RANK", "NAME", "BEST SCORE", "BEST TIME"]

_BTN_W       = 160
_BTN_H       = 36
_BTN_BORDER  = (180, 140, 50)
_BG_ROW      = [(30, 55, 30, 200), (20, 40, 20, 200)]


class SurvivalLeaderboard(engine.State):

    def __init__(self):
        engine.State.__init__(self)

    def startup(self, current_time, persist):
        self.persist        = persist
        self.game_info      = persist
        self.next           = c.MAIN_MENU
        self._current_user  = persist.get(c.CURRENT_USER, '').lower()
        self._hover_btn     = False

        self._board = get_survival_leaderboard()
        self._setup_fonts()
        self._setup_bg()
        self._setup_btn()

    def _setup_fonts(self):
        fp = c.STATS_FONT_PATH
        try:
            self.fnt_title = pg.font.Font(fp, 30)
            self.fnt_sub   = pg.font.Font(fp, 16)
            self.fnt_hdr   = pg.font.Font(fp, 17)
            self.fnt_row   = pg.font.Font(fp, 20)
            self.fnt_btn   = pg.font.Font(fp, 18)
        except Exception:
            self.fnt_title = pg.font.SysFont('arial', 30, bold=True)
            self.fnt_sub   = pg.font.SysFont('arial', 16, bold=True)
            self.fnt_hdr   = pg.font.SysFont('arial', 17, bold=True)
            self.fnt_row   = pg.font.SysFont('arial', 20, bold=True)
            self.fnt_btn   = pg.font.SysFont('arial', 18, bold=True)

    def _setup_bg(self):
        try:
            raw    = engine.GFX[c.MAIN_MENU_IMAGE]
            self._bg = pg.transform.smoothscale(raw, c.SCREEN_SIZE)
        except Exception:
            self._bg = None
        self._dim = pg.Surface(c.SCREEN_SIZE, pg.SRCALPHA)
        self._dim.fill((0, 0, 0, 155))

    def _setup_btn(self):
        self._btn = pg.Rect(
            c.SCREEN_WIDTH // 2 - _BTN_W // 2,
            c.SCREEN_HEIGHT - 55,
            _BTN_W, _BTN_H)

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, surface, current_time, mouse_pos, mouse_click):
        real_pos         = pg.mouse.get_pos()
        self._hover_btn  = self._btn.collidepoint(real_pos)

        if mouse_click and mouse_click[0] and self._hover_btn:
            self.next = c.MAIN_MENU
            self.done = True
            return

        self._draw(surface)

    # ── draw ──────────────────────────────────────────────────────────────────

    def _draw(self, surface):
        if self._bg:
            surface.blit(self._bg, (0, 0))
        else:
            surface.fill((10, 25, 10))
        surface.blit(self._dim, (0, 0))

        cx = c.SCREEN_WIDTH // 2

        # Title
        _blit_text(surface, self.fnt_title,
                   "SURVIVAL LEADERBOARD", _GOLD, cx, 44)
        _blit_text(surface, self.fnt_sub,
                   "Score = Zombies x100 + Sun x2 + Plants x10 + Seconds x5",
                   _GRAY, cx, 74, shadow=False)

        self._draw_table(surface)
        self._draw_btn(surface)

    def _draw_table(self, surface):
        tx, ty = _TABLE_X, _TABLE_Y
        tw     = sum(_COL_WIDTHS)

        # Header
        hdr_surf = pg.Surface((tw, _HDR_H), pg.SRCALPHA)
        hdr_surf.fill((0, 0, 0, 180))
        surface.blit(hdr_surf, (tx, ty))
        pg.draw.rect(surface, _GOLD, (tx, ty, tw, _HDR_H), 1)

        x = tx
        for lbl, cw in zip(_COL_LABELS, _COL_WIDTHS):
            s = self.fnt_hdr.render(lbl, True, _GOLD)
            surface.blit(s, s.get_rect(center=(x + cw // 2, ty + _HDR_H // 2)))
            x += cw

        # Empty state
        if not self._board:
            empty = self.fnt_row.render(
                "No survival scores yet - be the first!", True, _GRAY)
            surface.blit(empty, empty.get_rect(
                center=(tx + tw // 2, ty + _HDR_H + 60)))
            pg.draw.rect(surface, _GOLD, (tx, ty, tw, _HDR_H + 80), 2)
            return

        # Data rows
        for idx, entry in enumerate(self._board):
            ry    = ty + _HDR_H + idx * _ROW_H
            is_me = entry['name'].lower() == self._current_user

            row_bg = pg.Surface((tw, _ROW_H), pg.SRCALPHA)
            row_bg.fill((40, 100, 40, 210) if is_me else _BG_ROW[idx % 2])
            surface.blit(row_bg, (tx, ry))
            pg.draw.line(surface, (60, 80, 60),
                         (tx, ry + _ROW_H - 1), (tx + tw, ry + _ROW_H - 1))

            rank = idx + 1
            if   rank == 1: rank_col = _GOLD
            elif rank == 2: rank_col = _SILVER
            elif rank == 3: rank_col = _BRONZE
            else:           rank_col = _WHITE

            txt_col = _GREEN if is_me else _WHITE
            name_txt = entry['name'] + (" (You)" if is_me else "")

            cells = [
                (str(rank),                             rank_col),
                (name_txt,                              txt_col),
                (f"{entry['survival_score']:,}",        txt_col),
                (_fmt_time(entry.get('survival_time', 0)), txt_col),
            ]

            x = tx
            for (text, color), cw in zip(cells, _COL_WIDTHS):
                s = self.fnt_row.render(text, True, color)
                surface.blit(s, s.get_rect(
                    center=(x + cw // 2, ry + _ROW_H // 2)))
                x += cw

        total_h = _HDR_H + len(self._board) * _ROW_H
        pg.draw.rect(surface, _GOLD, (tx, ty, tw, total_h), 2)

    def _draw_btn(self, surface):
        bg = (50, 95, 185) if self._hover_btn else (30, 60, 130)
        pg.draw.rect(surface, bg,          self._btn, border_radius=7)
        pg.draw.rect(surface, _BTN_BORDER, self._btn, 2, border_radius=7)
        lbl  = self.fnt_btn.render("Main Menu", True, _WHITE)
        shad = self.fnt_btn.render("Main Menu", True, (0, 0, 0))
        lx   = self._btn.centerx - lbl.get_width()  // 2
        ly   = self._btn.centery - lbl.get_height() // 2
        surface.blit(shad, (lx + 1, ly + 1))
        surface.blit(lbl,  (lx,     ly))