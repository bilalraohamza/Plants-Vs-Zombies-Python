__author__ = 'Rao Hamza Bilal'

import random
import pygame as pg
from ..core import constants as c
from ..core import engine
from ..components import map, menu_bar, plant, zombie
from ..states.level import Level, InGameMenuButton, PauseMenuOverlay, WaveText


# ── Phase definitions ──────────────────────────────────────────────────────────
# Each phase triggers at the given elapsed ms, shows a banner, and changes
# the zombie pool, spawn rate, spawn count and sun drop rate.

_PHASES = [
    # (trigger_ms, banner_text,                 is_huge, spawn_interval, spawn_count, sun_interval, zombie_pool_key)
    # sun_interval is ms between sky sun drops - much faster than adventure (7000ms)
    (       0,  "SURVIVAL MODE STARTED!",          True,   5500,  1,  3500, 'easy'),
    (  30_000,  "Wave 2 - They\'re multiplying!",  False,  4000,  1,  2800, 'easy'),
    (  60_000,  "Wave 3 - CONE HEADS INCOMING!",   False,  3000,  2,  2200, 'medium'),
    (  90_000,  "Wave 4 - DANGER! BUCKET HEADS!",  True,   2200,  2,  1700, 'hard'),
    ( 120_000,  "MASSIVE HORDE!",                  True,   1600,  3,  1300, 'hard'),
    ( 180_000,  "ENDLESS NIGHTMARE!",              True,   1100,  3,   950, 'nightmare'),
    ( 240_000,  "THEY NEVER STOP!",                True,    800,  4,   700, 'nightmare'),
]

_ZOMBIE_POOLS = {
    'easy':      [c.NORMAL_ZOMBIE] * 5,
    'medium':    [c.NORMAL_ZOMBIE] * 3 + [c.CONEHEAD_ZOMBIE] * 2 + [c.FLAG_ZOMBIE],
    'hard':      ([c.NORMAL_ZOMBIE] * 2 + [c.CONEHEAD_ZOMBIE] * 2 +
                  [c.BUCKETHEAD_ZOMBIE] + [c.FLAG_ZOMBIE] + [c.NEWSPAPER_ZOMBIE]),
    'nightmare': ([c.NORMAL_ZOMBIE] + [c.CONEHEAD_ZOMBIE] * 2 +
                  [c.BUCKETHEAD_ZOMBIE] * 2 + [c.FLAG_ZOMBIE] * 2 +
                  [c.NEWSPAPER_ZOMBIE] * 2),
}


class SurvivalLevel(Level):
    """
    Survival mode: no win condition, escalating zombie waves, increasing sun.
    Subclasses Level and overrides: load_map, startup, update, play,
    check_game_state, and draw.
    """

    # ── startup ───────────────────────────────────────────────────────────────

    def load_map(self):
        """Provide synthetic map data so no JSON file is needed."""
        self.map_data = {
            c.BACKGROUND_TYPE:  c.BACKGROUND_DAY,
            c.INIT_SUN_NAME:    150,           # More starting sun than adventure
            c.ZOMBIE_LIST:      [],
            c.CHOOSEBAR_TYPE:   c.CHOOSEBAR_STATIC,
        }

    def startup(self, current_time, persist):
        super().startup(current_time, persist)
        self.hint_system = None          # No tutorial in survival

        # Survival timing / phase state
        self.survival_start_time = None  # Set on first PLAY tick
        self.next_zombie_time    = 0
        self.current_phase_index = 0     # Tracks which phase we are in

        # Per-frame font for the HUD overlay
        try:
            self.hud_font = pg.font.Font(c.STATS_FONT_PATH, 19)
        except Exception:
            self.hud_font = pg.font.SysFont('arial', 19, bold=True)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _phase(self):
        """Return the current phase tuple."""
        idx = min(self.current_phase_index, len(_PHASES) - 1)
        return _PHASES[idx]

    def _advance_phases(self, elapsed):
        """Check if we should move to the next phase, show banner."""
        while self.current_phase_index + 1 < len(_PHASES):
            next_phase = _PHASES[self.current_phase_index + 1]
            if elapsed >= next_phase[0]:
                self.current_phase_index += 1
                txt, is_huge = next_phase[1], next_phase[2]
                self.wave_text.show(txt, is_huge, self.current_time)
            else:
                break

    # Max total zombies alive at once - keeps FPS stable at high phases
    MAX_ZOMBIES = 20

    def _spawn_zombies(self, elapsed):
        # Purge fully-dead sprites that have left the screen
        for i in range(self.map_y_len):
            for z in list(self.zombie_groups[i]):
                if z.rect.right < -60:
                    z.kill()

        # Cap to prevent FPS drops when many zombies accumulate
        total_live = sum(len(g) for g in self.zombie_groups)
        if total_live >= self.MAX_ZOMBIES:
            return

        phase = self._phase()
        spawn_interval = phase[3]
        spawn_count    = phase[4]
        pool_key       = phase[6]

        if self.current_time < self.next_zombie_time:
            return

        pool      = _ZOMBIE_POOLS[pool_key]
        used_rows = set()
        # Only spawn up to the remaining cap
        remaining = self.MAX_ZOMBIES - total_live
        count = min(spawn_count, remaining)
        for _ in range(count):
            zname  = random.choice(pool)
            avail  = [r for r in range(self.map_y_len) if r not in used_rows]
            if not avail:
                avail = list(range(self.map_y_len))
            row = random.choice(avail)
            used_rows.add(row)
            self.create_zombie(zname, row)

        self.next_zombie_time = self.current_time + spawn_interval

    # ── play (full override so we control sun + zombies) ──────────────────────

    def play(self, mouse_pos, mouse_click):

        # Initialise survival clock on first tick
        if self.survival_start_time is None:
            self.survival_start_time = self.current_time
            self.next_zombie_time    = self.current_time + 5500
            self.wave_text.show("SURVIVAL MODE STARTED!", True, self.current_time)

        elapsed = self.current_time - self.survival_start_time

        # Phase transitions
        self._advance_phases(elapsed)

        # Wave text animation
        self.wave_text.update(self.current_time)

        # Zombie spawning
        self._spawn_zombies(elapsed)

        # Sprite updates
        for i in range(self.map_y_len):
            self.bullet_groups[i].update(self.game_info)
            self.plant_groups[i].update(self.game_info)
            self.zombie_groups[i].update(self.game_info)
            self.hypno_zombie_groups[i].update(self.game_info)
            for z in list(self.hypno_zombie_groups[i]):
                if z.rect.x > c.SCREEN_WIDTH:
                    z.kill()

        self.head_group.update(self.game_info)
        self.sun_group.update(self.game_info)

        # Plant drag/place logic
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

        # Shovel tool
        if hasattr(self, 'shovel') and mouse_pos:
            consumed = self.shovel.handle_click(mouse_pos, mouse_click)
            if not consumed and mouse_click and mouse_click[0]:
                if self.shovel.active and not self.drag_plant:
                    self.shovel.try_remove_plant(
                        mouse_pos, self.plant_groups,
                        self.map, self.kill_plant, self.bar_type)
            if self.drag_plant and self.shovel.active:
                self.shovel.deactivate()

        # Dynamic sun production (interval shrinks each phase)
        sun_interval = self._phase()[5]
        if self.produce_sun:
            if (self.current_time - self.sun_timer) > sun_interval:
                self.sun_timer = self.current_time
                map_x, map_y  = self.map.get_random_map_index()
                x, y          = self.map.get_map_grid_pos(map_x, map_y)
                self.sun_group.add(plant.Sun(x, 0, x, y))

        # Sun collection
        if not self.drag_plant and mouse_pos and mouse_click[0]:
            for sun in self.sun_group:
                if sun.check_collision(mouse_pos[0], mouse_pos[1]):
                    self.menubar.increase_sun_value(sun.sun_value)
                    self.sun_collected += sun.sun_value

        for car in self.cars:
            car.update(self.game_info)

        self.menubar.update(self.current_time)

        self.check_bullet_collisions()
        self.check_zombie_collisions()
        self.check_plants()
        self.check_car_collisions()
        self.check_game_state()

    # ── no card recharge in survival ──────────────────────────────────────────

    def add_plant(self):
        """Place a plant then immediately clear all card cooldowns."""
        super().add_plant()
        # Reset every card's frozen timer so it is instantly usable again
        if hasattr(self, 'menubar') and hasattr(self.menubar, 'card_list'):
            for card in self.menubar.card_list:
                card.frozen_timer = -card.frozen_time

    # ── game state (survival never wins, only loses) ──────────────────────────

    def check_game_state(self):
        if not self.check_lose():
            return

        elapsed_ms = (self.current_time - self.survival_start_time
                      if self.survival_start_time else 0)

        score = (self.zombies_killed * 100 +
                 self.sun_collected  * 2   +
                 self.plants_planted * 10  +
                 (elapsed_ms // 1000) * 5)

        self.persist[c.ZOMBIES_KILLED]  = self.zombies_killed
        self.persist[c.SUN_COLLECTED]   = self.sun_collected
        self.persist[c.PLANTS_PLANTED]  = self.plants_planted
        self.persist[c.SURVIVAL_SCORE]  = score
        self.persist[c.SURVIVAL_TIME]   = elapsed_ms

        from ..states.user_select import save_survival_score, check_survival_beaten_users
        username = self.persist.get(c.CURRENT_USER, None)
        if username:
            is_best = save_survival_score(username, score, elapsed_ms)
            beaten  = check_survival_beaten_users(username, score)
        else:
            is_best = False
            beaten  = []

        self.persist[c.SURVIVAL_SCORE_IS_BEST] = is_best
        self.persist[c.SURVIVAL_BEATEN_USERS]  = beaten

        self.next = c.SURVIVAL_GAME_OVER
        self.done = True

    # ── update (override to fix pause-menu restart target) ────────────────────

    def update(self, surface, current_time, mouse_pos, mouse_click):
        self.current_time = self.game_info[c.CURRENT_TIME] = current_time

        # Pause menu
        if hasattr(self, 'pause_menu') and self.pause_menu.is_active:
            action = self.pause_menu.update(mouse_pos, mouse_click)
            if action:
                if action == "Back To Game":
                    self.pause_menu.is_active = False
                elif action == "Restart Level":
                    self.next = c.SURVIVAL       # restart survival, not adventure
                    self.done = True
                elif action == "Main Menu":
                    self.next = c.MAIN_MENU
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
        elif self.next == c.SURVIVAL_GAME_OVER:
            self.draw(surface)
            self.persist[c.LOSE_BACKGROUND] = surface.copy()

    # ── draw (add live HUD overlay) ───────────────────────────────────────────

    def draw(self, surface):
        super().draw(surface)

        if self.state != c.PLAY or self.survival_start_time is None:
            return

        elapsed_ms = self.current_time - self.survival_start_time
        total_s    = elapsed_ms // 1000
        mins       = total_s // 60
        secs       = total_s % 60
        time_str   = f"{mins}:{secs:02d}"

        live_score = (self.zombies_killed * 100 +
                      self.sun_collected  * 2   +
                      self.plants_planted * 10  +
                      total_s * 5)

        phase_name = ["Easy", "Easy", "Medium", "Hard",
                      "Hard", "Nightmare", "Nightmare"]
        phase_idx  = min(self.current_phase_index, len(phase_name) - 1)
        phase_label = phase_name[phase_idx]
        phase_colors = {
            "Easy":      (90, 220, 90),
            "Medium":    (255, 200, 50),
            "Hard":      (255, 130, 50),
            "Nightmare": (220, 60, 60),
        }
        phase_col = phase_colors.get(phase_label, (255, 255, 255))

        lines = [
            (f"Time:  {time_str}",         (255, 220, 60)),
            (f"Score: {live_score:,}",      (255, 255, 255)),
            (f"Wave:  {phase_label}",       phase_col),
        ]

        pad_x, pad_y = 8, 6
        line_h = self.hud_font.get_linesize() + 2
        box_w  = 148
        box_h  = pad_y * 2 + line_h * len(lines)
        bx     = c.SCREEN_WIDTH - box_w - 12
        by     = c.SCREEN_HEIGHT - box_h - 12

        bg = pg.Surface((box_w, box_h), pg.SRCALPHA)
        pg.draw.rect(bg, (0, 0, 0, 170), bg.get_rect(), border_radius=8)
        pg.draw.rect(bg, (80, 80, 0, 200), bg.get_rect(), 1, border_radius=8)
        surface.blit(bg, (bx, by))

        for i, (text, color) in enumerate(lines):
            surf = self.hud_font.render(text, True, color)
            shadow = self.hud_font.render(text, True, (0, 0, 0))
            tx = bx + pad_x
            ty = by + pad_y + i * line_h
            surface.blit(shadow, (tx + 1, ty + 1))
            surface.blit(surf,   (tx, ty))