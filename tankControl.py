#!/usr/bin/env python3

"""
Trilby Tanks 2018 copyright
Module: tankControl
"""

from machine import Pin
from machine import RTC
from machine import PWM
import network
import machine
import utime
import urequests
import ubinascii
from heartbeatClass import HeartBeat
from timeClass import TimeTank
from SensorRegistationClass import SensorRegistation
from NeoPixelClass import NeoPixel
from LogClass import Log

__log = Log()

__restHost = "http://192.168.86.240:5000"

__sensorname = ''
__deviceid = ''

# __future1 = Pin(16, Pin.OUT)  # D0
__irrigation = Pin(5, Pin.OUT)  # D1
# __future2 = Pin(4, Pin.OUT)  # D2
# __future3 = Pin(0, Pin.OUT)  # D3
__cooling = Pin(2, Pin.OUT)  # D4
# __future4 = Pin(14, Pin.OUT)  # D5
__hose = Pin(12, Pin.OUT)  # D6
__pump = PWM(Pin(13), freq=500)  # D7
__neoPin = 15  # D8

__hose.on()
__irrigation.on()
__cooling.on()

__pumpOff = 750  # mid PWM 1500 u seconds
__pumpOn = 1000  # max PWM 2000 u seconds

__np = NeoPixel(__neoPin, 8)

__powerLed = 3
__hoseLed = 2
__irrigationLed = 1
__pumpLed = 0

# Set initial state
__np.colour(__powerLed, 'red')
__np.colour(__irrigationLed, 'black')
__np.colour(__hoseLed, 'black')
__np.colour(__pumpLed, 'black')
__np.write()

__tanklevel1 = 4
__tanklevel2 = 5
__tanklevel3 = 6
__iswetled = 7

__stateOff = 0
__stateIrrigationSelected = 1
__stateHoseSelected = 2
__stateIrrigationOn = 3
__stateHoseOn = 4

__switchSensorIrrigation = 1
__switchSensorHose = 2
__switchSensorIrrigationAndPump = 5
__switchSensorHoseAndPump = 6

__debugcode = False


def printd(debugtext):
    if __debugcode:
        print(debugtext)


def getdeviceid():

    deviceid = ubinascii.hexlify(machine.unique_id()).decode()
    deviceid = deviceid.replace('b\'', '')
    deviceid = deviceid.replace('\'', '')

    return deviceid


def pumpstate(state):
    if state in (__stateOff, __stateIrrigationSelected, __stateHoseSelected):  # pump state
        __pump.duty(__pumpOff)
        __cooling.on()

        __np.colour(__pumpLed, 'purple')
    else:
        __pump.duty(__pumpOn)
        __cooling.off()

        __np.colour(__pumpLed, 'green')

    if state == __stateIrrigationSelected:  # irrigation selected
        printd('state == __stateIrrigationSelected')
        __hose.on()
        __irrigation.on()

        __np.colour(__irrigationLed, 'indigo')
        __np.colour(__hoseLed, 'purple')

    elif state == __stateHoseSelected:  # hose selected
        printd('state == __stateHoseSelected')
        __hose.on()
        __irrigation.on()

        __np.colour(__irrigationLed, 'purple')
        __np.colour(__hoseLed, 'indigo')
    elif state == __stateIrrigationOn:  # irrigation on
        printd('state == __stateIrrigationOn')
        __hose.off()
        __irrigation.on()

        __np.colour(__irrigationLed, 'green')
        __np.colour(__hoseLed, 'purple')

    elif state == __stateHoseOn:  # hose on
        printd('state == __stateHoseOn')
        __hose.on()
        __irrigation.off()

        __np.colour(__irrigationLed, 'purple')
        __np.colour(__hoseLed, 'green')

    __np.write()


def isstatechanged(state):
    returnvalue = -1
    timecount = 0

    while returnvalue == -1:
        url = __restHost + '/' + state

        print(url)

        try:
            response = urequests.get(url)

            returnvalue = int(response.text.replace('\"', ''))

            response.close()

            break
        except:

            __log.printl('isstatechanged: Fail www connection attempt ' + str(timecount))

            sta_if = network.WLAN(network.STA_IF)

            if not sta_if.active():
                __log.printl('wifi not active.')
                sta_if.active(True)
                sta_if.connect('dodger', 'skinner2263')
                testfornetwork()
                __log.printl('wifi reconnected.')

            timecount += 1

            if timecount > 10:
                import machine
                machine.reset()
                returnvalue = -1
                break

            # returnvalue = False

    return returnvalue


def tankleveldisplay(tanklevel):
    if tanklevel == 0:
        __np.colour(__tanklevel1, 'purple')
        __np.colour(__tanklevel2, 'purple')
        __np.colour(__tanklevel3, 'purple')
    elif tanklevel == 1:
        __np.colour(__tanklevel1, 'purple')
        __np.colour(__tanklevel2, 'purple')
        __np.colour(__tanklevel3, 'green')
    elif tanklevel == 2:
        __np.colour(__tanklevel1, 'purple')
        __np.colour(__tanklevel2, 'green')
        __np.colour(__tanklevel3, 'green')
    elif tanklevel == 3:
        __np.colour(__tanklevel1, 'green')
        __np.colour(__tanklevel2, 'green')
        __np.colour(__tanklevel3, 'green')

    __np.write()


def iswetdisplay(iswet):
    if iswet:
        __np.colour(__iswetled, 'blue')
    else:
        __np.colour(__iswetled, 'yellow')

    __np.write()


def getip():
    sta_if = network.WLAN(network.STA_IF)
    temp = sta_if.ifconfig()

    return temp[0]


def testfornetwork():
    sta_if = network.WLAN(network.STA_IF)

    while not sta_if.active():
        printd('Waiting for Wifi')

    while '0.0.0.0' == getip():
        printd('Waiting for IP')


def settime(mytime):
    timecount = 0

    while not mytime.settime(1):
        timecount += 1

        if timecount > 10:
            machine.reset()


def main():
    global __deviceid, __sensorname, __log

    debug = False
    __sensorname = 'control'
    __deviceid = getdeviceid()

    if debug:
        __sensorname += "-" + __deviceid + '-debug'

    __log = Log(__restHost, __deviceid)

    testfornetwork()
    __log.printl('Test for network.')

    __log.printl('startup: tankControl v1: ' + __sensorname)

    mySensorRegistation = SensorRegistation(__restHost, __deviceid)
    mySensorRegistation.register(__sensorname, 'Hardware', 'JH')
    __log.printl('registered: mySensorRegistation.register')

    myheartbeat = HeartBeat(__restHost, __deviceid)
    myheartbeat.longbeat()
    __log.printl('registered: myheartbeat.longbeat')

    mytime = TimeTank(__deviceid, __log.printl)
    settime(mytime)
    __log.printl('registered: mytime.settime')

    currTime = 0
    lastTime = 0
    lastMin = 0
    lastSecond = -1

    iswet = 0
    tanklevel = 0
    switchsensorvalue = 0
    isSunrise = 0
    isSunset = 0

    getdisplay = 0
    getsunrise = 0

    rtc = RTC()
    sampletimes = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
    samplehours = [1, 6, 12, 18]
    gethour = 0

    pumpstate(__stateOff)

    __np.colour(__iswetled, 'tango')

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
        currSecond = timeNow[6]

        if currSecond != lastSecond:
            lastSecond = currSecond

        if currMinute not in sampletimes and getdisplay == 0:
            getdisplay = 1

        if currMinute in sampletimes and getdisplay == 1:
            getdisplay = 0
            __log.printl('sample times functions')

            isWet = isstatechanged('isWet')
            iswetdisplay(iswet)

            tanklevel = isstatechanged('isLevel')
            tankleveldisplay(tanklevel)

        if currHour != 0 and currMinute != 1:
            getsunrise = 1

        if currHour == 0 and currMinute == 1 and getsunrise == 1:
            getsunrise = 0
            __log.printl('Midnight functions')

            settime(mytime)
            local = utime.localtime()
            __log.printl('midnight: mytime.settime')

        if lastMin != currMinute:
            lastMin = currMinute
            __log.printl('Minute functions')

            myheartbeat.longbeat()
            __log.printl('Minute functions: myheartbeat.longbeat')

            isSunrise = isstatechanged('isSunrise')
            isSunset = isstatechanged('isSunset')

        if currHour not in samplehours and gethour == 0:
            gethour = 1

        if currHour in samplehours and gethour == 1:
            gethour = 0
            __log.printl('Sample hour functions')

            settime(mytime)
            local = utime.localtime()

        switchsensorvalue = isstatechanged('isHose')

        if tanklevel != 0:  # not empty tank
            if isSunrise and iswet == 0:
                printd('isSunrise and iswet == 0')
                pumpstate(__stateIrrigationOn)

            elif isSunset and iswet == 0:
                printd('isSunset and iswet == 0')
                pumpstate(__stateIrrigationOn)

            elif switchsensorvalue == __switchSensorIrrigation:  # irrigation selected
                printd('switchsensorvalue == __switchSensorIrrigation')
                pumpstate(__stateIrrigationSelected)

            elif switchsensorvalue == __switchSensorHose:  # hose selected
                printd('switchsensorvalue == __switchSensorHose')
                pumpstate(__stateHoseSelected)

            elif switchsensorvalue == __switchSensorIrrigationAndPump:  # irrigation selected and pump on
                printd('switchsensorvalue == __switchSensorIrrigationAndPump')
                pumpstate(__stateIrrigationOn)

            elif switchsensorvalue == __switchSensorHoseAndPump:  # hose selected and pump on
                printd('switchsensorvalue == __switchSensorHoseAndPump')
                pumpstate(__stateHoseOn)
            else:
                printd('else:')
                pumpstate(__stateOff)

        # myheartbeat.beat()

        utime.sleep(0.25)


main()

