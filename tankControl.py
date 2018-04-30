#!/usr/bin/env python3

"""
Trilby Tanks 2018 copyright
Module: tankControl
"""

from machine import Pin
import machine
import utime
import varibles as vars
import neopixel
import urequests
import ubinascii

neoPin = 15  # D8
pump = machine.PWM(machine.Pin(13), freq=500)  # D7
hose = Pin(12, Pin.OUT)  # D6
irrigation = Pin(5, Pin.OUT)  # D1
cooling = Pin(2, Pin.OUT)  # D4

hose.on()
irrigation.on()
cooling.on()

pumpOff = 750  # mid PWM 1500 u seconds
pumpOn = 1000  # max PWM 2000 u seconds

np = neopixel.NeoPixel(Pin(neoPin), 8)
neoLow = 0
neoMid = 64
neoHi = 255

red = (neoMid, neoLow, neoLow)
yellow = (255, 226, neoLow)
tango = (243, 114, 82)
green = (neoLow, neoMid, neoLow)
indigo = (neoLow, 126, 135)
blue = (neoLow, neoLow, neoMid)
purple = (neoMid, neoLow, neoMid)
black = (neoLow, neoLow, neoLow)

powerLed = 3
hoseLed = 2
irrigationLed = 1
pumpLed = 0
tanklevel1 = 4
tanklevel2 = 5
tanklevel3 = 6
iswetled = 7

stateOff = 0
stateIrrigationSelected = 1
stateHoseSelected = 2
stateIrrigationOn = 3
stateHoseOn = 4

#  stateSelection = stateOff

#  functionStateChanged = False


def pumpstate(state):
    if state in (stateOff, stateIrrigationSelected, stateHoseSelected):  # pump state
        pump.duty(pumpOff)
        cooling.on()

        np[pumpLed] = purple
    else:
        pump.duty(pumpOn)
        cooling.off()

        np[pumpLed] = green

    if state == stateIrrigationSelected:  # irrigation selected
        hose.on()
        irrigation.on()

        np[irrigationLed] = indigo
        np[hoseLed] = purple

    elif state == stateHoseSelected:  # hose selected
        hose.on()
        irrigation.on()

        np[irrigationLed] = purple
        np[hoseLed] = indigo
    elif state == stateIrrigationOn:  # irrigation on
        hose.off()
        irrigation.on()

        np[irrigationLed] = green
        np[hoseLed] = purple

    elif state == stateHoseOn:  # hose on
        hose.on()
        irrigation.off()

        np[irrigationLed] = purple
        np[hoseLed] = green

    np.write()


def isstatechanged(state):
    returnvalue = 0
    url = "http://192.168.86.240:5000/{0}/".replace('{0}', state)

    print(url)

    try:
        response = urequests.get(url)

        returnvalue = int(response.text.replace('\"', ''))

        response.close()
    except:
        #  remoteHose = False
        #  remoteIrrigation = False
        #  remotePump = False
        print('Fail www connect...')

    return returnvalue


def tankleveldisplay(tanklevel):
    if tanklevel == 0:
        np[tanklevel1] = purple
        np[tanklevel2] = purple
        np[tanklevel3] = purple
    elif tanklevel == 1:
        np[tanklevel1] = purple
        np[tanklevel2] = purple
        np[tanklevel3] = green
    elif tanklevel == 2:
        np[tanklevel1] = purple
        np[tanklevel2] = green
        np[tanklevel3] = green
    elif tanklevel == 3:
        np[tanklevel1] = green
        np[tanklevel2] = green
        np[tanklevel3] = green

    np.write()

def iswetdisplay(iswet):
    if iswet:
        np[iswetled] = blue
    else:
        np[iswetled] = yellow

    np.write()

def main():  # Pump control
    # Set initial state
    np[powerLed] = red
    np[pumpLed] = black
    np[irrigationLed] = black
    np[hoseLed] = black

    np.write()

    pumpstate(stateOff)

    np[iswetled] = tango

    while True:
        # To pump or not to pump
        iswet = isstatechanged('isWet')
        iswetdisplay(iswet)

        tanklevel = isstatechanged('isLevel')
        tankleveldisplay(tanklevel)

        hosevalue = isstatechanged('isHose')

        if isstatechanged('isSunrise') and iswet == 0:
            pumpstate(stateIrrigationOn)
        elif isstatechanged('isSunset') and iswet == 0:
            pumpstate(stateIrrigationOn)
        elif hosevalue == 1:  #  irrigation selected
            pumpstate(stateIrrigationSelected)
        elif hosevalue == 2:  #  hose selected
            pumpstate(stateHoseSelected)
        elif hosevalue == 5:  #  irrigation selected and pump on
            pumpstate(stateIrrigationOn)
        elif hosevalue == 6:  #  hose selected and pump on
            pumpstate(stateHoseOn)
        else:
            pumpstate(stateOff)

        utime.sleep(0.25)


main()
