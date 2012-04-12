'''
Ranker
Ranks schedules based on how well it satisfies request

Point scale is as follows

x = working day
o = off day
r = red day
l = training day
v = vacation day
t = accumulated time off
m = military leave without pay
p = military leave with pay


o - 1
r - 2
l - 4
v - 3
t - should already be taken care of
m - should already be taken care of
p - should already be taken care of


Not sure which days Ryo is removing from possibilities


'''
from scheduleRyo import Officer


def main():
	exampleSchedule = []
	exampleSchedule[Officer("serial","name","car","schedule","rank")] = "01001001" #8 day schedule
