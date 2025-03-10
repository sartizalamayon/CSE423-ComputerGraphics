from OpenGL.GL import * 
from OpenGL.GLUT import *
from OpenGL.GLU import * 
import random


# Global Vars
window_Width = 1280
window_Height = 720

# For background Color
color = [1, 1, 1, 1.0]
border_color = [0, 0, 0, 1.0]

# Color Pallete
orange = [1, 0.5, 0, 1.0]
sand = [254/255,213/255,157/255, 1.0]
brown = [168/255, 82/255, 23/255, 1.0]
sky = [57/255, 187/255, 189/255, 1.0]
grey = [199/255, 197/255, 198/255, 1.0]


# House Points
big_roof_upper = [(419, 284), (600, 180), (730, 255)]
big_roof_lower = [(435, 304), (600, 208), (714,272)]

small_roof_upper = [(648, 336), (758, 226), (861, 329)]
small_roof_lower = [(666, 349), (758,257), (850,349)]

left_border = [(441, 539), (441, 299)]
right_border = [(836,494),(836,336)]
mid_border = [(680,494),(680,335)]
left_bottom_border = [(441,445),(680,445)]
big_stair = [(661, 539), (661, 517),(856, 517), (856, 539)]
small_stair = [(674, 517),(674, 494),(843, 494),(843, 517)]
door = [(720, 494), (720, 350), (797, 350), (797, 494)]
small_door = [(737, 494), (737, 367), (781, 367), (781, 494)]

window = [(510, 410), (510, 309),(630, 309), (630, 410)]
window_border = [(500, 420), (500, 300),(640, 300), (640, 420)]

chimney = [(474, 253), (474, 200), (533, 200), (533, 218)]
chimney_top = [(464, 200), (464, 170), (543, 170), (543, 200)]

# Rain
num_raindrops = 150
raindrops = []
raindrops = [{"x": random.randint(0, window_Width), "y": random.randint(0, window_Height)} for n in range(num_raindrops)]
raindrop_speed = 7
raindrop_color = [0.5,0.5, 1, 1]

def drawRaindrops():
    global raindrops, raindrop_color
    glColor4f(raindrop_color[0], raindrop_color[1], raindrop_color[2], raindrop_color[3])
    glLineWidth(3) 
    for drop in raindrops:
        glBegin(GL_LINES)
        glVertex2f(drop["x"], drop["y"])
        glVertex2f(drop["x"], drop["y"] + 12) 
        glEnd()

def drawLine(x, y): 
    glColor4f(border_color[0], border_color[1], border_color[2], border_color[3])
      
    glLineWidth(5)  

    glBegin(GL_LINES)
    glVertex2f(x[0], x[1])
    glVertex2f(y[0], y[1])
    glEnd()

def drawTriangle(x, y, z, color,):
    glColor4f(color[0], color[1], color[2], color[3])
    glBegin(GL_TRIANGLES)
    glVertex2f(x[0], x[1])
    glVertex2f(y[0], y[1])
    glVertex2f(z[0], z[1])
    glEnd()


def draw():
    # Sand background
    drawTriangle(mid_border[1], small_roof_lower[1], right_border[1], sand)
    drawTriangle(left_border[0], left_border[1], (mid_border[0][0], left_border[0][1]), sand)
    drawTriangle(left_border[1],big_roof_lower[2], (mid_border[0][0], left_border[0][1]), sand)
    drawTriangle(big_roof_lower[0], big_roof_lower[1], big_roof_lower[2], sand)

    drawTriangle(mid_border[0],mid_border[1], right_border[0], sand)
    drawTriangle(mid_border[1], right_border[1], right_border[0], sand)

    # Chimney
    drawTriangle(chimney[0], chimney[1], chimney[2], sand)
    drawTriangle(chimney[0], chimney[2], chimney[3], sand)

    # Roof Color
    drawTriangle(big_roof_upper[0], big_roof_upper[1], big_roof_lower[1], brown)
    drawTriangle(big_roof_upper[0], big_roof_lower[1], big_roof_lower[0], brown)
    drawTriangle(big_roof_upper[1], big_roof_upper[2], big_roof_lower[2], brown)
    drawTriangle(big_roof_upper[1], big_roof_lower[2], big_roof_lower[1], brown)

    drawTriangle(small_roof_upper[0], small_roof_upper[1], small_roof_lower[1], brown)
    drawTriangle(small_roof_upper[0], small_roof_lower[1], small_roof_lower[0], brown)
    drawTriangle(small_roof_upper[1], small_roof_upper[2], small_roof_lower[2], brown)
    drawTriangle(small_roof_upper[1], small_roof_lower[2], small_roof_lower[1], brown)

    # Upper Roof
    drawLine(big_roof_upper[0], big_roof_upper[1])
    drawLine(big_roof_upper[1], big_roof_upper[2])
    drawLine(big_roof_lower[0], big_roof_lower[1])
    drawLine(big_roof_lower[1], big_roof_lower[2])
    drawLine(big_roof_lower[0], big_roof_upper[0])
    # Lower Roof
    drawLine(small_roof_upper[0], small_roof_upper[1])
    drawLine(small_roof_upper[1], small_roof_upper[2])
    drawLine(small_roof_lower[0], small_roof_lower[1])
    drawLine(small_roof_lower[1], small_roof_lower[2])
    drawLine(small_roof_lower[0], small_roof_upper[0])
    drawLine(small_roof_lower[2], small_roof_upper[2])


    # Bootom left
    drawTriangle(left_border[0], left_bottom_border[0], left_bottom_border[1], orange)
    drawTriangle(left_border[0], left_bottom_border[1],(left_bottom_border[1][0], left_border[0][1]),orange)

    # Borders
    drawLine(left_border[0], left_border[1])
    drawLine(left_border[0], big_stair[0])
    drawLine(right_border[0], right_border[1])
    drawLine(mid_border[0], mid_border[1])
    drawLine(left_bottom_border[0], left_bottom_border[1])


    #Stairs
    drawTriangle(big_stair[0], big_stair[1], big_stair[2], grey)
    drawTriangle(big_stair[0], big_stair[2], big_stair[3], grey)
    drawLine(big_stair[0], big_stair[1])
    drawLine(big_stair[1], big_stair[2])
    drawLine(big_stair[2], big_stair[3])
    drawLine(big_stair[0], big_stair[3])
    
    drawTriangle(small_stair[0], small_stair[1], small_stair[2], grey)
    drawTriangle(small_stair[0], small_stair[2], small_stair[3], grey)
    drawLine(small_stair[0], small_stair[1])
    drawLine(small_stair[1], small_stair[2])
    drawLine(small_stair[2], small_stair[3])
    drawLine(small_stair[0], small_stair[3])
    


    # Door
    drawTriangle(door[0], door[1], door[2], orange)
    drawTriangle(door[0], door[2], door[3], brown)
    drawLine(door[0], door[1])
    drawLine(door[1], door[2])
    drawLine(door[2], door[3])
    drawLine(door[0], door[3])
    

    # Small Door
    drawTriangle(small_door[0], small_door[1], small_door[2], sky)
    drawTriangle(small_door[0], small_door[2], small_door[3], sky)
    drawLine(small_door[0], small_door[1])
    drawLine(small_door[1], small_door[2])
    drawLine(small_door[2], small_door[3])
    drawLine(small_door[0], small_door[3])

    # Window Border
    drawTriangle(window_border[0], window_border[1], window_border[2], orange)
    drawTriangle(window_border[0], window_border[2], window_border[3], brown)

    #Window Color
    drawTriangle(window[0], window[1], window[2], sky)
    drawTriangle(window[0], window[2], window[3], sky)

    # First Window
    drawLine(window[0], window[1])
    drawLine(window[1], window[2])
    drawLine(window[2], window[3])
    drawLine(window[0], window[3])

    # Window Border
    drawLine(window_border[0], window_border[1])
    drawLine(window_border[1], window_border[2])
    drawLine(window_border[2], window_border[3])
    drawLine(window_border[0], window_border[3])

    # Window Tint
    drawTriangle((window[0][0] + 10, window[0][1] - 10),(window[1][0]+10, window[1][1]+10),(window[3][0]-50, window[3][1]-10), color)

    # Chimney
    drawLine(chimney[0], chimney[1])
    drawLine(chimney[1], chimney[2])
    drawLine(chimney[2], chimney[3])

    # Chimney Top
    drawTriangle(chimney_top[0], chimney_top[1], chimney_top[2], brown)
    drawTriangle(chimney_top[0], chimney_top[2], chimney_top[3], brown)
    drawLine(chimney_top[0], chimney_top[1])
    drawLine(chimney_top[1], chimney_top[2])
    drawLine(chimney_top[2], chimney_top[3])
    drawLine(chimney_top[0], chimney_top[3])

    drawRaindrops()

def iterate():
    global window_Width, window_Height
    glViewport(0, 0, window_Width, window_Height) 
    glMatrixMode(GL_PROJECTION)  
    glLoadIdentity()       
    glOrtho(0, window_Width, window_Height, 0, 0.0, 1.0) 
    glMatrixMode(GL_MODELVIEW)   
    glLoadIdentity()            


def showScreen():
    global color
    # Projection related
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
    glLoadIdentity()   

    # Setup relaed properties
    iterate()
       
    draw()
    glutSwapBuffers()



def animate():
    global raindrops

    # Update Raindrop
    for drop in raindrops:
        drop["y"] += raindrop_speed  
        if drop["y"] > window_Height:  
            drop["y"] = 0
            drop["x"] = random.randint(0, window_Width) 

    glutPostRedisplay()

def keyPressed(key, x, y):
    print("x: ", x, "y: ", y)
    global color, border_color, raindrop_color

    if key == b"m":
        # Background Color
        color[0] += 0.25
        color[1] += 0.25
        color[2] += 0.25
        if color[0] >= 1 or color[1] >= 1 or color[2] >= 1:
            color = [1,1,1, 1.0]

        #Border Color
        border_color[0] -= 0.35
        border_color[1] -= 0.35
        border_color[2] -= 0.35
        if border_color[0] <= 0 or border_color[1] <= 0 or border_color[2] <= 0:
            border_color = [0,0,0, 1.0]
        
        #raindrop color for white backgrounds
        if color[0] >.25 and color[1] >.25 and color[2] >.25:
            raindrop_color = [0.5,0.5, 1, 1.0]

    if key == b"n":
        # Background Color
        color[0] -= 0.25
        color[1] -= 0.25
        color[2] -= 0.25
        if color[0] <= 0 or color[1] <= 0 or color[2] <= 0:
            color = [0,0,0, 1.0]

        #Border Color
        border_color[0] += 0.35
        border_color[1] += 0.35
        border_color[2] += 0.35
        if border_color[0] >= 1 or border_color[1] >= 1 or border_color[2] >= 1:
            border_color = [1,1,1, 1.0]
        
        #Special border + raindrop for black background
        if color == [0,0,0, 1.0]:
            border_color = [0,0,0, 1.0]
            raindrop_color = [173/255, 216/255, 230/255, 1.0]
        
        


    glClearColor(color[0], color[1], color[2], color[3]) 
    glutPostRedisplay()
    
def specialKeyPressed(key, x, y):
    global raindrops, raindrop_speed
    if key == GLUT_KEY_LEFT:
        # Rain to the left
        for drop in raindrops:
            drop["x"] -= 5
            drop["y"] += raindrop_speed 


    elif key == GLUT_KEY_RIGHT:
        # Rain to the right
        for drop in raindrops:
            drop["x"] += 5
            drop["y"] += raindrop_speed
    
    glutPostRedisplay()

def mouseClicked(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        print("Left mouse clicked at", x, y)
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        print("Right mouse clicked at", x, y)

    glutPostRedisplay()



# Main
glutInit()    
glutInitDisplayMode(GLUT_RGBA) 
glutInitWindowSize(window_Width, window_Height) 
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"House in Rainfall")
glClearColor(color[0], color[1], color[2], color[3]) 
glutDisplayFunc(showScreen)

# Animation and Keyobard and Mouse events
glutIdleFunc(animate)
glutKeyboardFunc(keyPressed)
glutSpecialFunc(specialKeyPressed)
glutMouseFunc(mouseClicked)

# Main Loop
glutMainLoop()  
