__author__ = 'Rao Hamza Bilal'

import random
import pygame as pg
from ..core import constants as c
from ..core import engine

# ==========================================
# --- UI ALIGNMENT ZONE ---
# ==========================================

# 1. STRETCH THE TOP MENU BAR
# Your original image is 446 wide. We stretch it to 500 to fit 8 cards comfortably.
MENU_BAR_WIDTH = 500 
#MENU_BAR_HEIGHT = 60

# 2. THE BOTTOM PANEL POSITION 
PANEL_Y_START = 86 

# 3. TOP MENU BAR CARDS (The Chosen Plants)
TOP_BAR_CARD_Y = 8          
TOP_BAR_CARD_X_START = 87   # Safely clears the Sun counter
TOP_BAR_CARD_SPACING = 50   # Increased spacing so cards DO NOT overlap!

# 4. BOTTOM PANEL INVENTORY CARDS (The Seed Pockets)
PANEL_CARD_X_START = 25     
PANEL_CARD_Y_START = 45     
PANEL_CARD_X_SPACING = 52   
PANEL_CARD_Y_SPACING = 72   

CARD_LIST_NUM = 8

# --- PLANT DATA LISTS ---
card_name_list = [c.CARD_SUNFLOWER, c.CARD_PEASHOOTER, c.CARD_SNOWPEASHOOTER, c.CARD_WALLNUT,
                  c.CARD_CHERRYBOMB, c.CARD_THREEPEASHOOTER, c.CARD_REPEATERPEA, c.CARD_CHOMPER,
                  c.CARD_PUFFSHROOM, c.CARD_POTATOMINE, c.CARD_SQUASH, c.CARD_SPIKEWEED,
                  c.CARD_JALAPENO, c.CARD_SCAREDYSHROOM, c.CARD_SUNSHROOM, c.CARD_ICESHROOM,
                  c.CARD_HYPNOSHROOM, c.CARD_WALLNUT, c.CARD_REDWALLNUT]

plant_name_list = [c.SUNFLOWER, c.PEASHOOTER, c.SNOWPEASHOOTER, c.WALLNUT,
                   c.CHERRYBOMB, c.THREEPEASHOOTER, c.REPEATERPEA, c.CHOMPER,
                   c.PUFFSHROOM, c.POTATOMINE, c.SQUASH, c.SPIKEWEED,
                   c.JALAPENO, c.SCAREDYSHROOM, c.SUNSHROOM, c.ICESHROOM,
                   c.HYPNOSHROOM, c.WALLNUTBOWLING, c.REDWALLNUTBOWLING]

plant_sun_list = [50, 100, 175, 50, 150, 325, 200, 150, 0, 25, 50, 100, 125, 25, 25, 75, 75, 0, 0]

plant_frozen_time_list = [7500, 7500, 7500, 30000, 50000, 7500, 7500, 7500, 7500, 30000,
                          30000, 7500, 50000, 7500, 7500, 50000, 30000, 0, 0]

all_card_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]


def get_card_pool(card_pool):
    return list(card_pool)


def get_sun_value_image(sun_value):
    font = pg.font.SysFont(None, 22)
    width = 32
    msg_image = font.render(str(sun_value), True, c.NAVYBLUE, c.LIGHTYELLOW)
    msg_rect = msg_image.get_rect()
    msg_w = msg_rect.width

    image = pg.Surface([width, 17]).convert()
    x = width - msg_w

    image.fill(c.LIGHTYELLOW)
    image.blit(msg_image, (x, 0), (0, 0, msg_rect.w, msg_rect.h))
    image.set_colorkey(c.BLACK)
    return image


class Card():
    def __init__(self, x, y, name_index, scale=0.78):
        self.load_frame(card_name_list[name_index], scale)
        self.rect = self.orig_image.get_rect(topleft=(x, y))
        
        self.name_index = name_index
        self.sun_cost = plant_sun_list[name_index]
        self.frozen_time = plant_frozen_time_list[name_index]
        self.frozen_timer = -self.frozen_time
        self.refresh_timer = 0
        self.select = True

    def load_frame(self, name, scale):
        frame = engine.GFX[name]
        rect = frame.get_rect()
        self.orig_image = engine.get_image(frame, 0, 0, rect.w, rect.h, c.BLACK, scale)
        self.image = self.orig_image

    def check_mouse_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def can_click(self, sun_value, current_time):
        return self.sun_cost <= sun_value and (current_time - self.frozen_timer) > self.frozen_time

    def can_select(self):
        return self.select

    def set_select(self, can_select):
        self.select = can_select
        self.image.set_alpha(255 if can_select else 128)

    def set_frozen_time(self, current_time):
        self.frozen_timer = current_time

    def create_show_image(self, sun_value, current_time):
        time = current_time - self.frozen_timer
        if time < self.frozen_time: 
            image = pg.Surface([self.rect.w, self.rect.h], pg.SRCALPHA).convert_alpha()
            frozen_image = self.orig_image.copy()
            frozen_image.set_alpha(128)
            frozen_height = (self.frozen_time - time) / self.frozen_time * self.rect.h
            
            image.blit(frozen_image, (0, 0), (0, 0, self.rect.w, frozen_height))
            image.blit(self.orig_image, (0, frozen_height),
                       (0, frozen_height, self.rect.w, self.rect.h - frozen_height))
        elif self.sun_cost > sun_value: 
            image = self.orig_image.copy()
            image.set_alpha(192)
        else:
            image = self.orig_image
        return image

    def update(self, sun_value, current_time):
        if (current_time - self.refresh_timer) >= 250:
            self.image = self.create_show_image(sun_value, current_time)
            self.refresh_timer = current_time

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class MenuBar():
    def __init__(self, card_list, sun_value):
        self.load_frame(c.MENUBAR_BACKGROUND)
        self.rect = self.image.get_rect(topleft=(10, 0))
        self.sun_value = sun_value
        self.setup_cards(card_list)

    def load_frame(self, name):
        frame = engine.GFX[name]
        rect = frame.get_rect()
        image = pg.Surface((rect.w, rect.h), pg.SRCALPHA)
        image.blit(frame, (0, 0), rect)
        self.image = pg.transform.scale(image, (500, 86))
        return self.image

    def update(self, current_time):
        self.current_time = current_time
        for card in self.card_list:
            card.update(self.sun_value, self.current_time)

    def setup_cards(self, card_list):
        self.card_list = []
        x = TOP_BAR_CARD_X_START
        y = TOP_BAR_CARD_Y
        for index in card_list:
            self.card_list.append(Card(x, y, index))
            x += TOP_BAR_CARD_SPACING

    def check_card_click(self, mouse_pos):
        for card in self.card_list:
            if card.check_mouse_click(mouse_pos) and card.can_click(self.sun_value, self.current_time):
                return (plant_name_list[card.name_index], card)
        return None
    
    def check_menu_bar_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def decrease_sun_value(self, value):
        self.sun_value -= value

    def increase_sun_value(self, value):
        self.sun_value += value

    def set_card_frozen_time(self, plant_name):
        for card in self.card_list:
            if plant_name_list[card.name_index] == plant_name:
                card.set_frozen_time(self.current_time)
                break

    def draw_sun_value(self):
        self.value_image = get_sun_value_image(self.sun_value)
        self.value_rect = self.value_image.get_rect(topleft=(21, self.rect.bottom - 21))
        self.image.blit(self.value_image, self.value_rect)

    def draw(self, surface):
        self.draw_sun_value()
        surface.blit(self.image, self.rect)
        for card in self.card_list:
            card.draw(surface)


class Panel():
    def __init__(self, card_list, sun_value):
        self.load_images(sun_value)
        self.selected_cards = []
        self.selected_num = 0
        self.setup_cards(card_list)
        self.is_hovering_start = False 

    def load_frame(self, name):
        frame = engine.GFX[name]
        rect = frame.get_rect()
        image = pg.Surface((rect.w, rect.h), pg.SRCALPHA).convert_alpha()
        image.blit(frame, (0, 0), rect)
        return image

    def load_images(self, sun_value):
        raw_menu_image = self.load_frame(c.MENUBAR_BACKGROUND)
        
        # CHANGED: Using regular scale instead of smoothscale removes the black artifact edge!
        self.menu_image = pg.transform.scale(raw_menu_image, (500, 86))
        self.menu_rect = self.menu_image.get_rect(topleft=(0, 0))

        self.panel_image = self.load_frame(c.PANEL_BACKGROUND)
        self.panel_image = pg.transform.scale(self.panel_image, (465, 513))
        self.panel_rect = self.panel_image.get_rect(topleft=(10, PANEL_Y_START))
        
        self.value_image = get_sun_value_image(sun_value)
        self.value_rect = self.value_image.get_rect(topleft=(21, self.menu_rect.bottom - 21))

        # --- UPDATED BUTTON LOGIC ---
        try:
            self.button_image = self.load_frame('SeedChooser_Button')
            self.button_disabled_image = self.load_frame('SeedChooser_Button_Disabled')
        except KeyError:
            self.button_image = self.load_frame(c.START_BUTTON)
            self.button_disabled_image = self.button_image.copy()
            self.button_disabled_image.set_alpha(128)

        self.button_hover_image = self.button_image.copy()

        # Load Simple Font
        pg.font.init()
        font = pg.font.SysFont("arial", 22, bold=True)
        
        # Define the exact colors requested
        color_white = (255, 255, 255)
        color_green = (0, 193, 33) 
        color_gray = (160, 160, 160) 
        
        # Render the text
        text_idle = font.render("LET'S ROCK!", True, color_white)
        text_hover = font.render("LET'S ROCK!", True, color_green)
        text_disabled = font.render("LET'S ROCK!", True, color_gray)
        
        # Center the text perfectly inside the buttons
        rect_idle = text_idle.get_rect(center=(self.button_image.get_width() // 2, self.button_image.get_height() // 2))
        rect_hover = text_hover.get_rect(center=(self.button_hover_image.get_width() // 2, self.button_hover_image.get_height() // 2))
        rect_disabled = text_disabled.get_rect(center=(self.button_disabled_image.get_width() // 2, self.button_disabled_image.get_height() // 2))
        
        # Blit the text to the respective button surfaces
        self.button_image.blit(text_idle, rect_idle)
        self.button_hover_image.blit(text_hover, rect_hover)
        self.button_disabled_image.blit(text_disabled, rect_disabled)

        # Place the button at exactly 155, 547
        self.button_rect = self.button_image.get_rect(topleft=(155, 547))

    def setup_cards(self, card_list):
        self.card_list = []
        x = PANEL_CARD_X_START - PANEL_CARD_X_SPACING
        y = PANEL_Y_START + PANEL_CARD_Y_START - PANEL_CARD_Y_SPACING
        for i, index in enumerate(card_list):
            if i % 8 == 0:
                x = PANEL_CARD_X_START - PANEL_CARD_X_SPACING
                y += PANEL_CARD_Y_SPACING
            x += PANEL_CARD_X_SPACING
            self.card_list.append(Card(x, y, index, 0.75))

    def update(self, mouse_pos):
        current_mouse_pos = mouse_pos if mouse_pos else pg.mouse.get_pos()
        self.is_hovering_start = self.button_rect.collidepoint(current_mouse_pos)

    def check_card_click(self, mouse_pos):
        delete_card = None
        for card in self.selected_cards:
            if delete_card: 
                card.rect.x -= TOP_BAR_CARD_SPACING
            elif card.check_mouse_click(mouse_pos):
                self.delete_card(card.name_index)
                delete_card = card

        if delete_card:
            self.selected_cards.remove(delete_card)
            self.selected_num -= 1

        if self.selected_num == CARD_LIST_NUM:
            return

        for card in self.card_list:
            if card.check_mouse_click(mouse_pos) and card.can_select():
                self.add_card(card)
                break

    def add_card(self, card):
        card.set_select(False)
        y = TOP_BAR_CARD_Y
        x = TOP_BAR_CARD_X_START + (self.selected_num * TOP_BAR_CARD_SPACING)
        self.selected_cards.append(Card(x, y, card.name_index))
        self.selected_num += 1

    def delete_card(self, index):
        self.card_list[index].set_select(True)

    def check_start_button_click(self, mouse_pos):
        if self.selected_num < CARD_LIST_NUM:
            return False
        return self.button_rect.collidepoint(mouse_pos)

    def get_selected_cards(self):
        return [card.name_index for card in self.selected_cards]

    def draw(self, surface):
        self.menu_image.blit(self.value_image, self.value_rect)
        surface.blit(self.menu_image, self.menu_rect)
        surface.blit(self.panel_image, self.panel_rect)
        
        for card in self.card_list:
            card.draw(surface)
        for card in self.selected_cards:
            card.draw(surface)

        # --- UPDATED BUTTON DRAW LOGIC ---
        if self.selected_num == CARD_LIST_NUM:
            if self.is_hovering_start:
                surface.blit(self.button_hover_image, self.button_rect)
            else:
                surface.blit(self.button_image, self.button_rect)
        else:
            surface.blit(self.button_disabled_image, self.button_rect)


# ==========================================
# --- CONVEYOR BELT CLASSES (MOVE BAR) ---
# ==========================================
class MoveCard():
    def __init__(self, x, y, card_name, plant_name, scale=0.78):
        self.load_frame(card_name, scale)
        self.rect = self.orig_image.get_rect(topleft=(x, y))
        self.rect.w = 1
        self.image = self.create_show_image()

        self.card_name = card_name
        self.plant_name = plant_name
        self.move_timer = 0
        self.select = True

    def load_frame(self, name, scale):
        frame = engine.GFX[name]
        rect = frame.get_rect()
        self.orig_image = engine.get_image(frame, 0, 0, rect.w, rect.h, c.BLACK, scale)
        self.orig_rect = self.orig_image.get_rect()
        self.image = self.orig_image

    def check_mouse_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def create_show_image(self):
        if self.rect.w < self.orig_rect.w:
            image = pg.Surface([self.rect.w, self.rect.h]).convert()
            image.blit(self.orig_image, (0, 0), (0, 0, self.rect.w, self.rect.h))
            self.rect.w += 1
        else:
            image = self.orig_image
        return image

    def update(self, left_x, current_time):
        if self.move_timer == 0:
            self.move_timer = current_time
        elif (current_time - self.move_timer) >= c.CARD_MOVE_TIME:
            if self.rect.x > left_x:
                self.rect.x -= 1
                self.image = self.create_show_image()
            self.move_timer += c.CARD_MOVE_TIME

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class MoveBar():
    def __init__(self, card_pool):
        self.load_frame(c.MOVEBAR_BACKGROUND)
        self.rect = self.image.get_rect(topleft=(90, 0))
        
        self.card_start_x = self.rect.x + 8
        self.card_end_x = self.rect.right - 5
        self.card_pool = card_pool
        self.card_list = []
        self.create_timer = -c.MOVEBAR_CARD_FRESH_TIME

    def load_frame(self, name):
        frame = engine.GFX[name]
        rect = frame.get_rect()
        self.image = engine.get_image(frame, rect.x, rect.y, rect.w, rect.h, c.WHITE, 1)

    def create_card(self):
        if len(self.card_list) > 0 and self.card_list[-1].rect.right > self.card_end_x:
            return False
        x = self.card_end_x
        y = 6
        index = random.randint(0, len(self.card_pool) - 1)
        card_index = self.card_pool[index]
        card_name = card_name_list[card_index] + '_move'
        plant_name = plant_name_list[card_index]
        
        self.card_list.append(MoveCard(x, y, card_name, plant_name))
        return True

    def update(self, current_time):
        self.current_time = current_time
        left_x = self.card_start_x
        for card in self.card_list:
            card.update(left_x, self.current_time)
            left_x = card.rect.right + 1

        if (self.current_time - self.create_timer) > c.MOVEBAR_CARD_FRESH_TIME:
            if self.create_card():
                self.create_timer = self.current_time

    def check_card_click(self, mouse_pos):
        for card in self.card_list:
            if card.check_mouse_click(mouse_pos):
                return (card.plant_name, card)
        return None
    
    def check_menu_bar_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def delete_card(self, card):
        self.card_list.remove(card)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        for card in self.card_list:
            card.draw(surface)


# ============================================================
# SHOVEL TOOL
# ============================================================

class ShovelTool:
    """
    Displays a ShovelBank on the menu bar.
    Click the bank/shovel to toggle shovel mode on/off.
    When active the shovel PNG follows the cursor.
    Clicking a plant while active removes it (no sun refund).
    Right-click always cancels.
    """

    # Position: just to the right of the MenuBar (x=510, bar height=86)
    BANK_X   = 512
    BANK_Y   = 4
    BANK_W   = 72
    BANK_H   = 78

    # Shovel cursor size when dragging
    SHOVEL_W = 52
    SHOVEL_H = 52

    def __init__(self):
        self.active = False   # True = shovel mode on

        # --- Shovel bank background ---
        try:
            raw_bank = engine.GFX[c.SHOVEL_BANK]
            self.bank_image = pg.transform.smoothscale(raw_bank, (self.BANK_W, self.BANK_H))
        except (KeyError, Exception):
            self.bank_image = pg.Surface((self.BANK_W, self.BANK_H))
            self.bank_image.fill((100, 70, 30))

        self.bank_rect = self.bank_image.get_rect(topleft=(self.BANK_X, self.BANK_Y))

        # --- Shovel cursor image ---
        try:
            raw_shovel = engine.GFX[c.SHOVEL]
            self.shovel_image = pg.transform.smoothscale(raw_shovel,
                                    (self.SHOVEL_W, self.SHOVEL_H))
        except (KeyError, Exception):
            self.shovel_image = pg.Surface((self.SHOVEL_W, self.SHOVEL_H))
            self.shovel_image.fill((180, 100, 30))

        # Shovel resting inside bank (centred)
        self.shovel_rest_rect = self.shovel_image.get_rect(center=self.bank_rect.center)

    # ----------------------------------------------------------------
    def handle_click(self, mouse_pos, mouse_click):
        """
        Call every frame from Level.play() BEFORE plant-drag logic.
        Returns True if the click was consumed by the shovel UI.
        """
        if mouse_click and mouse_click[1]:      # right-click always cancels
            if self.active:
                self.deactivate()
            return False                         # don't consume right-click

        if mouse_click and mouse_click[0]:
            if self.bank_rect.collidepoint(mouse_pos):
                # Toggle
                if self.active:
                    self.deactivate()
                else:
                    self.activate()
                return True                      # consumed
        return False

    def activate(self):
        self.active = True
        pg.mouse.set_visible(False)

    def deactivate(self):
        self.active = False
        pg.mouse.set_visible(True)

    def try_remove_plant(self, mouse_pos, plant_groups, map_obj,
                         kill_plant_fn, bar_type):
        """
        Call when shovel is active and left-click happens outside the bank.
        Checks every plant group for a click collision and removes the first hit.
        Returns True if a plant was removed.
        """
        if not self.active or mouse_pos is None:
            return False

        for group in plant_groups:
            for p in group:
                if p.rect.collidepoint(mouse_pos):
                    kill_plant_fn(p)
                    self.deactivate()
                    return True
        return False

    def draw(self, surface):
        """Draw the bank. If active draw shovel following cursor, else resting in bank."""
        surface.blit(self.bank_image, self.bank_rect)

        if self.active:
            # Shovel follows mouse cursor
            mx, my = pg.mouse.get_pos()
            cursor_rect = self.shovel_image.get_rect(center=(mx, my))
            surface.blit(self.shovel_image, cursor_rect)
        else:
            # Shovel rests centred inside the bank
            surface.blit(self.shovel_image, self.shovel_rest_rect)