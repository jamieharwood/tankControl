#!/usr/bin/env python

import urequests
import machine
import utime
try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct


class TimeTank:
    __printl = None
    __resthost = ''
    __deviceid = ''

    # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
    addBST = 3600
    NTP_DELTA = 3155673600 - addBST

    __hostpointer = 0
    __host = "{0}.uk.pool.ntp.org"

    def __init__(self, resthost='', deviceid=0, logfunc=None):
        self.__resthost = resthost
        self.__deviceid = deviceid

        if logfunc is None:
            __printl = self.funcprintl
        else:
            __printl = logfunc

    def __call__(self):
        pass

    def funcprintl(self, statustext):
        print(statustext)

    def gettime(self):
        try:
            # cycle through the different uk.pool.ntp.org servers
            temphost = self.__host.replace('{0}', str(self.__hostpointer))
            print('Get time from: ' + temphost)

            self.__hostpointer += 1
            if self.__hostpointer > 3:
                self.__hostpointer = 0
            # cycle through the different uk.pool.ntp.org servers

            NTP_QUERY = bytearray(48)
            NTP_QUERY[0] = 0x1b
            addr = socket.getaddrinfo(temphost, 123)[0][-1]
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
            s.close()
            val = struct.unpack("!I", msg[40:44])[0]

            return val - self.NTP_DELTA
        except OSError:

            return 0

    def settime(self, metheod=1):
        returnvalue = False

        if metheod == 0:
            url = "http://192.168.86.240:5000/gettime/"

            print(url)

            try:
                response = urequests.get(url)

                returnvalue = int(response.text.replace('\"', ''))

                response.close()
            except:
                print('Fail www connect: ' + url)

            # return returnvalue
        else:
            while self.gettime() == 0:
                print('Waiting for time...')

            t = self.gettime()
            try:
                tm = utime.localtime(t)
                tm = tm[0:3] + (0,) + tm[3:6] + (0,)

                machine.RTC().datetime(tm)

                print('tm[0:3]=' + str(tm[0:3]) + ' tm[3:6]=' + str(tm[3:6]))
                print('tm[0] = (' + str(tm[0]) + ')')
                print(utime.localtime())

                if int(tm[0]) != int(2000):
                    returnvalue = True
            except:
                returnvalue = False

        return returnvalue

