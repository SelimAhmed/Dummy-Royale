import json
import os
import sys
from copy import deepcopy
from math import pi, sin, cos, atan2
from random import randint, choice as rdChoice
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
from threading import Thread
from time import time

from pygame import draw, display, time as pyTime

from Scripts.button import *
from Scripts.enemy import Enemy
from Scripts.extra_functions import specialAngles, getBoundingSectors
from Scripts.game_map import GameMap
from Scripts.player import Player


def compareDiDist(a: tuple, b: tuple, compareVal: tuple):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 <= (compareVal[0] + compareVal[1]) ** 2


def setEnemyGrid(entitiesList: list, enemiesList: list, cratesList: list, groundWeaponsList: list, grid):
    try:
        enemies = 100 / len(enemiesList) / 100
    except ZeroDivisionError:
        return

    dotDotDotCounter = 1
    animationDelay = time()

    for idx, enemy in enumerate(enemiesList):
        load((idx + 1) * enemies, f"Generating enemies{''.join(['.' for _ in range(dotDotDotCounter)])}")

        if time() - animationDelay > 0.5:
            dotDotDotCounter += 1

            if dotDotDotCounter > 3:
                dotDotDotCounter = 0

            animationDelay = time()

        enemy.grid = deepcopy(grid)

        enemy.crateList = cratesList
        enemy.enemiesList = entitiesList
        enemy.groundWeaponsList = groundWeaponsList

        entitiesList.append(enemy)


def load(status: float, msg: str = ""):
    ev = pg.event.poll()

    if ev.type == pg.QUIT:
        sys.exit()

    elif ev.type == pg.KEYDOWN:
        if ev.key == pg.K_ESCAPE:
            sys.exit()

    SCREEN.fill((0, 0, 0))

    draw.rect(SCREEN, (118, 215, 196), pg.Rect(100 * SFX, HEIGHT - 200 * SFY, (WIDTH - 200 * SFX) * status, 50 * SFY),
              border_radius=int(4 * SFX + 4 * SFY))
    draw.rect(SCREEN, (211, 84, 0), pg.Rect(100 * SFX, HEIGHT - 200 * SFY, (WIDTH - 200 * SFX), 50 * SFY),
              width=int(5 * SFX + 5 * SFY), border_radius=int(4 * SFX + 4 * SFY))

    loadingText = DEFAULT_FONT.render(f"Loading {round(status * 100, 2)}%", 1, (215, 219, 221))
    loadingMsg = DEFAULT_FONT.render(msg, 1, (255, 255, 255))

    blitText(SCREEN, loadingText, (100 * SFX, HEIGHT - 100 * SFY))
    blitText(SCREEN, loadingMsg, (100 * SFX, HEIGHT - 250 * SFY))

    display.flip()


def main():
    """
        Game states
        1: intro,
        2: game,
        3: game over,
        4: character adjustments,
        5: help screen
        6: settings (possibly)
    """
    gamestate = 1
    SCALE = (SFX, SFY)

    # Variables for game state: intro (1)
    toGameScreenBtn = Button(SCREEN, WIDTH / 2, HEIGHT - 100 * SFY, (300 * SFX, 150 * SFY), (86, 101, 115), "Play!",
                             BTN_LARGE_FONT, (255, 255, 255), alignX="c", alignY="b", btnRound=int(5 * SFX + 5 * SFY))

    toHelpScreenBtn = Button(SCREEN, 300 * SFX, HEIGHT - 150 * SFY, (200 * SFX, 100 * SFY), (86, 101, 115), "Help!",
                             BTN_SMALL_FONT, (255, 255, 255), alignX="l", alignY="b", btnRound=int(5 * SFX + 5 * SFY))

    toCustomizeScreenBtn = Button(SCREEN, WIDTH - 300 * SFX, HEIGHT - 150 * SFY, (200 * SFX, 100 * SFY), (86, 101, 115),
                                  "Customize!", BTN_SMALL_FONT, (255, 255, 255), alignX="r", alignY="b",
                                  btnRound=int(5 * SFX + 5 * SFY))

    # Variables for the game
    DEFAULT_SCREEN_SIZE = (1920, 1080)
    GAME_SURFACE = pg.Surface(DEFAULT_SCREEN_SIZE)
    GS_WIDTH, GS_HEIGHT = GAME_SURFACE.get_size()

    numOfEnemies = 99
    gameMap = None
    storm = None
    player = None
    enemies = None
    entities = None
    bullets = None
    displacement = None
    bulletEntityColl = None
    spectating = None

    continueBtn = Button(GAME_SURFACE, 150, GS_HEIGHT - 150, (300, 150), (86, 101, 115), "Continue!",
                         BTN_SMALL_FONT, (255, 255, 255), alignX="l", alignY="b", btnRound=10, scale=(SFX, SFY))

    # Variables for game over screen
    toHomeScreenBtn = Button(SCREEN, WIDTH / 2, HEIGHT - 250 * SFY, (300 * SFX, 150 * SFY), (40, 116, 166), "Home",
                             BTN_LARGE_FONT, (255, 255, 255), alignX="c", alignY="b", btnRound=int(10 * SFX + 10 * SFY))

    quitBtn = Button(SCREEN, WIDTH / 2, HEIGHT - 50 * SFY, (300 * SFX, 150 * SFY), (231, 76, 60), "Quit",
                     BTN_LARGE_FONT, (255, 255, 255), alignX="c", alignY="b", btnRound=int(10 * SFX + 10 * SFY))

    placementText = None

    # Variables for costume screen
    customizeBuyBtn = Button(SCREEN, WIDTH - 75 * SFX, HEIGHT - 100 * SFY, (200 * SFX, 100 * SFY), (22, 160, 133),
                             "Buy",
                             BTN_SMALL_FONT, (255, 255, 255), alignX="r", alignY="b", btnRound=int(5 * SFX + 5 * SFY))

    customizeBackBtn = Button(SCREEN, 75 * SFX, HEIGHT - 100 * SFY, (200 * SFX, 100 * SFY), (86, 101, 115), "Back",
                              BTN_SMALL_FONT, (255, 255, 255), alignX="l", alignY="b", btnRound=int(5 * SFX + 5 * SFY))

    selected = None
    onColor = None

    currentColor = tuple(data["colors"][data["colorSelected"][0]][data["colorSelected"][1]]["rgb"])
    playerColor = currentColor

    # Variables for help screen
    helpHomeBtn = Button(SCREEN, 75 * SFX, HEIGHT - 100 * SFY, (200 * SFX, 100 * SFY), (86, 101, 115), "Home",
                         BTN_LARGE_FONT, (255, 255, 255), alignX="l", alignY="b", btnRound=int(5 * SFX + 5 * SFY))

    infoMsg = "You are on an island surrounded by dark abys,\nYour only goal is to kill. After all, that's the only way to survive.\nEquipped with nothing, you'll need to break crates to find weapons\nor if you're brave enough, you can punch your way to victory."
    infoMsgList = infoMsg.split("\n")
    renderedInfoText = [HELP_FONT.render(msg, True, (255, 255, 255)) for msg in infoMsgList]

    controlMsg = "WASD or Arrow Keys To Move\nF Key To Pick Up Weapons\nR Key To Reload\nMouse Button or Q Key To Punch/Shoot\n1, 2, 3 Num Keys To Switch Weapons (1 Is Always Fists)\nESC To Quit"
    controlMsgList = controlMsg.split("\n")
    renderedControlText = [DEFAULT_FONT.render(msg, True, (255, 255, 255)) for msg in controlMsgList]

    while 1:
        ev = pg.event.poll()
        FPS = clock.tick(ATTEMPTED_FPS)
        dt = FPS * 0.001 * TARGETED_FPS

        if ev.type == pg.QUIT:
            sys.exit()

        elif ev.type == pg.KEYDOWN:
            if ev.key == pg.K_ESCAPE:
                sys.exit()

        if gamestate == 1:
            SCREEN.fill((44, 62, 80))

            # State change checks:
            if toGameScreenBtn.update(ev):
                def punchEntityCollision(pos: tuple, r: int, puncher: object):
                    points = tuple((pos[0] - r * cos(angle), pos[1] - r * sin(angle)) for angle in specialAngles[::4])
                    puncherSectors = getBoundingSectors(puncher.sector)
                    collided = False

                    for idx, entity in enumerate(entities):
                        if entity is puncher or entity.sector not in puncherSectors:
                            continue

                        for point in points:
                            if compareDiDist(point, entity.getMap(), (r, entity.body["r"])):
                                entity.health -= 15
                                entity.healthRegenerateTime = time()

                                if idx != 0:
                                    entity.enemyTarget = puncher
                                    entity.priority = 3
                                    entity.healthRegenerateTime = time()

                                    puncher.priority = 3
                                    puncher.enemyTarget = entity

                                collided = True
                                break

                        if collided:
                            break

                def bulletEntityColl(pos: tuple, bulletSector, r: int, dmg: float, shooter: object):
                    collided = False
                    bulletSectors = getBoundingSectors(bulletSector)

                    for idx, entity in enumerate(entities):
                        if entity.sector not in bulletSectors or bullet.shooter is entity:
                            continue

                        if compareDiDist(pos, entity.getMap(), (r, entity.body["r"])):
                            entity.health -= dmg
                            entity.healthRegenerateTime = time()

                            if idx > 0:
                                shooterAlive = shooter in entities

                                if shooterAlive:
                                    if entity.enemyTarget:
                                        # if entity.getDist(entity.getMap(),
                                        #                   entity.enemyTarget.getMap()) > entity.getDist(
                                        #     entity.getMap(), shooter.getMap()):
                                        entity.enemyTarget = shooter
                                    else:
                                        entity.enemyTarget = shooter

                                    entity.priority = 3

                                    shooter.priority = 3
                                    shooter.enemyTarget = entity

                            collided = True
                            break

                    return collided

                # Variables for game state: game (2)
                gameMap = GameMap(GAME_SURFACE, load)

                displacement = [(GS_WIDTH / 2 - gameMap.MAP_SIZE[0] / 2), (GS_HEIGHT / 2 - gameMap.MAP_SIZE[1] / 2)]

                bullets = []

                player = Player(GAME_SURFACE, gameMap.WEAPON_SURF, gameMap.BULLET_SURF, gameMap.MAP_SIZE, playerColor,
                                (SFX, SFY),
                                displacement,
                                gameMap.GSTEP,
                                (gameMap.checkEntityOutOfMap, gameMap.checkEntityCrateCollision,
                                 gameMap.checkContactCrateCollision,
                                 punchEntityCollision, gameMap.checkEntityOverWeapon, gameMap.spawnWeapon), bullets)

                # storm = Storm(GAME_SURFACE, gameMap.MAP_SIZE, player)

                entities = [player]

                enemies = [
                    Enemy(GAME_SURFACE, gameMap.WEAPON_SURF, gameMap.BULLET_SURF, i + 1,
                          data["colors"][rdChoice(tuple(data["colors"].keys()))][randint(0, 8)]["rgb"],
                          gameMap.MAP_SIZE, gameMap.GSTEP,
                          (randint(100, gameMap.MAP_SIZE[0] - 100), randint(100, gameMap.MAP_SIZE[1] - 100)), (
                              gameMap.checkEntityCrateCollision, gameMap.checkContactCrateCollision,
                              punchEntityCollision,
                              gameMap.checkEntityOverWeapon, gameMap.spawnWeapon), bullets)
                    for i in range(numOfEnemies)]

                enemyGrid = Thread(target=setEnemyGrid,
                                   args=(entities, enemies, gameMap.crates, gameMap.groundWeapons, gameMap.grid))

                enemyGrid.start()
                enemyGrid.join()

                for enemy in enemies:
                    enemy.findNearestCrate()

                gamestate = 2

            elif toHelpScreenBtn.update(ev):
                gamestate = 5

            elif toCustomizeScreenBtn.update(ev):
                currentColor = None
                gamestate = 4
        elif gamestate == 2:
            rect(GAME_SURFACE, (0, 0, 0), (0, 0, GS_WIDTH, GS_HEIGHT))
            gameMap.update(displacement)

            for bullet in bullets:
                bullet.update(displacement, dt, (GS_WIDTH, GS_HEIGHT))

                pos = bullet.getMap()
                sector = bullet.getGrid()

                if bullet.dmg <= 0:
                    bullets.remove(bullet)

                elif sector[0] in gameMap.sectorHoriEdges and sector[1] in gameMap.sectorVertEdges:
                    if bullet.checkBoundary():
                        bullets.remove(bullet)

                elif gameMap.checkContactCrateCollision(pos, sector, bullet.r, bullet.dmg, True):
                    bullets.remove(bullet)

                elif bulletEntityColl(pos, sector, bullet.r, bullet.dmg, bullet.shooter):
                    bullets.remove(bullet)

            for enemy in enemies:
                enemy.update(displacement, dt)

            if player.alive:
                newDisplacement = player.update(dt)
            else:
                if player in entities and len(entities) > 1:
                    placementText = GAME_LARGE_FONT.render(f"You placed #{len(entities)}", 1, (255, 255, 255))
                    entities.remove(player)
                elif len(enemies):
                    if spectating is None or spectating not in enemies:
                        spectating = rdChoice(enemies)

                    newDisplacement = (GS_WIDTH / 2 - spectating.getMap()[0], GS_HEIGHT / 2 - spectating.getMap()[1])

            gameMap.drawAfterUpdate()

            for enemy in enemies:
                enemy.draw()

                if enemy.alive is False:
                    enemy.dropLoot()
                    entities.remove(enemy)
                    enemies.remove(enemy)

            player.draw()
            if player.alive:
                player.displayUI()
            else:
                if continueBtn.update(ev) or len(entities) <= 0:
                    gamestate = 3

                spectatingText = GAME_LARGE_FONT.render("Currently spectating", 1, (255, 255, 255))
                blitText(GAME_SURFACE, spectatingText, (GS_WIDTH / 2 - spectatingText.get_width() / 2, 10))

            if len(entities) == 1:
                if not entities[0].alive:
                    if entities[0] is player:
                        placementText = GAME_LARGE_FONT.render("You placed #1", 1, (255, 255, 255))

                    gamestate = 3
                    continue

                entities[0].forceStop = True

            # After all game entities have been rendered
            if len(gameMap.gridPosUpdates):
                for enemy in enemies:
                    for pos in gameMap.gridPosUpdates:
                        enemy.grid[pos[0]][pos[1]].wall = False

                gameMap.gridPosUpdates.clear()

            PLAYERS_ALIVE_TEXT = GAME_INFO_FONT.render(f"Players Remaining {len(entities)}", 1, (255, 255, 255))

            blitText(GAME_SURFACE, PLAYERS_ALIVE_TEXT, (GS_WIDTH - PLAYERS_ALIVE_TEXT.get_width() - 10, 10))
            SCREEN.blit(pg.transform.smoothscale(GAME_SURFACE, (WIDTH, HEIGHT)), (0, 0))

            displacement = newDisplacement
        elif gamestate == 3:
            SCREEN.fill((39, 55, 70))

            if toHomeScreenBtn.update(ev):
                gamestate = 1

            elif quitBtn.update(ev):
                sys.exit()

            blitText(SCREEN, placementText, (WIDTH / 2 - placementText.get_width() / 2, 50 * SFY))
        elif gamestate == 4:
            SCREEN.fill((44, 62, 80))
            mousePos = pg.mouse.get_pos()
            x, y = 300 * SFX, HEIGHT / 2
            r = 75 * SFX + 75 * SFY

            angle = atan2(mousePos[1] - y, mousePos[0] - x)

            pos1 = x + r * cos(angle - pi / 4), y + r * sin(angle - pi / 4)
            pos2 = x + r * cos(angle + pi / 4), y + r * sin(angle + pi / 4)

            coinsText = DEFAULT_FONT.render(f"Coins: ${data['coins']}", 1, (255, 255, 255))

            # Mock player
            circle(SCREEN, currentColor if currentColor else playerColor, (x, y), r)
            circle(SCREEN, (0, 0, 0), (x, y), r, width=int(5 * SFX + 5 * SFY))

            circle(SCREEN, currentColor if currentColor else playerColor, pos1, (25 * SFX + 25 * SFY))
            circle(SCREEN, (0, 0, 0), pos1, (25 * SFX + 25 * SFY), width=int(5 * SFX + 5 * SFY))

            circle(SCREEN, currentColor if currentColor else playerColor, pos2, (25 * SFX + 25 * SFY))
            circle(SCREEN, (0, 0, 0), pos2, (25 * SFX + 25 * SFY), width=int(5 * SFX + 5 * SFY))

            if onColor is None:
                for idx, (key, val) in enumerate(data["colors"].items()):
                    if idx < 3:
                        x = 2 - idx
                        y = 0
                    elif idx < 6:
                        x = 5 - idx
                        y = 1
                    else:
                        x = 8 - idx
                        y = 2

                    bgSurf = pg.Surface(((25 * SFX + 25 * SFY) * 2, (25 * SFX + 25 * SFY) * 2))
                    bgSurf.set_colorkey((0, 0, 0))
                    bgSurf.fill(bgSurf.get_colorkey())

                    posX = (WIDTH - 75 * SFX - (125 * SFX) * x)
                    xyOffset = (25 * SFX + 25 * SFY)
                    posY = (300 * SFY + 125 * SFY * y)

                    if (posX - mousePos[0]) ** 2 + (posY - mousePos[1]) ** 2 < xyOffset ** 2:
                        bgSurf.set_alpha(255)

                        if ev.type == pg.MOUSEBUTTONDOWN:
                            onColor = key
                    else:
                        bgSurf.set_alpha(150)

                    circle(bgSurf, tuple(val[4]["rgb"]), (bgSurf.get_width() / 2, bgSurf.get_height() / 2),
                           (25 * SFX + 25 * SFY))

                    SCREEN.blit(bgSurf, (posX - xyOffset, posY - xyOffset))
                    circle(SCREEN, (0, 0, 0), (posX, posY), (30 * SFX + 30 * SFY), width=int(5 * SFX + 5 * SFY))
            else:
                for idx, val in enumerate(data["colors"][onColor]):
                    if idx < 3:
                        x = 2 - idx
                        y = 0
                    elif idx < 6:
                        x = 5 - idx
                        y = 1
                    else:
                        x = 8 - idx
                        y = 2

                    bgSurf = pg.Surface(((25 * SFX + 25 * SFY) * 2, (25 * SFX + 25 * SFY) * 2))
                    bgSurf.set_colorkey((0, 0, 0))
                    bgSurf.fill(bgSurf.get_colorkey())

                    posX = (WIDTH - 75 * SFX - (125 * SFX) * x)
                    xyOffset = (25 * SFX + 25 * SFY)
                    posY = (300 * SFY + 125 * SFY * y)

                    if (posX - mousePos[0]) ** 2 + (posY - mousePos[1]) ** 2 < xyOffset ** 2:
                        bgSurf.set_alpha(255)

                        if ev.type == pg.MOUSEBUTTONDOWN:
                            selected = idx

                            currentColor = tuple(data["colors"][onColor][selected]["rgb"])
                    else:
                        bgSurf.set_alpha(150)

                    circle(bgSurf, tuple(val["rgb"]), (bgSurf.get_width() / 2, bgSurf.get_height() / 2),
                           (25 * SFX + 25 * SFY))

                    SCREEN.blit(bgSurf, (posX - xyOffset, posY - xyOffset))
                    circle(SCREEN, (0, 0, 0), (posX, posY), (30 * SFX + 30 * SFY), width=int(5 * SFX + 5 * SFY))

            if onColor and selected is not None:
                color = data["colors"][onColor][selected]
                if color["unlocked"] is False:

                    if data["coins"] > color["price"]:
                        purchasable = True
                        msg = f"You do not own {str(onColor).capitalize()} {selected + 1}. Purchase? ${color['price']}"
                    else:
                        purchasable = False
                        msg = f"Not enough coins to purchase {str(onColor).capitalize()} {selected + 1}."

                    msg = DEFAULT_FONT.render(msg, 1, (255, 255, 255))

                    blitText(SCREEN, msg, (WIDTH - msg.get_width() - 75 * SFX, HEIGHT - 300 * SFY))

                    if purchasable:
                        if customizeBuyBtn.update(ev):
                            color["unlocked"] = True
                            data["coins"] -= color["price"]
                            data["colorSelected"] = [onColor, selected]

                            updateData()

            if customizeBackBtn.update(ev):
                if onColor is None:
                    gamestate = 1

                elif selected is not None:
                    if data["colors"][onColor][selected]["unlocked"]:
                        currentColor = data["colors"][onColor][selected]["rgb"]
                        playerColor = currentColor
                        data["colorSelected"] = [onColor, selected]
                        updateData()

                    onColor = None
                    selected = None
                else:
                    onColor = None
                    selected = None

            blitText(SCREEN, coinsText, (WIDTH - coinsText.get_width() - 75 * SFX, 75 * SFY))
        elif gamestate == 5:
            SCREEN.fill((50, 50, 50))

            for i, text in enumerate(renderedInfoText):
                SCREEN.blit(text, (WIDTH / 2 - text.get_size()[0] / 2, (30 + 70 * i) * SFY))

                if text == renderedInfoText[-1]:
                    calc = HEIGHT / 2 - ((30 + 70 * i) / 2) * SFY + text.get_size()[1]
                    pg.draw.line(SCREEN, (200, 200, 200), (30 * SFX, calc), (WIDTH - 30 * SFX, calc),
                                 width=int(12.5 * SFX + 12.5 * SFY))

            for i, text in enumerate(renderedControlText):
                SCREEN.blit(text, (75 * SFX, HEIGHT / 2 + (50 * i) * SFY))

            if helpHomeBtn.update(ev):
                gamestate = 1

        FPS_TEXT = FPS_FONT.render(f"FPS: {round(clock.get_fps())}", 1, (255, 255, 255))
        blitText(SCREEN, FPS_TEXT, (10 * SFX, 10 * SFX))

        display.flip()


def blitText(SURFACE: pg.Surface, renderedText, pos: "(x, y)"):
    SURFACE.blit(renderedText, pos)


def updateData():
    os.chmod(DATA_FILE_PATH, S_IWUSR | S_IREAD)

    with open(DATA_FILE_PATH, "w") as file:
        json.dump(data, file, separators=(",", ":"), indent=4)
        file.close()

    os.chmod(DATA_FILE_PATH, S_IREAD | S_IRGRP | S_IROTH)


if __name__ == '__main__':
    DATA_FILE_PATH = "./data/data.json"

    # Set global vars
    with open(DATA_FILE_PATH) as file:
        data = json.load(file)
        file.close()

    pg.init()

    # Set title and icon
    pg.display.set_caption("Dummy Royale")
    icon = pg.image.load("Resources/Icon/Dummy Royale Icon.ico")
    pg.display.set_icon(icon)

    # For testing
    SIZES = [(1400, 800), (1000, 300), (40, 20), (randint(100, 1920), randint(100, 1080)), (960, 540),
             (2000, 800), (1000, 1000), (2560, 1440), (round(1920 * 2 / 3), round(1080 * 2 / 3)), (1536, 864)]
    SIZE = SIZES[-2]
    FLAGS = pg.DOUBLEBUF

    # Setup Vars
    FLAGS = pg.FULLSCREEN | pg.DOUBLEBUF
    SIZE = display.list_modes()[0]
    SCREEN = display.set_mode(SIZE, FLAGS)
    WIDTH, HEIGHT = SCREEN.get_size()

    SFX, SFY = (WIDTH / 1920, HEIGHT / 1080)

    print(SFX, SFY)

    # Clock
    clock = pyTime.Clock()

    # Fonts
    DEFAULT_FONT = pg.font.SysFont("calibri", int(15 * SFX + 15 * SFY))

    GAME_INFO_FONT = pg.font.SysFont("calibri", 30, bold=True)
    GAME_LARGE_FONT = pg.font.SysFont("arial", 60, bold=True)

    BTN_SMALL_FONT = pg.font.SysFont("impact", int(15 * SFX + 15 * SFY))
    BTN_LARGE_FONT = pg.font.SysFont("impact", int(30 * SFX + 30 * SFY))

    HELP_FONT = pg.font.SysFont("times", int(20 * SFX + 20 * SFY))

    FPS_FONT = pg.font.SysFont("calibri", int(20 * SFX + 20 * SFY))

    ATTEMPTED_FPS = 60
    TARGETED_FPS = 60

    # Call main loop
    main()
