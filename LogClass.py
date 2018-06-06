#!/usr/bin/env python

import urequests
import network
import uio
#import esp
import gc
from machine import RTC
# from timeClass import TimeTank

class Log:
    __resthost = ''
    __deviceid = ''
    __ip = ''
    __rssi = 0
    __currHour = 0
    __currMinute = 0
    __logto = 1  # 0 = file and 1 = restful

    # __file = uio.open("tank.log", "a", encoding="utf-8")
    # __output = uio.StringIO()

    def __init__(self, resthost='', deviceid=''):
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

    def printl(self, outstring):
        rtc = RTC()
        timeNow = rtc.datetime()
        __currHour = timeNow[4]
        __currMinute = timeNow[5]
        self.__getip__()

        if self.__logto == 0:
            outbuffer = '['
            outbuffer += '\'' + str(__currHour) + ':' + str(__currMinute) + '\', '
            outbuffer += '\'' + self.__deviceid + '\', '
            outbuffer += '\'' + self.__ip + '\', '
            outbuffer += '\'' + str(self.__rssi) + '\', '
            # outbuffer += '\'' + str(esp.freemem()) + '\', '
            outbuffer += '\'' + str(gc.mem_free()) + '\', '
            outbuffer += '\'' + outstring + '\', '
            outbuffer += ']\n'

            f = uio.open("tank.log", "a", encoding="utf-8")
            f.write(outbuffer)
            f.close()
        else:
            # api.add_resource(LogEvents,
            # '/logEvent/<string:sensorId>/<string:sensorIp>/<string:rssi>/<string:freemem>/<string:resthost>/<string:logtext>')

            url = self.__resthost + "/logEvent/{0}/{1}/{2}/{3}/{4}"
            url = url.replace('{0}', self.__deviceid)
            url = url.replace('{1}', self.__ip)
            url = url.replace('{2}', str(self.__rssi))
            # url = url.replace('{3}', str(esp.freemem()))
            url = url.replace('{3}', str(gc.mem_free()))
            url = url.replace('{4}', outstring.replace(' ', '_'))

            print(url)

            try:
                response = urequests.get(url)

                response.close()
            except:
                print('Fail www connect...')

