#!/usr/bin/env python3

"""
Trilby Tanks 2018 copyright
Module: tankControl
"""

from machine import Pin
from machine import RTC
from machine import I2C
from machine import PWM
import network
import machine
import ssd1306
import utime
# import varibles as vars
# import neopixel
import urequests
import ubinascii
import ujson
from heartbeatClass import HeartBeat
from timeClass import TimeTank
from SensorRegistationClass import SensorRegistation
from NeoPixelClass import NeoPixel
from LogClass import Log

i2c = I2C(-1, Pin(5), Pin(4))
__oled = ssd1306.SSD1306_I2C(128, 32, i2c)
__spinner = 0
__statustest = ''
__top = 0
__log = Log()

restHost = "http://192.168.86.240:5000"

__sensorname = ''
__deviceid = ''

neoPin = 15  # D8
pump = PWM(Pin(13), freq=500)  # D7
hose = Pin(12, Pin.OUT)  # D6
irrigation = Pin(0, Pin.OUT)  # D3
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
    returnvalue = -1
    timecount = 0

    while returnvalue == -1:
        url = getFullUrl('getControlStates')

        print(url)

        try:
            response = urequests.get(url)

            try:
                sensorData = ujson.loads(response)

                returnvalue = sensorData
                # print('returnvalue=' + str(returnvalue))

            except:
                print("JSON error")

            response.close()
            break
        except:
            print('isstatechangedall: Fail www connection attempt ' + str(timecount))

            timecount += 1

            if timecount > 10:
                import machine
                machine.reset()

    return returnvalue


def isstatechanged(state):
    returnvalue = -1
    timecount = 0

    while returnvalue == -1:
        # url = "http://192.168.86.240:5000/{0}/".replace('{0}', state)
        url = getFullUrl(state)

        print(url)

        try:
            response = urequests.get(url)

            returnvalue = int(response.text.replace('\"', ''))
            # print('returnvalue=' + str(returnvalue))

            response.close()

            break
        except:

            print('isstatechanged: Fail www connection attempt ' + str(timecount))

            timecount += 1

            if timecount > 10:
                import machine
                machine.reset()

            returnvalue = False

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


def printoled(statustest, top=0):
    global __statustest, __top

    __top = top
    __statustest = statustest

    __oled.fill(0)
    __oled.text(__statustest, 0, __top)
    __oled.show()


def spinneroled():
    global __deviceid, __sensorname,__spinner, __top

    __oled.fill(0)

    if __spinner == 0:
        __oled.text('-', 120, 22)
    elif __spinner == 1:
        __oled.text('/', 120, 22)
    elif __spinner == 2:
        __oled.text('|', 120, 22)
    elif __spinner == 3:
        __oled.text('\\', 120, 22)

    __oled.text(__statustest, 0, __top)
    __oled.text(__sensorname, 0, 12)
    __oled.text('dev: ' + __deviceid, 0, 22)
    __oled.show()

    __spinner += 1
    if __spinner > 3:
        __spinner = 0


def settime(mytime):
    timecount = 0

    while not mytime.settime(1):
        timecount += 1

        if timecount > 10:
            machine.reset()


def main():
    global __deviceid, __sensorname, __log

    debug = True
    __sensorname = 'control'

    if debug:
        __sensorname += '-debug'

    __deviceid = getdeviceid()

    __log = Log(restHost, __deviceid)
    printoled('tankControl v1')

    testfornetwork()
    __log.printl('Test for network.')
    spinneroled()

    __log.printl('startup: tankControl v1: ' + __sensorname)
    spinneroled()

    mySensorRegistation = SensorRegistation(restHost, __deviceid)
    mySensorRegistation.register(__sensorname, 'Hardware', 'JH')
    __log.printl('registered: mySensorRegistation.register')
    spinneroled()

    myheartbeat = HeartBeat(restHost, __deviceid)
    myheartbeat.beat()
    __log.printl('registered: myheartbeat.beat')
    spinneroled()

    mytime = TimeTank(__deviceid, __log.printl)
    settime(mytime)
    # mytime.settime(1)
    __log.printl('registered: mytime.settime')
    spinneroled()

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

    # settime(mytime)
    # mytime.settime(1)
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
        currSecond = timeNow[6]

        if currSecond != lastSecond:
            lastSecond = currSecond
            spinneroled()

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

            __log.printl('Hourly functions')
            settime(mytime)
            local = utime.localtime()
            # mytime.settime(1)
            __log.printl('registered: mytime.settime')

        if lastMin != currMinute:
            lastMin = currMinute

            __log.printl('Minute functions')
            myheartbeat.beat()
            isSunrise = isstatechanged('isSunrise')
            isSunset = isstatechanged('isSunset')

        if currHour not in samplehours and gethour == 0:
            gethour = 1

        if currHour in samplehours and gethour == 1:
            gethour = 0

            __log.printl('Sample hour functions')

            settime(mytime)
            local = utime.localtime()
            # mytime.settime(1)

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
