import OpenGL, math, time
from OpenGL.GLUT import *
from OpenGL.GL import *
import Core

color_index = {'red':[1.0, 0.0, 0.0],
               'orange':[1.0, 0.3, 0.0],
               'yellow':[1.0, 1.0, 0.0],
               'green':[0.0, 1.0, 0.0],
               'blue':[0.0, 0.0, 1.0],
               'indigo':[0.44, 0, 1.0],
               'violet':[0.56, 0, 255]}

def drawCircle(x, y, radius):
  rad = 0.0
  glBegin(GL_POLYGON)
  while rad < 2*math.pi:
    glVertex2i(int(math.cos(rad)*radius+x),
               int(math.sin(rad)*radius+y))
    rad += 0.1
  glEnd()

def display():
  glClear(GL_COLOR_BUFFER_BIT)
  #draw planets
  for i in main_game.planets:
    color = color_index[i.alignment]
    glColor3f(color[0], color[1], color[2])
    drawCircle(i.x, i.y, 20)
  #draw transfers
  for transfer in main_game.transfers:
    color = color_index[main_game.planets[transfer.a].alignment]
    glColor3f(color[0], color[1], color[2])
    #draw transfer line
    glBegin(GL_LINE_STRIP)
    glVertex2i(int(transfer.apos[0]), int(transfer.apos[1]))
    glVertex2i(int(transfer.bpos[0]), int(transfer.bpos[1]))
    glEnd()
    #draw transfer load
    drawCircle(transfer.pos[0], transfer.pos[1], 15)
  glFlush()

def victoryGraphic(winner_alignment):
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos3f(290, 240, 0.0)
    winner_alignment = winner_alignment.upper()
    winner_alignment += " WINS!"
    for i in winner_alignment:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ctypes.c_int(ord(i)))
    glFlush()

game_clock = 0
def idle():
  global game_clock

  #victory condition
  planets = main_game.planets
  if len(planets) > 0:
    alignment = planets[0].alignment
    alignment_counter = 0
    for i in planets:
        if alignment == i.alignment:
            alignment_counter += 1
    #game over!
    if alignment_counter == len(planets):
        victoryGraphic(alignment)
        glutPostRedisplay()
    #continue!
    else:
        game_clock += 1
        if game_clock >= 500:
            game_clock = 0
            main_game.proliferatePlanets()
        main_game.incrementTransfers()
        main_game.AITurns()
        glutPostRedisplay()

def init(argv, ai_list):
  global main_game
  main_game = Core.Game(ai_list)

  #GL stuff
  glutInit(argv)
  glutInitDisplayMode(GLUT_RGB);
  glutInitWindowSize(640, 480)
  glutCreateWindow("Circle Conquest")
  glMatrixMode(GL_PROJECTION)
  glOrtho(0, 640, 0, 480, -1, 1)
  glViewport(0, 0, 640, 480)
  glMatrixMode(GL_MODELVIEW)
  glClearColor(0, 0, 0, 0)
  glutDisplayFunc(display)
  glutIdleFunc(idle)
  glutMainLoop()
