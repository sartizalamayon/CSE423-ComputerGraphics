############################# Imports #############################
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import * 
import sys
import random
import math


############################# Global Vars #############################
window_width = 800
window_height = 800
point_size = 3
countdown_timer = 3
game_started = False
last_update_time = 0
game_won = False
move_speed = 20

############################# Color Pallete #############################
black = [0, 0, 0, 1.0]
white = [1, 1, 1, 1.0]
neon_blue = [0, 0.8, 1, 1.0]
neon_pink = [1, 0.2, 0.6, 1.0]
neon_green = [0.2, 1, 0.2, 1.0]
selected_color = [1, 1, 0, 1.0]

# Menu settings
menu_items = ["Start Game", "Instructions", "Exit"]
selected_item = 0
menu_spacing = 60

############################ Game Classes ############################
# Game states
MENU_STATE = 0
GAME_STATE = 1
END_STATE = 2
INSTRUCTION_STATE = 3
instructions = [
    "> Use arrow keys to move the player",
    "> Avoid evil dots to stay alive",
    "> Reach exit before timer runs out",
    "> Collect Magic Balls to unlock paths",
    "> Complete to win the game"
]
current_game = None
current_state = MENU_STATE

# class for a perticular game instance,
# it contains the properties of a single game instance, 
# when the user hit play button, a new instance is created
class MazeRunner:
    def __init__(self):
        self.timer = 60
        self.last_time = glutGet(GLUT_ELAPSED_TIME)
        self.countdown = 3
        self.countdown_last_time = glutGet(GLUT_ELAPSED_TIME)

        #  maze dimensions
        self.maze_width = 800
        self.maze_height = 700
        self.maze_offset_x = 0
        self.maze_offset_y = 0  # Offset to center vertically
        
        # cell size based on  dimensions
        self.grid_width = 21  
        self.grid_height = 15  
        self.cell_width = self.maze_width // self.grid_width
        self.cell_height = self.maze_height // self.grid_height
        
        # Player initialization
        self.player_size = 15
        self.player_pos = [
            self.maze_offset_x + self.cell_width,
            self.maze_offset_y + self.maze_height - self.cell_height
        ]
        
        # End point
        self.end_pos = [
            self.maze_offset_x + self.maze_width - self.cell_width,
            self.maze_offset_y + self.cell_height
        ]

        # maze grid using recursive backtracker algorithm
        self.maze_grid = self.generate_maze()

        start_y = None
        for i in range(1, self.grid_height-1):
            if self.maze_grid[i][1] == 0: 
                start_y = i
                break
        
        if start_y is not None:
            self.player_pos = [
                self.maze_offset_x + self.cell_width * 1.5,  # Slightly offset from wall
                self.maze_offset_y + start_y * self.cell_height + self.cell_height/2
            ]

        self.magic_balls = []  # Store ball positions
        self.ball_size = 10     # Size of magic balls
        self.generate_magic_balls()


        # Add after existing initialization code
        self.evils = []        # Store evil positions
        self.evil_size = 4     # Size of evil dots
        self.generate_evils()
    
    def generate_evils(self):
        # Place evils directly on path cells (0s), not on or next to walls
        empty_cells = []
        
        # Find all valid path cells, excluding edges
        for y in range(1, self.grid_height - 1):
            for x in range(1, self.grid_width - 1):
                if self.maze_grid[y][x] == 0:
                    empty_cells.append((x, y))
        
        # Select 5 random locations from available paths
        for _ in range(min(5, len(empty_cells))):
            if empty_cells:
                x, y = random.choice(empty_cells)
                empty_cells.remove((x, y))
                
                evil_pos = [
                    self.maze_offset_x + x * self.cell_width + self.cell_width/2,
                    self.maze_offset_y + y * self.cell_height + self.cell_height/2
                ]
                self.evils.append(evil_pos)
    
    def check_evil_collision(self):
        px, py = self.player_pos
        for evil_pos in self.evils:
            ex, ey = evil_pos
            # Check collision using distance formula
            if math.sqrt((px - ex)**2 + (py - ey)**2) < (self.player_size + self.evil_size):
                return True
        return False

    def draw_evils(self):
        # Blinking effect using sine wave
        blink = (math.sin(glutGet(GLUT_ELAPSED_TIME) / 100.0) + 1) / 2  # Faster blink 
        evil_color = [1.0, 0.0, 0.0, blink]  # Red with varying opacity
        
        for evil_pos in self.evils:
            drawMidpointCircle(evil_pos[0] + 7, evil_pos[1]+7
                               , self.evil_size, evil_color)
            
    def generate_magic_balls(self):
        # Find empty path cells for ball placement
        for _ in range(3):  # Place 3 magic balls
            while True:
                x = random.randint(1, self.grid_width - 3)  # Not too close to exits
                y = random.randint(1, self.grid_height - 2) # Not too close to top/bottom
                if self.maze_grid[y][x] == 0:  # If it's a path
                    ball_pos = [
                        self.maze_offset_x + x * self.cell_width + self.cell_width/2,
                        self.maze_offset_y + y * self.cell_height + self.cell_height/2
                    ]
                    self.magic_balls.append(ball_pos)
                    break
    
    def draw_magic_balls(self):
        ball_color = [neon_blue[0], neon_blue[1], neon_blue[2], 1.0]  # Full opacity, no blinking
        for ball_pos in self.magic_balls:
            drawMidpointCircle(ball_pos[0], ball_pos[1], self.ball_size, ball_color)

    def check_ball_collision(self):
        px, py = self.player_pos
        for ball_pos in self.magic_balls[:]: # Iterate over a copy of the list
            bx, by = ball_pos
            # Check if player touches ball
            if math.sqrt((px - bx)**2 + (py - by)**2) < (self.player_size + self.ball_size):
                self.magic_balls.remove(ball_pos)
                self.create_magic_openings()
                return True
        return False  

    def create_magic_openings(self):
        # Get player's current grid position
        grid_x = int((self.player_pos[0] - self.maze_offset_x) / self.cell_width)
        grid_y = int((self.player_pos[1] - self.maze_offset_y) / self.cell_height)
        
        # Create openings in next 6 walls to the right
        walls_opened = 0
        for x in range(grid_x + 1, min(grid_x + 4, self.grid_width - 1)):
            if self.maze_grid[grid_y][x] == 1:  # If it's a wall
                self.maze_grid[grid_y][x] = 0    # Create opening
                walls_opened += 1
                if walls_opened == 6: 
                    break      

    def generate_maze(self):
        # grid of all 1's (walls)
        maze = [[1 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        def carve_path(x, y):
            maze[y][x] = 0
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)

            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self.grid_width and 
                    0 <= new_y < self.grid_height and 
                    maze[new_y][new_x] == 1):
                    # Carve the wall between current and next cell
                    maze[y + dy//2][x + dx//2] = 0
                    carve_path(new_x, new_y)
        
        # Start from top-bottom cell
        carve_path(1, 1)
        
        # on the right wall, 3 random end points
        for _ in range(3):
            y = random.randint(1, self.grid_height - 2)
            maze[y][self.grid_width - 1] = 0
        #
        return maze

    def draw_maze(self):
        # Draw maze cells
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                if self.maze_grid[i][j] == 1:  # Wall
                    x = self.maze_offset_x + j * self.cell_width
                    y = self.maze_offset_y + i * self.cell_height
                    drawFilledPolygon([
                        (x, y),
                        (x + self.cell_width, y),
                        (x + self.cell_width, y + self.cell_height),
                        (x, y + self.cell_height)
                    ], white)
                    
        self.draw_magic_balls() 

    def draw_player(self):
        x, y = self.player_pos
        
        # Main body ( square)
        body_size = self.player_size
        drawFilledPolygon([
            (x - body_size/2, y - body_size/2),
            (x + body_size/2, y - body_size/2),
            (x + body_size/2, y + body_size/2),
            (x - body_size/2, y + body_size/2)
        ], neon_green)
        
        # Eyes (two small circles)
        eye_size = body_size / 6
        eye_offset = body_size / 4
        eye_height = body_size / 8
        drawMidpointCircle(x - eye_offset, y + eye_height, eye_size, black)
        drawMidpointCircle(x + eye_offset, y + eye_height, eye_size, black)

    def check_collision(self, new_x, new_y):
        # player position to grid coordinates
        grid_x = int((new_x - self.maze_offset_x) / self.cell_width)
        grid_y = int((new_y - self.maze_offset_y) / self.cell_height)
        
        # bounds
        if (grid_x < 0 or grid_x >= self.grid_width or 
            grid_y < 0 or grid_y >= self.grid_height):
            return True
        
        try:
            # if the new position would be inside a wall (1 represents wall)
            return self.maze_grid[grid_y][grid_x] == 1
        except IndexError:
            return True
    

    def move_player(self, dx, dy):
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        
        # Boundary and wall collision check
        if (new_x < self.maze_offset_x or 
            new_x > self.maze_offset_x + self.maze_width or
            new_y < self.maze_offset_y or 
            new_y > self.maze_offset_y + self.maze_height):
            return
        
        if not self.check_collision(new_x, new_y):
            self.player_pos = [new_x, new_y]
            self.check_ball_collision()
            
            # evil collision after movement
            if self.check_evil_collision():
                return True  # Signal game over
        return False

    def check_win(self):
        # player position to grid coordinates
        grid_x = int((self.player_pos[0] - self.maze_offset_x) / self.cell_width)
        grid_y = int((self.player_pos[1] - self.maze_offset_y) / self.cell_height)
        
        # if player has reached the rightmost column
        return grid_x >= self.grid_width - 1

############################# Start Screen #############################
def drawStartScreen():
    # title "MAZE RUNNER"
    draw_Header(150, 500, "MAZE", neon_blue, 50, 40, 4)  
    draw_Header(370, 500, "RUNNER", neon_pink, 50, 40, 4)  
    
    # menu items
    y_position = 410
    for i, item in enumerate(menu_items):
        color = selected_color if i == selected_item else white
        text_width = len(item) * 30
        x_position = (window_width - text_width) // 2 + 30
        draw_Header(x_position, y_position, item, color, 30, 20, 2)
        y_position -= menu_spacing

############################# Game Screen #############################
def drawGameScreen():
    global current_game, countdown_timer, game_started, last_update_time, current_state, game_won
    
    # if no current game exists, return to menu
    if current_game is None:
        current_state = MENU_STATE
        return
    
    current_time = glutGet(GLUT_ELAPSED_TIME)
    

    
    # Logo
    draw_Header(40, 735, "MAZE", neon_blue, 20, 20, 2)
    draw_Header(140, 735, "RUNNER", neon_pink, 20, 20, 2)
    
    if not game_started:
        # Update countdown
        if current_time - last_update_time >= 1000:  # Every 1 second
            countdown_timer -= 1
            last_update_time = current_time
            
            if countdown_timer <= 0:
                game_started = True
                current_game.last_time = current_time
        
        # countdown
        draw_Header(385, 735, str(countdown_timer), neon_blue, 30, 20, 3)

        # Static Timer
        draw_Header(600, 735, f"TIME {current_game.timer}", neon_blue, 20, 20, 2)
        
    elif game_started:
        if current_game.check_win():
            game_won = True
            current_state = END_STATE
            return
        if current_game.check_evil_collision():
            game_won = False
            current_state = END_STATE
            return
        # Game timer update
        if current_time - current_game.last_time >= 1000:
            current_game.timer -= 1
            current_game.last_time = current_time
            
            if current_game.timer <= 0:
                game_won = False
                current_game = None
                countdown_timer = 3
                current_state = END_STATE
                return
        
        # timer
        if current_game.timer > 10:
            draw_Header(600, 735, f"TIME {current_game.timer}", neon_blue, 20, 20, 2)
        
        else:
            draw_Header(600, 735, f"TIME {current_game.timer}", neon_pink, 20, 20, 2)

    
    # maze and player
    current_game.draw_maze()
    current_game.draw_evils()
    current_game.draw_player()
    current_game.draw_magic_balls()


############################# End Screen #############################
def drawEndScreen():
    if game_won:
        draw_Header(190, 550, "YAY YOU WON", neon_blue, 50, 35, 3)
    else:
        draw_Header(215, 550, "GAME OVER", neon_pink, 50, 35, 3)
    

    button_x, button_y = 270, 400
    button_width, button_height = 270, 50

    # outer glow
    drawFilledPolygon([
        (button_x-5, button_y-5),
        (button_x-5, button_y+button_height+5),
        (button_x+button_width+5, button_y+button_height+5),
        (button_x+button_width+5, button_y-5)
    ], [neon_blue[0]*0.5, neon_blue[1]*0.5, neon_blue[2]*0.5, 0.5])

    # button background
    drawFilledPolygon([
        (button_x, button_y),
        (button_x, button_y+button_height),
        (button_x+button_width, button_y+button_height),
        (button_x+button_width, button_y)
    ], neon_blue)

    # button text
    draw_Header(button_x + 30, button_y + 15, "$ Restart", white, 25, 20, 2)

    # menu button, glowing effect
    button_x, button_y = 270, 300
    button_width, button_height = 270, 50

    # outer glow
    drawFilledPolygon([
        (button_x-5, button_y-5),
        (button_x-5, button_y+button_height+5),
        (button_x+button_width+5, button_y+button_height+5),
        (button_x+button_width+5, button_y-5)
    ], [neon_blue[0]*0.5, neon_blue[1]*0.5, neon_blue[2]*0.5, 0.5])

    # button background
    drawFilledPolygon([
        (button_x, button_y),
        (button_x, button_y+button_height),
        (button_x+button_width, button_y+button_height),
        (button_x+button_width, button_y)
    ], neon_blue)

    # button text
    draw_Header(button_x + 55, button_y + 15, "^ Menu", white, 25, 20, 2)


############################# Instruction Screen #############################
def drawInstructionScreen():
    # Title
    draw_Header(180, 600, "INSTRUCTIONS", neon_pink, 40, 30, 3)
    
    # instructions
    y_position = 520
    for i, text in enumerate(instructions):
        draw_Header(70, y_position, text, white, 15, 15, 2)
        y_position -= 60

    # back button with glowing effect
    button_x, button_y = 290, 160
    button_width, button_height = 220, 50
    
    # outer glow
    drawFilledPolygon([
        (button_x-5, button_y-5),
        (button_x-5, button_y+button_height+5),
        (button_x+button_width+5, button_y+button_height+5),
        (button_x+button_width+5, button_y-5)
    ], [neon_blue[0]*0.5, neon_blue[1]*0.5, neon_blue[2]*0.5, 0.5])
    
    # button background
    drawFilledPolygon([
        (button_x, button_y),
        (button_x, button_y+button_height),
        (button_x+button_width, button_y+button_height),
        (button_x+button_width, button_y)
    ], neon_blue)
    
    # button text
    draw_Header(button_x + 30, button_y + 15, "<-Menu", white, 25, 20, 2)


############################# Utils #################################
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

def drawPolygon(vertices, color, pSize = None):
    glColor4f(color[0], color[1], color[2], color[3])

    for i in range(len(vertices)):
        drawMidpointLine(vertices[i][0], vertices[i][1], vertices[(i + 1) % len(vertices)][0], vertices[(i + 1) % len(vertices)][1], color, pSize)

def drawFilledPolygon(vertices, color):
    min_y = int(min(y for _, y in vertices))
    max_y = int(max(y for _, y in vertices))
    
    # For each scanline
    for y in range(min_y, max_y + 1):
        intersections = []
        
        # intersections with each edge
        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]
            
            if min(y1, y2) <= y <= max(y1, y2) and y1 != y2:
                # x-intersection using line equation
                x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                intersections.append(x)
        
        # Sort intersections
        intersections.sort()
        
        # Horizontal lines between pairs of intersections
        for i in range(0, len(intersections) - 1, 2):
            if i + 1 < len(intersections):
                drawMidpointLine(int(intersections[i]), y, 
                               int(intersections[i + 1]), y, 
                               color)
                
def LookUpTable(width, height):
        return {
            'A': [
            (0, 0, width/2, height),      # Left diagonal
            (width/2, height, width, 0),   # Right diagonal
            (width/4, height/2, 3*width/4, height/2)  # Middle horizontal
        ],
        'B': [
            (0, 0, 0, height),            # Left vertical
            (0, height, 3*width/4, height),# Top horizontal
            (0, 0, 3*width/4, 0),         # Bottom horizontal
            (0, height/2, 3*width/4, height/2), # Middle horizontal
            (3*width/4, height, 3*width/4, height/2),  # Top curve
            (3*width/4, height/2, 3*width/4, 0)   # Bottom curve
        ],
        'C': [
            (width, height, width/4, height),  # Top horizontal
            (width/4, height, 0, 3*height/4),  # Top curve
            (0, 3*height/4, 0, height/4),      # Left vertical
            (0, height/4, width/4, 0),         # Bottom curve
            (width/4, 0, width, 0)             # Bottom horizontal
        ],
        'D': [
            (0, 0, 0, height),            # Left vertical
            (0, height, 2*width/3, height),# Top horizontal
            (0, 0, 2*width/3, 0),         # Bottom horizontal
            (2*width/3, height, width, 3*height/4),  # Top curve
            (width, 3*height/4, width, height/4),    # Right vertical
            (width, height/4, 2*width/3, 0)         # Bottom curve
        ],
        'E': [
            (0, 0, 0, height),            # Left vertical
            (0, height, width, height),    # Top horizontal
            (0, 0, width, 0),             # Bottom horizontal
            (0, height/2, 3*width/4, height/2)  # Middle horizontal
        ],
        'F': [
            (0, 0, 0, height),            # Left vertical
            (0, height, width, height),    # Top horizontal
            (0, height/2, 3*width/4, height/2)  # Middle horizontal
        ],
        'G': [
            (width, height, width/4, height),  # Top horizontal
            (width/4, height, 0, 3*height/4),  # Top curve
            (0, 3*height/4, 0, height/4),      # Left vertical
            (0, height/4, width/4, 0),         # Bottom curve
            (width/4, 0, width, 0),            # Bottom horizontal
            (width, 0, width, height/2),       # Right vertical
            (width, height/2, 2*width/3, height/2)  # Middle horizontal
        ],
        'H': [
            (0, 0, 0, height),            # Left vertical
            (width, 0, width, height),     # Right vertical
            (0, height/2, width, height/2) # Middle horizontal
        ],
        'I': [
            (width/2, 0, width/2, height), # Middle vertical
            (width/4, height, 3*width/4, height), # Top horizontal
            (width/4, 0, 3*width/4, 0)     # Bottom horizontal
        ],
        'J': [
            (3*width/4, height/2, 3*width/4, height), # Upper vertical
            (width/4, 0, 3*width/4, 0),     # Bottom horizontal
            (width/4, 0, 0, height/4)       # Left curve
        ],
        'K': [
            (0, 0, 0, height),            # Left vertical
            (0, height/2, width, height),  # Upper diagonal
            (0, height/2, width, 0)        # Lower diagonal
        ],
        'L': [
            (0, height, 0, 0),            # Left vertical
            (0, 0, width, 0)              # Bottom horizontal
        ],
        'M': [
            (0, 0, 0, height),            # Left vertical
            (0, height, width/2, height/2),# Left diagonal
            (width/2, height/2, width, height), # Right diagonal
            (width, height, width, 0)      # Right vertical
        ],
        'N': [
            (0, 0, 0, height),            # Left vertical
            (0, height, width, 0),         # Diagonal
            (width, 0, width, height)      # Right vertical
        ],
        'O': [
            (width/4, height, 3*width/4, height), # Top horizontal
            (width/4, 0, 3*width/4, 0),    # Bottom horizontal
            (0, height/4, 0, 3*height/4),  # Left vertical
            (width, height/4, width, 3*height/4), # Right vertical
            (0, 3*height/4, width/4, height), # Top left curve
            (0, height/4, width/4, 0),     # Bottom left curve
            (width, 3*height/4, 3*width/4, height), # Top right curve
            (width, height/4, 3*width/4, 0) # Bottom right curve
        ],
        'P': [
            (0, 0, 0, height),            # Left vertical
            (0, height, 3*width/4, height),# Top horizontal
            (3*width/4, height, 3*width/4, height/2), # Right vertical
            (0, height/2, 3*width/4, height/2) # Middle horizontal
        ],
        'Q': [
            (width/4, height, 3*width/4, height), # Top horizontal
            (width/4, 0, 3*width/4, 0),    # Bottom horizontal
            (0, height/4, 0, 3*height/4),  # Left vertical
            (width, height/4, width, 3*height/4), # Right vertical
            (0, 3*height/4, width/4, height), # Top left curve
            (0, height/4, width/4, 0),     # Bottom left curve
            (width, 3*height/4, 3*width/4, height), # Top right curve
            (width, height/4, 3*width/4, 0), # Bottom right curve
            (width/2, height/4, width, 0)   # Diagonal tail
        ],
        'R': [
            (0, 0, 0, height),            # Left vertical
            (0, height, 3*width/4, height),# Top horizontal
            (3*width/4, height, 3*width/4, height/2), # Right vertical
            (0, height/2, 3*width/4, height/2), # Middle horizontal
            (width/2, height/2, width, 0)  # Diagonal
        ],
        'S': [
            (width, height, width/4, height), # Top horizontal
            (width/4, height, 0, 3*height/4), # Top curve
            (0, 3*height/4, width/4, height/2), # Middle top curve
            (width/4, height/2, 3*width/4, height/2), # Middle horizontal
            (3*width/4, height/2, width, height/4), # Middle bottom curve
            (width, height/4, 3*width/4, 0), # Bottom curve
            (3*width/4, 0, 0, 0)          # Bottom horizontal
        ],
        'T': [
            (width/2, 0, width/2, height), # Middle vertical
            (0, height, width, height)     # Top horizontal
        ],
        'U': [
            (0, height, 0, height/4),      # Left vertical
            (width, height, width, height/4), # Right vertical
            (0, height/4, width/4, 0),     # Bottom left curve
            (width/4, 0, 3*width/4, 0),    # Bottom horizontal
            (3*width/4, 0, width, height/4) # Bottom right curve
        ],
        'V': [
            (0, height, width/2, 0),      # Left diagonal
            (width/2, 0, width, height)    # Right diagonal
        ],
        'W': [
            (0, height, width/4, 0),      # Left diagonal
            (width/4, 0, width/2, height/2), # Middle left diagonal
            (width/2, height/2, 3*width/4, 0), # Middle right diagonal
            (3*width/4, 0, width, height)  # Right diagonal
        ],
        'X': [
            (0, 0, width, height),        # Forward diagonal
            (0, height, width, 0)         # Backward diagonal
        ],
        'Y': [
            (0, height, width/2, height/2), # Left diagonal
            (width, height, width/2, height/2), # Right diagonal
            (width/2, height/2, width/2, 0)  # Bottom vertical
        ],
        'Z': [
            (0, height, width, height),    # Top horizontal
            (width, height, 0, 0),         # Diagonal
            (0, 0, width, 0)              # Bottom horizontal
        ],
        ' ': [],  # Space - no lines
        '0': [
            (width/4, height, 3*width/4, height), # Top horizontal
            (width/4, 0, 3*width/4, 0),    # Bottom horizontal
            (0, height/4, 0, 3*height/4),  # Left vertical
            (width, height/4, width, 3*height/4), # Right vertical
            (0, 3*height/4, width/4, height), # Top left curve
            (0, height/4, width/4, 0),     # Bottom left curve
            (width, 3*height/4, 3*width/4, height), # Top right curve
            (width, height/4, 3*width/4, 0) # Bottom right curve
        ],
        '1': [
            (width/2, 0, width/2, height), # Vertical line
            (width/4, height, width/2, height), # Top horizontal
            (width/4, 0, 3*width/4, 0)    # Base
        ],
        '2': [
            (0, height, width, height),    # Top horizontal
            (width, height, width, height/2), # Right vertical
            (width, height/2, 0, 0),       # Diagonal
            (0, 0, width, 0)              # Bottom horizontal
        ],
        '3': [
            (0, height, width, height),    # Top horizontal
            (width, height, width, 0),     # Right vertical
            (0, 0, width, 0),             # Bottom horizontal
            (width/4, height/2, width, height/2) # Middle horizontal
        ],
        '4': [
            (3*width/4, 0, 3*width/4, height), # Right vertical
            (0, height, 0, height/2),     # Left vertical
            (0, height/2, width, height/2) # Middle horizontal
        ],
        '5': [
            (width, height, 0, height),    # Top horizontal
            (0, height, 0, height/2),      # Left vertical
            (0, height/2, width, height/2), # Middle horizontal
            (width, height/2, width, 0),   # Right vertical
            (width, 0, 0, 0)              # Bottom horizontal
        ],
        '6': [
    (width, height, width/4, height),       # Top horizontal
    (width/4, height, 0, height/2),        # Left curve downward
    (0, height/2, width/4, 0),             # Bottom-left curve
    (width/4, 0, width, 0),                # Bottom horizontal
    (width, 0, width, height/2),           # Right vertical
    (width, height/2, width/4, height/2)   # Middle connector
]




,

        '7': [
            (0, height, width, height),    # Top horizontal
            (width, height, 0, 0)         # Diagonal
        ],
        '8': [
    # Two simple boxes stacked
    # Top box
    (width/4, height, width, height),    # Top horizontal
    (width/4, height/2, width, height/2), # Middle horizontal
    (width/4, height, width/4, height/2),    # Left vertical top
    (width, height, width, height/2), # Right vertical top
    
    # Bottom box
    (width/4, height/2, width/4, 0),        # Left vertical bottom
    (width, height/2, width, 0),    # Right vertical bottom
    (width/4, 0, width, 0),             # Bottom horizontal
],

'9': [
    # Top circle (box)
    (width/4, height, width, height),    # Top horizontal
    (width/4, height, width/4, height/2),    # Left vertical 
    (width, height, width, height/2), # Right vertical top
    (width/4, height/2, width, height/2), # Middle horizontal
    
    # Straight line down
    (width, height/2, width/4, 0),    # Right vertical bottom
],

        '>': [
            (0, height/2, width/2, height/2),          # Horizontal line
            (width/2, height/2, width/2, height),      # Vertical line
            (width/2, height, width, height/2),        # Diagonal to tip
            (width, height/2, width/2, 0)             # Diagonal to base
        ],
        '<': [
            (width, height/2, 0, height/2),           # Horizontal line
            (0, height/2, width/4, 3*height/4),      # Diagonal pointing upwards
            (0, height/2, width/4, height/4)         # Diagonal pointing downwards
        ],
        '$': [
    # Circular arrow (¾ of a circle, starting from top-right going counter-clockwise)
    (width/2, height, width, height),        # Top right quarter
    (width, height, width, 3*height/4),      # Right side
    (width, height, width, height/2),        # Right side
    (width, height/2, 3*width/4, 0),        # Bottom right curve
    (3*width/4, 0, width/4, 0),             # Bottom
    (width/4, 0, 0, height/2),              # Bottom left curve
    (0, height/2, 0, height),               # Left side
    (0, height, width/2, height),            # Top left quarter
    (0, height, width/2, height),           # Top left quarter
    (width/2, height, width, height) ,        # Top
    (width, height, width, 3*height/4),      # Right side
    # Arrow head at top-right
    (width-width/4, height+height/4, width, height),  # Arrow diagonal up
    (width-width/4, height-height/4, width, height)   # Arrow diagonal down
],

'^': [
    # (hamburger menu)
    (0, height, width, height),              # Top line
    (0, height/2, width, height/2),          # Middle line
    (0, 0, width, 0),                        # Bottom line
]
}

def draw_Header(x, y, text, color=(1, 1, 1), height=30, width=20, point_size=2):
    lookupTable = LookUpTable(width, height)

    text = text.upper()
    

    spacing = width * 0.2
    
    # Current x
    current_x = x
    
    for char in text:
        # Skip unknown characters
        if char not in lookupTable:
            current_x += width + spacing
            continue

        # line segments for the character
        segments = lookupTable[char]
        

        for x1, y1, x2, y2 in segments:
            # relative coordinates to absolute coordinates
            abs_x1 = current_x + x1
            abs_y1 = y + y1
            abs_x2 = current_x + x2
            abs_y2 = y + y2
            

            drawMidpointLine(abs_x1, abs_y1, abs_x2, abs_y2, color, point_size)
        
        # Move to the next character
        current_x += width + spacing

    
############################# Controller Functions #############################
def drawGrid():
    global window_width, window_height
    glColor4f(white[0], white[1], white[2], 0.6)  
    glPointSize(1)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glBegin(GL_POINTS)
    for i in range(0, window_width, 40):
        for j in range(0, 700, 40):
            glVertex2f(i, j)
    glEnd()
    

def draw():
    global current_state
    if current_state == MENU_STATE:
        drawStartScreen()
    elif current_state == GAME_STATE:
        drawGameScreen()
        drawGrid()
    elif current_state == END_STATE:
        drawEndScreen()
    elif current_state == INSTRUCTION_STATE:
        drawInstructionScreen()
    
    glutPostRedisplay()
    

def animate():
    global current_game, game_started, move_speed
    if current_state == GAME_STATE and game_started and current_game:
        move_speed = 20


    glutPostRedisplay()

def keyPressed(key, x, y):
    global selected_item, current_state, current_game, move_speed
    
    if current_state == MENU_STATE:
        if key == b'\r':  # Enter key
            if selected_item == 0:
                startGame()
            elif selected_item == 1:
                showInstructions()
            elif selected_item == 2:
                exitGame()
    
    elif current_state == GAME_STATE and game_started:
        if key in [b'w', b'W']:  # Up
            current_game.move_player(0, move_speed)
        elif key in [b's', b'S']:  # Down
            current_game.move_player(0, -move_speed)
        elif key in [b'a', b'A']:  # Left
            current_game.move_player(-move_speed, 0)
        elif key in [b'd', b'D']:  # Right
            current_game.move_player(move_speed, 0)
    
def specialKeyPressed(key, x, y):
    global selected_item, current_state, current_game, game_started
    
    if current_state == MENU_STATE:
        # Menu navigation
        if key == GLUT_KEY_UP:
            selected_item = (selected_item - 1) % len(menu_items)
        elif key == GLUT_KEY_DOWN:
            selected_item = (selected_item + 1) % len(menu_items)
    glutPostRedisplay()

def mouseClicked(button, state, x, y):
    global selected_item, current_state, current_game

    converted_y = window_height - y
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if current_state == MENU_STATE:
            menu_y = 400
            for i in range(len(menu_items)):
                # Menu items
                if menu_y - 20 <= converted_y <= menu_y + 30: 
                    selected_item = i
                    if i == 0:
                        startGame()
                    elif i == 1:
                        showInstructions()
                    elif i == 2:
                        exitGame()
                    break
                menu_y -= menu_spacing
        
        elif current_state == INSTRUCTION_STATE:
            # If back button is clicked
            button_x, button_y = 290, 160
            button_width, button_height = 220, 50
            if (button_x <= x <= button_x + button_width and 
                window_height - (button_y + button_height) <= y <= window_height - button_y):
                current_state = MENU_STATE

        elif current_state == END_STATE:
            # If menu button is clicked
            button_x, button_y = 270, 300
            button_width, button_height = 270, 50
            if (button_x <= x <= button_x + button_width and 
                window_height - (button_y + button_height) <= y <= window_height - button_y):
                current_state = MENU_STATE

            # If restart button is clicked
            button_x, button_y = 270, 400
            button_width, button_height = 270, 50
            if (button_x <= x <= button_x + button_width and 
                window_height - (button_y + button_height) <= y <= window_height - button_y):
                current_game = None
                startGame()
    
    glutPostRedisplay()

############################# Initialization Functions #############################
def iterate():
    global window_width, window_height
    glViewport(0, 0, window_width, window_height) 
    glMatrixMode(GL_PROJECTION)  
    glLoadIdentity()       
    glOrtho(0, window_width, 0, window_height, 0.0, 1.0) 
    glMatrixMode(GL_MODELVIEW)   
    glLoadIdentity()            


def showScreen():
    global color
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
    glLoadIdentity()         
    iterate()
    draw()
    glutSwapBuffers()


############################# Menu Actions #############################
def startGame():
    global current_state, current_game, countdown_timer, game_started, last_update_time, game_won
    current_game = MazeRunner()
    current_state = GAME_STATE
    game_won = False
    game_started = False
    last_update_time = glutGet(GLUT_ELAPSED_TIME)

def showInstructions():
    global current_state
    current_state = INSTRUCTION_STATE

def exitGame():
    glutDestroyWindow(wind)
    sys.exit(0)


############################# Main Function #############################
glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(window_width, window_height) 
screen_width = glutGet(GLUT_SCREEN_WIDTH)
screen_height = glutGet(GLUT_SCREEN_HEIGHT)
window_x = (screen_width - window_width) // 2
window_y = (screen_height - window_height) // 2
glutInitWindowPosition(window_x, window_y)
wind = glutCreateWindow(b"Maze Runner")
glClearColor(black[0], black[1], black[2], black[3])
glutDisplayFunc(showScreen)
glutIdleFunc(animate)
glutKeyboardFunc(keyPressed) 
glutSpecialFunc(specialKeyPressed)
glutMouseFunc(mouseClicked)
glutMainLoop()