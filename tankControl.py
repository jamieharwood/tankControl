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
# D4, spare

hose.on()
irrigation.on()
cooling.on()

pumpOff = 750  # mid PWM 1500 useconds
pumpOn = 1000  # max PWM 2000 useaconds

np = neopixel.NeoPixel(Pin(neoPin), 4)

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

stateOff = 0
stateIrrigationSelected = 1
stateHoseSelected = 2
stateIrrigationOn = 3
stateHoseOn = 4

stateSelection = stateOff

functionStateChanged = False


def pumpState(state):
    if state in (stateOff, stateIrrigationSelected, stateHoseSelected):  # pump state
        pump.duty(pumpOff)
        cooling.on()

        np[pumpLed] = purple
    else:
        pump.duty(pumpOn)
        cooling.off()

        np[pumpLed] = green

    if state == stateIrrigationSelected:  # irrigation selected
        #pump.duty(pumpOff)
        hose.on()
        irrigation.on()

        #np[pumpLed] = green
        np[irrigationLed] = indigo
        np[hoseLed] = purple

    elif state == stateHoseSelected:  # hose selected
        #pump.duty(pumpOff)
        hose.on()
        irrigation.on()

        #np[pumpLed] = green
        np[irrigationLed] = purple
        np[hoseLed] = indigo
    elif state == stateIrrigationOn:  # irrigation on
        #pump.duty(pumpOn)
        hose.off()
        irrigation.on()

        #np[pumpLed] = green
        np[irrigationLed] = green
        np[hoseLed] = purple

    elif state == stateHoseOn:  # hose on
        #pump.duty(pumpOn)
        hose.on()
        irrigation.off()

        #np[pumpLed] = green
        np[irrigationLed] = purple
        np[hoseLed] = green

    np.write()


def isSunrise():
    returnValue = 0
    url = "http://192.168.86.240:5000/isSunrise/"

    print(url)

    try:
        response = urequests.get(url)

        returnValue = int(response.text.replace('\"', ''))

        response.close()
    except:
        print('Fail www connect...')

    return returnValue


def isSunset():
    returnValue = 0
    url = "http://192.168.86.240:5000/isSunset/"

    print(url)

    try:
        response = urequests.get(url)

        returnValue = int(response.text.replace('\"', ''))

        response.close()
    except:
        print('Fail www connect...')

    return returnValue


def isHose():
    returnValue = 0
    url = "http://192.168.86.240:5000/isHose/"

    print(url)

    try:
        response = urequests.get(url)

        returnValue = int(response.text.replace('\"', ''))

        response.close()
    except:
        remoteHose = False
        remoteIrrigation = False
        remotePump = False
        print('Fail www connect...')

    return returnValue


def isStateChanged(state):
    returnValue = 0
    url = "http://192.168.86.240:5000/{0}/".replace('{0}', state)

    print(url)

    try:
        response = urequests.get(url)

        returnValue = int(response.text.replace('\"', ''))

        response.close()
    except:
        remoteHose = False
        remoteIrrigation = False
        remotePump = False
        print('Fail www connect...')

    return returnValue


def main():  # Pump control
    # Set initial state
    np[powerLed] = red
    np[pumpLed] = black
    np[irrigationLed] = black
    np[hoseLed] = black

    np.write()

    pumpState(stateOff)

    while True:
        # To pump or not to pump
        #hoseValue = isHose()
        hoseValue = isStateChanged('isHose')

        #if isSunrise():
        if isStateChanged('isSunrise'):
            pumpState(stateIrrigationOn)
        #elif isSunset():
        elif isStateChanged('isSunset'):
            pumpState(stateIrrigationOn)
        elif hoseValue == 1:
            pumpState(stateIrrigationSelected)
        elif hoseValue == 2:
            pumpState(stateHoseSelected)
        elif hoseValue == 5:
            pumpState(stateIrrigationOn)
        elif hoseValue == 6:
            pumpState(stateHoseOn)
        else:
            pumpState(stateOff)

        utime.sleep(0.25)

main()
