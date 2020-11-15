from __future__ import annotations
from inspect import signature, Parameter, _ParameterKind
from typing import Dict, Any, Tuple, Union, List, Final, TypeVar, Callable
import re
import os
import json

import pygame as pg

from . import constant as ct
from .helpers.vector import Vector, parseVector
from .mover import VelocityMover, AccelerationMover, EventMover, TrackingMover
from .basedanmaku import BaseDanmaku, RadialBaseDanmaku, BurstBaseDanmaku, PlaneBaseDanmaku
from .image import BlockImage
from .element import Element
from .generator import Generator

T = TypeVar('T')


class Parser:
    allow = {"Gen": Generator,
             "Generator": Generator,
             "Radial": RadialBaseDanmaku,
             "Burst": BurstBaseDanmaku,
             "Plane": PlaneBaseDanmaku,
             "Velocity": VelocityMover,
             "Acceleration": AccelerationMover,
             "Event": EventMover,
             "Tracking": TrackingMover,
             "Block": BlockImage}

    def __init__(self,
                 screenrect: pg.rect.Rect,
                 groupdict: Dict[str, pg.sprite.Group],
                 spritedict: Dict[str, Element]):
        self.screenrect = screenrect
        self.groupdict = groupdict
        self.spritedict = spritedict

    def parseColor(self, data: Union[List[int], str]) -> Tuple[int, int, int]:
        st: str
        ret: Tuple[int, int, int]

        if isinstance(data, str):
            if match := re.search(r'(?<=__).*(?=__)', data):
                st = match.group().upper()

                if not st in vars(ct):
                    raise ValueError
                if not isinstance(vars(ct)[st], tuple):
                    raise ValueError

                ret = vars(ct)[st]
                return ret

            if match := re.search(r'(?<=#)[0-9a-f]{6}', data):
                st = match.group()

                return(int(st[:2], 16),
                       int(st[2:4], 16),
                       int(st[4:], 16))

        elif isinstance(data, list):
            if len(data) != 3:
                raise ValueError
            if [*filter(lambda x: not isinstance(x, int), data)]:
                raise ValueError
            if [*filter(lambda x: x < 0 or x >= 256, data)]:
                raise ValueError

            return (data[0], data[1], data[2])

        else:
            raise TypeError

        raise ValueError

    def parsePosition(self, data: Union[str, List[Union[int, float]]]) -> Vector:
        _allow: Final[List[str]] = ['topleft', 'bottomleft', 'topright', 'bottomright',
                                    'midtop', 'midleft', 'midbottom', 'midright',
                                    'center']

        st: str

        if isinstance(data, str):
            if match := re.search(r'(?<=__).*(?=__)', data):
                st = match.group().lower()

                if not st in _allow:
                    raise ValueError

                coor: Tuple[int, int] = getattr(self.screenrect, st)
                return parseVector(coor)

        elif isinstance(data, list):
            if len(data) != 2:
                raise ValueError
            if [*filter(lambda x: not isinstance(x, (int, float)), data)]:
                raise ValueError

            return parseVector((data[0], data[1]))

        else:
            raise TypeError

        raise ValueError

    def parse(self, data: Dict[str, Any]) -> Any:
        if not '__type__' in data:
            raise ValueError
        if not data['__type__'] in self.allow:
            raise ValueError

        wrap: bool = False
        if '__wrap__' in data and data['__wrap__']:
            wrap = True

        elem = self.allow[data['__type__']]
        sig = signature(elem)

        args: List[Any] = list()
        kwargs: Dict[str, Any] = dict()
        for name in sig.parameters:
            tmp: Any
            param = sig.parameters[name]

            if param.kind == _ParameterKind.VAR_POSITIONAL:
                if "args" in data:
                    data_args: List[Any] = data["args"]
                    args += data_args

            elif param.kind == _ParameterKind.VAR_KEYWORD:
                if "kwargs" in data:
                    data_kwargs: Dict[str, Any] = data["kwargs"]
                    kwargs.update(data_kwargs)

            else:
                if param.default == Parameter.empty:
                    if not name in data:
                        raise ValueError

                if not name in data:
                    continue

                tmp = data[name]
                print(tmp)

                if tmp == "__arg__":
                    continue

                if isinstance(tmp, dict) and "__type__" in tmp:
                    tmp = self.parse(tmp)

                if elem == Generator and name in ("danmaku",):
                    def parseBase(data: Dict[str, Any]) -> Tuple[int, Callable[[Tuple[int, int]], BaseDanmaku]]:
                        if not "refresh" in data:
                            raise ValueError

                        ref: int = data["refresh"]
                        gen: Callable[[Tuple[int, int]],
                                      BaseDanmaku] = self.parse(data)
                        return (ref, gen)

                    tmp = [*map(parseBase, tmp)]

                if name in ("direction",):
                    tmp *= ct.PI

                if param.annotation in ("pg.sprite.Group",):
                    if not tmp in self.groupdict:
                        raise ValueError
                    tmp = self.groupdict[tmp]
                if param.annotation in ("Element", "Optional[Element]"):
                    if not tmp in self.spritedict:
                        raise ValueError
                    tmp = self.spritedict[tmp]

                if param.annotation in ("Coordinate",):
                    tmp = self.parsePosition(tmp)
                if param.annotation in ("Tuple[int, int, int]",):
                    tmp = self.parseColor(tmp)

                if param.default == Parameter.empty:
                    args.append(tmp)
                else:
                    kwargs.update({name: tmp})

        if not wrap:
            print(elem)
            print(*args)
            print(*kwargs.items())
            return elem(*args, **kwargs)
        else:
            return lambda *wrap_args: elem(*wrap_args, *args, **kwargs)

    def load(self, rel_path: str) -> Any:
        script_dir = os.path.dirname(__file__)
        abs_path = os.path.join(script_dir, rel_path)

        ret: Any = None
        with open(abs_path, "r") as f:
            ret = self.parse(json.loads(f.read()))

        return ret
