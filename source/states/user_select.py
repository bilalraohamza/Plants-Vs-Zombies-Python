__author__ = 'Rao Hamza Bilal'

import os
import json
import pygame as pg
from ..core import constants as c
from ..core import engine


# -----------------------------------------
#  Save-data helpers
# -----------------------------------------
def load_profiles():
    if not os.path.exists(c.SAVE_DATA_PATH):
        return []
    try:
        with open(c.SAVE_DATA_PATH, 'r') as f:
            data = json.load(f)
        return data.get('profiles', [])
    except (json.JSONDecodeError, IOError):
        return []


def save_profiles(profiles):
    os.makedirs(os.path.dirname(c.SAVE_DATA_PATH), exist_ok=True)
    with open(c.SAVE_DATA_PATH, 'w') as f:
        json.dump({'profiles': profiles}, f, indent=4)


def add_profile(name, level=1):
    profiles = load_profiles()
    for p in profiles:
        if p['name'].lower() == name.lower():
            return False
    profiles.append({'name': name, 'level': level})
    save_profiles(profiles)
    return True


def delete_profile(name):
    profiles = load_profiles()
    profiles = [p for p in profiles if p['name'].lower() != name.lower()]
    save_profiles(profiles)


def update_profile_level(name, level):
    profiles = load_profiles()
    for p in profiles:
        if p['name'].lower() == name.lower():
            if level > p['level']:
                p['level'] = level
            save_profiles(profiles)
            return


# -----------------------------------------
#  UI helpers
# -----------------------------------------
def draw_plain_text(surface, font, text, color, cx, cy):
    """No shadow - matches main menu plain text style."""
    surf = font.render(text, True, color)
    surface.blit(surf, surf.get_rect(center=(cx, cy)))


def draw_title_text(surface, font, text, color, cx, cy):
    """Title text with subtle shadow for readability over background."""
    shadow = font.render(text, True, (0, 0, 0))
    surf   = font.render(text, True, color)
    surface.blit(shadow, shadow.get_rect(center=(cx + 2, cy + 2)))
    surface.blit(surf,   surf.get_rect(center=(cx, cy)))


def draw_panel(surface, rect, panel_img=None):
    if panel_img:
        scaled = pg.transform.smoothscale(panel_img, (rect.width, rect.height))
        surface.blit(scaled, rect)
    else:
        panel = pg.Surface((rect.width, rect.height), pg.SRCALPHA)
        pg.draw.rect(panel, (100, 100, 130, 210), panel.get_rect(), border_radius=18)
        pg.draw.rect(panel, (180, 180, 210, 255), panel.get_rect(),
                     width=3, border_radius=18)
        surface.blit(panel, rect)


def draw_nav_button(surface, font, text, cx, cy, hovered, scale=1.2):
    """
    Plain text button - no background, no shadow.
    Matches main menu exactly: white idle, green hover, scale on hover.
    """
    color = (0, 193, 33) if hovered else (255, 255, 255)
    surf  = font.render(text, True, color)
    if hovered:
        surf = pg.transform.smoothscale(surf,
               (int(surf.get_width() * scale),
                int(surf.get_height() * scale)))
    rect = surf.get_rect(center=(cx, cy))
    surface.blit(surf, rect)
    return rect


def draw_x_button(surface, font, rect, hovered=False):
    bg   = (160, 30, 30) if hovered else (110, 20, 20)
    bord = (255, 100, 100) if hovered else (190, 60, 60)
    panel = pg.Surface((rect.width, rect.height), pg.SRCALPHA)
    pg.draw.rect(panel, (*bg, 235), panel.get_rect(), border_radius=8)
    pg.draw.rect(panel, (*bord, 255), panel.get_rect(), width=2, border_radius=8)
    surface.blit(panel, rect)
    x_surf = font.render('X', True, (255, 210, 210))
    surface.blit(x_surf, x_surf.get_rect(center=rect.center))


# -----------------------------------------
#  Main state
# -----------------------------------------
class UserSelectScreen(engine.State):

    W, H         = c.SCREEN_WIDTH, c.SCREEN_HEIGHT
    # Select Profile panel (main screen)
    SELECT_PANEL_W = 550
    SELECT_PANEL_H = 280

    # Choose Profile panel (existing user screen)
    CHOOSE_PANEL_W = 380
    CHOOSE_PANEL_H = 280
    MAX_NAME_LEN = 18
    ROWS_VISIBLE = 4

    GOLD  = (255, 215, 60)
    WHITE = (255, 255, 255)
    GREEN = (0, 193, 33)
    RED   = (220, 60, 60)

    def __init__(self):
        engine.State.__init__(self)

    def startup(self, current_time, persist):
        self.persist   = persist
        self.game_info = persist
        self.next      = c.MAIN_MENU
        self.sub_state = 'main'
        self._init_fonts()
        self._init_background()
        self._reset_new_user()
        self._reset_existing_user()

    def update(self, surface, current_time, mouse_pos, mouse_click):
        self.current_time = current_time
        real_mouse = pg.mouse.get_pos()

        surface.blit(self.bg, (0, 0))
        dim = pg.Surface((self.W, self.H), pg.SRCALPHA)
        dim.fill((0, 0, 0, 150))
        surface.blit(dim, (0, 0))

        if self.sub_state == 'main':
            self._update_main(surface, real_mouse, mouse_pos, mouse_click)
        elif self.sub_state == 'new_user':
            self._update_new_user(surface, real_mouse, mouse_pos, mouse_click)
        elif self.sub_state == 'existing_user':
            self._update_existing_user(surface, real_mouse, mouse_pos, mouse_click)

    # -- init --
    def _init_fonts(self):
        fp = os.path.join(c.FONTS_DIR, 'Fredoka-Bold.ttf')
        try:
            self.font_title = pg.font.Font(fp, 40)
            self.font_btn   = pg.font.Font(fp, 28)
            self.font_sub   = pg.font.Font(fp, 18)
            self.font_input = pg.font.Font(fp, 26)
            self.font_small = pg.font.Font(fp, 22)
            self.font_tiny  = pg.font.Font(fp, 16)
        except (IOError, FileNotFoundError):
            self.font_title = pg.font.SysFont('arial', 40, bold=True)
            self.font_btn   = pg.font.SysFont('arial', 28, bold=True)
            self.font_sub   = pg.font.SysFont('arial', 18, bold=True)
            self.font_input = pg.font.SysFont('arial', 26, bold=True)
            self.font_small = pg.font.SysFont('arial', 22, bold=True)
            self.font_tiny  = pg.font.SysFont('arial', 16, bold=True)

    def _init_background(self):
        try:
            raw = engine.GFX[c.MAIN_MENU_IMAGE]
            self.bg = pg.transform.smoothscale(raw, (self.W, self.H))
        except (KeyError, TypeError):
            self.bg = pg.Surface((self.W, self.H))
            self.bg.fill((20, 60, 20))

        try:
            raw_panel = engine.GFX['UserSelectPanel']
            self.panel_img = raw_panel.convert_alpha()
            self.panel_img.set_colorkey((0, 0, 0))
        except (KeyError, TypeError):
            self.panel_img = None

    def _reset_new_user(self):
        self.name_input   = ''
        self.error_msg    = ''
        self.cursor_timer = 0
        self.show_cursor  = True

    def _reset_existing_user(self):
        self.profiles       = []
        self.scroll_offset  = 0
        self.delete_confirm = -1

    # -- helpers --

    def _select_panel_rect(self):
        r = pg.Rect(0, 0, self.SELECT_PANEL_W, self.SELECT_PANEL_H)
        r.center = (self.W // 2, self.H // 2 + 30)
        return r
    def _choose_panel_rect(self):
        r = pg.Rect(0, 0, self.CHOOSE_PANEL_W, self.CHOOSE_PANEL_H)
        r.center = (self.W // 2, self.H // 2 + 30)
        return r

    # -- MAIN --
    def _update_main(self, surface, real_mouse, mouse_pos, mouse_click):
        cx = self.W // 2
        pr = self._select_panel_rect()
        draw_panel(surface, pr, self.panel_img)

        # Title above panel, with subtle shadow for readability over bg
        draw_title_text(surface, self.font_title, 'Select Profile',
                        self.GOLD, cx, pr.top - 10)

        # Sub text inside panel, no shadow
        draw_plain_text(surface, self.font_sub, 'Who is playing today?',
                        (210, 190, 130), cx, pr.top + 15)

        # Buttons - plain text, no shadow, white/green like main menu
        h_new = False
        h_ex  = False

        btn_new_y = pr.top + 110
        btn_ex_y  = pr.top + 170

        # Build hover rects
        new_surf = self.font_btn.render('New User', True, self.WHITE)
        ex_surf  = self.font_btn.render('Existing User', True, self.WHITE)
        self._btn_new_rect = new_surf.get_rect(center=(cx, btn_new_y))
        self._btn_ex_rect  = ex_surf.get_rect(center=(cx, btn_ex_y))

        h_new = self._btn_new_rect.collidepoint(real_mouse)
        h_ex  = self._btn_ex_rect.collidepoint(real_mouse)

        new_r = draw_nav_button(surface, self.font_btn, 'New User',
                                cx, btn_new_y, h_new)
        ex_r  = draw_nav_button(surface, self.font_btn, 'Existing User',
                                cx, btn_ex_y, h_ex)

        self._btn_new_rect = new_r
        self._btn_ex_rect  = ex_r

        if mouse_pos and mouse_click and mouse_click[0]:
            if h_new:
                self._reset_new_user()
                self.sub_state = 'new_user'
            elif h_ex:
                self._reset_existing_user()
                self.profiles = load_profiles()
                self.sub_state = 'existing_user'

    # -- NEW USER --
    def _update_new_user(self, surface, real_mouse, mouse_pos, mouse_click):
        cx = self.W // 2
        pr = self._select_panel_rect()
        draw_panel(surface, pr, self.panel_img)

        draw_title_text(surface, self.font_title, 'New User',
                        self.GOLD, cx, pr.top - 28)

        draw_plain_text(surface, self.font_sub, 'Enter your name:',
                        (210, 190, 130), cx, pr.top + 38)

        # Input box
        input_rect = pg.Rect(0, 0, 290, 44)
        input_rect.center = (cx, pr.top + 100)
        pg.draw.rect(surface, (30, 22, 8), input_rect, border_radius=8)
        pg.draw.rect(surface, self.GOLD, input_rect, width=2, border_radius=8)

        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_timer = 0
            self.show_cursor  = not self.show_cursor

        display = self.name_input + ('|' if self.show_cursor else '')
        t = self.font_input.render(display, True, self.WHITE)
        surface.blit(t, t.get_rect(midleft=(input_rect.left + 10,
                                             input_rect.centery)))

        if self.error_msg:
            draw_plain_text(surface, self.font_tiny, self.error_msg,
                            self.RED, cx, input_rect.bottom + 18)

        btn_y    = pr.top + 210
        h_create = pg.Rect(cx + 30, btn_y - 16, 100, 32).collidepoint(real_mouse)
        h_back   = pg.Rect(cx - 130, btn_y - 16, 80, 32).collidepoint(real_mouse)

        cr = draw_nav_button(surface, self.font_small, 'Create',
                             cx + 80, btn_y, h_create)
        br = draw_nav_button(surface, self.font_small, 'Back',
                             cx - 80, btn_y, h_back)

        h_create = cr.collidepoint(real_mouse)
        h_back   = br.collidepoint(real_mouse)

        for event in self.game_info.get('key_events', []):
            if event.key == pg.K_BACKSPACE:
                self.name_input = self.name_input[:-1]
                self.error_msg  = ''
            elif event.key == pg.K_RETURN:
                self._try_create_user()
            elif len(self.name_input) < self.MAX_NAME_LEN:
                if event.unicode.isprintable():
                    self.name_input += event.unicode
                    self.error_msg   = ''

        if mouse_pos and mouse_click and mouse_click[0]:
            if h_create:
                self._try_create_user()
            elif h_back:
                self.sub_state = 'main'

    def _try_create_user(self):
        name = self.name_input.strip()
        if not name:
            self.error_msg = 'Name cannot be empty!'
            return
        if not add_profile(name, level=1):
            self.error_msg = 'Name already taken!'
            return
        self._launch_game(name, 1)

    # -- EXISTING USER --
    def _update_existing_user(self, surface, real_mouse, mouse_pos, mouse_click):
        cx = self.W // 2
        pr = self._select_panel_rect()
        draw_panel(surface, pr, self.panel_img)

        draw_title_text(surface, self.font_title, 'Choose Profile',
                        self.GOLD, cx, pr.top - 28)

        if not self.profiles:
            draw_plain_text(surface, self.font_small, 'No saved profiles found.',
                            (210, 190, 130), cx, pr.centery - 20)
            draw_plain_text(surface, self.font_tiny,
                            'Go back and create a New User.',
                            (170, 150, 110), cx, pr.centery + 16)
        else:
            self._draw_profile_list(surface, real_mouse,
                                    mouse_pos, mouse_click, pr)

        # Back button below panel, no shadow, plain like main menu
        back_y  = pr.bottom + 26
        h_back  = abs(pg.mouse.get_pos()[1] - back_y) < 20 and \
                  abs(pg.mouse.get_pos()[0] - cx) < 60
        br = draw_nav_button(surface, self.font_btn, 'Back',
                             cx, back_y, h_back)
        h_back = br.collidepoint(real_mouse)

        if mouse_pos and mouse_click and mouse_click[0] and h_back:
            self.delete_confirm = -1
            self.sub_state = 'main'

    def _draw_profile_list(self, surface, real_mouse, mouse_pos,
                           mouse_click, pr):
        cx        = self.W // 2
        row_h     = 52
        list_top  = pr.top + 50
        visible   = self.ROWS_VISIBLE
        total     = len(self.profiles)
        max_scroll = max(0, total - visible)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        for i in range(visible):
            idx = i + self.scroll_offset
            if idx >= total:
                break

            profile  = self.profiles[idx]
            name_cy  = list_top + i * row_h + 16
            lvl_cy   = list_top + i * row_h + 36
            del_rect = pg.Rect(cx + 105, list_top + i * row_h + 8, 34, 30)

            # Hover area covers the name text zone
            hov_area = pg.Rect(cx - 150, list_top + i * row_h, 260, row_h - 4)
            hov_row  = hov_area.collidepoint(real_mouse)
            hov_del  = del_rect.collidepoint(real_mouse)

            # Name - plain text, no shadow, white/green like main menu
            name_color = self.GREEN if hov_row else self.WHITE
            name_surf  = self.font_small.render(profile['name'], True, name_color)
            if hov_row:
                name_surf = pg.transform.smoothscale(name_surf,
                            (int(name_surf.get_width() * 1.1),
                             int(name_surf.get_height() * 1.1)))
            surface.blit(name_surf, name_surf.get_rect(
                midleft=(cx - 145, name_cy)))

            # Level text - plain, no shadow
            lvl_surf = self.font_tiny.render(
                f"Level {profile['level']}", True, (180, 160, 100))
            surface.blit(lvl_surf, lvl_surf.get_rect(midleft=(cx - 145, lvl_cy)))

            draw_x_button(surface, self.font_tiny, del_rect, hovered=hov_del)

            if mouse_pos and mouse_click and mouse_click[0]:
                if hov_del:
                    if self.delete_confirm == idx:
                        delete_profile(profile['name'])
                        self.profiles = load_profiles()
                        self.delete_confirm = -1
                        self.scroll_offset = max(
                            0, min(self.scroll_offset,
                                   len(self.profiles) - visible))
                    else:
                        self.delete_confirm = idx
                elif hov_row:
                    self._launch_game(profile['name'], profile['level'])
                    self.delete_confirm = -1

            if self.delete_confirm == idx:
                c_surf = self.font_tiny.render('Confirm?', True, self.RED)
                surface.blit(c_surf, c_surf.get_rect(
                    midleft=(del_rect.right + 4, del_rect.centery)))

        # Scroll arrows if needed
        if self.scroll_offset > 0:
            br = draw_nav_button(surface, self.font_tiny, 'up',
                                 cx + 152, list_top + 10, False)
            if mouse_pos and mouse_click and mouse_click[0]:
                if br.collidepoint(real_mouse):
                    self.scroll_offset -= 1

        if self.scroll_offset < max_scroll:
            br = draw_nav_button(surface, self.font_tiny, 'dn',
                                 cx + 152,
                                 list_top + visible * row_h - 14, False)
            if mouse_pos and mouse_click and mouse_click[0]:
                if br.collidepoint(real_mouse):
                    self.scroll_offset += 1

    # -- Launch --
    def _launch_game(self, name, level):
        self.persist[c.CURRENT_USER] = name
        self.persist[c.LEVEL_NUM]    = level
        self.next = c.MAIN_MENU
        self.done = True