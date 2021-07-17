import pygame as pg
from pygame.draw import circle
from math import sin, cos


class Bullet:
    __slots__ = "BULLET_SURF", "MAP_SIZE", "SFX", "SFY", "GSTEP", "shooter", "x", "y", "theta", "vel", "changeInX", \
                "changeInY", "dmg", "deltaTime", "r", "d", "displacement"

    def __init__(self, BULLET_SURF, MAP_SIZE, GSTEP, shooter, x, y, theta, vel, weaponType, dmg):
        self.BULLET_SURF = BULLET_SURF
        self.MAP_SIZE = MAP_SIZE
        self.GSTEP = GSTEP

        self.shooter = shooter

        self.x = x
        self.y = y
        self.theta = theta
        self.vel = vel

        self.changeInX = self.vel * cos(theta)
        self.changeInY = self.vel * sin(theta)

        self.dmg = dmg

        self.deltaTime = 0

        if weaponType == "M1911":
            self.r = 4
            self.d = 8
        elif weaponType == "AWP":
            self.r = 7
            self.d = 14
        else:
            self.r = 5
            self.d = 10

        self.displacement = (0, 0)

    def getGrid(self):
        return int(self.x / self.GSTEP[0]), int(self.y / self.GSTEP[1])

    def getRect(self):
        return self.x - self.r, self.y - self.r, self.d, self.d

    def getMap(self):
        return self.x, self.y

    def inScreenView(self, DIMS):
        return self.x + self.displacement[0] + self.r > 0 and self.x + self.displacement[0] - self.r < DIMS[
            0] and self.y + self.r + self.displacement[1] > 0 and self.y - self.r + self.displacement[1] < DIMS[1]

    def update(self, displacement, dt, DIMS):
        self.displacement = displacement
        self.deltaTime = dt

        if self.inScreenView(DIMS):
            self.draw()
        self.move()

    def draw(self):
        circle(self.BULLET_SURF, (245, 176, 65), (self.x, self.y), self.r)
        circle(self.BULLET_SURF, (0, 0, 0), (self.x, self.y), self.r, width=int(self.r / 2))

    def move(self):
        '''
        This method updats the x and y positions of the bullet

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''

        self.x += self.changeInX * self.deltaTime
        self.y -= self.changeInY * self.deltaTime

    def checkBoundary(self):
        if (self.x < 0) or (self.y < 0) or (self.x > self.MAP_SIZE[0]) or (
                self.y > self.MAP_SIZE[1]):
            return True
        else:
            self.dmg -= 0.1
