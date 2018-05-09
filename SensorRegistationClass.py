#!/usr/bin/env python

import urequests


class SensorRegistation:
    deviceid = ''

    def __init__(self, deviceid):
        self.deviceid = deviceid

    def __call__(self, deviceid):
        self.deviceid = deviceid

    def register(self, sensortype, sensormedium, provider):

        url = "http://192.168.86.240:5000/sensorRegistration/{0}/{1}/{2}/{3}"
        url = url.replace('{0}', self.deviceid)
        url = url.replace('{1}', sensortype)
        url = url.replace('{2}', sensormedium)
        url = url.replace('{3}', provider)

        print(url)

        try:
            response = urequests.get(url)

            response.close()
        except:
            print('Fail www connect...')


