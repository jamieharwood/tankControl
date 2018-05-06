#!/usr/bin/env python3

"""
Trilby Tanks 2018 copyright
Module: tankControl
"""

from machine import Pin
from machine import RTC
import machine
import utime
import varibles as vars
import neopixel
import urequests
import ubinascii
import ujson

try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct

# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 3155673600

host = "0.uk.pool.ntp.org"

restHost = "http://192.168.86.240:5000/{0}/"

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

# Set initial state
np[powerLed] = red
np[irrigationLed] = black
np[hoseLed] = black
np[pumpLed] = black
np.write()

tanklevel1 = 4
tanklevel2 = 5
tanklevel3 = 6
iswetled = 7

stateOff = 0
stateIrrigationSelected = 1
stateHoseSelected = 2
stateIrrigationOn = 3
stateHoseOn = 4

switchSensorIrrigation = 1
switchSensorHose = 2
switchSensorIrrigationAndPump = 5
switchSensorHoseAndPump = 6


def time():
    try:
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1b
        addr = socket.getaddrinfo(host, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
        s.close()
        val = struct.unpack("!I", msg[40:44])[0]

        return val - NTP_DELTA
    except OSError:

        return 0

# There's currently no timezone support in MicroPython, so
# utime.localtime() will return UTC time (as if it was .gmtime())


def settime():
    while time() == 0:
        print('Waiting for time...')

    t = time()
    import machine
    import utime
    tm = utime.localtime(t)
    tm = tm[0:3] + (0,) + tm[3:6] + (0,)
    machine.RTC().datetime(tm)
    print(utime.localtime())


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


def getFullUrl(restFunction):

    return restHost.replace('{0}', restFunction)


def isstatechangedall():
    returnvalue = 0
    url = getFullUrl('getControlStates')

    print(url)

    try:
        response = urequests.get(url)

        try:
            sensorData = ujson.loads(response)

            returnvalue = sensorData
        except:
            print("JSON error")

        response.close()
    except:
        print('Fail www connect...')

    return returnvalue


def isstatechanged(state):
    returnvalue = 0
    # url = "http://192.168.86.240:5000/{0}/".replace('{0}', state)
    url = getFullUrl(state)

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


def getiswet():
    return isstatechanged('isWet')


def getislevel():
    return isstatechanged('isLevel')


def getishose():
    return isstatechanged('isHose')


def getissunrise():
    return isstatechanged('isSunrise')


def getissunset():
    return isstatechanged('isSunset')


def main():  # Pump control
    currTime = 0
    lastTime = 0
    lastMin = 0

    iswet = 0
    tanklevel = 0
    switchsensorvalue = 0
    isSunrise = 0
    isSunset = 0

    getdisplay = 0
    getsunrise = 0

    #  sensorValues = {"isSunrise": "0", "isWet": "0", "isSunset": "0", "isLevel": "0", "isHose": "0"}

    settime()

    pumpstate(stateOff)

    np[iswetled] = tango

    # Set initial status

    iswet = getiswet()
    tanklevel = getislevel()
    isSunrise = getissunrise()
    isSunset = getissunset()

    switchsensorvalue = getishose()

    iswetdisplay(iswet)
    tankleveldisplay(tanklevel)

    rtc = RTC()
    sampletimes = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]

    while True:
        # To pump or not to pump

        timeNow = rtc.datetime()
        currHour = timeNow[4]
        currMinute = timeNow[5]

        if currMinute not in sampletimes and getdisplay == 0:

            getdisplay = 1

        if currMinute in sampletimes and getdisplay == 1:
            iswet = getiswet()
            iswetdisplay(iswet)

            tanklevel = getislevel()
            tankleveldisplay(tanklevel)

            getdisplay = 0

        if currHour != 0 and currMinute != 1:
            getsunrise = 1

        if currHour == 0 and currMinute == 1 and getsunrise == 1:
            settime()

            getsunrise = 0

        if lastMin != currMinute:
            isSunrise = getissunrise()
            isSunset = getissunset()

            lastMin = currMinute

        switchsensorvalue = getishose()

        if tanklevel != 0:  # not empty tank
            if isSunrise and iswet == 0:
                pumpstate(stateIrrigationOn)

            elif isSunset and iswet == 0:
                pumpstate(stateIrrigationOn)

            elif switchsensorvalue == switchSensorIrrigation:  # irrigation selected
                pumpstate(stateIrrigationSelected)

            elif switchsensorvalue == switchSensorHose:  # hose selected
                pumpstate(stateHoseSelected)

            elif switchsensorvalue == switchSensorIrrigationAndPump:  # irrigation selected and pump on
                pumpstate(stateIrrigationOn)

            elif switchsensorvalue == switchSensorHoseAndPump:  # hose selected and pump on
                pumpstate(stateHoseOn)
            else:
                pumpstate(stateOff)

        utime.sleep(0.25)


main()
