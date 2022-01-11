import pygame
import gamebox
import numpy as np
import random
width = 800
height = 600
fps = 60
n = 0 #index for pacman's image
player_speed = 1 #pacman's speed
camera = gamebox.Camera(width,height)
pacman_images = [gamebox.load_sprite_sheet('mouth_open.png',1,1)[0], gamebox.load_sprite_sheet('mouth_closed.png', 1,1)[0]]
pacman = gamebox.from_image(402, 250, pacman_images[n])
pacman_scale_factor = 1.8
pacman.scale_by(pacman_scale_factor)
target_angle = 0
pacman.rotate(180)
pacman.speedx = 1
pacman_center = gamebox.from_color(pacman.x, pacman.y, 'red', 1,1)
pacman_center.speedx = 1
angle = 0 #pacman's angle
game_started = False
game_over = False
mouth_open = True
ghosts_active = 0
pacman_speed = 1
ghost_speed = 1
score = 0
ticker = 0
walls = []
tracks = []
feelers = []
dots = []

#making the ghosts
ghost_images = gamebox.load_sprite_sheet('ghosts.png',2,2)

g1 = gamebox.from_image(width/2 - 15, height/2 + 10, ghost_images[0])
g2 = gamebox.from_image(width/2 - 15, height/2 - 13, ghost_images[1])
g3 = gamebox.from_image(width/2 + 15, height/2 - 13, ghost_images[2])
g4 = gamebox.from_image(width/2 + 15, height/2 + 10, ghost_images[3])

ghosts = [g1, g2, g3 ,g4]
for ghost in ghosts:
    ghost.scale_by(0.2) 
    ghost.in_box = True
    ghost.feelers = []
    ghost.c = gamebox.from_color(ghost.x, ghost.y, 'red', 1,1)
    ghost.feelers.append(gamebox.from_color(ghost.c.x, ghost.c.y - 1, 'red', 1,1)) #top
    ghost.feelers.append(gamebox.from_color(ghost.c.x + 1, ghost.c.y, 'red', 1,1)) #right
    ghost.feelers.append(gamebox.from_color(ghost.c.x, ghost.c.y + 1, 'red', 1,1)) #bottom
    ghost.feelers.append(gamebox.from_color(ghost.c.x - 1, ghost.c.y, 'red', 1,1)) #left

def set_g_speed(ghost, v_x, v_y):
    ghost.speedy = v_y
    ghost.c.speedy = v_y
    ghost.speedx = v_x
    ghost.c.speedx = v_x
    for feeler in ghost.feelers:
        feeler.speedx = v_x
        feeler.speedy = v_y
def move_ghost(ghost):
    global target_angle, current_track, angle
    if not ghost.in_box:
        ghost.move_speed()
        ghost.c.move_speed()
        ghost.feelers[0].move_speed()
        ghost.feelers[1].move_speed()
        ghost.feelers[2].move_speed()
        ghost.feelers[3].move_speed()
        candidates = find_touching_tracks(ghost.current_track)
        if (ghost.speedx != 0 and (not ghost.feelers[1].touches(ghost.current_track) or not ghost.feelers[3].touches(ghost.current_track))) or (ghost.speedy != 0 and (not ghost.feelers[0].touches(ghost.current_track) or not ghost.feelers[2].touches(ghost.current_track))):
            can_turn = [-1, -1, -1, -1] #up, right, down, left
            for c in candidates:
                if ghost.feelers[0].touches(c) and c != ghost.current_track:
                    can_turn[0] = 0
                if ghost.feelers[1].touches(c) and c != ghost.current_track:
                    can_turn[1] = 1
                if ghost.feelers[2].touches(c) and c != ghost.current_track:
                    can_turn[2] = 2
                if ghost.feelers[3].touches(c) and c != ghost.current_track:
                    can_turn[3] = 3
            direction = random.choice(can_turn)
            if sum(can_turn) > -4:
                while direction < 0:
                    direction = random.choice(can_turn)
            if direction == 0:
                set_g_speed(ghost,0,-ghost_speed)
            elif direction == 1:
                set_g_speed(ghost,ghost_speed,0)
            elif direction == 2:
                set_g_speed(ghost,0,ghost_speed)
            elif direction == 3:
                set_g_speed(ghost,-ghost_speed, 0)
            for track in candidates:
                if ghost.c.touches(track):
                    ghost.current_track = track
            for wall in walls:
                if ghost.touches(wall):
                    if ghost.speedx != 0:
                        set_g_speed(ghost,-ghost.speedx,0)
                    if ghost.speedy != 0:
                        set_g_speed(ghost,0,-ghost.speedy)

            
feelers.append(gamebox.from_color(pacman_center.x, pacman_center.y - 1, 'red', 1,1)) #top
feelers.append(gamebox.from_color(pacman_center.x + 1, pacman_center.y, 'red', 1,1)) #right
feelers.append(gamebox.from_color(pacman_center.x, pacman_center.y + 1, 'red', 1,1)) #bottom
feelers.append(gamebox.from_color(pacman_center.x - 1, pacman_center.y, 'red', 1,1)) #left
for feeler in feelers:
    feeler.speedx = 1

target_angle = 0
def set_speeds(xspeed, yspeed):
    global pacman, pacman_center
    pacman.speedy = yspeed
    pacman_center.speedy = yspeed
    pacman.speedx = xspeed
    pacman_center.speedx = xspeed
    for feeler in feelers:
        feeler.speedx = xspeed
        feeler.speedy = yspeed

def move_pacman(keys):
    global target_angle, angle, current_track,pacman, mouth_open
    pacman.move_speed()
    pacman_center.move_speed()
    if pacman.speedx > 0 and angle != 0:
        pacman.rotate(0-angle)
        angle = 0
    if pacman.speedx < 0 and angle != 180:
        pacman.rotate(180-angle)
        angle = 180
    if pacman.speedy > 0 and angle != 270:
        pacman.rotate(270-angle)
        angle = 270 
    if pacman.speedy < 0 and angle != 90:
        pacman.rotate(90-angle)
        angle = 90
    for feeler in feelers:
        feeler.move_speed()
    if pacman_center.x > 637:
        pacman.x = 177
        pacman_center.x = 177
        feelers[0].x = 177
        feelers[2].x = 177
        feelers[1].x = 178
        feelers[3].x = 176
        set_speeds(pacman_speed, 0)
        current_track = tracks[4]
    if pacman_center.x < 177:
        pacman_center.x = 637
        pacman.x = 637
        feelers[0].x = 637
        feelers[2].x = 637
        feelers[1].x = 638
        feelers[3].x = 636
        set_speeds(-pacman_speed, 0)
        current_track = tracks[-1]
    if ticker % 10 == 0:
        if mouth_open:
            pacman.image = pacman_images[1]
            mouth_open = False
        else:
            pacman.image = pacman_images[0]
            mouth_open = True



def find_center(x,y, w,h):
    """
    Given the coordinates of the bottom left-hand corner of a gamebox
    x,y and the dimensions width w and height h, returns the
    coordinates of the center
    """
    A = np.array([[1,0,0.5*w], [0,1,-0.5*h]])
    v = np.array([[x],[y],[1]])
    c = np.dot(A,v)
    return (c[0,0], c[1,0])

#Making the maze
color = (69,66,153)
def make_walls():
    w, h = 450, 10
    left_edge = 178
    bottom_edge = 562
    x, y = find_center(178, 562, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 10, 190
    x,y = find_center(left_edge, bottom_edge, w, h)
    walls.append(gamebox.from_color(x,y, color,w,h ))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 85, 10
    x,y = find_center(left_edge, bottom_edge - 185, w,h)
    walls.append(gamebox.from_color(x,y, color, w,h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 10, 60
    x,y = find_center(left_edge + 78, bottom_edge - 185, w, h)
    walls.append(gamebox.from_color(x,y,color, w,h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 88, 10
    x,y = find_center(left_edge, bottom_edge - 240, w,h)
    walls.append(gamebox.from_color(x,y, color, w,h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 16, 65
    x,y = find_center(297,376, w,h)
    walls.append(gamebox.from_color(x,y, color, w,h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 16, 65
    x,y = find_center(488, 376, w,h)
    walls.append(gamebox.from_color(x,y, color, w,h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 39, 16
    x,y = find_center(179, 472, w,h)
    walls.append(gamebox.from_color(x,y, color, w,h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 88, 10
    x,y = find_center(176, 282, w,h)
    walls.append(gamebox.from_color(x,y, color, w,h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 11, 65
    x,y = find_center(258, 282, w,h)
    walls.append(gamebox.from_color(x,y, color, w,h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 92, 10
    x,y = find_center(176, 224, w,h)
    walls.append(gamebox.from_color(x,y, color, w,h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 10, 162
    x,y = find_center(176, 224, w,h)
    walls.append(gamebox.from_color(x,y, color, w,h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 450, 10
    x, y = find_center(178, 72, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 50, 33
    x, y = find_center(217, 137, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 50, 17
    x, y = find_center(217, 185, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 65, 33
    x, y = find_center(297, 137, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 17, 114
    x, y = find_center(297, 282, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 48, 18
    x, y = find_center(314, 234, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 65, 18
    x, y = find_center(297, 426, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 49, 18
    x, y = find_center(217, 426, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 17, 64
    x, y = find_center(249, 474, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 145, 18
    x, y = find_center(217, 522, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 16, 51
    x, y = find_center(297, 507, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 113, 18
    x, y = find_center(345, 474, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 17, 51
    x, y = find_center(393, 522, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 113, 18
    x, y = find_center(345, 376, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 17, 51
    x, y = find_center(393, 427, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 113, 18
    x, y = find_center(345, 186, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 17, 51
    x, y = find_center(393, 234, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 17, 71
    x, y = find_center(393, 138, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 9, 60
    x, y = find_center(345, 329, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 113, 9
    x, y = find_center(345, 329, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 9, 65
    x, y = find_center(450, 329, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x + 2
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 43, 9
    x, y = find_center(343, 273, w,h)
    walls.append(gamebox.from_color(x, y, color, w, h))
    x = width - x 
    walls.append(gamebox.from_color(x,y, color, w,h))

    w, h = 30, 10
    x, y = find_center(386, 274, w,h)
    walls.append(gamebox.from_color(x, y, 'white', w, h))
make_walls()

def append_dots(spacing, length, x_0, y_0, v = False):
    global dots
    if not v:
        for i in range(0,length, spacing):
            w,h = 3,3
            x,y = find_center(x_0 + i, y_0, w,h)
            dots.append(gamebox.from_color(x,y,'white',w,h))
    if v:
        for i in range(0,length, spacing):
            w,h = 3,3
            x,y = find_center(x_0, y_0 - i, w,h)
            dots.append(gamebox.from_color(x,y,'white',w,h)) 
def collide_with_dots():
    global score, dots
    for dot in dots:
        if pacman_center.touches(dot, 10,10):
            dots.remove(dot)
            score += 10
            
        
def find_dist(d1,d2):
    x_i = d1.x
    x_j = d2.x
    y_i = d1.y
    y_j = d2.y

    return (np.abs(x_i - x_j)**2 + np.abs(y_i - y_j)**2)**(1/2)
color = 'white'
def make_tracks():
    w, h = 142, 1
    x, y = find_center(331, 251, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 331, 251)


    w, h = 1, 140
    x, y = find_center(331, 391, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 331, 391, v = True)

   
    w, h = 1, 140
    x, y = find_center(472, 391, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 472, 391, v = True)

    w, h = 141, 1
    x, y = find_center(332, 344, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 332, 344)


    w, h = 174, 1
    x, y = find_center(158, 299, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w - 20, 180, 299, v = False)

    w, h = 172, 1
    x, y = find_center(204, 392, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 204, 392, v = False)
    x = width - x + 4
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, 1, 473, 299, v = False)

    w, h = 1, 49
    x, y = find_center(204, 441, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h , 204, 441, v = True)
    x = width - x + 4
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 600, 441, v = True)

    w, h = 29, 1
    x, y = find_center(204, 442, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w + 5, 204, 442, v = False)
    x = width - x + 4
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 569, 442, v = False)

    w, h = 1, 47
    x, y = find_center(233, 488, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 233, 488, v = True)
    x = width - x + 4
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 233, 488, v = True)

    w, h = 78, 1
    x, y = find_center(203, 488, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 203, 488, v = False)
    x = width - x + 2
    tracks.append(gamebox.from_color(x,y,color,82,h))
    append_dots(10, w, 522, 488, v = False)

    w, h = 1, 397
    x, y = find_center(280, 488, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 280, 488, v = True)
    x = width - x 
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 518, 488, v = True)

    w, h = 1, 50
    x, y = find_center(203, 538, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 203, 538, v = True)


    w, h = 398, 1
    x, y = find_center(203, 538, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 203, 538, v = False)

    w, h = 238, 1
    x, y = find_center(281, 443, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 281, 443, v = False)

    w, h = 1, 52
    x, y = find_center(375, 443, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 375, 443, v = True)
    x = width - x + 4
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 425, 443, v = True)

    w, h = 1, 47
    x, y = find_center(330, 490, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 330, 490, v = True)
    x = width - x + 4
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 474, 490, v = True)

    w, h = 45, 1
    x, y = find_center(330, 490, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 330, 490, v = False)
    x = width - x + 2
    tracks.append(gamebox.from_color(x,y,color,w + 4,h))
    append_dots(10, w, 427, 490, v = False)

    w, h = 1, 48
    x, y = find_center(374, 538, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 374, 538, v = True)
    x = width - x
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 425, 538, v = True)

    w, h = 1, 51
    x, y = find_center(600, 538, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 600, 538, v = True)


    w, h = 79, 1
    x, y = find_center(202, 201, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 202, 201, v = False)

    w, h = 1, 109
    x, y = find_center(202, 201, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 202, 201, v = True)

    w, h = 174, 1
    x, y = find_center(202, 92, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 202, 92, v = False)
    x = width - x
    tracks.append(gamebox.from_color(x,y,color,176,h))
    append_dots(10, w, 425, 92, v = False)

    w, h = 397, 1
    x, y = find_center(202, 154, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 202, 154, v = False)

    w, h = 1, 62
    x, y = find_center(376, 154, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 376, 154, v = True)
    x = width - x
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 425, 154, v = True)

    w, h = 1, 47
    x, y = find_center(330, 201, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 330, 201, v = True)
    x = width - x
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 472, 201, v = True)

    w, h = 45, 1    
    x, y = find_center(330, 201, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 330, 201, v = False)
    x = width - x
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 426, 201, v = False)

    w, h = 1, 50
    x, y = find_center(375, 251, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 375, 251, v = True)
    x = width - x 
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 426, 251, v = True)

    w, h = 1, 63
    x, y = find_center(599, 154, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 599, 154, v = True)

    w, h = 80, 1
    x, y = find_center(520, 202, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 520, 202, v = False)

    w, h = 1, 48
    x, y = find_center(599, 202, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, h, 599, 202, v = True)

    w, h = 177, 1
    x, y = find_center(473, 299, w, h)
    tracks.append(gamebox.from_color(x,y,color,w,h))
    append_dots(10, w, 473, 299, v = False)
    append_dots(10, 176, 426, 393, v = False)
    append_dots(10, 46, 571, 489, v = True)


make_tracks()
current_track = tracks[0]



def find_touching_tracks(current_track):
    ans = []
    for track in tracks:
        if current_track.touches(track) and track != current_track:
            ans.append(track)
    return ans


def move_along_track(keys):
    global target_angle, current_track, angle
    for track in tracks:
        if pacman.speedy != 0 and feelers[0].touches(current_track) and feelers[2].touches(current_track): #controls non-corner y-movement
            if pygame.K_UP in keys and pacman.speedy != -1:
                set_speeds(0, -pacman_speed)
            if pygame.K_DOWN in keys and pacman.speedy != 1:
                set_speeds(0, pacman_speed)
        if pacman.speedx != 0 and feelers[1].touches(current_track) and feelers[3].touches(current_track): #controls non-corner x-movement
            if pygame.K_LEFT in keys and pacman.speedx != -1:
                set_speeds(-pacman_speed, 0)
            if pygame.K_RIGHT in keys and pacman.speedx != 1:
                set_speeds(pacman_speed, 0)

        if feelers[2].touches(track) and pygame.K_DOWN in keys and track != current_track:
            set_speeds(0, pacman_speed)
            current_track = track

        if feelers[3].touches(track) and pygame.K_LEFT in keys and track != current_track:
            set_speeds(-pacman_speed, 0) 
            current_track = track
        
        if feelers[1].touches(track) and pygame.K_RIGHT in keys and track != current_track:
            set_speeds(pacman_speed, 0)
            current_track = track

        if feelers[0].touches(track) and pygame.K_UP in keys and track != current_track:
            set_speeds(0, -pacman_speed)
            current_track = track
        
        if pacman.speedx == 0 and current_track.width > 1 and feelers[3].touches(current_track) and pygame.K_LEFT in keys:
            set_speeds(-pacman_speed, 0)
            
        if pacman.speedx == 0 and current_track.width > 1 and feelers[1].touches(current_track) and pygame.K_RIGHT in keys:
            set_speeds(pacman_speed, 0)
        
        if pacman.speedy == 0 and current_track.height > 1 and feelers[0].touches(current_track) and pygame.K_UP in keys:
            set_speeds(0, -pacman_speed)

        if pacman.speedy == 0 and current_track.height > 1 and feelers[2].touches(current_track) and pygame.K_DOWN in keys:
            set_speeds(0, pacman_speed)
def check_at_corner(keys):
    global current_track
    candidates = find_touching_tracks(current_track)
    if pacman.speedx != 0 and (not feelers[1].touches(current_track) or not feelers[3].touches(current_track)):
        can_turn = False
        for c in candidates:
            if feelers[2].touches(c) and pygame.K_DOWN in keys or feelers[0].touches(c) and pygame.K_UP in keys or feelers[1].touches(c) and pygame.K_RIGHT in keys or feelers[3].touches(c) and pygame.K_LEFT in keys:
                can_turn = True
        if not can_turn:
            set_speeds(0,0)
    if pacman.speedy != 0 and (not feelers[2].touches(current_track) or not feelers[0].touches(current_track)):
            can_turn = False
            for c in candidates:
                if feelers[2].touches(c) and pygame.K_DOWN in keys or feelers[0].touches(c) and pygame.K_UP in keys or feelers[1].touches(c) and pygame.K_RIGHT in keys or feelers[3].touches(c) and pygame.K_LEFT in keys:
                    can_turn = True
            if not can_turn:
                set_speeds(0,0)

x_1 = 0
x_2 = 0
y_1 = 0
y_2 = 0
pos_1 = (x_1,y_1)
pos_2 = (x_2,y_2)
dp1 = False
dp2 = False
def check_mouse():
    global x_1, x_2, y_1, y_2, dp1, dp2, pos_1, pos_2
    state = pygame.mouse.get_pressed()
    if state[0]:
        x_1 = pygame.mouse.get_pos()[0]
        y_1 = pygame.mouse.get_pos()[1]
        pos_1 = (x_1,y_1)
        dp1 = True
    if state[2]:
        x_2 = pygame.mouse.get_pos()[0]
        y_2 = pygame.mouse.get_pos()[1]
        pos_2 = (x_2,y_2)
        dp2 = True




def draw_scene():
    camera.clear('black')
    camera.draw(pacman)
    if dp1:
        camera.draw(gamebox.from_text(50,50,'('+ str(pos_1[0]) + ',' + str(pos_1[1]) + ')', 14, 'white'))
    if dp2:
        camera.draw(gamebox.from_text(50,70,'('+ str(pos_2[0]) + ',' + str(pos_2[1]) + ')', 14, 'white'))
        diff = (np.abs(pos_1[0]-pos_2[0]), np.abs(pos_1[1]-pos_2[1]))
        camera.draw(gamebox.from_text(50,90,str(diff), 14, 'white'))
    for wall in walls:
        camera.draw(wall)
    for dot in dots:
        camera.draw(dot)
    for ghost in ghosts:
        camera.draw(ghost)
    camera.draw(gamebox.from_text(width/2, 50, 'Score: ' + str(score), 20,'white', bold=True))

    camera.display()

def draw_start_screen():
    boxes = []
    boxes.append(gamebox.from_text(width/2, height/4, 'Pacman', 80, 'yellow', bold=True))
    boxes.append(gamebox.from_text(width/2, height/4 + 50, 'Braden Desman - jzf5hc', 20, 'white'))
    boxes.append(gamebox.from_text(width/2, height/4 + 150, 'Instructions: use the arrow keys to control Pacman as he attempts to eat all the bits.', 20, 'white'))
    boxes.append(gamebox.from_text(width/2, height/4 + 175, 'Be sure to avoid all of the ghosts! Press space to begin.', 20, 'white'))
    boxes.append(gamebox.from_image(402, 250, pacman_images[0]))
    boxes[4].scale_by(pacman_scale_factor)
    boxes[4].rotate(180)
    for box in boxes:
        camera.draw(box)
    camera.display()


def tick(keys):
    global ticker, game_started, game_over,angle,score,dots,tracks,ghosts_active,ghosts
    ticker += 1 
    if game_started:
        check_at_corner(keys)
        move_along_track(keys)
        move_pacman(keys)
        if ticker % 600 == 0: # move a ghost into the game every 10 seconds
            if ghosts_active < 4:
                ghosts[ghosts_active].x = 402
                ghosts[ghosts_active].y = 250
                ghosts[ghosts_active].c.x = 402
                ghosts[ghosts_active].c.y = 250
                ghosts[ghosts_active].feelers[0].center = (402,249)
                ghosts[ghosts_active].feelers[1].center = (403,250)
                ghosts[ghosts_active].feelers[2].center = (402,251)
                ghosts[ghosts_active].feelers[3].center = (401,250)
                ghosts[ghosts_active].current_track = tracks[0]
                ghosts[ghosts_active].in_box = False
                set_g_speed(ghosts[ghosts_active], ghost_speed, 0)
                ghosts_active += 1
        for ghost in ghosts:
            move_ghost(ghost)
        check_mouse()
        collide_with_dots()
        draw_scene()
    if not game_started and not game_over:
        camera.clear('black')
        draw_start_screen()
        if pygame.K_SPACE in keys:
            game_started = True
            game_over = False
            score = 0
    for ghost in ghosts:
        if ghost.touches(pacman):
            game_over = True
            game_started = False
            end_text = 'GAME OVER'
            end_color = 'red'
    if len(dots) == 0:
        game_over = True
        game_started = False
        end_text = 'YOU WON!'
        end_color = 'green'
    if game_over:
        camera.clear('black')
        camera.draw(gamebox.from_text(width/2, height/2 + 150, end_text, 80, end_color, bold=True))
        camera.draw(gamebox.from_text(width/2, height/2 + 220, 'Score: ' + str(score), 40, 'white', bold=True))
        camera.draw(gamebox.from_text(width/2, height/2 + 260, 'Press space to play again!', 30, 'white', bold= True))
        draw_start_screen()
        if pygame.K_SPACE in keys: 
            game_started = True
            game_over = False
            pacman.x = 402
            pacman_center.x = 402
            feelers[0].x = 402
            feelers[2].x = 402
            feelers[1].x = 403
            feelers[3].x = 401
            pacman.y = 250
            pacman_center.y = 250
            feelers[0].y = 249
            feelers[2].y = 251
            feelers[1].y = 250
            feelers[3].y = 250
            if angle != 0:
                pacman.rotate(0 - angle)
                angle = 0
            score = 0
            set_speeds(pacman_speed, 0)
            tracks = []
            dots = []
            make_tracks()
            set_speeds(pacman_speed, 0)
            g1 = gamebox.from_image(width/2 - 15, height/2 + 10, ghost_images[0])
            g2 = gamebox.from_image(width/2 - 15, height/2 - 13, ghost_images[1])
            g3 = gamebox.from_image(width/2 + 15, height/2 - 13, ghost_images[2])
            g4 = gamebox.from_image(width/2 + 15, height/2 + 10, ghost_images[3])

            ghosts = [g1, g2, g3 ,g4]
            for ghost in ghosts:
                ghost.scale_by(0.2) 
                ghost.in_box = True
                ghost.feelers = []
                ghost.c = gamebox.from_color(ghost.x, ghost.y, 'red', 1,1)
                ghost.feelers.append(gamebox.from_color(ghost.c.x, ghost.c.y - 1, 'red', 1,1)) #top
                ghost.feelers.append(gamebox.from_color(ghost.c.x + 1, ghost.c.y, 'red', 1,1)) #right
                ghost.feelers.append(gamebox.from_color(ghost.c.x, ghost.c.y + 1, 'red', 1,1)) #bottom
                ghost.feelers.append(gamebox.from_color(ghost.c.x - 1, ghost.c.y, 'red', 1,1)) #left
            ghosts_active = 0




gamebox.timer_loop(fps,tick)