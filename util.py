import pygame
import numpy as np
import math
win_width = 640
win_height = 480
# set up the colors
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 0)
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)

class Mosher(pygame.sprite.Sprite):
    def __init__(self, state, mosherType):
        self.mosherType = mosherType
        self.width = 16
        self.height = 16
        self.state = np.zeros(5, dtype='float32')
        for i in range(5):
            self.state[i] = state[i]
        if mosherType == "active":
            self.color = RED
        elif mosherType == "passive":
            self.color = BLACK

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([self.width, self.height], flags=pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        cx = self.rect.centerx
        cy = self.rect.centery
        pygame.draw.circle(self.image, self.color, (int(self.width/2), int(self.height/2)), cx, cy)

    def setPos(self, pos):
        self.rect.x = pos[0] - self.rect.width//2
        self.rect.y = pos[1] - self.rect.height//2

def load_image(name):
    image = pygame.image.load(name)
    return image

def to_screen(x, y, winwidth, winheight):
    return winwidth//2 + x, winheight//2 - y

def from_screen(x, y, winwidth, winheight):
    return x - winwidth//2, winheight//2 - y

class MyText():
    def __init__(self, color, background=None, antialias=True, fontname="comicsansms", fontsize=32):
        pygame.font.init()
        self.font = pygame.font.SysFont(fontname, fontsize)
        self.color = color
        self.background = background
        self.antialias = antialias
    
    def draw(self, str1, screen, pos):
        text = self.font.render(str1, self.antialias, self.color, self.background)
        screen.blit(text, pos)

'''
i want active moshers to start in the center, so i'm going
to randomly generate a position and use a rejection method
this function will get the distance between the generated pos
and the center of the crowd, and will return true if it is
within a radius, and false if not

this was expanded to make sure that moshers don't start
inside other moshers. Keep that for the bathrooms, not the crowd

this was split into 2 functions, one for in and one for out.
I'm doing this 'cuz i'm getting weird stuff around the border of the
circle and i don't like it.
'''
def OutCenter(pos, otherpos):
    '''
    returns true if the position is in the center and not overlapping
    with a position already in the circle, returns false if either
    of these conditions are not satisfied
    '''
    x = abs(pos[0] - win_width / 2) * abs(pos[0] - win_width / 2)
    y = abs(pos[1] - win_height / 2) * abs(pos[1] - win_height / 2)
    dist = math.sqrt(x+y)
    if dist > 80:
        for curPos in otherpos:
            if calcPointDist(pos, curPos) < 15:
                return False
        return True
    else:
        return False


def InCenter(pos, otherpos):
    '''
    essentially the inverse of InCircle, returns true if out of the
    circle and not overlapping with any other positions, returns
    false otherwise.
    '''
    x = abs(pos[0] - win_width / 2) * abs(pos[0] - win_width / 2)
    y = abs(pos[1] - win_height/2) * abs(pos[1] - win_height/2)
    dist = math.sqrt(x+y)

    if dist < 100:
        for curPos in otherpos:
            if calcPointDist(pos, curPos) < 15:
                return False
        return True
    else:
        return False


def calcPointDist(pos, otherPos):
    distx = abs(pos[0] - otherPos[0]) * abs(pos[0] - otherPos[0])
    disty = abs(pos[1] - otherPos[1]) * abs(pos[1] - otherPos[1])
    dist = math.sqrt(distx + disty)
    return dist
