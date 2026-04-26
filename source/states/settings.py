__author__ = 'Rao Hamza Bilal'

import json
import os
import pygame as pg
from ..core import constants as c
from ..core import engine
from ..states.user_select import (load_profiles, save_profiles,
                                   delete_profile, get_leaderboard)
from ..states.hint_system import _save_tutorial_seen

# ── colours ──────────────────────────────────────────────────
_GOLD       = (255, 210,  50)
_WHITE      = (235, 235, 235)
_GREEN      = ( 80, 210,  80)
_RED        = (210,  60,  60)
_RED_H      = (240,  90,  90)
_GRAY       = (140, 140, 140)
_BTN_BORDER = (180, 140,  50)

# ── panel dimensions ─────────────────────────────────────────
_PW, _PH    = 480, 430
_PX         = c.SCREEN_WIDTH  // 2 - _PW // 2
_PY         = c.SCREEN_HEIGHT // 2 - _PH // 2

# ── row layout inside panel ───────────────────────────────────
_ROW_H      = 54
_ROWS_TOP   = _PY + 80
_BTN_W      = 170
_BTN_H      = 34


class Settings(engine.State):
    def __init__(self):
        engine.State.__init__(self)

    def startup(self, current_time, persist):
        self.start_time    = current_time
        self.persist       = persist
        self.game_info     = persist
        self.next          = c.MAIN_MENU
        self.current_user  = persist.get(c.CURRENT_USER, '')

        # Confirm states
        self._confirm      = None   # None | 'delete_scores' | 'delete_account'
        self._feedback     = ''     # short message shown after an action
        self._feedback_timer = 0

        self._hover        = -1
        self._setup_fonts()
        self._setup_bg()
        self._build_rows()

    # ── setup ─────────────────────────────────────────────────
    def _setup_fonts(self):
        pg.font.init()
        try:
            fp = c.STATS_FONT_PATH
            self.fnt_title  = pg.font.Font(fp, 28)
            self.fnt_row    = pg.font.Font(fp, 20)
            self.fnt_btn    = pg.font.Font(fp, 18)
            self.fnt_tiny   = pg.font.Font(fp, 15)
        except (IOError, AttributeError):
            self.fnt_title  = pg.font.SysFont('arial', 28, bold=True)
            self.fnt_row    = pg.font.SysFont('arial', 20, bold=True)
            self.fnt_btn    = pg.font.SysFont('arial', 18, bold=True)
            self.fnt_tiny   = pg.font.SysFont('arial', 15)

    def _setup_bg(self):
        try:
            raw      = engine.GFX[c.MAIN_MENU_IMAGE]
            self._bg = pg.transform.smoothscale(raw, (c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        except Exception:
            self._bg = None
        dim = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pg.SRCALPHA)
        dim.fill((0, 0, 0, 160))
        self._dim = dim

    def _build_rows(self):
        """
        Each row: (label, description, btn_label, action_key, btn_color, btn_hover)
        """
        self._rows = [
            ('GAME',     'Reset Tutorial',
             'Reset',    'reset_tutorial',
             (40, 100, 40), (60, 140, 60)),

            ('DISPLAY',  'Show FPS Counter',
             'ON' if self.persist.get('show_fps', False) else 'OFF',
             'toggle_fps',
             (40, 60, 120), (60, 90, 170)),

            ('PROFILE',  'Switch Profile',
             'Switch',   'switch_profile',
             (90, 60, 15), (130, 90, 25)),

            ('PROFILE',  'Delete My Scores',
             'Delete',   'delete_scores',
             (130, 35, 35), (175, 55, 55)),

            ('PROFILE',  'Delete Account',
             'Delete',   'delete_account',
             (110, 20, 20), (160, 40, 40)),
        ]
        self._btn_rects = []
        for i in range(len(self._rows)):
            ry = _ROWS_TOP + i * _ROW_H
            bx = _PX + _PW - _BTN_W - 18
            self._btn_rects.append(pg.Rect(bx, ry + (_ROW_H - _BTN_H) // 2,
                                           _BTN_W, _BTN_H))

        # Back button
        self._back_rect = pg.Rect(c.SCREEN_WIDTH // 2 - 80,
                                  _PY + _PH - 50, 160, 36)

    # ── update ────────────────────────────────────────────────
    def update(self, surface, current_time, mouse_pos, mouse_click):
        self.current_time = current_time
        real_pos          = pg.mouse.get_pos()

        # Hover
        self._hover = -1
        for i, r in enumerate(self._btn_rects):
            if r.collidepoint(real_pos):
                self._hover = i
                break
        self._hover_back = self._back_rect.collidepoint(real_pos)

        # Click
        if mouse_click and mouse_click[0]:
            if self._hover >= 0:
                self._handle_action(self._rows[self._hover][3])
            elif self._hover_back:
                self.next = c.MAIN_MENU
                self.done = True

        # Feedback timer
        if self._feedback and current_time - self._feedback_timer > 2500:
            self._feedback = ''

        self._draw(surface)

    # ── actions ───────────────────────────────────────────────
    def _handle_action(self, key):
        if self._confirm == key:
            # Second click = confirmed
            self._execute(key)
            self._confirm = None
        elif key in ('delete_scores', 'delete_account'):
            self._confirm = key   # ask for confirmation first
        else:
            self._execute(key)

    def _execute(self, key):
        if key == 'reset_tutorial':
            # Set tutorial_seen = False so hints reappear
            try:
                with open(c.SAVE_DATA_PATH) as f:
                    data = json.load(f)
                for p in data.get('profiles', []):
                    if p['name'].lower() == self.current_user.lower():
                        p['tutorial_seen'] = False
                        break
                os.makedirs(os.path.dirname(c.SAVE_DATA_PATH), exist_ok=True)
                with open(c.SAVE_DATA_PATH, 'w') as f:
                    json.dump(data, f, indent=4)
                self._feedback = 'Tutorial reset! Hints will show on Level 1.'
            except Exception:
                self._feedback = 'Could not reset tutorial.'
            self._feedback_timer = self.current_time

        elif key == 'toggle_fps':
            current = self.persist.get('show_fps', False)
            self.persist['show_fps'] = not current
            # Update button label live
            self._rows[1] = (
                self._rows[1][0], self._rows[1][1],
                'ON' if self.persist['show_fps'] else 'OFF',
                self._rows[1][3], self._rows[1][4], self._rows[1][5]
            )

        elif key == 'switch_profile':
            self.next = c.USER_SELECT
            self.done = True

        elif key == 'delete_scores':
            profiles = load_profiles()
            for p in profiles:
                if p['name'].lower() == self.current_user.lower():
                    p['scores'] = {}
                    p.pop('survival_score', None)   # also clear survival best
                    p.pop('survival_time',  None)
                    break
            save_profiles(profiles)
            self._feedback = 'All your scores have been deleted.'
            self._feedback_timer = self.current_time
            self._confirm = None

        elif key == 'delete_account':
            delete_profile(self.current_user)
            self.next = c.USER_SELECT
            self.done = True

    # ── draw ──────────────────────────────────────────────────
    def _draw(self, surface):
        if self._bg:
            surface.blit(self._bg, (0, 0))
        else:
            surface.fill((10, 25, 10))
        surface.blit(self._dim, (0, 0))

        # Panel background
        panel = pg.Surface((_PW, _PH), pg.SRCALPHA)
        panel.fill((15, 22, 35, 230))
        surface.blit(panel, (_PX, _PY))
        pg.draw.rect(surface, _BTN_BORDER, (_PX, _PY, _PW, _PH), 2, border_radius=10)

        # Title
        title  = self.fnt_title.render('SETTINGS', True, _GOLD)
        shadow = self.fnt_title.render('SETTINGS', True, (0, 0, 0))
        tx     = _PX + _PW // 2 - title.get_width() // 2
        surface.blit(shadow, (tx + 2, _PY + 22))
        surface.blit(title,  (tx,     _PY + 20))

        # Separator
        pg.draw.line(surface, _BTN_BORDER,
                     (_PX + 16, _PY + 58), (_PX + _PW - 16, _PY + 58), 1)

        # Rows
        last_section = ''
        for i, (section, desc, btn_lbl, action, bg_n, bg_h) in enumerate(self._rows):
            ry = _ROWS_TOP + i * _ROW_H

            # Section label (only when it changes)
            if section != last_section:
                sl = self.fnt_tiny.render(section, True, _GOLD)
                surface.blit(sl, (_PX + 18, ry))
                last_section = section

            # Description
            dl = self.fnt_row.render(desc, True, _WHITE)
            surface.blit(dl, (_PX + 18, ry + 20))

            # Action button
            rect   = self._btn_rects[i]
            is_confirm = (self._confirm == action)
            bg     = bg_h if (i == self._hover or is_confirm) else bg_n
            label  = 'Confirm?' if is_confirm else btn_lbl

            pg.draw.rect(surface, bg,          rect, border_radius=7)
            pg.draw.rect(surface, _BTN_BORDER,  rect, 2, border_radius=7)

            lbl  = self.fnt_btn.render(label, True, _WHITE)
            shad = self.fnt_btn.render(label, True, (0, 0, 0))
            lx   = rect.centerx - lbl.get_width()  // 2
            ly   = rect.centery - lbl.get_height() // 2
            surface.blit(shad, (lx + 1, ly + 1))
            surface.blit(lbl,  (lx,     ly))

            # Row separator
            pg.draw.line(surface, (40, 55, 40),
                         (_PX + 12, ry + _ROW_H - 2),
                         (_PX + _PW - 12, ry + _ROW_H - 2))

        # Feedback message
        if self._feedback:
            fs = self.fnt_tiny.render(self._feedback, True, _GREEN)
            surface.blit(fs, fs.get_rect(center=(c.SCREEN_WIDTH // 2,
                                                  _PY + _PH - 70)))

        # Back button
        bg = (50, 95, 185) if self._hover_back else (30, 60, 130)
        pg.draw.rect(surface, bg,          self._back_rect, border_radius=7)
        pg.draw.rect(surface, _BTN_BORDER,  self._back_rect, 2, border_radius=7)
        bl   = self.fnt_btn.render('Back', True, _WHITE)
        bsh  = self.fnt_btn.render('Back', True, (0, 0, 0))
        lx   = self._back_rect.centerx - bl.get_width()  // 2
        ly   = self._back_rect.centery - bl.get_height() // 2
        surface.blit(bsh, (lx + 1, ly + 1))
        surface.blit(bl,  (lx,     ly))