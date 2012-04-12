#Scheduling police officers using a CSP solver#

###Constraint Satisfaction Problems, What Are They?###
* Here's a textbook chapter that does a good job of explaining things in math language: http://aima.cs.berkeley.edu/newchap05.pdf
* CSP's involve 3 main concepts: **variables, domains, and constraints**
* **variables** are the units of data that you want to solve for
* **domains** are the possible outcomes that the units of data could be
* **constraints** are ways to describe what the variables can/cannot be

###Tools Used###
* Python Constraint Solver (http://labix.org/python-constraint)

###Example of a simple CSP (taken from python-constraint)###
So how do we translate a typical CSP to python to solve? Consider some trivial CSP:

* We have two variables, `a` and `b`

* We have a constraint, that `b` must be twice the value of `a`

* `a` can be 1, 2, or 3

* `b` can be 4, 5, or 6

```python

>>> from constraint import *
>>> problem = Problem()
>>> problem.addVariable("a", [1,2,3])
>>> problem.addVariable("b", [4,5,6])
>>> problem.getSolutions()
[{'a': 3, 'b': 6}, {'a': 3, 'b': 5}, {'a': 3, 'b': 4},
 {'a': 2, 'b': 6}, {'a': 2, 'b': 5}, {'a': 2, 'b': 4},
 {'a': 1, 'b': 6}, {'a': 1, 'b': 5}, {'a': 1, 'b': 4}]

>>> problem.addConstraint(lambda a, b: a*2 == b,
                          ("a", "b"))
>>> problem.getSolutions()
[{'a': 3, 'b': 6}, {'a': 2, 'b': 4}]

```

###How do we model a schedule?###
First, define the problem:

* Officers can either work, or not work on a day

* A schedule consists of seven days

* Officers cannot work more than 3 days off in a row

* We need a certain number of officers working on a day

* We always need more senior officers working each day than new recruits

###CSP's, what are they again?###

They are: **variables**, **domains**, **constraints**

Let's break the problem down

* **variables** - officer schedules

* **domains** - possible schedules

* **constraints** - the requirements we mentioned above

###Translating to Code###

We can represent each officer's schedule with 7 bits, which can be translated into integers for our convenience (binary 1000000 -> decimal 64)

So, minus the constraints, the possibility for each schedule is all integers from 0 to 2^7-1

```python
scheduleDays = 7
officerDomain = range(0, 2**scheduleDays-1)
```

Much like the algebra problem, we first figure out what possible schedules are available, ruling out ones that obviously violate the constraints

Even before entering any constraints into the library, we can take some possibilities out, for example, all schedules with more than 3 consecutive working days can be removed:

```python
consecutiveWorkingDaysLimit = 3
badPossibilities = []
for possibility in officerDomain:
    if re.search("1{%s,}" % consecutiveWorkingDaysLimit, bin(possibility)):
        badPossibilities.append(possibility);
for badPossibility in badPossibilities:
    officerDomain.remove(badPossibility)
```

After we have defined the domains, let's create the problem and add the variables

```python
solver = MinConflictsSolver()
problem = Problem(solver)

officers = []
officers.append({'name':'Ryan', 'rank':'3'})
officers.append({'name':'Mond', 'rank':'1'})
officers.append({'name':'Eric', 'rank':'3'})
for officer in officers:
    problem.addVariable(officer, officerDomain)
```

The other constraints can't be done in the same way as were done above, since these constraints apply over a group of variables. So, we translate the constraint into a function and use the library to apply it to all, or a subset of our variables

For the constraint where we have to define a certain number of officers working on a day:

```python

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

def getDayInt(self, i, possibility):
    return int(self.expandBin(bin(possibility), scheduleDays)[i])

fulfillmentThreshold = 2 #how many officers need to be working each day?   
 
for i in range(0,scheduleDays):
    def makeConstraint(day):
        def rankConstraint(*args):
            return sum(map(getDayInt,[day]*len(args), args)) >= fulfillmentThreshold

        return rankConstraint
        
    fulfillmentConstraint = makeConstraint(i) 
    problem.addConstraint(fulfillmentConstraint, officers)
```

For the constraint where we need more senior officers working each day than new recruits (this is a bit tricky):

```python
for i in range(0,scheduleDays):
    P3s = [officers if officer.rank == '3']
    P1s = [officers if officer.rank == '1']
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
                numP3s = sum(map(getDayInt,[i]*len(p3s), p3s))
                numP1s = sum(map(getDayInt,[i]*len(p1s), p1s))
                #print numP3s, numP1s
                res =  numP3s >= numP1s
                return res

            return rankConstraint
            
        for i in range(0,scheduleDays): # for each day, add a constraint
            constraint = makeConstraint(P1s, i)
            self.problem.addConstraint(constraint, myofficers)
```

Now, we use the library and solve the problem (this is NP hard, so please be patient)

```python
sol = problem.getSolution()
    if sol is not None:
        for key in sol:
            #print "%s %s" % (key.name, bin(sol[key]))
    else:
        # no solution called, so recursively call self
        print "No solution found, trying again."
```


