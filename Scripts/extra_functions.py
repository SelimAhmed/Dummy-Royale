import pygame as pg
from math import pi

"""
  0       0,          
  1           30,     
  2           45,     
  3           60,      
  4       90,         
  5           120,    
  6           135,    
  7           150,    
  8       180,        
  9           210,    
  10          225,    
  11          240,    
  12      270,
  13          300,
  14          315,
  15          330
"""

specialAngles = (
    0,  # 00
    pi / 6,  # 01
    pi / 4,  # 02
    pi / 3,  # 03
    pi / 2,  # 04
    2 * pi / 3,  # 05
    3 * pi / 4,  # 06
    5 * pi / 6,  # 07
    pi,  # 08
    7 * pi / 6,  # 09
    5 * pi / 4,  # 10
    4 * pi / 3,  # 11
    3 * pi / 2,  # 12
    5 * pi / 3,  # 13
    7 * pi / 4,  # 14
    11 * pi / 6  # 15
)


def getBoundingSectors(center: tuple):
    # Center, left, top, right, bottom, TL, TR, BL, BR
    return (center,
            (center[0] - 1, center[1]),
            (center[0], center[1] - 1),
            (center[0] + 1, center[1]),
            (center[0], center[1] + 1),
            (center[0] - 1, center[1] - 1),
            (center[0] + 1, center[1] - 1),
            (center[0] - 1, center[1] + 1),
            (center[0] + 1, center[1] + 1),)


def resizeImage(imageFile: pg.image, scaleFactor: float, scale: tuple = (1, 1)):
    image = pg.image.load(imageFile)
    image = pg.transform.scale(image, (
        round(image.get_width() * (scaleFactor * scale[0])), round(image.get_height() * (scaleFactor * scale[1]))))
    image.convert()

    return image, (scaleFactor * scale[0], scaleFactor * scale[1])


def scaleImageTo(imageFile: pg.image, to: tuple):
    image = pg.image.load(imageFile)
    ogSize = image.get_size()

    image = pg.transform.scale(image, (int(to[0]), int(to[1])))
    image.convert()

    newSize = image.get_size()

    scaleFactor = (newSize[0] / ogSize[0]), (newSize[1] / ogSize[1])

    return image, scaleFactor


def getDist(a: tuple, b: tuple):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
