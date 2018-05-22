#!/usr/bin/env python3

import requests


def main():
    resp = requests.get('http://192.168.86.240:5000/getControlStates/')

    if resp.status_code != 200:
        raise ApiError('GET /tasks/ {}'.format(resp.status_code))
    else:
        retrieved = resp.json()

        print(str(retrieved['isWet']))

        """
        conn = psycopg2.connect(host='localhost', dbname='tankstore', user='tank', password='skinner2')
        conn.autocommit = True
        cur = conn.cursor()

        sql = "INSERT INTO public.sunrisesetnow (sunrise, sunset, day_length) VALUES ('{0}', '{1}', '{2}')"
        sql = sql.replace('{0}', retrieved['results']['sunrise'])
        sql = sql.replace('{1}', retrieved['results']['sunset'])
        sql = sql.replace('{2}', retrieved['results']['day_length'])

        cur.execute(sql)
        """


main()