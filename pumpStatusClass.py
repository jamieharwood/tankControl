#!/usr/bin/env python3

import psycopg2

class PumpStatus:
    dbIPaddress = 'localhost'
    dbconn = psycopg2.extensions.connection
    dbCur = psycopg2.extensions.cursor
    
    hosestate = 0
    irrigationstate = 0
    pumpstate = 0
    eventname = 'Not sure what\'s going on!'
    
    def __init__(self):
        self.dbconn = psycopg2.connect(host = self.dbIPaddress, dbname='tankstore', user='tank', password='skinner2')
        self.dbconn.autocommit = True
        self.dbCur = self.dbconn.cursor()

    def __call__(self):
        self.dbconn = psycopg2.connect(host = self.dbIPaddress, dbname='tankstore', user='tank', password='skinner2')
        self.dbconn.autocommit = True
        self.dbCur = self.dbconn.cursor()
    
    def setSatus(self,  hosestate,  irrigationstate,  pumpstate,  eventname):
        self.hosestate = hosestate
        self.irrigationstate = irrigationstate
        self.pumpstate = pumpstate
        self.eventname = eventname
        
        sql = "insert into pumpcontrol (hosestate, irrigationstate, pumpstate, eventname) values({0}, {1}, {2}, '{3}')"
        sql = sql.replace("{0}", str(self.hosestate))
        sql = sql.replace("{1}", str(self.irrigationstate))
        sql = sql.replace("{2}", str(self.pumpstate))
        sql = sql.replace("{3}", str(self.eventname))
        
        self.dbCur.execute(sql)

    def getStatus(self):
        sql = "select hosestate, irrigationstate, pumpstate, eventname from pumpcontrol where datestamp = (select MAX(datestamp) from pumpcontrol)"
        self.dbCur.execute(sql)
        rows = self.dbCur.fetchall()
        
        for row in rows:
            self.hosestate = row[0]
            self.irrigationstate = row[1]
            self.pumpstate = row[2]
            #self.eventname = row[3]
