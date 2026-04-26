__author__ = 'Rao Hamza Bilal'

import os

START_LEVEL_NUM = 1

ORIGINAL_CAPTION = 'Plant VS Zombies Game'

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

GRID_X_LEN = 9
GRID_Y_LEN = 5
GRID_X_SIZE = 80
GRID_Y_SIZE = 100


WHITE        = (255, 255, 255)
NAVYBLUE     = ( 60,  60, 100)
SKY_BLUE     = ( 39, 145, 251)
BLACK        = (  0,   0,   0)
LIGHTYELLOW  = (234, 233, 171)
RED          = (255,   0,   0)
PURPLE       = (255,   0, 255)
GOLD         = (255, 215,   0)
GREEN        = (  0, 255,   0)

SIZE_MULTIPLIER = 1.3

#GAME INFO DICTIONARY KEYS
CURRENT_TIME = 'current time'
LEVEL_NUM = 'level num'

#STATES FOR ENTIRE GAME
MAIN_MENU    = 'main menu'
LOAD_SCREEN  = 'load screen'
PAUSE_MENU   = 'pause menu'
GAME_LOSE    = 'game los'
GAME_VICTORY = 'game victory'
LEVEL        = 'level'
LEVEL_SELECT = 'level_select'
LEADERBOARD  = 'leaderboard'
SETTINGS     = 'settings'

MAX_LEVEL = 9   # levels 1-9 exist in the levels directory

# Score / leaderboard persist keys
LEVEL_SCORE        = 'level_score'
LEVEL_SCORE_IS_BEST = 'level_score_is_best'
BEATEN_USERS       = 'beaten_users'

MAIN_MENU_IMAGE = 'MainMenu'

PAUSE_MENU_IMAGE = 'PauseMenuBG'

# --- PROJECT PATHS ---
RESOURCE_DIR = 'resources'
GRAPHICS_DIR = os.path.join(RESOURCE_DIR, 'graphics')
FONTS_DIR = os.path.join(RESOURCE_DIR, 'fonts')
DATA_DIR = os.path.join('source', 'data')
LEVELS_DIR = os.path.join(DATA_DIR, 'levels')
ENTITIES_DIR = os.path.join(DATA_DIR, 'entities')

# --- GLOBAL TEXT STYLE ---
FONT_PATH = os.path.join(FONTS_DIR, 'DWARVESC.ttf')

# Colors
TEXT_COLOR_NORMAL = (255, 255, 255) # Pure White
TEXT_COLOR_HOVER = (0, 193, 33)     # Zombie Green (#00C121)

# MAIN MENU BUTTON IMAGES
ADVENTURE_IMAGE_IDLE = 'Adventure'
ADVENTURE_IMAGE_HOVER = 'Adventure_1'
MINIGAMES_IMAGE_IDLE = 'MINI_GAMES'
MINIGAMES_IMAGE_HOVER = 'MINI-GAMES_1'
PUZZLE_IMAGE_IDLE = 'PUZZLE'
PUZZLE_IMAGE_HOVER = 'PUZZLE_1'
SURVIVAL_IMAGE_IDLE = 'SURVIVAL'
SURVIVAL_IMAGE_HOVER = 'SURVIVAL_1'
OPTION_IMAGE_IDLE = 'OPTIONS'
OPTION_IMAGE_HOVER = 'OPTIONS_1'
QUIT_IMAGE_IDLE = 'QUIT'
QUIT_IMAGE_HOVER = 'QUIT_1'

OPTION_ADVENTURE = 'Adventure'
GAME_LOOSE_IMAGE = 'GameLoose'
GAME_LOOSE_X = 50
GAME_LOOSE_Y = 50
GAME_LOOSE_WIDTH = 680
GAME_LOOSE_HEIGHT = 490
GAME_LOOSE_BACKGROUND_COLOR = BLACK
GAME_LOOSE_BLUR_SCALE = 2
GAME_LOOSE_DIM_ALPHA = 30
GAME_VICTORY_IMAGE = 'GameVictory'
GAME_VICTORY_X = 50
GAME_VICTORY_Y = 50
GAME_VICTORY_WIDTH = 680
GAME_VICTORY_HEIGHT = 490
GAME_VICTORY_BACKGROUND_COLOR = BLACK
GAME_VICTORY_BLUR_SCALE = 2
GAME_VICTORY_DIM_ALPHA = 30
VICTORY_BACKGROUND = 'victory_background'
LOSE_BACKGROUND = 'lose_background'

#MAP COMPONENTS
BACKGROUND_NAME = 'Background'
BACKGROUND_TYPE = 'background_type'
INIT_SUN_NAME = 'init_sun_value'
ZOMBIE_LIST = 'zombie_list'

MAP_EMPTY = 0
MAP_EXIST = 1

BACKGROUND_OFFSET_X = 220
MAP_OFFSET_X = 35
MAP_OFFSET_Y = 100

#MENUBAR
CHOOSEBAR_TYPE = 'choosebar_type'
CHOOSEBAR_STATIC = 0
CHOOSEBAR_MOVE = 1
CHOSSEBAR_BOWLING = 2
MENUBAR_BACKGROUND = 'MenuButtonBG'
MOVEBAR_BACKGROUND = 'MoveBackground'
PANEL_BACKGROUND = 'PanelBackground'
START_BUTTON = 'StartButton'
CARD_POOL = 'card_pool'

MOVEBAR_CARD_FRESH_TIME = 6000
CARD_MOVE_TIME = 60

#PLANT INFO
PLANT_IMAGE_RECT = 'plant_image_rect'
CAR = 'car'
SUN = 'Sun'
SUNFLOWER = 'SunFlower'
PEASHOOTER = 'Peashooter'
SNOWPEASHOOTER = 'SnowPea'
WALLNUT = 'WallNut'
CHERRYBOMB = 'CherryBomb'
THREEPEASHOOTER = 'Threepeater'
REPEATERPEA = 'RepeaterPea'
CHOMPER = 'Chomper'
CHERRY_BOOM_IMAGE = 'Boom'
PUFFSHROOM = 'PuffShroom'
POTATOMINE = 'PotatoMine'
SQUASH = 'Squash'
SPIKEWEED = 'Spikeweed'
JALAPENO = 'Jalapeno'
SCAREDYSHROOM = 'ScaredyShroom'
SUNSHROOM = 'SunShroom'
ICESHROOM = 'IceShroom'
HYPNOSHROOM = 'HypnoShroom'
WALLNUTBOWLING = 'WallNutBowling'
REDWALLNUTBOWLING = 'RedWallNutBowling'

PLANT_HEALTH = 5
WALLNUT_HEALTH = 30
WALLNUT_CRACKED1_HEALTH = 20
WALLNUT_CRACKED2_HEALTH = 10
WALLNUT_BOWLING_DAMAGE = 10

PRODUCE_SUN_INTERVAL = 7000
FLOWER_SUN_INTERVAL = 22000
SUN_LIVE_TIME = 7000
SUN_VALUE = 50

ICE_SLOW_TIME = 2000

FREEZE_TIME = 7500
ICETRAP = 'IceTrap'

#PLANT CARD INFO
CARD_SUNFLOWER = 'card_sunflower'
CARD_PEASHOOTER = 'card_peashooter'
CARD_SNOWPEASHOOTER = 'card_snowpea'
CARD_WALLNUT = 'card_wallnut'
CARD_CHERRYBOMB = 'card_cherrybomb'
CARD_THREEPEASHOOTER = 'card_threepeashooter'
CARD_REPEATERPEA = 'card_repeaterpea'
CARD_CHOMPER = 'card_chomper'
CARD_PUFFSHROOM = 'card_puffshroom'
CARD_POTATOMINE = 'card_potatomine'
CARD_SQUASH = 'card_squash'
CARD_SPIKEWEED = 'card_spikeweed'
CARD_JALAPENO = 'card_jalapeno'
CARD_SCAREDYSHROOM = 'card_scaredyshroom'
CARD_SUNSHROOM = 'card_sunshroom'
CARD_ICESHROOM = 'card_iceshroom'
CARD_HYPNOSHROOM = 'card_hypnoshroom'
CARD_REDWALLNUT = 'card_redwallnut'

#BULLET INFO
BULLET_PEA = 'PeaNormal'
BULLET_PEA_ICE = 'PeaIce'
BULLET_MUSHROOM = 'BulletMushRoom'
BULLET_DAMAGE_NORMAL = 1

#ZOMBIE INFO
ZOMBIE_IMAGE_RECT = 'zombie_image_rect'
ZOMBIE_HEAD = 'ZombieHead'
NORMAL_ZOMBIE = 'Zombie'
CONEHEAD_ZOMBIE = 'ConeheadZombie'
BUCKETHEAD_ZOMBIE = 'BucketheadZombie'
FLAG_ZOMBIE = 'FlagZombie'
NEWSPAPER_ZOMBIE = 'NewspaperZombie'
BOOMDIE = 'BoomDie'

LOSTHEAD_HEALTH = 5
NORMAL_HEALTH = 10
FLAG_HEALTH = 15
CONEHEAD_HEALTH = 20
BUCKETHEAD_HEALTH = 30
NEWSPAPER_HEALTH = 15

ATTACK_INTERVAL = 1000
ZOMBIE_WALK_INTERVAL = 70

ZOMBIE_START_X = SCREEN_WIDTH + 50

#STATE
IDLE = 'idle'
FLY = 'fly'
EXPLODE = 'explode'
ATTACK = 'attack'
ATTACKED = 'attacked'
DIGEST = 'digest'
WALK = 'walk'
DIE = 'die'
CRY = 'cry'
FREEZE = 'freeze'
SLEEP = 'sleep'

#LEVEL STATE
CHOOSE = 'choose'
PLAY = 'play'

#BACKGROUND
BACKGROUND_DAY = 0
BACKGROUND_NIGHT = 1

# --- STATS TRACKING KEYS ---
ZOMBIES_KILLED = 'zombies_killed'
SUN_COLLECTED = 'sun_collected'
PLANTS_PLANTED = 'plants_planted'
STATS_FONT_PATH = os.path.join(FONTS_DIR, 'Fredoka-Bold.ttf')

# USER SYSTEM
USER_SELECT  = 'user_select'
CURRENT_USER = 'current_user'
SAVE_DATA_PATH = os.path.join(DATA_DIR, 'save_data.json')

# SHOVEL TOOL
SHOVEL      = 'Shovel'
SHOVEL_BANK = 'ShovelBank'

# SURVIVAL MODE STATES
SURVIVAL            = 'survival'
SURVIVAL_GAME_OVER  = 'survival_game_over'
SURVIVAL_LEADERBOARD = 'survival_leaderboard'

# SURVIVAL PERSIST KEYS
SURVIVAL_SCORE          = 'survival_score'
SURVIVAL_TIME           = 'survival_time'
SURVIVAL_SCORE_IS_BEST  = 'survival_score_is_best'
SURVIVAL_BEATEN_USERS   = 'survival_beaten_users'