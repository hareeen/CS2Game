from typing import Final, Tuple
import math

import pygame as pg

WIDTH: Final[int] = 512     #너비
HEIGHT: Final[int] = 768    #높이

WHITE: Final[Tuple[int, int, int]] = (255, 255, 255)        #색깔 지정
BLACK: Final[Tuple[int, int, int]] = (0, 0, 0)
RED: Final[Tuple[int, int, int]] = (140, 0, 0)
REDTRACK: Final[Tuple[int, int, int]] = (255, 0, 128)
GREEN: Final[Tuple[int, int, int]] = (0, 140, 0)
GREENTRACK: Final[Tuple[int, int, int]] = (0, 255, 0)
BLUE: Final[Tuple[int, int, int]] = (0, 0, 255)
BLUETRACK: Final[Tuple[int, int, int]] = (0, 175, 255)

PI: Final[float] = math.pi      #3.1415
ELEMENTSIZE: Final[Tuple[int, int]] = (10, 10)      #객체 기본 크기
FPS: Final[int] = 60        #FPS

pg.mixer.init()
#F_BGM = open("audio/bgm.mp3", "r")
#S_GOTHIT: Final[pg.mixer.Sound] = pg.mixer.Sound("audio/gothit.wav")
#S_MATCHED: Final[pg.mixer.Sound] = pg.mixer.Sound("audio/matched.wav")
#S_TOUCHDOWN: Final[pg.mixer.Sound] = pg.mixer.Sound("audio/touchdown.wav")

