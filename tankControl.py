#!/usr/bin/env python3

from settings import settingsClass
from sunrisesetClass import sunRiseSet
#from ledcontrolClass import ledcontrol
from weatherClass import weather
from pumpStatusClass import PumpStatus
import socket
import time
import datetime
import subprocess
import pytz

myTimeZone= pytz.timezone('Europe/London')

def checkProcess(processname):
    procList = subprocess.getstatusoutput('ps ax | grep {0} | grep -v grep | awk \'{print $1}\''.replace('{0}',  processname))
    if (len(procList[1]) > 0):

        processCount = str(procList[1] ).count('\n')

        if (processCount > 0):
            print('kill {0}'.replace('{0}',  processname))
            quit()
        else:
            print('run {0}'.replace('{0}',  processname))

def getStatusTrendText(trend):
    nowTime = datetime.datetime.now(myTimeZone)
    trend = trend[1:len(trend)-1]
    
    if (nowTime.minute > 9):
        returnString = "  @" + str(nowTime.hour) + ":" + str(nowTime.minute)
    else:
        returnString = "  @" + str(nowTime.hour) + ":0" + str(nowTime.minute)
    
    returnString = returnString + chr(0) + "no irrigation due to " + trend.lower() +"."
    
    return returnString

def getStatusText(sunrise,  sunset):
    nowTime = datetime.datetime.now(myTimeZone)
        
    if (nowTime.minute > 9):
        returnString = "  @" + str(nowTime.hour) + ":" + str(nowTime.minute) + chr(0)
    else:
        returnString = "  @" + str(nowTime.hour) + ":0" + str(nowTime.minute) + chr(0)
    returnString = returnString + chr(0) + chr(30) + sunrise[0:5] +"  "
    returnString = returnString + chr(31) + sunset[0:5]
    
    return returnString
    
def main():
    # Setup
    checkProcess('control.py')
    
    state = -2 # Startup state
    myWeather  = weather()
    #myLedControl = ledcontrol() # init remote led control
    mySettings = settingsClass() # get settings from db
    myPumpStatus = PumpStatus()
    #mySettings.resetSettings()
        
    # Init pump and soleniods
    hostname = 'tankControl'
    mqServerAddr = socket.gethostbyname(hostname)
    hostname = socket.gethostname()
    
    # ****************************************
    # Set init hose, irrigation and pump state
    hoseState = 0
    irrigationState = 0
    pumpState = 0
    
    #myPumpStatus.setSatus(hoseState,  irrigationState,  pumpState,  'Initiate the app')
    #myPumpStatus.getStatus()

    #jason = json .dumps(returnString)
    #myMqControl = mqPump(mqServerAddr)
    #myMqControl.send(hoseState, irrigationState, pumpState)
    # ****************************************
    
    # Init sensors and tank display
    #tankLeds = {'pin0': 1,  'pin1': 1,  'pin2': 1, 'pin3': 0,  'pin4': 0,  'pin5': 1,  'pin6': 0,  'pin7': 0 }
    #mySensor = mqSensor(mqServerAddr)
    #mySensor.send(tankLeds)
    
    # Set sunrise sunset vars
    dayRollover = -1 # get new sunrise sunset times only once!
    mySunrise = sunRiseSet() # Get sunrise and sunset from DB
    
    myWeather.getWeather()
    
    myTimeNow = datetime.datetime.now(myTimeZone)
    currTime = myTimeNow.hour + myTimeNow.minute
    lastTime = currTime
    currHour = -1
    lastHour = -2
    
    while True: # Loop
        myTimeNow = datetime.datetime.now(myTimeZone)
        currTime = myTimeNow.hour + myTimeNow.minute
        currHour = myTimeNow.hour
        
        # Update the time string for the display every minute
        if (currTime != lastTime and state == -1):
            lastTime = currTime
        
        # Update the weather trend (last 24 hours) every hour
        if (currHour != lastHour):
            lastHour = currHour
            myWeather.getWeather()
            myWeather.getRecentTrend()
        
        # get new sunrise and sunset times
        rollTime = myTimeNow.hour + myTimeNow.minute
        if (rollTime == 0 and dayRollover == -1):
            mySunrise = sunRiseSet()
            
            dayRollover = 0
        elif (rollTime == 0 and dayRollover == 0):
            dayRollover = 0
        else:
            dayRollover = -1
        
        numStartTime = (myTimeNow.hour * 3600) + (myTimeNow.minute * 60) + myTimeNow.second

        # *****************************************************
        # complex if conditions so I pulled them into variables
        # Extreme weather
        ifWeatherTrend = ((myWeather.isTrend('Rain') or myWeather.isTrend('Snow')) and state != 5)
        
        # Normal sun rise and set
        ifSunrise = ((numStartTime >= mySunrise.numSunriseSeconds and numStartTime <= (mySunrise.numSunriseSeconds + (mySettings.settings["pumpduration"] * 60))) and state != 1)
        ifSunset = ((numStartTime >= mySunrise.numSunsetSeconds and numStartTime <= (mySunrise.numSunsetSeconds + (mySettings.settings["pumpduration"] * 60))) and state != 4)
        
        # Irrigation and hose requests
        ifIrrigationButton = False #ifIrrigationButton = (str(mySensor.settings['irrigationButton']) =='1');
        ifHose = False #ifHose = (str(mySensor.settings['hoseButton']) =='1') ;
        
        # Return from all previous states
        ifBauFromSunrise = (not(numStartTime >= mySunrise.numSunriseSeconds and numStartTime <= (mySunrise.numSunriseSeconds + (mySettings.settings["pumpduration"] * 60))) and state == 1) 
        ifBauFromSunset = (not(numStartTime >= mySunrise.numSunsetSeconds and numStartTime <= (mySunrise.numSunsetSeconds + (mySettings.settings["pumpduration"] * 60))) and state == 4)
        ifBauFromIrrigationButton = (ifIrrigationButton == False and state == 3)
        ifBauFromHoseButton = (ifHose == False and state == 2)
        ifBauFromStartup = ((ifIrrigationButton or ifHose) and state == -2)
        # *****************************************************
        
        if (ifWeatherTrend == True and (ifHose == False and state != 2)):
            state = 5 # Weather is rain or snow
            
            hoseState = 0
            irrigationState = 0
            pumpState = 0
            
            myPumpStatus.setSatus(hoseState,  irrigationState,  pumpState,  'state = 5')
            
        elif (ifIrrigationButton and ifHose):
            #Fail
            
            hoseState = 0
            irrigationState = 0
            pumpState = 0
            
            myPumpStatus.setSatus(hoseState,  irrigationState,  pumpState,  'state = fail')
            
        elif (ifSunrise):
            # sunrise irrigation requested
            state = 1 # Sunrise state
            
            hoseState = 0
            irrigationState = 1
            pumpState = 1
            
            myPumpStatus.setSatus(hoseState,  irrigationState,  pumpState,  'state = 1')

        elif (ifSunset):
            # sunrise irrigation requested
            state = 4 # Sunset state
            
            hoseState = 0
            irrigationState = 1
            pumpState = 1
            
        elif (ifIrrigationButton and state != 3):
            # sunrise irrigation requested
            state = 3 # Sunrise state
            
            hoseState = 0
            irrigationState = 1
            pumpState = 1
            
            myPumpStatus.setSatus(hoseState,  irrigationState,  pumpState)

        elif (ifHose and state != 2):
            # hose requested on
            state = 2 # Hose state
            
            hoseState = 1
            irrigationState = 0
            pumpState = 1
            
            myPumpStatus.setSatus(hoseState,  irrigationState,  pumpState,  'state = 2')

        elif (ifBauFromSunrise or ifBauFromSunset or ifBauFromStartup or ifBauFromIrrigationButton or ifBauFromHoseButton):
            # BAU state
            state = -1
            
            hoseState = 0
            irrigationState = 0
            pumpState = 0
            
            myPumpStatus.setSatus(hoseState,  irrigationState,  pumpState,  'state = -1')

        time.sleep(5)
        
main()
