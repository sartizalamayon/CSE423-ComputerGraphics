from OpenGL.GL import * 
from OpenGL.GLUT import *
from OpenGL.GLU import * 
import random
import time


# Global Vars
window_Width = 1280
window_Height = 720
# bl - tl - tr - br
box_cordinates = [(100, 620), (100,100), (1180, 100), (1180, 620)]
xMax = 1180
yMax = 620
xMin = 100
yMin = 100


# Velocity - tl - tr - br - bl
velocity = [(-1, 1), (1, 1), (1, -1), (-1, -1)]
ball_speed = 1
max_speed = 100
min_speed = 0.05 
frozen = False
isBlinking = False
blink = False
prev_blink_time = time.time()
blink_time = 0.3
point_size = 12

# For background Color
color = [1, 1, 1, 1.0]
black = [0, 0, 0, 1.0]

points = []

class Point:
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.ogColor = color
        self.velocity = velocity
        
    def blink(self):
        if self.color == self.ogColor:
            self.color = [0.0, 0.0, 0.0, 1.0]
        else:
            self.color = self.ogColor 

def drawPoint(x, y, color):
    global point_size
    glColor4f(color[0], color[1], color[2], color[3])
    glPointSize(point_size)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def drawTriangle(x, y, z, color,):
    glColor4f(0,0,0,1)
    glBegin(GL_TRIANGLES)
    glVertex2f(x[0], x[1])
    glVertex2f(y[0], y[1])
    glVertex2f(z[0], z[1])
    glEnd()


def draw():
    # Draw a box
    drawTriangle(box_cordinates[0], box_cordinates[1], box_cordinates[2], black)
    drawTriangle(box_cordinates[0], box_cordinates[2], box_cordinates[3], black)


    for point in points:
        drawPoint(point.x, point.y, point.color)
    
    if isBlinking:
        blinkThePoints()

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
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
    glLoadIdentity()   

    iterate()
    draw()
    glutSwapBuffers()



def animate():
    global points, xMax, yMax, xMin, yMin, ball_speed, frozen, blink
    if not frozen:
        for point in points:
            if ball_speed > max_speed:
                ball_speed = max_speed
            elif ball_speed < min_speed:
                ball_speed = min_speed
            
            #next position
            next_x = point.x + point.velocity[0] * ball_speed
            next_y = point.y + point.velocity[1] * ball_speed
            

            if next_x >= xMax:
                point.x = xMax
                point.velocity = (-point.velocity[0], point.velocity[1])
            elif next_x <= xMin:
                point.x = xMin
                point.velocity = (-point.velocity[0], point.velocity[1])
            else:
                point.x = next_x
                

            if next_y >= yMax:
                point.y = yMax
                point.velocity = (point.velocity[0], -point.velocity[1])
            elif next_y <= yMin:
                point.y = yMin
                point.velocity = (point.velocity[0], -point.velocity[1])
            else:
                point.y = next_y

    glutPostRedisplay()

def keyPressed(key, x, y):
    global ball_speed, frozen, isBlinking
    if key == b' ':
        frozen = not frozen
        isBlinking = False
    glutPostRedisplay()
    
def specialKeyPressed(key, x, y):
    global ball_speed, frozen
    if not frozen:  
        if key == GLUT_KEY_UP:
            ball_speed += 0.1  
        elif key == GLUT_KEY_DOWN:
            ball_speed -= 0.1
    glutPostRedisplay()

def blinkThePoints():
    global blink,blink_time, prev_blink_time, points
    current_time = time.time()
    if current_time - prev_blink_time >= blink_time: 
        for point in points:
            point.blink()
        blink = not blink
        prev_blink_time = current_time
    


def mouseClicked(button, state, x, y):
    global points, xMax, yMax, xMin, yMin, frozen, blink, isBlinking
    if not frozen: 
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            isBlinking = True
        elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            if x > xMin and x < xMax and y > yMin and y < yMax:
                random_color = [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), 1.0]
                temp = Point(x, y, random_color, random.choice(velocity))
                points.append(temp)
    glutPostRedisplay()



# Main
glutInit()    
glutInitDisplayMode(GLUT_RGBA) 
glutInitWindowSize(window_Width, window_Height) 
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"Amazing Box")
glClearColor(color[0], color[1], color[2], color[3]) 
glutDisplayFunc(showScreen)

# Animation and Keyobard and Mouse events
glutIdleFunc(animate)
glutKeyboardFunc(keyPressed)
glutSpecialFunc(specialKeyPressed)
glutMouseFunc(mouseClicked)

# Main Loop
glutMainLoop()  