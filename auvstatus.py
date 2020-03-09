#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
	Version 1.2 - making UBAT pontus-specific (move to svg["pontus"] for more vehicles)
	Version 1.1 - adding cart
	Version 1.0 - works for pontus
	
	Usage: auvstatus.py -v pontus -r  (see a summary of reports)
	       auvstatus.py -v pontus > pontusfile.svg  (save svg display)
			 
	  https://okeanids.mbari.org/TethysDash/api/events?vehicles=pontus&eventTypes=logImportant&limit=4
	  

	  Battery thresholds:
	  onfigSet IBIT.batteryVoltageThreshold 13 v persist;configSet IBIT.batteryCapacityThreshold 15 Ah persist
	  
	 	  
	  Ground faults - check with Erik about what is most useful for GF reporting
	  
	  TODO: query missions to get the defaults:
	  https://okeanids.mbari.org/TethysDash/api/git/mission/Science/isotherm_depth_sampling.xml?tag=2019-12-03'
	  
	  
	  '''

import argparse
import sys
import time
import os
import urllib2
import json
import math
from collections import deque
from LRAUV_svg import svgtext,svghead,svgpontus,svgtail   # define the svg text?

# Default timeouts for selected missions

def get_options():
	parser = argparse.ArgumentParser(usage = __doc__) 
#	parser.add_argument('infile', type = argparse.FileType('rU'), nargs='?',default = sys.stdin, help="output of vars_retrieve")
	parser.add_argument("-b", "--DEBUG",	action="store_true", help="Print debug info")
	parser.add_argument("-r", "--report",	action="store_true", help="print results")
	parser.add_argument("-f", "--savefile",	action="store_true", help="save to SVG named by vehicle at default location")
	parser.add_argument("-v", "--vehicle",	default="pontus"  , help="specify vehicle")
	parser.add_argument("-m", "--missions",action="store_true"  , help="spit out mission defaults")
	parser.add_argument("Args", nargs='*')
	options = parser.parse_args()
	return options


def hours(unixtime):
	t1=time.localtime(unixtime/1000)
	TimeString = time.strftime('%H:%M',t1)
	return TimeString

def sendMessage(MessageText="EV Status"):
	import smtplib
	import settings

	from email.mime.text import MIMEText


	# PCfB Stuff
	me = 'steve@jellywatch.org'
	port = 587
	password = settings.pa
	mailhost = 'smtp.dreamhost.com'

	you = '8315667696@mms.att.net'
	msg = MIMEText(MessageText)
	msg['Subject'] = "EV Charger" 
	msg['From'] = me
	msg['To'] = you

	server = smtplib.SMTP(mailhost, port)
	# server.ehlo()
	server.starttls()
	# server.ehlo()
	server.login(me, password)
	server.sendmail(me, you, msg.as_string() )
	server.quit()

def getMissionDefaults():
	missions=["Science/profile_station","Science/sci2","Transport/keepstation","Maintenance/ballast_and_trim","Transport/keepstation_3km","Transport/transit_3km","Science/spiral_cast"]
	for mission in missions:
		URL = "https://okeanids.mbari.org/TethysDash/api/git/mission/{}.xml".format(mission)
		print "\n#===========================\n",mission, "\n"
		try:
			connection = urllib2.urlopen(URL,timeout=5)
		except urllib2.HTTPError:
			print >> sys.stderr, "\n###", mission, "not found"
			connection=False
			
		if connection:
			raw = connection.read()
			structured = json.loads(raw)
			connection.close()
			result = structured['result']
			
			print URL
			try: 
				print result
			except KeyError:
				print "NA"
	

def runQuery(vehicle,events,limit="",timeafter="1234567890123"):
	vehicle = VEHICLE
	BaseQuery = "http://okeanids.mbari.org/TethysDash/api/events?vehicles={0}&eventTypes={1}{2}&from={3}"
	URL = BaseQuery.format(vehicle,events,limit,timeafter)
	
	connection = urllib2.urlopen(URL,timeout=5)
	if connection:
		raw = connection.read()
		structured = json.loads(raw)
		connection.close()
		result = structured['result']
	else:
		result = '# offline'
	if DEBUG:
		print URL
		print result
	return result
	
	
def getDeployment():
	startTime = 0
	launchString = runQuery(VEHICLE,"launch","&limit=1",)
	startTime = launchString[0]['unixTime']
	return startTime
	
def getRecovery(starttime):
	launchString = runQuery(VEHICLE,"recover","&limit=1",starttime)
	recover = False
	if launchString:
		recover = launchString[0]['unixTime']
	
	return recover

def getPlugged(starttime):
	launchString = runQuery(VEHICLE,"deploy","&limit=1",starttime)
	plugged = False
	if launchString:
		plugged = launchString[0]['unixTime']
	
	return plugged
 
def getGPS(starttime):
	''' TODO Might need to go way back to get two spots to compare -- these two are consecutive fixes so not the speed.
	Have the second older fix be at least 20+ minutes before'''
	qString = runQuery(VEHICLE,"gpsFix","&limit=1",starttime)
	retstring=""
	if qString:
		retstring = qString	
	return retstring
	
def getOldGPS(starttime,missionstart):
	previoustime = starttime - 30*60*1000
	qString = runQuery(VEHICLE,"gpsFix","&limit=1&to={}".format(previoustime),missionstart)
	retstring=False
	if qString:
		retstring = qString
	return retstring


def getCritical(starttime):
	qString = runQuery(VEHICLE,"logCritical","",starttime)
	retstring = False
	if qString:
		retstring = qString
	
	return retstring

def parseGPS(recordlist):
	# print "GPS record", recordlist
	'''[{u'eventId': 12283560, u'unixTime': 1583301462000, u'vehicleName': u'pontus', u'fix': {u'latitude': 36.757467833070464, u'date': u'Wed Mar 04 05:57:42 GMT 2020', u'longitude': -122.02584799923866}, u'eventType': u'gpsFix'},'''
	if not recordlist:
		return(36.0,122.0,1573301462000)
	site =    (recordlist[0]['fix']['latitude'],recordlist[0]['fix']['longitude'])
	gpstime = recordlist[0]['unixTime']
	return site,gpstime
	
def parseCritical(recordlist):
	Drop = False
	ThrusterServo=False
	for Record in recordlist:
		# if DEBUG:
		# 	print Record["name"],Record["text"]
		if Record["name"]=="DropWeight":
			Drop=Record["unixTime"]
		if (not ThrusterServo) and Record["text"]=="ThrusterServo":
			ThrusterServo = Record["unixTime"]
	return Drop, ThrusterServo 
	

def getImportant(starttime):
	qString = runQuery(VEHICLE,"logImportant","&limit=2000",starttime)
	retstring = ""
	if qString:
		retstring = qString
	return retstring

def getComms(starttime):
	qString = runQuery(VEHICLE,"sbdReceive","",starttime)
	retstring = False
	if qString:
		retstring = qString
	if DEBUG:
		for rec in retstring:
			print rec
	return retstring

def parseComms(recordlist):
	satCommTime = False
	directCommTime = False
	for Record in recordlist:
		# Any event that starts with Received.
		if satCommTime == False and Record["eventType"]=="sbdReceive" and Record['state'] == 0:
			satCommTime=Record["unixTime"]
		if directCommTime == False and Record["eventType"]=="sbdReceive" and Record['eventType'] == 'sbdReceive' and Record['state'] == 2:
			directCommTime=Record["unixTime"]
		if directCommTime and satCommTime:
			break

		# Direct Comms event type for cell comms
	return satCommTime,directCommTime 

def getData(starttime):
	'''NOTE this walks through the whole file to get the right field. Not very slick'''
	''' IBIT will show battery thresholds that could be used to determine warning colors'''
	''' GREY OUT BATTERY VALUES - cache battery values to use if new log
	
	Entries from shore.asc use same deque "trick" to get values. get maybe 150 lines
	2020-03-04T20:58:38.153Z,1583355518.153 Unknown==>platform_battery_charge=126.440002 Ah
	2020-03-04T20:58:38.153Z,1583355518.153 Unknown==>platform_battery_voltage=14.332275 V
	
	'''
	
	volt="0"
	amp ="0"
	volttime="0"
	saveline="na,na,na"
	'''https://okeanids.mbari.org/TethysDash/data/pontus/realtime/sbdlogs/2020/202003/20200303T074113/shore.csv
	2020/202003/20200303T074113'''
	DataURL='https://okeanids.mbari.org/TethysDash/data/{vehicle}/realtime/sbdlogs/{extrapath}/shore.csv'
	
	record = runQuery(VEHICLE,"dataProcessed","&limit=1",starttime)
	extrapath = record[0]['path']
	NewURL = DataURL.format(vehicle=VEHICLE,extrapath=extrapath)
	datacon = urllib2.urlopen(NewURL,timeout=5)
	lastlines = deque(datacon, 10)
	for nextline in lastlines:
		if "V," in nextline:
			fields = nextline.split(",")
			volt     = float(fields[8].split(" ")[0])
			amp      = float(fields[7].split(" ")[0])
			volttime = int(float(fields[1])*1000)  # in seconds not MS
			break

	return volt,amp,volttime

def parseGF(gfstring):
	GFlist = []
	'''multi-line input, find max value after colon
	mA:
CHAN A0 (Batt): -0.002926
CHAN A1 (24V): -0.000568
CHAN A2 (12V): -0.002154
CHAN A3 (5V): -0.001574
CHAN B0 (3.3V): 0.000075
CHAN B1 (3.15aV): 4.767929
CHAN B2 (3.15bV): -0.000301
CHAN B3 (GND): -0.000056
OPEN: -0.000713
Full Scale Calc: 4.765 mA, -1.589 mA
'''
	for Line in gfstring.split("\n"):
		if Line.startswith("CHAN") and ":" in Line:
			GFlist.append(float(Line.split(":")[1]))
	return "%.2f" % max(GFlist)

'''
Commanded speed may not show up in Important if it is default for mission
Look between load and start for all these things -- needcomms, mission Timeout etc.

Reset to default if you get a mission event before commanded speed. 
If you see a Loaded mission command, or Started default before getting speed (or Need Comms [Default 60]....)

Ground fault: Queue on RED on Low side ground fault detected - Yellow on any ground fault
...
TODO: Get defaults for missions and store locally
git tag -  
   profile station
   sci2
	
	drop weight - 


'''

def parseMission(recordlist):
	MissionName=False
	MissionTime=False
	## PARSE MISSION NAME
	for Record in recordlist:
		if Record["name"]=="MissionManager":
			MissionName = Record["text"].split("mission ")[1]
			MissionTime = Record["unixTime"]
			break
	return MissionName,MissionTime


def parseImptMisc(recordlist):
	'''Loads events that persist across missions'''

	GF = False
	GFtime = False

	ubatStatus = "st3"
	ubatTime = False

	FlowRate = False
	FlowTime = False
	
	LogTime = False
	
	for Record in recordlist:
		if DEBUG:
			print Record["name"],"<-->",Record["text"]
			
		## PARSE GROUND FAULTS
		if GF == False and Record["name"]=="CBIT":
			if Record["text"].startswith("Ground fault detected") or Record["text"].startswith("Low side ground fault detected"):
				# print "\n####\n",Record["text"]
				GF = parseGF(Record["text"])
				GFtime = Record["unixTime"]
				
			elif Record["text"].startswith("No ground fault"):
				GF = "None"
				GFtime = Record["unixTime"]
				
		if not LogTime and Record["name"] =='CommandLine' and 'got command restart logs' in Record["text"]:
			LogTime = Record["unixTime"]
			
		## PARSE UBAT (make vehicle-specific)
		if ubatTime == False and Record["name"]=="CommandLine" and "00000" in Record["text"] and "WetLabsUBAT.loadAtStartup" in Record["text"]:
			ubatBool = bool(float(Record["text"].split("loadAtStartup ")[1].split(" ")[0]))
			ubatStatus = ["st6","st4"][ubatBool]
			ubatTime   = Record["unixTime"]
			
		if FlowRate == False and Record["name"]=="CommandLine" and Record["text"].startswith("WetLabsUBAT.flow_rate"):
			FlowRate = float(Record["text"].split("WetLabsUBAT.flow_rate ")[1].split(" ")[0])
			FlowTime   = Record["unixTime"]

	return GF, GFtime, ubatStatus, ubatTime, FlowRate,FlowTime, LogTime
	
def parseDefaults(recordlist,MissionName,MissionTime):
	''' parse events that get reset after missions and might be default'''
	''' todo, need to move the ubat here and change the ubat on command parsing'''
	mission_defaults = {
		"profile_station"  : {"MissionTimeout": 4,   "NeedCommsTime":60, "Speed":1 },
		"sci2"             : {"MissionTimeout": 2,   "NeedCommsTime":60, "Speed":1 },
		"keepstation"      : {"MissionTimeout": 4,   "NeedCommsTime":45, "Speed":.75 },
		"ballast_and_trim" : {"MissionTimeout": 1.5, "NeedCommsTime":45, "Speed":0.1 },
		"keepstation_3km"  : {"MissionTimeout": 4,   "NeedCommsTime":45, "Speed":.75 },
		"transit_3km"      : {"MissionTimeout": 1,   "NeedCommsTime":30, "Speed":1 },
		"spiral_cast"      : {"MissionTimeout": 3,   "NeedCommsTime":180, "Speed":1 }
	}
	
	TimeoutDuration=False
	TimeoutStart   =False
	NeedComms = False
	Speed = 0

	
	for Record in recordlist:
		## PARSE TIMEOUTS Assumes HOURS
		if TimeoutDuration == False and Record["name"]=="CommandLine" and ".MissionTimeout" in Record["text"] and Record["text"].startswith("got"):
			'''got command set profile_station.MissionTimeout 24.000000 hour'''
			TimeoutDuration = int(float(Record["text"].split("MissionTimeout ")[1].split(" ")[0]))
			TimeoutStart    = Record["unixTime"]
		
		## PARSE NEED COMMS Assumes MINUTES
		if NeedComms == False and Record["name"]=="CommandLine" and ".NeedCommsTime" in Record["text"]:
			'''command set keepstation.NeedCommsTime 60.000000 minute	'''
			NeedComms = int(float(Record["text"].split("NeedCommsTime ")[1].split(" ")[0]))
			
			## ADD FLOW RATE FOR UBAT...
			
			### For the moment this will just go from the start of the mission, but once we get SatComms, use that time
			
		## PARSE UBAT (make vehicle-specific)
		## PARSE SPEED
		if Speed == False and Record["name"]=="CommandLine" and ".Speed" in Record["text"]:
			Speed = "%.1f" % (float(Record["text"].split(".Speed")[1].strip().split(" ")[0]))
			
			# Speed = "%.1f" % (float(Record["text"].split(".Speed")[1].split(" ")[0]))
		
	if not Speed:
			Speed = mission_defaults.get(MissionName,{}).get("Speed","na")
	if not NeedComms:
			NeedComms = mission_defaults.get(MissionName,{}).get("NeedCommsTime",0)
	if not TimeoutDuration:
			TimeoutDuration = mission_defaults.get(MissionName,{}).get("MissionTimeout",0)
			TimeoutStart = MissionTime
	
			
	return TimeoutDuration, TimeoutStart, NeedComms,Speed 

	
def elapsed(rawdur):
	'''input in millis not seconds'''
	DurationBase = '{}{}{}'
	duration = abs(rawdur/1000)
	minutes = int(duration/60)
	hours = int(minutes/60)
	days = int(hours/24)
	MinuteString = minutes
	HourString = ""
	DayString  = ""
	if minutes>59:
		MinuteString = str(minutes%60) + "m"
		HourString = str(minutes//60) + "h " 
		hours = minutes//60
	if (hours)>23:
		HourString = str(hours%24) + "h "
		DayString = str(hours//24) + "d " 
	DurationString = DurationBase.format(DayString,HourString,MinuteString)
	if rawdur < 1:
		DurationString += " ago"
	else:
		DurationString = "in " + DurationString
	return DurationString

def distance(site,time,oldsite,oldtime):
	"""
	from https://stackoverflow.com/a/38187562/1681480
	----------
	origin and destination:  tuple of (lat, long)
	distance_in_km : float

	"""
	lat1, lon1 = site
	lat2, lon2 = oldsite
	deltat = time - oldtime
	seconds = deltat / 1000.0
	hours = seconds / (60*60)
	
	radius = 6371  # km

	dlat = math.radians(lat2 - lat1)
	dlon = math.radians(lon2 - lon1)
	a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
		math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
		math.sin(dlon / 2) * math.sin(dlon / 2))
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	d = radius * c
	speed = d / hours
	return d,hours,speed

########################################################################
##
##
##    End function definitions
##
########################################################################

Opt = get_options()
global DEBUG
DEBUG = Opt.DEBUG
global VEHICLE
VEHICLE = Opt.vehicle

if Opt.missions:
	getMissionDefaults()
	sys.exit("Done")
	
# TODO: If running on tethys, use '/var/www/html/widget/auv_{}.svg' as the outpath
if 'tethysdash' in os.uname()[1]:
	OutPath       = '/var/www/html/widget/auv_{}.svg'
	StartTimePath = '/var/www/html/widget/auvstats_{}.csv'
elif 'jellywatch' in os.uname():
	OutPath       = '/home/jellywatch/jellywatch.org/misc/auv_{}.svg'
	StartTimePath = '/home/jellywatch/jellywatch.org/misc/auvstats_{}.csv'
else:
	OutPath = './auv_{}.svg'
	StartTimePath = "./auvstats_{}.csv" # make this .py for importing or .json?
	
	
	
#########
##
## LOAD AND PARSE EVENTS
##
now = 1000 * time.mktime(time.localtime())  # (*1000?)

startTime = getDeployment()

recovered = getRecovery(starttime=startTime)

plugged = getPlugged(recovered)
	
critical  = getCritical(startTime)

site,gpstime = parseGPS(getGPS(startTime))

oldsite,oldgpstime = parseGPS(getOldGPS(gpstime,startTime))

deltadist,deltat,speedmadegood = distance(site,gpstime,oldsite,oldgpstime)

# FULL RANGE OF RECORDS
important = getImportant(startTime)

missionName,missionTime = parseMission(important)
gf,gftime,ubatStatus,ubatTime,flowrate,flowtime,logtime  = parseImptMisc(important)

if not logtime:
	logtime = startTime
	
# ONLY RECORDS AFTER MISSION
postmission = getImportant(missionTime)
duration,timeoutstart,needcomms,speed  = parseDefaults(postmission,missionName,missionTime)

#this is volt, amp, time
volt,amphr,batttime = getData(startTime)
satcomms,cellcomms = parseComms(getComms(startTime))

if not needcomms: 
	needcomms = 60  #default
	
	
if (critical):
	dropWeight,ThrusterServo= parseCritical(critical)


if Opt.report:
	print "Now: " ,hours(now)
	print "GroundFault: ",gf,hours(gftime)
	print "Duration:    ",duration
	print "TimeoutStart:",hours(timeoutstart)
	print "NeedComms:",needcomms
	print "SatComms:",satcomms
	print "CellComms:",cellcomms
	ago_log = logtime - now
	print "LogRestart",hours(logtime), elapsed(ago_log), logtime
	print "UBAT: ", ubatStatus, hours(ubatTime)
	print "FLOW: ",flowrate, hours(flowtime)
	print "Mission: ",missionName,hours(missionTime)
	print "SPEED: ",speed  
	print "GPS",site
	print "GPSTIme",hours(gpstime)
	print "OLDGPS",oldsite
	print "OLDGPSTIme",hours(oldgpstime)
	  # last two points: [0] is most recent
	print "Distance:",deltadist,deltat,speedmadegood
	print "Battery: ",volt, amphr, batttime
	print "DropWeight:",dropWeight
	print "Thruster:  ",ThrusterServo
	print "Deployed:  ", hours(startTime), elapsed(startTime - now)
	if recovered:
		print "Recovered: ",hours(recovered), elapsed(recovered - now), recovered
		if plugged:
			print "Plugged in: ",hours(plugged)
	else:
		print "Still out there..."

# print svgtext  # from importing
'''	
	.st0{fill:#CFDEE2;} <!-- WaveColor -->
	.st1{fill:none;stroke:#000000; }
	.st2{fill:#D4D2D2;stroke:#000000; } <!-- Background wave -->
	.st3{fill:#FFFFFF;stroke:#000000; } <!--White Fill -->
	.st4{fill:#5AC1A4;stroke:#000000; } <!--Green Fill -->
	.st5{fill:#FFE850;stroke:#000000; } <!--Yellow Fill -->
	.st6{fill:#EF9D30;stroke:#000000; } <!--Orange Fill -->
	.st7{fill:#FFFFFF;stroke:#000000;stroke-linecap:round; }
	.st8{fill:#C6C4C4;stroke:#000000;stroke-linecap:round; }
	.st9{font-family:'HelveticaNeue';}
	.st10{font-size:9px;}
	.st11{fill:#6D6E6E;stroke:#000000; } <!-- DarkGray Fill-->
	.st12{fill:#606060;}  <!--MidGray text -->
	.st13{font-size:7px;}
	.st14{font-family:'HelveticaNeue-Medium';}
	.st15{font-size:11px;}
	.st16{fill:#929090;} <!-- Arrow gray-->
	.st17{fill:#e3cfa7;} <!-- DirtBrown-->
	.st18{fill:none;stroke:none; } <!--invisible-->
	.st19{fill:#555555;stroke:#000000;stroke-miterlimit:10;}  <!-- Cart color -->
	.st20{fill:#e3cfa7;stroke:#000000;stroke-miterlimit:10;}  <!-- Circle color -->
	.st21{fill:none;stroke:#46A247;stroke-width:4;stroke-miterlimit:10;} <!-- small cable color -->
	.st22{fill:none;stroke:#555555;stroke-width:9;stroke-linecap:round;stroke-miterlimit:10;} <!-- big cablecolor -->
	.st23{fill:none;stroke:#46A247;stroke-width:4;stroke-miterlimit:10;} <!-- small cable color2 -->
	
	'''
cdd={}
colornames=[
"color_drop",
"color_thrust",
"color_bat1",
"color_bat2",
"color_bat3",
"color_bat4",
"color_bat5",
"color_bat6",
"color_bat7",
# "color_bat8",
"color_satcomm",
"color_cell",
"color_gps",
"color_amps",
"color_volts",
"color_gf",
"color_sonar",
"color_bt2",
"color_bt1",
"color_ubat",
"color_flow",
"color_wavecolor",
"color_dirtbox",
"color_bigcable",
"color_smallcable",
"color_cart",
"color_cartcircle"]

for cname in colornames:
	cdd[cname]='st3'

cartcolors=["color_bigcable",
"color_smallcable",
"color_cart",
"color_cartcircle"]

for cname in cartcolors:
	cdd[cname]='st18'

textnames=[
"text_mission",
"text_cell",
"text_sat",
"text_gps",
"text_speed",
"text_nextcomm",
"text_timeout",
"text_amps",
"text_volts",
"text_droptime",
"text_gftime",
"text_gf",
"text_thrusttime",
"text_vehicle",
"text_commago",
"text_ampago",
"text_cellago",
"text_flowago",
"text_logago",
"text_logtime",
"text_lastupdate"]

for tname in textnames:
	cdd[tname]='na'

'''
 _            _       
| |_ ___   __| | ___  
| __/ _ \ / _` |/ _ \ 
| || (_) | (_| | (_) |
 \__\___/ \__,_|\___/ 

 transparent for vehicle-specific features
 TODO: Check thruster color to make sure it detects a fault
 Change GPS calculation to look over a longer time scale
 add more time ago fields
 GO HOME
 
 '''
commreftime = max(cellcomms,satcomms)

now = time.time() * 1000  # localtime in unix
gfnum=int(4+ 1*(float(gf)>0.2) + 1*(float(gf)>0.6))

###
###   GROUND FAULT DISPLAY
###

cdd["color_gf"]= "st{}".format(gfnum)
cdd["text_gf"] = gf
ago_gftime = gftime - now 
cdd["text_gftime"] = elapsed(ago_gftime)

###
###   MISSION TIMEOUTS DISPLAY
###

# This in in hours
# cdd["text_timeout"] = hours(timeoutstart+duration*3600*1000)
cdd["text_timeout"] = hours(timeoutstart+duration*3600*1000) + " - " + elapsed((missionTime+duration*3600*1000) - now )

#Change this to use sat comms time
# This is typically in minutes

# cdd["text_nextcomm"] = hours(timeoutstart+needcomms*60*1000)
cdd["text_nextcomm"] = hours(commreftime+needcomms*60*1000) + " - " + elapsed((commreftime+needcomms*60*1000) - now)

###
###   UBAT FLOW DISPLAY
###
if VEHICLE == 'pontus':
	if flowrate:
		if (.25 < flowrate <.45):
			cdd["color_flow"]= 'st4'
		else:
			cdd["color_flow"]= 'st6'

	if flowtime:
		cdd["text_flowago"] = elapsed(flowtime-now)
	else:
		cdd["text_flowago"]=""

	cdd["color_ubat"] = ubatStatus
else:
	cdd["color_ubat"] = 'st3'
	cdd["color_flow"] = 'st3'
	
# ubatTime TO ADD?

###
###   MISSION OVERVIEW DISPLAY
###

cdd["text_mission"]=missionName + " - " + hours(missionTime)
cdd["text_speed"]= speed + "m/s"

###
###   GPS DISPLAY
###

cdd["text_gps"] = hours(gpstime)
cdd["color_gps"] = ['st4','st5'][(now - gpstime > 3600000)]
cdd["text_thrusttime"] = "%.1f" % speedmadegood + "km/hr"

###
###   SAT COMM DISPLAY
###
ago_satcomms = satcomms - now 
cdd["text_commago"] = elapsed(ago_satcomms)
cdd["text_sat"] = hours(satcomms)

ago_log = logtime - now
cdd["text_logago"] = elapsed(ago_log)
cdd["text_logtime"] = hours(logtime)

# more than 13 minutes (underwater) = yellow. Beyond needcomms time by 20 mins: orange
satnum=int(4 + 1*(abs(ago_satcomms) > (13*60*1000)) + 1*(abs(ago_satcomms) > ((needcomms+20)*60*1000)) )
cdd["color_satcomm"] = "st{}".format(satnum)

###
###   CELL COMM DISPLAY
###

ago_cellcomms = cellcomms - now 
cdd["text_cellago"] = elapsed(ago_cellcomms)
cdd["text_cell"] = hours(cellcomms)

cellnum=int(4 + 1*(abs(ago_cellcomms) > (10*60*1000)) + 1*(abs(ago_cellcomms) > ((needcomms+45)*60*1000)) )
cdd["color_cell"] = "st{}".format(cellnum)


###
###   CELL COMM DISPLAY
###



if recovered:
	for cname in colornames:
		cdd[cname]='st18'
	for tname in textnames:
		cdd[tname]=''
	
	cdd["color_wavecolor"] = 'st18' # invisible
	cdd["color_dirtbox"] = 'st17'   # brown
	if plugged:
		cdd["text_mission"]     = "PLUGGED IN at " + hours(plugged)
		cdd["color_cart"]       = 'st19'
		cdd["color_cartcircle"] = 'st20'
		cdd["color_smallcable"] = 'st23'
		cdd["color_bigcable"]   = 'st22'
		
	else:
		cdd["text_mission"] = "RECOVERED at " + hours(recovered)
		
	
	
else:
	
	### BATTERY INFO
	
	cdd["color_wavecolor"] = 'st0'
	cdd["color_dirtbox"] = 'st18'
	
	if batttime:
		cdd["text_ampago"] = elapsed(batttime-now)
	else:
		cdd["text_flowago"]="Default"
	

	cdd["text_volts"]= "%.1f" % volt
	cdd["text_amps"]= "%.1f" % amphr 
	
	voltnum=int(4 + 1*(volt<15) + 1*(volt<14))
	cdd["color_amps"]  = "st{}".format(voltnum)  # change this to independent amp range
	cdd["color_volts"] = "st{}".format(voltnum)

	cdd["color_bat1"] = ['st4','st6'][volt <= 13.5]
	cdd["color_bat2"] = ['st4','st6'][volt < 14.0]
	cdd["color_bat3"] = ['st4','st6'][volt < 14.5]
	cdd["color_bat4"] = ['st4','st6'][volt < 15.0]
	cdd["color_bat5"] = ['st4','st6'][volt < 15.5]
	cdd["color_bat6"] = ['st4','st6'][volt < 16.0]
	cdd["color_bat7"] = ['st4','st6'][volt < 16.5]
	# cdd["color_bat8"] = ['st4','st6'][volt < 16.5]


	cdd["color_thrust"] = ['st4','st6'][(ThrusterServo>100)]

	cdd["color_drop"] = ['st4','st6'][(dropWeight>1)]
	if dropWeight > 100:
		cdd["text_droptime"] = hours(dropWeight)
	else:
		cdd["text_droptime"] =""
cdd["text_vehicle"] = VEHICLE.upper()
cdd["text_lastupdate"] = time.strftime('%H:%M')

# print "Launched:  ", hours(startTime)  
# if recovered:
# 	print "Recovered: ",hours(recovered)
if Opt.savefile:
	with open(OutPath.format(VEHICLE),'w') as outfile:
		outfile.write(svghead)
		outfile.write(svgtext.format(**cdd))
		if VEHICLE=="pontus":
			outfile.write(svgpontus)
		outfile.write(svgtail)
		
		
elif not Opt.report:
	print svghead
	print svgtext.format(**cdd)
	if VEHICLE=="pontus":
		print svgpontus
	print svgtail
	
	
# svgDictionary = dict(x.items() + y.items())
