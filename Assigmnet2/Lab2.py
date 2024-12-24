# Importing libraries
from OpenGL.GL import * 
from OpenGL.GLUT import * 
from OpenGL.GLU import *
import random
import time
import math
import sys


# Global Vars
window_width = 800
window_height = 800
point_size = 3

# Color Pallete
black_color = [0, 0, 0, 1.0]
white_color = [1, 1, 1, 1.0]
gold_color = [1, 0.84, 0, 1.0]
red_color = [1, 0, 0, 1.0]
blue_color = [0, 0, 1, 1.0]
green_color = [0, 1, 0, 1.0]


# Initial Rocket Points
initial_rocket_nose = [400, 615]
initial_rocket_body = [[380, 665], [420, 665], [420, 750], [380, 750]]
initial_fire_1 = [[382, 760], [390, 760], [390, 794], [382, 794]]
initial_fire_2 = [[396, 760], [404, 760], [404, 794], [396, 794]]
initial_fire_3 = [[410, 760], [418, 760], [418, 794], [410, 794]]
initial_wing_right = [[420, 745], [440, 750], [420, 714]]
initial_wing_left = [[380, 745], [360, 750], [380, 714]]

# Rocket Points
rocket_nose = [400, 615]
# tl - tr - br - bl
rocket_body = [[380, 665], [420, 665], [420, 750], [380, 750]]
fire_1 = [[382, 760], [390, 760], [390, 794], [382, 794]]
fire_2 = [[396, 760], [404, 760], [404, 794], [396, 794]]
fire_3 = [[410, 760], [418, 760], [418, 794], [410, 794]]
# Anti-Clockwise starting from left bottom
wing_right = [[rocket_body[2][0], rocket_body[2][1] - 5], [rocket_body[2][0] + 20, rocket_body[2][1]], [rocket_body[2][0], rocket_body[2][1] - 36]]
wing_left = [[rocket_body[3][0], rocket_body[3][1] - 5], [rocket_body[3][0] - 20, rocket_body[3][1]], [rocket_body[3][0], rocket_body[3][1] - 36]]

# Buttons
# Clockwise - Starting from top left
play_button = [[380, 30], [420, 45], [380, 60]]
# First Line, Second Line - Left to Right
cross_button = [[750, 30], [770, 50], [750, 50], [770, 30]]
# Arrow 3 points - Top, Mid, Bottom, Mid Line
arrow_button = [[40, 30], [30, 40], [40, 50], [70, 40]]
# First Line, Second Line - Left to Right
pause_button = [[390, 30], [390, 60], [410, 30], [410, 60]]


# Layout Mapping for buttons
play_mapping = {
    'xMin' : play_button[0][0],
    'xMax' : play_button[1][0],
    'yMin' : play_button[0][1],
    'yMax' : play_button[2][1]
}

cross_mapping = {
    'xMin' : cross_button[0][0],
    'xMax' : cross_button[1][0],
    'yMin' : cross_button[3][1],
    'yMax' : cross_button[1][1]
}

arrow_mapping = {
    'xMin' : arrow_button[1][0],
    'xMax' : arrow_button[3][0],
    'yMin' : arrow_button[0][1],
    'yMax' : arrow_button[2][1]
}

pause_mapping = {
    'xMin' : pause_button[0][0],
    'xMax' : pause_button[2][0],
    'yMin' : pause_button[0][1],
    'yMax' : pause_button[1][1]
}


# Control Variables - General For all games
paused = True
fire_radius = 7 
last_frame_time = time.time()
curr_game = None

# Class for a perticular round
class Game:
    def __init__(self):
        self.projectiles = []
        self.base_rocket_speed = 400
        self.base_projectile_speed = 200
        self.score = 0
        self.missed = 0   
        self.misfires = 0  
        self.falling_circles = [] 
        self.spawn_timer = 0     # To see when to spawn a new circles
        self.game_time = 0  # To keep track of time so game gets harder
        self.game_over = False 
        self.speed_multiplier = 1.0 # To increase speed of circles
    
    def update_speed_multiplier(self, delta_time):
        self.game_time += delta_time
        # Speed by 20% every 10 seconds
        self.speed_multiplier = 1.0 + (self.game_time // 10) * 0.2
        
    def spawn_circle(self):
        self.falling_circles.append(Circle())
    

class Circle():
    def __init__(self):
        self.x = random.randint(50, window_width-50)
        self.y = 0  
        self.base_radius = random.randint(10, 15)
        self.radius = self.base_radius
        self.is_special = random.random() < 0.2  
        self.phase = 0 
        self.color = green_color if self.is_special else gold_color
        self.speed = 50
        
    def update(self, delta_time, speed_multiplier):
        # Move down
        self.y += self.speed * delta_time  * speed_multiplier
        
        # Special circles pulse
        if self.is_special:
            self.phase += delta_time * 5
            self.radius = self.base_radius + math.sin(self.phase) * 5


def resetRocketPosition():
    global rocket_nose, rocket_body, wing_left, wing_right, fire_1, fire_2, fire_3
    rocket_nose = initial_rocket_nose.copy()
    rocket_body = [point.copy() for point in initial_rocket_body]
    fire_1 = [point.copy() for point in initial_fire_1]
    fire_2 = [point.copy() for point in initial_fire_2]
    fire_3 = [point.copy() for point in initial_fire_3]
    wing_right = [point.copy() for point in initial_wing_right]
    wing_left = [point.copy() for point in initial_wing_left]

def get_rocket_box():
    return {
        'x': wing_left[1][0],
        'width': wing_right[1][0] - wing_left[1][0],
        'y': rocket_nose[1],
        'height': fire_1[3][1] - rocket_nose[1]
    }

def get_circle_box(circle):
    return {
        'x': circle.x - circle.radius,
        'y': circle.y - circle.radius,
        'width': circle.radius * 2,
        'height': circle.radius * 2
    }

def get_projectile_box(proj):
    return {
        'x': proj[0] - fire_radius,
        'y': proj[1] - fire_radius,
        'width': fire_radius * 2,
        'height': fire_radius * 2
    }

def has_collided(box1, box2):
    return (box1['x'] < box2['x'] + box2['width'] and
            box1['x'] + box1['width'] > box2['x'] and
            box1['y'] < box2['y'] + box2['height'] and
            box1['y'] + box1['height'] > box2['y'])

def check_rocket_circle_collision():
    global curr_game, paused
    
    rocket_box = get_rocket_box()  # Get current rocket position
    for circle in curr_game.falling_circles:
        circle_box = get_circle_box(circle)
        if has_collided(circle_box, rocket_box):
            curr_game.game_over = True
            print(f"Game Over! Rocket hit! Final Score: {curr_game.score}")
            paused = True
            curr_game = None
            resetRocketPosition()
            return True
    return False

def check_game_over():
    global curr_game, paused
    
    if curr_game.missed >= 3 or curr_game.misfires >= 3 or curr_game.game_over:
        curr_game.game_over = True
        print(f"Game Over! Final Score: {curr_game.score}")
        print(f"Missed Circles: {curr_game.missed}")
        print(f"Misfires: {curr_game.misfires}")
        # Reset game state
        paused = True
        curr_game = None
        resetRocketPosition() 
        return True
    return False

def check_collisions():
    global curr_game
    
    for proj in curr_game.projectiles[:]:
        proj_box = get_projectile_box(proj)
        
        for circle in curr_game.falling_circles[:]:
            circle_box = get_circle_box(circle)
            
            if has_collided(proj_box, circle_box):
                # Collision detected
                if circle.is_special:
                    curr_game.score += 2  
                else:
                    curr_game.score += 1
                    
                # Remove both projectile and circle
                if proj in curr_game.projectiles:
                    curr_game.projectiles.remove(proj)
                if circle in curr_game.falling_circles:
                    curr_game.falling_circles.remove(circle)
                
                # Print score
                print(f"Score: {curr_game.score}")
                break


def moveRocket(move_amount, delta_time):
    global rocket_nose, rocket_body, wing_left, wing_right, fire_1, fire_2, fire_3
    
    # Calculate actual movement based on delta time
    actual_move = move_amount * delta_time
    
    rocket_nose[0] += actual_move
    
    for point in rocket_body:
        point[0] += actual_move
        
    for point in wing_left:
        point[0] += actual_move
        
    for point in wing_right:
        point[0] += actual_move
        
    for point in fire_1:
        point[0] += actual_move
        
    for point in fire_2:
        point[0] += actual_move
        
    for point in fire_3:
        point[0] += actual_move

# Drawing Functions
def drawPlayButton():
    global play_button, gold_color
    drawTriangle(play_button[0], play_button[1], play_button[2], gold_color)

def drawPauseButton():
    global pause_button, gold_color
    drawMidpointLine(pause_button[0][0], pause_button[0][1], pause_button[1][0], pause_button[1][1], gold_color)
    drawMidpointLine(pause_button[2][0], pause_button[2][1], pause_button[3][0], pause_button[3][1], gold_color)

def drawCrossButton():
    global cross_button, red_color
    drawMidpointLine(cross_button[0][0], cross_button[0][1], cross_button[1][0], cross_button[1][1], red_color)
    drawMidpointLine(cross_button[2][0], cross_button[2][1], cross_button[3][0], cross_button[3][1], red_color)

def drawArrowButton():
    global arrow_button, blue_color
    drawMidpointLine(arrow_button[0][0], arrow_button[0][1], arrow_button[1][0], arrow_button[1][1], blue_color)
    drawMidpointLine(arrow_button[1][0], arrow_button[1][1], arrow_button[2][0], arrow_button[2][1], blue_color)
    drawMidpointLine(arrow_button[1][0], arrow_button[1][1], arrow_button[3][0], arrow_button[3][1], blue_color)
    
def FindZone(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0

    if abs(dx) > abs(dy):
        if dx >= 0 and dy >= 0:
            return 0
        elif dx < 0 and dy >= 0:
            return 3
        elif dx < 0 and dy < 0:
            return 4
        else:
            return 7
    else:
        if dx >= 0 and dy >= 0:
            return 1
        elif dx < 0 and dy >= 0:
            return 2
        elif dx < 0 and dy < 0:
            return 5
        else:
            return 6

def convertToZoneZero(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    else:
        return x, -y

def convertToOriginalZone(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    else:
        return x, -y

def drawMidpointLine(x0, y0, x1, y1, color, pSize = None):
    global point_size
    glColor4f(color[0], color[1], color[2], color[3])
    glPointSize(point_size if pSize is None else pSize)

    zone = FindZone(x0, y0, x1, y1)

    x0_conv, y0_conv = convertToZoneZero(x0, y0, zone)
    x1_conv, y1_conv = convertToZoneZero(x1, y1, zone)

    if x1_conv < x0_conv:
        x0_conv, x1_conv = x1_conv, x0_conv
        y0_conv, y1_conv = y1_conv, y0_conv

    dx = x1_conv - x0_conv
    dy = y1_conv - y0_conv
    d = 2 * dy - dx
    incrE = 2 * dy
    incrNE = 2 * (dy - dx)
    x = x0_conv
    y = y0_conv

    glBegin(GL_POINTS)
    while x <= x1_conv:
        px, py = convertToOriginalZone(x, y, zone)
        glVertex2f(px, py)
        
        if d <= 0:
            d += incrE
        else:
            d += incrNE
            y += 1
        x += 1
    glEnd()

def drawMidpointCircle(xc, yc, radius, color, pSize = None):
    global point_size
    glColor4f(color[0], color[1], color[2], color[3])
    glPointSize(point_size if pSize is None else pSize)

    x = radius
    y = 0
    d = 1 - radius  # Initial decision parameter

    glBegin(GL_POINTS)
    while x >= y:
        glVertex2f(xc + x, yc + y)  # Zone 0
        glVertex2f(xc - x, yc + y)  # Zone 3
        glVertex2f(xc + x, yc - y)  # Zone 1
        glVertex2f(xc - x, yc - y)  # Zone 4
        glVertex2f(xc + y, yc + x)  # Zone 2
        glVertex2f(xc - y, yc + x)  # Zone 7
        glVertex2f(xc + y, yc - x)  # Zone 6
        glVertex2f(xc - y, yc - x)  # Zone 5

        y += 1
        if d < 0:  # Midpoint is inside the circle
            d += 2 * y + 1
        else:  # Midpoint is outside or on the circle
            x -= 1
            d += 2 * y - 2 * x + 1
    glEnd()

def drawTriangle(x, y, z, color, pSize = None):
    glColor4f(color[0], color[1], color[2], color[3])

    drawMidpointLine(x[0], x[1], y[0], y[1], color, pSize)  # First line
    drawMidpointLine(y[0], y[1], z[0], z[1], color, pSize)  # Second line
    drawMidpointLine(z[0], z[1], x[0], x[1], color, pSize)  # Third line

def drawTheRocket():
    global rocket_nose, window_width, window_height

    # Nose
    drawTriangle(rocket_nose, rocket_body[0], rocket_body[1], gold_color)

    # Body
    drawMidpointLine(rocket_body[1][0], rocket_body[1][1], rocket_body[2][0], rocket_body[2][1], gold_color)
    drawMidpointLine(rocket_body[2][0], rocket_body[2][1], rocket_body[3][0], rocket_body[3][1], gold_color)
    drawMidpointLine(rocket_body[3][0], rocket_body[3][1], rocket_body[0][0], rocket_body[0][1], gold_color)

    # Fire
    def drawFire(fire):
        drawMidpointLine(fire[0][0], fire[0][1], fire[1][0], fire[1][1], gold_color, 2)
        drawMidpointLine(fire[1][0], fire[1][1], fire[2][0], fire[2][1], gold_color, 2)
        drawMidpointLine(fire[2][0], fire[2][1], fire[3][0], fire[3][1], gold_color, 2)
        drawMidpointLine(fire[3][0], fire[3][1], fire[0][0], fire[0][1], gold_color, 2)

    drawFire(fire_1)
    drawFire(fire_2)
    drawFire(fire_3)

    # Wings
    drawTriangle(wing_right[0], wing_right[1], wing_right[2], gold_color, 2)
    drawTriangle(wing_left[0], wing_left[1], wing_left[2], gold_color, 2)



def draw():
    drawTheRocket()

    if paused:
        drawPlayButton()
        drawCrossButton()
        drawArrowButton()
    else:
        drawPauseButton()


    if curr_game is not None:
        for proj in curr_game.projectiles:
            drawMidpointCircle(proj[0], proj[1], fire_radius, gold_color, 2)
        
        for circle in curr_game.falling_circles:
            drawMidpointCircle(int(circle.x), int(circle.y), int(circle.radius), circle.color, 2)

    
def animate():
    global last_frame_time, curr_game
    
    current_time = time.time()
    delta_time = current_time - last_frame_time
    last_frame_time = current_time

    if not paused and curr_game is not None:
        # Update speed multiplier
        curr_game.update_speed_multiplier(delta_time)

        # Update projectiles
        for proj in curr_game.projectiles:
            proj[1] -= curr_game.base_projectile_speed * delta_time * curr_game.speed_multiplier
        
        # Check for misfires 
        old_proj_count = len(curr_game.projectiles)
        curr_game.projectiles = [proj for proj in curr_game.projectiles if proj[1] > 0]
        curr_game.misfires += old_proj_count - len(curr_game.projectiles)

        if check_game_over():
            return

        # Update circles
        for circle in curr_game.falling_circles:
            circle.update(delta_time, curr_game.speed_multiplier)
        
        # Check for missed circles
        old_circle_count = len(curr_game.falling_circles)
        curr_game.falling_circles = [c for c in curr_game.falling_circles if c.y < window_height]
        curr_game.missed += old_circle_count - len(curr_game.falling_circles)

        if check_game_over():
            return
        
        # Spawn new circles
        curr_game.spawn_timer += delta_time
        if curr_game.spawn_timer > 2:  # Spawn every 2 seconds
            curr_game.spawn_circle()
            curr_game.spawn_timer = 0
        
        # Check for collisions
        check_collisions()

        # if rocket hit any circles
        check_rocket_circle_collision()

    glutPostRedisplay()


def keyPressed(key, x, y):
    global rocket_nose, paused, window_width, last_frame_time, curr_game

    if not paused and curr_game is not None:
        # delta time
        current_time = time.time()
        delta_time = current_time - last_frame_time

        

        if key == b'a' and rocket_nose[0] > curr_game.base_rocket_speed * delta_time * curr_game.speed_multiplier:
            moveRocket(-curr_game.base_rocket_speed, delta_time)
                
        elif key == b'd' and rocket_nose[0] < window_width - curr_game.base_rocket_speed * delta_time * curr_game.speed_multiplier:
            moveRocket(curr_game.base_rocket_speed, delta_time)
                
        elif key == b' ':  # spacebar
            curr_game.projectiles.append([rocket_nose[0], rocket_nose[1]])
    
    glutPostRedisplay()
    

def mouseClicked(button, state, x, y):
    global paused, play_mapping, pause_mapping, curr_game
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # if mouse is Clicked in the Play Button, pause = False
        if paused and play_mapping['xMin'] <= x <= play_mapping['xMax'] and play_mapping['yMin'] <= y <= play_mapping['yMax']:
            paused = False
            if curr_game is None:
                curr_game = Game()

        # if mouse is Clicked in the Pause Button, pause = True
        elif not paused and pause_mapping['xMin'] <= x <= pause_mapping['xMax'] and pause_mapping['yMin'] <= y <= pause_mapping['yMax']:
            paused = True

        elif cross_mapping['xMin'] <= x <= cross_mapping['xMax'] and cross_mapping['yMin'] <= y <= cross_mapping['yMax']:
            print("Goodbye!")
            if curr_game is not None:
                print(f"Final Score: {curr_game.score}")

            glutDestroyWindow(wind)
            sys.exit(0)
        
        elif arrow_mapping['xMin'] <= x <= arrow_mapping['xMax'] and arrow_mapping['yMin'] <= y <= arrow_mapping['yMax']:
            print("Starting Over!")
            resetRocketPosition()
            curr_game = Game() 
        
    glutPostRedisplay()

###################BASE CODE######################

def iterate():
    global window_width, window_height
    glViewport(0, 0, window_width, window_height) 
    glMatrixMode(GL_PROJECTION)  
    glLoadIdentity()       
    glOrtho(0, window_width, window_height, 0, 0.0, 1.0) 
    glMatrixMode(GL_MODELVIEW)   
    glLoadIdentity()            

def showScreen():
    global color
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
    glLoadIdentity()         
    iterate()

    draw()
    glutSwapBuffers()

# Environment
glutInit()    
glutInitDisplayMode(GLUT_RGBA) 
glutInitWindowSize(window_width, window_height)
screen_width = glutGet(GLUT_SCREEN_WIDTH)
screen_height = glutGet(GLUT_SCREEN_HEIGHT)
window_x = (screen_width - window_width) // 2
window_y = (screen_height - window_height) // 2
glutInitWindowPosition(window_x, window_y)
wind = glutCreateWindow(b"Shoot The Circles")
glClearColor(black_color[0], black_color[1], black_color[2], black_color[3]) 
glutDisplayFunc(showScreen)
glutIdleFunc(animate)
glutKeyboardFunc(keyPressed)
glutMouseFunc(mouseClicked)
glutMainLoop()  