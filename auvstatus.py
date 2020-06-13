#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
	Version 1.3 - Streamlined code so it doesn't download data for recovered vehicles
	Version 1.2 - making UBAT pontus-specific (move to svg["pontus"] for more vehicles)
	Version 1.1 - adding cart
	Version 1.0 - works for pontus
	
	Usage: auvstatus.py -v pontus -r  (see a summary of reports)
	       auvstatus.py -v pontus > pontusfile.svg  (save svg display)
			 
	https://okeanids.mbari.org/TethysDash/api/events?vehicles=pontus&eventTypes=logImportant&limit=4
	

	Battery thresholds:
	onfigSet IBIT.batteryVoltageThreshold 13 v persist;configSet IBIT.batteryCapacityThreshold 15 Ah persist
	
		  
	Ground faults - check with Erik about what is most useful for GF reporting
	
	  
	  '''

import argparse
import sys
import time
import os
import urllib2
import json
import math
from collections import deque
from LRAUV_svg import svgtext,svghead,svgpontus,svgbadbattery,svgtail,svglabels,svgerror,svgerrorhead   # define the svg text?

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Default timeouts for selected missions

def get_options():
	parser = argparse.ArgumentParser(usage = __doc__) 
#	parser.add_argument('infile', type = argparse.FileType('rU'), nargs='?',default = sys.stdin, help="output of vars_retrieve")
	parser.add_argument("-b", "--DEBUG",	action="store_true", help="Print debug info")
	parser.add_argument("-r", "--report",	action="store_true", help="print results")
	parser.add_argument("-f", "--savefile",	action="store_true", help="save to SVG named by vehicle at default location")
	parser.add_argument("-v", "--vehicle",	default="pontus"  , help="specify vehicle")
	parser.add_argument("--printhtml",action="store_true"  , help="print auv.html web links")
	parser.add_argument("-m", "--missions",action="store_true"  , help="spit out mission defaults")
	parser.add_argument("Args", nargs='*')
	options = parser.parse_args()
	return options


def runQuery(event="",limit="",name="",timeafter="1234567890123"):
	if limit:
		limit = "&limit=" + limit
	if name:
		name = "&name=" + name
	if event:
		event = "&eventTypes=" + event
		
	'''send a generic query to the REST API. Extra parameters can be over packed into limit (2)'''
	
	vehicle = VEHICLE

	if not timeafter:
		timeafter="1234567890123"
		
	BaseQuery = "https://okeanids.mbari.org/TethysDash/api/events?vehicles={v}{e}{n}{l}&from={t}"
	URL = BaseQuery.format(v=vehicle,e=event,n=name,l=limit,t=timeafter)
	
	if DEBUG:
		print "### QUERY:",URL

	try:
		connection = urllib2.urlopen(URL,timeout=5)		
		if connection:
			raw = connection.read()
			structured = json.loads(raw)
			connection.close()
			result = structured['result']
		else:
			print >> sys.stderr, "# Query timeout",URL
			result = ''
		return result
	except urllib2.HTTPError:
		print >> sys.stderr, "# FAILURE IN QUERY:",URL
		handleURLerror()

	
def getDeployment():
	'''return start time for deployment'''
	startTime = 0
	launchString = runQuery(event="launch",limit="1")
	if launchString:
		startTime = launchString[0]['unixTime']
	return startTime
	
def getRecovery(starttime):
	launchString = runQuery(event="recover",limit="1",timeafter=starttime)
	recover = False
	if launchString:
		recover = launchString[0]['unixTime']
	
	return recover

def getPlugged(starttime):
	launchString = runQuery(event="deploy",limit="1",timeafter=starttime)
	plugged = False
	if launchString:
		plugged = launchString[0]['unixTime']
	
	return plugged
 
def getGPS(starttime):
	''' extract the most recent GPS entry'''
	qString = runQuery(event="gpsFix",limit="1",timeafter=starttime)
	retstring=""
	if qString:
		retstring = qString	
	return retstring
	
def getOldGPS(gpstime,missionstart):
	'''using the date of the most recent entry [mission start], go back 30 minutes and get GPS fix'''
	
	previoustime = gpstime - 30*60*1000
	qString = runQuery(event="gpsFix",limit="1&to={}".format(previoustime),timeafter=missionstart)
	retstring=""
	if qString:
		retstring = qString
	return retstring

def getMissionDefaults():
	'''print standard defaults for the listed missions. some must have inheritance because it doesn't get them all'''
	missions=["Science/profile_station","Science/sci2","Science/mbts_sci2","Transport/keepstation","Maintenance/ballast_and_trim","Transport/keepstation_3km","Transport/transit_3km","Science/spiral_cast"]
	missions=["Science/mbts_sci2","Science/profile_station"]
	for mission in missions:
		URL = "https://okeanids.mbari.org/TethysDash/api/git/mission/{}.xml".format(mission)
		print "\n#===========================\n",mission, "\n"
		try:
			connection = urllib2.urlopen(URL,timeout=5)
			if connection: # here?
				raw = connection.read()
				structured = json.loads(raw)
				connection.close()
				result = structured['result']
			
				print URL
				try: 
					splitted = str(result).split("{")
					for item in splitted:
						print item
				except KeyError:
					print "NA"
		except urllib2.HTTPError:
			print >> sys.stderr, "# FAILED TO FIND MISSION",mission
			

	
def getNotes(starttime):
	'''get notes with #widget in the text'''
	qString = runQuery(event="note",limit="10",timeafter=starttime)
	retstring = ''
	if qString:
		retstring=qString

	return retstring
	
def getCritical(starttime):
	'''get critical entries, like drop weight'''
	qString = runQuery(event="logCritical",limit="2000",timeafter=starttime)
	retstring = ""
	if qString:
		retstring = qString
	
	return retstring
	
def getFaults(starttime):
	'''
	Software Overcurrent Add swatch to thruster section? 
	Hardware Overcurrent 
	On overcurrent errors, the component varies. Probably worth having a special indicator and report what is flagged
		LCB Fault
		
		2020-03-06T00:10:13.771Z,1583453413.771 [CBIT](CRITICAL): Communications Fault in component: RDI_Pathfinder
		
	2020-03-06T00:09:26.051Z,1583453366.051 [RDI_Pathfinder](FAULT): DVL failed to acquire valid data within timeout.'''
	qString = runQuery(event="logFault",limit="2000",timeafter=starttime)
	retstring = ""
	if qString:
		retstring = qString	
	return retstring

def getImportant(starttime):
	qString = runQuery(event="logImportant",limit="1000",timeafter=starttime)
	retstring = ""
	if qString:
		retstring = qString
	return retstring

def getCBIT(starttime):
	'''may also hold some DVL info'''
	qString = runQuery(name="CBIT",timeafter=starttime)
	retstring = ""
	if qString:
		retstring = qString
	return retstring

def getDrop(starttime):
	qString = runQuery(name="DropWeight",timeafter=starttime)
	retstring = ""
	if qString:
		retstring = qString
	return retstring

	
def getComms(starttime):
	qString = runQuery(event="sbdReceive",timeafter=starttime)
	retstring = ""
	if qString:
		retstring = qString
#	if DEBUG:
#		for rec in retstring:
#			print rec
	return retstring

def getDataAsc(starttime):
	''' TODO: cache batteries for when there is a new log file
	OR if you don't find it, rerun the Query with limit 2 and parse the second file

	
	Entries from shore.asc use same deque "trick" to get values. get maybe 150 lines
	2020-03-04T20:58:38.153Z,1583355518.153 Unknown==>platform_battery_charge=126.440002 Ah
	2020-03-04T20:58:38.153Z,1583355518.153 Unknown==>platform_battery_voltage=14.332275 V
	Split on '='
	
	['2020-03-03T09:17:56.203Z,1583227076.203 Unknown', '', '>platform_battery_charge', '153.968887 Ah']
	
	'''
	
	'''https://okeanids.mbari.org/TethysDash/data/pontus/realtime/sbdlogs/2020/202003/20200303T074113/shore.csv
	2020/202003/20200303T074113
	
	look for platform_battery_charge or platform_battery_voltage
	
'''

	Bailout=False
	DataURL='https://okeanids.mbari.org/TethysDash/data/{vehicle}/realtime/sbdlogs/{extrapath}/shore.asc'
	
	record = runQuery(event="dataProcessed",limit="2",timeafter=starttime)
	for pathpart in record:
		volt=0
		amp =0
		volttime=0
		
		extrapath = pathpart['path']
		NewURL = DataURL.format(vehicle=VEHICLE,extrapath=extrapath)
		datacon = urllib2.urlopen(NewURL,timeout=5)
		# pull last X lines from queue. This was causing problems on some missions so increased it
		lastlines = deque(datacon, 1500)
		for nextline in lastlines:
			# if DEBUG:
			# 	print >> sys.stderr, "#Battery nextline:",nextline.rstrip()
			if "platform_battery_" in nextline:
				fields = nextline.split("=")
				if (volt==0) and "voltage" in nextline:
					volt     = float(fields[3].split(" ")[0])
					volttime = int(float(fields[0].split(',')[1].split(" ")[0])*1000)  # in seconds not MS
				elif "charge" in nextline:
					amp      = float(fields[3].split(" ")[0])
			if (volt) and (amp):
				Bailout = True
				break
		if Bailout == True:
			break
	return volt,amp,volttime

def getData(starttime):
	'''NOT USED? see getDataAsc'''
	'''Walk through the file backwards'''
	''' IBIT will show battery thresholds that could be used to determine warning colors'''
	''' GREY OUT BATTERY VALUES - cache battery values to use if new log
	'''
	volt="0"
	amp ="0"
	volttime="0"
	saveline="na,na,na"
	'''https://okeanids.mbari.org/TethysDash/data/pontus/realtime/sbdlogs/2020/202003/20200303T074113/shore.csv
	2020/202003/20200303T074113'''
	DataURL='https://okeanids.mbari.org/TethysDash/data/{vehicle}/realtime/sbdlogs/{extrapath}/shore.csv'
	
	record = runQuery(event="dataProcessed",limit="1",timeafter=starttime)
	extrapath = record[0]['path']
	NewURL = DataURL.format(vehicle=VEHICLE,extrapath=extrapath)
	datacon = urllib2.urlopen(NewURL,timeout=5)
	if DEBUG:
		print >> sys.stderr, "# Data URL",NewURL
	lastlines = deque(datacon, 10)
	for nextline in lastlines:
		if "V," in nextline:
			try:
				fields = nextline.split(",")
				volt     = float(fields[8].split(" ")[0])
				amp      = float(fields[7].split(" ")[0])
				volttime = int(float(fields[1])*1000)  # in seconds not MS
			except IndexError:
				print >> sys.stderr, "VOLT parsing error"
				volt=False
				amp=False
				volttime=False
			break

	return volt,amp,volttime
	
def parseGPS(recordlist):
	# print "GPS record", recordlist
	site=False
	gpstime=False
	'''[{u'eventId': 12283560, u'unixTime': 1583301462000, u'vehicleName': u'pontus', u'fix': {u'latitude': 36.757467833070464, u'date': u'Wed Mar 04 05:57:42 GMT 2020', u'longitude': -122.02584799923866}, u'eventType': u'gpsFix'},'''
	if not recordlist:
		return((False,False),False)
	site =    (recordlist[0]['fix']['latitude'],recordlist[0]['fix']['longitude'])
	gpstime = recordlist[0]['unixTime']
	return site,gpstime

def parseNotes(recordlist):
	Note = ''
	NoteTime = False
	for Record in recordlist:
		# if DEBUG:
		# 	print Record["name"],Record["text"]
		if "#widget" in Record["note"]:
			Note = "NOTE " + Record["note"].replace("#widget","")[:120]
			NoteTime = Record["unixTime"]
			break
	return Note,NoteTime 
	
def parseDrop(recordlist):
	Drop          = False
	for Record in recordlist:
		# Expand this to check other DropWeight associated messages?
		if Record["name"]=="DropWeight":
			Drop=Record["unixTime"]
	return Drop
	 
def parseCritical(recordlist):
	'''Maybe some of these are in logFault?'''
	Drop          = False
	ThrusterServo = False

	
	# if DEBUG:
	# 	print "### Start Recordlist"
	# 	print recordlist
	# 	print "### End Recordlist"
	# 	# need to split this record?
	
	for Record in recordlist:
		if DEBUG:
			print >> sys.stderr, "# CRITICAL NAME:",Record["name"],"===> ", Record["text"]
		if Record["name"]=="DropWeight":
			Drop=Record["unixTime"]
		if (not ThrusterServo) and Record.get("text","NA")=="ThrusterServo":
			ThrusterServo = Record["unixTime"]
		# if Record["name"]=="CBIT" and Record.get("text","NA").startswith("LAST"):
	return Drop, ThrusterServo

def parseFaults(recordlist):
	'''https://okeanids.mbari.org/TethysDash/api/events?vehicles=brizo&eventTypes=logFault&from=1591731032512
	
	Also includes RudderServo and DVL_Micro, RDI_Pathfinder'''
	BadBattery    = False
	DVLError = False
	
	# if DEBUG:
	# 	print "### Start Recordlist"
	# 	print recordlist
	# 	print "### End Recordlist"
	# 	# need to split this record?
	for Record in recordlist:
		if DEBUG:
			print "NAME:",Record["name"],"===> ", Record["text"]
		if Record["name"]=="BPC1" and Record.get("text","NA").startswith("Battery stick"):
			BadBattery=Record["unixTime"]
			if DEBUG:
				print >> sys.stderr,"\n\n## BAD BATTERY in FAULT\n\n"
		# THIS ONE needs to take only the most recent DVL entry, in case it was off and now on. See other examples.

		# if not DVLError and Record["name"] in ["DVL_Micro", "RDI_Pathfinder"] and "failed" in Record.get("text","NA").lower():
		# 	DVLError=Record["unixTime"]
	return BadBattery,DVLError

def parseDVL(recordlist):
	'''2020-03-06T00:30:17.769Z,1583454617.769 [CBIT](CRITICAL): Communications Fault in component: RDI_Pathfinder
	
	DVL potential instruments: 
		DVL_micro
		Rowe_600
		RDI_Pathfinder

	'''
	## All boilerplate DON'T USE!!
	Drop = False
	ThrusterServo=False
	for Record in recordlist:
		# if DEBUG:
		# 	print Record["name"],Record["text"]
		if Record["name"]=="DropWeight":
			Drop=Record["unixTime"]
		if (not ThrusterServo) and Record.get("text","NA")=="ThrusterServo":
			ThrusterServo = Record["unixTime"]
	return Drop, ThrusterServo 

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
	


def parseMission(recordlist):
	MissionName=False
	MissionTime=False
	## PARSE MISSION NAME
	for Record in recordlist:
		if Record["name"]=="MissionManager":
			if DEBUG:
				print >> sys.stderr,"## MISSION RECORD",Record
			MissionName = Record.get("text","mission NA").split("mission ")[1]
			MissionTime = Record["unixTime"]
			break
	return MissionName,MissionTime

def parseCBIT(recordlist):
	'''Use special query for CBIT and GF'''
	GF = False
	GFtime = False
	DVL=False
	
	'''DVL stuff  Rowe_600.loadAtStartup=1 bool
	old pontus/tethys command:
	configSet Rowe_600.loadAtStartup 0 bool persist;restart app
	"Communications Fault in component: RDI_Pathfinder"
	name column is RDI_Pathfinder for tethys: DVL failed to acquire valid data within timeout."
	
	'''
	if recordlist:
		for Record in recordlist:
			if DEBUG: 
				print >> sys.stderr, "# GF RECORD",Record
			if GF == False:
				if Record.get("text","NA").startswith("Ground fault detected") or Record.get("text","NA").startswith("Low side ground fault detected"):
					# print "\n####\n",Record["text"]
					GF = parseGF(Record.get("text","NA"))
					GFtime = Record["unixTime"]
			
				elif Record.get("text","NA").startswith("No ground fault"):
					GF = "OK"
					GFtime = Record["unixTime"]
			if DVL == False:
				if Record.get("text","NA").startswith("Communications Fault in component: RDI_Pathfinder"):
					if DEBUG:
						print >> sys.stderr, "DVL COMM ERROR"
					#need to find turned off commands.
	else:
		GF = "NA"
	return GF, GFtime		
	
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
	M=[(abs(n), (n>0)-(n<0)) for n in GFlist]
	chosen = max(M) 
	return "%.2f" % (chosen[0]*chosen[1])

'''
Commanded speed may not show up in Important if it is default for mission
Look between load and start for all these things -- needcomms, mission Timeout etc.

Reset to default if you get a mission event before commanded speed. 
If you see a Loaded mission command, or Started default before getting speed (or Need Comms [Default 60]....)

Ground fault: Queue on RED on Low side ground fault detected - Yellow on any ground fault
...


'''
def parseImptMisc(recordlist):
	'''Loads events that persist across missions'''
   #FORMER HOME OF GF SCANS
	ubatStatus = "st3"
	ubatTime = False

	FlowRate = False
	FlowTime = False
	
	LogTime = False
	
	for Record in recordlist:
		#if DEBUG:
		#	print Record["name"],"<-->",Record.get("text","NO TEXT FIELD")
				
		if not LogTime and Record["name"] =='CommandLine' and 'got command restart logs' in Record.get("text","NA"):
			LogTime = Record["unixTime"]

		## TODO distinguish between UBAT off and FlowRate too low
		## PARSE UBAT (make vehicle-specific)
				
		'''Change to got command ubat on'''
		if VEHICLE == "pontus" and ubatTime == False and Record["name"]=="CommandLine" and "00000" in Record.get("text","NA") and "WetLabsUBAT.loadAtStartup" in Record.get("text","NA"):
			ubatBool = bool(float(Record["text"].split("loadAtStartup ")[1].split(" ")[0]))
			ubatStatus = ["st6","st4"][ubatBool]
			ubatTime   = Record["unixTime"]
			
		if VEHICLE == "pontus" and FlowRate == False and Record["name"]=="CommandLine" and Record.get("text","NA").startswith("WetLabsUBAT.flow_rate"):
			FlowRate = float(Record["text"].split("WetLabsUBAT.flow_rate ")[1].split(" ")[0])
			FlowTime   = Record["unixTime"]

	return ubatStatus, ubatTime, FlowRate,FlowTime, LogTime

def parseDefaults(recordlist,mission_defaults,MissionName,MissionTime):
	''' parse events that get reset after missions and might be default'''
	''' todo, need to move the ubat here and change the ubat on command parsing'''
	
	TimeoutDuration=False
	TimeoutStart   =False
	NeedComms = False
	Speed = 0
	if DEBUG:
		print >>sys.stderr, "## Parsing defaults"
	for Record in recordlist:
		if DEBUG:
			print >> sys.stderr, "DEFAULTNAME: ", Record["name"] ,"===>",Record["text"]
		## PARSE TIMEOUTS Assumes HOURS
		if TimeoutDuration == False and Record["name"]=="CommandLine" and ".MissionTimeout" in Record.get("text","NA") and Record.get("text","NA").startswith("got"):
			'''got command set profile_station.MissionTimeout 24.000000 hour'''
			TimeoutDuration = int(float(Record["text"].split("MissionTimeout ")[1].split(" ")[0]))
			TimeoutStart    = Record["unixTime"]
		
		## PARSE NEED COMMS Assumes MINUTES
		if NeedComms == False and Record["name"]=="CommandLine" and Record.get("text","NA").startswith("got command") and ".NeedCommsTime" in Record.get("text","NA"):
			'''    command set keepstation.NeedCommsTime 60.000000 minute	'''
			'''got command set profile_station.NeedCommsTime 20.000000 minute'''
			NeedComms = int(float(Record["text"].split("NeedCommsTime ")[1].split(" ")[0]))
			if DEBUG:
				print >> sys.stderr, "#FOUND NEEDCOMMS",NeedComms
			## ADD FLOW RATE FOR UBAT...
			
			### For the moment this will just go from the start of the mission, but once we get SatComms, use that time
			
		## PARSE UBAT (make vehicle-specific)
		## PARSE SPEED # THis used to be ".Speed"
		if Speed == False and Record["name"]=="CommandLine" and ".speedCmd" in Record.get("text","NA") and Record.get("text","NA").startswith("got"):
			Speed = "%.1f" % (float(Record["text"].split(".speedCmd")[1].strip().split(" ")[0]))
			
			# Speed = "%.1f" % (float(Record["text"].split(".Speed")[1].split(" ")[0]))
		
	if not Speed:
			Speed = mission_defaults.get(MissionName,{}).get("Speed","na")
	if not NeedComms:
			NeedComms = mission_defaults.get(MissionName,{}).get("NeedCommsTime",0)
	if not TimeoutDuration:
			TimeoutDuration = mission_defaults.get(MissionName,{}).get("MissionTimeout",0)
			TimeoutStart = MissionTime
	
			
	return TimeoutDuration, TimeoutStart, NeedComms,Speed 

def handleURLerror():
	now = 1000 * time.mktime(time.localtime())
	timestring = dates(now) + " - " +hours(now)
	if Opt.savefile:
		with open(OutPath.format(VEHICLE),'w') as outfile:
			outfile.write(svgerrorhead)
			outfile.write(svgerror.format(text_vehicle=VEHICLE,text_lastupdate=timestring))		
		print >> sys.stderr ("URL ACCESS ERROR:"+VEHICLE)
		
	elif not Opt.report:
		print svgerrorhead
		print svgerror.format(text_vehicle=VEHICLE,text_lastupdate=timestring)
		sys.exit("URL ACCESS ERROR:"+VEHICLE)
	

def printhtmlutility():
	''' Print the html for the auv.html web page'''
	
	vehicles = ["daphne","pontus","tethys","galene","sim","triton","makai"]

	for v in vehicles:
		print '''var myImageElement1 = document.getElementById('{0}');
myImageElement1.src = 'https://okeanids.mbari.org/widget/auv_{0}.svg';'''.format(v)

	for v in vehicles:
		print '''<img src="https://okeanids.mbari.org/widget/auv_{0}.svg" id="{0}" width="100%"/>'''.format(v)
	
	
def elapsed(rawdur):
	'''input in millis not seconds'''
	if rawdur:
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
		else:
			MinuteString = str(minutes) + "m"
		if (hours)>23:
			HourString = str(hours%24) + "h "
			DayString = str(hours//24) + "d " 
		DurationString = DurationBase.format(DayString,HourString,MinuteString)
		if days > 30:
			DurationString = "long time"
		if rawdur < 1:
			DurationString += " ago"
		else:
			DurationString = "in " + DurationString
		return DurationString
	else:
		return "NA"

def distance(site,time,oldsite,oldtime):
	"""
	from https://stackoverflow.com/a/38187562/1681480
	----------
	origin and destination:  tuple of (lat, long)
	distance_in_km : float
	Bearing from https://www.igismap.com/what-is-bearing-angle-and-calculate-between-two-points/
	"""
	lat1, lon1 = oldsite
	lat2, lon2 = site
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
	# BEARING: 
	Y = math.sin(dlon) *  math.cos(math.radians(lat2))	
	X = math.cos(math.radians(lat1))*math.sin(math.radians(lat2)) - math.sin(math.radians(lat1))*math.cos(math.radians(lat2))*math.cos(dlon)
	Bearing = -1* int(math.degrees(math.atan2(X,Y)) - 90 ) % 360
	return d,hours,speed,Bearing
	


def hours(unixtime):
	'''return epoch in HH:MM string'''
	if unixtime:
		t1=time.localtime(unixtime/1000)
		TimeString = time.strftime('%H:%M',t1)
		return TimeString
	else:
		return "99:99"
		
def dates(unixtime):
	'''return epoch in DDmonYY string'''
	if unixtime:
		t1=time.localtime(unixtime/1000)
		TimeString = time.strftime('%d%b%y',t1)
		return TimeString
	else:
		return "9NaN99"

def sendMessage(MessageText="EV Status"):
	'''not presently used, but email / sms notification sending function'''
	import smtplib
	import settings

	from email.mime.text import MIMEText


	# PCfB Stuff
	me = 'XXXXXX@jellywatch.org'
	port = 587
	password = settings.pa
	mailhost = 'smtp.dreamhost.com'

	you = 'XXXXx@mms.att.net'
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
BadBattery = False
ThrusterServo = False
dropWeight = False

if Opt.missions:
	'''utility to show default values for selected missions'''
	getMissionDefaults()
	sys.exit("Done")

if Opt.printhtml:
	'''print format of auv.html auto-refreshing file'''
	printhtmlutility()
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
	
# TIMEOUTS are in hours? or days?
mission_defaults = {
	"profile_station"  : {"MissionTimeout": 4,   "NeedCommsTime":60, "Speed":1 },
	"sci2"             : {"MissionTimeout": 2,   "NeedCommsTime":60, "Speed":1 },
	"mbts_sci2"        : {"MissionTimeout": 48,  "NeedCommsTime":60, "Speed":1 },
	"keepstation"      : {"MissionTimeout": 4,   "NeedCommsTime":45, "Speed":.75 },
	"ballast_and_trim" : {"MissionTimeout": 1.5, "NeedCommsTime":45, "Speed":0.1 },
	"keepstation_3km"  : {"MissionTimeout": 4,   "NeedCommsTime":45, "Speed":.75 },
	"transit_3km"      : {"MissionTimeout": 1,   "NeedCommsTime":30, "Speed":1 },
	"spiral_cast"      : {"MissionTimeout": 3,   "NeedCommsTime":180, "Speed":1 }
}

#########
##
## LOAD AND PARSE EVENTS
##
now = 1000 * time.mktime(time.localtime())  # (*1000?)

startTime = getDeployment()

if not startTime:
	if DEBUG:
		sys.exit("##  Vehicle {} has no deployments".format(VEHICLE))
	else:
		sys.exit()

recovered = getRecovery(starttime=startTime)

plugged = getPlugged(recovered)

note,noteTime = parseNotes(getNotes(startTime))

# vehicle not recovered
if (not recovered) or DEBUG:
	critical  = getCritical(startTime)
	faults = getFaults(startTime)
	gfrecords = getCBIT(startTime)
	
	site,gpstime = parseGPS(getGPS(startTime))

	oldsite,oldgpstime = parseGPS(getOldGPS(gpstime,startTime))

	deltadist,deltat,speedmadegood,bearing = distance(site,gpstime,oldsite,oldgpstime)

# FULL RANGE OF RECORDS
	important = getImportant(startTime)

	missionName,missionTime = parseMission(important)
	ubatStatus,ubatTime,flowrate,flowtime,logtime  = parseImptMisc(important)
	
	gf,gftime = parseCBIT(gfrecords)

	if not logtime:
		logtime = startTime
	
	# ONLY RECORDS AFTER MISSION ## SUBTRACT A LITTLE OFFSET?
	postmission = getImportant(missionTime)
	duration,timeoutstart,needcomms,speed  = parseDefaults(postmission,mission_defaults,missionName,missionTime)

	#this is volt, amp, time
	volt,amphr,batttime = getDataAsc(startTime)
	satcomms,cellcomms = parseComms(getComms(startTime))

	if not needcomms: 
		needcomms = 60  #default
	
	
	if (critical):
		dropWeight,ThrusterServo = parseCritical(critical)
		
	if faults:
		BadBattery,DVLError = parseFaults(faults)

# vehicle has been recovered
else:   
	gf = False
	gftime = False
	duration = False
	timeoutstart = False
	needcomms = False
	satcomms = False
	cellcomms = False
	ubatTime = False
	flowtime = False
	missionTime = False
	speed = False
	site = False
	gpstime = False
	oldsite = False
	oldgpstime = False
	deltadist=False
	deltat=False
	speedmadegood = False
	volt, amphr = (False,False)
	batttime = False
	dropWeight = False
	ThrusterServo = False
	BadBattery = False
	DVLError = False
	logtime = now
	startTime = now
	missionName = "Out of the water"
	
	

if Opt.report:
	print "###############\nVehicle: " ,VEHICLE.upper()
	print "Now: " ,hours(now)
	print "GroundFault: ",gf,hours(gftime)
	print "Duration:    ",duration
	print "TimeoutStart:",hours(timeoutstart)
	print "NeedComms:",needcomms
	print "SatComms:",satcomms
	print "CellComms:",cellcomms
	ago_log = logtime - now
	print "LogRestart",hours(logtime), elapsed(ago_log), logtime
	if VEHICLE=="pontus" and not recovered:
		print "UBAT: ", ubatStatus, hours(ubatTime)
		print "FLOW: ",flowrate, hours(flowtime)
	print "SPEED: ",speed  
	print "GPS",site
	print "GPSTIme",hours(gpstime)
	print "OLDGPS",oldsite
	print "OLDGPSTIme",hours(oldgpstime)
	  # last two points: [0] is most recent
	print "Distance:",deltadist,deltat,speedmadegood
	print "Bearing: ",bearing
	print "Battery: ",volt, amphr, batttime
	print "DropWeight:",dropWeight
	print "Thruster:  ",ThrusterServo
	print "Mission: ",missionName,hours(missionTime)
	print "Deployed:  ", hours(startTime), dates(startTime),elapsed(startTime - now)
	if recovered:
		print "Recovered: ",hours(recovered), elapsed(recovered - now), recovered
		if plugged:
			print "Plugged in: ",hours(plugged)
	else:
		print "Still out there..."
	print "#####   ", VEHICLE, "######"


else:   #not opt report
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
	.st24{font-size:6px;}
	.st25{fill:#5AC1A4;stroke:none; } <!--Green No Stroke -->
	.st26{fill:#FFE850;stroke:none; } <!--Yellow No Stroke -->
	.st27{fill:#EF9D30;stroke:none; } <!--Orange No Stroke -->	
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
	"color_cartcircle",
	"color_missiondefault"]

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
	"text_bearing",
	"text_thrusttime",
	"text_commago",
	"text_ampago",
	"text_cellago",
	"text_flowago",
	"text_logago",
	"text_logtime"
]
	for tname in textnames:
		cdd[tname]='na'

	# these should persist after recovery
	specialnames=[
	"text_vehicle","text_lastupdate",
	"text_note", "text_notetime"	
	]
	for tname in specialnames:
		cdd[tname]=''
	

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
	
	if gf=="NA":
		gfnum = 3
	elif gf and gf != "OK":
		gfnum=int(4+ 1*(float(gf)>0.2) + 1*(float(gf)>0.6))
	else:
		gfnum=4    # OK means no GF. NA is no data

	###
	###   GROUND FAULT DISPLAY
	###

	cdd["color_gf"]= "st{}".format(gfnum)
	if gf == "NA":
		cdd["text_gftime"] = "no scan"
	else:
		ago_gftime = gftime - now 
		cdd["text_gftime"] = elapsed(ago_gftime)
		
	cdd["text_gf"] = gf

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
	###   MISSION OVERVIEW DISPLAY
	###

	cdd["text_vehicle"] = VEHICLE.upper()
	cdd["text_lastupdate"] = time.strftime('%H:%M')
	# Green = 5 if in defaults Lets go orange for not in
	cdd["color_missiondefault"] = ['st6','st4'][missionName in mission_defaults]   
	if noteTime:
		cdd["text_note"] = note
		cdd["text_notetime"] = elapsed(noteTime)


	
	if recovered:
	
	# The colors for boxes when vehicle is recovered
	# Set this to st18 for invisible, and st3 for white filled
	
		for cname in colornames:
			cdd[cname]='st3'
		for tname in textnames:
			cdd[tname]=''
	
		cdd["color_wavecolor"] = 'st18' # invisible
		cdd["color_dirtbox"] = 'st17'   # brown
		if plugged:
			cdd["text_mission"]     = "PLUGGED IN " + hours(plugged) + " &#x2022; " + dates(plugged)
			cdd["color_cart"]       = 'st19'
			cdd["color_cartcircle"] = 'st20'
			cdd["color_smallcable"] = 'st23'
			cdd["color_bigcable"]   = 'st22'
		
		else:
			cdd["text_mission"] = "RECOVERED " + hours(recovered)+ " &#x2022; " + dates(recovered)
			
	# NOT RECOVERED
	else:                                                                  # unicode bullet
		if missionName and missionTime:
			cdd["text_mission"]=missionName + " - " + hours(missionTime)+ " &#x2022; " + dates(missionTime)
		else:
			cdd["text_mission"]     = "PENDING " 
			
		if speed != 'na':
	#		if DEBUG:
	#			print >> sys.stderr, "#SPEED:",speed
			cdd["text_speed"]= "%.1f" % speed + "m/s"

		###
		###   GPS DISPLAY
		###
		cdd["text_gps"] = hours(gpstime)
		cdd["color_gps"] = ['st4','st5'][(now - gpstime > 3600000)]
		cdd["text_thrusttime"] = "%.1f" % speedmadegood + "km/hr"
		cdd["text_bearing"] = "tbd&#x00B0;"  # 		
		# cdd["text_bearing"] = "%d" % (int(bearing)) "&#x00B0;"  # degree sign


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
	
		### BATTERY INFO
	
		cdd["color_wavecolor"] = 'st0'
		cdd["color_dirtbox"] = 'st18'

	
		if batttime:
	#		if DEBUG:
			#	print >> sys.stderr, "#BATTTIME", batttime
			cdd["text_ampago"] = elapsed(batttime-now)
		else:
			cdd["text_flowago"]="Default"
	

		cdd["text_volts"]= "%.1f" % volt
		cdd["text_amps"]= "%.1f" % amphr 
	
		voltnum=int(4 + 1*(volt<15) + 1*(volt<14))
		if volt > 0:
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
		if BadBattery > 100: # this is the unixtine
			if DEBUG:
				print >> sys.stderr, "# BAD BATTERY:",elapsed(BadBattery)

		cdd["color_drop"] = ['st4','st6'][(dropWeight>1)]
		if dropWeight > 100:
			cdd["text_droptime"] = hours(dropWeight)
		else:
			cdd["text_droptime"] =""
			
			

	# print "Launched:  ", hours(startTime)  
	# if recovered:
	# 	print "Recovered: ",hours(recovered)

	if Opt.savefile:
		with open(OutPath.format(VEHICLE),'w') as outfile:
			outfile.write(svghead)
			outfile.write(svgtext.format(**cdd))
			if BadBattery > 100:
				outfile.write(svgbadbattery)
			if not recovered:
				outfile.write(svglabels)
				if VEHICLE=="pontus":
					outfile.write(svgpontus)
			outfile.write(svgtail)
		
		
	elif not Opt.report and not DEBUG:
		print svghead
		print svgtext.format(**cdd)
		if BadBattery:
			print svgbadbattery
		if not recovered:
			print svglabels
			if VEHICLE=="pontus":
				print svgpontus
		print svgtail
	
	
# svgDictionary = dict(x.items() + y.items())
