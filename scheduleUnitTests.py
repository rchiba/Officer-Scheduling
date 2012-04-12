'''
scheduleUnitTests.py
Testing the scheduleRyo program

Ryo Chiba
'''

'''Useful links for MySQLdb

http://zetcode.com/databases/mysqlpythontutorial/

'''

import MySQLdb as mdb
from scheduleRyo import *

class unitTester():
    def __init__(self):
        self.mysqlUser = "root"
        self.mysqlPass = "" #To change to using config file
        self.host = "localhost"
        self.dbName = "lapd"
        self.connectToDB()

    #Pass in dpID to run specific query to get equal dpID's
    def connectToDB(self):
        self.db=mdb.connect(host=self.host, user=self.mysqlUser, passwd=self.mysqlPass, db=self.dbName)
        
    def test1(self):
        print "Test 1 - normative case with 5 users"
        curs = self.db.cursor()
        curs.execute("""TRUNCATE TABLE Officers; """)
        curs.execute("""INSERT INTO Officers (serialNo, divisionID, rankID, lastName, firstName) VALUES
        (69696, 3, 2, 'Ball', 'Ryan'),
        (12345, 3, 2, 'Smith', 'John'),
        (44444, 3, 2, 'Chiba', 'Ryo'),
        (44445, 3, 2, 'Hello', 'Ryo'),
        (44446, 3, 2, 'Bob', 'Ryo');""")
        
        curs.execute("""TRUNCATE TABLE OfficerSchedules; """)
        curs.execute("""INSERT INTO OfficerSchedules (serialNo, dpID, watchID, assignmentID, schedule, request, genSchedule) VALUES
        (12345, 22, 0, 0, 'N N N N V N', 1, 'N N N R'),
        (44444, 22, 0, 0, 'N N N V N N', 1, 'R N N N'),
        (44445, 22, 0, 0, 'V V N N N V', 1, 'R N N N'),
        (44446, 22, 0, 0, 'N V T V N V', 1, 'R N N N'),
        (69696, 22, 0, 0, 'N N N N T N', 1, 'N R N N');""")
        
        options = {}
        options['consecutiveLimit'] = 6
        options['scheduleDays'] = 6
        options['fulfillmentThreshold'] = 2
        options['maxDaysOff'] = 3
        options['patrolThreshold'] = 1
        options['dpid'] = 22
        x = lapdScheduler(options)
        x.schedule()
                
        curs.execute("""SELECT * 
                                FROM OfficerSchedules;""")
        # read out results
        for i in range(int(curs.rowcount)):
            row = curs.fetchone()
            print row
        
        print " "
        
    def test2(self):
        print "Test 2 - normative case with 10 users"
        curs = self.db.cursor()
        curs.execute("""TRUNCATE TABLE Officers; """)
        curs.execute("""INSERT INTO Officers (serialNo, divisionID, rankID, lastName, firstName) VALUES
        (69696, 3, 2, 'Ball', 'Ryan'),
        (12345, 3, 2, 'Smith', 'John'),
        (44444, 3, 2, 'Chiba', 'Ryo'),
        (44445, 3, 2, '1', 'Ryo'),
        (44446, 3, 2, '2', 'Ryo'),
        (44447, 3, 2, '3', 'Ryo'),
        (44448, 3, 2, '4', 'Ryo'),
        (44449, 3, 2, '5', 'Ryo'),
        (44450, 3, 2, '6', 'Ryo'),
        (44451, 3, 2, '7', 'Ryo');""")
        
        curs.execute("""TRUNCATE TABLE OfficerSchedules; """)
        curs.execute("""INSERT INTO OfficerSchedules (serialNo, dpID, watchID, assignmentID, schedule, request, genSchedule) VALUES
        (12345, 22, 0, 0, 'N N N N V N', 1, 'N N N R'),
        (44444, 22, 0, 0, 'N N N V N N', 1, 'R N N N'),
        (44445, 22, 0, 0, 'V V N N N V', 1, 'R N N N'),
        (44446, 22, 0, 0, 'N V T V N V', 1, 'R N N N'),
        (69696, 22, 0, 0, 'N N N N T N', 1, 'N R N N'),
        (44447, 22, 0, 0, 'N T T V N V', 1, 'R N N N'),
        (44448, 22, 0, 0, 'N T T V N V', 1, 'R N N N'),
        (44449, 22, 0, 0, 'N V N V N V', 1, 'R N N N'),
        (44450, 22, 0, 0, 'N V N V N V', 1, 'R N N N'),
        (44451, 22, 0, 0, 'N V N V N V', 1, 'R N N N');""")
        
        options = {}
        options['consecutiveLimit'] = 6
        options['scheduleDays'] = 6
        options['fulfillmentThreshold'] = 2
        options['maxDaysOff'] = 3
        options['patrolThreshold'] = 1
        options['dpid'] = 22
        x = lapdScheduler(options)
        x.schedule()
                
        curs.execute("""SELECT * 
                                FROM OfficerSchedules;""")
        # read out results
        for i in range(int(curs.rowcount)):
            row = curs.fetchone()
            print row
        
        print " "
    def closeDB(self):
        if self.db:
            self.db.close()

    def test3(self):
        print "Test 3 - testing rank constraint"
        print "num of P3s should always exceed P1s"
        curs = self.db.cursor()
        curs.execute("""TRUNCATE TABLE Officers; """)
        curs.execute("""INSERT INTO Officers (serialNo, divisionID, rankID, lastName, firstName) VALUES
        (33333, 1, 3, 'P3', 'Ryan'),
        (11111, 1, 1, 'P1', 'John'),
        (11112, 1, 1, 'P1', 'Ryo');""")
        
        curs.execute("""TRUNCATE TABLE OfficerSchedules; """)
        curs.execute("""INSERT INTO OfficerSchedules (serialNo, dpID, watchID, assignmentID, schedule, request, genSchedule) VALUES
        (33333, 22, 0, 0, 'N N N N N N', 1, 'N N N R'),
        (11111, 22, 0, 0, 'N N N N N N', 1, 'R N N N'),
        (11112, 22, 0, 0, 'N N N N N N', 1, 'R N N N');""")
        
        options = {}
        options['consecutiveLimit'] = 6
        options['scheduleDays'] = 6
        options['fulfillmentThreshold'] = 2
        options['maxDaysOff'] = 3
        options['patrolThreshold'] = 1
        options['dpid'] = 22
        x = lapdScheduler(options)
        x.schedule()
                
        curs.execute("""SELECT * 
                                FROM OfficerSchedules;""")
        # read out results
        for i in range(int(curs.rowcount)):
            row = curs.fetchone()
            print row
        
        print " "
            
def main():
    #Create instances of pull and push classes
    '''
    self.consecutiveLimit = 6 # how many consecutive days are they allowed to work?
    self.scheduleDays = 6 # how long is a schedule period?
    self.fulfillmentThreshold = 2 # how many officers need to work on a specific day?
    self.maxDaysOff = 3# how many total days can an officer take off at maximum 
    self.patrolThreshold = 1 # how many cars need to be on patrol every day?
    self.dpid = 22 # which deployment id to schedule?
    '''
    
    ut = unitTester()
    #ut.test1()
    #ut.test2()
    ut.test3()

if __name__ == "__main__":
    main()


