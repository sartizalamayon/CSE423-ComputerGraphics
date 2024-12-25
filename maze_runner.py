############################# Imports #############################
from OpenGL.GL import *       # Core OpenGL functions for rendering
from OpenGL.GLUT import *     # GLUT (Utility Toolkit) for windowing and event handling
from OpenGL.GLU import *      # GLU (Utility Library) for higher-level operations like camera setup
import sys
import random
import math


############################# Global Vars #############################
window_width = 800
window_height = 800
point_size = 3

############################# Color Pallete #############################
black = [0, 0, 0, 1.0]
white = [1, 1, 1, 1.0]
neon_blue = [0, 0.8, 1, 1.0]
neon_pink = [1, 0.2, 0.6, 1.0]
neon_green = [0.2, 1, 0.2, 1.0]
selected_color = [1, 1, 0, 1.0]  # Yellow for selected menu item

# Menu settings
menu_items = ["Start Game", "Instructions", "Exit"]
selected_item = 0  # Currently selected menu item
menu_spacing = 60  # Spacing between menu items

############################ Game Classes ############################
# Game states
MENU_STATE = 0
GAME_STATE = 1
END_STATE = 2
INSTRUCTION_STATE = 3
instructions = [
    "> Use arrow keys to move the player",
    "> Avoid traps and moving obstacles",
    "> Reach exit before timer runs out",
    "> Collect collectibles to unlock paths",
    "> Complete all levels to win the game"
]
current_game = None
current_state = MENU_STATE

# class for a perticular game instance, it contains the properties of a single game instance, when the user hit play button, a new instance of this class will be created
class MazeRunner:
    def __init__(self):
        self.state = MENU_STATE
        self.level = 1
        self.max_levels = 3
        self.player_pos = [400, 400]
        self.player_size = 20
        self.timer = 60
        self.last_time = 0
        self.maze_grid = []
        self.collectibles = []
        self.traps = []
        self.moving_obstacles = []

############################# Start Screen #############################
def drawStartScreen():
    # Draw the title "MAZE RUNNER"
    draw_Header(150, 500, "MAZE", neon_blue, 50, 40, 4)  # Draw "MAZE" in blue
    draw_Header(370, 500, "RUNNER", neon_pink, 50, 40, 4)  # Draw "RUNNER" in pink
    
    # Draw menu items
    y_position = 410
    for i, item in enumerate(menu_items):
        color = selected_color if i == selected_item else white
        # Center the text by calculating x position
        text_width = len(item) * 30  # Approximate width of text
        x_position = (window_width - text_width) // 2 + 30
        draw_Header(x_position, y_position, item, color, 30, 20, 2)
        y_position -= menu_spacing

############################# Game Screen #############################
def drawGameScreen():
    pass

############################# End Screen #############################
def drawEndScreen():
    pass

############################# Instruction Screen #############################
def drawInstructionScreen():
    # Draw Title
    draw_Header(180, 600, "INSTRUCTIONS", neon_pink, 40, 30, 3)
    
    # Draw instructions
    y_position = 520
    for i, text in enumerate(instructions):
        draw_Header(70, y_position, text, white, 15, 15, 2)
        y_position -= 60

    # Draw back button with glowing effect
    button_x, button_y = 290, 160
    button_width, button_height = 220, 50
    
    # Draw outer glow
    drawFilledPolygon([
        (button_x-5, button_y-5),
        (button_x-5, button_y+button_height+5),
        (button_x+button_width+5, button_y+button_height+5),
        (button_x+button_width+5, button_y-5)
    ], [neon_blue[0]*0.5, neon_blue[1]*0.5, neon_blue[2]*0.5, 0.5])
    
    # Draw button background
    drawFilledPolygon([
        (button_x, button_y),
        (button_x, button_y+button_height),
        (button_x+button_width, button_y+button_height),
        (button_x+button_width, button_y)
    ], neon_blue)
    
    # Draw button text
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
    # Draw the outline first
    drawPolygon(vertices, color)
    
    # Find min and max y coordinates
    min_y = int(min(y for _, y in vertices))
    max_y = int(max(y for _, y in vertices))
    
    # For each scanline
    for y in range(min_y, max_y + 1):
        intersections = []
        
        # Find intersections with each edge
        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]
            
            if min(y1, y2) <= y <= max(y1, y2) and y1 != y2:
                # Calculate x-intersection using line equation
                x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                intersections.append(x)
        
        # Sort intersections
        intersections.sort()
        
        # Draw horizontal lines between pairs of intersections
        for i in range(0, len(intersections) - 1, 2):
            if i + 1 < len(intersections):
                drawMidpointLine(int(intersections[i]), y, 
                               int(intersections[i + 1]), y, 
                               color)
                
def LookUpTable(width, height):
        return {'A': [
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
            (width, height, width/4, height), # Top horizontal
            (width/4, height, 0, 3*height/4), # Top curve
            (0, 3*height/4, 0, height/4),   # Left vertical
            (0, height/4, width/4, 0),      # Bottom curve
            (width/4, 0, 3*width/4, 0),     # Bottom horizontal
            (3*width/4, 0, width, height/4), # Right curve
            (0, height/2, width, height/2)   # Middle horizontal
        ],
        '7': [
            (0, height, width, height),    # Top horizontal
            (width, height, 0, 0)         # Diagonal
        ],
        '8': [
            (width/4, height, 3*width/4, height), # Top horizontal
            (width/4, 0, 3*width/4, 0),    # Bottom horizontal
            (0, height/4, 0, 3*height/4),  # Left vertical
            (width, height/4, width, 3*height/4), # Right vertical
            (0, 3*height/4, width/4, height), # Top left curve
            (0, height/4, width/4, 0),     # Bottom left curve
            (width, 3*height/4, 3*width/4, height), # Top right curve
            (width, height/4, 3*width/4, 0), # Bottom right curve
            (width/4, height/2, 3*width/4, height/2) # Middle horizontal
        ],
        '9': [
            (width/4, height, 3*width/4, height), # Top horizontal
            (3*width/4, height, width, 3*height/4), # Top right curve
            (width, 3*height/4, width, height/4),  # Right vertical
            (width, height/4, 3*width/4, 0),      # Bottom right curve
            (3*width/4, 0, width/4, 0),          # Bottom horizontal
            (width/4, 0, 0, height/4),           # Bottom left curve
            (width/4, height/2, width, height/2)  # Middle horizontal
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
        ]
}

def draw_Header(x, y, text, color=(1, 1, 1), height=30, width=20, point_size=2):
    # Example lookupTable with graph-based representation for letters 'A' and 'H'
    lookupTable = LookUpTable(width, height)

    # Convert text to uppercase since our lookup table is for uppercase letters
    text = text.upper()
    
    # Space between characters (can be adjusted)
    spacing = width * 0.2
    
    # Current x position
    current_x = x
    
    for char in text:
        # Skip unknown characters
        if char not in lookupTable:
            current_x += width + spacing
            continue

        # Get the line segments for the current character
        segments = lookupTable[char]
        
        # Draw each line segment of the character
        for x1, y1, x2, y2 in segments:
            # Convert relative coordinates to absolute coordinates
            abs_x1 = current_x + x1
            abs_y1 = y + y1
            abs_x2 = current_x + x2
            abs_y2 = y + y2
            
            # Draw the line using midpoint algorithm
            drawMidpointLine(abs_x1, abs_y1, abs_x2, abs_y2, color, point_size)
        
        # Move to the next character position
        current_x += width + spacing

    
############################# Controller Functions #############################

def drawGrid():
    global window_width, window_height
    glColor4f(white[0], white[1], white[2], white[3])
    glPointSize(1)
    glBegin(GL_POINTS)
    # draw a 4x4 grid
    for i in range(0, window_width, 200):
        for j in range(0, window_height, 20):
            glVertex2f(i, j)
    
    for i in range(0, window_width, 20):
        for j in range(0, window_height, 200):
            glVertex2f(i, j)

    
    

    glEnd()


def draw():
    global current_state
    drawGrid() # this is for visual purpose only, it will not be in the final game
    if current_state == MENU_STATE:
        drawStartScreen()
    elif current_state == GAME_STATE:
        drawGameScreen()
    elif current_state == END_STATE:
        drawEndScreen()
    elif current_state == INSTRUCTION_STATE:
        drawInstructionScreen()
    

def animate():
    glutPostRedisplay()

# Params: which key was pressed, x and y coordinates of the mouse
def keyPressed(key, x, y):
    global selected_item, current_state
    
    if current_state == MENU_STATE:
        if key == b'\r':  # Enter key
            if selected_item == 0:
                startGame()
            elif selected_item == 1:
                showInstructions()
            elif selected_item == 2:
                exitGame()
    glutPostRedisplay()
    
def specialKeyPressed(key, x, y):
    global selected_item
    
    if current_state == MENU_STATE:
        if key == GLUT_KEY_UP:
            selected_item = (selected_item - 1) % len(menu_items)
        elif key == GLUT_KEY_DOWN:
            selected_item = (selected_item + 1) % len(menu_items)
    
    glutPostRedisplay()

def mouseClicked(button, state, x, y):
    global selected_item, current_state
    
    # Convert window coordinates to OpenGL coordinates
    converted_y = window_height - y
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if current_state == MENU_STATE:
            # Calculate menu item positions
            menu_y = 400
            for i in range(len(menu_items)):
                if menu_y - 20 <= converted_y <= menu_y + 30:  # Height of menu item
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
            # Check if back button is clicked
            button_x, button_y = 290, 160
            button_width, button_height = 220, 50
            if (button_x <= x <= button_x + button_width and 
                window_height - (button_y + button_height) <= y <= window_height - button_y):
                current_state = MENU_STATE
    
    glutPostRedisplay()
############################# Initialization Functions #############################
def iterate():
    # Bezel size, first parameter is the x coordinate, second is the y coordinate, third is the width and fourth is the height
    # Here we are working with 1st cordinate only
    # x = 0 to window_width
    # y = 0 to window_height
    # starts from bottom left corner
    global window_width, window_height
    glViewport(0, 0, window_width, window_height) 

    # From here everything Projection related

    # Switch to the projection matrix (matrix that transforms 3D coordinates to 2D screen coordinates)
    glMatrixMode(GL_PROJECTION)  

    # Reset the projection matrix to the identity matrix
    glLoadIdentity()       

    # Besically set up axis, left, right, bottom, top, near, far
    # Parameters: left, right, bottom, top, near, far
    # left, right: where the x axis will start and end
    # bottom, top: where the y axis will start and end
    # near, far: where the z axis will start and end
    glOrtho(0, window_width, 0, window_height, 0.0, 1.0) 

    # Switch to the model-view matrix (for positioning objects in the scene
    glMatrixMode(GL_MODELVIEW)   

    # Reset the model-view matrix to its default state
    glLoadIdentity()            

# Here, we actually draw
def showScreen():
    global color
    # Clear the color buffer and depth buffer, projection related
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
    # Reset any transformations applied to the model-view matrix, projection related 
    glLoadIdentity()         
    # Setup relaed properties
    iterate()

    draw()
    glutSwapBuffers()


############################# Menu Actions #############################
def startGame():
    global current_state, current_game
    current_game = MazeRunner()
    current_state = GAME_STATE

def showInstructions():
    global current_state
    current_state = INSTRUCTION_STATE

def exitGame():
    glutDestroyWindow(wind)
    sys.exit(0)


############################# Main Function #############################

# Initialize the GLUT library
glutInit()    

# Set the display mode, we are here telling the GLUT library to use RGBA (Red, Green, Blue, Alpha) color space, by default it uses RGB color space
glutInitDisplayMode(GLUT_RGBA) 

# Set the window size
glutInitWindowSize(window_width, window_height) 

# Set the window position, 100 means 100 pixels from the left and 200 means 200 pixels from the top
# screen_width = glutGet(GLUT_SCREEN_WIDTH)
# screen_height = glutGet(GLUT_SCREEN_HEIGHT)
# window_x = (screen_width - window_width) // 2
# window_y = (screen_height - window_height) // 2
# glutInitWindowPosition(window_x, window_y)

glutInitWindowPosition(0,0)

# Besically the Window name
wind = glutCreateWindow(b"Maze Runner")

 # Set background color (R, G, B, Alpha)
glClearColor(black[0], black[1], black[2], black[3]) 

# This function is called continuously to update the screen,the more the processor speed, the more frames will be created in 1 second
glutDisplayFunc(showScreen)


# Now for animation, 
# This will call the animate function after every frame is drawed 
glutIdleFunc(animate)

# Keyboard function
# Keyborad has three categories
# 1. Normal: has ascii values
glutKeyboardFunc(keyPressed)

# 2. Special: has special keys like F1,up, Down, Home 
glutSpecialFunc(specialKeyPressed)

# 3. Mouse: has mouse clicks
glutMouseFunc(mouseClicked)

# To keep the program running
glutMainLoop()  