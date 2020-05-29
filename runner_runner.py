import tkinter
from tkinter import *
import time
import random
import math
import pandas
from pandas import ExcelWriter
from pandas import ExcelFile
from PIL import Image, ImageTk

# CONSTANTS
TOP = tkinter.Tk()
CANVAS_WIDTH = 798
CANVAS_HEIGHT = 800
CANVAS = tkinter.Canvas(TOP, width=CANVAS_WIDTH + 1, height=CANVAS_HEIGHT + 1)

RUN_SPEED = 5
PLAYER_CENTER_X = 30
PLAYER_CENTER_Y = 30
SHIELD_ANGLE_SPEED = 60
SHIELD_X1_OFFSET = {'shield01': 0, 'shield02': 30, 'shield03': 30, 'shield04': 0}
SHIELD_Y1_OFFSET = {'shield01': -30, 'shield02': -30, 'shield03': -30, 'shield04': -30}
SHIELD_X2_OFFSET = {'shield01': 30, 'shield02': 30, 'shield03': 30, 'shield04': 30}
SHIELD_Y2_OFFSET = {'shield01': -30, 'shield02': -60, 'shield03': 0, 'shield04': -30}
SHIELD_X3_OFFSET = {'shield01': 30, 'shield02': 60, 'shield03': 60, 'shield04': 30}
SHIELD_Y3_OFFSET = {'shield01': -60, 'shield02': -30, 'shield03': -30, 'shield04': 0}

# ADJUSTS FREQUENCY OF PROJECTILE FIRING
CANNON_FIRE_MAX = {'ls': 8, 'rs': 8, 'tl': 5, 'tr': 5, 'bl': 12, 'br': 12}
CANNON_NAMES = ['ls', 'rs', 'tl', 'tr', 'bl', 'br']
CORNER_CANNON_ANGLE_MIN = {'tl': 271, 'tr': 179, 'bl': -1, 'br': 90}
CORNER_CANNON_ANGLE_MAX = {'tl': 360, 'tr': 270, 'bl': 90, 'br': 180}

# GLOBAL VARIABLES
FIRST_START = True
PLAYER_MOVE_X = 0
PLAYER_MOVE_Y = 0
SHIELD_ROT = 0
IMG_PLAYER = Image.open("images/player01_up_01.png")
IMG_RESIZE_WIDTH = 40
IMG_RESIZE_LENGTH = 50
UP_STEP = False
DOWN_STEP = False
LEFT_STEP = False
RIGHT_STEP = False


def main():
    # SETUP
    global PLAYER_MOVE_X
    global PLAYER_MOVE_Y
    global CANVAS
    global FIRST_START

    CANVAS = tkinter.Canvas(TOP, width=CANVAS_WIDTH + 1, height=CANVAS_HEIGHT + 1)
    CANVAS.pack()

    # FUNCTION VARIABLES

    # PLAYER & SHIELD VARIABLES
    player_curr_x = 400
    player_curr_y = 780
    player_shield_img = {}
    shield_avatar = {}
    img_shield = {'shield01': Image.open("images/shield_01.png"), 'shield02': Image.open("images/shield_02.png"),
                  'shield03': Image.open("images/shield_03.png"), 'shield04': Image.open("images/shield_04.png")}
    shield_hit_box = {}
    shield_destroyed = []

    # WALL/OBSTACLE VARIABLES
    wall_key = []
    wall_hb_x1 = {}
    wall_hb_y1 = {}
    wall_hb_x2 = {}
    wall_hb_y2 = {}
    wall_x = {}
    wall_y = {}
    wall_x_len = {}
    wall_y_len = {}
    wall_img = {}
    wall_hit_box = []

    cannon_bodies = {}
    cannon_vis_img = {}
    cannon_angle = {'ls': 0, 'rs': 180, 'tl': 360, 'tr': 180, 'bl': 0, 'br': 180}
    cannon_rot_img = {}
    cannon_img_x = {'ls': -50, 'rs': 750, 'tl': -50, 'tr': 750, 'bl': -50, 'br': 750}
    cannon_img_y = {'ls': 400, 'rs': 400, 'tl': 0, 'tr': 0, 'bl': 800, 'br': 800}
    side_cannon_speed_y = {'ls': 10, 'rs': -8}
    corner_cannon_angle_inc = {'tl': 1, 'tr': 1, 'bl': 2, 'br': 2}

    projectile_start_x1_const = {'ls': 30, 'rs': 750, 'tl': 0, 'tr': CANVAS_WIDTH, 'bl': 0, 'br': CANVAS_WIDTH}
    projectile_start_y1_const = {'ls': 0, 'rs': 0, 'tl': 0, 'tr': 0, 'bl': CANVAS_HEIGHT, 'br': CANVAS_HEIGHT}
    projectile_start_x2_const = {'ls': 40, 'rs': 760, 'tl': 10, 'tr': CANVAS_WIDTH-10, 'bl': 10, 'br': CANVAS_WIDTH-10}
    projectile_start_y2_const = {'ls': 10, 'rs': 10, 'tl': 10, 'tr': 10, 'bl': CANVAS_HEIGHT-10, 'br': CANVAS_HEIGHT-10}
    projectile_fire_direction_x = {'tl': 1, 'tr': -1, 'bl': 1, 'br': -1}
    projectile_fire_direction_y = {'tl': 1, 'tr': 1, 'bl': -1, 'br': -1}
    projectiles_ls = []
    projectiles_rs = []
    projectiles_tl = []
    projectiles_tr = []
    projectiles_bl = []
    projectiles_br = []
    cannon_projectiles = {'ls': projectiles_ls, 'rs': projectiles_rs, 'tl': projectiles_tl, 'tr': projectiles_tr,
                          'bl': projectiles_bl, 'br': projectiles_br}
    # PROJECTILE SPEED WHEN FIRED (X, Y)
    projectile_change_x = {'ls': 12, 'rs': -10, 'tl': 5, 'tr': -8, 'bl': 12, 'br': -10}
    projectile_change_y = {'ls': 0, 'rs': 0, 'tl': 5, 'tr': 8, 'bl': -12, 'br': -10}
    projectiles_dir_factor_tl = []
    projectiles_dir_factor_tr = []
    projectiles_dir_factor_bl = []
    projectiles_dir_factor_br = []
    projectile_slope_factor = {'tl': projectiles_dir_factor_tl, 'tr': projectiles_dir_factor_tr,
                               'bl': projectiles_dir_factor_bl, 'br': projectiles_dir_factor_br}

    # SETUP GAME WINDOW
    canvas_setup(CANVAS_WIDTH, CANVAS_HEIGHT, 'RUNNER! RUNNER!')

    # SET BACKGROUND IN SCENE
    background_img = create_background()
    CANVAS.create_image(0, 0, anchor='nw', image=background_img, tag='background')

    # SET EXIT LOCATION IN SCENE
    level_exit_img, level_exit_marker = create_level_exit()
    CANVAS.create_image(310, 180, anchor='sw', image=level_exit_img, tag='exit')
    CANVAS.create_image(350, 60, anchor='sw', image=level_exit_marker, tag='exit_marker')
    exit_hit_box = CANVAS.create_rectangle(350, 60, 375, 35, fill='', outline='', tag='exit_hit_box')

    # SET EXTRA BACKGROUND ASSETS IN SCENE
    north_forest_img, west_forest_img, east_forest_img = create_background_forest()
    CANVAS.create_image(0, 75, anchor='sw', image=north_forest_img, tag='forest_bg')
    CANVAS.create_image(-510, CANVAS_HEIGHT, anchor='sw', image=west_forest_img, tag='forest_bg')
    CANVAS.create_image(CANVAS_WIDTH + 500, CANVAS_HEIGHT, anchor='se', image=east_forest_img, tag='forest_bg')

    # SET WALL OBSTACLES
    wall_img, wall_key, wall_hb_x1, wall_hb_y1, wall_hb_x2, wall_hb_y2, wall_x, wall_y, wall_x_len, wall_y_len = \
        create_walls(wall_img, wall_key, wall_hb_x1, wall_hb_y1, wall_hb_x2, wall_hb_y2, wall_x, wall_y, wall_x_len,
                     wall_y_len)

    for key in wall_key:
        wall_hit_box.append(CANVAS.create_rectangle(wall_hb_x1[key], wall_hb_y1[key], wall_hb_x2[key], wall_hb_y2[key],
                                                    outline='', tag='wall'))
        CANVAS.create_image(wall_x[key], wall_y[key], anchor='sw', image=wall_img[key], tag='wall_avatar')

    # SET CANNON BODY LOCATIONS IN SCENE
    cannon_bodies = make_cannon_bodies(cannon_bodies)

    run = True

    while run:

        # AT GAME FIRST START UP, DISPLAYS START MENU TO PLAYER
        if FIRST_START:
            CANVAS.create_rectangle(100, 700, 700, 100, fill='white')

            pc01_img = Image.open("images/player_control_01.png")
            pc01_vis_img = ImageTk.PhotoImage(pc01_img.resize((200, 150)))
            CANVAS.create_image(250, 460, anchor='center', image=pc01_vis_img)

            pc02_img = Image.open("images/player_control_02.png")
            pc02_vis_img = ImageTk.PhotoImage(pc02_img.resize((200, 150)))
            CANVAS.create_image(550, 460, anchor='center', image=pc02_vis_img)

            sr01_img = Image.open("images/shield_rotation_01.png")
            sr01_vis_img = ImageTk.PhotoImage(sr01_img.resize((100, 90)))
            CANVAS.create_image(255, 615, anchor='center', image=sr01_vis_img)

            sr02_img = Image.open("images/shield_rotation_02.png")
            sr02_vis_img = ImageTk.PhotoImage(sr02_img.resize((100, 90)))
            CANVAS.create_image(555, 615, anchor='center', image=sr02_vis_img)

            start_menu("RUNNER! RUNNER!")
            FIRST_START = False
            break

        """
        ---PLAYER INTERACTIONS & MOVEMENT--
        1. PLACES PLAYER & SHIELD UPDATED LOCATION ON CANVAS PER USER INPUT
        2. CHECKS INTERACTION CONDITIONS: 
            1) PLAYER/PROJECTILE INTERACTION
            2) PLAYER REACHES EXIT MARKER
            3) PLAYER/WALL COLLISION
            4) PLAYER BEYOND CANVAS DIMENSIONS ==> STOPS PLAYER FROM MOVING BEYOND DIMENSIONS
        """
        # SET PLAYER AVATAR AND HIT/COLLISION BOX STARTUP LOCATION IN SCENE
        player_img, player_hit_box = create_player(player_curr_x, player_curr_y)
        player_avatar = CANVAS.create_image(player_curr_x, player_curr_y,
                                            anchor='sw', image=player_img, tag='player_avatar')
        # SET PLAYER PLASMA SHIELD
        player_shield_img.clear()
        shield_avatar.clear()

        player_shield_img, shield_hit_box = create_player_shield(img_shield, player_shield_img, shield_hit_box,
                                                                 shield_destroyed, player_curr_x, player_curr_y)
        for key in player_shield_img:
            shield_avatar[key] = CANVAS.create_image(player_curr_x - 10, player_curr_y + 10,
                                                     anchor='sw', image=player_shield_img[key], tag='shield_avatar')

        # CHECK IF PLAYER HIT BY PROJECTILE
        # GAME OVER IF PLAYER AND PROJECTILE OVERLAP
        if player_hit(player_hit_box):
            open_menu("GAME OVER")
            run = False

        # CHECK IF PLAYER REACHES EXIT MARKER
        # GAME OVER IF PLAYER AND EXIT MARKER OVERLAP - PLAYER WINS
        if player_win(player_hit_box):
            open_menu("YOU HAVE SUCCEEDED!")
            run = False

        # ADVANCES PLAYER BASED ON USER KEY INPUT
        CANVAS.move(player_avatar, PLAYER_MOVE_X, PLAYER_MOVE_Y)
        CANVAS.move(player_hit_box, PLAYER_MOVE_X, PLAYER_MOVE_Y)
        # player_prev_x = player_curr_x
        # player_prev_y = player_curr_y
        # print('player current y: ' + str(player_curr_y))
        # CHECK IF OBSTACLE IN PLAYER'S PATH
        if wall_blocking(player_hit_box):
            """
            move_player(player_avatar, player_hit_box, player_prev_x, player_prev_y, player_curr_x, player_curr_y)
            player_curr_x = CANVAS.coords(player_avatar)[0]
            player_curr_y = CANVAS.coords(player_avatar)[1]
            print('player current y adjusted: ' + str(player_curr_y))
            """
            PLAYER_MOVE_X *= -1
            PLAYER_MOVE_Y *= -1

        # CHECK IF PLAYER BEYOND SCENE BOUNDS
        if player_beyond_boundary(player_hit_box):
            PLAYER_MOVE_X *= -1
            PLAYER_MOVE_Y *= -1

        # OTHERWISE PLAYER FREE TO MOVE
        else:
            # UPDATE PLAYER MOVEMENT BASED ON KEY PRESSES
            CANVAS.move(player_avatar, PLAYER_MOVE_X, PLAYER_MOVE_Y)
            CANVAS.move(player_hit_box, PLAYER_MOVE_X, PLAYER_MOVE_Y)

            # UPDATE PLAYER CURRENT LOCATION TO ASSIGN WHEN AVATAR AND HIT BOX REDRAWN
            player_curr_x = CANVAS.coords(player_avatar)[0]
            player_curr_y = CANVAS.coords(player_avatar)[1]

        """
        ---PLASMA CANNON UPDATES---
        1. UPDATES CANNON MOVEMENTS AND ROTATIONS
        2. DETERMINES IF CANNONS WILL FIRE PROJECTILE (USES RANDOM LIBRARY)
        """
        # UPDATES CORNER CANNONS ANGLE POSITIONS IN SCENE
        # RECREATES IMAGE PER ANGLE CHANGE
        cannon_rot_img = create_cannons(CANNON_NAMES, cannon_rot_img, cannon_angle)

        # SET UPDATED LOCATIONS OF ALL CANNONS IN GAME
        for key in cannon_rot_img:
            cannon_vis_img[key] = CANVAS.create_image(cannon_img_x[key], cannon_img_y[key],
                                                      anchor='w', image=cannon_rot_img[key], tag='cannon')

        for key in cannon_angle:

            # IF SIDE CANNONS (LEFT OR RIGHT) UPDATES MOVEMENT
            if key == 'ls' or key == 'rs':
                # DETERMINE IF CANNONS ON LEFT (WEST) AND RIGHT (EAST) MOVING VERTICAL
                # DIRECTION TO CHANGE DIRECTION (UP OR DOWN ALONG CANVAS HEIGHT)
                if hit_bottom_cannon(cannon_bodies, key) or hit_top_cannon(cannon_bodies, key):
                    side_cannon_speed_y[key] *= -1

                # INCREMENTS LEFT AND RIGHT CANNON LOCATIONS IN VERTICAL (Y) DIRECTION
                CANVAS.move(cannon_bodies[key], 0, side_cannon_speed_y[key])
                CANVAS.move(cannon_vis_img[key], 0, side_cannon_speed_y[key])

                # UPDATE CURRENT LOCATION IN Y-DIRECTION FOR SETTING IMAGE ON CANVAS IN NEXT ITERATION
                cannon_img_y[key] = CANVAS.coords(cannon_vis_img[key])[1]

            else:
                # DETERMINE IF ROTATION DIRECTION CHANGES IF CANNON AT SCENE PERIMETER/BOUNDARY
                if hit_cannon_angle_bounds(cannon_angle, key):
                    corner_cannon_angle_inc[key] *= -1

                # INCREMENTS EACH CANNON ANGLE ROTATION
                cannon_angle[key] += corner_cannon_angle_inc[key]

            # DETERMINE IF CANNON WILL LAUNCH PROJECTILE (USES RANDOM LIBRARY)
            if cannon_fire_projectile(key):
                angle_deg = 0

                if key == 'ls' or key == 'rs':
                    curr_x = 0
                    curr_y = CANVAS.coords(cannon_vis_img[key])[1]
                else:
                    # cannon image length is 40 px (1/2 of image length)
                    if key == "tl":
                        angle_deg = 360 - cannon_angle[key]
                    elif key == "tr":
                        angle_deg = cannon_angle[key] - 180
                    elif key == "bl":
                        angle_deg = cannon_angle[key]
                    elif key == "br":
                        angle_deg = 180 - cannon_angle[key]

                    curr_x = projectile_fire_direction_x[key] * math.cos(math.radians(angle_deg)) * 40
                    curr_y = projectile_fire_direction_y[key] * math.sin(math.radians(angle_deg)) * 40

                    # FOR ROTATING CANNONS, FACTORS IN SLOPE SO PROJECTILE CONTINUES DIRECTION POINTED
                    projectile_slope_factor[key].append(curr_y / curr_x)

                cannon_projectiles[key].append(
                    CANVAS.create_oval(curr_x + projectile_start_x1_const[key],
                                       curr_y + projectile_start_y1_const[key],
                                       curr_x + projectile_start_x2_const[key],
                                       curr_y + projectile_start_y2_const[key],
                                       fill='alice blue', outline='deep sky blue', tag='projectile'))

            """
            ---PROJECTILE UPDATES PER ITERATION---
            ADVANCES PROJECTILE MOVEMENT
            CHECK CONDITIONS: 
            1)  PROJECTILE IN CANVAS DIMENSIONS ==> REMOVES PROJECTILE IF OUTSIDE BOUNDS
            2) PROJECTILE/WALL COLLISION ==> REMOVES PROJECTILE IF COLLISION OCCURS
            3) PROJECTILE/SHIELD COLLISION ==> REMOVES PROJECTILE AND SHIELD SECTION
            """
            # ITERATES OVER ALL CANNONS AND THEIR PROJECTILES ON SCREEN
            for projectile in cannon_projectiles[key][:]:

                # ADVANCE ALL PROJECTILES ON CANVAS
                if key == 'ls' or key == 'rs':
                    CANVAS.move(projectile, projectile_change_x[key], projectile_change_y[key])
                else:
                    CANVAS.move(projectile, projectile_change_x[key],
                            projectile_slope_factor[key][cannon_projectiles[key].index(projectile)]
                                * projectile_change_x[key])

                # 1. CHECK IF PLASMA PROJECTILE IS WITHIN CANVAS BOUNDARY (CANVAS WIDTH, CANVAS HEIGHT)
                # POP PROJECTILE IF OUTSIDE
                if projectile_beyond_scene_boundary(projectile):
                    if key == 'tl' or key == 'tr' or key == 'bl' or key == 'br':
                        projectile_slope_factor[key].pop(cannon_projectiles[key].index(projectile))
                    CANVAS.delete(cannon_projectiles[key].pop(cannon_projectiles[key].index(projectile)))

                # 2. CHECK IF PLASMA PROJECTILE COLLIDES WITH WALL
                # POP PROJECTILE IF RETURNS TRUE
                if projectile_hit_wall(cannon_projectiles[key]):
                    if key == 'tl' or key == 'tr' or key == 'bl' or key == 'br':
                        projectile_slope_factor[key].pop(cannon_projectiles[key].index(projectile))
                    CANVAS.delete(cannon_projectiles[key].pop(cannon_projectiles[key].index(projectile)))

                # 3. CHECK IF PLASMA SHIELD HIT BY PROJECTILE
                # POP BOTH PROJECTILE AND SHIELD SECTION IF RETURNS TRUE
                if projectile_hit_shield(cannon_projectiles[key]):
                    if len(shield_avatar) > 0:
                        for shield_part in shield_avatar:
                            # ASSIGN SHIELD NAME KEY TO shield_destroyed LIST to remove from dictionary
                            # shield_destroyed ALSO USED TO PREVENT MAKING DESTROYED SHIELD VISIBLE IN FUTURE ITERATIONS
                            # (CANNOT BE REMOVED WHILE ITERATING OVER DICTIONARY)
                            if len(CANVAS.coords(shield_avatar[shield_part])) != 0 and \
                                    shield_hit(shield_hit_box, shield_part, cannon_projectiles[key]):
                                shield_destroyed.append(shield_part)

                        # REMOVE SHIELD SECTION THAT HAS BEEN DESTROYED FROM shield_avatar dictionary
                        for shield in shield_destroyed:
                            if shield in shield_avatar:
                                # DELETES SHIELD SECTION FROM APPEARING ON CANVAS IN NEXT ITERATION USING POP
                                CANVAS.delete(shield_avatar.pop(shield))

                        # DELETES ASSOCIATED PROJECTILE CAUSES SHIELD SECTION REMOVAL
                        if key == 'tl' or key == 'tr' or key == 'bl' or key == 'br':
                            projectile_slope_factor[key].pop(cannon_projectiles[key].index(projectile))
                        CANVAS.delete(cannon_projectiles[key].pop(cannon_projectiles[key].index(projectile)))

        # REDRAW CANVAS
        CANVAS.update()

        # DELETE FROM CANVAS DUE TO UPDATED WILL BE REDRAWN (SAVE MEMORY)
        CANVAS.delete('player', 'player_avatar', 'shield_avatar', 'shield', 'shield_hit_box')

        # PAUSE
        time.sleep(1 / 60)

    # KEEP CANVAS OPEN FOR USER TO VIEW
    CANVAS.mainloop()


"""
---CREATE GAME ASSETS IN SCENE---
"""


# SETS BACKGROUND DRAWING
# USES AN IMAGE
def create_background():
    img_back = Image.open("images/background.png")
    resize_img_back = img_back.resize((CANVAS_WIDTH, CANVAS_HEIGHT))
    background_img = ImageTk.PhotoImage(resize_img_back)
    return background_img


def create_background_forest():
    img_north_forest = Image.open("images/forest01.png")
    img_west_forest = Image.open("images/forest02.png")
    img_east_forest = Image.open("images/forest03.png")
    resize_img_north = img_north_forest.resize((800, 600))
    resize_img_west = img_west_forest.resize((600, 800))
    resize_img_east = img_east_forest.resize((600, 800))

    return ImageTk.PhotoImage(resize_img_north), ImageTk.PhotoImage(resize_img_west), ImageTk.PhotoImage(
        resize_img_east)


def create_level_exit():
    img_exit_marker = Image.open("images/level_exit_marker.png")
    resize_img_emarker = img_exit_marker.resize((25, 50))
    img_exit = Image.open("images/level_exit_loc.png")
    resize_img_exit = img_exit.resize((100, 300))
    return ImageTk.PhotoImage(resize_img_exit), ImageTk.PhotoImage(resize_img_emarker)


# SETS WALLS THAT PLAYER AND PLASMA PROJECTILES INTERACT WITH
# IMPORTS WALL PROPERTIES AND COORDINATES FROM EXCEL FILE - REDIRECTS TO ANOTHER FUNCTION
def create_walls(wall_img, wall_key, wall_hb_x1, wall_hb_y1, wall_hb_x2, wall_hb_y2, wall_x, wall_y, wall_x_len,
                 wall_y_len):
    wall_key, wall_img_str, wall_hb_x1, wall_hb_y1, wall_hb_x2, wall_hb_y2, wall_x, wall_y, wall_x_len, wall_y_len \
        = load_wall_data(wall_key, wall_hb_x1, wall_hb_y1, wall_hb_x2, wall_hb_y2, wall_x, wall_y, wall_x_len,
                         wall_y_len)

    for key in wall_key:
        img_wall = Image.open(wall_img_str[key])
        wall_img[key] = (ImageTk.PhotoImage(img_wall.resize((wall_x_len[key], wall_y_len[key]))))

    return wall_img, wall_key, wall_hb_x1, wall_hb_y1, wall_hb_x2, wall_hb_y2, wall_x, wall_y, wall_x_len, wall_y_len


# IMPORTS WALL PROPERTIES FROM EXCEL FILE TO POSITION WALLS AVATAR AND WALL HIT BOX
# USES PANDAS LIBRARY
def load_wall_data(wall_key, wall_hb_x1, wall_hb_y1, wall_hb_x2, wall_hb_y2, wall_x, wall_y, wall_x_len, wall_y_len):
    wall_img_str = {}

    wall_info = pandas.read_excel('data/wall_data.xlsx', sheet_name='Properties')

    for i in wall_info.index:
        wall_key.append(wall_info['key'][i])
        wall_img_str[wall_key[i]] = wall_info['image'][i]
        wall_hb_x1[wall_key[i]] = wall_info['hit_box_x1'][i]
        wall_hb_y1[wall_key[i]] = wall_info['hit_box_y1'][i]
        wall_hb_x2[wall_key[i]] = wall_info['hit_box_x2'][i]
        wall_hb_y2[wall_key[i]] = wall_info['hit_box_y2'][i]
        wall_x[wall_key[i]] = wall_info['sw_x'][i]
        wall_y[wall_key[i]] = wall_info['sw_y'][i]
        wall_x_len[wall_key[i]] = wall_info['resize_x'][i]
        wall_y_len[wall_key[i]] = wall_info['resize_y'][i]
    return wall_key, wall_img_str, wall_hb_x1, wall_hb_y1, wall_hb_x2,wall_hb_y2, wall_x, wall_y, wall_x_len, wall_y_len


# CREATES PLAYER CHARACTER AVATAR
# USES AN IMAGE
def create_player(player_curr_x, player_curr_y):
    resize_img_player = IMG_PLAYER.resize((IMG_RESIZE_WIDTH, IMG_RESIZE_LENGTH))
    player_box_width = 35
    player_box_length = 35
    player_hit_box = CANVAS.create_rectangle(player_curr_x + 5, player_curr_y - 10,
                                             player_curr_x + player_box_width,
                                             player_curr_y - player_box_length, outline='', tag='player')
    return ImageTk.PhotoImage(resize_img_player), player_hit_box


# CREATES PLAYER CHARACTER'S PLASMA SHIELD
# USES AN IMAGE
# GETS REDRAWN EVERY TIME-STEP, THEREFORE, CHECKS IF SHIELD HIT BY PLASMA PROJECTILE.
# IF PLASMA SHIELD WAS HIT (WAS RECORDED IN shield_destroyed list) THEN DOES NOT GET REDRAWN IN IN CURRENT TIME-STEP.
def create_player_shield(img_shield, shield_img, shield_hit_box, shield_destroyed, player_curr_x, player_curr_y):
    for key in img_shield:
        if key in shield_destroyed:
            continue
        else:
            shield_img[key] = (ImageTk.PhotoImage(img_shield[key].resize((60, 60)).rotate(SHIELD_ROT,
                                                                                          center=(PLAYER_CENTER_X,
                                                                                                  PLAYER_CENTER_Y))))
            rot_x1_offset, rot_y1_offset, rot_x2_offset, rot_y2_offset, rot_x3_offset, rot_y3_offset = \
                shield_hit_box_rotation(SHIELD_X1_OFFSET[key], SHIELD_Y1_OFFSET[key], SHIELD_X2_OFFSET[key],
                                        SHIELD_Y2_OFFSET[key], SHIELD_X3_OFFSET[key], SHIELD_Y3_OFFSET[key])
            rot_x1 = (player_curr_x - 10) + rot_x1_offset
            rot_y1 = (player_curr_y - 50) + rot_y1_offset
            rot_x2 = (player_curr_x - 10) + rot_x2_offset
            rot_y2 = (player_curr_y - 50) + rot_y2_offset
            rot_x3 = (player_curr_x - 10) + rot_x3_offset
            rot_y3 = (player_curr_y - 50) + rot_y3_offset

            shield_hit_box[key] = CANVAS.create_polygon((rot_x1, rot_y1), (rot_x2, rot_y2), (rot_x3, rot_y3), fill='',
                                                        outline='', tag='shield_hit_box')

    return shield_img, shield_hit_box


def shield_hit_box_rotation(x1_os, y1_os, x2_os, y2_os, x3_os, y3_os):
    center_x = PLAYER_CENTER_X
    center_y = PLAYER_CENTER_Y
    x1_trans = x1_os - center_x
    x2_trans = x2_os - center_x
    x3_trans = x3_os - center_x
    y1_trans = -1 * y1_os - center_y
    y2_trans = -1 * y2_os - center_y
    y3_trans = -1 * y3_os - center_y

    rot_x1 = x1_trans * math.cos(math.radians(SHIELD_ROT)) - y1_trans * math.sin(math.radians(SHIELD_ROT))
    rot_y1 = y1_trans * math.cos(math.radians(SHIELD_ROT)) + x1_trans * math.sin(math.radians(SHIELD_ROT))
    rot_x2 = x2_trans * math.cos(math.radians(SHIELD_ROT)) - y2_trans * math.sin(math.radians(SHIELD_ROT))
    rot_y2 = y2_trans * math.cos(math.radians(SHIELD_ROT)) + x2_trans * math.sin(math.radians(SHIELD_ROT))
    rot_x3 = x3_trans * math.cos(math.radians(SHIELD_ROT)) - y3_trans * math.sin(math.radians(SHIELD_ROT))
    rot_y3 = y3_trans * math.cos(math.radians(SHIELD_ROT)) + x3_trans * math.sin(math.radians(SHIELD_ROT))

    new_x1 = center_x - (-1 * rot_x1)
    new_x2 = center_x - (-1 * rot_x2)
    new_x3 = center_x - (-1 * rot_x3)
    new_y1 = center_y - rot_y1
    new_y2 = center_y - rot_y2
    new_y3 = center_y - rot_y3

    return new_x1, new_y1, new_x2, new_y2, new_x3, new_y3


# CREATES PLASMA CANNON BODIES IN THE SCENE. (6) CANNONS TOTAL
# DRAWS GRAPHIC
# tl = TOP LEFT, tr = TOP RIGHT, bl = BOTTOM LEFT, br = BOTTOM RIGHT, ls = LEFT SIDE, rs = RIGHT SIDE
def make_cannon_bodies(cannon_bodies):
    cannon_bodies['tl'] = CANVAS.create_oval(-25, -25, 25, 25, fill="grey", tag='cannon')
    cannon_bodies['tr'] = CANVAS.create_oval(775, -25, 825, 25, fill="grey", tag='cannon')
    cannon_bodies['bl'] = CANVAS.create_oval(-25, 775, 25, 825, fill="grey", tag='cannon')
    cannon_bodies['br'] = CANVAS.create_oval(775, 775, 825, 825, fill="grey", tag='cannon')
    cannon_bodies['ls'] = CANVAS.create_oval(-25, 375, 25, 425, fill="grey", tag='cannon')
    cannon_bodies['rs'] = CANVAS.create_oval(775, 375, 825, 425, fill="grey", tag='cannon')

    return cannon_bodies


# CREATES ALL CANNONS (ls, rs, tl, tr, bl, br)
# USES AN IMAGE
# CORNER CANNONS WILL ROTATE ABOUT A CENTER POINT OR
# TRAVEL IN THE VERTICAL (Y-DIRECTION) IF CANNON LEFT (WEST) AND RIGHT (EAST)
def create_cannons(cannon_names, cannon_rot_img, cannon_angle):
    img = Image.open("images/cannon01.png")
    resize_cannon = img.resize((100, 100))

    for name in cannon_names:
        cannon_rot_img[name] = ImageTk.PhotoImage(resize_cannon.rotate(cannon_angle[name], center=(50, 50)))

    return cannon_rot_img


"""
---DEFINES PARAMETERS FOR CANNON MOVEMENTS---
CANNONS AT LEFT (WEST) AND RIGHT (EAST) WILL TRAVEL IN THE VERTICAL DIRECTION (Y-DIRECTION)
CANNONS AT THE SCENE CORNERS WILL ROTATE ABOUT CANNON CENTER POINT.
CANNONS WILL MOVE ONLY WITHIN THE SCENE, THEREFORE BOUND BY CANVAS SIZE (CANVAS_WIDTH, CANVAS_HEIGHT)
"""


# WHEN LEFT AND RIGHT CANNON REACH CORNER CANNONS AT BOTTOM OF CANVAS.
# PREVENTS CANNONS FROM OVERLAPPING.
def hit_bottom_cannon(cannon_bodies, key):
    # get moving cannon in y-direction bottom y coordinate
    cannonbody_bottom_y = CANVAS.coords(cannon_bodies[key])[3]

    # get top y-coordinate of bottom cannon
    if key == 'ls':
        bottom_cannon_top_y = CANVAS.coords(cannon_bodies['bl'])[1]
    if key == 'rs':
        bottom_cannon_top_y = CANVAS.coords(cannon_bodies['bl'])[1]

    return cannonbody_bottom_y > bottom_cannon_top_y


# WHEN LEFT AND RIGHT CANNON REACH CORNER CANNONS AT TOP OF CANVAS.
# PREVENTS CANNONS FROM OVERLAPPING.
def hit_top_cannon(cannon_bodies, key):
    cannonbody_top_y = CANVAS.coords(cannon_bodies[key])[1]

    if key == 'ls':
        top_cannon_bottom_y = CANVAS.coords(cannon_bodies['tl'])[3]
    if key == 'rs':
        top_cannon_bottom_y = CANVAS.coords(cannon_bodies['tr'])[3]
    return cannonbody_top_y < top_cannon_bottom_y


# CANNON TOP-LEFT (NORTH-WEST) THAT WILL ROTATE.
# CANVAS LIMITS IN CIRCLE ANGLE (DEGREE) TERMS
def hit_cannon_angle_bounds(corner_cannon_angle, key):

    return corner_cannon_angle[key] <= CORNER_CANNON_ANGLE_MIN[key] or \
           corner_cannon_angle[key] == CORNER_CANNON_ANGLE_MAX[key]


"""
---PLASMA CANNON PROJECTILE FIRING FREQUENCY---
SETS WHEN CANNON FIRES A PLASMA PROJECTILE.  USES RANDOM INT TO DETERMINE WHEN TO FIRE WHEN RETURNS A VALUE (2) WILL
FIRE.  TO MAKE CANNON  FIRE PROJECTILE MORE FREQUENTLY, REDUCE MAXIMUM RANGE
"""


# SETTING CORNER CANNONS AND SIDE CANNONS FIRING FREQUENCY
def cannon_fire_projectile(key):
    value = random.randint(0, CANNON_FIRE_MAX[key])
    if value == 2:
        return True
    else:
        return False


"""
----COLLISION CHECKS---
CHECKS OVERLAPPING OBJECTS IN SCENE AND VARIOUS ACTIONS TO BE TAKEN AS A RESULT
"""


# DETERMINES IF PLAYER HAS COLLIDED WITH EXIT MARKER
# COMPARES IF  PLAYER AND EXIT MARKER COORDINATES OVERLAP. IF OVERLAP ==> RETURNS TRUE
def player_win(player_hit_box):
    exit_marker = CANVAS.find_withtag('exit_hit_box')

    x1 = CANVAS.coords(player_hit_box)[0]
    y1 = CANVAS.coords(player_hit_box)[3]
    x2 = CANVAS.coords(player_hit_box)[2]
    y2 = CANVAS.coords(player_hit_box)[1]
    player_exit_hit = CANVAS.find_overlapping(x1, y1, x2, y2)

    for marker in exit_marker:
        if marker in player_exit_hit:
            return True

    return False


# DETERMINES IF PLAYER IS HIT WITH A PLASMA PROJECTILE.
# COMPARES IF PROJECTILE AND PLAYER HIT BOX COORDINATES OVERLAP.  IF OVERLAP ==> HIT OCCURS AND RETURNS TRUE
def player_hit(player_hit_box):
    projectile_objects = CANVAS.find_withtag('projectile')

    x1 = CANVAS.coords(player_hit_box)[0]
    y1 = CANVAS.coords(player_hit_box)[1]
    x2 = CANVAS.coords(player_hit_box)[2]
    y2 = CANVAS.coords(player_hit_box)[3]
    player_projectile_hit = CANVAS.find_overlapping(x1, y1, x2, y2)

    for projectile in projectile_objects:
        if projectile in player_projectile_hit:
            return True

    return False



# DETERMINES IF PLAYER SHIELD IS HIT WITH A PLASMA PROJECTILE.
def shield_hit(shield_hit_box, key, scene_projectiles):
    for projectile in scene_projectiles:
        x1 = CANVAS.coords(projectile)[0]
        y1 = CANVAS.coords(projectile)[1]
        x2 = CANVAS.coords(projectile)[2]
        y2 = CANVAS.coords(projectile)[3]

        collision = CANVAS.find_overlapping(x1, y1, x2, y2)

        if shield_hit_box[key] in collision:
            return True

    return False


# DETERMINES IF PLASMA PROJECTILE COLLIDES WITH WALL.
# COMPARES IF PROJECTILE AND WALL HIT BOX (TAGGED WITH WALL WHEN CREATED)
# COORDINATES OVERLAP.  IF OVERLAP ==> COLLISION OCCURS AND RETURNS TRUE
def projectile_hit_wall(scene_projectiles):
    all_walls = CANVAS.find_withtag('wall')

    for projectile in scene_projectiles:
        x1 = CANVAS.coords(projectile)[0]
        y1 = CANVAS.coords(projectile)[1]
        x2 = CANVAS.coords(projectile)[2]
        y2 = CANVAS.coords(projectile)[3]

        collision = CANVAS.find_overlapping(x1, y1, x2, y2)

        for wall in all_walls:
            if wall in collision:
                return True

    return False


# DETERMINES IF PLASMA PROJECTILE COLLIDES WITH PLAYER PLASMA SHIELD.
# COMPARES IF PROJECTILE AND PLASMA SHIELD (TAGGED WITH WALL WHEN CREATED)
# COORDINATES OVERLAP.  IF OVERLAP ==> COLLISION OCCURS AND RETURNS TRUE
def projectile_hit_shield(scene_projectiles):
    shield_in_scene = CANVAS.find_withtag('shield_hit_box')

    for projectile in scene_projectiles:
        x1 = CANVAS.coords(projectile)[0]
        y1 = CANVAS.coords(projectile)[1]
        x2 = CANVAS.coords(projectile)[2]
        y2 = CANVAS.coords(projectile)[3]

        collision = CANVAS.find_overlapping(x1, y1, x2, y2)

        for shield in shield_in_scene:
            if shield in collision:
                return True

    return False


# DETERMINES IF PLAYER COLLIDES WITH WALL.
# COMPARES IF PLAYER AND WALL HIT BOX (TAGGED WITH 'WALL' WHEN CREATED)
# COORDINATES OVERLAP.  IF OVERLAP ==> COLLISION OCCURS AND RETURNS TRUE
def wall_blocking(player_hit_box):
    all_walls = CANVAS.find_withtag('wall')

    player_x1 = CANVAS.coords(player_hit_box)[0]
    player_y1 = CANVAS.coords(player_hit_box)[1]
    player_x2 = CANVAS.coords(player_hit_box)[2]
    player_y2 = CANVAS.coords(player_hit_box)[3]
    collision = CANVAS.find_overlapping(player_x1, player_y1, player_x2, player_y2)

    for wall in all_walls:
        if wall in collision:
            return True

    return False


"""
def move_player(player_avatar, player_hit_box, player_prev_x, player_prev_y, player_curr_x, player_curr_y):
    all_walls = CANVAS.find_withtag('wall')

    player_x1 = CANVAS.coords(player_hit_box)[0]
    player_y1 = CANVAS.coords(player_hit_box)[1]
    player_x2 = CANVAS.coords(player_hit_box)[2]
    player_y2 = CANVAS.coords(player_hit_box)[3]
    collision = CANVAS.find_overlapping(player_x1, player_y1, player_x2, player_y2)
    print(player_curr_x, player_y1, player_x2, player_y2)
    print(player_prev_x)
    for wall in all_walls:
        if wall in collision:
            wall_x1 = CANVAS.coords(wall)[0]
            wall_y1 = CANVAS.coords(wall)[1]
            wall_x2 = CANVAS.coords(wall)[2]
            wall_y2 = CANVAS.coords(wall)[3]
            print(wall_x1, wall_y1, wall_x2, wall_y2)

            # CHECK IF NORTH BLOCKED
            if wall_x1 <= player_x1 <= wall_x2 and wall_y1 <= player_y1 <= wall_y2:
                player_curr_y = wall_y2 + 1
                CANVAS.moveto(player_hit_box, player_curr_x, player_curr_y)
                CANVAS.moveto(player_avatar, player_curr_x, player_curr_y)
                print("NORTH 1")
                # print(player_x1, player_y1, player_x2, player_y2)

            elif wall_x1 <= player_x2 <= wall_x2 and wall_y1 <= player_y1 <= wall_y2:
                player_curr_y = wall_y2 + 1
                CANVAS.moveto(player_hit_box, player_curr_x, player_curr_y)
                CANVAS.moveto(player_avatar, player_x1, player_curr_y)
                print("NORTH 2")
                # print(player_x1, player_y1, player_curr_x, player_y2)

            # CHECK IF SOUTH BLOCKED
            if wall_x1 <= player_x1 <= wall_x2 and wall_y1 <= player_y2 <= wall_y2:
                player_y2 = wall_y1 - 3
                print(player_y2)
                player_y1 = player_y2 - 35
                CANVAS.moveto(player_hit_box, player_x1, player_y2)
                CANVAS.moveto(player_avatar, player_x1, player_y2)
                print("SOUTH 1")
                print(player_x1, player_y1, player_x2, player_y2)
            elif wall_x1 <= player_x2 <= wall_x2 and wall_y1 <= player_y2 <= wall_y2:
                player_y2 = wall_y1 - 3
                print(player_y2)
                player_y1 = player_y2 - 35
                CANVAS.moveto(player_hit_box, player_x1, player_y2)
                CANVAS.moveto(player_avatar, player_x1, player_y2)
                print("SOUTH 2")
                print(player_x1, player_y1, player_x2, player_y2)


            # CHECK WEST BLOCKED
            elif wall_x1 <= player_x1 <= wall_x2 and wall_y2 <= player_y2 <= wall_y1:
                CANVAS.moveto(player_hit_box, wall_x2 + 2, player_curr_y)
                CANVAS.moveto(player_avatar, wall_x2 + 2, player_curr_y)
                print("WEST 1")
            elif wall_x1 <= player_x1 <= wall_x2 and wall_y2 <= player_y1 <= wall_y1:
                CANVAS.moveto(player_hit_box, wall_x2 + 2, player_curr_y)
                CANVAS.moveto(player_avatar, wall_x2 + 2, player_curr_y)
                print("WEST 2")

            # CHECK EAST BLOCKED
            elif wall_x1 <= player_x2 <= wall_x2 and wall_y2 <= player_y2 <= wall_y1:
                CANVAS.moveto(player_hit_box, wall_x1 - 2, player_curr_y)
                CANVAS.moveto(player_avatar, wall_x1 - 2, player_curr_y)
                print("EAST 1")
            elif wall_x1 <= player_x2 <= wall_x2 and wall_y2 <= player_y1 <= wall_y1:
                CANVAS.moveto(player_hit_box, wall_x1 - 2, player_curr_y)
                CANVAS.moveto(player_avatar, wall_x1 - 2, player_curr_y)
                print("EAST 2")
    """


# DETERMINES IF PLAYER COLLIDES WITH SET SCENE PERIMETER/PLAY BOUNDARY.
# COMPARES IF PLAYER COORDINATES FALL BEYOND DEFINED SCENE COORDINATES. IF OVERLAP ==> COLLISION OCCURS AND RETURNS TRUE
def player_beyond_boundary(player_hit_box):
    player_x1 = CANVAS.coords(player_hit_box)[0]
    player_y1 = CANVAS.coords(player_hit_box)[3]
    player_x2 = CANVAS.coords(player_hit_box)[2]
    player_y2 = CANVAS.coords(player_hit_box)[1]

    if player_x1 <= 50 or player_x2 >= CANVAS_WIDTH - 50:
        return True
    if player_y2 <= 10 or player_y1 >= CANVAS_HEIGHT - 10:
        return True

    return False


def projectile_beyond_scene_boundary(projectile):
    if CANVAS.coords(projectile)[0] > CANVAS_WIDTH or CANVAS.coords(projectile)[0] < 0 \
            or CANVAS.coords(projectile)[0] > CANVAS_HEIGHT or CANVAS.coords(projectile)[0] < 0:
        return True

    return False


"""
---USER CONTROL---
SET OF FUNCTIONS BINDING USER INPUT COMMANDS WITH UI
"""


# DEFINES KEYBOARD KEYS BOUND TO PLAYER MOVEMENT IN GAME
def key_pressed(event):
    global PLAYER_MOVE_X
    global PLAYER_MOVE_Y
    global IMG_PLAYER
    global IMG_RESIZE_WIDTH
    global IMG_RESIZE_LENGTH
    global UP_STEP
    global DOWN_STEP
    global LEFT_STEP
    global RIGHT_STEP
    global SHIELD_ROT

    if event.keysym == 'a' or event.keysym == 'A' or event.keysym == 'Left':
        PLAYER_MOVE_X = -1 * RUN_SPEED
        PLAYER_MOVE_Y = 0
        IMG_RESIZE_WIDTH = 50
        IMG_RESIZE_LENGTH = 40

        if LEFT_STEP:
            IMG_PLAYER = Image.open("images/player01_left_01.png")
            LEFT_STEP = False
        else:
            IMG_PLAYER = Image.open("images/player01_left_02.png")
            LEFT_STEP = True

    if event.keysym == 'd' or event.keysym == 'D' or event.keysym == 'Right':
        PLAYER_MOVE_X = RUN_SPEED
        PLAYER_MOVE_Y = 0
        IMG_RESIZE_WIDTH = 50
        IMG_RESIZE_LENGTH = 40

        if RIGHT_STEP:
            IMG_PLAYER = Image.open("images/player01_right_01.png")
            RIGHT_STEP = False
        else:
            IMG_PLAYER = Image.open("images/player01_right_02.png")
            RIGHT_STEP = True

    if event.keysym == 'w' or event.keysym == 'W' or event.keysym == 'Up':
        PLAYER_MOVE_X = 0
        PLAYER_MOVE_Y = -1 * RUN_SPEED
        IMG_RESIZE_WIDTH = 40
        IMG_RESIZE_LENGTH = 50

        if UP_STEP:
            IMG_PLAYER = Image.open("images/player01_up_01.png")
            UP_STEP = False
        else:
            IMG_PLAYER = Image.open("images/player01_up_02.png")
            UP_STEP = True

    if event.keysym == 's' or event.keysym == 'S' or event.keysym == 'Down':
        PLAYER_MOVE_X = 0
        PLAYER_MOVE_Y = RUN_SPEED
        IMG_RESIZE_WIDTH = 40
        IMG_RESIZE_LENGTH = 50

        if DOWN_STEP:
            IMG_PLAYER = Image.open("images/player01_down_01.png")
            DOWN_STEP = False
        else:
            IMG_PLAYER = Image.open("images/player01_down_02.png")
            DOWN_STEP = True

    if event.keysym == 'v' or event.keysym == 'V' or event.keysym == 'm' or event.keysym == 'M':
        SHIELD_ROT -= SHIELD_ANGLE_SPEED

    if event.keysym == 'c' or event.keysym == 'C' or event.keysym == 'n' or event.keysym == 'N':
        SHIELD_ROT += SHIELD_ANGLE_SPEED

    if event.keysym == 'Escape':
        open_menu("QUIT GAME?")


# PLAYER ACTION FOR WHEN KEYBOARD KEYS ARE RELEASED.  PLAYER STOPS MOVING
def key_released(event):
    global PLAYER_MOVE_X
    global PLAYER_MOVE_Y

    PLAYER_MOVE_X = 0
    PLAYER_MOVE_Y = 0


def start_menu(msg):
    CANVAS.create_rectangle(150, 300, 650, 175, fill='', outline='black')
    CANVAS.create_rectangle(150, 675, 650, 325, fill='', outline='black')

    start_label = Label(CANVAS, text=msg, font='arial', bg='white')
    start_label.place(x=400, y=175, anchor='center')

    instructions_label = Label(CANVAS, text="PLAYER CONTROLS:", bg='white')
    instructions_label.config(font=("arial bold", 12))
    instructions_label.place(x=400, y=325, anchor='center')

    nav_label = Label(CANVAS, text="NAVIGATION", bg='white')
    nav_label.config(font=('arial', 10))
    nav_label.place(x=400, y=375, anchor='center')

    shield_label = Label(CANVAS, text="PLASMA SHIELD ORIENTATION", bg='white')
    shield_label.config(font=('arial', 10))
    shield_label.place(x=400, y=555, anchor='center')

    button_play = Button(CANVAS, text="Play", padx=10, pady=5, command=start_game)
    button_play.place(x=300, y=235, anchor='center')

    button_close = Button(CANVAS, text="Close", padx=10, pady=5, command=TOP.destroy)
    button_close.place(x=500, y=235, anchor='center')


def open_menu(msg):
    CANVAS.create_rectangle(200, 500, 600, 200, fill='white')

    go_label = Label(CANVAS, text=msg, font='arial', bg='white')
    go_label.place(x=400, y=300, anchor='center')

    button_close = Button(CANVAS, text="Close Game", padx=10, pady=5, command=TOP.destroy)
    button_close.place(x=300, y=400, anchor='center')

    button_restart = Button(CANVAS, text="Play Again", padx=10, pady=5, command=restart_game)
    button_restart.place(x=500, y=400, anchor='center')


def start_game():
    CANVAS.pack_forget()
    main()


def restart_game():
    CANVAS.pack_forget()
    main()


def canvas_setup(width, height, title):
    """
    SETUP CANVAS PROPERTIES AND USER INTERACTION
    """
    TOP.minsize(width=width, height=height)
    TOP.title(title)
    TOP.bind_all('<KeyPress>', key_pressed)
    TOP.bind_all('<KeyRelease>', key_released)

    return


if __name__ == '__main__':
    main()