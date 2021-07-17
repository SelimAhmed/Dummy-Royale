import pygame as pg
from pygame import Rect
from pygame.draw import rect
from time import time
from random import choice as rdChoice, randint as rdint
from math import sin, cos, pi
from Scripts.crate import Crate
from Scripts.extra_functions import *


class GameMap:
    def __init__(self, GAME_SURFACE: pg.Surface, loadFunc):
        """

        :type GAME_SURFACE: `Pygame Surface (Object)`
        """

        self.GAME_SURFACE = GAME_SURFACE
        self.GAME_SURFACE_DIMS = GAME_SURFACE.get_size()

        self.GSTEP = (100, 100)

        self.displacement = (0, 0)
        self.MAP_SIZE = (4000, 4000)

        self.sectorHoriEdges = (0, int(4000 / self.GSTEP[0]))
        self.sectorVertEdges = (0, int(4000 / self.GSTEP[1]))

        self.BG_SURFACE = pg.Surface(self.MAP_SIZE)

        self.ENTITY_SURF = pg.Surface(self.MAP_SIZE)
        self.ENTITY_SURF.set_colorkey((255, 255, 255))
        self.ENTITY_SURF.fill(self.ENTITY_SURF.get_colorkey())

        self.GROUND_WEAPON_SURF = pg.Surface(self.MAP_SIZE)
        self.GROUND_WEAPON_SURF.set_colorkey((0, 0, 0))
        self.GROUND_WEAPON_SURF.fill(self.GROUND_WEAPON_SURF.get_colorkey())

        self.BULLET_SURF = pg.Surface(self.MAP_SIZE)
        self.BULLET_SURF.set_colorkey((255, 255, 255))
        self.BULLET_SURF.fill(self.BULLET_SURF.get_colorkey())

        self.WEAPON_SURF = pg.Surface(self.MAP_SIZE)
        self.WEAPON_SURF.set_colorkey((132, 132, 132))
        self.WEAPON_SURF.fill(self.WEAPON_SURF.get_colorkey())

        # groundTile, gtSF = resizeImage("Assets/game/TileSets/RPG Nature Tileset.png", 5, scale)
        groundTile = pg.image.load("Assets/game/TileSets/RPG Nature Tileset.png")
        scaleTo = (groundTile.get_width() * (self.GSTEP[0] / 32), groundTile.get_height() * (self.GSTEP[1] / 32))
        groundTile, gtSF = scaleImageTo("Assets/game/TileSets/RPG Nature Tileset.png", scaleTo)
        groundTileInfo = [(round((i * 32) * gtSF[0]), round(64 * gtSF[1]), round(32 * gtSF[0]), round(32 * gtSF[1])) for
                          i in
                          range(3) if i != 1]

        crateTile, ctSF = resizeImage("Assets/game/TileSets/tilesheet_complete.png", 1.5, (1, 1))
        crateTileInfo = (1285 * ctSF[0], 261 * ctSF[1], 55 * ctSF[0], 55 * ctSF[1])

        self.crates = []
        self.cratesInNeedOfUpdating = []
        tempFont = pg.font.SysFont("Arial", 25);

        for x in range(0, self.MAP_SIZE[0], groundTileInfo[0][2]):
            for y in range(0, self.MAP_SIZE[1], groundTileInfo[0][3]):
                self.BG_SURFACE.blit(groundTile, (x, y), rdChoice(groundTileInfo))

        for x in range(0, self.MAP_SIZE[0] + groundTileInfo[0][2], groundTileInfo[0][2] * 3):
            pg.draw.line(self.BG_SURFACE, (100, 100, 100), (x, 0), (x, self.MAP_SIZE[1]), width=5)

        for y in range(0, self.MAP_SIZE[1] + groundTileInfo[0][3], groundTileInfo[0][3] * 3):
            pg.draw.line(self.BG_SURFACE, (100, 100, 100), (0, y), (self.MAP_SIZE[0], y), width=5)

        for x in range(0, self.MAP_SIZE[0], groundTileInfo[0][2] * 2):
            for y in range(0, self.MAP_SIZE[1], groundTileInfo[0][3] * 2):
                if groundTileInfo[0][2] < x < self.MAP_SIZE[0] - groundTileInfo[0][2] and groundTileInfo[0][3] < y < \
                        self.MAP_SIZE[1] - groundTileInfo[0][3]:
                    if rdint(1, 8) <= 2:
                        pos = (x, y)

                        sector = (int(pos[0] / self.GSTEP[0]), int(pos[1] / self.GSTEP[1]))
                        self.crates.append(Crate(GAME_SURFACE, self.ENTITY_SURF, (1, 1), pos, sector,
                                                 crateTile, crateTileInfo))

        self.weapons = [
            {
                "name": "M1911",
                "img": resizeImage("Assets/game/guns/M1911_side.png", 0.075)[0]
            },
            {
                "name": "Revolver",
                "img": resizeImage("Assets/game/guns/Revolver_side.png", 0.075)[0]
            },
            {
                "name": "AWP",
                "img": resizeImage("Assets/game/guns/AWP_side.png", 0.15)[0]
            }
        ]

        self.groundWeapons = []

        self.grid = self.genGrid(loadFunc)
        self.gridPosUpdates = []

    def genGrid(self, load):
        class gridSpot:
            __slots__ = "pos", "f", "h", "g", "neighbors", "previous", "wall"

            def __init__(self, pos: tuple, f: float, h: float, g: float, neighbors: list, previous: object, wall: bool):
                self.pos = pos
                self.f = f
                self.h = h
                self.g = g
                self.neighbors = neighbors
                self.previous = previous
                self.wall = wall

        cols = round(self.MAP_SIZE[0] / (self.GSTEP[0]))
        rows = round(self.MAP_SIZE[1] / (self.GSTEP[1]))

        grid = list(range(cols))

        numberOfColsIter = 100 / cols / 100

        dotDotDotCounter = 1
        animationDelay = time()

        for i in grid:
            grid[i] = list(range(rows))

        for i in range(cols):
            load((i + 1) * numberOfColsIter,
                 f"Loading Map{''.join(['.' for _ in range(dotDotDotCounter)])}")

            if time() - animationDelay > 0.5:
                dotDotDotCounter += 1

                if dotDotDotCounter > 3:
                    dotDotDotCounter = 0

                animationDelay = time()

            for j in range(rows):
                wall = False
                rect = pg.Rect(i * self.GSTEP[0], j * self.GSTEP[1], *self.GSTEP)

                for crate in self.crates:
                    crateRect = pg.Rect(crate.getGR())

                    if rect.colliderect(crateRect):
                        wall = True
                        break

                grid[i][j] = gridSpot((i, j), 0, 0, 0, [], None, wall)

        for i in range(cols):
            for j in range(rows):
                try:
                    if i < cols - 1:
                        grid[i][j].neighbors.append(grid[i + 1][j].pos)
                except IndexError:
                    pass

                try:
                    if i > 0:
                        grid[i][j].neighbors.append(grid[i - 1][j].pos)
                except IndexError:
                    pass

                try:
                    if j < rows - 1:
                        grid[i][j].neighbors.append(grid[i][j + 1].pos)
                except IndexError:
                    pass

                try:
                    if j > 0:
                        grid[i][j].neighbors.append(grid[i][j - 1].pos)
                except IndexError:
                    pass
                try:
                    if i > 0 and j > 0:
                        grid[i][j].neighbors.append(grid[i - 1][j - 1].pos)
                except IndexError:
                    pass

                try:
                    if i < cols - 1 and j > 0:
                        grid[i][j].neighbors.append(grid[i + 1][j - 1].pos)
                except IndexError:
                    pass

                try:
                    if i > 0 and j < rows - 1:
                        grid[i][j].neighbors.append(grid[i - 1][j + 1].pos)
                except IndexError:
                    pass

                try:
                    if i < cols - 1 and j < rows - 1:
                        grid[i][j].neighbors.append(grid[i + 1][j + 1].pos)
                except IndexError:
                    pass

        return grid

    def update(self, displacement):
        self.displacement = displacement

        self.drawBG()
        self.clearBulletRenders()
        self.clearWeaponRenders()
        self.drawEntities()

    def drawAfterUpdate(self):
        self.drawBullets()
        self.drawWeapons()

    def drawBG(self):
        self.GAME_SURFACE.blit(self.BG_SURFACE, (0, 0),
                               Rect(self.displacement[0] * -1, self.displacement[1] * -1, self.GAME_SURFACE_DIMS[0],
                                    self.GAME_SURFACE_DIMS[1]))

    def drawEntities(self):
        for crate in self.crates:
            crate.update(self.displacement)

        self.GAME_SURFACE.blit(self.ENTITY_SURF, (0, 0),
                               Rect(self.displacement[0] * -1, self.displacement[1] * -1, self.GAME_SURFACE_DIMS[0],
                                    self.GAME_SURFACE_DIMS[1]))

        self.GAME_SURFACE.blit(self.GROUND_WEAPON_SURF, (0, 0),
                               Rect(self.displacement[0] * -1, self.displacement[1] * -1, self.GAME_SURFACE_DIMS[0],
                                    self.GAME_SURFACE_DIMS[1]))

    def clearBulletRenders(self):
        rect(self.BULLET_SURF, self.BULLET_SURF.get_colorkey(),
             Rect(-self.displacement[0], -self.displacement[1], *self.GAME_SURFACE_DIMS))

    def drawBullets(self):
        self.GAME_SURFACE.blit(self.BULLET_SURF, (0, 0),
                               Rect(self.displacement[0] * -1, self.displacement[1] * -1, self.GAME_SURFACE_DIMS[0],
                                    self.GAME_SURFACE_DIMS[1]))

    def clearWeaponRenders(self):
        rect(self.WEAPON_SURF, self.WEAPON_SURF.get_colorkey(),
             Rect(-self.displacement[0], -self.displacement[1], *self.GAME_SURFACE_DIMS))

    def drawWeapons(self):
        self.GAME_SURFACE.blit(self.WEAPON_SURF, (0, 0),
                               Rect(self.displacement[0] * -1, self.displacement[1] * -1, self.GAME_SURFACE_DIMS[0],
                                    self.GAME_SURFACE_DIMS[1]))

    def updateGroundWeapons(self):
        pickedUp = []

        for weapon in self.groundWeapons:
            if weapon["picked_up"]:
                pickedUp.append((weapon, weapon["rect"]))
            else:
                if not weapon["blitted"]:
                    self.GROUND_WEAPON_SURF.blit(weapon["img"], weapon["pos"])
                    weapon["blitted"] = False
                else:
                    continue

        for pickUp in pickedUp:
            pg.draw.rect(self.GROUND_WEAPON_SURF, self.GROUND_WEAPON_SURF.get_colorkey(), pickUp[1])
            self.groundWeapons.remove(pickUp[0])

    def spawnWeapon(self, pos, sector, weaponName="", clip=None, ammo=None):
        idx = None

        if weaponName == "M1911":
            idx = 0
        elif weaponName == "Revolver":
            idx = 1
        elif weaponName == "AWP":
            idx = 2

        if idx is not None:
            weaponChoice = self.weapons[idx]
        else:
            weaponChoice = rdChoice(self.weapons)

        attainable = True
        if (clip and ammo) is not None:
            if clip == 0 and ammo == 0:
                attainable = False

        weaponSize = weaponChoice["img"].get_size()
        weaponRect = pg.Rect(pos[0] - weaponSize[0] / 2, pos[1] - weaponSize[1] / 2, weaponSize[0] * 2,
                             weaponSize[1] * 2)

        composition = {
            "name": weaponName if weaponName != "" else weaponChoice["name"],
            "pos": pos,
            "sector": sector,
            "rect": weaponRect,
            "img": weaponChoice["img"],
            "clip": clip,
            "ammo": ammo,
            "blitted": False,
            "picked_up": False,
            "attainable": attainable
        }

        self.groundWeapons.append(composition)
        self.updateGroundWeapons()

    def checkEntityOutOfMap(self, pos, r):
        # Collision top, left, bottom, right. (W, A, S, D)
        checks = [False for _ in range(4)]

        if pos[1] - r <= 0:
            checks[0] = True

        if pos[0] - r <= 0:
            checks[1] = True

        if pos[1] + r >= self.MAP_SIZE[1]:
            checks[2] = True

        if pos[0] + r >= self.MAP_SIZE[0]:
            checks[3] = True

        return tuple(checks)

    def checkEntityCrateCollision(self, pos: tuple, sector: tuple, r):
        sectors = getBoundingSectors(sector)

        collision = [False for _ in range(4)]
        points = tuple((pos[0] + r * cos(angle), pos[1] - r * sin(angle)) for angle in specialAngles)
        pointsCollided = [False for _ in range(len(points))]
        collidedObj = None

        for crate in self.crates:
            if crate.sector not in sectors:
                continue
            crateRect = pg.Rect(crate.getGR())

            pointsCollided = tuple(crateRect.collidepoint(point) for point in points)

            # Top collision
            if pointsCollided[12]:
                collision[2] = True

            elif True in pointsCollided[1:4]:
                collision[0] = True
                collision[3] = True

            elif True in pointsCollided[5:8]:
                collision[0] = True
                collision[1] = True

            # Left collision
            if pointsCollided[8]:
                collision[1] = True

            # Bottom collision
            if pointsCollided[4]:
                collision[0] = True

            elif True in pointsCollided[9:12]:
                collision[2] = True
                collision[1] = True

            elif True in pointsCollided[13:17]:
                collision[2] = True
                collision[3] = True

            # Right collision
            if pointsCollided[0]:
                collision[3] = True

            if True in collision:
                collidedObj = crate
                break

        return collision, pointsCollided, points, collidedObj
        # return collision, [False], None, None

    def checkContactCrateCollision(self, pos: tuple, sector: tuple, r, dmg, onePoint=False):
        # Center, left, top, right, bottom, TL, TR, BL, BR
        sectors = getBoundingSectors(sector)

        if onePoint:
            points = [(pos[0], pos[1])]
        else:
            points = [(pos[0] - r * cos(angle), pos[1] - r * sin(angle)) for angle in specialAngles[::4]]
            points.append((pos[0], pos[1]))

        for crate in self.crates:
            if crate.sector not in sectors:
                continue

            if True in [crate.getGR().collidepoint(point) for point in points]:
                self.cratesInNeedOfUpdating.append(crate)
                crate.health -= dmg

                if crate.health <= 0:
                    crate.deleteSelf()
                    self.crates.remove(crate)

                    self.gridPosUpdates.append(crate.getGrid())
                    self.spawnWeapon(crate.pos, crate.sector)
                    return 1

                return 2

    def checkEntityOverWeapon(self, pos: tuple, sector: tuple, r):
        # Center, left, top, right, bottom, TL, TR, BL, BR
        sectors = getBoundingSectors(sector)

        points = None
        rect = None

        if type(r) is not pg.Rect:
            points = tuple((pos[0] - r * cos(angle), pos[1] - r * sin(angle)) for angle in specialAngles)
        else:
            rect = r

        for weapon in self.groundWeapons:
            if weapon["sector"] not in sectors:
                continue

            if points is not None:
                if True in [weapon["rect"].collidepoint(point) for point in points]:
                    weapon["picked_up"] = True
                    self.updateGroundWeapons()
                    return weapon
                else:
                    continue
            elif rect is not None:
                if weapon["rect"].colliderect(rect):
                    weapon["picked_up"] = True
                    self.updateGroundWeapons()
                    return weapon
                else:
                    continue
            else:
                return
