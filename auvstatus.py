#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
	Version 1.4 - Bumping version number after misc changes.
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
import re
from collections import deque
from LRAUV_svg import svgtext,svghead,svgpontus,svgbadbattery,svgtail,svglabels,svgerror,svgerrorhead,svgwaterleak   # define the svg text?

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
	parser.add_argument("-s", "--sim",action="store_true"  , help="create a fake example SVG")
	parser.add_argument("-a", "--anyway",action="store_true"  , help="process even after recovery")
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
		print >> sys.stderr, "### QUERY:",URL

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
		return None

	
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
		print >> sys.stderr, "\n#===========================\n",mission, "\n"
		try:
			connection = urllib2.urlopen(URL,timeout=5)
			if connection: # here?
				raw = connection.read()
				structured = json.loads(raw)
				connection.close()
				result = structured['result']
			
				print >> sys.stderr, URL
				try: 
					splitted = str(result).split("{")
					for item in splitted:
						print >> sys.stderr,item
				except KeyError:
					print >> sys.stderr,"NA"
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
	qString = runQuery(event="logCritical",limit="1000",timeafter=starttime)
	retstring = ""
	if qString:
		retstring = qString
	
	return retstring
	
def getFaults(starttime):
	'''
	Software Overcurrent Add swatch to thruster section? 
	LCB fault: Software Overcurrent
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

def getImportant(starttime,inputname=""):
	qString = runQuery(event="logImportant",name=inputname,limit="2000",timeafter=starttime)
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

def getDataAsc(starttime,mission):
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
	
	WetLabsUBAT.flow_rate=0.333607 l/s
'''

	Bailout=False
	
	DataURL='https://okeanids.mbari.org/TethysDash/data/{vehicle}/realtime/sbdlogs/{extrapath}/shore.asc'
	volt = 0
	amp  = 0
	volttime = 0
	flowtime = 0
	flow = 999
	Tracking = []
	TrackTime = []
	allpaths =[]
	NeedTracking = True

	record = runQuery(event="dataProcessed",limit="3",timeafter=starttime)
	
	for checkpath in record:
		allpaths.append(checkpath['path'])
		
	if (len(allpaths) ==3):   # get three most recent
		if allpaths[0]==allpaths[1]:   # if first two are the same, drop second
			z=allpaths.pop(1)
		else:            # otherwise drop last one
			z=allpaths.pop(2)
			
	for pathpart in allpaths:
		volt=0
		amp =0
		volttime=0
		
		extrapath = pathpart
		NewURL = DataURL.format(vehicle=VEHICLE,extrapath=extrapath)
		if DEBUG:
			print >> sys.stderr, "# DATA NewURL",NewURL
		datacon = urllib2.urlopen(NewURL,timeout=5)
		# pull last X lines from queue. This was causing problems on some missions so increased it
		lastlines = deque(datacon)
		lastlines.reverse() #in place
		for nextline in lastlines:
# 			if DEBUG:
# 				print >> sys.stderr, "#Battery nextline:",nextline.rstrip()
			if "platform_battery_" in nextline:
				fields = nextline.split("=")
				
 				if (volt==0) and "voltage" in nextline:
#				if "voltage" in nextline:
					volt     = float(fields[3].split(" ")[0])
					volttime = int(float(fields[0].split(',')[1].split(" ")[0])*1000)  # in seconds not MS
				if amp == 0 and "charge" in nextline:
					amp      = float(fields[3].split(" ")[0])
			if VEHICLE == 'pontus':
				''' Fault  UBAT flow rate is below the specified threshold of 0.05 l/s.   WetLabsUBAT'''
				'''WetLabsUBAT.flow_rate=0.333607 l/s'''
				if (flow == 999) and "WetLabsUBAT.flow_rate" in nextline:
					if DEBUG:
						print >> sys.stderr, "# FLOWDATA",nextline.rstrip()
					flowfields = nextline.split("=")
					flow      = int(1000 * float(flowfields[-1].split(" ")[0]))
					flowtime = int(float(flowfields[0].split(',')[1].split(" ")[0])*1000)
					if DEBUG:
						print >> sys.stderr, "# FLOWNUM",flow
					
			if "acoustic" in mission and NeedTracking:
				'''2020-10-10T20:41:20.873Z,1602362480.873 Unknown-->Tracking.range_to_contact=389.093750 m'''
				if len(Tracking) < 2:
					if "Tracking.range" in nextline:
						tfields = nextline.split("=")
						trange  = int(float(tfields[-1].split(" ")[0]))
						ttime   = int(float(tfields[0].split(',')[1].split(" ")[0])*1000)
						if trange:
							Tracking.append(trange)
							TrackTime.append(ttime)
				else:
					NeedTracking = False
			else:
				NeedTracking = False
						

 			if (volt) and (amp) and (VEHICLE == 'pontus' and flow < 999) and (NeedTracking == False):
 				Bailout = True
 				break
 		if Bailout == True:
 			break
 	if DEBUG:
 		if len(TrackTime) > 1:
			print >> sys.stderr, "#> Complete tracking:",Tracking, TrackTime, elapsed(TrackTime[0] - now)

	return volt,amp,volttime,flow,flowtime,Tracking,TrackTime

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
	CriticalError = ""
	CriticalTime  = False
	Water         = False
	
	# if DEBUG:
	# 	print "### Start Recordlist"
	# 	print recordlist
	# 	print "### End Recordlist"
	# 	# need to split this record?
	'''WATER DETECTED IN PRESSURE HULL. BURNWIRE ACTIVATED CBIT'''
	
	
	for Record in recordlist:
		RecordText = Record.get("text","NA")
		# if DEBUG:
		# 	print >> sys.stderr, "# CRITICAL NAME:",Record["name"],"===> ", Record["text"]
		if Record["name"]=="DropWeight":
			Drop=Record["unixTime"]
		if RecordText.startswith("WATER DETECTED"):
			Water = Record["unixTime"]
			
		if "burnwire activated" in RecordText.lower():
			Drop = Record["unixTime"]
		if (not ThrusterServo) and "ThrusterServo" in RecordText and "Hardware Fault" in RecordText:
			ThrusterServo = Record["unixTime"]
		if (not CriticalError) and not RecordText.startswith("Could not open") and not Record["name"] == "NAL9602":
#		  and not "NAL9602" in RecordText and not "Hardware Fault in component" in RecordText:
			CriticalError = RecordText[:41]
			if len(RecordText)> 41:
				CriticalError += "..."
			CriticalTime = Record["unixTime"]
			if DEBUG:
				print >> sys.stderr, CriticalError, (now-CriticalTime)/3600000
			if (((now - CriticalTime)/3600000) > 6):
				CriticalError = ""
				CriticalTime = False
			
		# if Record["name"]=="CBIT" and Record.get("text","NA").startswith("LAST"):
	return Drop, ThrusterServo, CriticalError, CriticalTime, Water

def parseFaults(recordlist):
	'''https://okeanids.mbari.org/TethysDash/api/events?vehicles=brizo&eventTypes=logFault&from=1591731032512
	
	Also includes RudderServo and DVL_Micro, RDI_Pathfinder'''
	BadBattery    = False
	DVLError = False
	Software = False
	Hardware = False
	Overload = False
	WaterFault    = False
	# if DEBUG:
	# 	print "### Start Recordlist"
	# 	print recordlist
	# 	print "### End Recordlist"
	# 	# need to split this record?
	for Record in recordlist:
		# if DEBUG:
		# 	print "NAME:",Record["name"],"===> ", Record["text"]
		if Record["name"]=="BPC1" and Record.get("text","NA").startswith("Battery stick"):
			BadBattery=Record["unixTime"]
			if DEBUG:
				print >> sys.stderr,"## BAD BATTERY in FAULT"
		if (not Software) and "software overcurrent" in Record["text"].lower():
			Software = Record["unixTime"]
		
		if (not Overload) and "overload error" in Record["text"].lower():
			Overload = Record["unixTime"]
		
		if (not Hardware) and "thruster uart error" in Record["text"].lower():
			Hardware = Record["unixTime"]
			
		if Record["text"].upper().startswith("WATER ALARM AUX"):
			WaterFault = Record["unixTime"]
		
		# THIS ONE needs to take only the most recent DVL entry, in case it was off and now on. See other examples.

		if not DVLError and Record["name"] in ["DVL_Micro", "RDI_Pathfinder","AMEcho"] and "failed" in Record.get("text","NA").lower():
		 	DVLError=Record["unixTime"]
	return BadBattery,DVLError,Software,Overload,Hardware,WaterFault

def parseDVL(recordlist):
	'''2020-03-06T00:30:17.769Z,1583454617.769 [CBIT](CRITICAL): Communications Fault in component: RDI_Pathfinder
	
	DVL potential instruments: 
		DVL_micro
		Rowe_600
		RDI_Pathfinder
		configSet AMEcho.loadAtStartup 0 bool

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
	'''NOTE: this does not search back far enough to find original time when mission parameter were defined'''
	
	MissionName=""
	MissionTime=False
	## PARSE MISSION NAME
	for Record in recordlist:
		# if Record["name"]=="MissionManager":
# 		if MissionTime: 
# 			if Record["text"].startswith("Scheduling is paused") or Record["text"].startswith("Resuming mission and schedule"):
# 				MissionTime = False
# 			else:
# 				break
		if Record["name"]=="MissionManager" and Record["text"].startswith("Started mission"):
			if DEBUG:
				print >> sys.stderr,"\n\n## MISSION RECORD",Record
			MissionName = Record.get("text","mission NA").split("mission ")[1]
			MissionTime = Record["unixTime"]
			break
			# moved break from here. does it break the if or the for??
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
			# if DEBUG:
			# 	print >> sys.stderr, "# GF RECORD",Record
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
	ubatBool = True

	FlowRate = False
	FlowTime = False
	
	LogTime = False
	DVL_on = False
	GotDVL = False
	
	StationLat = False
	StationLon = False
	myre  =  re.compile(r'WP ?([\d\.\-]+)[ ,]+([\d\.\-]+)')
	wayre =  re.compile(r'point: ?([\d\.\-]+)[ ,]+([\d\.\-]+)')

	ReachedWaypoint=False
	
	# CONFIGURE DVL config defaults
	GetDVLStartup = {
		'pontus':True,
		'tethys':True,
		'daphne':True
	}
	
	DVL_on = GetDVLStartup.get(VEHICLE,False)
	
	for Record in recordlist:
		if DEBUG:
			if "dvl" in Record["text"].lower():
				print >> sys.stderr, "** ImptMisc:",Record["name"],"<-->",Record.get("text","NO TEXT FIELD")
				
		if not LogTime and (Record["name"] =='CommandLine' or Record["name"] =='CommandExec') and 'got command restart logs' in Record.get("text","NA"):
			LogTime = Record["unixTime"]
		
		''' DVL PARSING
		DVL potential instruments: 
			DVL_micro
			Rowe_600
			RDI_Pathfinder
			configSet AMEcho.loadAtStartup 0 bool
'''
		## RELOCATED (Duplicated) from parseMission
		RecordText = Record["text"]
		if not ReachedWaypoint and StationLon == False and RecordText.startswith("got command set") and (".Lon " in RecordText or ".Longitude" in RecordText or ".CenterLongitude" in RecordText):
			if "itude" in RecordText:
				StationLon = RecordText.split("itude ")[1]
			else:
				StationLon = RecordText.split(".Lon ")[1]
			StationLon = float(StationLon.split(" ")[0])
			if DEBUG:
				print >> sys.stderr, "## Got Lon from ImptMisc", StationLon

		if not ReachedWaypoint and StationLat == False and RecordText.startswith("got command set") and (".Lat " in RecordText or ".Latitude" in RecordText or ".CenterLatitude" in RecordText):
			if "itude" in RecordText:
				StationLat = RecordText.split("itude ")[1]
			else:
				StationLat = RecordText.split(".Lat ")[1]
			StationLat = float(StationLat.split(" ")[0])
			if DEBUG:
				print >> sys.stderr, "## Got Lat from ImptMisc", StationLat

		if not StationLon and not ReachedWaypoint: 
			if Record["text"].startswith("Reached Waypoint"):
			
				waresult = wayre.search(Record["text"])
				if waresult:
					textlat,textlon=waresult.groups()
					if textlat:
						StationLat = float(textlat)
						StationLon = float(textlon)
				if DEBUG:
					print >> sys.stderr, "## Got ReachedWaypoint", StationLat,StationLon
				ReachedWaypoint = Record["unixTime"]
				
			elif Record["text"].startswith("Navigating to") and not "box" in Record["text"]:
				NavRes = myre.search(Record["text"].replace("arcdeg",""))
				if NavRes:
					textlat,textlon = NavRes.groups()
					if textlat:
						StationLat = float(textlat)
						StationLon = float(textlon)
					if DEBUG:
						print >> sys.stderr, "## Got LatLon from Navigating To", StationLat,StationLon
			
		## TODO distinguish between UBAT off and FlowRate too low
		## PARSE UBAT (make vehicle-specific)
		## configSet AMEcho.loadAtStartup 0 bool
		## got command configSet AMEcho.enabled 1.000000 bool

 		if not GotDVL and (not "(bool)" in Record.get("text","NA")) and (not "requires" in Record.get("text","NA")) and (
 		      ("DVL_micro.loadAtStartup"      in Record.get("text","NA")) or 
 		      ("RDI_Pathfinder.loadAtStartup" in Record.get("text","NA")) or 
 		      ("AMEcho.loadAtStartup"         in Record.get("text","NA")) or 
 		      ("Rowe_600.loadAtStartup"       in Record.get("text","NA"))
 		      ):
 		    # TO CHECK. this might split icorrectly on the space because sometimes config set?
 		    # configSet
 		    
 		    ## SHOULD ADD A CHECK FOR restart HERE TO SEE IF DVL WENT BACK TO CONFIG that will override these later events
 		    
			if DEBUG: 
				print >> sys.stderr, "#>> FOUND DVL: ", Record["name"] ,"===>",Record["text"], "[{}]".format(Record["unixTime"])
			DVL_on = bool(float(Record["text"].replace("loadAtStartup=","loadAtStartup ").split("loadAtStartup ")[1].split(" ")[0]))
			GotDVL = True
			if DEBUG: 
				print >> sys.stderr, "DVL Value: ", DVL_on
		if not GotDVL and ("configSet AMEcho.enabled" in Record.get("text","NA")):
			DVL_on = bool(float(Record["text"].split(".enabled ")[1].split(" ")[0]))
			GotDVL = True
			

	
			
		'''Change to got command ubat on  got command restart application'''
		#if VEHICLE == "pontus" and ubatTime == False and Record["name"]=="CommandLine" and "00000" in Record.get("text","NA") and "WetLabsUBAT.loadAtStartup" in Record.get("text","NA"):
		if VEHICLE == "pontus" and ubatTime == False and (Record["name"] =='CommandLine' or Record["name"] =='CommandExec') :
			''' Changing this to default to ON unless specifically turned off'''
			
			RecordText = Record.get("text","NA")
			
			if  "WetLabsUBAT.loadAtStartup" in RecordText:
				ubatBool = bool(float(RecordText.replace("loadAtStartup=","loadAtStartup ").split("loadAtStartup ")[1].split(" ")[0]))
				ubatTime   = Record["unixTime"]
			
			elif  "abling UBAT" in RecordText:
				ubatBool = RecordText.startswith("Enabl")
				ubatTime   = Record["unixTime"]
	
			elif RecordText.startswith("got command ubat "):
				ubatBool = "on" in RecordText
				ubatTime   = Record["unixTime"]
				if DEBUG:
					print >>sys.stderr, "## Got UBAT ON", RecordText
				
			elif RecordText.startswith("got command restart app") or RecordText.startswith("got command restart system") or RecordText.startswith("got command restart hardware"):
				ubatBool = True
				ubatTime   = Record["unixTime"]
				
			ubatStatus = ["st6","st4"][ubatBool]
	

		# THIS IS NOT CURRENTLY REPORTED	
		# if VEHICLE == "pontus" and FlowRate == False and Record["name"]=="CommandLine" and Record.get("text","NA").startswith("WetLabsUBAT.flow_rate"):
		# 	FlowRate = float(Record["text"].split("WetLabsUBAT.flow_rate ")[1].split(" ")[0])
		# 	FlowTime   = Record["unixTime"]

	return ubatStatus, ubatTime, LogTime, DVL_on, GotDVL, StationLat, StationLon, ReachedWaypoint
	

def parseDefaults(recordlist,mission_defaults,MissionName,MissionTime):
	''' parse events that get reset after missions and might be default'''
	''' check schedule: got command schedule "run Science/mbts_sci2.xml"'''
	''' todo, need to move the ubat here and change the ubat on command parsing'''
	
	TimeoutDuration=False
	TimeoutStart   =False
	NeedComms = False
	Scheduled = False
	Cleared = False
	Speed = 0
	StationLat = False
	StationLon = False
	hash = "9x9x9"
	
	if DEBUG:
		print >>sys.stderr, "## Parsing defaults"
		

	for Record in recordlist:
		RecordText = Record.get("text","NA")
		
#  		if DEBUG and Record["name"] != 'CBIT':
# 			print >> sys.stderr, "DEFAULTNAME: ", Record["name"] ,"===>",RecordText, "[{}]".format(Record["unixTime"])
			
		## PARSE TIMEOUTS Assumes HOURS
		## NOTE / TODO: When schedule is stopped or goes to default mission and you do schedule resume, does the timeout start at zero then?
		## Widget fails to pick up duration that was set long ago in the schedule.
		# if goes to default and then resumes: got command resume 
		
		if TimeoutDuration == False and \
		     ".MissionTimeout" in RecordText and RecordText.startswith("got") and not ("chedule" in RecordText):
			'''got command set profile_station.MissionTimeout 24.000000 hour'''
			'''got command set sci2.MissionTimeout 24.000000 hour'''
			TimeoutDuration = int(float(Record["text"].split("MissionTimeout ")[1].split(" ")[0]))
			'''got command set Smear.MissionTimeout 8.000000 hour'''
			if DEBUG:
				print >> sys.stderr, "# Found TimeOut of ",TimeoutDuration
			TimeoutStart    = Record["unixTime"]
			
			"esp samples have 3h timeout"

		if RecordText.startswith("Started mission") or RecordText.startswith('got command schedule clear'):
			Cleared = True
			if DEBUG:
				print >> sys.stderr, "## Got CLEAR"

		if Scheduled == False and not Cleared and (RecordText.startswith('got command schedule "run') or RecordText.startswith('got command schedule "load') or RecordText.startswith('got command schedule asap "set')) :
			'''got command schedule "run " 3p78c'''
			if DEBUG:
				print >> sys.stderr, "## Schedule Record ",RecordText

			if RecordText.startswith('got command schedule "run"') or RecordText.startswith('got command schedule "run "'):
				hashre = re.compile(r'got command schedule "run ?" (\w+)')
				'''got command schedule "run " 3p78c '''
				hash_result = hashre.search(RecordText)
				if hash_result:
					hash=hash_result.group(1)
					if DEBUG:
						print >> sys.stderr, "## Schedule Hash found ",hash
			else:
			#'''got command schedule "run Science/mbts_sci2.xml"'''
			#	'''got command schedule "load Science/circle_acoustic_contact.xml'''
				#Scheduled = Record["text"].split("/")[1].replace('.xml"','')
				if "/" in RecordText[:30]:
					Scheduled = Record["text"].split("/")[1].split('.')[0]
				else:
					'''got command schedule "set circle_acoustic_contact'''
					Scheduled = RecordText.split('"')[1].split(' ')[1].split('.')[0]
				if DEBUG:
					print >> sys.stderr, "## Found Scheduled in else",Scheduled
					
#				TODO REPLACE WITH REGEX 
#Scheduled #27 (#1 of 2 with id='3p78c'): "load Science/profile_station.xml;set profile_station.MissionTimeout 14 hour;set profile_station.Lat 36.7970 degree;set profile_station.L'''


#'''Scheduled = Record["text"].split("/")[1].split('.')[0]'''

		if Scheduled == False and not Cleared and RecordText.startswith('Scheduled #') and ("load" in RecordText) and hash in RecordText:
			''': "load Science/profile_station.xml'''
			try:
				Scheduled = RecordText.split(': "load ')[1].split('.xml')[0].split("/")[1]
			except IndexError:
				sys.exit("## Can't parse scheduled mission name: \n\t" + RecordText)
			if DEBUG:
				print >> sys.stderr, "## Found Scheduled hash",Scheduled

					
		# SETTING STATION. Will fail on multi-station missions..?
		# CHECK For Reached Waypoint: 36.821898,-121.885600   
		# MOre parsing challenges: got command set IsothermDepthSampling.Lon1 -121.847000 degree [1595360755976]	
		# got command set transit.Longitude -121.848999 degree
		# MIGHT NEED THIS TO GO BEFORE STARTING MISSION?
		# MOVE TO ParseImptMisc only??? 
		
		if StationLon == False and RecordText.startswith("got command set") and (".Lon " in RecordText or ".Longitude" in RecordText or ".CenterLongitude" in RecordText):
			if "itude" in RecordText:
				StationLon = RecordText.split("itude ")[1]
			else:
				StationLon = RecordText.split(".Lon ")[1]
			StationLon = float(StationLon.split(" ")[0])
			if DEBUG:
				print >> sys.stderr, "## Got Lon from mission", StationLon

		if StationLat == False and RecordText.startswith("got command set") and (".Lat " in RecordText or ".Latitude" in RecordText or ".CenterLatitude" in RecordText):
			if "itude" in RecordText:
				StationLat = RecordText.split("itude ")[1]
			else:
				StationLat = RecordText.split(".Lat ")[1]
			StationLat = float(StationLat.split(" ")[0])
			if DEBUG:
				print >> sys.stderr, "## Got Lat from mission", StationLat
		
		## PARSE NEED COMMS Assumes MINUTES
		if NeedComms == False and (Record["name"]=="CommandLine" or Record["name"]=="CommandExec") and RecordText.startswith("got command") and not "chedule" in RecordText and ".NeedCommsTime" in RecordText:
			'''    command set keepstation.NeedCommsTime 60.000000 minute	'''
			'''got command set profile_station.NeedCommsTime 20.000000 minute'''
			'''got command set trackPatchChl_yoyo.NeedCommsTimeInTransit 45.000000'''
			'''got command set trackPatch_yoyo.NeedCommsTimePatchTracking 120.000000 minute '''
			if DEBUG:
				print >> sys.stderr, "#Entering NeedComms",Record["text"], VEHICLE, NeedComms
			try:
				NeedComms = int(float(Record["text"].split("NeedCommsTime ")[1].split(" ")[0]))
			except IndexError:
				try:
					NeedComms = int(float(Record["text"].split("NeedCommsTimeInTransect ")[1].split(" ")[0]))
				except IndexError:
					try:
						NeedComms = int(float(Record["text"].split("NeedCommsTimeInTransit ")[1].split(" ")[0]))
					except IndexError:
						try: 
							NeedComms = int(float(Record["text"].split("NeedCommsTimePatchTracking ")[1].split(" ")[0]))
						except IndexError:	
							try:  #This one assumes hours instead of minutes. SHOULD Code to check
								NeedComms = int(float(Record["text"].split("Smear.NeedCommsTimeVeryLong ")[1].split(" ")[0])) 
								if DEBUG:
									print >> sys.stderr, "#Long NeedComms",Record["text"], VEHICLE, NeedComms
							except IndexError:	
								print >> sys.stderr, "#NeedComms but no split",Record["text"], VEHICLE
			if NeedComms and "hour" in Record["text"]:
				NeedComms = NeedComms * 60
			if DEBUG:
				print >> sys.stderr, "#FOUND NEEDCOMMS",NeedComms, VEHICLE
			## ADD FLOW RATE FOR UBAT...
			
			### For the moment this will just go from the start of the mission, but once we get SatComms, use that time
			
		## PARSE UBAT (make vehicle-specific
		## PARSE SPEED # THis used to be ".Speed"
		if Speed == 0 and (Record["name"] =='CommandLine' or Record["name"] =='CommandExec')  and ("set" in RecordText) and (".speedCmd" in RecordText or ".SpeedTransit" in RecordText or "ApproachSpeed" in RecordText or ".Speed " in RecordText) and RecordText.startswith("got"):
			if (".SpeedTransit" in RecordText):
				Speed = "%.2f" % (float(Record["text"].split(".SpeedTransit")[1].strip().split(" ")[0]))
			elif (".ApproachSpeed" in RecordText):
				Speed = "%.2f" % (float(Record["text"].split(".ApproachSpeed")[1].strip().split(" ")[0]))
			elif (".Speed" in RecordText):
				Speed = "%.2f" % (float(Record["text"].split(".Speed")[1].strip().split(" ")[0]))
			else:
				try:
					Speed = "%.2f" % (float(Record["text"].split(".speedCmd")[1].strip().split(" ")[0]))
				except ValueError:
					print >> sys.stderr, "Error parsing speed",Record["text"]
					Speed = "na"
			
			if DEBUG:
				print >> sys.stderr, "# FOUND SPEED:",Speed
			# Speed = "%.1f" % (float(Record["text"].split(".Speed")[1].split(" ")[0]))
		
	if not Speed:
			Speed = mission_defaults.get(MissionName,{}).get("Speed","na")
	if not NeedComms:
			NeedComms = mission_defaults.get(MissionName,{}).get("NeedCommsTime",0)
	if not TimeoutDuration:
			if DEBUG:
				print >> sys.stderr, "# NO TIMEOUT - checking defaults"
			
			TimeoutDuration = mission_defaults.get(MissionName,{}).get("MissionTimeout",0)
			TimeoutStart = MissionTime
	
			
	return TimeoutDuration, TimeoutStart, NeedComms,Speed,Scheduled,StationLat,StationLon

def handleURLerror():
	now = 1000 * time.mktime(time.localtime())
	timestring = dates(now) + " - " +hours(now)
	if Opt.savefile:
		with open(OutPath.format(VEHICLE),'w') as outfile:
			outfile.write(svgerrorhead)
			outfile.write(svgerror.format(text_vehicle=VEHICLE,text_lastupdate=timestring))		
		print >> sys.stderr, "URL ACCESS ERROR:",VEHICLE
		
	elif not Opt.report:
		print svgerrorhead
		print svgerror.format(text_vehicle=VEHICLE,text_lastupdate=timestring)
		sys.exit("URL ACCESS ERROR:"+VEHICLE)

def makeTrackSVG(Tracking,TrackTime):
	'''<!-- tracking -->
<polygon class="st27" points="394,300 398,308 390,308 394,300"/>
<polygon class="st25" points="394,308 398,300 390,300 394,308"/>
<circle  class="st16" cx="394" cy="304" r="3"/>
<text desc="text_track" transform="matrix(1 0 0 1 400 303)" class="st12 st9 st13">RANGE: 283m</text>
<text desc="text_trackago" transform="matrix(1 0 0 1 400 310)" class="st12 st9 st13">18h 48m ago</text>'''
	
	BaseText = '''{tr}<text desc="text_track" transform="matrix(1 0 0 1 400 303)" class="st12 st9 st13">RANGE: {ra}m</text>
<text desc="text_trackago" transform="matrix(1 0 0 1 400 310)" class="st12 st9 st13">{ti}</text>'''

	rangem=Tracking[0]
	timetext =elapsed(TrackTime[0] - now)
	if len(Tracking)>1:
		trend = Tracking[0]-Tracking[1]
		if abs(trend) < 20:
			trackshape = '<circle  class="st16" cx="394" cy="304" r="3"/>\n'
		elif trend < 0:
			trackshape = '<polygon class="st25" points="394,308 398,300 390,300 394,308"/>\n'  # "green downarrow"
		else:
			trackshape = '<polygon class="st27" points="394,300 398,308 390,308 394,300"/>\n'  # orange uparrow
	else:
		trackshape = '<circle  class="st16" cx="394" cy="304" r="3"/>\n'
	
	tracksvg = BaseText.format(tr=trackshape,ra=rangem,ti=timetext)
	
	return tracksvg	

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
		if days > 4:
			DurationString = "long time"
		if rawdur < 1:
			DurationString += " ago"
		else:
			DurationString = "in " + DurationString
		return DurationString
	else:
		return "NA"

def parseDistance(site,StationLat,StationLon,knownspeed,knownbearing,gpstime):
	''' using already calculated reckoned speed, get distance and time to last waypoint'''
	if knownspeed > 0.09 and abs(site[0]) > 1:
		deltadist,deltat,speedmadegood,bearing = distance((StationLat,StationLon),3600000,site,7200000)
		if DEBUG:
			print >> sys.stderr, "# StationDistance, bearing:", deltadist,bearing
			print >> sys.stderr, "# OldBearing:", knownbearing
						
		if (deltadist > 0.3):			
			timetogo = deltadist / knownspeed
			return 3600000 * timetogo, deltadist
		elif abs(bearing-knownbearing) < 20:
			# heading mismatch
			return bearing,deltadist			  
			if DEBUG:									  
				print "# Station close or bearing mismatch"
		else:
			return -1,deltadist							  
	else:
		return -2,0
		



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
	radius = 6371  # km
	dlat = math.radians(lat2 - lat1)
	dlon = math.radians(lon2 - lon1)
	a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
		math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
		math.sin(dlon / 2) * math.sin(dlon / 2))
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	d = radius * c

	Y = math.sin(dlon) *  math.cos(math.radians(lat2))	
	X = math.cos(math.radians(lat1))*math.sin(math.radians(lat2)) - math.sin(math.radians(lat1))*math.cos(math.radians(lat2))*math.cos(dlon)
	Bearing = -1* int(math.degrees(math.atan2(X,Y)) - 90 ) % 360

	deltat = time - oldtime
	seconds = deltat / 1000.0
	hours = seconds / (60*60)

	if (hours > 0):
		speed = d / hours
	else:
		speed = 0
	# BEARING: 
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

def sim():
	cdd={
	"color_drop"           : "st4",
	"color_thrust"         : "st4",
	"color_bat1"           : "st4",
	"color_bat2"           : "st4",
	"color_bat3"           : "st4",
	"color_bat4"           : "st4",
	"color_bat5"           : "st6",
	"color_bat6"           : "st6",
	"color_bat7"           : "st6",
	"color_bat8"           : "st6",
	"color_satcomm"        : "st5",
	"color_cell"           : "st6",
	"color_gps"            : "st4",
	"color_amps"           : "st4",
	"color_volts"          : "st4",
	"color_gf"             : "st6",
	"color_dvl"            : "st3",
	"color_bt2"            : "st3",
	"color_bt1"            : "st3",
	"color_ubat"           : "st3",
	"color_flow"           : "st3",
	"color_sw"        	   : "st3",
	"color_wavecolor"      : "st0",
	"color_dirtbox"        : "st18",
	"color_missiondefault" : "st25",
	"color_commago"        : "st5",
	"color_missionago"     : "st6",
	"color_arrow"          : "st16",
	"color_scheduled"      : "st26"
	
	}
	

	cartcolors=["color_bigcable",
	"color_smallcable",
	"color_cart",
	"color_cartcircle"]
	
	for cname in cartcolors:
		cdd[cname]='st18'

	textdict={
	"text_mission"        : "profile_station - 03:56 • 15Jul15",
	"text_cell"           : "12:34",
	"text_sat"            : "01:23",
	"text_gps"            : "02:46",
	"text_speed"          : "1.0m/s",
	"text_nextcomm"       : "12:34",
	"text_timeout"        : "12:34",
	"text_amps"           : "234.5",
	"text_volts"          : "14.5",
	"text_droptime"       : "",
	"text_gftime"         : "12:35",
	"text_gf"             : "0.34",
	"text_bearing"        : "45°",
	"text_arrow"		  : "45",
	"text_thrusttime"     : "2.9km/hr",
	"text_reckondistance" : "3.2km in 1.2h",
	"text_commago"        : "1h 2m ago",
	"text_ampago"         : "2h 34m ago",
	"text_cellago"        : "2h 3m ago",
	"text_flowago"        : "12m ago",
	"text_gpsago"         : "1h 59m ago",
	"text_logago"         : "1d 1h 1m ago",
	"text_logtime"        : "01:23",
	"text_vehicle"        : "SIMULON",
	"text_lastupdate"     : "12:34",
	"text_note"           : "", 
	"text_notetime"       : "",
	"text_arrivestation"  : "12:34 in 1h 12m",
	"text_stationdist"    : "4.5km",
	"text_stationdist"    : "1.2km",
	"text_scheduled"      : "SCHEDULED: keep_station",
	"text_criticaltime"   : "12:34",
	"text_criticalerror"   : "SW LEAK"
	}


	cdd = dict(cdd.items() + textdict.items())
	print >> sys.stderr, "#Saving file auv_sim.svg"
	SimPath="./auv_sim.svg"
	with open(SimPath,'w') as outfile:
		outfile.write(svghead)
		outfile.write(svgtext.format(**cdd))
		outfile.write(svgbadbattery)
		outfile.write(svglabels)
		outfile.write(svgtail)

# svgDictionary = dict(x.items() + y.items())

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
Tracking = []
TrackTime = []

if Opt.missions:
	'''utility to show default values for selected missions'''
	getMissionDefaults()
	sys.exit("Done")

if Opt.sim:
	'''print out general svg'''
	sim()
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
	"profile_station"  	: {"MissionTimeout": 4,   "NeedCommsTime":60,  "Speed":1.0 },
	"portuguese_ledge" : {"MissionTimeout": 4,   "NeedCommsTime":120, "Speed":1.0 },
	"sci2"             : {"MissionTimeout": 2,   "NeedCommsTime":60,  "Speed":1.0 },
	"mbts_sci2"        : {"MissionTimeout": 48,  "NeedCommsTime":60,  "Speed":1.0 },
	"keepstation"      : {"MissionTimeout": 4,   "NeedCommsTime":45,  "Speed":.75 },
	"ballast_and_trim" : {"MissionTimeout": 1.5, "NeedCommsTime":45,  "Speed":0.1 },
	"profile_station_backseat" : {"MissionTimeout": 1, "NeedCommsTime":60,  "Speed":1.0 },
	"keepstation_3km"  : {"MissionTimeout": 4,   "NeedCommsTime":45,  "Speed":.75 },
	"transit_3km"      : {"MissionTimeout": 1,   "NeedCommsTime":30,  "Speed":1.0 },
	"transit"      	   : {"MissionTimeout": 1,   "NeedCommsTime":30,  "Speed":1.0 },
	"CorkAndScrew"     : {"MissionTimeout": 20,  "NeedCommsTime":60,  "Speed":1 },
	"IsothermDepthSampling"      : {"MissionTimeout": 20,  "NeedCommsTime":60,  "Speed":1 },
	"isotherm_depth_dampling"    : {"MissionTimeout": 20,  "NeedCommsTime":60,  "Speed":1 },
	"esp_sample_at_depth"        : {"MissionTimeout": 4,   "NeedCommsTime":180, "Speed":.7 },
	"esp_sample_station"         : {"MissionTimeout": 24,  "NeedCommsTime":45,  "Speed":1 },
	"calibrate_sparton_compass"  : {"MissionTimeout": 1,   "NeedCommsTime":60,  "Speed":1 },
	"SpartonCompassCal"          : {"MissionTimeout": 1,   "NeedCommsTime":60,  "Speed":1 },
	"spiral_cast"                : {"MissionTimeout": 3,   "NeedCommsTime":180, "Speed":1 },
	"trackPatchChl_yoyo"         : {"MissionTimeout": 24,  "NeedCommsTime":180, "Speed":1 } 
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

bearing = 999
WaterCritical = False
WaterFault = False

# vehicle not recovered
if (not recovered) or Opt.anyway or DEBUG:
	critical  = getCritical(startTime)
	faults = getFaults(startTime)
	gfrecords = getCBIT(startTime)
	
	site,gpstime = parseGPS(getGPS(startTime))

	oldsite,oldgpstime = parseGPS(getOldGPS(gpstime,startTime))

	deltadist,deltat,speedmadegood,bearing = distance(site,gpstime,oldsite,oldgpstime)

# FULL RANGE OF RECORDS
	important = getImportant(startTime)

	# mission time is off if schedule paused (default) and resumed. Detect this and go back further?
	missionName,missionTime = parseMission(important)
	
	ubatStatus,ubatTime,logtime,DVLon,GotDVL,NavLat,NavLon,ReachedWaypoint  = parseImptMisc(important)
	
	gf,gftime = parseCBIT(gfrecords)

	if not logtime:
		logtime = startTime
	
	if missionTime > 60000: 
		querytime = missionTime-60000
		# ONLY RECORDS AFTER MISSION ## SUBTRACT A LITTLE OFFSET?
		# CHANGING FROM CommandLine to CommandExec
		postmission = getImportant(querytime,inputname="CommandExec")
	else:
		postmission = ''
	
	if DEBUG:
		print >> sys.stderr, "MISSION TIME AND RAW", hours(missionTime),dates(missionTime),missionTime
		
	missionduration,timeoutstart,needcomms,speed,Scheduled,StationLat,StationLon  = \
	          parseDefaults(postmission,mission_defaults,missionName,missionTime)
	

	# Time to waypoint:
	if abs(NavLon) > 0:
		waypointtime,waypointdist = parseDistance(site,NavLat,NavLon,speedmadegood,bearing,gpstime)
	elif abs(StationLat) > 0:
		waypointtime,waypointdist = parseDistance(site,StationLat,StationLon,speedmadegood,bearing,gpstime)
	else:
		waypointtime = -2
		waypointdist = None
	if ReachedWaypoint:
		waypointtime = ReachedWaypoint
		waypointdist = 0.01

			

	# stationdist,stationdeltat,speedmadegood,bearing = distance(site,gpstime,oldsite,oldgpstime)
	# Just need distance from this calc, so put in fake times or make a new function and subfunction for d
	
	
	
	if DEBUG:
		print >> sys.stderr,"#DURATION and timeout start", missionduration,timeoutstart
	
	#this is volt, amp, time
	volt,amphr,batttime,flowdat,flowtime,Tracking,TrackTime = getDataAsc(startTime,missionName)
	satcomms,cellcomms = parseComms(getComms(startTime))

	if not needcomms: 
		needcomms = 60  #default
	
	CriticalError=False
	if (critical):
		if DEBUG:
			print >> sys.stderr,"# Starting CRITICAL parse  "
		dropWeight,ThrusterServo,CriticalError,CriticalTime,WaterCritical = parseCritical(critical)

	DVLError=False
	BadBattery=False
	SWError = False
	HWError = False
	OverloadError = False
	
	if faults:
		BadBattery,DVLError,SWError,OverloadError,HWError,WaterFault = parseFaults(faults)

	
# vehicle has been recovered
else:   
	gf = False
	gftime = False
	missionduration = False
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
	print "MissionDuration:    ",missionduration
	print "TimeoutStart:",hours(timeoutstart)
	print "NeedComms:",needcomms
	print "SatComms:",satcomms
	print "CellComms:",cellcomms
	ago_log = logtime - now
	print "LogRestart",hours(logtime), elapsed(ago_log), logtime
	if VEHICLE=="pontus" and (not recovered):
		print "UBAT: ", ubatStatus, hours(ubatTime)
		print "FLOW: ",flowdat, hours(flowtime)
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
	if recovered and not Opt.anyway:
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
	.stleak2{fill:#7DA6D8;} <!-- critical water leak-->
	.stleak1{fill:#92c19b;} <!--aux water leak-->

	'''
	cdd={}
	# 	these are made white with black stroke
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
	"color_bat8",
	"color_satcomm",
	"color_cell",
	"color_gps",
	"color_amps",
	"color_volts",
	"color_gf",
	"color_dvl",
	"color_bt2",
	"color_bt1",
	"color_ubat",
	"color_flow",
	"color_wavecolor",
	"color_dirtbox",
	"color_bigcable",
	"color_smallcable",
	"color_cart",
	"color_sw" ,
	"color_hw",
	"color_cartcircle",
	"color_missiondefault" ]
	for cname in colornames:
		cdd[cname] = 'st3'
	
	cdd["color_arrow"] = "st16"
	
	# These are made invisible
	cartcolors=["color_bigcable",
	"color_smallcable",
	"color_cart",
	"color_cartcircle",
	"color_scheduled",
	"color_commago",
	"color_missionago",
	"color_leak"]

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
	"text_reckondistance",
	"text_commago",
	"text_ampago",
	"text_cellago",
	"text_gpsago",
	"text_logago",	
	"text_dvlstatus",
	"text_logtime"
 ]
	
	for tname in textnames:
		cdd[tname]='na'
	cdd["text_arrow"]='90'
	# these should persist after recovery
	specialnames=[
	"text_vehicle","text_lastupdate","text_flowago",
	"text_note", "text_notetime","text_scheduled","text_arrivestation",
	"text_stationdist","text_currentdist",	"text_criticaltime",
	"text_leak","text_leakago",
	"text_criticalerror"



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
	 GO TO SLEEP
 
	 '''

	commreftime = max(cellcomms,satcomms)

	now = time.time() * 1000  # localtime in unix
	
	if gf=="NA":
		gfnum = 3
	elif gf and gf != "OK":
		gfnum=int(4+ 1*(abs(float(gf))>0.08) + 1*(abs(float(gf))>0.2))
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
	# cdd["text_timeout"] = hours(timeoutstart+missionduration*3600*1000)

	cdd["text_timeout"] = hours(missionTime+missionduration*3600*1000) + " - " + elapsed((missionTime+missionduration*3600*1000) - now )

	# cdd["text_nextcomm"] = hours(timeoutstart+needcomms*60*1000)
	cdd["text_nextcomm"] = hours(commreftime+needcomms*60*1000) + " - " + elapsed((commreftime+needcomms*60*1000) - now)


	###
	###   MISSION OVERVIEW DISPLAY
	###

	cdd["text_vehicle"] = VEHICLE.upper()
	cdd["text_lastupdate"] = time.strftime('%H:%M')
	# Green = 5 if in defaults Lets go orange for not in
	cdd["color_missiondefault"] = ['st27','st25'][missionName in mission_defaults] 
	
	# NOT USED YET! NOTES  
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
		cdd["color_cartcircle"] = 'st18'
		cdd["color_smallcable"] = 'st18'
		cdd["color_bigcable"]   = 'st18'

		cdd["color_wavecolor"] = 'st18' # invisible
		cdd["color_arrow"]     = 'st18'
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
	else: 
	  
		# SWError = False
		# CriticalError = False                                                               # unicode bullet
		if missionName and missionTime:
			cdd["text_mission"]=missionName + " - " + hours(missionTime)+ " &#x2022; " + dates(missionTime)
		else:
			cdd["text_mission"]     = "PENDING " 
			
		if speed != 'na':
	#		if DEBUG:
	#			print >> sys.stderr, "#SPEED:",speed
			try:
				cdd["text_speed"]= speed + "m/s"
			except TypeError:
				cdd["text_speed"]= "%.2f" % speed + "m/s"
				
		if Scheduled:
			cdd["text_scheduled"] = "SCHEDULED: "+ Scheduled
			if "/" in Scheduled:
				Scheduled=Scheduled.split("/")[-1]
			cdd["color_scheduled"] = ['st27','st25'][Scheduled in mission_defaults]   

		# MISSION TIMES
		timetotimeout =  ((missionTime+missionduration*3600*1000)  - now) / (60*1000)
	
		if DEBUG:
			print >> sys.stderr, "#TIME TO MISSION TIMEOUT",timetotimeout

		if timetotimeout > 11:
			cdd["color_missionago"] = 'st4'
		elif timetotimeout < 1:
			cdd["color_missionago"] = 'st6'
		else:
			cdd["color_missionago"] = 'st5'

		# This is typically in minutes

		# CIRCLE NEXT TO COMM TIME in minutes
		timetocomm = int(((commreftime+needcomms*60*1000) -now) / (60*1000))
		if DEBUG:
			print >> sys.stderr, "#TIME TO COMM",timetocomm
		if timetocomm > 9:
			cdd["color_commago"] = 'st4'
		elif timetocomm < -4:
			cdd["color_commago"] = 'st6'
		else:
			cdd["color_commago"] = 'st5'

		###
		###   GPS DISPLAY
		###
		cdd["text_gps"] = hours(gpstime)
		cdd["color_gps"] = ['st4','st5'][(now - gpstime > 3600000)]
		if gpstime:
			ago_gps = gpstime - now
			cdd["text_gpsago"] = elapsed(ago_gps)

		###
		###   RECKON SPEED DISPLAY
		###
	
		cdd["text_thrusttime"] = "%.1f" % speedmadegood + "km/hr"
		# cdd["text_# bearing"] = "tbd&#x00B0;"  #
		cdd["text_arrow"] = "%d" % (int(bearing))
		cdd["text_bearing"] = "%d" % (int(bearing)) + "&#x00B0;"  # degree sign
		if (deltadist and deltat) and (deltadist < 100):
			reckontext="%.1fkm in %.1fh" % (deltadist,deltat)
			cdd["text_reckondistance"] = reckontext


		###
		###   ARRIVAL ESTIMATE
		###


		if DEBUG and (waypointtime >= 0):
			print >> sys.stderr, "TIME TO STATION from GPS TIME, not now:",hours(waypointtime),elapsed(waypointtime)
		if ReachedWaypoint:
			arrivetext = "Arrived at WP"
			cdd["text_stationdist"]   = elapsed(waypointtime - now)

		elif waypointtime == -1 or waypointdist < 0.4:
			if waypointdist:
				arrivetext = "On Station %.1f km" % waypointdist
			else:
				arrivetext = "On Station" 
		elif waypointtime == -2:
			arrivetext = "Nav missing"
		# Cheating by storing heading in waypointtime if mismatch in function
		elif waypointtime < 361:
			 arrivetext = "Heading? %d" % waypointtime
		else:
			timeatstation = gpstime + waypointtime
			arriveago = timeatstation - now

			distancetext   = "%.1fkm from last fix" % waypointdist
			currentdist = speedmadegood * (timeatstation - now) / 3600000
			currenttext   = "%.1fkm from est.veh" % currentdist

			cdd["text_stationdist"]   = distancetext
			cdd["text_currentdist"]   = currenttext

			arrivetext="%s - %s" % (hours(timeatstation),elapsed(arriveago))
			
		cdd["text_arrivestation"] = arrivetext
								

		###
		###   UBAT FLOW DISPLAY
		###
		if VEHICLE == 'pontus':
			if (flowdat < 999) and (ubatStatus=="st4"):
				if ((290 < flowdat) and (flowdat < 500)):
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
	
		voltnum=int(4 + 1*(volt<15) + 1*(volt<14.2))

		if BadBattery > 100: # this is the unixtine
			if DEBUG:
				print >> sys.stderr, "# BAD BATTERY:",elapsed(BadBattery)
			LowBattColor='st6'
		else:
			LowBattColor='st11'

		if volt > 0:
			cdd["color_amps"]  = "st{}".format(voltnum)  # change this to independent amp range
			cdd["color_volts"] = "st{}".format(voltnum)
			cdd["color_bat1"] = ['st4',LowBattColor][volt < 13.7]
			cdd["color_bat2"] = ['st4',LowBattColor][volt < 14.1]
			cdd["color_bat3"] = ['st4',LowBattColor][volt < 14.5]
			cdd["color_bat4"] = ['st4',LowBattColor][volt < 14.9]
			cdd["color_bat5"] = ['st4',LowBattColor][volt < 15.3]
			cdd["color_bat6"] = ['st4',LowBattColor][volt < 15.7]
			cdd["color_bat7"] = ['st4',LowBattColor][volt < 16.1]
			cdd["color_bat8"] = ['st4',LowBattColor][volt < 16.5]

		if DEBUG and SWError:
			print >> sys.stderr, "SOFTWARE ERROR: " ,(now-SWError)/3600000
 		
		# Ignore SW errors more than 4 hours old	
 		if (SWError and ((now - SWError)/3600000 < 4)):
			cdd["color_sw"] = 'st5'

 		if (HWError and ((now - HWError)/3600000 < 4)):
			cdd["color_hw"] = 'st5'

		if DVLError and not GotDVL:
			DVLcolor = 'st6'
			cdd["text_dvlstatus"]="ERROR"
		elif DVLon:
			DVLcolor = 'st4'
			cdd["text_dvlstatus"]="ON"
		else:
			DVLcolor = 'st5'
			cdd["text_dvlstatus"]="OFF"
		
		if CriticalError:
			cdd["text_criticalerror"] = "CRITICAL: "+ CriticalError.replace(" in component","")
			cdd["text_criticaltime"]  = elapsed(CriticalTime-now)
			
		cdd["color_dvl"] = DVLcolor
		
		if (WaterCritical):
			cdd["color_leak"] = "stleak2"
			cdd["text_leak"] = "CRITICAL LEAK: "
			cdd["text_leakago"] = elapsed(WaterCritical-now)

		elif (WaterFault):
			cdd["color_leak"] = "stleak1"
			cdd["text_leak"] = "AUX LEAK: "
			cdd["text_leakago"] = elapsed(WaterFault-now)
		

 		if (ThrusterServo>100) and ((now - ThrusterServo)/3600000 < 4):
			cdd["color_thrust"] = 'st6'
		else:
			cdd["color_thrust"] = 'st4'


		cdd["color_drop"] = ['st4','st6'][(dropWeight>1)]
		if dropWeight > 100:
			cdd["text_droptime"] = elapsed(dropWeight-now)
		else:
			cdd["text_droptime"] =""
			
			

	# print "Launched:  ", hours(startTime)  
	# if recovered:
	# 	print "Recovered: ",hours(recovered)

	if Opt.savefile:
		if DEBUG:
			print >> sys.stderr, "#Saving file ", OutPath.format(VEHICLE)
		with open(OutPath.format(VEHICLE),'w') as outfile:
			outfile.write(svghead)
			outfile.write(svgtext.format(**cdd))
			if BadBattery > 100:
				outfile.write(svgbadbattery)
			if WaterCritical or WaterFault:
				outfile.write(svgwaterleak.format(
					color_leak = cdd["color_leak"],
					text_leak = cdd["text_leak"],
					text_leakago = cdd["text_leakago"] )
				)
			if len(Tracking)>=1:
				outfile.write(makeTrackSVG(Tracking,TrackTime))
			if not recovered:
				outfile.write(svglabels)
				if VEHICLE=="pontus":
					outfile.write(svgpontus)
			outfile.write(svgtail)
		
		
	elif not Opt.report:
		print svghead
		print svgtext.format(**cdd)   # insert values from dictionary by name
		if BadBattery:
			print svgbadbattery
		if len(Tracking)>=1:
			print makeTrackSVG(Tracking,TrackTime)
		if not recovered:
			print svglabels
			if VEHICLE=="pontus":
				print svgpontus
		print svgtail
	
