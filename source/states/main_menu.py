__author__ = 'Rao Hamza Bilal'

import random
import pygame as pg
import sys
from ..core import constants as c
from ..core import engine


class Menu(engine.State):
    def __init__(self):
        engine.State.__init__(self)

    def startup(self, current_time, persist):
        self.next          = c.LEVEL_SELECT
        self.persist       = persist
        self.game_info     = persist
        self.current_user  = persist.get(c.CURRENT_USER, 'Stranger')

        self.setup_background()
        self.setup_options()

    def setup_background(self):
        bg_surface = engine.GFX[c.MAIN_MENU_IMAGE]
        self.bg_image = pg.transform.smoothscale(bg_surface, (800, 600))
        self.bg_rect  = self.bg_image.get_rect()

    def setup_options(self):
        pg.font.init()
        try:
            self.font_large  = pg.font.Font(c.FONT_PATH, 36)
            self.font_medium = pg.font.Font(c.FONT_PATH, 26)
            self.font_small  = pg.font.Font(c.FONT_PATH, 20)
            self.font_msg    = pg.font.Font(c.FONT_PATH, 18)
        except (IOError, AttributeError):
            self.font_large  = pg.font.SysFont('papyrus', 36, bold=True)
            self.font_medium = pg.font.SysFont('papyrus', 26, bold=True)
            self.font_small  = pg.font.SysFont('papyrus', 20, bold=True)
            self.font_msg    = pg.font.SysFont('papyrus', 18, bold=True)

        self.buttons = {
            'ADVENTURE':   {'type': 'text', 'font': self.font_medium, 'pos': (400, 310), 'action': 'start_game'},
            'SURVIVAL':    {'type': 'text', 'font': self.font_medium, 'pos': (400, 380), 'action': 'survival'},
            'LEADERBOARD': {'type': 'text', 'font': self.font_medium, 'pos': (400, 445), 'action': 'leaderboard'},
            'SETTINGS':    {'type': 'text', 'font': self.font_small,  'pos': (705, 500), 'action': 'settings'},
            'EXIT':        {'type': 'text', 'font': self.font_small,  'pos': (120, 485), 'action': 'exit_game'},
        }

        for name, data in self.buttons.items():
            self.update_button(name, data, 'idle')
            data['clicked']    = False
            data['start_time'] = 0

        self.active_click = None

    def update_button(self, name, data, state):
        if data.get('type', 'text') == 'text':
            if state in ('hover', 'click'):
                color      = getattr(c, 'TEXT_COLOR_HOVER', (0, 193, 33))
                text_scale = 1.2
            else:
                color      = getattr(c, 'TEXT_COLOR_NORMAL', (255, 255, 255))
                text_scale = 1.0

            base_image = data['font'].render(name, True, color)
            if text_scale != 1.0:
                nw = int(base_image.get_width()  * text_scale)
                nh = int(base_image.get_height() * text_scale)
                base_image = pg.transform.smoothscale(base_image, (nw, nh))
        else:
            img_key = data['hover_img'] if state in ('hover', 'click') else data['idle_img']
            try:
                raw        = engine.GFX[img_key]
                sf         = data.get('scale', 1.0)
                base_image = pg.transform.smoothscale(
                    raw, (int(raw.get_width() * sf), int(raw.get_height() * sf))
                ) if sf != 1.0 else raw
            except KeyError:
                base_image = pg.Surface((150, 40))
                base_image.fill((255, 0, 0))

        data['image'] = pg.transform.rotate(base_image, data['angle']) \
                        if 'angle' in data else base_image
        data['rect']  = data['image'].get_rect(center=data['pos'])

    def check_option_click(self, mouse_pos):
        for name, data in self.buttons.items():
            if data['rect'].collidepoint(mouse_pos):
                data['clicked']    = True
                data['start_time'] = self.current_time
                self.active_click  = name
                return True
        return False

    def draw_user_message(self, surface):
        name = self.current_user
        messages = [
            ("The zombies already know", f"where you live, {name}!"),
            ("Your brains smell extra", f"tasty today, {name}!"),
            ("The lawn is counting", f"on you, {name}!"),
            ("Welcome back!", f"The zombies missed you, {name}."),
            (f"{name}, your Sunflowers", "are getting nervous!"),
            ("Don't let them eat", f"your brain, {name}!"),
            (f"{name}, the zombies filed", "a complaint. Plant faster!"),
            (f"Ah {name}, the zombies", "have been practicing. Have you?"),
            (f"{name}, even the Peashooter", "believes in you. Barely."),
        ]
        random.seed(hash(name) % 9999)
        line1, line2 = random.choice(messages)
        try:
            font = pg.font.Font(c.STATS_FONT_PATH, 20)
        except Exception:
            font = pg.font.SysFont('arial', 20, bold=True)
        for i, line in enumerate([line1, line2]):
            shadow = font.render(line, True, (0, 0, 0))
            text = font.render(line, True, (255, 255, 255))
            rx = 400 - text.get_width() // 2
            ry = 180 + i * 28
            surface.blit(shadow, (rx + 2, ry + 2))
            surface.blit(text,   (rx,     ry))

    def update(self, surface, current_time, mouse_pos, mouse_click):
        self.current_time = self.game_info[c.CURRENT_TIME] = current_time
        real_mouse_pos    = pg.mouse.get_pos()

        for name, data in self.buttons.items():
            if not data['clicked']:
                state = 'hover' if (self.active_click is None and
                                    data['rect'].collidepoint(real_mouse_pos)) else 'idle'
                self.update_button(name, data, state)
            else:
                elapsed = self.current_time - data['start_time']
                self.update_button(name, data,
                                   'click' if (elapsed // 150) % 2 == 0 else 'idle')
                if elapsed > 1000:
                    self.trigger_action(data['action'])

        if self.active_click is None and mouse_pos:
            self.check_option_click(mouse_pos)

        surface.blit(self.bg_image, self.bg_rect)
        self.draw_user_message(surface)
        for data in self.buttons.values():
            surface.blit(data['image'], data['rect'])

    def trigger_action(self, action):
        if action == 'start_game':
            self.next = c.LEVEL_SELECT
            self.done = True
        elif action == 'survival':
            self.next = c.SURVIVAL
            self.done = True
        elif action == 'leaderboard':
            self.persist[c.LEADERBOARD_ORIGIN] = c.MAIN_MENU
            self.next = c.LEADERBOARD
            self.done = True
        elif action == 'settings':
            self.next = c.SETTINGS
            self.done = True
        elif action == 'exit_game':
            pg.quit()
            sys.exit()
        else:
            self.active_click = None
            for data in self.buttons.values():
                data['clicked'] = False