import pygame as pg
from pygame.draw import *


class Crate:
    def __init__(self, SCREEN: pg.Surface, SURFACE: pg.Surface, scale: tuple, pos: tuple, sector: tuple, img: pg.image,
                 imgRect: tuple):
        self.SCREEN = SCREEN
        self.SCREEN_DIMS = SCREEN.get_size()

        self.healthRenderDistX = 200 * scale[0]
        self.healthRenderDistY = 200 * scale[1]

        self.SURFACE = SURFACE

        self.SFX, self.SFY = scale
        self.displacement = (0, 0)

        self.pos = pos
        self.sector = sector

        self.img = img
        self.imgRect = imgRect
        self.w, self.h = imgRect[2:4]
        self.RENDERSURFACE = pg.Surface((imgRect[2], imgRect[3]))
        self.RENDERSURFACE.set_colorkey((255, 255, 255))
        self.RENDERSURFACE.fill(self.RENDERSURFACE.get_colorkey())

        self.health = 75
        self.maxHealth = self.health

        """
            Chest Status:
                0: not blitted
                1: blitted
        """
        self.status = 0
        self.previousStatus = -1

        self.needsUpdating = False
        self.blitted = False

    def inCameraView(self, d: tuple):
        """
        :param d: displacement
        :return:
        """
        # return True
        return (self.pos[0] + self.imgRect[2] + d[0] >= self.SCREEN_DIMS[0] / 2 - self.healthRenderDistX) and (
                self.pos[0] - self.imgRect[2] + d[0] <= self.SCREEN_DIMS[0] / 2 + self.healthRenderDistX) and (
                       self.pos[1] + self.imgRect[3] + d[1] >= self.SCREEN_DIMS[1] / 2 - self.healthRenderDistY) and (
                       self.pos[1] - self.imgRect[3] + d[1] <= self.SCREEN_DIMS[1] / 2 + self.healthRenderDistY)

    def getMap(self):
        return self.pos

    def getCenter(self):
        return self.pos[0] + self.imgRect[2] / 2, self.pos[1] + self.imgRect[3] / 2

    def getGR(self):
        """
            This function will return the position along with the width, and height.
        :return: tuple
        """

        return pg.Rect(*self.pos, *self.imgRect[2:4])

    def getGrid(self):
        return self.sector

    def update(self, displacement):
        self.displacement = displacement
        self.draw()

    def draw(self, forceUpdate=False):
        updated = False

        if self.status != self.previousStatus or forceUpdate:
            self.RENDERSURFACE.blit(self.img, (0, 0), self.imgRect)

            self.previousStatus = self.status

            if not forceUpdate:
                updated = True

        if self.inCameraView(self.displacement):
            # Health bar
            rect(self.SCREEN, (236, 112, 99), (
                self.pos[0] + self.displacement[0], (self.pos[1] - 40 * self.SFY) + self.displacement[1],
                self.imgRect[2] * (self.health / self.maxHealth),
                20 * self.SFX))

            # Health bar background
            rect(self.SCREEN, (0, 0, 0), (
                self.pos[0] + self.displacement[0], (self.pos[1] - 40 * self.SFY) + self.displacement[1],
                self.imgRect[2],
                20 * self.SFX),
                 width=round(2 * self.SFX + 2 * self.SFY))

        if updated:
            self.RENDERSURFACE.fill(self.RENDERSURFACE.get_colorkey())
            self.draw(True)

        if not self.blitted:
            self.SURFACE.blit(self.RENDERSURFACE, (self.pos[0], self.pos[1]))
            self.blitted = True

    def deleteSelf(self):
        pg.draw.rect(self.SURFACE, self.SURFACE.get_colorkey(), (self.pos[0], self.pos[1], *self.imgRect[2:4]))
