__author__ = 'Rao Hamza Bilal'

import pygame as pg
from ..core import constants as c
from ..core import engine

# ==========================================
# --- BASE SCREEN CLASS (Used for Win/Loss) ---
# ==========================================
class Screen(engine.State):
    def __init__(self):
        engine.State.__init__(self)
        self.end_time = 3000

    def startup(self, current_time, persist):
        self.start_time = current_time
        self.next = c.LEVEL
        self.persist = persist
        self.game_info = persist
        name = self.get_image_name()
        self.setup_background()
        self.setup_image(name)
        self.next = self.set_next_state()

    def get_image_name(self):
        pass

    def set_next_state(self):
        pass

    def get_background_color(self):
        return c.WHITE

    def setup_background(self):
        self.background_image = None

    def setup_blurred_background(self, key, blur_scale, dim_alpha):
        if key not in self.persist:
            self.background_image = None
            return

        background = self.persist[key]
        small_size = (max(1, c.SCREEN_WIDTH // blur_scale),
                      max(1, c.SCREEN_HEIGHT // blur_scale))
        small_background = pg.transform.smoothscale(background, small_size)
        self.background_image = pg.transform.smoothscale(small_background, c.SCREEN_SIZE)

        dim_surface = pg.Surface(c.SCREEN_SIZE, pg.SRCALPHA)
        dim_surface.fill((0, 0, 0, dim_alpha))
        self.background_image.blit(dim_surface, (0, 0))

    def setup_image(self, name):
        raw_image = engine.GFX[name]
        self.image = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pg.SRCALPHA).convert_alpha()
        self.image.blit(raw_image, (0, 0), (0, 0, c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        self.rect = self.image.get_rect(topleft=(0, 0))

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
    def __init__(self):
        Screen.__init__(self)
        self.end_time = 999999  # stays until player clicks

    def get_image_name(self):
        return c.GAME_VICTORY_IMAGE

    def set_next_state(self):
        return c.LEVEL

    def get_background_color(self):
        return c.GAME_VICTORY_BACKGROUND_COLOR

    def setup_background(self):
        self.setup_blurred_background(
            c.VICTORY_BACKGROUND,
            c.GAME_VICTORY_BLUR_SCALE,
            c.GAME_VICTORY_DIM_ALPHA,
        )

    def setup_image(self, name):
        # convert_alpha + set_colorkey removes the black background from the PNG
        raw_image = engine.GFX[name].convert_alpha()
        self.image = pg.transform.smoothscale(raw_image, (c.GAME_VICTORY_WIDTH, c.GAME_VICTORY_HEIGHT))
        self.image.set_colorkey(c.BLACK)
        self.rect = self.image.get_rect(topleft=(c.GAME_VICTORY_X, c.GAME_VICTORY_Y))
        self.setup_stats_text()

    def setup_stats_text(self):
        pg.font.init()
        try:
            self.font_large = pg.font.Font(c.STATS_FONT_PATH, 32)
            self.font_small = pg.font.Font(c.STATS_FONT_PATH, 22)
        except (IOError, AttributeError):
            self.font_large = pg.font.SysFont("arial", 32, bold=True)
            self.font_small = pg.font.SysFont("arial", 22, bold=True)

        zombies = self.persist.get(c.ZOMBIES_KILLED, 0)
        sun     = self.persist.get(c.SUN_COLLECTED, 0)
        plants  = self.persist.get(c.PLANTS_PLANTED, 0)

        gold   = (255, 200,  50)
        green  = ( 80, 200,  80)
        orange = (255, 140,   0)
        white  = (255, 255, 255)
        shadow = ( 60,  30,   0)

        self.stat_lines = [
            (self.font_large, f"Zombies Defeated:  {zombies}", gold,   shadow),
            (self.font_small, f"Plants Planted:       {plants}",  green,  shadow),
            (self.font_small, f"Sun Collected:        {sun}",     orange, shadow),
            (self.font_small, "Click anywhere to continue!",      white,  shadow),
        ]

    def update(self, surface, current_time, mouse_pos, mouse_click):
        # Draw blurred game screenshot behind the board
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill(self.get_background_color())

        # Draw the victory board PNG (no black)
        surface.blit(self.image, self.rect)

        # Draw stats inside the parchment area
        self.draw_stats(surface)

        # Click anywhere to proceed
        if mouse_click and mouse_click[0]:
            self.done = True

    def draw_stats(self, surface):
        # start_y positions text inside the parchment (lower half of the board image)
        start_y = self.rect.y + 250
        line_gap = 45

        for i, (font, text, color, shadow_color) in enumerate(self.stat_lines):
            rendered = font.render(text, True, color)
            shadow   = font.render(text, True, shadow_color)
            rx = c.SCREEN_WIDTH // 2 - rendered.get_width() // 2
            ry = start_y + i * line_gap
            # Draw shadow offset by 2px for depth
            surface.blit(shadow,   (rx + 2, ry + 2))
            surface.blit(rendered, (rx, ry))


# ==========================================
# --- LOSE SCREEN ---
# ==========================================
class GameLoseScreen(Screen):
    def __init__(self):
        Screen.__init__(self)
        self.end_time = 999999  # stays until player clicks

    def get_image_name(self):
        return c.GAME_LOOSE_IMAGE

    def set_next_state(self):
        return c.MAIN_MENU

    def get_background_color(self):
        return c.GAME_LOOSE_BACKGROUND_COLOR

    def setup_background(self):
        self.setup_blurred_background(
            c.LOSE_BACKGROUND,
            c.GAME_LOOSE_BLUR_SCALE,
            c.GAME_LOOSE_DIM_ALPHA,
        )

    def setup_image(self, name):
        # convert_alpha + set_colorkey removes the black background from the PNG
        raw_image = engine.GFX[name].convert_alpha()
        self.image = pg.transform.smoothscale(raw_image, (c.GAME_LOOSE_WIDTH, c.GAME_LOOSE_HEIGHT))
        self.image.set_colorkey(c.BLACK)
        self.rect = self.image.get_rect(topleft=(c.GAME_LOOSE_X, c.GAME_LOOSE_Y))
        self.setup_lose_text()

    def setup_lose_text(self):
        pg.font.init()
        try:
            self.font = pg.font.Font(c.STATS_FONT_PATH, 26)
        except (IOError, AttributeError):
            self.font = pg.font.SysFont("arial", 26, bold=True)

        self.lose_lines = [
            "The zombies ate your brains!",
            "Click anywhere to try again...",
        ]

    def update(self, surface, current_time, mouse_pos, mouse_click):
        # Draw blurred game screenshot behind the board
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill(self.get_background_color())

        # Draw the lose board PNG (no black)
        surface.blit(self.image, self.rect)

        # Draw lose text
        self.draw_lose_text(surface)

        # Click anywhere to go back to main menu
        if mouse_click and mouse_click[0]:
            self.done = True

    def draw_lose_text(self, surface):
        start_y = self.rect.y + 300
        colors = [(255, 80, 80), (255, 255, 255)]
        shadow_color = (60, 0, 0)

        for i, text in enumerate(self.lose_lines):
            rendered = self.font.render(text, True, colors[i])
            shadow   = self.font.render(text, True, shadow_color)
            rx = c.SCREEN_WIDTH // 2 - rendered.get_width() // 2
            ry = start_y + i * 45
            surface.blit(shadow,   (rx + 2, ry + 2))
            surface.blit(rendered, (rx, ry))


# ==========================================
# --- PHOTOREALISTIC LOADING SCREEN ---
# ==========================================
class LoadScreen(engine.State):
    def __init__(self):
        engine.State.__init__(self)

    def startup(self, current_time, persist):
        self.start_time = current_time
        self.next = c.USER_SELECT
        self.persist = persist
        self.game_info = persist

        self.is_loaded = False
        self.loading_duration = 3500
        self.progress = 0.0
        self.is_hovering = False

        self.setup_images()
        self.setup_text()

    def setup_images(self):
        raw_bg = engine.GFX['TitleBG']
        self.bg_image = pg.transform.smoothscale(raw_bg, (c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        self.bg_rect = self.bg_image.get_rect(topleft=(0, 0))

        self.dirt_image = engine.GFX['LoadBar_dirt']
        self.dirt_rect = self.dirt_image.get_rect()
        self.dirt_rect.centerx = c.SCREEN_WIDTH // 2
        self.dirt_rect.bottom = c.SCREEN_HEIGHT - 40

        self.grass_image = engine.GFX['LoadBar_grass']
        self.grass_rect = self.grass_image.get_rect()
        self.grass_rect.center = self.dirt_rect.center

    def setup_text(self):
        pg.font.init()

        try:
            self.font = pg.font.Font(c.FONT_PATH, 26)
        except (IOError, AttributeError):
            self.font = pg.font.SysFont("papyrus", 26, bold=True)

        color_white = (255, 255, 255)
        color_green = (0, 193, 33)

        self.loading_text   = self.font.render("Loading...",    True, color_white)
        self.loading_shadow = self.font.render("Loading...",    True, c.BLACK)

        self.start_text_idle  = self.font.render("Click to Start!", True, color_white)
        self.start_text_hover = self.font.render("Click to Start!", True, color_green)
        self.start_shadow     = self.font.render("Click to Start!", True, c.BLACK)

        self.start_rect = self.start_text_idle.get_rect(center=self.dirt_rect.center)
        self.start_rect.y -= 4

    def update(self, surface, current_time, mouse_pos, mouse_click):
        self.current_time = current_time

        real_mouse_pos = pg.mouse.get_pos()

        if not self.is_loaded:
            elapsed = self.current_time - self.start_time
            self.progress = elapsed / self.loading_duration

            if self.progress >= 1.0:
                self.progress = 1.0
                self.is_loaded = True
        else:
            if self.start_rect.collidepoint(real_mouse_pos):
                self.is_hovering = True
                if mouse_click[0]:
                    self.done = True
            else:
                self.is_hovering = False

        self.draw(surface)

    def draw(self, surface):
        surface.blit(self.bg_image, self.bg_rect)
        surface.blit(self.dirt_image, self.dirt_rect)

        current_width = int(self.grass_rect.width * self.progress)
        if current_width > 0:
            crop_rect = pg.Rect(0, 0, current_width, self.grass_rect.height)
            surface.blit(self.grass_image, self.grass_rect.topleft, crop_rect)

        if not self.is_loaded:
            if (self.current_time // 500) % 2 == 0:
                text_rect = self.loading_text.get_rect(center=self.dirt_rect.center)
                text_rect.y -= 4
                surface.blit(self.loading_shadow, (text_rect.x + 2, text_rect.y + 2))
                surface.blit(self.loading_text, text_rect)
        else:
            surface.blit(self.start_shadow, (self.start_rect.x + 2, self.start_rect.y + 2))
            if self.is_hovering:
                surface.blit(self.start_text_hover, self.start_rect)
            else:
                surface.blit(self.start_text_idle, self.start_rect)