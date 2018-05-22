#!/usr/bin/env python

import urequests
import network

class HeartBeat:
    __resthost = ''
    __deviceid = ''
    __ip = ''
    __rssi = 0

    def __init__(self, resthost, deviceid):
        self.__resthost = resthost
        self.__deviceid = deviceid
        self.__getip__()

    def __call__(self):
        pass

    def __getip__(self):

        sta_if = network.WLAN(network.STA_IF)
        self.__rssi = sta_if.status('rssi')

        if sta_if.active():
            temp = sta_if.ifconfig()
            self.__ip = temp[0]
        else:
            self.__ip = '0.0.0.0'

    def beat(self):
        self.__getip__()

        url = self.__resthost + "/sensorHeartbeatIP/{0}/{1}/{2}"
        url = url.replace('{0}', self.__deviceid)
        url = url.replace('{1}', self.__ip)
        url = url.replace('{2}', str(self.__rssi))

        print(url)

        try:
            response = urequests.get(url)

            response.close()
        except:
            print('Fail www connect...')
