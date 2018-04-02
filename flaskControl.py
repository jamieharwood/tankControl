#!/usr/bin/env python3

#from pumpStatusClass import PumpStatus
#from ledcontrolClass import ledcontrol
#import json
from flask import Flask
app = Flask(__name__)

@app.route('/valueStatus/<componentID>')
def valueStatus(componentID):
    # call for action
    # irrigation
    # hose
    return 'valueStatus'
    
@app.route('/pumpStatus/<componentID>')
def pumpStatus(componentID):
    # call for action
    # main irrigation pump
    # remote tank pump 1
    # remote tank pump 2
    return 'pumpStatus'
    
@app.route('/moistureStatus/<componentID>')
def moistureStatus(componentID):
    # call for action
    # many sensors
    return 'valueStatus'

@app.route('/levelStatus/<componentID>')
def levelStatus(componentID):
    # call for action
    # 3 sensors per tank sensors
    return 'valueStatus'
