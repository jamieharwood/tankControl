from machine import Pin
import machine
import utime
import varibles as vars
import neopixel
import urequests
import ubinascii

pump = machine.PWM(machine.Pin(12), freq=50)
hose = Pin(4, Pin.OUT)  # D3
irrigation = Pin(4, Pin.OUT)  # D3

pumpOff = 77
pumpOn = 115

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
pumpLed = 2
irrigationLed = 1
hoseLed = 0

stateOff = 0
stateIrrigation = 1
stateHose = 2

functionStateChanged = False


def pumpState(state):
    if state == stateOff:  # all off
        pump.duty(pumpOff)
        hose.off()
        irrigation.off()

        np[pumpLed] = red
        np[irrigationLed] = red
        np[hoseLed] = red

    elif state == stateIrrigation:  # irrigation on
        pump.duty(pumpOn)
        hose.oon()
        irrigation.off()

        np[pumpLed] = green
        np[irrigationLed] = green
        np[hoseLed] = red

    elif state == stateHose:  # pump on
        pump.duty(pumpOn)
        hose.off()
        irrigation.on()

        np[pumpLed] = green
        np[irrigationLed] = red
        np[hoseLed] = green


def isSunrise():
    url = "http://192.168.86.240:5000/isSunrise"

    print(url)

    try:
        response = urequests.get(url)

        # print(url)
        print(response.text)

        # utime.sleep(0.25)

        response.close()
    except:
        print('Fail www connect...')


def isSunset():
    url = "http://192.168.86.240:5000/isSunset"

    print(url)

    try:
        response = urequests.get(url)

        # print(url)
        print(response.text)

        # utime.sleep(0.25)

        response.close()
    except:
        print('Fail www connect...')


def isHose():
    url = "http://192.168.86.240:5000/isHose"

    print(url)

    try:
        response = urequests.get(url)

        # print(url)
        print(response.text)

        # utime.sleep(0.25)

        response.close()
    except:
        print('Fail www connect...')


def main():  # Pump control
    # Set initial state
    np = neopixel.NeoPixel(machine.Pin(12), 4)
    np[powerLed] = red
    np.write()

    pumpState(stateOff)

    while True:
        # To pump or not to pump

        if isSunrise():
            pumpState(stateIrrigation)
        elif isSunset():
            pumpState(stateIrrigation)
        elif isHose():
            pumpState(stateHose)
        else:
            pumpState(stateOff)


main()
