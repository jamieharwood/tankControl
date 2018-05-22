#!/usr/bin/env python3

import psycopg2

class sensorState:
    dbIPaddress = 'localhost'
    dbname = 'tank'
    user = 'tank'
    password = 'skinner2'
    dbconn = psycopg2.extensions.connection
    dbCur = psycopg2.extensions.cursor
    
    sensorId = 0
    sensorType = ''
    sensorValue = 0.0

    def __init__(self):
        self.dbconn = psycopg2.connect(host = self.dbIPaddress, dbname = self.dbname, user = self.user, password = self.password)
        self.dbconn.autocommit = True
        self.dbCur = self.dbconn.cursor()
        
        #self.getStatus()

    def __call__(self):
        self.dbconn = psycopg2.connect(host = self.dbIPaddress, dbname = self.dbname, user = self.user, password = self.password)
        self.dbconn.autocommit = True
        self.dbCur = self.dbconn.cursor()

    def getStatus(self,  sensorId):
        self.sensorId = sensorId
        
        sql = "select * from sensorStatus where sensorid = '{0}'".replace('{0}',  self.sensorId)
        self.dbCur.execute(sql)
        rows = self.dbCur.fetchall()
        
        for row in rows:
            self.sensorType = row[1]
            self.sensorvalue = row[2]
    
    def setSatus(self):
        sql = "insert into sensorStates (sensorid, sensortype, sensorvalue, enabled) values( '{0}', '{1}', {2}, 1 )"
        sql = sql.replace('{0}',  self.sensorId)
        sql = sql.replace('{1}',  self.sensorType)
        sql = sql.replace('{2}',  str(self.sensorvalue))
        
        print(sql)
        
        self.dbCur.execute(sql)

    def setHeartbeat(self):
        sql = "insert into sensorHeartbeats (sensorid) values('{0}')"
        sql = sql.replace('{0}',  self.sensorId)
        
        print(sql)
        
        self.dbCur.execute(sql)

# sensorId
    def setSensorID(self, sensorId):
            self.sensorId = sensorId
            #self.setSatus()
            
    def getSensorID(self):
            return self.sensorId
    
# sensorType
    def setSensorType(self, sensorType):
            self.sensorType = sensorType
            #self.setSatus()
            
    def getSensorType(self):
            return self.sensorType

# sensorvalue
    def setSensorValue(self, sensorvalue):
            self.sensorvalue = sensorvalue
            #self.setSatus()
            
    def getSensorValue(self):
            return self.sensorvalue

