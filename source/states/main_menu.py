__author__ = 'Rao Hamza Bilal'

import pygame as pg
import sys
from ..core import constants as c
from ..core import engine

class Menu(engine.State):
    def __init__(self):
        engine.State.__init__(self)
    
    def startup(self, current_time, persist):
        self.next = c.LEVEL
        self.persist = persist
        self.game_info = persist
        
        self.setup_background()
        self.setup_options()

    def setup_background(self):
        # Grab the background surface
        bg_surface = engine.GFX[c.MAIN_MENU_IMAGE]
        
        # Locked in to 800x600 so it fits your game window perfectly
        self.bg_image = pg.transform.smoothscale(bg_surface, (800, 600))
        self.bg_rect = self.bg_image.get_rect()
        self.bg_rect.x = 0
        self.bg_rect.y = 0
        
    def setup_options(self):
        pg.font.init()
        
        # --- LOAD CUSTOM FONT ---
        try:
            # Tries to load your custom downloaded font file from constants
            self.font_main = pg.font.Font(c.FONT_PATH, 25)
            self.font_small = pg.font.Font(c.FONT_PATH, 20)
        except (IOError, AttributeError):
            # Fallback just in case the folder path is slightly wrong or missing in constants
            self.font_main = pg.font.SysFont("papyrus", 30, bold=True)
            self.font_small = pg.font.SysFont("papyrus", 20, bold=True)

        self.font_large = pg.font.Font(c.FONT_PATH, 36)
        self.font_medium = pg.font.Font(c.FONT_PATH, 26)
        self.font_small = pg.font.Font(c.FONT_PATH, 20)

        # --- THE BUTTON DICTIONARY ---
        # Your custom scales and positions are strictly preserved!
        self.buttons = {
            "ADVENTURE":  {"type": "text", "font": self.font_large,  "pos": (400, 205), "action": "start_game"},
            "MINI GAMES": {"type": "text", "font": self.font_medium,  "pos": (400, 310), "action": "none"},
            "PUZZLE":     {"type": "text", "font": self.font_medium, "pos": (400, 380), "action": "none"},
            "SURVIVAL":   {"type": "text", "font": self.font_medium, "pos": (400, 445), "action": "none"},
            "OPTIONS":    {"type": "text", "font": self.font_small,  "pos": (705, 500), "action": "none"},
            "EXIT":       {"type": "text", "font": self.font_small,  "pos": (120, 485), "action": "exit_game"}
        }

        # Setup the initial look for each button
        for name, data in self.buttons.items():
            self.update_button(name, data, "idle")
            data["clicked"] = False
            data["start_time"] = 0
            
        self.active_click = None
        
    def update_button(self, name, data, state):
        """Helper function to cleanly render, rotate, scale, and center images OR text."""
        
        # 1. Handle TEXT buttons (With Pop-Up Effect & Papyrus Font)
        if data.get("type", "text") == "text":
            if state in ["hover", "click"]:
                try:
                    color = c.TEXT_COLOR_HOVER
                except AttributeError:
                    color = (0, 193, 33) # Fallback Zombie Green
                text_scale = 1.2 # Makes the text 20% bigger when hovered!
            else:
                try:
                    color = c.TEXT_COLOR_NORMAL
                except AttributeError:
                    color = (255, 255, 255) # Fallback Pure White
                text_scale = 1.0 # Normal size
                
            base_image = data["font"].render(name, True, color)
            
            # Apply the "Pop Up" stretch to the text
            if text_scale != 1.0:
                new_width = int(base_image.get_width() * text_scale)
                new_height = int(base_image.get_height() * text_scale)
                base_image = pg.transform.smoothscale(base_image, (new_width, new_height))
                
        # 2. Handle IMAGE buttons (Your custom scaling logic preserved perfectly)
        else:
            img_key = data["hover_img"] if state in ["hover", "click"] else data["idle_img"]
            try:
                raw_image = engine.GFX[img_key]
                
                # --- APPLY DYNAMIC SCALING ---
                scale_factor = data.get("scale", 1.0)
                if scale_factor != 1.0:
                    new_width = int(raw_image.get_width() * scale_factor)
                    new_height = int(raw_image.get_height() * scale_factor)
                    base_image = pg.transform.smoothscale(raw_image, (new_width, new_height))
                else:
                    base_image = raw_image
                    
            except KeyError:
                # Fallback red box just in case there is a typo in the filename
                base_image = pg.Surface((150, 40))
                base_image.fill((255, 0, 0))

        # 3. Spin it if this button has an "angle" setting
        if "angle" in data:
            data["image"] = pg.transform.rotate(base_image, data["angle"])
        else:
            data["image"] = base_image
            
        # 4. Always recalculate the exact center so the hover effect doesn't wobble
        data["rect"] = data["image"].get_rect(center=data["pos"])
    
    def check_option_click(self, mouse_pos):
        for name, data in self.buttons.items():
            if data["rect"].collidepoint(mouse_pos):
                data["clicked"] = True
                data["start_time"] = self.current_time
                self.active_click = name
                return True
        return False
        
    def update(self, surface, current_time, mouse_pos, mouse_click):
        self.current_time = self.game_info[c.CURRENT_TIME] = current_time
        real_mouse_pos = pg.mouse.get_pos()
        
        # Handle Hover & Click Logic for all buttons
        for name, data in self.buttons.items():
            if not data["clicked"]:
                # Hover effect
                if self.active_click is None and data["rect"].collidepoint(real_mouse_pos):
                    self.update_button(name, data, "hover")
                else:
                    self.update_button(name, data, "idle")
            else:
                # Click flash animation
                elapsed = self.current_time - data["start_time"]
                if (elapsed // 150) % 2 == 0:
                    self.update_button(name, data, "click")
                else:
                    self.update_button(name, data, "idle")
                    
                # Action trigger after the flashing animation finishes
                if elapsed > 1000:
                    self.trigger_action(data["action"])

        # Check for new clicks only if no button is currently animating
        if self.active_click is None and mouse_pos:
            self.check_option_click(mouse_pos)

        # Draw background and all buttons
        surface.blit(self.bg_image, self.bg_rect)
        for data in self.buttons.values():
            surface.blit(data["image"], data["rect"])

    def trigger_action(self, action):
        """Routes the game to the correct place based on what was clicked"""
        if action == "start_game":
            self.done = True 
        elif action == "exit_game":
            pg.quit()
            sys.exit() 
        else:
            self.active_click = None
            for data in self.buttons.values():
                data["clicked"] = False

