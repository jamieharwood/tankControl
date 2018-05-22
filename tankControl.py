#!/usr/bin/env python3

"""
Trilby Tanks 2018 copyright
Module: tankControl
"""

from machine import Pin
from machine import RTC
import network
import machine
import utime
import varibles as vars
import neopixel
import urequests
import ubinascii
import ujson
from heartbeatClass import HeartBeat
from timeClass import TimeTank
from SensorRegistationClass import SensorRegistation
from NeoPixelClass import NeoPixel

restHost = "http://192.168.86.240:5000"

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

np = NeoPixel(neoPin, 8)

powerLed = 3
hoseLed = 2
irrigationLed = 1
pumpLed = 0

# Set initial state
np.colour(powerLed, 'red')
np.colour(irrigationLed, 'black')
np.colour(hoseLed, 'black')
np.colour(pumpLed, 'black')
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


def getdeviceid():

    deviceid = ubinascii.hexlify(machine.unique_id()).decode()
    deviceid = deviceid.replace('b\'', '')
    deviceid = deviceid.replace('\'', '')

    return deviceid


def pumpstate(state):
    if state in (stateOff, stateIrrigationSelected, stateHoseSelected):  # pump state
        pump.duty(pumpOff)
        cooling.on()

        np.colour(pumpLed, 'purple')
    else:
        pump.duty(pumpOn)
        cooling.off()

        np.colour(pumpLed, 'green')

    if state == stateIrrigationSelected:  # irrigation selected
        hose.on()
        irrigation.on()

        np.colour(irrigationLed, 'indigo')
        np.colour(hoseLed, 'purple')

    elif state == stateHoseSelected:  # hose selected
        hose.on()
        irrigation.on()

        np.colour(irrigationLed, 'purple')
        np.colour(hoseLed, 'indigo')
    elif state == stateIrrigationOn:  # irrigation on
        hose.off()
        irrigation.on()

        np.colour(irrigationLed, 'green')
        np.colour(hoseLed, 'purple')

    elif state == stateHoseOn:  # hose on
        hose.on()
        irrigation.off()

        np.colour(irrigationLed, 'purple')
        np.colour(hoseLed, 'green')

    np.write()


def getFullUrl(restFunction):
    # return restHost.replace('{0}', restFunction)

    return restHost + '/' + restFunction


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

        print('Fail www connect...')

    return returnvalue


def tankleveldisplay(tanklevel):
    if tanklevel == 0:
        np.colour(tanklevel1, 'purple')
        np.colour(tanklevel2, 'purple')
        np.colour(tanklevel3, 'purple')
    elif tanklevel == 1:
        np.colour(tanklevel1, 'purple')
        np.colour(tanklevel2, 'purple')
        np.colour(tanklevel3, 'green')
    elif tanklevel == 2:
        np.colour(tanklevel1, 'purple')
        np.colour(tanklevel2, 'green')
        np.colour(tanklevel3, 'green')
    elif tanklevel == 3:
        np.colour(tanklevel1, 'green')
        np.colour(tanklevel2, 'green')
        np.colour(tanklevel3, 'green')

    np.write()


def iswetdisplay(iswet):
    if iswet:
        np.colour(iswetled, 'blue')
    else:
        np.colour(iswetled, 'yellow')

    np.write()


def getip():
    sta_if = network.WLAN(network.STA_IF)
    temp = sta_if.ifconfig()

    return temp[0]


def testfornetwork():
    sta_if = network.WLAN(network.STA_IF)
    while not sta_if.active():
        print('Waiting for Wifi')

    while '0.0.0.0' == getip():
        print('Waiting for IP')


def main():
    testfornetwork()

    debug = False
    sensorname = 'control'

    if debug:
        sensorname += '-debug'

    deviceid = getdeviceid()

    mySensorRegistation = SensorRegistation(restHost, deviceid)
    mySensorRegistation.register(sensorname, 'Hardware', 'JH')

    myheartbeat = HeartBeat(restHost, deviceid)
    myheartbeat.beat()

    mytime = TimeTank(deviceid)
    mytime.settime(1)

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

    mytime.settime(1)
    rtc = RTC()
    sampletimes = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
    samplehours = [1, 6, 12, 18]
    gethour = 0

    pumpstate(stateOff)

    np.colour(iswetled, 'tango')

    # Set initial status
    isWet = isstatechanged('isWet')
    tanklevel = isstatechanged('isLevel')
    isSunrise = isstatechanged('isSunrise')
    isSunset = isstatechanged('isSunset')
    switchsensorvalue = isstatechanged('isHose')

    iswetdisplay(iswet)
    tankleveldisplay(tanklevel)

    while True:
        # To pump or not to pump
        timeNow = rtc.datetime()
        currHour = timeNow[4]
        currMinute = timeNow[5]

        if currMinute not in sampletimes and getdisplay == 0:

            getdisplay = 1

        if currMinute in sampletimes and getdisplay == 1:
            isWet = isstatechanged('isWet')
            iswetdisplay(iswet)

            tanklevel = isstatechanged('isLevel')
            tankleveldisplay(tanklevel)

            getdisplay = 0

        if currHour != 0 and currMinute != 1:
            getsunrise = 1

        if currHour == 0 and currMinute == 1 and getsunrise == 1:
            mytime.settime(1)

            getsunrise = 0

        if lastMin != currMinute:
            myheartbeat.beat()
            isSunrise = isstatechanged('isSunrise')
            isSunset = isstatechanged('isSunset')

            lastMin = currMinute

        if currHour not in samplehours and gethour == 0:
            gethour = 1

        if currHour in samplehours and gethour == 1:
            gethour = 0
            local = utime.localtime()
            mytime.settime(1)

        switchsensorvalue = isstatechanged('isHose')

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
