__author__ = 'Rao Hamza Bilal'

import pygame as pg
from ..core import constants as c
from ..core import engine
from ..states.user_select import load_profiles


# ==========================================
# --- BASE SCREEN CLASS ---
# ==========================================
class Screen(engine.State):
    def __init__(self):
        engine.State.__init__(self)
        self.end_time = 3000

    def startup(self, current_time, persist):
        self.start_time = current_time
        self.next       = c.LEVEL
        self.persist    = persist
        self.game_info  = persist
        name            = self.get_image_name()
        self.setup_background()
        self.setup_image(name)
        self.next       = self.set_next_state()

    def get_image_name(self):       pass
    def set_next_state(self):       pass
    def get_background_color(self): return c.WHITE
    def setup_background(self):     self.background_image = None

    def setup_blurred_background(self, key, blur_scale, dim_alpha):
        if key not in self.persist:
            self.background_image = None
            return
        background   = self.persist[key]
        small_size   = (max(1, c.SCREEN_WIDTH // blur_scale),
                        max(1, c.SCREEN_HEIGHT // blur_scale))
        small        = pg.transform.smoothscale(background, small_size)
        self.background_image = pg.transform.smoothscale(small, c.SCREEN_SIZE)
        dim          = pg.Surface(c.SCREEN_SIZE, pg.SRCALPHA)
        dim.fill((0, 0, 0, dim_alpha))
        self.background_image.blit(dim, (0, 0))

    def setup_image(self, name):
        raw        = engine.GFX[name]
        self.image = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pg.SRCALPHA).convert_alpha()
        self.image.blit(raw, (0, 0), (0, 0, c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        self.rect  = self.image.get_rect(topleft=(0, 0))

    def update(self, surface, current_time, mouse_pos, mouse_click):
        if (current_time - self.start_time) < self.end_time:
            if self.background_image:
                surface.blit(self.background_image, (0, 0))
            else:
                surface.fill(self.get_background_color())
            surface.blit(self.image, self.rect)
        else:
            self.done = True


# ==========================================
# --- VICTORY SCREEN ---
# ==========================================
class GameVictoryScreen(Screen):
    _BTN_W      = 118
    _BTN_H      = 36
    _BTN_GAP    = 10
    _BTN_BORDER = (180, 140, 50)

    _BTN_DEFS = [
        ("Exit",         "exit",         (130, 35,  35), (175, 55,  55), (255, 255, 255)),
        ("Level Select", c.LEVEL_SELECT, ( 40, 60,  130), ( 60, 90, 180), (255, 255, 255)),
        ("Main Menu",    c.MAIN_MENU,    ( 90, 60,   15), (130, 90,  25), (255, 220, 100)),
        ("Next Level",   c.LEVEL,        ( 30, 110,  30), ( 50, 155, 50), (255, 255, 255)),
    ]

    def __init__(self):
        Screen.__init__(self)
        self.end_time = 999999
        self._hover   = -1
        self._buttons = []

    def get_image_name(self):       return c.GAME_VICTORY_IMAGE
    def set_next_state(self):       return c.LEVEL
    def get_background_color(self): return c.GAME_VICTORY_BACKGROUND_COLOR

    def setup_background(self):
        self.setup_blurred_background(
            c.VICTORY_BACKGROUND, c.GAME_VICTORY_BLUR_SCALE, c.GAME_VICTORY_DIM_ALPHA)

    def setup_image(self, name):
        raw        = engine.GFX[name].convert_alpha()
        self.image = pg.transform.smoothscale(raw, (c.GAME_VICTORY_WIDTH, c.GAME_VICTORY_HEIGHT))
        self.image.set_colorkey(c.BLACK)
        self.rect  = self.image.get_rect(topleft=(c.GAME_VICTORY_X, c.GAME_VICTORY_Y))
        self._setup_content()

    def _setup_content(self):
        pg.font.init()
        try:
            self.font_lg  = pg.font.Font(c.STATS_FONT_PATH, 30)
            self.font_md  = pg.font.Font(c.STATS_FONT_PATH, 22)
            self.font_sm  = pg.font.Font(c.STATS_FONT_PATH, 17)
            self.font_btn = pg.font.Font(c.STATS_FONT_PATH, 19)
        except (IOError, AttributeError):
            self.font_lg  = pg.font.SysFont("arial", 30, bold=True)
            self.font_md  = pg.font.SysFont("arial", 22, bold=True)
            self.font_sm  = pg.font.SysFont("arial", 17, bold=True)
            self.font_btn = pg.font.SysFont("arial", 19, bold=True)

        zombies = self.persist.get(c.ZOMBIES_KILLED, 0)
        sun     = self.persist.get(c.SUN_COLLECTED,  0)
        plants  = self.persist.get(c.PLANTS_PLANTED, 0)
        score   = self.persist.get(c.LEVEL_SCORE,    0)
        is_best = self.persist.get(c.LEVEL_SCORE_IS_BEST, False)
        beaten  = self.persist.get(c.BEATEN_USERS,   [])

        score_label = f"Score:  {score}" + ("   * NEW BEST!" if is_best else "")

        self.stat_lines = [
            (self.font_lg, f"Zombies Defeated:  {zombies}", (255, 200,  50), (60, 30, 0)),
            (self.font_md, f"Plants Planted:       {plants}", ( 80, 200,  80), (60, 30, 0)),
            (self.font_md, f"Sun Collected:        {sun}",    (255, 140,   0), (60, 30, 0)),
            (self.font_md, score_label,
             (255, 255, 80) if is_best else (180, 220, 255), (30, 30, 60)),
        ]

        self.beat_lines = []
        if beaten:
            names = ", ".join(beaten[:3])
            self.beat_lines.append(
                (self.font_sm, f"You beat:  {names}!", (100, 255, 130), (0, 50, 0))
            )

        self._build_buttons()

    def _build_buttons(self):
        n       = len(self._BTN_DEFS)
        total_w = n * self._BTN_W + (n - 1) * self._BTN_GAP
        board_center = c.GAME_VICTORY_X + c.GAME_VICTORY_WIDTH // 2
        start_x = board_center - total_w // 2
        y_off   = 440 if self.beat_lines else 400
        btn_y   = self.rect.y + y_off
        self._buttons = [
            pg.Rect(start_x + i * (self._BTN_W + self._BTN_GAP),
                    btn_y, self._BTN_W, self._BTN_H)
            for i in range(n)
        ]

    def update(self, surface, current_time, mouse_pos, mouse_click):
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill(self.get_background_color())
        surface.blit(self.image, self.rect)

        real_pos    = pg.mouse.get_pos()
        self._hover = -1
        for i, r in enumerate(self._buttons):
            if r.collidepoint(real_pos):
                self._hover = i
                break

        if mouse_click and mouse_click[0] and self._hover >= 0:
            _, action, *_ = self._BTN_DEFS[self._hover]
            if action == "exit":
                import sys; pg.quit(); sys.exit()
            else:
                self.next = action
                self.done = True

        self._draw_stats(surface)
        self._draw_buttons(surface)

    def _draw_stats(self, surface):
        y = self.rect.y + 248
        for font, text, color, shadow in self.stat_lines:
            r  = font.render(text, True, color)
            sh = font.render(text, True, shadow)
            rx = c.SCREEN_WIDTH // 2 - r.get_width() // 2
            surface.blit(sh, (rx + 2, y + 2))
            surface.blit(r,  (rx,     y))
            y += font.get_linesize() + 10
        for font, text, color, shadow in self.beat_lines:
            r  = font.render(text, True, color)
            sh = font.render(text, True, shadow)
            rx = c.SCREEN_WIDTH // 2 - r.get_width() // 2
            surface.blit(sh, (rx + 2, y + 2))
            surface.blit(r,  (rx,     y))
            y += font.get_linesize() + 6

    def _draw_buttons(self, surface):
        for i, (rect, (label, _, bg_n, bg_h, txt)) in enumerate(
                zip(self._buttons, self._BTN_DEFS)):
            bg = bg_h if i == self._hover else bg_n
            pg.draw.rect(surface, bg,               rect, border_radius=7)
            pg.draw.rect(surface, self._BTN_BORDER,  rect, 2, border_radius=7)
            lbl  = self.font_btn.render(label, True, txt)
            shad = self.font_btn.render(label, True, (0, 0, 0))
            lx   = rect.centerx - lbl.get_width()  // 2
            ly   = rect.centery - lbl.get_height() // 2
            surface.blit(shad, (lx + 1, ly + 1))
            surface.blit(lbl,  (lx,     ly))


# ==========================================
# --- LOSE SCREEN ---
# ==========================================
class GameLoseScreen(Screen):
    _BTN_W      = 118
    _BTN_H      = 38
    _BTN_GAP    = 10
    _BTN_Y_OFF  = 400
    _BTN_BORDER = (180, 140, 50)

    _BTN_DEFS = [
        ("Exit",         "exit",         (130, 35,  35), (175, 55,  55), (255, 255, 255)),
        ("Level Select", c.LEVEL_SELECT, ( 40, 60,  130), ( 60, 90, 180), (255, 255, 255)),
        ("Main Menu",    c.MAIN_MENU,    ( 90, 60,   15), (130, 90,  25), (255, 220, 100)),
        ("Retry Level",  c.LEVEL,        ( 30, 80,  140), ( 45, 115, 190), (255, 255, 255)),
    ]

    def __init__(self):
        Screen.__init__(self)
        self.end_time = 999999
        self._hover   = -1
        self._buttons = []

    def get_image_name(self):       return c.GAME_LOOSE_IMAGE
    def set_next_state(self):       return c.MAIN_MENU
    def get_background_color(self): return c.GAME_LOOSE_BACKGROUND_COLOR

    def setup_background(self):
        self.setup_blurred_background(
            c.LOSE_BACKGROUND, c.GAME_LOOSE_BLUR_SCALE, c.GAME_LOOSE_DIM_ALPHA)

    def setup_image(self, name):
        raw        = engine.GFX[name].convert_alpha()
        self.image = pg.transform.smoothscale(raw, (c.GAME_LOOSE_WIDTH, c.GAME_LOOSE_HEIGHT))
        self.image.set_colorkey(c.BLACK)
        self.rect  = self.image.get_rect(topleft=(c.GAME_LOOSE_X, c.GAME_LOOSE_Y))
        self._setup_content()

    def _setup_content(self):
        pg.font.init()
        try:
            self.font_large = pg.font.Font(c.STATS_FONT_PATH, 30)
            self.font_small = pg.font.Font(c.STATS_FONT_PATH, 22)
            self.font_btn   = pg.font.Font(c.STATS_FONT_PATH, 20)
        except (IOError, AttributeError):
            self.font_large = pg.font.SysFont("arial", 30, bold=True)
            self.font_small = pg.font.SysFont("arial", 22, bold=True)
            self.font_btn   = pg.font.SysFont("arial", 20, bold=True)

        level_num = self.persist.get(c.LEVEL_NUM, 1)
        zombies   = self.persist.get(c.ZOMBIES_KILLED, 0)
        sun       = self.persist.get(c.SUN_COLLECTED,  0)
        plants    = self.persist.get(c.PLANTS_PLANTED, 0)

        self.lose_lines = [
            (self.font_large, f"Level {level_num}  -  The zombies won!", (255,  80,  80), (60, 0, 0)),
            (self.font_small, f"Zombies Defeated:    {zombies}",          (255, 200,  50), (60, 0, 0)),
            (self.font_small, f"Plants Planted:         {plants}",         ( 80, 200,  80), (60, 0, 0)),
            (self.font_small, f"Sun Collected:          {sun}",            (255, 140,   0), (60, 0, 0)),
        ]

        self._build_buttons()

    def _build_buttons(self):
        n            = len(self._BTN_DEFS)
        total_w      = n * self._BTN_W + (n - 1) * self._BTN_GAP
        board_center = c.GAME_LOOSE_X + c.GAME_LOOSE_WIDTH // 2
        start_x      = board_center - total_w // 2
        btn_y        = self.rect.y + self._BTN_Y_OFF
        self._buttons = [
            pg.Rect(start_x + i * (self._BTN_W + self._BTN_GAP),
                    btn_y, self._BTN_W, self._BTN_H)
            for i in range(n)
        ]

    def update(self, surface, current_time, mouse_pos, mouse_click):
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill(self.get_background_color())
        surface.blit(self.image, self.rect)

        real_pos    = pg.mouse.get_pos()
        self._hover = -1
        for i, rect in enumerate(self._buttons):
            if rect.collidepoint(real_pos):
                self._hover = i
                break

        if mouse_click and mouse_click[0] and self._hover >= 0:
            _, action, *_ = self._BTN_DEFS[self._hover]
            if action == "exit":
                import sys; pg.quit(); sys.exit()
            else:
                self.next = action
                self.done = True

        self._draw_lose_text(surface)
        self._draw_buttons(surface)

    def _draw_lose_text(self, surface):
        y        = self.rect.y + 230
        line_gap = 46
        for i, (font, text, color, shadow_color) in enumerate(self.lose_lines):
            rendered = font.render(text, True, color)
            shadow   = font.render(text, True, shadow_color)
            rx       = c.SCREEN_WIDTH // 2 - rendered.get_width() // 2
            ry       = y + i * line_gap
            surface.blit(shadow,   (rx + 2, ry + 2))
            surface.blit(rendered, (rx,     ry))

    def _draw_buttons(self, surface):
        for i, (rect, (label, _, bg_n, bg_h, txt_col)) in enumerate(
                zip(self._buttons, self._BTN_DEFS)):
            bg = bg_h if i == self._hover else bg_n
            pg.draw.rect(surface, bg,               rect, border_radius=8)
            pg.draw.rect(surface, self._BTN_BORDER,  rect, 2, border_radius=8)
            lbl  = self.font_btn.render(label, True, txt_col)
            shad = self.font_btn.render(label, True, (0, 0, 0))
            lx   = rect.centerx - lbl.get_width()  // 2
            ly   = rect.centery - lbl.get_height() // 2
            surface.blit(shad, (lx + 1, ly + 1))
            surface.blit(lbl,  (lx,     ly))


# ==========================================
# --- LOADING SCREEN ---
# ==========================================
class LoadScreen(engine.State):
    def __init__(self):
        engine.State.__init__(self)

    def startup(self, current_time, persist):
        self.start_time       = current_time
        self.persist          = persist
        self.game_info        = persist
        self.is_loaded        = False
        self.loading_duration = 3500
        self.progress         = 0.0
        self.is_hovering      = False

        # Route based on whether profiles exist
        profiles = load_profiles()
        if profiles:
            self.next = c.MAIN_MENU
            self.persist[c.CURRENT_USER] = profiles[0]['name']
            self.persist[c.LEVEL_NUM]    = min(
                profiles[0].get('level', 1), c.MAX_LEVEL)
        else:
            self.next = c.USER_SELECT

        self.setup_images()
        self.setup_text()

    def setup_images(self):
        raw_bg         = engine.GFX['TitleBG']
        self.bg_image  = pg.transform.smoothscale(raw_bg, (c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        self.bg_rect   = self.bg_image.get_rect(topleft=(0, 0))

        self.dirt_image = engine.GFX['LoadBar_dirt']
        self.dirt_rect  = self.dirt_image.get_rect()
        self.dirt_rect.centerx = c.SCREEN_WIDTH // 2
        self.dirt_rect.bottom  = c.SCREEN_HEIGHT - 40

        self.grass_image = engine.GFX['LoadBar_grass']
        self.grass_rect  = self.grass_image.get_rect()
        self.grass_rect.center = self.dirt_rect.center

    def setup_text(self):
        pg.font.init()
        try:
            self.font = pg.font.Font(c.FONT_PATH, 26)
        except (IOError, AttributeError):
            self.font = pg.font.SysFont("papyrus", 26, bold=True)

        white = (255, 255, 255)
        green = (0, 193, 33)

        self.loading_text   = self.font.render("Loading...",     True, white)
        self.loading_shadow = self.font.render("Loading...",     True, c.BLACK)
        self.start_idle     = self.font.render("Click to Start!", True, white)
        self.start_hover    = self.font.render("Click to Start!", True, green)
        self.start_shadow   = self.font.render("Click to Start!", True, c.BLACK)
        self.start_rect     = self.start_idle.get_rect(center=self.dirt_rect.center)
        self.start_rect.y  -= 4

    def update(self, surface, current_time, mouse_pos, mouse_click):
        self.current_time = current_time
        real_pos          = pg.mouse.get_pos()

        if not self.is_loaded:
            elapsed       = current_time - self.start_time
            self.progress = min(elapsed / self.loading_duration, 1.0)
            if self.progress >= 1.0:
                self.is_loaded = True
        else:
            self.is_hovering = self.start_rect.collidepoint(real_pos)
            if self.is_hovering and mouse_click and mouse_click[0]:
                self.done = True

        self.draw(surface)

    def draw(self, surface):
        surface.blit(self.bg_image,   self.bg_rect)
        surface.blit(self.dirt_image, self.dirt_rect)

        current_width = int(self.grass_rect.width * self.progress)
        if current_width > 0:
            surface.blit(self.grass_image, self.grass_rect.topleft,
                         pg.Rect(0, 0, current_width, self.grass_rect.height))

        if not self.is_loaded:
            if (self.current_time // 500) % 2 == 0:
                tr = self.loading_text.get_rect(center=self.dirt_rect.center)
                tr.y -= 4
                surface.blit(self.loading_shadow, (tr.x + 2, tr.y + 2))
                surface.blit(self.loading_text,    tr)
        else:
            surface.blit(self.start_shadow, (self.start_rect.x + 2, self.start_rect.y + 2))
            surface.blit(self.start_hover if self.is_hovering else self.start_idle,
                         self.start_rect)