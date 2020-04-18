import numpy as np
import random
import util
from scipy.integrate import ode
win_width = 640
win_height = 480
center = [win_width, win_height]

class Simulation:
    def __init__(self, title, nact, npass, dt):
        self.paused = True
        self.title = title
        self.curTime = 0
        self.dt = dt
        self.nact = nact
        self.npass = npass
        self.actState = np.zeros([nact, 5], dtype = 'float32')
        # x y vx vy stamina for active moshers
        self.passState = np.zeros([npass, 5], dtype = 'float32')
        # x y vx vy stamina for passive moshers

    def set_actState(self, actState):
        self.actState = actState

    def set_passState(self, passState):
        self.passState = passState

    def getActiveList(self):
        actives = []
        for i in range(self.nact):
            actives.append(util.Mosher(self.actState[i],"active"))
        return actives

    def getPassiveList(self):
        passives = []
        for i in range(self.npass):
            passives.append(util.Mosher(self.passState[i], "passive"))
        return passives

    def set_time(self, cur_time=0):
        self.cur_time = cur_time

    def set_dt(self, dt):
        self.dt = dt

    def checkBoundsActive(self, i):
        #this will check physical bounds as well as stamina bounds
        if self.actState[i][0] < 15:
            self.actState[i][0] = 15
            self.actState[i][2] *= -1
        elif self.actState[i][0] > 625:
            self.actState[i][0] = 625
            self.actState[i][2] *= -1
        if self.actState[i][1] < 55:
            self.actState[i][1] = 55
            self.actState[i][3] *= -1
        elif self.actState[i][1] > 465:
            self.actState[i][1] = 465
            self.actState[i][3] *= -1
        if self.actState[i][4] < 0:
            self.actState[i][4] = 0

    def checkBoundsPassive(self, i):
        # checks stamina bounds too
        if self.passState[i][0] < 15:
            self.passState[i][0] = 15
        elif self.passState[i][0] > 625:
            self.passState[i][0] = 625
        if self.passState[i][1] < 55:
            self.passState[i][1] = 55
        elif self.passState[i][1] > 465:
            self.passState[i][1] = 465
        if self.passState[i][4] > 100:
            self.passState[i][4] = 100.00

    def step(self):
        '''
        this seems like a good place to check for boundry conditions
        '''
        self.cur_time += self.dt
        for i in range(self.actState.shape[0]):
            dist = util.calcPointDist(self.actState[i][:2], center)
            nudge = self.biasCollision(i, 0.0001 * dist)
            self.actState[i][0] += self.actState[i][2] * self.dt
            self.actState[i][1] += self.actState[i][3] * self.dt
            self.actState[i][2] += nudge[0]
            self.actState[i][3] += nudge[1]
            self.actState[i][4] -= self.dt * 3 * random.random()
            self.checkBoundsActive(i)

        for i in range(self.npass):
            self.passState[i][0] += self.passState[i][2] * self.dt
            self.passState[i][1] += self.passState[i][3] * self.dt
            self.passState[i][4] += self.dt * 2
            self.checkBoundsPassive(i)
        self.checkForCollision()

        #this for loop isn't part of the beforehand for loop because
        #passive passive mosher collisions involves undoing a timestep
        #and I need the random numbers to be the same to do that
        for i in range(self.npass):
            self.passState[i][2] = random.randrange(-14,15)
            self.passState[i][3] = random.randrange(-14,15)
        self.checkPassToAct()
        self.checkActToPass()
        

    def checkActToPass(self):
        upperLimit = self.nact
        for i in range(upperLimit):
            if i >= upperLimit:
                break
            stateThreshold = random.random()
            if self.actState[i][4] < stateThreshold and self.nact > self.npass / 10:
                print("Active to Passive")
                upperLimit -= 1
                temp = np.zeros(5, dtype = 'float32')
                for j in range(5):
                    temp[j] = self.actState[i][j]
                self.actState = np.delete(self.actState, i, 0)
                self.passState = np.append(self.passState, [temp], axis = 0)
                nudge = self.outOfMosh(i, 12)
                self.passState[self.npass][2] += nudge[0]
                self.passState[self.npass][3] += nudge[1]
                self.nact -= 1
                self.npass += 1

    def checkPassToAct(self):
        upperLimit = self.npass
        for i in range(upperLimit):
            if i >= upperLimit:
                break
            if self.passState[i][4] > 50 and random.random() > 0.75 and self.nact < (self.npass/6) :
                print("Passive to Active")
                upperLimit -= 1
                temp = np.zeros(5, dtype = 'float32')
                for j in range(5):
                    temp[j] = self.passState[i][j]
                self.passState = np.delete(self.passState, i, 0)
                self.actState = np.append(self.actState, [temp], axis = 0)
                self.actState[self.nact][4] += 30
                self.nact += 1
                self.npass -= 1 

    def checkForCollision(self):
        # we're just gonna not bother with P/P collisions for now
        # cuz they take too long & this gets SLOW & they don't add much
        '''
        for i in range(self.npass):
            for j in range(i, self.npass):
                pos1 = self.passState[i][:2]
                pos2 = self.passState[j][:2]
                dist = util.calcPointDist(pos1, pos2)
                if dist < 8 and dist > 0:
                    self.PassPassCollision(i, j)
        '''
        # this will do P/A collisions
        for i in range(self.npass):
            for j in range(self.nact):
                pos1 = self.passState[i][:2]
                pos2 = self.actState[j][:2]
                dist = util.calcPointDist(pos1, pos2)
                if dist < 16:
                    self.PassActCollision(i, j)

        for i in range(self.nact):
            for j in range(i, self.nact):
                pos1 = self.actState[i][:2]
                pos2 = self.actState[j][:2]
                if util.calcPointDist(pos1, pos2) < 8:
                    self.ActActCollision(i, j)

    def PassPassCollision(self, i, j):
        '''
        since we don't care much about passive moshers, we're gonna
        not focus much on this. If 2 passive moshers collide into
        each other then just undo the timestep. we don't care about
        the velocities because they're random and redone every step
        '''
        self.passState[i][0] -= self.passState[i][2] * self.dt
        self.passState[i][1] -= self.passState[i][3] * self.dt
        self.passState[j][0] -= self.passState[j][2] * self.dt
        self.passState[j][1] -= self.passState[j][3] * self.dt
        '''
        OOH! This is going to slow down things a lot since there is
        going to be more passive moshers than active, and therefore
        this is going to take a lot of time. Since P/P collisions are
        not really important, we can just like, not.
        '''


    def PassActCollision(self, i, j):
        '''
        passive i, active j. Bias active to be pushed towards center
        this is where i might break the laws of physics a little bit
        '''
        velx = abs(self.passState[i][2]) + abs(self.actState[j][2])
        vely = abs(self.passState[i][3]) + abs(self.actState[j][3])

        self.passState[i][2] = np.sign(self.passState[i][2]) * velx * 0.3

        self.passState[i][3] = np.sign(self.passState[i][3]) * vely * 0.3
        nudge = self.biasCollision(j, 0.15)

        self.actState[j][2] = np.sign(self.actState[j][2]) * velx * 0.7
        self.actState[j][2] += nudge[0]

        self.actState[j][3] = np.sign(self.actState[j][3]) * vely * 0.7
        self.actState[j][3] += nudge[1]


    def ActActCollision(self, i, j):
        
        velx = abs(self.actState[i][2]) + abs(self.actState[j][2])
        vely = abs(self.actState[i][3]) + abs(self.actState[j][3])

        self.actState[i][2] = np.sign(self.actState[i][2]) * velx * 0.5
        self.actState[j][2] = np.sign(self.actState[j][2]) * velx * 0.5

        self.actState[i][3] = np.sign(self.actState[i][3]) * vely * 0.5
        self.actState[j][3] = np.sign(self.actState[j][3]) * vely * 0.5


    def biasCollision(self, i, bias):
        '''
        the idea behind introducing bias is when in a typical mosh pit
        when an active colides with a passive, the passive will push the
        active towards the center of the pit. Actually doing the bias
        will be nudging the velocity vector to point towards the center by
        a percent
        '''
        randx = random.randrange(-75,75)
        randy = random.randrange(-75,75)
        distx = abs(self.actState[i][0] - ((win_width + randx)  / 2))
        disty = abs(self.actState[i][1] - ((win_height + randy) / 2))
        if self.actState[i][0] > (win_width/2):
            distx *= -1
        if self.actState[i][1] > (win_height/2):
            disty *= -1
        return [distx * bias, disty * bias]

    def outOfMosh(self, i, bias):
        distx = abs(self.passState[i][0] - (win_width / 2))
        disty = abs(self.passState[i][1] - (win_height / 2))
        if self.passState[i][0] < (win_width/2):
            distx *= -1
        if self.passState[i][1] < (win_height/2):
            disty *= -1
        return [distx * bias, disty * bias]

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def save(self, filename):
        pass

    def load(self, filename):
        pass