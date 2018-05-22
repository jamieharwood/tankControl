#!/usr/bin/env python

import urequests


class SensorRegistation:
    __resthost = ''
    __deviceid = ''

    def __init__(self, resthost, deviceid):
        self.__resthost = resthost
        self.__deviceid = deviceid

    def __call__(self):
        pass

    def register(self, sensortype, sensormedium, provider):

        url = self.__resthost + "/sensorRegistration/{0}/{1}/{2}/{3}"
        url = url.replace('{0}', self.__deviceid)
        url = url.replace('{1}', sensortype)
        url = url.replace('{2}', sensormedium)
        url = url.replace('{3}', provider)

        print(url)

        try:
            response = urequests.get(url)

            response.close()
        except:
            print('Fail www connect...')


