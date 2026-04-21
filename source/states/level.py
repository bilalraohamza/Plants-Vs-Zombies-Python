__author__ = 'Rao Hamza Bilal'

import os
import json
import pygame as pg
from ..core import constants as c
from ..core import engine
from ..components import map, menu_bar, plant, zombie
from ..states.hint_system import HintSystem, _load_tutorial_seen

class WaveText:
    def __init__(self):
        try:
            font_path = os.path.join(c.FONTS_DIR, 'Fredoka-Bold.ttf')
            self.font_normal = pg.font.Font(font_path, 30)
            self.font_huge   = pg.font.Font(font_path, 38)
        except (IOError, AttributeError):
            self.font_normal = pg.font.SysFont('arial', 30, bold=True)
            self.font_huge   = pg.font.SysFont('arial', 38, bold=True)

        self.active   = False
        self.text     = ''
        self.is_huge  = False
        self.x        = float(c.SCREEN_WIDTH + 300)
        self.y        = 120
        self.alpha    = 255
        self.state    = 'done'
        self.hold_start = 0

        self.TARGET_X = c.SCREEN_WIDTH // 2
        self.SLIDE_SPEED = 14
        self.HOLD_TIME   = 2500
        self.FADE_SPEED  = 6

    def show(self, text, is_huge, current_time):
        self.text       = text
        self.is_huge    = is_huge
        self.active     = True
        self.x          = float(c.SCREEN_WIDTH + 300)
        self.alpha      = 255
        self.state      = 'slide_in'
        self.hold_start = 0

    def update(self, current_time):
        if not self.active:
            return
        if self.state == 'slide_in':
            self.x -= self.SLIDE_SPEED
            if self.x <= self.TARGET_X:
                self.x = float(self.TARGET_X)
                self.state = 'hold'
                self.hold_start = current_time
        elif self.state == 'hold':
            if current_time - self.hold_start >= self.HOLD_TIME:
                self.state = 'fade_out'
        elif self.state == 'fade_out':
            self.alpha -= self.FADE_SPEED
            if self.alpha <= 0:
                self.alpha  = 0
                self.active = False
                self.state  = 'done'

    def draw(self, surface):
        if not self.active:
            return
        font  = self.font_huge   if self.is_huge else self.font_normal
        color = (255, 60, 60)    if self.is_huge else (255, 230, 50)

        shadow = font.render(self.text, True, (0, 0, 0))
        text   = font.render(self.text, True, color)

        shadow.set_alpha(self.alpha)
        text.set_alpha(self.alpha)

        cx, cy = int(self.x), self.y
        shadow_rect = shadow.get_rect(center=(cx + 3, cy + 3))
        text_rect   = text.get_rect(center=(cx, cy))

        surface.blit(shadow, shadow_rect)
        surface.blit(text,   text_rect)

# ==========================================
# --- UI & MENU BUTTON CLASSES ---
# ==========================================
class InGameMenuButton():
    def __init__(self):
        try:
            raw_bg = engine.GFX['CustomMenuButton']
            self.bg_image = pg.transform.scale(raw_bg, (130, 40))
        except KeyError:
            print("Warning: Could not find CustomMenuButton.png!")
            self.bg_image = pg.Surface((130, 40))
            self.bg_image.fill((100, 100, 100))

        self.bg_image.set_colorkey(c.BLACK)
        self.rect = self.bg_image.get_rect(topright=(c.SCREEN_WIDTH - 10, 5))

        pg.font.init()
        try:
            self.font = pg.font.Font(c.FONT_PATH, 24)
        except (IOError, AttributeError):
            self.font = pg.font.SysFont("papyrus", 24, bold=True)

        self.is_hovering = False
        self.text_idle = self.font.render("Menu", True, (255, 255, 255))
        self.text_hover = self.font.render("Menu", True, (0, 193, 33))

        new_w = int(self.text_hover.get_width() * 1.1)
        new_h = int(self.text_hover.get_height() * 1.1)
        self.text_hover = pg.transform.smoothscale(self.text_hover, (new_w, new_h))

    def update(self, mouse_pos, mouse_click):
        current_mouse_pos = mouse_pos if mouse_pos else pg.mouse.get_pos()
        clicked = False
        if current_mouse_pos and self.rect.collidepoint(current_mouse_pos):
            self.is_hovering = True
            if mouse_click and mouse_click[0]:
                clicked = True
        else:
            self.is_hovering = False
        return clicked

    def draw(self, surface):
        surface.blit(self.bg_image, self.rect)

        color = (0, 193, 33) if self.is_hovering else (255, 255, 255)
        text_img = self.font.render("Menu", True, color)

        if self.is_hovering:
            new_w, new_h = int(text_img.get_width() * 1.1), int(text_img.get_height() * 1.1)
            text_img = pg.transform.smoothscale(text_img, (new_w, new_h))

        text_rect = text_img.get_rect(center=self.rect.center)
        text_rect.y += 2
        surface.blit(text_img, text_rect)


class PauseMenuOverlay():
    def __init__(self):
        self.is_active = False

        try:
            self.bg_image = engine.GFX['options_menuback']
            self.bg_image.set_colorkey(c.BLACK)
        except KeyError:
            print("Warning: options_menuback.png not found. Using fallback.")
            self.bg_image = pg.Surface((400, 450))
            self.bg_image.fill((80, 80, 100))

        self.bg_rect = self.bg_image.get_rect(center=(c.SCREEN_WIDTH//2, c.SCREEN_HEIGHT//2))

        pg.font.init()
        try:
            self.font = pg.font.Font(c.FONT_PATH, 28)
        except (IOError, AttributeError):
            self.font = pg.font.SysFont("papyrus", 28, bold=True)

        self.options = ["Back To Game", "Restart Level", "Main Menu", "Quit Game"]

        start_y = self.bg_rect.y + (self.bg_rect.height // 3) - 20
        self.rects = [pg.Rect(self.bg_rect.centerx - 130, start_y + (i * 60), 260, 40) for i in range(len(self.options))]

        self.hovered_index = -1

    def update(self, mouse_pos, mouse_click):
        if not self.is_active: return None
        self.hovered_index = -1
        current_mouse_pos = mouse_pos if mouse_pos else pg.mouse.get_pos()

        for i, rect in enumerate(self.rects):
            if rect.collidepoint(current_mouse_pos):
                self.hovered_index = i
                if mouse_click and mouse_click[0]:
                    return self.options[i]
        return None

    def draw(self, surface):
        if not self.is_active: return

        overlay = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        surface.blit(self.bg_image, self.bg_rect)

        for i, option in enumerate(self.options):
            rect = self.rects[i]
            is_hovered = (i == self.hovered_index)

            color = (0, 193, 33) if is_hovered else (255, 255, 255)
            text_img = self.font.render(option, True, color)

            if is_hovered:
                text_img = pg.transform.smoothscale(text_img, (int(text_img.get_width()*1.1), int(text_img.get_height()*1.1)))

            surface.blit(text_img, text_img.get_rect(center=rect.center))


class Level(engine.State):
    def __init__(self):
        engine.State.__init__(self)

    def startup(self, current_time, persist):
        self.game_info = persist
        self.persist = self.game_info
        self.game_info[c.CURRENT_TIME] = current_time
        self.map_y_len = c.GRID_Y_LEN
        self.map = map.Map(c.GRID_X_LEN, self.map_y_len)

        self.load_map()
        self.setup_background()
        self.init_state()

        self.menu_button = InGameMenuButton()
        self.pause_menu = PauseMenuOverlay()

        # Hint system: only for Level 1, and only if the player hasn't seen it before
        current_user = self.game_info.get(c.CURRENT_USER, None)
        if self.game_info.get(c.LEVEL_NUM, 1) == 1 and not _load_tutorial_seen(current_user):
            self.hint_system = HintSystem(self)
        else:
            self.hint_system = None

    def load_map(self):
        map_file = 'level_' + str(self.game_info[c.LEVEL_NUM]) + '.json'
        file_path = os.path.join(c.LEVELS_DIR, map_file)
        with open(file_path) as file_handle:
            self.map_data = json.load(file_handle)

    def setup_background(self):
        img_index = self.map_data[c.BACKGROUND_TYPE]
        self.background_type = img_index
        self.background = engine.GFX[c.BACKGROUND_NAME][img_index]
        self.bg_rect = self.background.get_rect()

        self.level = pg.Surface((self.bg_rect.w, self.bg_rect.h)).convert()
        self.viewport = engine.SCREEN.get_rect(bottom=self.bg_rect.bottom)
        self.viewport.x += c.BACKGROUND_OFFSET_X

    def setup_groups(self):
        self.sun_group = pg.sprite.Group()
        self.head_group = pg.sprite.Group()

        self.plant_groups = []
        self.zombie_groups = []
        self.hypno_zombie_groups = []
        self.bullet_groups = []
        for i in range(self.map_y_len):
            self.plant_groups.append(pg.sprite.Group())
            self.zombie_groups.append(pg.sprite.Group())
            self.hypno_zombie_groups.append(pg.sprite.Group())
            self.bullet_groups.append(pg.sprite.Group())

    def setup_zombies(self):
        def take_time(element):
            return element[0]

        self.zombie_list = []
        for data in self.map_data[c.ZOMBIE_LIST]:
            self.zombie_list.append((data['time'], data['name'], data['map_y']))
        self.zombie_start_time = 0
        self.zombie_list.sort(key=take_time)

    def setup_cars(self):
        self.cars = []
        for i in range(self.map_y_len):
            _, y = self.map.get_map_grid_pos(0, i)
            self.cars.append(plant.Car(-25, y+20, i))

    def update(self, surface, current_time, mouse_pos, mouse_click):
        self.current_time = self.game_info[c.CURRENT_TIME] = current_time

        keys = pg.key.get_pressed()
        if keys[pg.K_n]:
            self.game_info[c.LEVEL_NUM] += 1
            self.persist[c.ZOMBIES_KILLED] = 7
            self.persist[c.SUN_COLLECTED]  = 350
            self.persist[c.PLANTS_PLANTED] = 5
            self.next = c.GAME_VICTORY
            self.done = True
            self.draw(surface)                                    # ADD THIS
            self.persist[c.VICTORY_BACKGROUND] = surface.copy()  # ADD THIS
            return

        if keys[pg.K_l]:
            self.next = c.GAME_LOSE
            self.done = True
            self.draw(surface)                                # ADD THIS
            self.persist[c.LOSE_BACKGROUND] = surface.copy() # ADD THIS
            return
        

        if hasattr(self, 'pause_menu') and self.pause_menu.is_active:
            action = self.pause_menu.update(mouse_pos, mouse_click)
            if action:
                if action == "Back To Game":
                    self.pause_menu.is_active = False
                elif action == "Restart Level":
                    self.next = c.LEVEL
                    self.done = True
                elif action == "Main Menu":
                    self.next = getattr(c, 'MAIN_MENU', 'main menu')
                    self.done = True
                elif action == "Quit Game":
                    import sys
                    pg.quit()
                    sys.exit()
            if not self.done:
                self.draw(surface)
            return

        if self.state == c.CHOOSE:
            self.choose(mouse_pos, mouse_click)
        elif self.state == c.PLAY:
            self.play(mouse_pos, mouse_click)

        if hasattr(self, 'menu_button'):
            if self.menu_button.update(mouse_pos, mouse_click):
                self.pause_menu.is_active = True
                if not self.done:
                    self.draw(surface)
                return

        if not self.done:
            self.draw(surface)
        elif self.next == c.GAME_VICTORY:
            self.draw(surface)
            self.persist[c.VICTORY_BACKGROUND] = surface.copy()
        elif self.next == c.GAME_LOSE:
            self.draw(surface)
            self.persist[c.LOSE_BACKGROUND] = surface.copy()

    def init_bowling_map(self):
        print('init_bowling_map')
        for x in range(3, self.map.width):
            for y in range(self.map.height):
                self.map.set_map_grid_type(x, y, c.MAP_EXIST)

    def init_state(self):
        if c.CHOOSEBAR_TYPE in self.map_data:
            self.bar_type = self.map_data[c.CHOOSEBAR_TYPE]
        else:
            self.bar_type = c.CHOOSEBAR_STATIC

        if self.bar_type == c.CHOOSEBAR_STATIC:
            self.init_choose()
        else:
            card_pool = menu_bar.get_card_pool(self.map_data[c.CARD_POOL])
            self.init_play(card_pool)
            if self.bar_type == c.CHOSSEBAR_BOWLING:
                self.init_bowling_map()

    def init_choose(self):
        self.state = c.CHOOSE
        self.panel = menu_bar.Panel(menu_bar.all_card_list, self.map_data[c.INIT_SUN_NAME])

    def choose(self, mouse_pos, mouse_click):
        self.panel.update(mouse_pos)
        if mouse_pos and mouse_click[0]:
            self.panel.check_card_click(mouse_pos)
            if self.panel.check_start_button_click(mouse_pos):
                self.init_play(self.panel.get_selected_cards())

        if self.hint_system:
            self.hint_system.update(self.current_time, mouse_pos, mouse_click)

    def init_play(self, card_list):
        self.state = c.PLAY

        # --- STAT TRACKING COUNTERS ---
        self.zombies_killed = 0
        self.sun_collected = 0
        self.plants_planted = 0

        if self.bar_type == c.CHOOSEBAR_STATIC:
            self.menubar = menu_bar.MenuBar(card_list, self.map_data[c.INIT_SUN_NAME])
        else:
            self.menubar = menu_bar.MoveBar(card_list)
        self.drag_plant = False
        self.hint_image = None
        self.hint_plant = False
        if self.background_type == c.BACKGROUND_DAY and self.bar_type == c.CHOOSEBAR_STATIC:
            self.produce_sun = True
        else:
            self.produce_sun = False
        self.sun_timer = self.current_time

        self.remove_mouse_image()
        self.setup_groups()
        self.setup_zombies()
        # --- WAVE TEXT SETUP ---
        self.wave_data = list(self.map_data.get('wave_data', []))
        self.next_wave_index = 0
        self.wave_text = WaveText()
        self.setup_cars()

    def play(self, mouse_pos, mouse_click):
        if self.zombie_start_time == 0:
            self.zombie_start_time = self.current_time
        elif len(self.zombie_list) > 0:
            data = self.zombie_list[0]
            if data[0] <= (self.current_time - self.zombie_start_time):
                self.create_zombie(data[1], data[2])
                self.zombie_list.remove(data)
        # --- WAVE TEXT TRIGGER ---
        if hasattr(self, 'wave_text') and hasattr(self, 'wave_data'):
            elapsed = self.current_time - self.zombie_start_time
            if self.next_wave_index < len(self.wave_data):
                wave = self.wave_data[self.next_wave_index]
                if elapsed >= wave['trigger_time']:
                    self.wave_text.show(
                        wave['warning_text'],
                        wave['is_huge_wave'],
                        self.current_time
                    )
                    self.next_wave_index += 1
            self.wave_text.update(self.current_time)

        for i in range(self.map_y_len):
            self.bullet_groups[i].update(self.game_info)
            self.plant_groups[i].update(self.game_info)
            self.zombie_groups[i].update(self.game_info)
            self.hypno_zombie_groups[i].update(self.game_info)
            for zombie in self.hypno_zombie_groups[i]:
                if zombie.rect.x > c.SCREEN_WIDTH:
                    zombie.kill()

        self.head_group.update(self.game_info)
        self.sun_group.update(self.game_info)

        if not self.drag_plant and mouse_pos and mouse_click[0]:
            result = self.menubar.check_card_click(mouse_pos)
            if result:
                self.setup_mouse_image(result[0], result[1])
        elif self.drag_plant:
            if mouse_click[1]:
                self.remove_mouse_image()
            elif mouse_click[0]:
                if self.menubar.check_menu_bar_click(mouse_pos):
                    self.remove_mouse_image()
                else:
                    self.add_plant()
            elif mouse_pos is None:
                self.setup_hint_image()

        if self.produce_sun:
            if (self.current_time - self.sun_timer) > c.PRODUCE_SUN_INTERVAL:
                self.sun_timer = self.current_time
                map_x, map_y = self.map.get_random_map_index()
                x, y = self.map.get_map_grid_pos(map_x, map_y)
                self.sun_group.add(plant.Sun(x, 0, x, y))

        if not self.drag_plant and mouse_pos and mouse_click[0]:
            for sun in self.sun_group:
                if sun.check_collision(mouse_pos[0], mouse_pos[1]):
                    self.menubar.increase_sun_value(sun.sun_value)
                    # --- TRACK SUN COLLECTED ---
                    self.sun_collected += sun.sun_value

        for car in self.cars:
            car.update(self.game_info)

        self.menubar.update(self.current_time)

        self.check_bullet_collisions()
        self.check_zombie_collisions()
        self.check_plants()
        self.check_car_collisions()
        self.check_game_state()

        if self.hint_system:
            self.hint_system.update(self.current_time, mouse_pos, mouse_click)

    def create_zombie(self, name, map_y):
        x, y = self.map.get_map_grid_pos(0, map_y)
        if name == c.NORMAL_ZOMBIE:
            self.zombie_groups[map_y].add(zombie.NormalZombie(c.ZOMBIE_START_X, y, self.head_group))
        elif name == c.CONEHEAD_ZOMBIE:
            self.zombie_groups[map_y].add(zombie.ConeHeadZombie(c.ZOMBIE_START_X, y, self.head_group))
        elif name == c.BUCKETHEAD_ZOMBIE:
            self.zombie_groups[map_y].add(zombie.BucketHeadZombie(c.ZOMBIE_START_X, y, self.head_group))
        elif name == c.FLAG_ZOMBIE:
            self.zombie_groups[map_y].add(zombie.FlagZombie(c.ZOMBIE_START_X, y, self.head_group))
        elif name == c.NEWSPAPER_ZOMBIE:
            self.zombie_groups[map_y].add(zombie.NewspaperZombie(c.ZOMBIE_START_X, y, self.head_group))

    def can_seed_plant(self):
        x, y = pg.mouse.get_pos()
        return self.map.show_plant(x, y)

    def add_plant(self):
        pos = self.can_seed_plant()
        if pos is None:
            return

        if self.hint_image is None:
            self.setup_hint_image()
        x, y = self.hint_rect.centerx, self.hint_rect.bottom
        map_x, map_y = self.map.get_map_index(x, y)
        if self.plant_name == c.SUNFLOWER:
            new_plant = plant.SunFlower(x, y, self.sun_group)
        elif self.plant_name == c.PEASHOOTER:
            new_plant = plant.PeaShooter(x, y, self.bullet_groups[map_y])
        elif self.plant_name == c.SNOWPEASHOOTER:
            new_plant = plant.SnowPeaShooter(x, y, self.bullet_groups[map_y])
        elif self.plant_name == c.WALLNUT:
            new_plant = plant.WallNut(x, y)
        elif self.plant_name == c.CHERRYBOMB:
            new_plant = plant.CherryBomb(x, y)
        elif self.plant_name == c.THREEPEASHOOTER:
            new_plant = plant.ThreePeaShooter(x, y, self.bullet_groups, map_y)
        elif self.plant_name == c.REPEATERPEA:
            new_plant = plant.RepeaterPea(x, y, self.bullet_groups[map_y])
        elif self.plant_name == c.CHOMPER:
            new_plant = plant.Chomper(x, y)
        elif self.plant_name == c.PUFFSHROOM:
            new_plant = plant.PuffShroom(x, y, self.bullet_groups[map_y])
        elif self.plant_name == c.POTATOMINE:
            new_plant = plant.PotatoMine(x, y)
        elif self.plant_name == c.SQUASH:
            new_plant = plant.Squash(x, y)
        elif self.plant_name == c.SPIKEWEED:
            new_plant = plant.Spikeweed(x, y)
        elif self.plant_name == c.JALAPENO:
            new_plant = plant.Jalapeno(x, y)
        elif self.plant_name == c.SCAREDYSHROOM:
            new_plant = plant.ScaredyShroom(x, y, self.bullet_groups[map_y])
        elif self.plant_name == c.SUNSHROOM:
            new_plant = plant.SunShroom(x, y, self.sun_group)
        elif self.plant_name == c.ICESHROOM:
            new_plant = plant.IceShroom(x, y)
        elif self.plant_name == c.HYPNOSHROOM:
            new_plant = plant.HypnoShroom(x, y)
        elif self.plant_name == c.WALLNUTBOWLING:
            new_plant = plant.WallNutBowling(x, y, map_y, self)
        elif self.plant_name == c.REDWALLNUTBOWLING:
            new_plant = plant.RedWallNutBowling(x, y)

        if new_plant.can_sleep and self.background_type == c.BACKGROUND_DAY:
            new_plant.set_sleep()
        self.plant_groups[map_y].add(new_plant)

        # --- TRACK PLANTS PLANTED ---
        self.plants_planted += 1

        if self.bar_type == c.CHOOSEBAR_STATIC:
            self.menubar.decrease_sun_value(self.select_plant.sun_cost)
            self.menubar.set_card_frozen_time(self.plant_name)
        else:
            self.menubar.delete_card(self.select_plant)

        if self.bar_type != c.CHOSSEBAR_BOWLING:
            self.map.set_map_grid_type(map_x, map_y, c.MAP_EXIST)
        self.remove_mouse_image()

    def setup_hint_image(self):
        pos = self.can_seed_plant()
        if pos and self.mouse_image:
            if (self.hint_image and pos[0] == self.hint_rect.x and
                pos[1] == self.hint_rect.y):
                return
            width, height = self.mouse_rect.w, self.mouse_rect.h
            image = pg.Surface([width, height])
            image.blit(self.mouse_image, (0, 0), (0, 0, width, height))
            image.set_colorkey(c.BLACK)
            image.set_alpha(128)
            self.hint_image = image
            self.hint_rect = image.get_rect()
            self.hint_rect.centerx = pos[0]
            self.hint_rect.bottom = pos[1]
            self.hint_plant = True
        else:
            self.hint_plant = False

    def setup_mouse_image(self, plant_name, select_plant):
        frame_list = engine.GFX[plant_name]
        if plant_name in engine.PLANT_RECT:
            data = engine.PLANT_RECT[plant_name]
            x, y, width, height = data['x'], data['y'], data['width'], data['height']
        else:
            x, y = 0, 0
            rect = frame_list[0].get_rect()
            width, height = rect.w, rect.h

        if (plant_name == c.POTATOMINE or plant_name == c.SQUASH or
            plant_name == c.SPIKEWEED or plant_name == c.JALAPENO or
            plant_name == c.SCAREDYSHROOM or plant_name == c.SUNSHROOM or
            plant_name == c.ICESHROOM or plant_name == c.HYPNOSHROOM or
            plant_name == c.WALLNUTBOWLING or plant_name == c.REDWALLNUTBOWLING):
            color = c.WHITE
        else:
            color = c.BLACK
        self.mouse_image = engine.get_image(frame_list[0], x, y, width, height, color, 1)
        self.mouse_rect = self.mouse_image.get_rect()
        pg.mouse.set_visible(False)
        self.drag_plant = True
        self.plant_name = plant_name
        self.select_plant = select_plant

    def remove_mouse_image(self):
        pg.mouse.set_visible(True)
        self.drag_plant = False
        self.mouse_image = None
        self.hint_image = None
        self.hint_plant = False

    def check_bullet_collisions(self):
        collided_func = pg.sprite.collide_circle_ratio(0.7)
        for i in range(self.map_y_len):
            for bullet in self.bullet_groups[i]:
                if bullet.state == c.FLY:
                    zombie = pg.sprite.spritecollideany(bullet, self.zombie_groups[i], collided_func)
                    if zombie and zombie.state != c.DIE:
                        zombie.set_damage(bullet.damage, bullet.ice)
                        # Count kill if this bullet was lethal
                        if zombie.health <= 0:
                            self.zombies_killed += 1
                        bullet.set_explode()

    def check_zombie_collisions(self):
        if self.bar_type == c.CHOSSEBAR_BOWLING:
            ratio = 0.6
        else:
            ratio = 0.7
        collided_func = pg.sprite.collide_circle_ratio(ratio)
        for i in range(self.map_y_len):
            hypo_zombies = []
            for zombie in self.zombie_groups[i]:
                if zombie.state != c.WALK:
                    continue
                plant = pg.sprite.spritecollideany(zombie, self.plant_groups[i], collided_func)
                if plant:
                    if plant.name == c.WALLNUTBOWLING:
                        if plant.can_hit(i):
                            zombie.set_damage(c.WALLNUT_BOWLING_DAMAGE)
                            plant.change_direction(i)
                    elif plant.name == c.REDWALLNUTBOWLING:
                        if plant.state == c.IDLE:
                            plant.set_attack()
                    elif plant.name != c.SPIKEWEED:
                        zombie.set_attack(plant)

            for hypno_zombie in self.hypno_zombie_groups[i]:
                if hypno_zombie.health <= 0:
                    continue
                zombie_list = pg.sprite.spritecollide(hypno_zombie,
                               self.zombie_groups[i], False, collided_func)
                for zombie in zombie_list:
                    if zombie.state == c.DIE:
                        continue
                    if zombie.state == c.WALK:
                        zombie.set_attack(hypno_zombie, False)
                    if hypno_zombie.state == c.WALK:
                        hypno_zombie.set_attack(zombie, False)

    def check_car_collisions(self):
        collided_func = pg.sprite.collide_circle_ratio(0.8)
        for car in self.cars:
            zombies = pg.sprite.spritecollide(car, self.zombie_groups[car.map_y], False, collided_func)
            for zombie in zombies:
                if zombie and zombie.state != c.DIE:
                    car.set_walk()
                    zombie.set_die()
                    # --- TRACK ZOMBIE KILLS (car) ---
                    self.zombies_killed += 1
            if car.dead:
                self.cars.remove(car)

    def boom_zombies(self, x, map_y, y_range, x_range):
        for i in range(self.map_y_len):
            if abs(i - map_y) > y_range:
                continue
            for zombie in self.zombie_groups[i]:
                if abs(zombie.rect.centerx - x) <= x_range:
                    zombie.set_boom_die()
                    # --- TRACK ZOMBIE KILLS (explosions) ---
                    self.zombies_killed += 1

    def freeze_zombies(self, plant):
        for i in range(self.map_y_len):
            for zombie in self.zombie_groups[i]:
                if zombie.rect.centerx < c.SCREEN_WIDTH:
                    zombie.set_freeze(plant.trap_frames[0])

    def kill_plant(self, plant):
        x, y = plant.get_position()
        map_x, map_y = self.map.get_map_index(x, y)
        if self.bar_type != c.CHOSSEBAR_BOWLING:
            self.map.set_map_grid_type(map_x, map_y, c.MAP_EMPTY)
        if (plant.name == c.CHERRYBOMB or plant.name == c.JALAPENO or
            (plant.name == c.POTATOMINE and not plant.is_init) or
            plant.name == c.REDWALLNUTBOWLING):
            self.boom_zombies(plant.rect.centerx, map_y, plant.explode_y_range,
                              plant.explode_x_range)
        elif plant.name == c.ICESHROOM and plant.state != c.SLEEP:
            self.freeze_zombies(plant)
        elif plant.name == c.HYPNOSHROOM and plant.state != c.SLEEP:
            zombie = plant.kill_zombie
            zombie.set_hypno()
            _, map_y = self.map.get_map_index(zombie.rect.centerx, zombie.rect.bottom)
            self.zombie_groups[map_y].remove(zombie)
            self.hypno_zombie_groups[map_y].add(zombie)
        plant.kill()

    def check_plant(self, plant, i):
        zombie_len = len(self.zombie_groups[i])
        if plant.name == c.THREEPEASHOOTER:
            if plant.state == c.IDLE:
                if zombie_len > 0:
                    plant.set_attack()
                elif (i-1) >= 0 and len(self.zombie_groups[i-1]) > 0:
                    plant.set_attack()
                elif (i+1) < self.map_y_len and len(self.zombie_groups[i+1]) > 0:
                    plant.set_attack()
            elif plant.state == c.ATTACK:
                if zombie_len > 0:
                    pass
                elif (i-1) >= 0 and len(self.zombie_groups[i-1]) > 0:
                    pass
                elif (i+1) < self.map_y_len and len(self.zombie_groups[i+1]) > 0:
                    pass
                else:
                    plant.set_idle()
        elif plant.name == c.CHOMPER:
            for zombie in self.zombie_groups[i]:
                if plant.can_attack(zombie):
                    plant.set_attack(zombie, self.zombie_groups[i])
                    break
        elif plant.name == c.POTATOMINE:
            for zombie in self.zombie_groups[i]:
                if plant.can_attack(zombie):
                    plant.set_attack()
                    break
        elif plant.name == c.SQUASH:
            for zombie in self.zombie_groups[i]:
                if plant.can_attack(zombie):
                    plant.set_attack(zombie, self.zombie_groups[i])
                    break
        elif plant.name == c.SPIKEWEED:
            can_attack = False
            for zombie in self.zombie_groups[i]:
                if plant.can_attack(zombie):
                    can_attack = True
                    break
            if plant.state == c.IDLE and can_attack:
                plant.set_attack(self.zombie_groups[i])
            elif plant.state == c.ATTACK and not can_attack:
                plant.set_idle()
        elif plant.name == c.SCAREDYSHROOM:
            need_cry = False
            can_attack = False
            for zombie in self.zombie_groups[i]:
                if plant.need_cry(zombie):
                    need_cry = True
                    break
                elif plant.can_attack(zombie):
                    can_attack = True
            if need_cry:
                if plant.state != c.CRY:
                    plant.set_cry()
            elif can_attack:
                if plant.state != c.ATTACK:
                    plant.set_attack()
            elif plant.state != c.IDLE:
                plant.set_idle()
        elif (plant.name == c.WALLNUTBOWLING or
              plant.name == c.REDWALLNUTBOWLING):
            pass
        else:
            can_attack = False
            if (plant.state == c.IDLE and zombie_len > 0):
                for zombie in self.zombie_groups[i]:
                    if plant.can_attack(zombie):
                        can_attack = True
                        break
            if plant.state == c.IDLE and can_attack:
                plant.set_attack()
            elif (plant.state == c.ATTACK and not can_attack):
                plant.set_idle()

    def check_plants(self):
        for i in range(self.map_y_len):
            for plant in self.plant_groups[i]:
                if plant.state != c.SLEEP:
                    self.check_plant(plant, i)
                if plant.health <= 0:
                    self.kill_plant(plant)

    def check_victory(self):
        if len(self.zombie_list) > 0:
            return False
        for i in range(self.map_y_len):
            if len(self.zombie_groups[i]) > 0:
                return False
        return True

    def check_lose(self):
        for i in range(self.map_y_len):
            for zombie in self.zombie_groups[i]:
                if zombie.rect.right < 0:
                    return True
        return False

    def check_game_state(self):
        if self.check_victory():
            self.game_info[c.LEVEL_NUM] += 1
            self.persist[c.ZOMBIES_KILLED] = self.zombies_killed
            self.persist[c.SUN_COLLECTED]  = self.sun_collected
            self.persist[c.PLANTS_PLANTED] = self.plants_planted

            # Calculate score
            score = (self.zombies_killed * 100 +
                     self.sun_collected  * 2   +
                     self.plants_planted * 10)
            self.persist[c.LEVEL_SCORE] = score

            # Save score and check for beaten users
            from ..states.user_select import save_level_score, check_beaten_users
            completed_level = self.game_info[c.LEVEL_NUM] - 1
            username        = self.persist.get(c.CURRENT_USER, None)
            if username:
                is_best = save_level_score(username, completed_level, score)
                beaten  = check_beaten_users(username, completed_level, score)
            else:
                is_best = False
                beaten  = []
            self.persist[c.LEVEL_SCORE_IS_BEST] = is_best
            self.persist[c.BEATEN_USERS]        = beaten

            # Save level progress
            from ..states.user_select import update_profile_level
            if username:
                update_profile_level(username, self.game_info[c.LEVEL_NUM])

            self.next = c.GAME_VICTORY
            self.done = True

        elif self.check_lose():
            self.persist[c.ZOMBIES_KILLED] = self.zombies_killed
            self.persist[c.SUN_COLLECTED]  = self.sun_collected
            self.persist[c.PLANTS_PLANTED] = self.plants_planted
            self.next = c.GAME_LOSE
            self.done = True

    def draw_mouse_show(self, surface):
        if self.hint_plant:
            surface.blit(self.hint_image, self.hint_rect)
        x, y = pg.mouse.get_pos()
        self.mouse_rect.centerx = x
        self.mouse_rect.centery = y
        surface.blit(self.mouse_image, self.mouse_rect)

    def draw_zombie_freeze_trap(self, i, surface):
        for zombie in self.zombie_groups[i]:
            zombie.draw_freeze_trap(surface)

    def draw(self, surface):
        self.level.blit(self.background, self.viewport, self.viewport)
        surface.blit(self.level, (0, 0), self.viewport)

        is_paused = hasattr(self, 'pause_menu') and self.pause_menu.is_active

        if self.state == c.CHOOSE:
            if not is_paused:
                self.panel.draw(surface)

        elif self.state == c.PLAY:
            # --- DRAW WAVE TEXT ---
            if hasattr(self, 'wave_text') and not is_paused:
                self.wave_text.draw(surface)
            if hasattr(self, 'menubar') and not is_paused:
                self.menubar.draw(surface)

            for i in range(self.map_y_len):
                self.plant_groups[i].draw(surface)
                self.zombie_groups[i].draw(surface)
                self.hypno_zombie_groups[i].draw(surface)
                self.bullet_groups[i].draw(surface)
                self.draw_zombie_freeze_trap(i, surface)
            for car in self.cars:
                car.draw(surface)
            self.head_group.draw(surface)
            self.sun_group.draw(surface)

            if self.drag_plant:
                self.draw_mouse_show(surface)

            if hasattr(self, 'menu_button') and not is_paused:
                self.menu_button.draw(surface)

        if is_paused:
            self.pause_menu.draw(surface)
        elif self.hint_system and not is_paused:
            self.hint_system.draw(surface, self.current_time)