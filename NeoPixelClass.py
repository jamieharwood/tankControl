#!/usr/bin/env python3

"""
Trilby Tanks 2018 copyright
Module: NeoPixel
"""

import neopixel
from machine import Pin


class NeoPixel:
    __neopin = 15
    __neocount = 4

    __np = neopixel.NeoPixel(Pin(__neopin), __neocount)

    __neoLow = 0
    __neoMid = 64
    __neoHi = 255

    colours = {'red': (__neoMid, __neoLow, __neoLow),
               'yellow': (255, 226, __neoLow),
               'tango': (243, 114, 82),
               'green': (__neoLow, __neoMid, __neoLow),
               'indigo': (__neoLow, 126, 135),
               'blue': (__neoLow, __neoLow, __neoMid),
               'purple': (__neoMid, __neoLow, __neoMid),
               'black': (__neoLow, __neoLow, __neoLow)}

    def __init__(self, neopin=15, neocount=4):
        self.__neopin = neopin
        self.__neocount = neocount

        self.__np = neopixel.NeoPixel(Pin(self.__neopin), self.__neocount)

    def __call__(self):
        pass

    def colour(self, pin, newcolour, update=False):
        self.__np[pin] = self.colours[newcolour.lower()]

        if update:
            self.update()

    def write(self):
        self.__np.write()

