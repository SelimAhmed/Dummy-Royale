import pygame as pg
from pygame.mouse import get_pressed as mouseGetPreseed
from pygame.key import get_pressed as keyGetPressed

from Scripts.gun import Gun
from Scripts.bullet import Bullet

from time import time
from math import cos, sin

defaultSurface = pg.Surface((10, 10))
defaultSurface.set_colorkey((132, 132, 132))
defaultSurface.fill(defaultSurface.get_colorkey())


class M1911(Gun):
    def __init__(self, GAME_SURFACE: pg.Surface, WEAPONSURF: pg.Surface, BULLETSURF: pg.Surface, GSTEP: tuple,
                 pos: tuple,
                 shooter: object,
                 clip=1,
                 ammo=1):

        self.range = 400
        self.mobility = 1 / 1.5

        self.GAME_SURFACE = GAME_SURFACE
        self.WEAPONSURF = WEAPONSURF
        self.BULLETSURF = BULLETSURF
        self.GSTEP = GSTEP

        self.pos = pos

        self.shooter = shooter

        self.angle = 0

        self.AI = True if "enemy" in str(type(shooter)) else False
        self.AITimeout = time()
        self.selected = True

        self.weaponID = "M1911"

        self.shootCT = time()
        self.fRate = 0.4
        self.mag = 16
        self.clip = clip if clip is not None else self.mag
        self.ammo = ammo if ammo is not None else 52

        self.reloadTime = 1
        self.reloadCT = time()
        self.reloading = False

        self.bulletDmg = 15
        self.bulletVel = 16
        self.bulletLoc = None

        imageTop = pg.image.load("assets/game/guns/M1911_top.png").convert()
        self.imageTop = pg.transform.scale(imageTop, (round(imageTop.get_size()[0] / 7.5),
                                                      round(imageTop.get_size()[1] / 7.5)))

        imageSide = pg.image.load("assets/game/guns/M1911_side.png")
        self.imageSide = pg.transform.scale(imageSide,
                                            (round(imageSide.get_size()[0] / 4),
                                             round(imageSide.get_size()[1] / 4)))
        self.imageSideDims = self.imageSide.get_size()

        self.wTop, self.hTop = self.imageTop.get_size()
        self.wSide, self.hSide = self.imageSide.get_size()

        self.SURFACE = pg.transform.scale(defaultSurface, (self.wTop, self.hTop))

        # Blit the imageTop to the surface
        self.SURFACE.blit(self.imageTop, (0, 0))

        self.mouseWasDown = False

        self.displacement = (0, 0)

        super().__init__(pos, shooter)

    def update(self, pos: tuple, angle: float, displacement: tuple):
        self.bulletLoc = pos
        self.displacement = displacement

        if self.AI is False or self.shooter.inCameraView:
            self.parentUpdate(pos, angle)

        if not self.reloading:
            if self.clip > 0:
                if not self.AI:
                    self.checkInput()
                self.reloadCT = time()
            elif self.ammo > 0:
                self.reloading = True
                self.reload()
        else:
            self.reload()

    def checkInput(self, AIOverride=False):
        if AIOverride:
            mouse = True
        else:
            mouse = True in mouseGetPreseed()

        keys = keyGetPressed()
        keyR = keys[pg.K_r]
        keyQ = keys[pg.K_q]

        if not self.reloading:
            if (mouse or keyQ) and not self.mouseWasDown:
                if self.clip > 0:
                    self.shoot()
                    self.AITimeout = time()
                else:
                    self.reloading = True
            else:
                if (not mouse and not keyQ) and self.mouseWasDown:
                    self.mouseWasDown = False

        if keyR and self.clip != self.mag:
            self.reloading = True

        if self.AI and self.mouseWasDown and time() - self.AITimeout > self.fRate:
            self.mouseWasDown = False

    def shoot(self):
        if time() - self.shootCT > self.fRate:
            # bx = self.x + self.shooter.body["r"] * cos(self.angle)
            # by = self.y - self.shooter.body["r"] * sin(self.angle)
            bx = self.bulletLoc[0] + self.shooter.body["r"] * cos(self.angle)
            by = self.bulletLoc[1] - self.shooter.body["r"] * sin(self.angle)

            self.shooter.bullets.append(
                Bullet(self.BULLETSURF, self.shooter.MAP_SIZE, self.GSTEP, self.shooter, bx, by,
                       self.angle, self.bulletVel, self.weaponID,
                       self.bulletDmg))
            # pg.mixer.Sound.play(self.gunshot)

            self.clip -= 1
            self.mouseWasDown = True
            self.shootCT = time()

            if not self.AI:
                self.shooter.forceUIUpdate = True


class Revolver(Gun):
    def __init__(self, GAME_SURFACE: pg.Surface, WEAPONSURF: pg.Surface, BULLETSURF: pg.Surface, GSTEP: tuple,
                 pos: tuple,
                 shooter: object,
                 clip=6,
                 ammo=32):
        self.range = 800
        self.mobility = 1 / 2

        self.GAME_SURFACE = GAME_SURFACE
        self.WEAPONSURF = WEAPONSURF
        self.BULLETSURF = BULLETSURF
        self.GSTEP = GSTEP

        self.pos = pos

        self.shooter = shooter

        self.angle = 0

        self.AI = True if "enemy" in str(type(shooter)) else False
        self.AITimeout = time()
        self.selected = True

        self.weaponID = "Revolver"

        self.shootCT = time()
        self.fRate = 1.3
        self.mag = 6
        self.clip = clip if clip is not None else self.mag
        self.ammo = ammo if ammo is not None else 32

        self.reloadTime = 0.5
        self.reloadCT = time()
        self.reloading = False

        self.bulletDmg = 27
        self.bulletVel = 12
        self.bulletLoc = None

        imageTop = pg.image.load("assets/game/guns/revolver_top.png").convert()
        self.imageTop = pg.transform.scale(imageTop, (round(imageTop.get_size()[0] / 4.5),
                                                      round(imageTop.get_size()[1] / 7.5)))

        imageSide = pg.image.load("assets/game/guns/Revolver_side.png")
        self.imageSide = pg.transform.scale(imageSide,
                                            (round(imageSide.get_size()[0] / 4),
                                             round(imageSide.get_size()[1] / 4)))
        self.imageSideDims = self.imageSide.get_size()

        self.wTop, self.hTop = self.imageTop.get_size()
        self.wSide, self.hSide = self.imageSide.get_size()

        self.SURFACE = pg.transform.scale(defaultSurface, (self.wTop, self.hTop))

        # Blit the imageTop to the surface
        self.SURFACE.blit(self.imageTop, (0, 0))

        self.mouseWasDown = False

        self.displacement = (0, 0)

        super().__init__(pos, shooter)

    def update(self, pos: tuple, angle: float, displacement: tuple):
        self.displacement = displacement
        self.bulletLoc = pos

        if self.AI is False or self.shooter.inCameraView:
            self.parentUpdate(pos, angle)

        if not self.reloading:
            if self.clip > 0:
                if not self.AI:
                    self.checkInput()
                self.reloadCT = time()
            elif self.ammo > 0:
                self.reloading = True
                self.reload()
        else:
            self.reload()

    def checkInput(self, AIOverride=False):
        if AIOverride:
            mouse = True
        else:
            mouse = True in mouseGetPreseed()

        keys = keyGetPressed()
        keyR = keys[pg.K_r]
        keyQ = keys[pg.K_q]

        if not self.reloading:
            if (mouse or keyQ) and not self.mouseWasDown:
                if self.clip > 0:
                    self.shoot()
                    self.AITimeout = time()
                else:
                    self.reloading = True
            else:
                if (not mouse and not keyQ) and self.mouseWasDown:
                    self.mouseWasDown = False

        if keyR and self.clip != self.mag:
            self.reloading = True

        if self.AI and self.mouseWasDown and time() - self.AITimeout > self.fRate:
            self.mouseWasDown = False

    def shoot(self):
        if time() - self.shootCT > self.fRate:
            # bx = self.x + self.shooter.body["r"] * cos(self.angle)
            # by = self.y - self.shooter.body["r"] * sin(self.angle)
            bx = self.bulletLoc[0] + self.shooter.body["r"] * cos(self.angle)
            by = self.bulletLoc[1] - self.shooter.body["r"] * sin(self.angle)

            self.shooter.bullets.append(
                Bullet(self.BULLETSURF, self.shooter.MAP_SIZE, self.GSTEP, self.shooter, bx, by,
                       self.angle, self.bulletVel, self.weaponID,
                       self.bulletDmg))

            self.clip -= 1
            self.mouseWasDown = True
            self.shootCT = time()

            if not self.AI:
                self.shooter.forceUIUpdate = True


class AWP(Gun):
    def __init__(self, GAME_SURFACE: pg.Surface, WEAPONSURF: pg.Surface, BULLETSURF: pg.Surface, GSTEP: tuple,
                 pos: tuple,
                 shooter: object,
                 clip=3,
                 ammo=15):

        self.range = 800
        self.mobility = 1 / 2.5

        self.GAME_SURFACE = GAME_SURFACE
        self.WEAPONSURF = WEAPONSURF
        self.BULLETSURF = BULLETSURF
        self.GSTEP = GSTEP

        self.pos = pos

        self.shooter = shooter

        self.AI = True if "enemy" in str(type(shooter)) else False
        self.AITimeout = time()
        self.selected = True

        self.weaponID = "AWP"

        self.shootCT = time()
        self.fRate = 1
        self.mag = 5
        self.clip = clip if clip is not None else self.mag
        self.ammo = ammo if ammo is not None else 15

        self.reloadTime = 2
        self.reloadCT = time()
        self.reloading = False

        self.bulletDmg = 40
        self.bulletVel = 20
        self.bulletLoc = None

        imageTop = pg.image.load("assets/game/guns/AWP_top.png").convert()
        self.imageTop = pg.transform.scale(imageTop,
                                           (round(imageTop.get_size()[0] / 2.25),
                                            round(imageTop.get_size()[1] / 4.5)))

        imageSide = pg.image.load("assets/game/guns/AWP_side.png")
        self.imageSide = pg.transform.scale(imageSide, (200, 60))
        self.imageSideDims = self.imageSide.get_size()

        self.wTop, self.hTop = self.imageTop.get_size()
        self.wSide, self.hSide = self.imageSide.get_size()

        self.SURFACE = pg.transform.scale(defaultSurface, (self.wTop, self.hTop))

        # Blit the imageTop to the surface
        self.SURFACE.blit(self.imageTop, (0, 0))

        self.HOTKEYSURFACE = pg.Surface((self.wSide, self.hSide))
        self.HOTKEYSURFACE.fill((255, 255, 255))
        self.HOTKEYSURFACE.set_colorkey((255, 255, 255))
        self.HOTKEYSURFACE.blit(self.imageSide, (0, 0))

        self.mouseWasDown = False

        self.displacement = (0, 0)

        super().__init__(pos, shooter)

    def update(self, pos: tuple, angle: float, displacement=(0, 0)):
        self.bulletLoc = pos
        self.displacement = displacement

        if self.AI is False or self.shooter.inCameraView:
            self.parentUpdate(pos, angle)

        if not self.reloading:
            if self.clip > 0:
                if not self.AI:
                    self.checkInput()
                self.reloadCT = time()
            elif self.ammo > 0 and self.selected:
                self.reloading = True
                self.reload()
        else:
            if self.selected:
                self.reload()

    def checkInput(self, AIOverride=False):
        if AIOverride:
            mouse = True
        else:
            mouse = True in mouseGetPreseed()

        keys = keyGetPressed()
        keyR = keys[pg.K_r]
        keyQ = keys[pg.K_q]

        if not self.reloading:
            if (mouse or keyQ) and not self.mouseWasDown:
                if self.clip > 0:
                    self.shoot()
                    self.AITimeout = time()
                else:
                    self.reloading = True
            else:
                if (not mouse and not keyQ) and self.mouseWasDown:
                    self.mouseWasDown = False

        if keyR and self.clip != self.mag:
            self.reloading = True

        if self.AI and self.mouseWasDown and time() - self.AITimeout > self.fRate:
            self.mouseWasDown = False

    def shoot(self):
        if time() - self.shootCT > self.fRate:
            # bx = self.x + self.shooter.body["r"] * cos(self.angle)
            # by = self.y - self.shooter.body["r"] * sin(self.angle)
            bx = self.bulletLoc[0] + self.shooter.body["r"] * cos(self.angle)
            by = self.bulletLoc[1] - self.shooter.body["r"] * sin(self.angle)

            self.shooter.bullets.append(
                Bullet(self.BULLETSURF, self.shooter.MAP_SIZE, self.GSTEP, self.shooter, bx, by,
                       self.angle, self.bulletVel, self.weaponID,
                       self.bulletDmg))

            self.clip -= 1
            self.mouseWasDown = True
            self.shootCT = time()

            if not self.AI:
                self.shooter.forceUIUpdate = True
