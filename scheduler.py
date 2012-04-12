'''
Created on Mar 27, 2012

@author: rchiba

Script to solve a CSP with officers 
'''
from constraint import *
import re
import time
from schedulePull import schedulePull, schedulePush #Ryan's module
import copy

class Officer():
    
    def __init__(self, mySerial, myName, myCar, mySchedule, myRank):
        self.serial = mySerial
        self.name = myName
        self.car = myCar
        self.requestedSchedule = mySchedule
        self.rank = myRank
     

class lapdScheduler():

    '''
    
    each officer will have a schedule that we input to this program, that will be 
    28 characters long, representing a requested schedule
    
    Key: (in order of importance to not cut)
    t - training days
    v - vacation days
    r - red days
    
    -----r-r-r---v---t-t----
    
    Taking this input, we'll remove all possibile schedules with these days
    
    '''

    '''
    options - all configurations needed to solve problem
    retry - a value from 0 to 3 that determines the progression
            of how constraints are turned off if solution is not found
    
    '''
    def __init__(self, options = None, retry = 0):
        
        #self.solver = BacktrackingSolver()
        #self.solver = RecursiveBacktrackingSolver()
        self.solver = MinConflictsSolver()
        self.problem = Problem(self.solver)
        self.options = options
        self.retry = retry
        if options is None:
            self.consecutiveLimit = 6 # how many consecutive days are they allowed to work?
            self.scheduleDays = 6 # how long is a schedule period?
            self.fulfillmentThreshold = 2 # how many officers need to work on a specific day?
            self.maxDaysOff = 3# how many total days can an officer take off at maximum 
            self.patrolThreshold = 1 # how many cars need to be on patrol every day?
            self.dpid = 22 # which deployment id to schedule?
        else:
            self.consecutiveLimit = options['consecutiveLimit'] # how many consecutive days are they allowed to work?
            self.scheduleDays = options['scheduleDays'] # how long is a schedule period?
            self.fulfillmentThreshold = options['fulfillmentThreshold'] # how many officers need to work on a specific day?
            self.maxDaysOff = options['maxDaysOff']# how many total days can an officer take off at maximum 
            self.patrolThreshold = options['patrolThreshold'] # how many cars need to be on patrol every day?
            self.dpid = options['dpid'] # which deployment id to schedule?
        
        # constraint flags
        self.determineConstraints(retry)
        
        # use ryan's module to get data
        self.schedulePush = schedulePush()
        self.schedulePull = schedulePull()
        self.officers = []
        self.carTypes = []
        curs = self.schedulePull.connectToDB(self.dpid)
        #print "mySerial, myName, myCar, mySchedule, myRank"
        for i in range(int(curs.rowcount)):
            row = curs.fetchone()
            #print "adding officer: "
            #print row
            #print row[0], row[10]+row[9], row[3], row[4], row[8]
            self.carTypes.append(row[3])
            # officer constructor (mySerial, myName, myCar, mySchedule, myRank)
            self.officers.append(Officer(row[0], row[10]+row[9], row[3], row[4], row[8]))
            '''
			Columns
			0 serialNO | dpID | watchID | assignmentID | schedule | request | divisionID | rankID | lastName | firstName
			'''
        # get a list of all distinct car types
        self.carTypes = list(set(self.carTypes))

    # a helper function to determine which constraints to activate
    def determineConstraints(self, retry):
        if retry == 0:
            self.tooManyConsecutiveWorkingDaysConstraint = True
            self.tooFewWorkingDaysConstraint = True
            self.offDaysConstraints = True
            self.p3p1TetherConstraint = True
            self.meetTheNeedsConstraint = True
        elif retry == 1:
            self.tooManyConsecutiveWorkingDaysConstraint = True
            self.tooFewWorkingDaysConstraint = True
            self.offDaysConstraints = True
            self.p3p1TetherConstraint = False
            self.meetTheNeedsConstraint = True
        elif retry == 2:
            self.tooManyConsecutiveWorkingDaysConstraint = True
            self.tooFewWorkingDaysConstraint = True
            self.offDaysConstraints = True
            self.p3p1TetherConstraint = False
            self.meetTheNeedsConstraint = False
        elif retry == 3:
            print "No solutions found, even after reducing constraints"
    
    # generate regex from requestedSchedulesString
    def scheduleToRegex(self,schedule):
        # they are coming in like "N N T N N"
        schedule = schedule.replace(' ', '')
        regex = re.sub(r'\s', "", schedule)
        regex = re.sub("[N]", "[01]", schedule)
        regex = re.sub("[T]", "[1]", regex)
        regex = re.sub("[VR]", "[0]", regex)
        # so this regex needs to match when rvt is set to working
        #print "scheduleToRegex = %s" % regex
        return regex
    
   
    
    # remove from the possibilities the days that the officers request off
    # each schedule will have this run on it
    def removeOffDays(self):
        
        # remove red days
        '''
        ex: -----r-r-r---v-
         -> 000001010100010 - we don't want possibilities where any of these are 1
        requestedSchedule - the string schedule
        domain - a lits of possibilities
        '''
        
        for officer in self.officers:
            #print officer.name
            #print officer.domain
            goodDomainReg = self.scheduleToRegex(officer.requestedSchedule)
            # for all the domains, remove all entries that fail the regex
            badPossibilities = []
            for possibility in officer.domain:
                #print "comparing"
                #print goodDomainReg
                #print self.expandBin(bin(possibility), self.scheduleDays)
                if re.search(goodDomainReg, self.expandBin(bin(possibility), self.scheduleDays)) is None: # we want to flag it as bad if it is none
                    #print 'bad possibility: %s %s' % (self.expandBin(bin(possibility), self.scheduleDays), officer.name)
                    badPossibilities.append(possibility);
                # else:
                    #print 'good possibility: %s %s' % (self.expandBin(bin(possibility), self.scheduleDays), officer.name)
            for badPossibility in badPossibilities:
                #print 'removing bad possibilities for %s' % officer.name
                officer.domain.remove(badPossibility)
    
    
    def fulfillmentConstraint(self, i, *args):
        sum = 0
        for officerSchedule in args:
            sum = sum + int(self.expandBin(bin(officerSchedule), self.scheduleDays)[i])
        
        return sum > self.fulfillmentThreshold
    
    def getDayInt(self, i, possibility):
        return int(self.expandBin(bin(possibility), self.scheduleDays)[i])
        
    
    def schedule(self):
        startTime = time.clock()
       
        # for 15 days, domain of officers consists of a number 0-32767 = 2^15 possibilities, which is the number of possible schedules an officer can have
        officerDomain = range(0, 2**self.scheduleDays-1)
        
        # OVERALL CONSTRAINTS ______________________________________________
        
        # * remove all entries that have more too many consecutive working days
        if self.tooManyConsecutiveWorkingDaysConstraint:
            badPossibilities = []
            for possibility in officerDomain:
                if re.search("1{%s,}" % self.consecutiveLimit, bin(possibility)):
                    #print 'consecutive bad possibility: %s' % bin(possibility)
                    badPossibilities.append(possibility);
            for badPossibility in badPossibilities:
                officerDomain.remove(badPossibility)
        
        # * remove all entries that have too few working days
        if self.tooFewWorkingDaysConstraint:
            badPossibilities = []
            for possibility in officerDomain:
                if self.expandBin(bin(possibility), self.scheduleDays).count("0") > self.maxDaysOff:
                    badPossibilities.append(possibility);
            
            for badPossibility in badPossibilities:
                officerDomain.remove(badPossibility)
        
        # creating domains for each officer based off of the common officer domain
        # each officerDomain in officer domains is a list of all possibilities
        for officer in self.officers:
            # print 'adding officer domain to %s' % officer.name
            # print 'domain is %s' % officerDomain
            officer.domain = copy.deepcopy(officerDomain)
        
        
        # SPECIFIC CONSTRAINTS ______________________________________________
        # 1. remove the domains that fail the regex for requested schedules
        if self.offDaysConstraints:
            self.removeOffDays()
            
        # all bad domains removed, so add officers and domains to problem
        
        # add each officer
        for officer in self.officers:
            #print 'adding domain for %s' % officer.name
            #print officer.domain
            self.problem.addVariable(officer, officer.domain)
            
        # 2. each day should have a certain number of officers working
        # we find the sum of a list of all of the officer's bits for a given day
        if self.meetTheNeedsConstraint is True:
            for i in range(0,self.scheduleDays):
                def makeConstraint(day):
                    def rankConstraint(*args):
                        # print "sum is "
                        # print sum(map(self.getDayInt,[i]*len(args), args))
                        return sum(map(self.getDayInt,[day]*len(args), args)) >= self.fulfillmentThreshold

                    return rankConstraint
                    
                fulfillmentConstraint = makeConstraint(i) 
                self.problem.addConstraint(fulfillmentConstraint, self.officers)

        # 3. P1s paired with P3s for a given car (P3s must outnumber or equal P1s for a given car)
        # need to access variables somehow to remove domains where p1's can't be paired with p3's
        if self.p3p1TetherConstraint is True:
            for i in range(0,self.scheduleDays):
                for car in self.carTypes:
                    P3s = [officer for officer in self.officers if officer.car == car and officer.rank == 3 ]
                    P1s = [officer for officer in self.officers if officer.car == car and officer.rank == 1 ]
                    if len(P1s)>0: # only worry about this constraint if you have rookies on your squad
                        myofficers = P1s
                        myofficers.extend(P3s)
                        
                        # using closure to make our lives better
                        # http://ynniv.com/blog/2007/08/closures-in-python.html
                        def makeConstraint(x, day):
                            def rankConstraint(*args):
                                p1s = args[0:len(x)]
                                p3s = args[len(x):]
                                # sum of p3s on a given day must be greater or equal to the number of p1s
                                numP3s = sum(map(self.getDayInt,[i]*len(p3s), p3s))
                                numP1s = sum(map(self.getDayInt,[i]*len(p1s), p1s))
                                #print numP3s, numP1s
                                res =  numP3s >= numP1s
                                return res

                            return rankConstraint
                            
                        for i in range(0,self.scheduleDays): # for each day, add a constraint
                            constraint = makeConstraint(P1s, i)
                            self.problem.addConstraint(constraint, myofficers)
        
        endTime = time.clock()
        print "problem definition took %s" % (endTime - startTime)
        
        startTime = time.clock()
        sol = self.problem.getSolution()
        
        
        if sol is not None:
            for key in sol:
                #print "%s %s" % (key.name, self.expandBin(bin(sol[key]), self.scheduleDays))
                self.schedulePush.connectToDB([key.serial], [self.expandBin(bin(sol[key]), self.scheduleDays)]) # push to mysql
        else:
            # no solution called, so recursively call self
            print "No solution found, trying again."
            x = lapdScheduler(self.options, self.retry+1)
            x.schedule()
            
        endTime = time.clock()
        
        self.schedulePush.closeDB()
        
        print "problem.getSolution() took %s" % (endTime - startTime)
        
        
    # used to conver bin output to something more usable in the lambdas
    # 0b101 -> 000000000101
    def expandBin(self, str, bitLength):
        temp = str
        length = len(str)
        if bitLength < length-2:
            print "ERR: expandbin was given a bitlength shorter than str length %s %s" % (temp,bitLength)
        # remove the 0b
        str = str[2:]
        # add as many zeros to the beginning as needed
        while(len(str)<bitLength):
            str = "0"+str
        
        #print "expandBin: %s -> %s" % (temp, str)
        return str


def main():
    x = lapdScheduler()
    x.schedule()
        
if __name__ == "__main__":
    main()