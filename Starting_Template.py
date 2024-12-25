############################# Libraries #############################
from OpenGL.GL import *       # Core OpenGL functions for rendering
from OpenGL.GLUT import *     # GLUT (Utility Toolkit) for windowing and event handling
from OpenGL.GLU import *      # GLU (Utility Library) for higher-level operations like camera setup
import random


############################# Global Vars #############################
window_Width = 1280
window_Height = 720

############################# Color Pallete #############################
black = [0, 0, 0, 1.0]
white = [1, 1, 1, 1.0]


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


############################# Main Functions #############################

def draw():
    pass

def animate():
    pass
    glutPostRedisplay()

# Params: which key was pressed, x and y coordinates of the mouse
def keyPressed(key, x, y):
    pass
    glutPostRedisplay()
    
def specialKeyPressed(key, x, y):
    pass
    glutPostRedisplay()

def mouseClicked(button, state, x, y):
    pass

    glutPostRedisplay()


############################# Initialization Functions #############################
def iterate():
    # Bezel size, first parameter is the x coordinate, second is the y coordinate, third is the width and fourth is the height
    global window_Width, window_Height
    glViewport(0, 0, window_Width, window_Height) 

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
    glOrtho(0, window_Width, window_Height, 0, 0.0, 1.0) 

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


############################# Main Function #############################

# Initialize the GLUT library
glutInit()    

# Set the display mode, we are here telling the GLUT library to use RGBA (Red, Green, Blue, Alpha) color space, by default it uses RGB color space
glutInitDisplayMode(GLUT_RGBA) 

# Set the window size
glutInitWindowSize(window_Width, window_Height) 

# Set the window position, 100 means 100 pixels from the left and 200 means 200 pixels from the top

glutInitWindowPosition(0, 0)

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
