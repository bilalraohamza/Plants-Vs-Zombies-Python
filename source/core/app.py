__author__ = 'Rao Hamza Bilal'

from . import constants as c
from . import engine
from ..states import level, main_menu, pause_menu, screens, user_select
from ..states import level_select, leaderboard, settings
from ..states import survival
from ..states import survival_screens

def run():
    game = engine.Control()
    state_dict = {
        c.USER_SELECT:          user_select.UserSelectScreen(),
        c.MAIN_MENU:            main_menu.Menu(),
        c.LOAD_SCREEN:          screens.LoadScreen(),
        c.GAME_VICTORY:         screens.GameVictoryScreen(),
        c.GAME_LOSE:            screens.GameLoseScreen(),
        c.LEVEL:                level.Level(),
        c.PAUSE_MENU:           pause_menu.PauseMenu(),
        c.LEVEL_SELECT:         level_select.LevelSelect(),
        c.LEADERBOARD:          leaderboard.Leaderboard(),
        c.SETTINGS:             settings.Settings(),
        c.SURVIVAL:             survival.SurvivalLevel(),
        c.SURVIVAL_GAME_OVER:   survival_screens.SurvivalGameOverScreen(),
        c.SURVIVAL_LEADERBOARD: survival_screens.SurvivalLeaderboard(),
    }
    game.setup_states(state_dict, c.LOAD_SCREEN)
    game.main()


def main():
    """Backward-compatible alias for older imports."""
    run()