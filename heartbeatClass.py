#!/usr/bin/env python

import urequests
import network

class HeartBeat:
    deviceid = ''
    ip = ''

    def __init__(self, deviceid):
        self.deviceid = deviceid
        self.__getip__()

    def __call__(self, deviceid):
        self.deviceid = deviceid
        self.__getip__()

    def __getip__(self):

        sta_if = network.WLAN(network.STA_IF)
        if sta_if.active():
            temp = sta_if.ifconfig()
            self.ip = temp[0]
        else:
            self.ip = '0.0.0.0'

    def beat(self):
        self.__getip__()

        url = "http://192.168.86.240:5000/sensorHeartbeatIP/{0}/{1}"
        url = url.replace('{0}', self.deviceid)
        url = url.replace('{1}', self.ip)

        print(url)

        try:
            response = urequests.get(url)

            response.close()
        except:
            print('Fail www connect...')
