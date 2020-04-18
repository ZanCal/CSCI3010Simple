import pygame, sys
import matplotlib.pyplot as plt
import numpy as np
import random

import sim as Simulation
import util


#the mosh pit only really works proper if there's enough people
#but adding enough people to fill up the screen slows stuff down
#so it might be best to reduce the screen size itself 
win_width = 640
win_height = 480

#nact is the number of active moshers 
nact = 30
#npass is the number of passive moshers
npass = nact * 9
#a nact:npass ratio of 1:8 looks about right, will probably tweak tho


def main():

    title = 'Mosh Simulation'
    pygame.init()
    clock = pygame.time.Clock()
    text = util.MyText(util.BLACK)

    activeMoshers = []
    passiveMoshers = []
    for i in range(nact):
        activeMoshers.append(util.Mosher([0,0,0,0,0],"active"))
    for i in range(npass):
        passiveMoshers.append(util.Mosher([0,0,0,0,0],"passive"))



    '''
    the following chunk of code is used for setting up inital postions
    of the moshers, using a rejection based technique
    '''

    curPosActive = []
    actState = np.zeros([nact, 5], dtype = 'float32')
    for i in range(nact):
        xpos = random.randrange(15,win_width - 15)
        ypos = random.randrange(55,win_height - 15)
        while(util.OutCenter([xpos, ypos], curPosActive)):
            xpos = random.randrange(15,win_width - 15)
            ypos = random.randrange(55,win_height - 15)
        activeMoshers[i].setPos([xpos, ypos])
        curPosActive.append([xpos,ypos])
        actState[i][0] = xpos
        actState[i][1] = ypos
        actState[i][4] = 100.00

    curPosPassive = []
    passState = np.zeros([npass, 5], dtype = 'float32')
    for i in range(npass):
        xpos = random.randrange(15, win_width-15)
        ypos = random.randrange(55, win_height-15)
        while(util.InCenter([xpos,ypos], curPosPassive)):
            xpos = random.randrange(15, win_width-15)
            ypos = random.randrange(55, win_height-15)
        passiveMoshers[i].setPos([xpos, ypos])
        curPosPassive.append([xpos,ypos])
        passState[i][0] = xpos
        passState[i][1] = ypos
        passState[i][4] = 0.00


    '''
    now for initial velocities. Passive moshers start with an init
    velocity of 0, and active moshers (for now) start with a random
    velocity, where the sum of the active mosher velocities is 0
    '''

    velX = 0
    velY = 0
    for i in range(nact):
        xvel = random.randrange(50,150)
        yvel = random.randrange(50,150)
        actState[i][2] = xvel
        actState[i][3] = yvel
        velX += xvel
        velY += yvel

    # comment this out and all the actives just flow to one end
    velX /= nact
    velY /= nact
    for i in range(nact):
        actState[i][2] -= velX
        actState[i][3] -= velY


    # set up drawing canvas
    # top left corner is (0,0) top right (640,0) bottom left (0,480)
    # and bottom right is (640,480).
    
    screen = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption(title)

    # setting up simulation
    sim = Simulation.Simulation(title, nact, npass, 0.3333)
    sim.set_time(0.0)
    sim.set_actState(actState)
    sim.set_passState(passState)

    print('--------------------------------')
    print('Usage:')
    print('Press (r) to start/resume simulation')
    print('Press (p) to pause simulation')
    print('Press (q) to quit')
    print('Press (space) to step forward simulation when paused')
    print('--------------------------------')
    while True:
        
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            sim.pause()
            continue
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            sim.resume()
            continue
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            break
        else:
            pass

        # clear the background, and draw the sprites
        screen.fill(util.WHITE)

        if nact != sim.nact or npass != sim.npass:
            activeMoshers = sim.getActiveList()
            passiveMoshers = sim.getPassiveList()
            
        for i in range(sim.nact):
            activeMoshers[i].setPos(sim.actState[i][:2])
            temp = pygame.sprite.Group(activeMoshers[i])
            temp.update()
            temp.draw(screen)
        for i in range(sim.npass):
            passiveMoshers[i].setPos(sim.passState[i][:2])
            temp = pygame.sprite.Group(passiveMoshers[i])
            temp.update()
            temp.draw(screen)


            
        text.draw("Time(seconds) = %f" % sim.cur_time, screen, (10,10))
        #text.draw("x = %f" % sim.state[0], screen, (10,40))
        #text.draw("y = %f" % sim.state[1], screen, (10,70))
        
        pygame.display.flip()

        # update simulation
        if not sim.paused:
            sim.step()
            
        else:
            pass
    
    pygame.quit()
    sys.exit(0)

if __name__ == '__main__':
    main()
