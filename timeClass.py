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
    deviceid = ''

    # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
    NTP_DELTA = 3155673600

    host = "0.uk.pool.ntp.org"

    def __init__(self, deviceid):
        self.deviceid = deviceid

    def __call__(self, deviceid):
        self.deviceid = deviceid

    def gettime(self):
        try:
            NTP_QUERY = bytearray(48)
            NTP_QUERY[0] = 0x1b
            addr = socket.getaddrinfo(self.host, 123)[0][-1]
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
            s.close()
            val = struct.unpack("!I", msg[40:44])[0]

            return val - self.NTP_DELTA
        except OSError:

            return 0

    def settime(self, metheod):

        if metheod == 0:
            url = "http://192.168.86.240:5000/gettime/"

            print(url)

            try:
                response = urequests.get(url)

                returnvalue = int(response.text.replace('\"', ''))

                response.close()
            except:
                #  remoteHose = False
                #  remoteIrrigation = False
                #  remotePump = False
                print('Fail www connect...')

            # return returnvalue
        else:
            while self.gettime() == 0:
                print('Waiting for time...')

            t = self.gettime()
            tm = utime.localtime(t)
            tm = tm[0:3] + (0,) + tm[3:6] + (0,)

            machine.RTC().datetime(tm)

            print(utime.localtime())

