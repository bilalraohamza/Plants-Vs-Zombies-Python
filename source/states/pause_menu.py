__author__ = 'Rao Hamza Bilal'

import pygame as pg
import sys
from ..core import constants as c
from ..core import engine

class PauseMenu(engine.State):
    def __init__(self):
        engine.State.__init__(self)

    def startup(self, current_time, persist):
        self.game_info = persist
        self.persist = persist
        self.current_time = current_time
        
        # We save the "Level" state so we can draw it in the background
        self.level_surface = self.game_info.get('level_surface') 
        
        self.setup_background()
        self.setup_options()

    def setup_background(self):
        # 1. Create a dark overlay to make the game look "paused"
        self.overlay = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(150) # 0 is clear, 255 is solid black

        # 2. Load the Gravestone Image
        try:
            self.bg_image = engine.GFX[c.PAUSE_MENU_IMAGE]
        except KeyError:
            # Fallback if image isn't named correctly yet
            self.bg_image = pg.Surface((400, 500))
            self.bg_image.fill((100, 100, 100))
            
        self.bg_rect = self.bg_image.get_rect(center=(c.SCREEN_WIDTH//2, c.SCREEN_HEIGHT//2))

    def setup_options(self):
        pg.font.init()
        try:
            self.font = pg.font.Font(c.FONT_PATH, 30)
        except (IOError, AttributeError):
            self.font = pg.font.SysFont("papyrus", 30, bold=True)

        try:
            self.color_normal = c.TEXT_COLOR_NORMAL
            self.color_hover = c.TEXT_COLOR_HOVER
        except AttributeError:
            self.color_normal = (255, 255, 255)
            self.color_hover = (0, 193, 33)

        # --- THE PAUSE MENU BUTTONS ---
        # Adjust the 'pos' Y values to match where the buttons actually are on your Gravestone image
        self.buttons = {
            "RESTART LEVEL": {"pos": (self.bg_rect.centerx, self.bg_rect.y + 340), "action": "restart"},
            "MAIN MENU":     {"pos": (self.bg_rect.centerx, self.bg_rect.y + 390), "action": "main_menu"},
            "BACK TO GAME":  {"pos": (self.bg_rect.centerx, self.bg_rect.y + 450), "action": "resume", "scale": 1.2} # Made Back to Game slightly bigger
        }

        for name, data in self.buttons.items():
            self.update_button(name, data, False)

    def update_button(self, name, data, is_hovering):
        color = self.color_hover if is_hovering else self.color_normal
        base_scale = data.get("scale", 1.0)
        
        # Add 20% pop-up effect if hovering
        final_scale = base_scale * 1.2 if is_hovering else base_scale

        base_image = self.font.render(name, True, color)
        
        if final_scale != 1.0:
            new_w = int(base_image.get_width() * final_scale)
            new_h = int(base_image.get_height() * final_scale)
            data["image"] = pg.transform.smoothscale(base_image, (new_w, new_h))
        else:
            data["image"] = base_image

        data["rect"] = data["image"].get_rect(center=data["pos"])

    def update(self, surface, current_time, mouse_pos, mouse_click):
        self.current_time = current_time
        real_mouse_pos = pg.mouse.get_pos()

        for name, data in self.buttons.items():
            is_hovering = data["rect"].collidepoint(real_mouse_pos)
            self.update_button(name, data, is_hovering)

            if is_hovering and mouse_click[0]:
                self.trigger_action(data["action"])

        self.draw(surface)

    def trigger_action(self, action):
        if action == "resume":
            self.next = c.LEVEL
            self.done = True
        elif action == "main_menu":
            self.next = c.MAIN_MENU
            self.done = True
        elif action == "restart":
            # Resets the level by going back to the level state without advancing c.LEVEL_NUM
            self.next = c.LEVEL
            self.done = True

    def draw(self, surface):
        # 1. Draw the frozen level in the background
        if self.level_surface:
            surface.blit(self.level_surface, (0, 0))
            
        # 2. Draw the dark overlay
        surface.blit(self.overlay, (0, 0))
        
        # 3. Draw the gravestone
        surface.blit(self.bg_image, self.bg_rect)
        
        # 4. Draw the buttons
        for data in self.buttons.values():
            surface.blit(data["image"], data["rect"])

