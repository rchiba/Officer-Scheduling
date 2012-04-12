'''
schedulePull.py
Pull schedule from database to use in schedule.py

Ryan Ball
'''

'''Useful links for MySQLdb

http://zetcode.com/databases/mysqlpythontutorial/
http://mysql-python.sourceforge.net/MySQLdb.htmlloc


'''

import MySQLdb as mdb

class schedulePull():
	def __init__(self):
		self.schedules = []
		self.dpID = 0
		self.db = 0
		self.password = "" #To change to using config file

	#Pass in dpID to run specific query to get equal dpID's
	def connectToDB(self, dp):
		self.dpID = dp
		#print 'Connecting to database with DP ID of', self.dpID, '\n'
		db=mdb.connect(host="localhost", user="root", 
											passwd=self.password, db="lapd") #Figure out how to prompt for password or just keep it hardcoded
		curs = db.cursor()
		curs.execute("""SELECT * 
								FROM OfficerSchedules NATURAL JOIN Officers
								WHERE dpID = %s""", (self.dpID,))
		#TODO: Comment out to be done on Ryo's end, return curs
		return curs
        #Create Officer here using row data
        '''
        Columns
        serialNO | dpID | watchID | assignmentID | schedule | request | divisionID | rankID | lastName | firstName
        '''
				

	def closeDB(self):
		if self.db:
			self.db.close()

class schedulePush():
	def __init__(self):
		self.schedules = []
		self.db = 0
		self.password = ""	#To change to using config file
		self.officers = []

	def connectToDB(self, offs, schds):
		self.schedules = schds
		self.officers = offs
		db=mdb.connect(host="localhost", user="root",
										passwd=self.password, db="lapd") 
		curs = db.cursor()
		for i in range(len(self.officers)):
			#print self.officers[i], self.schedules[i]
			curs.execute("""UPDATE OfficerSchedules
											SET genSchedule = %s
											WHERE serialNo = %s""", (self.schedules[i], self.officers[i]))
			
	def closeDB(self):
		if self.db:
			self.db.close()

            
def main():
	#Create instances of pull and push classes
	x = schedulePull()
	y = schedulePush()

	'''Pull requested schedules from database'''
	#Pass dpID {21,22}
	for i in range(21,23):
		x.connectToDB(i)

	#Close connection when done
	x.closeDB()

	'''
	Scheduling code
	'''

	'''Push created databases to database based on serialNo'''
	#Initialize arrays to pass
	schedules = []
	officers = []

	#Create mock schedules to add to database
	schedules.append("N N N R")
	schedules.append("R N N N")
	schedules.append("N R N N")

	#Create mock officers to add to database
	officers.append(12345)
	officers.append(44444)
	officers.append(69696)

	#Pass schedules & officer serialNo list
	y.connectToDB(schedules, officers)
	
	#Close connection when done
	y.closeDB()

if __name__ == "__main__":
	main()


