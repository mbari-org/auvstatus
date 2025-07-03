#! /usr/bin/env python3
# -*- coding: utf-8 -*-
'''
	v 2.89  - Made dock yellow if lineCapture. reset voltage threshold if reboot
	v 2.88  - Added some docking WPs to the lookup
	v 2.87  - Changed OT to orange
	v 2.86  - Added makai to the piscivore hosts. Moved to GFScanner vs CBIT
	v 2.85  - Updated depth sparkline to have max of 1280, for Opah (!) Changed to 2560
	v 2.84  - Separate post-Mission parser for Galene to check chiton+LEDs
	v 2.83  - GPS orange if more than 3h old, and led tweaks
	v 2.82  - Added Camera and LED indicators for Galene. 
	v 2.81  - Omitted SpeedControl from Speed parsing. 
	v 2.80  - Increased max depth for sparkline to 320 m instead of 240. 
	v 2.79  - WIP: adding indicator for Planktivore ROIs - account for missing data
	v 2.78  - If vehicle is paused but a new command has been sent, show special icon
	v 2.77  - DVL Error timeout after 6h. Drop weight gray if turned off
	v 2.76  - Improved Water Leak location reporting
	v 2.75  - Put Chiton/Ayeris indicator back on for Galene
	v 2.74  - Support for docking ops - first working version
	v 2.73  - Adding NeedCommsTimeProfileStation to the parsing
	v 2.72  - Critical messages < 31 characters were sometimes not reported!
	v 2.71  - Fixed bug parsing default timeout, etc, when mission is Run vs Loaded
	v 2.70  - Moved next waypoint out of ImptMisc to its own mission-specific query
	v 2.69  - Working on parsing one-waypoint missions in case of no Nav To entry
	v 2.68  - Muting query timeout for average_current :^(
	v 2.67  - Added Fore Aft Aux to water critical message
	v 2.66  - Fixed copy/paste bug where OT triggers Paused event
	v 2.65  - Removed old debugging code which made error in mission defaults
	v 2.64  - Projected battery remaining shows days if > 5 days remaining
	v 2.63  - Parsing powerOnly piscivore cam for ahi also
	v 2.62  - Changed the way defaults and full mission names are retrieved
	v 2.61  - Upped the mA expectation for piscivore
	v 2.60  - Added Waterlinked to the list of potential DVLs, and Ahi DVL on = True 
	v 2.59  - Report piscivore powerOnly widget for daphne also
	v 2.58  - Remove year from mission start time if not recovered
	v 2.57  - Make mission name red if DEFAULT > 15 minutes
	v 2.56  - Quieting the No dataProcessed message
	v 2.55  - Properly come up paused after critical
	v 2.54  - Smarter schedule parsing for upcoming missions
	v 2.53  - Added age colors for argo battery and show ARGO battery when on shore
	v 2.52  - Fixed integer timeout bug
	v 2.51  - Fixed bug parsing Pause status when recent critical
	v 2.50  - Show age of last good Argo Battery Record
	v 2.49  - Show orange status for Piscivore cameras sending old data
	v 2.48  - Updated battery to use 3 queries
	v 2.47  - Implemented API-based retrieval of default values (lightly tested)
	v 2.46  - Accounted for age of battery update in calculating Amps remaining
	v 2.45  - YASD - Yet another speed definition ApproachSpeedNotFirstTime
	v 2.44  - Added parsing of environmental critical
	v 2.43  - Some light formatting
	v 2.42  - If two GPS fixes are too close together (30 mins), get an older one
	v 2.41  - Adding volt and amp battery threshold display
	v 2.40  - Working on recovering dead reckon data
	v 2.39  - Added piscivore camera debug info
	v 2.38  - Increased URL timeout to 8s. Display version on widget
	v 2.37  - Schedule is NOT paused upon boot-up or restart. Added mission default
	v 2.36  - Added another overthreshold scenario (migrated to github)
	v 2.35  - Make Next comm label red if more than an hour overdue
	v 2.34  - Report piscivore cam amps instead of generic label
	v 2.33  - Make Sat comm label red if last comm more than an hour overdue
	v 2.32  - Don't pause schedule on ESP stop messages
	v 2.31  - Adjusting range for piscivore camera current-to-status
	v 2.3   - Added piscivore camera status widget
	v 2.28  - If Critical since last schedule resume, then schedule = paused
	v 2.27  - Add Schedule Pause indicator (untested)
	v 2.26  - Maybe fixed a lastlines empty parsing bug around 431
	v 2.25  - Added rudimentary camera indicator for Galene.
	v 2.24  - Made station Lookup use 3 decimals.
	v 2.24  - Added arrow for high-side/low-side GF.
	v 2.23  - Lookup table for waypoint names in the Nav projection section
	v 2.22  - Added dot for log age. Added [ASAP] to schedule. Extended sparkline.
	v 2.21  - Added Argo battery status (low or OK)
	v 2.20  - Added freshness label to the depth sparkline
	v 2.19  - Use last 7 values to calculate current draw
	v 2.18  - Added projection of hours remaining on battery
	v 2.17  - Added new NeedComms syntax
	v 2.16  - Dynamically adjust max depth for sparkline
	v 2.15  - Improved retrieval of Depth Data for full record
	v 2.14  - New style query for Depth Data. Changed GPS query to limit 2
	v 2.13  - Reformatted and relocated sparkline
	v 2.12  - In progress sparkline for depth
	v 2.11  - Fixed data decoding from ASCII retrieve
	v 2.1   - Updated to Python 3
	v 2.03  - Fixed pontus-specific UBAT formatting
	v 2.02  - Adding #sticky note functionality
	v 2.01  - Missing variable initialization in recovered vehicle
	v 2.0   - Implemented config file
	v 1.96  - Starting to incorporate config file. Removed email function
	v 1.95a - Implemented over threshold
	v 1.94  - Added indicator for failure to communicate with CTD
	v 1.93  - Added battery discharge rate meter indicator
	v 1.92  - Added report for number of bad battery sticks
	v 1.91  - In progress, Adding new Data parsing
	v 1.9   - Fixed Navigating to Parsing
	v 1.8   - Added Motor Lock Fault parsing
	v 1.7   - Minor enhancements
	v 1.6   - Updated needcomms parsing
	v 1.5   - Updated default mission list
	v 1.4   - Bumping version number after misc changes.
	v 1.3   - Streamlined code so it doesn't download data for recovered vehicles
	v 1.2   - making UBAT pontus-specific (move to svg["pontus"] for more vehicles)
	v 1.1   - adding cart
	v 1.0   - works for pontus
	
	Usage: auvstatus.py -v pontus -r  (see a summary of reports)
	       auvstatus.py -v pontus > pontusfile.svg  (save svg display)
	  
	  '''

import argparse
import sys
import time
import os
import urllib.request, urllib.error, urllib.parse
import json
import math
import re
from collections import deque
from LRAUV_svg import svgtext,svghead,svgpontus,svggalene,svgbadbattery,svgtail,svglabels,svgerror,svgerrorhead,svgwaterleak,svgstickynote,svgpiscivore,svg_planktivore   # define the svg text?
from config_auv import servername, basefilepath

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def get_options():
	parser = argparse.ArgumentParser(usage = __doc__)
#	parser.add_argument('infile', type = argparse.FileType('rU'), nargs='?',default = sys.stdin, help="output of vars_retrieve")
	parser.add_argument("-b", "--DEBUG",	action="store_true", help="Print debug info")
	parser.add_argument("-r", "--report",	action="store_true", help="print results")
	parser.add_argument("-f", "--savefile",	action="store_true", help="save to SVG named by vehicle at default location")
	parser.add_argument("-v", "--vehicle",	default="pontus"  , help="specify vehicle")
	parser.add_argument("--printhtml",action="store_true"  , help="print auv.html web links")
	parser.add_argument("-m", "--missions",action="store_true"  , help="spit out mission defaults")
	parser.add_argument("--newmissions",action="store_true"  , help="test new mission defaults")
	parser.add_argument("-a", "--anyway",action="store_true"  , help="process even after recovery")
	parser.add_argument("-i", "--inst",default="mbari"  , help="choose the server (mbari or whoi)")
	parser.add_argument("Args", nargs='*')
	options = parser.parse_args()
	return options

def unpackJSON(data):
	if type(data) == type(b'x'):
		data = data.decode('utf-8')

	structured = json.loads(data)
	# if DEBUG:
	# 	print("### STRUCTURED:",structured, file=sys.stderr)
	if 'result' in structured:
		result = structured['result']
	elif 'chartData' in structured:
		result = structured['chartData']
	else:
		result = structured
	return result

def runQuery(event="",limit="",name="",match="",timeafter="1234567890123"):
	limit_str=""
	if limit:
		limit_str = "&limit={}".format(limit)
	if match:
		match = "&text.matches=" + match
	if name:
		name = "&name=" + name
	if event:
		event = "&eventTypes=" + event
		
	'''send a generic query to the REST API. Extra parameters can be over packed into limit (2)'''
	
	vehicle = VEHICLE

	if not timeafter or int(timeafter) < 1234567890123:
		timeafter="1234567890123"
		
	BaseQuery = "https://{ser}/TethysDash/api/events?vehicles={v}{e}{n}{tm}{l}&from={t}"
	URL = BaseQuery.format(ser=servername,v=vehicle,e=event,n=name,tm=match,l=limit_str,t=timeafter)
	
	if DEBUG:
		print("### QUERY:",URL, file=sys.stderr)

	try:
		connection = urllib.request.urlopen(URL,timeout=8)		
		if connection:
			raw = connection.read()
			structured = json.loads(raw)
			connection.close()
			result = structured['result']
		else:
			print("# Query timeout",URL, file=sys.stderr)
			result = ''
		return result
	except urllib.error.HTTPError or ssl.SSLError:
		if ssl.SSLError:
			print("# QUERY TIMEOUT:",URL, file=sys.stderr)
		else:
			print("# FAILURE IN QUERY:",URL, file=sys.stderr)
		handleURLerror()
		return None

def runNewStyleQuery(api="",extrastring=""):
	# example /events? or /data?  
	# https://okeanids.mbari.org/TethysDash/api/vconfig?vehicle=makai&gitTag=2020-07-18a&since=2020-07-21
	# https://okeanids.mbari.org/TethysDash/api/deployments/last?vehicle=pontus
	# https://okeanids.mbari.org/TethysDash/api/data?vehicle=pontus

	if api:
		apistring = "{a}?vehicle={v}".format(a=api,v=VEHICLE)
		
	'''send a generic query to the REST API. Extra parameters can be over packed into limit (2)'''

	NewBaseQuery = "https://{ser}/TethysDash/api/{apistring}{e}"
	URL = NewBaseQuery.format(ser=servername,apistring=apistring,e=extrastring)
	
	if DEBUG:
		print("### NEW QUERY:",URL, file=sys.stderr)

	try:
		connection = urllib.request.urlopen(URL,timeout=8)		
		if connection:
			datastream = connection.read()
			result = unpackJSON(datastream)
		else:
			print("# Query timeout",URL, file=sys.stderr)
			result = ''
		return result
	except urllib.error.HTTPError or ssl.SSLError:
		if ssl.SSLError:
			if DEBUG:
				print("\n### HTTP ERROR:",URL, file=sys.stderr)
			if not "PowerOnly" in URL and not "AvgRois" in URL and not "average_current" in URL and not "battery_voltage" in URL and not "battery_charge" in URL and not "data/depth" in URL:
				print("# NEW QUERY TIMEOUT:",URL, file=sys.stderr)
				handleURLerror()
		else:
			print("# FAILURE IN QUERY:",URL, file=sys.stderr)
			handleURLerror()
		return None	

def getDeployment():
	'''return start time for deployment'''
	startTime = 0
	try:
		launchString = runQuery(event="launch",limit="1")
		if launchString:
			startTime = launchString[0]['unixTime']
			if DEBUG:
				print("# LAUNCH STRING:",launchString, file=sys.stderr)
	except ssl.SSLError:
		print("# DEPLOYMENT TIMEOUT",VEHICLE, file=sys.stderr)
	return startTime

def getNewDeployment():
	'''return start time for deployment and deploymentID. Starts too early!'''
	startTime = 0
	deployID = ""
	try:
		launchData = runNewStyleQuery(api="deployments/last")
		if launchData:
			startTime = launchData.get('startEvent',{}).get('unixTime',0)
			deployID = launchData.get('deploymentId',"")
	except ssl.SSLError:
		print("# DEPLOYMENT TIMEOUT",VEHICLE, file=sys.stderr)
	if DEBUG:
		print("### DEPLOYMENT TIME:",startTime, file=sys.stderr)
		print("### DEPLOYMENT ID:",deployID, file=sys.stderr)
		print("### New Deploy String:",launchData, file=sys.stderr)
	return startTime,deployID


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
 
def getGPS(starttime,mylimit="1"):
	''' extract the most recent GPS entry'''
	if DEBUG:
		print("###\n### RUNNING GPS LIMIT 1 starttime:",starttime, file=sys.stderr)
	qString = runQuery(event="gpsFix",limit=mylimit,timeafter=starttime)
	retstring=""
	if qString:
		retstring = qString	
	return retstring

def getArgo(starttime,mylimit="1"):
	''' extract the most recent GPS entry'''
	if DEBUG:
		print("###\n### RUNNING ARGO LIMIT 50 starttime:",starttime, file=sys.stderr)
	qString = runQuery(event="argoReceive",limit=mylimit,timeafter=starttime)
	retstring=""
	if qString:
		retstring = qString	
	return retstring
	
def getArgo50(starttime,mylimit="100"):
	''' extract the most recent GPS entry'''
	if DEBUG:
		print("###\n### RUNNING ARGO LIMIT 50 starttime:",starttime, file=sys.stderr)
	qString = runQuery(event="argoReceive",limit=mylimit,timeafter=starttime)
	retstring=""
	if qString:
		retstring = qString	
	return retstring

def newGetOldGPS(starttime,mylimit="2"):
	''' extract the most recent GPS entry'''
	if DEBUG:
		print("###\n### RUNNING NEW OLD GPS LIMIT 2 starttime:",starttime, file=sys.stderr)
	qString = runQuery(event="gpsFix",limit=mylimit,timeafter=starttime)
	retstring=""
	if qString and len(qString) > 1:
		# CHANGING FROM [1] to [-1] to allow getting older records
		retstring = [qString[-1]]
		if DEBUG:
			print ("###\n### NEW OLD GPS:",retstring, file=sys.stderr)
	return retstring

def getMissionDefaults():
	'''https://okeanids.mbari.org/TethysDash/api/commands/script?path=Science/altitudeServo_approach_backseat_poweronly.tl'''
	'''{"description":"Maximum duration of mission","name":"MissionTimeout","unit":"hour","value":"12"},{"description":"How often to surface for commumications","name":"NeedCommsTime","unit":"minute","value":"180"},'''
	'''MBARI specific Utility script. Not routinely used. 
	SurfacingIntervalDuringListening
	print standard defaults for the listed missions. some must have inheritance because it doesn't get them all'''
	missions=["Science/profile_station","Science/sci2","Science/mbts_sci2","Transport/keepstation","Maintenance/ballast_and_trim","Transport/keepstation_3km","Transport/transit_3km","Science/spiral_cast"]
	missions=["Science/mbts_sci2","Science/profile_station"]
	for mission in missions:
		URL = "https://{}/TethysDash/api/git/mission/{}.xml".format(servername,mission)
		print("\n#===========================\n",mission, "\n", file=sys.stderr)
		try:
			connection = urllib.request.urlopen(URL,timeout=8)
			if connection: # here?
				raw = connection.read()
				structured = json.loads(raw)
				connection.close()
				result = structured['result']
			
				print(URL, file=sys.stderr)
				try: 
					splitted = str(result).split("{")
					for item in splitted:
						print(item, file=sys.stderr)
				except KeyError:
					print("NA", file=sys.stderr)
		except urllib.error.HTTPError:
			print("# FAILED TO FIND MISSION",mission, file=sys.stderr)
			
def getNewMissionDefaults(missionn):
	Speed = None
	NCTime = None
	TimeOut = None
	Docked = False
	"""NOTE: This mission name needs the suffix!"""
	
	'''https://okeanids.mbari.org/TethysDash/api/commands/script?path=Science/altitudeServo_approach_backseat_poweronly.tl'''
	'''{"description":"Maximum duration of mission","name":"MissionTimeout","unit":"hour","value":"12"},{"description":"How often to surface for commumications","name":"NeedCommsTime","unit":"minute","value":"180"},'''
	missions=["Science/mbts_sci2.tl","Transport/keepstation.tl"]
	# TEMPORARY FOR DEBUGGING
	# missionn=missions[1]
	URL = "https://{}/TethysDash/api/commands/script?path={}".format(servername,missionn)
	if DEBUG: 
		print("\n#===========================\n",missionn, "\n", file=sys.stderr)
		print("\n#===========================\n",URL, "\n", file=sys.stderr)
	if missionn:
		try:
			connection = urllib.request.urlopen(URL,timeout=8)
			if connection: # here?
				raw = connection.read()
				structured = json.loads(raw)
				connection.close()
				try:
					result = structured['result']['scriptArgs']
				except KeyError:
					#print("\n#=Key Error in Mission Defaults=\n",missionn, VEHICLE,structured, "\n", file=sys.stderr)
					result = structured['result']['inserts'][0]['scriptArgs']
			
				# if DEBUG: 
				# 	print(result, file=sys.stderr)
				for subfield in result:
					sfn = subfield.get('name')
					if "NeedCommsTime" in sfn:
						'''needcomms expects minutes'''
						NCTime = subfield.get('value',None)
						if subfield.get('unit',0)=='hour':
							NCTime = int(NCTime)*60
						if DEBUG:
							print("FOUND NEEDCOMMS TIME in Defaults:",subfield, file=sys.stderr)
					# Mission Timeout = DockedTime plus 5 mins
					elif sfn=="DockedTime":
						TimeOut = subfield.get('value',None)
						Docked=True
						if subfield.get('unit',0)=='minute':
							TimeOut = int(TimeOut)/60
						if DEBUG:
							print("FOUND DOCKED TIME:", subfield, file=sys.stderr)				
					elif sfn=="MissionTimeout" and not Docked:
						'''Timeout expects hours'''
						TimeOut = subfield.get('value',None)
						if subfield.get('unit',0)=='minute':
							TimeOut = int(TimeOut)/60
						if DEBUG:
							print("FOUND MISSION TIMEOUT:", subfield, file=sys.stderr)
					elif sfn=="Speed":
						Speed = subfield.get('value',None)
						if DEBUG:
							print(f"FOUND SPEED IN NEW DEFAULTS {subfield}", file=sys.stderr)
				# try: 
				# 	splitted = str(result).split("{")
				# 	for item in splitted:
				# 		print(item, file=sys.stderr)
				# except KeyError:
				# 	print("NA", file=sys.stderr)
				if DEBUG: 
					print(NCTime,TimeOut,Speed, file=sys.stderr)
		except urllib.error.HTTPError:
			print("# FAILED TO FIND NEW MISSION",missionn, file=sys.stderr)
	return NCTime,TimeOut,Speed,Docked
		

	
def getNotes(starttime):
	'''get notes with #widget in the text'''
	qString = runQuery(event="note",limit="10",timeafter=starttime)
	# if DEBUG:
	# 	print("# NOTESTRING FOUND",qString, file=sys.stderr)
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

def getCommands(starttime):
	'''get commands which have been sent'''
	qString = runQuery(event="command",limit="1000",timeafter=starttime)
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
	qString = runQuery(name="GFScanner",timeafter=starttime)
	retstring = ""
	if qString:
		retstring = qString
	return retstring

def getDrop(starttime):
	qString = runQuery(name="DropWeight",limit="2000",timeafter=starttime)
	retstring = ""
	if qString:
		retstring = qString
	return retstring

	
def getComms(starttime):
	qString = runQuery(event="sbdReceive",limit="2000",timeafter=starttime)
	retstring = ""
	if qString:
		retstring = qString
	if DEBUG:
		print("# GETCOMMS\n#\nPrinting Comms SBD", len(retstring), file=sys.stderr)
		# for rec in retstring:
		#	print >> sys.stderr,  rec
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
	
	With Ahi: 2023-10-25T01:52:45.597Z,1698198765.597 Unknown==>platform_battery_voltage=15.262939 V
	look for platform_battery_charge or platform_battery_voltage
	
	WetLabsUBAT.flow_rate=0.333607 l/s
'''

	Bailout=False
	
	DataURL='https://{ser}/TethysDash/data/{vehicle}/realtime/sbdlogs/{extrapath}/shore.asc'
	volt = 0
	amp  = 0
	volttime = 0
	flowtime = 0
	flow = 999
	Tracking = []
	TrackTime = []
	allpaths =[]
	NeedTracking = True
	
	if DEBUG:
		print("# Running Old Data query...")
			
	record = runQuery(event="dataProcessed",limit="10",timeafter=starttime)
	
	if record:
		for checkpath in record:
			if not (checkpath['path'] in allpaths):
				allpaths.append(checkpath['path'])
		if DEBUG:
			print("# Found (allpaths) Data Path", allpaths,file=sys.stderr)
	else:
		if DEBUG:
			print("# No dataProcessed Path found", file=sys.stderr)
		return volt,amp,volttime,flow,flowtime,Tracking,TrackTime
	
	#moving duplicate checking above		
	# if (len(allpaths) ==3):   # get three most recent
	# 	if allpaths[0]==allpaths[1]:   # if first two are the same, drop second
	# 		z=allpaths.pop(1)
	# 	else:            # otherwise drop last one
	# 		z=allpaths.pop(2)
	
	firstlast = 0		
	
	for pathpart in allpaths[:2]:
		volt = 0
		amp  = 0
		volttime=0

		
		extrapath = pathpart
		NewURL = DataURL.format(ser=servername,vehicle=VEHICLE,extrapath=extrapath)
		if DEBUG:
			print("# DATA ASC URL",NewURL, file=sys.stderr)
		datacon = urllib.request.urlopen(NewURL,timeout=8)
		content =  datacon.read().decode('utf-8').splitlines()
		# if DEBUG:
		# 	print("# DATA content",content[:10], file=sys.stderr)
		# pull last X lines from queue. This was causing problems on some missions so increased it
		lastlines = list(deque(content))
		#lastlines = list(deque(content))
		lastlines.reverse() #in place
		# if DEBUG:
		# 	print("dimensions of lastlines",len(lastlines), file=sys.stderr)
		# 	print("# Lastlines (reversed):",lastlines[0:10], file=sys.stderr)
		# 	for li in lastlines:
		# 		if "flow" in li:
		# 			print("#",li, file=sys.stderr)
		# 
		# if DEBUG:
		# 	print("# Lastlines first):",lastlines[0], file=sys.stderr)
		# trying to avoid parsing the same part twice
		# THIS doesn't work even if the first entity is the same
		if lastlines and (firstlast == lastlines[0]):
			Bailout = True
			lastlines=[]
			break
		elif lastlines:
			firstlast = lastlines[0]
		else: # not lastlines
			Bailout = True
			lastlines=[]
			break
			

		for nextline in lastlines:
#			if DEBUG:
#				print >> sys.stderr, "#Battery nextline:",nextline.rstrip()
			if "platform_battery_" in nextline:
				if not('BPC1' in nextline):
					fields = nextline.split("=")	
					if (volt==0) and ("voltage" in nextline) and (VEHICLE!='ahi'):
						if DEBUG:
							print("# Found Data Battery Voltage",fields[2:], file=sys.stderr)
						volt     = float(fields[3].split(" ")[0])
						# in seconds not MS
					if amp == 0 and "charge" in nextline:
						if DEBUG:
							print("# Found Data Battery Charge",fields[2:], file=sys.stderr)
						amp      = float(fields[3].split(" ")[0])
						volttime = int(float(fields[0].split(',')[1].split(" ")[0])*1000)  
				else:
					# VEHICLE=='ahi' and "voltage" in nextline: # Use BPC1
					fields = nextline.split('>')[1].split("=")
					if (volt==0) and ("voltage" in nextline) and (VEHICLE=='ahi'):
						if DEBUG:
							print("\n# Found AHI Data Battery Voltage",fields, file=sys.stderr)
						volt     = float(fields[1].split(" ")[0])
						volttime = int(float(nextline.split('>')[0].split(',')[1].split(" ")[0])*1000)  
				

				
			if VEHICLE == 'pontus':
				''' Fault  UBAT flow rate is below the specified threshold of 0.05 l/s.   WetLabsUBAT'''
				'''WetLabsUBAT.flow_rate=0.333607 l/s'''
				if (flow == 999) and "WetLabsUBAT.flow_rate" in nextline:
					if DEBUG:
						print("# FLOWDATA",nextline.rstrip(), file=sys.stderr)
					flowfields = nextline.split("=")
					flow      = int(1000 * float(flowfields[-1].split(" ")[0]))
					flowtime = int(float(flowfields[0].split(',')[1].split(" ")[0])*1000)
					if DEBUG:
						print("# FLOWNUM",flow, file=sys.stderr)
					
			if ("acoustic" in mission or "CircleSample" in mission) and NeedTracking:
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
			print("#> Complete tracking:",Tracking, TrackTime, elapsed(TrackTime[0] - now), file=sys.stderr)

	return volt,amp,volttime,flow,flowtime,Tracking,TrackTime
	
def getNewUBATFlow(starttime):	
	'''Returns the most recent flow rate from the UBAT sensor'''
	'''PowerOnly.component_avgCurrent_loadControl'''
	'''https://okeanids.mbari.org/TethysDash/api/data/WetLabsUBAT.flow_rate?vehicle=pontus&from=0&maxlen=2'''
	record = runNewStyleQuery(api="data/WetLabsUBAT.flow_rate",extrastring="&from=0&maxlen=1")
	if record:
		flow = record['values'][:]
		flowtime = record['times'][:]
	else:
		flow=999
		flowtime=""
	return flow,flowtime

def ampToCat(val):
	'''convert piscivore current draw to number of cameras'''
	'''each camera draws 100, not 50, so upping ranges'''
	'''Cameras now drawing 392 ma total. upping ranges again'''
	cat = False
	ival = int(val)
	'''for piscivore, convert raw current to category'''
	if ival <=30:
		cat = 0
	elif ival < 176:
		cat = 1
	elif ival > 430:
		cat = 3
	elif ival > 175:
		cat = 2
	return cat
		



def getNewPlanktivore(starttime):	
	'''https://okeanids.mbari.org/TethysDash/api/data/_.planktivore_HM_AvgRois?vehicle=ahi&maxlen=10&from=1701196801652
	https://okeanids.mbari.org/TethysDash/api/data/_.ayeris_particle_counts?vehicle=galene&maxlen=10&from=1701196801652
	
_.ayeris_particle_counts=996.500000 count/s
{"name":"_.planktivore_HM_AvgRois","units":"count/s","values":[0.602051,0.0,0.301025,0.602051,0.0,0.0,0.301025,0.0,0.301025,0.0],"times":[1715273810966,1715273962095,1715273992123,1715274201341,1715274241384,1715274366502,1715274414547,1715274559677,1715274600716,1715274824916]}
2024-05-08T03:19:18.234Z,1715138358.234 Unknown-->_.planktivore_LM_AvgRois=2.650269 count/s
2024-05-08T03:19:39.255Z,1715138379.255 Unknown-->_.planktivore_HM_AvgRois=0.477119 count/s'''

	nowcat=-999
	origtime = False
	nowpowtime = False
	if DEBUG:
		print(f"# Plank &maxlen=10&from={starttime}", file=sys.stderr)
	record = runNewStyleQuery(api="data/_.planktivore_HM_AvgRois",extrastring=f"&maxlen=10&from={starttime}")
	'''(-ago_cellcomms / (60*1000)) > (needcomms+60):'''
	if record and nowcat < -998: #nowcat check not needed because no loop
		nowcat = ampToCat(record['values'][-1])
		nowpow = "{}".format(int(record['values'][-1])) + "ma"
		nowpowtime = record['times'][-1]
		# -1 to 15, 16-65, 66-125
		agopowtime = now - nowpowtime
		if (agopowtime / (60*1000)) > (needcomms+60):
			nowpow="Too Old"
			nowcat=5
			if DEBUG:
				print("# PowerOnly too old",elapsed(nowpowtime - now), file=sys.stderr)

		for v,t in zip(record['values'][::-1],record['times'][::-1]):
			tc = ampToCat(v)
			if tc == nowcat:
				nowpowtime = t
			else:
				break
		if DEBUG:
			print("# record",record['values'], file=sys.stderr)
			# print("# ORIGTIME",elapsed(origtime - now), file=sys.stderr)
			print("# FIRST TIME",elapsed(nowpowtime - now), file=sys.stderr)
	else:
		nowpow="PISC"
		nowpowtime=False
	return nowcat,nowpowtime,nowpow

def getNewCameraPower(starttime):	
	nowcat=-999
	origtime = False
	nowpowtime = False
	'''Returns the most recent power consumption for the piscivore cameras'''
	'''PowerOnly.component_avgCurrent_loadControl''' 
	'''https://okeanids.mbari.org/TethysDash/api/data/PowerOnly.component_avgCurrent_loadControl?vehicle=pontus
	# updated to add extra string if values are not being reported? 
	https://okeanids.mbari.org/TethysDash/api/data/PowerOnly.component_avgCurrent_loadControl?vehicle=pontus&maxlen=10&from=1701196801652'''
	if DEBUG:
		print(f"# NewPowerOnly &maxlen=10&from={starttime}", file=sys.stderr)
	record = runNewStyleQuery(api="data/PowerOnly.component_avgCurrent_loadControl",extrastring=f"&maxlen=10&from={starttime}")
	'''(-ago_cellcomms / (60*1000)) > (needcomms+60):'''
	if record and nowcat < -998: #nowcat check not needed because no loop
		nowcat = ampToCat(record['values'][-1])
		nowpow = "{}".format(int(record['values'][-1])) + "ma"
		nowpowtime = record['times'][-1]
		# -1 to 15, 16-65, 66-125
		agopowtime = now - nowpowtime
		if (agopowtime / (60*1000)) > (needcomms+60):
			nowpow="Too Old"
			nowcat=5
			if DEBUG:
				print("# PowerOnly too old",elapsed(nowpowtime - now), file=sys.stderr)

		for v,t in zip(record['values'][::-1],record['times'][::-1]):
			tc = ampToCat(v)
			if tc == nowcat:
				nowpowtime = t
			else:
				break
		if DEBUG:
			print("# record",record['values'], file=sys.stderr)
			# print("# ORIGTIME",elapsed(origtime - now), file=sys.stderr)
			print("# FIRST TIME",elapsed(nowpowtime - now), file=sys.stderr)
	else:
		nowpow="PISC"
		nowpowtime=False
	return nowcat,nowpowtime,nowpow
	
def getNewNavigating(missiontime):
	recordlist = getImportant(missiontime)
	StationLat = False
	StationLon = False
	ReachedWaypoint = False
	NavigatingTo    = False
	WaypointName = "Waypoint"
	myre  =  re.compile(r'WP ?([\d\.\-]+)[ ,]+([\d\.\-]+)')
	wayre =  re.compile(r'point: ?([\d\.\-]+)[ ,]+([\d\.\-]+)')

	
	RawWaypoints={"C1"    : "-121.847,36.797",
		"M1"    : "-122.022,36.750",
		"M2"    : "-122.375999,36.691",
		"3km"   : "-121.824326,36.806965",
		"Sta.N" : "-121.9636,36.9026",
		"Sta.S" : "-121.8934,36.6591",
		"NEreal" : "-121.900002,36.919998",
		"NE"    : "-121.9,36.9"}
	TruncatedWaypoints = {
  		"36.797,-121.847": "C1"    ,
  		"36.797,-121.850": "C1 profile",
  		"36.750,-122.022": "M1"    ,
  		"36.691,-122.376": "M2"    ,
  		"36.807,-121.824": "3km"   ,
  		"36.903,-121.964": "Sta.N" ,
  		"36.659,-121.893": "Sta.S" ,
  		"36.920,-121.900": "NE-b",
  		"36.900,-121.900": "NE",
		"36.81,-121.98": "Lower Soquel", 
		"36.77,-121.89": "Krill Shelf",
		"36.82,-121.86": "N. Spur",
		"36.712,-122.187" : "MARS",
		"36.722,-122.187" : "Canon 1N",
		"36.713,-122.176" : "Canon 1E",
		"36.704,-122.187" : "Canon 1S",
		"36.713,-122.198" : "Canon 1W",
		"36.731,-122.187" : "Canon 2N",
		"36.713,-122.165" : "Canon 2E",
		"36.695,-122.187" : "Canon 2S",
		"36.713,-122.209" : "Canon 2W",
		"36.87,-121.96" : "Upper Soquel",
		"36.903,-121.111" : "Dock Appr.",
		"36.906,-122.116" : "Dock",
		"36.910,-122.110" : "Dock",
		"37.020,-122.270" : "NW",
		"36.910,-121.900" : "East"
		}
	
	if DEBUG:
		print(f"Parsing Waypoints for current mission",file=sys.stderr)
	for Record in recordlist:
		RecordText = Record.get("text","NA")
		# This will only parse the most recent event in the queue between Reached or Nav
		if not NavigatingTo and not ReachedWaypoint: 
			if RecordText.startswith("Navigating to") and not "box" in RecordText:
				if DEBUG:
					print("## Found Navigating To Event", RecordText, file=sys.stderr)
					'''Navigating to waypoint: 36.750000,-122.022003'''
				NavRes = wayre.search(RecordText.replace("arcdeg",""))
				if NavRes:
					textlat,textlon = NavRes.groups()
					if textlat:
						StationLat = float(textlat)
						StationLon = float(textlon)
					if DEBUG:
						print("## Got LatLon from Navigating To", StationLat,StationLon, file=sys.stderr)
					NavigatingTo = Record["unixTime"]
			if RecordText.lower().startswith("reached waypoint"):
				if DEBUG:
					print("## Found Reached Event", RecordText, Record["unixTime"], file=sys.stderr)
				waresult = wayre.search(RecordText)
				if waresult:
					textlat,textlon=waresult.groups()
					if textlat:
						StationLat = float(textlat)
						StationLon = float(textlon)
				if DEBUG:
					print("## Got ReachedWaypoint", StationLat,StationLon, file=sys.stderr)
				ReachedWaypoint = Record["unixTime"]
				
			if StationLat:
				LookupLL = f"{round(StationLat,3):.3f},{round(StationLon,3):.3f}"
				if DEBUG:
					print("## Looking up Station", LookupLL, file=sys.stderr)
				
				WaypointName = TruncatedWaypoints.get(LookupLL,"Station.")  # if not found, use "Station"
	return StationLat, StationLon, ReachedWaypoint, WaypointName

def getNewNextWaypoint():
	wpq = ""
	'''https://okeanids.mbari.org/TethysDash/api/wp?vehicle=pontus
	"result": {
        "missionLatLonArgs": [
            {
                "name": "Lat",
                "value": "36.806966"
            },
            {
                "name": "Lon",
                "value": "-121.824326"
            }
        ],
        "points": [
            {
                "lat": 36.903,
                "lon": -122.113
            }
        ],
	'''
	wpq = runNewStyleQuery(api="wp")
	if DEBUG:
		print("## QUERYING FOR WAYPOINTS", file=sys.stderr)
	if not wpq:
		return None,None
	else:
		wpr = wpq.get('points',None) # (get only First result of this)
		# List will contain all the waypoints. Only use if there is only one.
		if wpr and len(wpr)==1:
			wp_lat = wpr[0].get('lat',None)
			wp_lon = wpr[0].get('lon',None)
			if DEBUG:
				print(f"WAYPOINT LAT AND LON: {wpr} \n {wp_lat} {wp_lon}",file=sys.stderr)
			return wp_lat,wp_lon
		else:
			return None,None
		
	

def getNewLatLon(starttime=1676609209829):
	'''https://okeanids.mbari.org/TethysDash/api/data/depth?vehicle=pontus&maxlen=200
	   https://okeanids.mbari.org/TethysDash/api/data/depth?vehicle=triton&maxlen=2&from=1676609209829
'''
	depthl = []
	timed = []
	choplat = []
	choplon = []
	chopt = []
	maxdepthseconds = 480

	# if we are constraining with a from statement
	howlongago = int(now - 10+maxdepthseconds*60*1000)  

	rec_lat = runNewStyleQuery(api="data/latitude_fix",extrastring=f"&maxlen=400&from={starttime}")
	rec_lon = runNewStyleQuery(api="data/longitude_fix",extrastring=f"&maxlen=400&from={starttime}")
	
	# if DEBUG:
	# 	print("# LATLON",rec_lat,rec_lon, file=sys.stderr)
	if not rec_lat:
		return choplat,choplon,False
	
	latitudes  = rec_lat['values'][:]
	longitudes = rec_lon['values'][:]
	millis = rec_lat['times'][:]
	elapse_list = [elapsed(m - now) for m in millis]

	from itertools import groupby
	llist=[k for k, g in groupby(zip(latitudes,longitudes,millis,elapse_list))]
	lat,lon,mill,elapse = zip(*llist)
	# if DEBUG:
	# 	for j in llist:
	# 		print(j, file=sys.stderr)
	bearinglist=[]
	for i in range(len(llist)-1):
		# deltadist,deltat,speedmadegood,bearing
		# distance(site,gpstime,oldsite,oldgpstime)
		bearinglist.append( (mill[i],) + distance( (lat[i+1],lon[i+1]),mill[i+1],(lat[i],lon[i]),mill[i]) )
		
	# for z in bearinglist:
	# 	print(z[0],z[3],z[4], file=sys.stderr)

	# for k in cdd:
	# 	print(f"{k};{cdd.get(k)}", file=sys.stderr)

	
	# depthl = [-0.993011,0.102385,0.065651,0.117626,0.060571,0.105122,2.669861,17.237305,28.119141,31.023926,30.093750,29.107910,0.071512,0.076593,0.081284,0.126614,0.086754,0.059008,1.560425,40.828125,1.911346,20.146484,1.978973,40.566406,2.295471,40.296875,2.434631,40.497070,1.792938,40.433594,0.143028,0.074247,1.753479,40.653320,14.269775,1.691742,39.653320,1.316193,40.268555,1.810150,18.678711,17.157227,31.187012,30.313477,28.996582,0.170383,0.097305,0.067604,0.130524,0.091835,1.672180,39.883789,1.678436,40.720703,2.512756,3.323242,40.277344,1.808563,40.340820,3.286133,2.399048,12.588135,0.106293,0.089098,0.108639,1.649902,39.648438,10.620605,1.938721,30.812012,0.092224,0.044939,0.150452,0.158268,0.080893,0.059008,0.101604,0.103167,1.726135,40.442383,8.166504,1.699158,40.311523,2.993469,2.450623,34.390625,22.701172,0.234081,0.076202,1.844910,40.644531,34.384766,34.854492,27.496094,30.463867,30.583008,28.158691,0.100822,0.126614,0.150063,0.220406]
	# millis = [1676497296190,1676497452506,1676497521881,1676497853558,1676497959418,1676497960217,1676498110631,1676498229806,1676498308178,1676498378481,1676498494060,1676500238921,1676500298712,1676500339930,1676500750518,1676501082201,1676501238954,1676501239366,1676501766221,1676501887410,1676502033260,1676502106414,1676502173458,1676502314893,1676502452638,1676502591218,1676502726162,1676502864738,1676503000918,1676503141900,1676503280473,1676503443286,1676503518242,1676503663286,1676503761056,1676503805098,1676503941247,1676504076986,1676504219634,1676504356158,1676504424433,1676504483023,1676504625626,1676504762994,1676506604327,1676506663304,1676506707348,1676507137945,1676507186970,1676507199997,1676507327348,1676507462698,1676507601282,1676507741872,1676507872787,1676507886522,1676508021049,1676508157225,1676508297401,1676508424267,1676508437599,1676508484061,1676508513148,1676508646066,1676508659573,1676508784502,1676508925910,1676509030133,1676509064074,1676509174778,1676509238600,1676509534745,1676510163866,1676510164308,1676510184145,1676510219290,1676510279217,1676510279612,1676510395234,1676510539487,1676510653418,1676510679673,1676510818271,1676510944323,1676510958462,1676511077685,1676511102317,1676511145158,1676511355273,1676511429762,1676511557810,1676511590196,1676511658837,1676511723883,1676511813189,1676513466133,1676513612535,1676513666698,1676513718046,1676513836238,1676513861722]
	timed = [(x/1000)/60 for x in millis] # in minutes
	nowmin = (now/1000)/60
	fakedepth = 10
	padded = False
	if nowmin - max(timed) > 4:
		timed = timed + [max(timed),max(timed)+2,nowmin]
		depthl = depthl + [1,fakedepth,fakedepth]
		padded = True
	md = max(timed)
	if (False):  # TESTING
		depthl = [1,1,10,10,50,50,100,100,150,150,200,200,250,250,150,150,25,25]
		millis = [10,20,30,40,50,60,70,80,100,130,150,170,190,200,250,350,400,480]
		timed = millis
	# This list is now padded so the last 3 values are placeholders 
	if (md - min(timed) > maxdepthseconds-1):		
		chopt = [x for x in timed if md - x < maxdepthseconds]
		chopd = depthl[-len(chopt):]   # last n elements
	else:
		chopt = timed
		chopd = depthl
	# if DEBUG:
	# 	for i in range(len(chopt)):
	# 		print("# Chop",i,chopt[i],hours(60000*chopt[i]), file=sys.stderr)
	return chopt,chopd,padded

def getNewROIs(starttime=1676609209829):
	'''https://okeanids.mbari.org/TethysDash/api/data/_.planktivore_HM_AvgRois?vehicle=ahi&maxlen=20
	https://okeanids.mbari.org/TethysDash/api/data/_.planktivore_LM_AvgRois?vehicle=ahi&maxlen=20
	planktivore_HM_AvgRois'''
	Ave_LM=-99
	Ave_HM=-99
	recent_LM=None
	recent_HM=None
	old_LM=None
	old_HM=None
	
	record_LM = runNewStyleQuery(api="data/_.planktivore_LM_AvgRois",extrastring=f"&maxlen=20&from={starttime}")
	record_HM = runNewStyleQuery(api="data/_.planktivore_HM_AvgRois",extrastring=f"&maxlen=20&from={starttime}")
	if record_LM:
		roi_LM    = record_LM['values'][:]
		millis_LM = record_LM['times'][:]
		Ave_LM    = sum(roi_LM)/len(roi_LM)
		recent_LM = millis_LM[-1]
		old_LM    = millis_LM[0]
		
	if record_HM:
		roi_HM    = record_HM['values'][:]
		millis_HM = record_HM['times'][:]
		Ave_HM    = sum(roi_HM)/len(roi_HM)
		recent_HM = millis_HM[-1]
		old_HM    = millis_HM[0]

	return Ave_LM,recent_LM,old_LM,Ave_HM,recent_HM,old_HM
	
def getNewDepth(starttime=1676609209829):
	'''https://okeanids.mbari.org/TethysDash/api/data/depth?vehicle=pontus&maxlen=200
	   https://okeanids.mbari.org/TethysDash/api/data/depth?vehicle=triton&maxlen=2&from=1676609209829
'''
	depthl = []
	timed = []
	chopt = []
	chopd = []
	maxdepthseconds = 480

	# if we are constraining with a from statement
	howlongago = int(now - 10+maxdepthseconds*60*1000)  

	record = runNewStyleQuery(api="data/depth",extrastring=f"&maxlen=400&from={starttime}")
	# if DEBUG:
	# 	print("# DEPTH RECORD",record, file=sys.stderr)
	if not record:
		return chopt,chopd,False
	depthl = record['values'][:]
	millis = record['times'][:]
	if DEBUG:
		print("# LENGTH DEPTH RECORD",len(millis), file=sys.stderr)
	
	# depthl = [-0.993011,0.102385,0.065651,0.117626,0.060571,0.105122,2.669861,17.237305,28.119141,31.023926,30.093750,29.107910,0.071512,0.076593,0.081284,0.126614,0.086754,0.059008,1.560425,40.828125,1.911346,20.146484,1.978973,40.566406,2.295471,40.296875,2.434631,40.497070,1.792938,40.433594,0.143028,0.074247,1.753479,40.653320,14.269775,1.691742,39.653320,1.316193,40.268555,1.810150,18.678711,17.157227,31.187012,30.313477,28.996582,0.170383,0.097305,0.067604,0.130524,0.091835,1.672180,39.883789,1.678436,40.720703,2.512756,3.323242,40.277344,1.808563,40.340820,3.286133,2.399048,12.588135,0.106293,0.089098,0.108639,1.649902,39.648438,10.620605,1.938721,30.812012,0.092224,0.044939,0.150452,0.158268,0.080893,0.059008,0.101604,0.103167,1.726135,40.442383,8.166504,1.699158,40.311523,2.993469,2.450623,34.390625,22.701172,0.234081,0.076202,1.844910,40.644531,34.384766,34.854492,27.496094,30.463867,30.583008,28.158691,0.100822,0.126614,0.150063,0.220406]
	# millis = [1676497296190,1676497452506,1676497521881,1676497853558,1676497959418,1676497960217,1676498110631,1676498229806,1676498308178,1676498378481,1676498494060,1676500238921,1676500298712,1676500339930,1676500750518,1676501082201,1676501238954,1676501239366,1676501766221,1676501887410,1676502033260,1676502106414,1676502173458,1676502314893,1676502452638,1676502591218,1676502726162,1676502864738,1676503000918,1676503141900,1676503280473,1676503443286,1676503518242,1676503663286,1676503761056,1676503805098,1676503941247,1676504076986,1676504219634,1676504356158,1676504424433,1676504483023,1676504625626,1676504762994,1676506604327,1676506663304,1676506707348,1676507137945,1676507186970,1676507199997,1676507327348,1676507462698,1676507601282,1676507741872,1676507872787,1676507886522,1676508021049,1676508157225,1676508297401,1676508424267,1676508437599,1676508484061,1676508513148,1676508646066,1676508659573,1676508784502,1676508925910,1676509030133,1676509064074,1676509174778,1676509238600,1676509534745,1676510163866,1676510164308,1676510184145,1676510219290,1676510279217,1676510279612,1676510395234,1676510539487,1676510653418,1676510679673,1676510818271,1676510944323,1676510958462,1676511077685,1676511102317,1676511145158,1676511355273,1676511429762,1676511557810,1676511590196,1676511658837,1676511723883,1676511813189,1676513466133,1676513612535,1676513666698,1676513718046,1676513836238,1676513861722]
	timed = [(x/1000)/60 for x in millis] # in minutes
	nowmin = (now/1000)/60
	fakedepth = 10
	padded = False
	if nowmin - max(timed) > 4:
		timed = timed + [max(timed),max(timed)+2,nowmin]
		depthl = depthl + [1,fakedepth,fakedepth]
		padded = True
	md = max(timed)
	if (False):  # TESTING
		depthl = [1,1,10,10,50,50,100,100,150,150,200,200,250,250,150,150,25,25]
		millis = [10,20,30,40,50,60,70,80,100,130,150,170,190,200,250,350,400,480]
		timed = millis
	# This list is now padded so the last 3 values are placeholders 
	if (md - min(timed) > maxdepthseconds-1):		
		chopt = [x for x in timed if md - x < maxdepthseconds]
		chopd = depthl[-len(chopt):]   # last n elements
	else:
		chopt = timed
		chopd = depthl
	# if DEBUG:
	# 	for i in range(len(chopt)):
	# 		print("# Chop",i,chopt[i],hours(60000*chopt[i]), file=sys.stderr)
	return chopt,chopd,padded

def getNewBattery():
	''' IBIT will show battery thresholds that could be used to determine warning colors'''
	''' GREY OUT BATTERY VALUES - cache battery values to use if new log
	 Make battery meter function of amph instead of volts (360 = 100%)
	 https://okeanids.mbari.org/TethysDash/api/data?vehicle=pontus&from={extrapath}  REPLACE WITH THIS! starttime?
	 Fields available: average_current, battery_voltage, battery_charge
	Change this to be more like the getDataAsc function. 
	Sometimes the battery_charge field can be empty, so use .get instead of []
		Battery thresholds:
	onfigSet IBIT.batteryVoltageThreshold 13 v persist;configSet IBIT.batteryCapacityThreshold 15 Ah persist
	
	Important
        IBIT.batteryVoltageThreshold=13 volt;

	Nov 2023: redo with 3 separate queries so maxlen is respected
	average_current
	battery_charge
	battery_voltage
	
	'''
	volt= 0.0
	amp = 0.0
	avgcurrent = 0.0
	volttime= 0.0
	hoursleft = -999
	daysleft = -999
	currentlist = []
	baseline = 1
	cameracurrent=-999
	cameratime = 0

	#DataURL='https://okeanids.mbari.org/TethysDash/api/data?vehicle={vehicle}'
	#extrastring=f"&maxlen=800"
	if VEHICLE != 'sim':
		VoltFields    = runNewStyleQuery(api="data/battery_voltage",extrastring="&maxlen=5")
		if DEBUG:
			print("# NEW STYLE VOLT FIELD RECORD",VoltFields, file=sys.stderr)
	
		if VoltFields:
			record = VoltFields
			volt = record['values'][-1]
			volttime = record['times'][-1]
		# Temporary removing Ahi due to error
		#if VEHICLE != 'ahi':
		if True:
			AmpFields     = runNewStyleQuery(api="data/battery_charge",extrastring="&maxlen=5")
			if AmpFields:
				record = AmpFields
				amp = record['values'][-1]
				if DEBUG:
					print("# NEW STYLE AMP RECORD",record, file=sys.stderr)
	
		CurrentFields = runNewStyleQuery(api="data/average_current",extrastring="&maxlen=7")
		if CurrentFields:
			record = CurrentFields
			currentlist = record['values'][-7:]
			if DEBUG:
				print("\n# CURRENT LIST",currentlist, file=sys.stderr)
	
			if currentlist:
				precisecurrent = sum(currentlist)/(len(currentlist)*1000)
				avgcurrent = round(precisecurrent,1)

	'''# Old strategy
	BattFields    = runNewStyleQuery(api="data")
	if BattFields:
		for record in BattFields:
			if record['name'] == 'battery_voltage':
				if DEBUG:
					print("# NEW STYLE VOLT RECORD",record, file=sys.stderr)
				volt = record['values'][-1]
			elif record['name'] == 'battery_charge':
				amp = record['values'][-1]
				volttime = record['times'][-1]
				if DEBUG:
					print("# NEW STYLE AMP RECORD",record, file=sys.stderr)
			elif record['name'] == 'average_current':
				currentlist = record['values'][-7:]
				if DEBUG:
					print("\n# CURRENT LIST",currentlist, file=sys.stderr)
	
				if currentlist:
					precisecurrent = sum(currentlist)/(len(currentlist)*1000)
					avgcurrent = round(precisecurrent,1)
			# Is this used or replaced by getNewCameraPower?
			# elif record['name'] == 'PowerOnly.component_avgCurrent_loadControl':
			# 	cameracurrent = record['values'][-1]
			# 	cameratime = record['times'][-1]
			# 	if DEBUG:
			# 		print("\n# PISCIVORE CURRENT",cameracurrent, file=sys.stderr)
	'''
	if DEBUG:
		print("# Extra New Battery",volt,amp,volttime,avgcurrent, file=sys.stderr)
		
	batterycolor = "st12"
	if amp > 0 and avgcurrent > 0.1:
		now = 1000 * time.mktime(time.localtime())
		hourssincebatt = abs((volttime-now) / (60*60*1000))
		timeinhours = ((amp-baseline)/precisecurrent)
		hoursleft = int(round(timeinhours-hourssincebatt,0))
		daysleft = round(hoursleft/24,1)
		if DEBUG:
			print("\n# RAW BATTERY HOURS:",timeinhours, file=sys.stderr)
			print(  "# HOURS SINCE BATT :",hourssincebatt, file=sys.stderr)
			print(  "# BATT HOURS REMAIN:",hoursleft, file=sys.stderr)

		# should subtract additional time since battery reported

		# cdd["text_ampago"] = elapsed(batttime-now)
		if hoursleft < 48:
			batterycolor = "st31"

		
	return volt,amp,avgcurrent,volttime,hoursleft,daysleft,batterycolor

def parseGPS(recordlist):
	if DEBUG:
		print("parseGPS",recordlist, file=sys.stderr)
	site=False
	gpstime=False
	'''[{u'eventId': 12283560, u'unixTime': 1583301462000, u'vehicleName': u'pontus', u'fix': {u'latitude': 36.757467833070464, u'date': u'Wed Mar 04 05:57:42 GMT 2020', u'longitude': -122.02584799923866}, u'eventType': u'gpsFix'},'''
	if not recordlist:
		return((False,False),False)
	site =    (recordlist[0]['fix']['latitude'],recordlist[0]['fix']['longitude'])
	gpstime = recordlist[0]['unixTime']
	return site,gpstime
	
def parseARGO(recordlist):
	if DEBUG:
		print("parseARGO",recordlist, file=sys.stderr)
	argobatt=False
	argotime=False
	'''{"result":[{"eventId":18239361,"vehicleName":"makai","unixTime":1681926395000,"isoTime":"2023-04-19T17:46:35.000Z","eventType":"argoReceive","fix":{"latitude":36.793,"longitude":-121.983,"date":"Wed Apr 19 10:46:35 PDT 2023"},"note":"B","text":"127"}]}'''
	if not recordlist:
		return(False,False)
	else:
		status =    recordlist[0].get('text','')
		if status == "127":
			argobatt = "Good"
		elif status == "255":
			argobatt = "Low"
		argotime = recordlist[0].get('unixTime',False)
		return argobatt,argotime

def parseARGO50(recordlist):
	''' Find last good ARGO battery time as well as current status '''
	# if DEBUG:
	# 	print("parseARGO50",recordlist, file=sys.stderr)
	argobatt="na"
	argogoodtime = False
	argobadtime  = False
	argotime = False
	'''{"result":[{"eventId":18239361,"vehicleName":"makai","unixTime":1681926395000,"isoTime":"2023-04-19T17:46:35.000Z","eventType":"argoReceive","fix":{"latitude":36.793,"longitude":-121.983,"date":"Wed Apr 19 10:46:35 PDT 2023"},"note":"B","text":"127"}]}'''
	if not recordlist:
		return(False,False,False)
	else:
		for r in recordlist:
			status =    r.get('text','')
			if (status == "127" and not argogoodtime):
				if DEBUG:
					print("ARGO FULL GOOD RECORD",r,file=sys.stderr)
				argogoodtime = r.get('unixTime',False)
			elif (status == "255" and not argobadtime):
				argobadtime = r.get('unixTime',False)
				if DEBUG:
					print("ARGO FULL BAD RECORD",r,file=sys.stderr)
		if argogoodtime > argobadtime:
			argobatt = "Good"
			argotime = argogoodtime
		elif argobadtime:
			argotime = argobadtime
			argobatt = "Low"
		return argobatt,argotime,argogoodtime
		
def addSparkDepth(xlist,ylist,padded=False,w=120,h=20,x0=594,y0=295,need_comm_mins=60,lastcomm=1684547199000):
	''' 
	TODO: make orange region from now back to the start of the time
	h0 362 for near the middle of the vehicle
	    h0 588 for the lower right corner 
		can manually calculate the values for data multipliers using the
		width and desired range of values.
		xrange is 480 minutes. yrange is 150 meters (or 200)
		xdivider = 480/96 = 5
		ydivider = 200/20 = 10'''
	min_to_show = 480
	dep_to_show = 40
	xdiv = min_to_show/w
	
	
	boxr = x0+w
	xmax = max(xlist)
	ymax = max(ylist)
	if ymax > dep_to_show + 5:
		dep_to_show = 80
	if ymax > dep_to_show + 5:
		dep_to_show = 120
	# COMMENTING OUT DEEP Sparklines to omit stray point.
	# if ymax > dep_to_show + 5:
	# 	dep_to_show = 160
	# if ymax > dep_to_show + 5:
	# 	dep_to_show = 240
	# if ymax > dep_to_show + 5:
	# 	dep_to_show = 320
	# if ymax > dep_to_show + 5:
	# 	dep_to_show = 640
	# if ymax > dep_to_show + 5:
	# 	dep_to_show = 1280
	# if ymax > dep_to_show + 5:
	# 	dep_to_show = 1920
	# if ymax > dep_to_show + 5:
	# 	dep_to_show = 2560
	
	
	ydiv = dep_to_show/h
	
	xplist = [(boxr-(xmax-x)/xdiv) for x in xlist]  # move from right to left
	ytrunc = [y/ydiv if y < dep_to_show else h for y in ylist]
	yplist = [y0 + y for y in ytrunc]
	
	if padded:
		# subplist = xplist[:-3]
		padplist = xplist[-3:]
		sublist = xlist[:-3]
	else:
		# subplist = xplist
		sublist = xlist
# if DEBUG:
	# 	print("xplist",xplist, file=sys.stderr)
	# 	print("yplist",yplist, file=sys.stderr)
	# 	print("ylist",ylist, file=sys.stderr)
	
	faked=10
	pliststring = ''
	for i in range(len(xplist)):
		pliststring += f"""{xplist[i]:.5f},{yplist[i]:.5f} """
	
	lp = """{},{}""".format(xplist[0],y0-0.6)

	rp = """{},{}""".format(boxr,y0-0.6)
	
	# sparkbg for gray box
	# removed point count from display
	# <text desc="sparknote" transform="matrix(1 0 0 1 {x0+w+2} {y0+10})" class="st12 st9 sparktext">{len(xlist):n} pts</text>
	
	# changed orange to be 25% more than needcomms
	if DEBUG:
		if (sublist):
			print("### SPARK TIME (minutes?)", (now-max(sublist)*60000)/(1000*60*60),file=sys.stderr)
		else:
			print("### NO DEPTH DATA sublist",file=sys.stderr)
	if sublist and (now-max(sublist)*60000)/(1000*60*60) > (1.25 * need_comm_mins/60):
		agecolor = "st27"
		padcolor = "st27" # padded values if more than an hour: orange
	elif sublist: 
		agecolor = "st25"
		padcolor = "st16"  # padded values if recent
	else: # last records are older than 8 hours
		sublist = [lastcomm/60000]
		agecolor = "st27"
		padcolor = "st27" # padded values if more than an hour: orange

	# add recent poly in orange, four points.
	if padded:
		if (not padplist) or (len(padplist)< 2):
			padpoly = f'''<polyline desc="emptysparkline" class="st27" points="{x0},{y0-0.6} {x0},{y0+faked/ydiv} {boxr - 1},{y0+faked/ydiv} {boxr},{y0+faked/ydiv} {rp}"/>'''
		else:
			padpoly = f'''<polyline desc="sparkline" class="{padcolor}" points="{padplist[0]:.5f},{y0-0.6} {padplist[0]:.5f},{y0+1/ydiv} {padplist[1]:.5f},{y0+faked/ydiv} {boxr},{y0+faked/ydiv} {rp}"/>'''
	else:
		padpoly = ''
	#,y0-0.6, boxr,(y0 + 20/ydiv),  max(xplist),(y0 + 20/ydiv),   max(xplist),y0-0.6,
	# if DEBUG:
	# 	print("### PADPOLY", padpoly,file=sys.stderr)
	# 	print("### SUBLIST", sublist,file=sys.stderr)
	#Timeago in hours
	

	polystring = '''<polygon desc="sparkpoly" class="sparkpoly" points="{lp} {ps} {rp}"/>'''.format(lp=lp,ps=pliststring,rp=rp)
	SVGbg = f'''<rect desc="sparkbox" x="{x0}" y="{y0}" class="sparkline" width="{w}" height="{h}"/>'''
	SVGbody=f'''
	<polyline desc="sparkline" class="gridline" points="{x0+w*.25},{y0} {x0+w*.25},{y0+h}"/>
	<polyline desc="sparkline" class="gridline" points="{x0+w*.50},{y0} {x0+w*.50},{y0+h}"/>
	<polyline desc="sparkline" class="gridline" points="{x0+w*.75},{y0} {x0+w*.75},{y0+h}"/>
	<polyline desc="sparkline" class="gridline" points="{x0},{y0+h*.25} {x0+w},{y0+h*.25}"/>
	<polyline desc="sparkline" class="gridline" points="{x0},{y0+h*.50} {x0+w},{y0+h*.50}"/>
	<polyline desc="sparkline" class="gridline" points="{x0},{y0+h*.75} {x0+w},{y0+h*.75}"/>
	<polyline desc="minorgrid" class="gridline" points="{x0+w*.125},{y0} {x0+w*.125},{y0+h}"/>
	<polyline desc="minorgrid" class="gridline" points="{x0+w*.375},{y0} {x0+w*.375},{y0+h}"/>
	<polyline desc="minorgrid" class="gridline" points="{x0+w*.625},{y0} {x0+w*.625},{y0+h}"/>
	<polyline desc="minorgrid" class="gridline" points="{x0+w*.875},{y0} {x0+w*.875},{y0+h}"/>
	<text desc="sparknote" transform="matrix(1 0 0 1 {x0+w+2} {y0+4})" class="st12 st9 sparktext">{hours(max(sublist)*60000)}</text>
	<text desc="sparknote" transform="matrix(1 0 0 1 {x0+w+2} {y0+10})" class="st12 st9 sparktext">{elapsed(max(sublist)*60000-now)}</text>
	
	<text desc="axislabel" transform="matrix(1 0 0 1 {x0-2+w*.25} {y0+h+5.5})" class="st12 st9 sparktext">{(1-0.25)*min_to_show/60:n}h</text>
	<text desc="axislabel" transform="matrix(1 0 0 1 {x0-2+w*.50} {y0+h+5.5})" class="st12 st9 sparktext">{(1-0.50)*min_to_show/60:n}h</text>
	<text desc="axislabel" transform="matrix(1 0 0 1 {x0-2+w*.75} {y0+h+5.5})" class="st12 st9 sparktext">{(1-0.75)*min_to_show/60:n}h</text>
	<text desc="axislabel" transform="matrix(1 0 0 1 {x0-1} {y0+h+5.5})" class="st12 st9 sparktext">{min_to_show/60:n}h</text>
	<circle desc="spr_is_old" class="{agecolor}" cx="272" cy="168" r="2"/>'''
	
	depstr = f'''<text desc="sparknote" transform="matrix(1 0 0 1 {x0+1} {y0+h-1})" class="st12 st9 sparktext">{dep_to_show:n}m</text>'''
	if DEBUG:
		print("DEPTHAGO hours",(now-max(xlist)*60000)/(1000*60*60),elapsed(max(xlist)*60000-now), file=sys.stderr)
		
	return SVGbg  + SVGbody + polystring + padpoly + depstr
  

def parseNotes(recordlist):
	'''{u'eventId': 17402257, u'unixTime': 1674066119081, u'isoTime': u'2023-01-18T18:21:59.081Z', u'note': u'#note Test of new feature.', u'state': 0, u'user': u'Steven Haddock', u'eventType': u'note', u'vehicleName': u'daphne'},'''
	Note = ''
	NoteTime = False
	if recordlist:
		for Record in recordlist:
			
			if (("#sticky" in Record["note"]) or ("#note" in Record["note"])):
				Note = Record["note"].replace("#sticky","").replace("#note","").lstrip(" :")[:55]
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

def parseCommands(recordlist):
	Soon = 0
	for Record in recordlist:
		# Expand this to check other DropWeight associated messages?
		RecordText = Record.get("text","NA")
		if "resum" in Record["text"]:
			Soon=Record["unixTime"]
	return Soon

	 
def parseCritical(recordlist):
	'''Maybe some of these are in logFault?'''
	Drop          = False
	ThrusterServo = False
	CriticalError = ""
	CriticalTime  = False
	Water         = False
	Envir         = False
	WaterLoc    = ""
	LeakLoc = ""
	
	# if DEBUG:
	#	print "### Start Recordlist"
	#	print recordlist
	#	print "### End Recordlist"
	#	# need to split this record?
	'''WATER DETECTED IN PRESSURE HULL. BURNWIRE ACTIVATED CBIT'''
	
	
	for Record in recordlist:
		RecordText = Record.get("text","NA")
		# if DEBUG:
		#	print >> sys.stderr, "# CRITICAL NAME:",Record["name"],"===> ", Record["text"]
		if Record["name"]=="DropWeight":
			Drop=Record["unixTime"]
		if RecordText.startswith("Dropped weight"):
			Drop=Record["unixTime"]
		
		"""WATER DETECTED IN PRESSURE HULL: AUX"""
		if RecordText.startswith("WATER DETECTED"):
			Water = Record["unixTime"]
			if DEBUG: 
				print("## FOUND WATER LEAK in PARSE",RecordText, file=sys.stderr)
			if not WaterLoc:
				try:
					LeakLoc = RecordText.split(":")[1].strip()
					if DEBUG: 
						print("## LEAK LOCATION",LeakLoc, file=sys.stderr)
					if LeakLoc[:3].lower() in ["aux","for","aft"]:
						WaterLoc = f" ({LeakLoc[:3].upper()})"
						if WaterLoc == " (FOR)":
							WaterLoc = " (FORE)"
				except IndexError:
					WaterLoc="-"
				
		if "environmental failure" in RecordText.lower():
			Envir = Record["unixTime"]
			
		if "burnwire activated" in RecordText.lower():
			Drop = Record["unixTime"]
			
		if (not ThrusterServo) and ("ThrusterServo" in RecordText and "Hardware Fault" in RecordText):
			ThrusterServo = Record["unixTime"]
			
		if (not CriticalError) and not RecordText.startswith("Could not open") and not Record["name"] == "NAL9602":
#		  and not "NAL9602" in RecordText and not "Hardware Fault in component" in RecordText:
			if len(RecordText)> 31:
				CriticalError = RecordText.replace(" in component","")[:29]
				if len(CriticalError)>28:
					CriticalError += "..."
			else:
				CriticalError = RecordText
			CriticalTime = Record["unixTime"]
			if DEBUG:
				print("FOUND CRITICAL >",RecordText,"\nDetails:",CriticalError, CriticalTime, elapsed(CriticalTime-now), file=sys.stderr)
			if (((now - CriticalTime)/3600000) > 6):
				CriticalError = ""
				CriticalTime = False
				if DEBUG:
					print("CRITICAL older than 6 HOURS\n    ##>",RecordText,"\n",CriticalError,
					     file=sys.stderr)
			
		# if Record["name"]=="CBIT" and Record.get("text","NA").startswith("LAST"):
	return Drop, ThrusterServo, CriticalError, CriticalTime, Water, WaterLoc, Envir

def parseFaults(recordlist):
	'''https://okeanids.mbari.org/TethysDash/api/events?vehicles=brizo&eventTypes=logFault&from=1591731032512
	Fault Lock Detect. Motor stopped spinning or could not start spinning.
	Also includes RudderServo and DVL_Micro, RDI_Pathfinder'''
	BadBattery = False
	BadBatteryText = ""
	DVLError = False
	Software = False
	Hardware = False
	Overload = False
	MotorLock = False
	WaterFault    = False
	CTDError = False
	PauseFault = False
	IgnoreOverride = False
	# Do we parse this:
	# LCB fault: LCB Watchdog Reset. Hardware Overcurrent Shutdown. Current Limiter Activated
	# if DEBUG:
	#	print "### Start Recordlist"
	#	print recordlist
	#	print "### End Recordlist"
	#	# need to split this record?
	for Record in recordlist:
		# if DEBUG:
		#	print "NAME:",Record["name"],"===> ", Record["text"]
		RT = Record.get("text","NA")
		if Record["name"]=="BPC1" and RT.startswith("Battery stick"):
			if not BadBattery > 100:
				BadBattery=Record["unixTime"]
			if DEBUG:
				print("## BAD BATTERY in FAULT", file=sys.stderr)
		'''Failed to receive data from 6 sticks prior to timeout. Missing stick IDs are: 21, 22, 48, 49, 50, 51. [BPC1]'''
		if Record["name"]=="BPC1" and not BadBatteryText and RT.startswith("Failed to receive data"):
			ma = re.search("from (\d+) sticks",RT)
			if not BadBattery > 100:
				BadBattery=Record["unixTime"]
			if ma:  
				BadBatteryText ='<text transform="matrix(1 0 0 1 286.0 245)" class="st31 st9 st24" text-anchor="end">{}x</text>'.format(ma.group(1))
			if DEBUG:
				print("## BAD STICK REPORT", RT, file=sys.stderr)
		if (not Software) and "software overcurrent" in RT.lower() or "data fault in component" in RT.lower():
			Software = Record["unixTime"]
		
		if (not Overload) and "overload error" in RT.lower():
			Overload = Record["unixTime"]
		
		# CHECK this parsefault. Used to say if "overload error" in RT, but I think that was copy/paste
		if (not PauseFault) and "paused" in RT.lower():
			PauseFault = Record["unixTime"]
			if DEBUG:
				print("## PAUSE IN FAULT REPORT", PauseFault,elapsed(PauseFault - now), file=sys.stderr)
		
		if (not Hardware) and ("thruster uart error" in RT.lower()):
			Hardware = Record["unixTime"]
			
		if (not Overload) and ("hardware overcurrent shutdown" in RT.lower()):
			Overload = Record["unixTime"]
			
		if (not CTDError) and ("Failed to acquire real or simulated CTD" in Record["text"]):
			CTDError = Record["unixTime"]
			
		if (not MotorLock) and ("motor stopped spinning" in Record["text"].lower()):
			MotorLock = Record["unixTime"]
				
		if Record["text"].upper().startswith("WATER ALARM AUX"):
			WaterFault = Record["unixTime"]
		if "Ignoring configuration overrides" in Record["text"]:
			IgnoreOverride = Record["unixTime"]
			if DEBUG: 
				print("\n\n## FOUND PERSISTED OVERRIDE",elapsed(IgnoreOverride-now), file=sys.stderr)
		# THIS ONE needs to take only the most recent DVL entry, in case it was off and now on. See other examples.
		# Water linked??
		if not DVLError and Record["name"] in ["DVL_Micro", "Waterlinked","RDI_Pathfinder","AMEcho"] and "failed" in Record.get("text","NA").lower():
			DVLError=Record["unixTime"]
	return BadBattery,BadBatteryText,DVLError,Software,Overload,Hardware,WaterFault,MotorLock,CTDError,PauseFault,IgnoreOverride

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
		#	print Record["name"],Record["text"]
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
#		if MissionTime: 
#			if Record["text"].startswith("Scheduling is paused") or Record["text"].startswith("Resuming mission and schedule"):
#				MissionTime = False
#			else:
#				break
		if Record["name"]=="MissionManager" and Record["text"].startswith("Started mission"):
			if DEBUG:
				print("\n\n## MISSION RECORD",Record, file=sys.stderr)
			MissionName = Record.get("text","mission NA").split("mission ")[1]
			MissionTime = Record["unixTime"]
			
			break
			# moved break from here. does it break the if or the for??
	return MissionName,MissionTime

def parseCBIT(recordlist):
	'''Use special query for CBIT and GF'''
	GF = False
	GFtime = False
	DVL = False
	GFLow = False
	
	'''DVL stuff  Rowe_600.loadAtStartup=1 bool
	old pontus/tethys command:
	configSet Rowe_600.loadAtStartup 0 bool persist;restart app
	"Communications Fault in component: RDI_Pathfinder"
	name column is RDI_Pathfinder for tethys: DVL failed to acquire valid data within timeout."
	
	'''
	if recordlist:
		for Record in recordlist:
			# if DEBUG:
			#	print >> sys.stderr, "# GF RECORD",Record
			RecordText = Record.get("text","NA")
			if GF == False:
				if RecordText.startswith("Ground fault detected") or RecordText.startswith("Low side ground fault detected"):
					# print "\n####\n",Record["text"]
					GF,GF_low = parseGF(RecordText)
					if "Low side" in RecordText or GF_low:
						GFLow = True
					GFtime = Record["unixTime"]
			
				elif RecordText.startswith("No ground fault"):
					GF = "OK"
					GFtime = Record["unixTime"]
			if DVL == False:
				if RecordText.startswith("Communications Fault in component: RDI_Pathfinder"):
					if DEBUG:
						print("DVL COMM ERROR", file=sys.stderr)
					#need to find turned off commands.
	else:
		GF = "NA"
	if GF == False:
		GF = "NA"
	if DEBUG:
		print(f"GF{GF},GF-LOW:{GFLow}", file=sys.stderr)

	return GF,GFtime,GFLow		
	
def parseGF(gfstring):
	GFlist = []
	GF_low = False
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
			if "GND" in Line:
				if float(Line.split(":")[1]) > 0.01:
					GF_low = True
	M=[(abs(n), (n>0)-(n<0)) for n in GFlist]
	chosen = max(M) 
	return "%.2f" % (chosen[0]*chosen[1]), GF_low

'''
Commanded speed may not show up in Important if it is default for mission
Look between load and start for all these things -- , mission Timeout etc.

Reset to default if you get a mission event before commanded speed. 
If you see a Loaded mission command, or Started default before getting speed (or Need Comms [Default 60]....)

Ground fault: Queue on RED on Low side ground fault detected - Yellow on any ground fault
...

	
'''

def parseGaleneImpt(recordlist):
	Chiton=""
	ChitonTime=0
	RedOn = ""
	WhiteOn = ""
	
	lightre = re.compile(r'MultiRay (\w+) lights (\w+)')

	for Record in recordlist:
		RecordText = Record.get("text","NA")
		if not Chiton:
			if "PowerOnly.SampleLoad1" in RecordText:
				ChitonVal = int(RecordText.replace("bool","").split("PowerOnly.SampleLoad1 ")[1].split(";")[0])
				Chiton=["OFF","ON"][ChitonVal]
				ChitonTime = Record["unixTime"]
		if not WhiteOn or not RedOn:
			if ("MultiRay" in RecordText) and ("lights" in RecordText):
				LightResult = lightre.search(RecordText)
				if not WhiteOn and "white" in RecordText:
					WhiteOn = LightResult.groups()[1]
				elif not RedOn and "red" in RecordText:
					RedOn = LightResult.groups()[1]
				if DEBUG:
					print("LED STATUS",RecordText,WhiteOn,RedOn,LightResult,file=sys.stderr)
	if DEBUG:
		print(f"In parseGalene, Chiton {Chiton},Time {ChitonTime}, Red {RedOn}, White {WhiteOn}",file=sys.stderr)
	return Chiton,ChitonTime,WhiteOn,RedOn

def parseImptMisc(recordlist,MissionN):
	'''Loads events that persist across missions'''
   #FORMER HOME OF GF SCANS
	ubatStatus = "st3"
	ubatTime = False
	ubatBool = True
	
	NeedSched = True
	Paused = False
	PauseTime=False
	
	FlowRate = False
	FlowTime = False
	
	LogTime = False
	DVL_on = False
	GotDVL = False
	
	StationLat = False
	StationLon = False
	
	CTDonCommand = False
	CTDoffCommand = False
	
	Docking = False
	DockTime = None
	DockTimeout = None
	
	voltthresh = 0
	ampthresh  = 0
	ampthreshtime = 0
	FullMission = ""
	
	DropOff = False
	
	Chiton=""
	AcousticTime=0
	RedOn = ""
	WhiteOn = ""
	
	myre  =  re.compile(r'WP ?([\d\.\-]+)[ ,]+([\d\.\-]+)')
	wayre =  re.compile(r'point: ?([\d\.\-]+)[ ,]+([\d\.\-]+)')
	missionre =  re.compile(r'Loaded ./Missions/(.+\.tl).?')
	missionrunning= re.compile(r'Running ./Missions/(.+\.tl).?')
	lightre = re.compile(r'MultiRay (\w+) lights (\w+)')
	undockre = re.compile(r'.*OnDock.DockedTime ([\d\.]+) h')
	

	# CONFIGURE DVL config defaults
	GetDVLStartup = {
		'makai':True,
		'pontus':True, 
		'tethys':True,
		'daphne':False,
		'brizo':True,
		'ahi':True,
		'galene':False,
		'triton':True,
		'opah':False, #check this!!
		'polaris':True,
		'proxima':True,
		'stella':True,
		'pyxis':True
	}
	
	DVL_on = GetDVLStartup.get(VEHICLE,False)
	# NEW get DVL from grepping (or other) out of https://okeanids.mbari.org/TethysDash/api/vconfig?vehicle=daphne

	if DEBUG:
		print(f"Parsing Important for Mission {MissionN}",file=sys.stderr)
	for Record in recordlist:
		if DEBUG:
			if "dvl" in Record["text"].lower():
				print("** ImptMisc:",Record["name"],"<-->",Record.get("text","NO TEXT FIELD"), file=sys.stderr)
				
		if not LogTime and (Record["name"] =='CommandLine' or Record["name"] =='CommandExec') and 'got command restart logs' in Record.get("text","NA"):
			LogTime = Record["unixTime"]
		
		''' DVL PARSING
		DVL potential instruments: 
			DVL_micro
			Rowe_600
			RDI_Pathfinder
			Waterlinked.loadAtStartup
			configSet AMEcho.loadAtStartup 0 bool
'''
		## RELOCATED (Duplicated) from parseMission
		RecordText = Record.get("text","NA")
		# if not ReachedWaypoint and StationLon == False and RecordText.startswith("got command set") and (".Lon " in RecordText or ".Longitude" in RecordText or ".CenterLongitude" in RecordText):
		#	if "itude" in RecordText:
		#		StationLon = RecordText.split("itude ")[1]
		#	else:
		#		StationLon = RecordText.split(".Lon ")[1]
		#	StationLon = float(StationLon.split(" ")[0])
		#	if DEBUG:
		#		print >> sys.stderr, "## Got Lon from ImptMisc", StationLon

		# if not ReachedWaypoint and StationLat == False and RecordText.startswith("got command set") and (".Lat " in RecordText or ".Latitude" in RecordText or ".CenterLatitude" in RecordText):
		#	if "itude" in RecordText:
		#		StationLat = RecordText.split("itude ")[1]
		#	else:
		#		StationLat = RecordText.split(".Lat ")[1]
		#	StationLat = float(StationLat.split(" ")[0])
		#DropWeight.loadAtStartup=0 bool;
		if not DropOff and RecordText.strip().startswith("DropWeight.loadAtStartup"):
			if DEBUG:
				print("\n## Got GOT DROPWEIGHT COMMAND", RecordText, file=sys.stderr)
			if "=0" in RecordText:
				DropOff =  Record["unixTime"]
			else:
				DropOff = 1
			
		# IBIT.batteryCapacityThreshold=20 ampere_hour;
		# IBIT.batteryVoltageThreshold=10 volt;
		if not Docking:
			if RecordText.strip().startswith("Undocking sequence complete"):
				if DEBUG:
					print("\n## Got UNDOCKING Event from ImptMisc", file=sys.stderr)
				Docking = 2
				DockTime = Record["unixTime"]
			elif RecordText.strip().startswith("Docking sequence complete"):
				if DEBUG:
					print("\n## Got DOCKING Event from ImptMisc", file=sys.stderr)
				Docking = 1
				DockTime = Record["unixTime"]
				 
		
		if not AcousticTime:
			if RecordText.strip().startswith("Ac Comms: from"):
				if DEBUG:
					print("\n## Got ACOUSTIC COMMS from ImptMisc", file=sys.stderr)
				AcousticTime = Record["unixTime"]
			

		if not voltthresh and RecordText.startswith("IBIT.batteryVoltageThreshold="):
			voltthresh = float(RecordText.split("IBIT.batteryVoltageThreshold=")[1].split(" ")[0])

			if DEBUG:
				print("## Got VoltThresh from ImptMisc", voltthresh, file=sys.stderr)
				
		if VEHICLE in ["galene","triton"]: 
			if not Chiton:
			# if "Running AyeRIS backseat app" in RecordText:
			# 	Chiton = "ON"
			# elif RecordText.startswith("got command set") and ("BackseatDriver.EnableBackseat" in RecordText):
			# 	ChitonVal = int(RecordText.replace("bool","").split("BackseatDriver.EnableBackseat")[1])
			# 	Chiton=["OFF","ON"][ChitonVal]
			# # new camera status stuff
				if "PowerOnly.SampleLoad1" in RecordText:
					ChitonVal = int(RecordText.replace("bool","").split("PowerOnly.SampleLoad1 ")[1].split(";")[0])
					Chiton=["OFF","ON"][ChitonVal]
			if not WhiteOn or not RedOn:
				if ("MultiRay" in RecordText) and ("lights" in RecordText):
					LightResult = lightre.search(RecordText)
					if not WhiteOn and "white" in RecordText:
						WhiteOn = LightResult.groups()[1]
					elif not RedOn and "red" in RecordText:
						RedOn = LightResult.groups()[1]
					if DEBUG:
						print("LED STATUS",RecordText,WhiteOn,RedOn,LightResult,file=sys.stderr)
					

		if not ampthresh and RecordText.startswith("IBIT.batteryCapacityThreshold="):
			ampthresh = round(float(RecordText.split("IBIT.batteryCapacityThreshold=")[1].split(" ")[0]))
			ampthreshtime=Record["unixTime"]
			if DEBUG:
				print("## Got AmpThresh from ImptMisc", ampthresh, elapsed(ampthreshtime-now),file=sys.stderr)

		if not FullMission and not (MissionN=="Default"):
			'''Loaded ./Missions/Transport/keepstation.tl id=keepstation'''
			if RecordText.startswith("Loaded ./Mission") or RecordText.startswith("Running ./Mission"):
				extrat="NONE"
				if DEBUG:
					print("## GETTING FULL MISSION FROM", RecordText, file=sys.stderr)
				missionresult = missionre.search(RecordText)
				if missionresult:
					FullMission = missionresult.groups()[0]
					extrat = "Loaded"
				else:
					missionresult = missionrunning.search(RecordText)
					if missionresult:
						FullMission = missionresult.groups()[0]
						extrat = "Running"
			
				if DEBUG:
					print(f"## Found FULL {extrat} Mission name {FullMission} for {MissionN}", file=sys.stderr)
		# got command schedule resume 
		# Can also have a Fault: Scheduling is paused 
		# Time for that is stored in PauseFault
		# also Scheduling was paused by a command
		# This assumes scheduler comes up running after app restart
		if not Docking and "lineCapture" in FullMission:
			if DEBUG:
				print("\n## Got DOCKING Mission but not docked", file=sys.stderr)
			Docking = 3
			DockTime = Record["unixTime"]
			
			
		#OnDock.DockedTime 11 h
		if Docking == 3 and not DockTimeout and "DockedTime" in RecordText:
			# Looking in Undock mission, but only searches for hours
			DockTimeoutResult = undockre.search(RecordText)
			if DockTimeoutResult:
				DockTimeout = float(DockTimeoutResult.groups()[0])

		if NeedSched:
			if bool(re.search('got command schedule resume|got command restart application|scheduling is resumed',RecordText.lower())):
			# if "got command schedule resume" in RecordText or "Scheduling is resumed" in RecordText:
				Paused = False
				PauseTime = Record["unixTime"]
				NeedSched = False
				if DEBUG:
					print("## Got SCHEDULE RESUME", elapsed(PauseTime-now), file=sys.stderr)
			elif bool(re.search('got command stop|got command schedule pause |scheduling is paused',RecordText.lower())) and not ('schedule clear' in RecordText) and not ('restart logs' in RecordText) and not ('ESP' in RecordText):
				Paused = True
				PauseTime = Record["unixTime"]
				NeedSched = False
				if DEBUG:
					print("## Got SCHEDULE PAUSE", elapsed(PauseTime-now), file=sys.stderr)
				
		# This will only parse the most recent event in the queue between Reached or Nav
		# if not NavigatingTo and not ReachedWaypoint: 
		# 	if Record["text"].startswith("Navigating to") and not "box" in Record["text"]:
		# 		if DEBUG:
		# 			print("## Found Navigating To Event", Record["text"], file=sys.stderr)
		# 			'''Navigating to waypoint: 36.750000,-122.022003'''
		# 		NavRes = wayre.search(Record["text"].replace("arcdeg",""))
		# 		if NavRes:
		# 			textlat,textlon = NavRes.groups()
		# 			if textlat:
		# 				StationLat = float(textlat)
		# 				StationLon = float(textlon)
		# 			if DEBUG:
		# 				print("## Got LatLon from Navigating To", StationLat,StationLon, file=sys.stderr)
		# 			NavigatingTo = Record["unixTime"]
		# 	if Record["text"].lower().startswith("reached waypoint"):
		# 		if DEBUG:
		# 			print("## Found Reached Event", Record["text"], Record["unixTime"], file=sys.stderr)
		# 		waresult = wayre.search(Record["text"])
		# 		if waresult:
		# 			textlat,textlon=waresult.groups()
		# 			if textlat:
		# 				StationLat = float(textlat)
		# 				StationLon = float(textlon)
		# 		if DEBUG:
		# 			print("## Got ReachedWaypoint", StationLat,StationLon, file=sys.stderr)
		# 		ReachedWaypoint = Record["unixTime"]
		# 		
		# 	if StationLat:
		# 		LookupLL = f"{round(StationLat,3):.3f},{round(StationLon,3):.3f}"
		# 		if DEBUG:
		# 			print("## Looking up Station", LookupLL, file=sys.stderr)
		# 		
		# 		WaypointName = TruncatedWaypoints.get(LookupLL,"Station.")  # if not found, use "Station"
			
		## TODO distinguish between UBAT off and FlowRate too low
		## PARSE UBAT (make vehicle-specific)
		## configSet AMEcho.loadAtStartup 0 bool
		## got command configSet AMEcho.enabled 1.000000 bool

		if not GotDVL and (not "(bool)" in Record.get("text","NA")) and (not "requires" in Record.get("text","NA")) and (
		      ("DVL_micro.loadAtStartup"      in Record.get("text","NA")) or 
		      ("RDI_Pathfinder.loadAtStartup" in Record.get("text","NA")) or 
		      ("AMEcho.loadAtStartup"         in Record.get("text","NA")) or 
		      ("Waterlinked.loadAtStartup"    in Record.get("text","NA")) or 
		      ("Rowe_600.loadAtStartup"       in Record.get("text","NA"))
		      ):
		    # TO CHECK. this might split incorrectly on the space because sometimes config set?
		    # configSet
		    
		    ## SHOULD ADD A CHECK FOR restart HERE TO SEE IF DVL WENT BACK TO CONFIG that will override these later events
		    
			if DEBUG: 
				print("#>> FOUND DVL: ", Record["name"] ,"===>",Record["text"], "[{}]".format(Record["unixTime"]), file=sys.stderr)
			DVL_on = bool(float(Record["text"].replace("loadAtStartup=","loadAtStartup ").split("loadAtStartup ")[1].split(" ")[0]))
			GotDVL = True
			if DEBUG: 
				print("DVL Value: ", DVL_on, file=sys.stderr)
		if not GotDVL and ("configSet AMEcho.enabled" in Record.get("text","NA")):
			DVL_on = bool(float(Record["text"].split(".enabled ")[1].split(" ")[0]))
			GotDVL = True
		
		# ADDING CTD on/off parsing
		if (not CTDonCommand and not CTDoffCommand) and ("CTD_Seabird.loadAtStartup" in Record["text"]):
			skip = False
			CTD_command = False
			try:
				CTD_command = bool(float(Record["text"].replace("loadAtStartup=","loadAtStartup ").split("loadAtStartup ")[1].split(" ")[0]))
			except ValueError:
				if DEBUG:
					print("#Error parsing CTD Command: ",VEHICLE, Record["name"] ,"==>",Record["text"],file=sys.stderr)
				skip=True
				
			if CTD_command and not skip:
				CTDonCommand = Record["unixTime"]
			elif not skip:
				CTDoffCommand = Record["unixTime"] 
	
			
		'''Change to got command ubat on  got command restart application'''
		#if VEHICLE == "pontus" and ubatTime == False and Record["name"]=="CommandLine" and "00000" in Record.get("text","NA") and "WetLabsUBAT.loadAtStartup" in Record.get("text","NA"):
		if VEHICLE == "pontus" and ubatTime == False:
			 # and (Record["name"] =='CommandLine' or Record["name"] =='CommandExec' or Record["name"] =='Important') :
			''' Changing this to default to ON unless specifically turned off'''
			'''WetLabsUBAT.loadAtStartup=0 bool'''
			if  "WetLabsUBAT.loadAtStartup" in RecordText and not "loadAtStartup (bool)" in RecordText:
				if DEBUG:
					print("## Got UBAT Load at startup", RecordText, Record["name"],file=sys.stderr)
				ubatBool = bool(float(RecordText.replace("loadAtStartup=","loadAtStartup ").split("loadAtStartup ")[1].split(" ")[0]))			
				ubatTime   = Record["unixTime"]
				
			elif  "abling UBAT" in RecordText:
				ubatBool = RecordText.startswith("Enabl")
				ubatTime   = Record["unixTime"]
	
			elif RecordText.startswith("got command ubat "):
				ubatBool = "on" in RecordText
				ubatTime   = Record["unixTime"]
				if DEBUG:
					print("## Got UBAT ON", RecordText, file=sys.stderr)
					
			# Disabling this for now	
			# elif RecordText.startswith("got command restart app") or RecordText.startswith("got command restart system") or RecordText.startswith("got command restart hardware"):
			# 	ubatBool = True
			# 	ubatTime   = Record["unixTime"]
				
			ubatStatus = ["st6","st4"][ubatBool]
	

		# THIS IS NOT CURRENTLY REPORTED	
		# if VEHICLE == "pontus" and FlowRate == False and Record["name"]=="CommandLine" and Record.get("text","NA").startswith("WetLabsUBAT.flow_rate"):
		#	FlowRate = float(Record["text"].split("WetLabsUBAT.flow_rate ")[1].split(" ")[0])
		#	FlowTime   = Record["unixTime"]

#	return ubatStatus, ubatTime, LogTime, DVL_on, GotDVL, StationLat, StationLon, ReachedWaypoint, WaypointName, CTDonCommand,CTDoffCommand,Paused,PauseTime,ampthresh,voltthresh, FullMission
	return ubatStatus, ubatTime, LogTime, DVL_on, GotDVL,CTDonCommand,CTDoffCommand,Paused,PauseTime,ampthresh,voltthresh,ampthreshtime,FullMission,Docking,DockTime,DockTimeout,Chiton,AcousticTime,DropOff,WhiteOn,RedOn

	

def parseDefaults(recordlist,mission_defaults,FullMission,MissionTime):
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
	ScheduledFresh = True
	ScheduledTime = 0
	ASAP = False
	dotcolor="st27"
	hash = "9x9x9"
	
	if DEBUG:
		print("## Parsing defaults", file=sys.stderr)
		

	for Record in recordlist:
		RecordText = Record.get("text","NA")
		
#		if DEBUG and Record["name"] != 'CBIT':
#			print >> sys.stderr, "DEFAULTNAME: ", Record["name"] ,"===>",RecordText, "[{}]".format(Record["unixTime"])
			
		## PARSE TIMEOUTS Assumes HOURS
		## NOTE / TODO: When schedule is stopped or goes to default mission and you do schedule resume, does the timeout start at zero then?
		## Widget fails to pick up duration that was set long ago in the schedule.
		# if goes to default and then resumes: got command resume 
		
		# TODO: Add DockedTime to this parsing as a sub for MissionTimeout
		if TimeoutDuration == False and \
		     ".MissionTimeout" in RecordText and RecordText.startswith("got") and not ("chedule" in RecordText):
			'''got command set profile_station.MissionTimeout 24.000000 hour'''
			'''got command set sci2.MissionTimeout 24.000000 hour'''
			TimeoutDuration = float(Record["text"].split("MissionTimeout ")[1].split(" ")[0])
			'''got command set Smear.MissionTimeout 8.000000 hour'''
			if "minute" in Record["text"]:
				TimeoutDuration = TimeoutDuration/60.0
				if DEBUG:
					print("# NOTE: Timeout given in minutes ", file=sys.stderr)
			if DEBUG:
				print("# Found TimeOut of ",TimeoutDuration, Record["text"], file=sys.stderr)
			TimeoutStart    = Record["unixTime"]
			
			"esp samples have 3h timeout"
		if DEBUG and "sched" in Record["text"]:
			print("\n#\n# MISSION: found Scheduled item", Record["text"],Record["name"],file=sys.stderr)
		# removing Started mission from schedule clear
		if RecordText.startswith('got command schedule clear'):
			Cleared = True
			if DEBUG:
				print("## Got CLEAR", file=sys.stderr)
				
		# Mission Request - sched 20230609T11
		# sched 20230609T11 "load Science/profile_station.xml;

		# removing or RecordText.startswith('got command schedule asap "set') 
		if Scheduled == False and not Cleared and (RecordText.startswith('got command schedule "run') or RecordText.startswith('got command schedule "load') or RecordText.startswith('got command schedule asap "load') or ("load" in RecordText and RecordText.startswith('got command schedule 20'))) :
			if "ASAP" in RecordText.upper():
				ASAP = True
			'''got command schedule "run " 3p78c'''
			if DEBUG:
				print("## Schedule Record ",RecordText, file=sys.stderr)

			if RecordText.startswith('got command schedule "run"') or RecordText.startswith('got command schedule "run "'):
				if DEBUG:
					print("## SCHEDULE: Looking for Hash ",VEHICLE,"-",RecordText, file=sys.stderr)
				hashre = re.compile(r'got command schedule "run ?" (\w+)')
				'''got command schedule "run " 3p78c '''
				hash_result = hashre.search(RecordText)
				if hash_result:
					hash=hash_result.group(1)
					if DEBUG:
						print("## Schedule Hash found ",hash, file=sys.stderr)
			if Scheduled and "ASAP" in RecordText.upper():
				Scheduled += ' [ASAP]'
				# Scheduled = ''  # Blanking out schedule if ASAP

			else:
			#'''got command schedule "run Science/mbts_sci2.xml"'''
			#'''## failed to parse schedule: brizo got command schedule "run" 4d401 4 4.000000'''
			#	'''got command schedule "load Science/circle_acoustic_contact.xml'''
				#Scheduled = Record["text"].split("/")[1].replace('.xml"','')
				if "/" in RecordText[:30]:
					Scheduled = Record["text"].split("/")[1].split('.')[0]
				else:
					'''got command schedule "set circle_acoustic_contact'''
					try:
						Scheduled = RecordText.split('"')[1].split(' ')[1].split('.')[0]
					except IndexError:
						print("## failed to parse schedule:",VEHICLE, RecordText, file=sys.stderr)
				if Scheduled and "ASAP" in RecordText.upper():
					Scheduled += ' [ASAP]'
					#Scheduled = ''    # Something amiss with the parsing. Blanking schedule if ASAP

				if DEBUG:
					print("## Found Scheduled in else",Scheduled, file=sys.stderr)
					
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
				print("## Found Scheduled hash",Scheduled, file=sys.stderr)
		if ScheduledFresh and Scheduled:
			ScheduledTime = Record["unixTime"]
			ScheduledFresh = False
					
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
				print("## Got Lon from mission", StationLon, file=sys.stderr)

		if StationLat == False and RecordText.startswith("got command set") and (".Lat " in RecordText or ".Latitude" in RecordText or ".CenterLatitude" in RecordText):
			if "itude" in RecordText:
				StationLat = RecordText.split("itude ")[1]
			else:
				StationLat = RecordText.split(".Lat ")[1]
			StationLat = float(StationLat.split(" ")[0])
			if DEBUG:
				print("## Got Lat from mission", StationLat, file=sys.stderr)
		
		## PARSE NEED COMMS Assumes MINUTES
		'''SurfacingIntervalDuringListening'''
		if DEBUG:
			if "SurfacingIntervalDuringListening" in RecordText:
				print("## NEEDCOMMS SURFACING", RecordText, file=sys.stderr)
		if NeedComms == False and (Record["name"]=="CommandLine" or Record["name"]=="CommandExec") and RecordText.startswith("got command") and not "chedule" in RecordText and (".NeedCommsTime" in RecordText or "NeedCommsMaxWait" in RecordText or "SurfacingIntervalDuringListening" in RecordText):
			'''    command set keepstation.NeedCommsTime 60.000000 minute	'''
			'''got command set profile_station.NeedCommsTime 20.000000 minute'''
			'''got command set trackPatchChl_yoyo.NeedCommsTimeInTransit 45.000000'''
			'''got command set trackPatch_yoyo.NeedCommsTimePatchTracking 120.000000 minute 
			; set PAM.SurfacingIntervalDuringListening 300 min
			NeedCommsTimeVeryLong
			NeedCommsMaxWait'''
			'''NeedCommsTimePatchMapping'''
			'''NeedCommsTimeMarginPatchTracking'''
			'''FrontSampling.NeedCommsTimeTransit'''
			if DEBUG:
				print("#Entering NeedComms",Record["text"], VEHICLE, NeedComms, file=sys.stderr)
			try:
				NeedComms = int(float(re.split("SurfacingIntervalDuringListening |NeedCommsTimeProfileStation |NeedCommsTimePatchMapping |NeedCommsTimeInTransect |FrontSampling.NeedCommsTimeTransit |NeedCommsTimeInTransit |NeedCommsTimeMarginPatchTracking |NeedCommsTimePatchTracking |NeedCommsMaxWait |NeedCommsTime ",Record["text"])[1].split(" ")[0]))
			except IndexError:
				try:  #This one assumes hours instead of minutes. SHOULD Code to check
					NeedComms = int(float(Record["text"].split("NeedCommsTimeVeryLong ")[1].split(" ")[0])) 
					if DEBUG:
						print("#Long NeedComms",Record["text"], VEHICLE, NeedComms, file=sys.stderr)
				except IndexError:	
					print("#NeedComms but no split",Record["text"], VEHICLE, file=sys.stderr)
			if NeedComms and "hour" in Record["text"]:
				NeedComms = NeedComms * 60
			if DEBUG and NeedComms:
				print("#FOUND NEEDCOMMS In Record zzz",NeedComms, VEHICLE, "\n" , Record["text"], file=sys.stderr)
			## ADD FLOW RATE FOR UBAT...
			
			### For the moment this will just go from the start of the mission, but once we get SatComms, use that time
			
		## PARSE UBAT (make vehicle-specific
		## PARSE SPEED # THis used to be ".Speed"
		## .ApproachSpeedNotFirstTime
		if Speed == 0 and (Record["name"] =='CommandLine' or Record["name"] =='CommandExec')  and ("set" in RecordText) and (".speedCmd" in RecordText or ".SpeedTransit" in RecordText or "ApproachSpeed" in RecordText or ".Speed " in RecordText) and (not "SpeedControl" in RecordText) and RecordText.startswith("got"):
			if (".SpeedTransit" in RecordText):
				Speed = "%.2f" % (float(Record["text"].split(".SpeedTransit")[1].strip().split(" ")[0]))
			elif (".ApproachSpeedNotFirstTime" in RecordText):
				Speed = "%.2f" % (float(Record["text"].split(".ApproachSpeedNotFirstTime")[1].strip().split(" ")[0]))
			elif (".ApproachSpeed" in RecordText):
				Speed = "%.2f" % (float(Record["text"].split(".ApproachSpeed")[1].strip().split(" ")[0]))
			elif (".Speed" in RecordText):
				Speed = "%.2f" % (float(Record["text"].split(".Speed")[1].strip().split(" ")[0]))
			else:
				try:
					Speed = "%.2f" % (float(Record["text"].split(".speedCmd")[1].strip().split(" ")[0]))
				except ValueError or IndexError:
					print("Error parsing speed for ",VEHICLE,Record["text"], file=sys.stderr)
					Speed = "na"
			
			if DEBUG:
				print("# FOUND SPEED:",Speed, file=sys.stderr)
			# Speed = "%.1f" % (float(Record["text"].split(".Speed")[1].split(" ")[0]))
	if not all([Speed,NeedComms,TimeoutDuration]):
		if DEBUG: 
			print(f"# TRYING NEW DEFAULT RETRIEVAL for {FullMission}\nSp,NeedC,Timeout:{Speed}, {NeedComms}, {TimeoutDuration}",file=sys.stderr)
			
		default_NCTime,default_TimeOut,default_Speed,default_Docked = getNewMissionDefaults(FullMission)
		
		if not Speed and default_Speed:
			# Speed = mission_defaults.get(FullMission,{}).get("Speed","na")
			Speed = float(default_Speed)
				
		if not NeedComms and default_NCTime:
			NeedComms = int(default_NCTime)
			# NeedComms = mission_defaults.get(FullMission,{}).get("NeedCommsTime",0)
			
		if not TimeoutDuration and default_TimeOut and not 'Docked' in str(default_TimeOut):
			if DEBUG:
				print(f"# NO TIMEOUT - checking defaults for {FullMission}", file=sys.stderr)
				print("# FOUND NEW TIMEOUT:",default_TimeOut, file=sys.stderr)
				
			TimeoutDuration = int(default_TimeOut)
			
			# TimeoutDuration = mission_defaults.get(FullMission,{}).get("MissionTimeout",0)
			TimeoutStart = MissionTime
			
	if NeedComms:
		dotcolor="st25"

			
	return TimeoutDuration, TimeoutStart, NeedComms,Speed,Scheduled,StationLat,StationLon,dotcolor,ScheduledTime

def handleURLerror():
	now = 1000 * time.mktime(time.localtime())
	timestring = dates(now) + " - " +hours(now)
	if Opt.savefile:
		try: 
			with open(OutPath.format(bas=basefilepath,veh=VEHICLE),'w') as outfile:
				outfile.write(svgerrorhead)
				outfile.write(svgerror.format(text_vehicle=VEHICLE,text_lastupdate=timestring))		
			print("URL ACCESS ERROR:",VEHICLE, file=sys.stderr)
		except KeyError:
			sys.exit("URL ACCESS ERROR and Key Error:"+VEHICLE)

	elif not Opt.report:
		print(svgerrorhead)
		print(svgerror.format(text_vehicle=VEHICLE,text_lastupdate=timestring))
		sys.exit("URL ACCESS ERROR:"+VEHICLE)

def makeTrackSVG(Tracking,TrackTime):
	'''<!-- tracking Up and down arrows for range increasing or decreasing -->
<polygon class="st27" points="394,300 398,308 390,308 394,300"/>
<polygon class="st25" points="394,308 398,300 390,300 394,308"/>
<circle  class="st16" cx="394" cy="304" r="3"/>
<text desc="text_track" transform="matrix(1 0 0 1 400 303)" class="st12 st9 st13">RANGE: 283m</text>
<text desc="text_trackago" transform="matrix(1 0 0 1 400 310)" class="st12 st9 st13">18h 48m ago</text>'''
	
	BaseText = '''{tr}<text desc="text_track" transform="matrix(1 0 0 1 430 308)" class="st12 st9 st13">RANGE: {ra} m</text>
<text desc="text_trackago" transform="matrix(1 0 0 1 430 315)" class="st12 st9 st13">{ti}</text>'''

	rangem=Tracking[0]
	timetext =elapsed(TrackTime[0] - now)
	if len(Tracking)>1:
		trend = Tracking[0]-Tracking[1]
		if abs(trend) < 20:
			trackshape = '<circle  class="st16" cx="424" cy="309" r="3"/>\n'
		elif trend < 0:
			trackshape = '<polygon class="st25" points="424,313 428,305 420,305 424,313"/>\n'  # "green downarrow"
		else:
			trackshape = '<polygon class="st27" points="424,305 428,313 420,313 424,305"/>\n'  # orange uparrow
	else:
		trackshape = '<circle  class="st16" cx="424" cy="309" r="3"/>\n'
	
	tracksvg = BaseText.format(tr=trackshape,ra=rangem,ti=timetext)
	
	return tracksvg	

def printhtmlutility():
	''' Print the html for the auv.html web page. (Not updated for all vehicles).'''
	
	vehicles = ["daphne","pontus","tethys","galene","sim","triton","makai"]

	for v in vehicles:
		print('''var myImageElement1 = document.getElementById('{0}');
myImageElement1.src = 'https://okeanids.mbari.org/widget/auv_{0}.svg';'''.format(v))

	for v in vehicles:
		print('''<img src="https://okeanids.mbari.org/widget/auv_{0}.svg" id="{0}" width="100%"/>'''.format(v))
	
	
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
		if days > 6:
			DurationString = "over 6 days"
		elif days > 5:
			DurationString = "over 5 days"
		elif days > 4:
			DurationString = "over 4 days"
		if rawdur < 1:
			DurationString += " ago"
		else:
			DurationString = "in " + DurationString
		return DurationString
	else:
		return "NA"

def parseDistance(site,StationLat,StationLon,knownspeed,knownbearing,gpstime):
	''' using already calculated reckoned speed, get distance and time to last waypoint'''
	if knownspeed > 0.01 and abs(site[0]) > 1:
		deltadist,deltat,speedmadegood,bearing = distance((StationLat,StationLon),3600000,site,7200000)
		if DEBUG:
			print("# StationDistance, bearing:", deltadist,bearing, file=sys.stderr)
			print("# OldBearing:", knownbearing, file=sys.stderr)
						
		if (deltadist > 0.3):			
			timetogo = deltadist / knownspeed
			return 3600000 * timetogo, deltadist
		elif abs(bearing-knownbearing) < 20:
			# heading mismatch
			return bearing,deltadist			  
			if DEBUG:									  
				print("# Station close or bearing mismatch")
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
		
def dates(unixtime,year=True):
	'''return epoch in DDmonYY string'''
	if unixtime:
		t1=time.localtime(unixtime/1000)
		if year:
			TimeString = time.strftime('%d%b%y',t1)
		else:
			TimeString = time.strftime('%d%b',t1)
		return TimeString
	else:
		return "9NaN99"


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
BadBatteryText = ""
ThrusterServo = False
dropWeight = False
gflow=False
Tracking = []
TrackTime = []
sparktext = ""
ResumeSoon = 0
lTime = None

if Opt.missions:
	'''utility to show default values for selected missions'''
	getMissionDefaults()
	sys.exit("Done")
	
### WHAT IS GOING ON HERE?

if Opt.newmissions:
	'''test retrieval of mission defaults'''
	getNewMissionDefaults("Science/mbts_sci2.tl")
	sys.exit("Done new mission test")
	
	
if Opt.inst == 'whoi':
	servername = 'lrauv.whoi.edu'
else:
	servername = 'okeanids.mbari.org'
	
if Opt.printhtml:
	'''print format of auv.html auto-refreshing file'''
	printhtmlutility()
	sys.exit("Done")
	
# TODO: If running on tethys, use '/var/www/html/widget/auv_{}.svg' as the outpath
if 'tethysdash' in os.uname()[1]:
	basefilepath  = "/var/www/html/widget"
	OutPath       = '{bas}/auv_{veh}.svg'
	StartTimePath = '{bas}/auvstats_{veh}.csv'
elif 'jellywatch' in os.uname():
	basefilepath=""
	OutPath       = '{bas}/home/jellywatch/jellywatch.org/misc/auv_{}.svg'
	StartTimePath = '{bas}/home/jellywatch/jellywatch.org/misc/auvstats_{}.csv'
else:
	basefilepath=""
	OutPath = '.{bas}/auv_{}.svg'
	StartTimePath = ".{bas}/auvstats_{}.csv" # make this .py for importing or .json?
	
# TIMEOUTS are in hours? or days?
mission_defaults = {
	"profile_station"  : {"MissionTimeout": 4,   "NeedCommsTime":60,  "Speed":1.0 },
	"portuguese_ledge" : {"MissionTimeout": 4,   "NeedCommsTime":120, "Speed":1.0 },
	"sci2"             : {"MissionTimeout": 2,   "NeedCommsTime":60,  "Speed":1.0 },
	"sci2_backseat"    : {"MissionTimeout": 2,   "NeedCommsTime":60,  "Speed":1.0 },
	"mbts_sci2"        : {"MissionTimeout": 48,  "NeedCommsTime":60,  "Speed":1.0 },
	"keepstation"      : {"MissionTimeout": 4,   "NeedCommsTime":45,  "Speed":.75 },
	"ballast_and_trim" : {"MissionTimeout": 1.5, "NeedCommsTime":45,  "Speed":0.1 },
	"keepstation_3km"  : {"MissionTimeout": 4,   "NeedCommsTime":45,  "Speed":.75 },
	"transit_3km"      : {"MissionTimeout": 1,   "NeedCommsTime":30,  "Speed":1.0 },
	"transit"          : {"MissionTimeout": 1,   "NeedCommsTime":30,  "Speed":1.0 },
	"CircleSample"     : {"MissionTimeout": 2,   "NeedCommsTime":240,  "Speed":1 },
	"circle_sample"    : {"MissionTimeout": 24,  "NeedCommsTime":240,  "Speed":1 },
	"CorkAndScrew"     : {"MissionTimeout": 20,  "NeedCommsTime":60,  "Speed":1 },
	"profile_station_backseat"   : {"MissionTimeout": 1, "NeedCommsTime":60,  "Speed":1.0 },
	"IsothermDepthSampling"      : {"MissionTimeout": 20,  "NeedCommsTime":60,  "Speed":1 },
	"location_depth_sampling"    : {"MissionTimeout": 168,  "NeedCommsTime":60,  "Speed":1 },
	"LocationDepthSampling"      : {"MissionTimeout": 168,  "NeedCommsTime":60,  "Speed":1 },
	"isotherm_depth_dampling"    : {"MissionTimeout": 20,  "NeedCommsTime":60,  "Speed":1 },
	"esp_sample_at_depth"        : {"MissionTimeout": 4,   "NeedCommsTime":180, "Speed":.7 },
	"esp_sample_station"         : {"MissionTimeout": 24,  "NeedCommsTime":45,  "Speed":1 },
	"calibrate_sparton_compass"  : {"MissionTimeout": 1,   "NeedCommsTime":60,  "Speed":1 },
	"SpartonCompassCal"          : {"MissionTimeout": 1,   "NeedCommsTime":60,  "Speed":1 },
	"spiral_cast"                : {"MissionTimeout": 3,   "NeedCommsTime":180, "Speed":1 },
	"trackPatchChl_yoyo"         : {"MissionTimeout": 24,  "NeedCommsTime":180, "Speed":1 },
	"trackPatch_yoyo"            : {"MissionTimeout": 12,  "NeedCommsTime":300, "Speed":1 },
	"FrontSampling"              : {"MissionTimeout": 12,  "NeedCommsTime":60,  "Speed":1 },
	"Smear"         		     : {"MissionTimeout": 3,   "NeedCommsTime":60,  "Speed":1 },
	"front_sampling"             : {"MissionTimeout": 12,  "NeedCommsTime":300,  "Speed":1 }, 
	"sci2_flat_and_level"        : {"MissionTimeout": 2,   "NeedCommsTime":60,  "Speed":1.0 },
	#WHOI Mission
	"altitudeServo_approach_backseat_poweronly": {"MissionTimeout": 6,   "NeedCommsTime":180,  "Speed":1.0 },
	"sci2_flat_and_level_backseat"    : {"MissionTimeout": 2,   "NeedCommsTime":60,  "Speed":1.0 }
}

#########
##
## LOAD AND PARSE EVENTS
##
now = 1000 * time.mktime(time.localtime())  # (*1000?)

startTime = getDeployment()   
# newdeploy,deployID = getNewDeployment() 
# reverting to launch instead of start, but getNewDeployment() can be a template for other new queries

if not startTime:
	if DEBUG:
		sys.exit("##  Vehicle {} has no deployments".format(VEHICLE))
	else:
		sys.exit()

recovered = getRecovery(starttime=startTime)

plugged = getPlugged(recovered)

text_note,text_noteago = parseNotes(getNotes(startTime))
if DEBUG and text_note:
	print("## CLEAN NOTE:",text_note,elapsed(text_noteago-now), file=sys.stderr)
bearing = 999
WaterCritical = False
WaterFault = False
newavgcurrent=0
batteryduration = -999
cameracurrent = -999
cameratime = False
camcat = -999
camchangetime = False
argobatt = False
padded = False
pisctext = ""
argoet=''
missiondot="st18" #next to mission: invisible
Paused = True
PauseTime = False
PauseFault = False
argogoodtime=False

DockStatus = False # 1 = on dock, 2 = undocked
DockingTime = None
DockingTimeout = None
WaypointName = "Waypoint"

# ========
# Get argo status even if vehicle not recovered
argobatt,argotime,argogoodtime = parseARGO50(getArgo50(startTime))

# determine age of last good battery time. Remove minutes if over an hour
if (argobatt == "Low" and argogoodtime):
	et = "Last good: " + elapsed(argogoodtime-argotime)
	if 'h' in et:
		et = re.sub(r'( \d+m)','',et)
	argoet = et
elif argotime:
	if argotime==argogoodtime:
		argoet=""
	else:
		et = elapsed(argogoodtime-argotime)
		if 'h' in et:
			et = re.sub(r'( \d+m)','',et)
		argoet = et

		
if DEBUG:
	print("## ARGO TIME AND LASTGOODTIME:", argobatt,argotime,argogoodtime,elapsed(argogoodtime-argotime),argoet, file=sys.stderr)

# vehicle not recovered
if (not recovered) or Opt.anyway or DEBUG:
	needcomms = 0
	critical  = getCritical(startTime)
	faults = getFaults(startTime)
	gfrecords = getCBIT(startTime)
	
	site,gpstime = parseGPS(getGPS(startTime))
	if DEBUG:
		print("## GPS: SITE:",site,gpstime, file=sys.stderr)

	oldsite,oldgpstime = parseGPS(newGetOldGPS(startTime,mylimit=2))

	if DEBUG:
		print("## FIRST OLD GPS: SITE:",oldsite,oldgpstime, file=sys.stderr)

	if gpstime - oldgpstime < (60*1000*(30)):  # less than 30 minutes difference (make this relative to needcomms)
		# Go back for another GPS fix
		if DEBUG:
			print("\n## Second GPS RECORD NOT OLD ENOUGH. Trying again", file=sys.stderr)
			
		# Change this back when Carlos fix gets incorporated
		oldsite,oldgpstime = parseGPS(newGetOldGPS(startTime,mylimit=4))
		if DEBUG:
			print("## GOT SECOND OLDER GPS:", oldsite,oldgpstime, file=sys.stderr)
		
#	argobatt,argotime = parseARGO(getArgo(startTime))
			
	# if DEBUG:
	# 	print("## ARGO TIME AND LASTGOODTIME:", argobatt,argotime,argogoodtime,elapsed(argogoodtime-argotime), file=sys.stderr)
		
	deltadist,deltat,speedmadegood,bearing = distance(site,gpstime,oldsite,oldgpstime)
	

# FULL RANGE OF RECORDS
	important = getImportant(startTime)
	querytime = 0
	# mission time is off if schedule paused (default) and resumed. Detect this and go back further?
	missionName,missionTime = parseMission(important)
	Ampthreshnum=0
	Voltthreshnum = 0
	IgnoreOverride = 0
	AmpthreshTime = 0
	DropWeightOff = -1
	
	nextLat,nextLon = getNewNextWaypoint()  # From the mission statement, in case Navigating To is not found
	#  MOVE NavLat and ReachedWaypoint to after mission time
	ubatStatus,ubatTime,logtime,DVLon,GotDVL,CTDonCommand,CTDoffCommand,Paused,PauseTime,Ampthreshnum,Voltthreshnum,AmpthreshTime,FullMission,DockStatus,DockingTime,DockingTimeout,ChitonVal,AcousticComms,DropWeightOff,WhiteLightOn,RedLightOn  = parseImptMisc(important,missionName)
	
	if DEBUG:
		print(f"## Found NEXT WAYPOINTS {nextLat,nextLon}", file=sys.stderr)

	NavLat,NavLon, ReachedWaypoint, WaypointName = getNewNavigating(missionTime-60000)
	
	if VEHICLE in ["galene","triton"] and not 'DEFAULT' in missionName:
		''' get only post-Mission log events '''
		missionImpt = getImportant(missionTime-6000)
		ChitonVal,ChitonTime,WhiteLightOn,RedLightOn=parseGaleneImpt(missionImpt)
	else:
		ChitonVal,ChitonTime,WhiteLightOn,RedLightOn = ["","","",""]
		
	if DEBUG:
		print(f"FRESH PAUSE/RESUME: {Paused}",file=sys.stderr)
		
	gf,gftime,gflow = parseCBIT(gfrecords)

	if not logtime:
		logtime = startTime
	
	if missionTime > 60000: 
		querytime = missionTime-120000
		# ONLY RECORDS AFTER MISSION ## SUBTRACT A LITTLE OFFSET?
		# CHANGING FROM CommandLine to CommandExec
		postmission = getImportant(querytime,inputname="CommandExec")
	else:
		querytime = missionTime
		postmission = ''
	
	if DEBUG:
		print("MISSION          TIME AND RAW", hours(missionTime),dates(missionTime),missionTime, file=sys.stderr)
		print("REACHED WAYPOINT TIME AND RAW", hours(ReachedWaypoint),dates(ReachedWaypoint), ReachedWaypoint, file=sys.stderr)
	
	# Do we want station from here or not?	
	# Changing missiontime to querytime (mission minus 2 minutes)
	StationLat=0
	StationLon=0
	if querytime:
		missionduration,timeoutstart,needcomms,speed,Scheduled,StationLat,StationLon,missiondot,scheduledtime  = \
				parseDefaults(postmission,mission_defaults,FullMission,querytime)
			  
	

	# Time to waypoint:
	if ReachedWaypoint > missionTime:
		waypointtime = ReachedWaypoint
		waypointdist = 0.01
	else: 
		ReachedWaypoint = False
		if nextLat and not NavLat:
			if DEBUG: 
				print("## Using mission WAYPOINT {nextLat},{nextLon} instead of Navigating to",file=sys.stderr)
			NavLat = nextLat
			NavLon = nextLon
		if abs(NavLon) > 0:
			waypointtime,waypointdist = parseDistance(site,NavLat,NavLon,speedmadegood,bearing,gpstime)
		elif abs(StationLat) > 0:
			waypointtime,waypointdist = parseDistance(site,StationLat,StationLon,speedmadegood,bearing,gpstime)
		else:
			waypointtime = -2
			waypointdist = None

			

	# stationdist,stationdeltat,speedmadegood,bearing = distance(site,gpstime,oldsite,oldgpstime)
	# Just need distance from this calc, so put in fake times or make a new function and subfunction for d
	
	
	newvolt,newamp,newavgcurrent,newvolttime,batteryduration,batterydaysleft,colorduration = getNewBattery()
	depthdepth,depthtime,sparkpad = getNewDepth(startTime)
	if VEHICLE in ["pontus","daphne","makai"]:
		camcat,camchangetime,pisctext = getNewCameraPower(startTime)
		if DEBUG:
			print("## PISCIVORE STATS:",camcat,camchangetime,pisctext, file=sys.stderr)
	
	# ADDING Ahi - Planktivore ROIs
	if VEHICLE == "ahi":
		lROI,lTime,lfTime,hROI,hTime,hfTime = getNewROIs(startTime)
		if DEBUG and lTime and lfTime and lROI:
			print(f"## AHI Regions of Interest:\n\t{elapsed(lTime-now)},{elapsed(lfTime-now)},{lROI}\n\t{elapsed(hTime-now)},{hROI}", file=sys.stderr)
		
	if DEBUG:
		print("# DURATION and timeout start", missionduration,timeoutstart, file=sys.stderr)
	#NEW BATTERY PARSING
		print("# NewBatteryData: ",newvolt,newamp,newavgcurrent,newvolttime,batteryduration, file=sys.stderr)

	#this is volt, amp, time
	volt,amphr,batttime,flowdat,flowtime,Tracking,TrackTime = getDataAsc(startTime,missionName)
	# COMMENTED this out to get battery data from the old data-file method instead of new API
	# if VEHICLE!='ahi' and newvolt>0:
	if newvolt>0:
		volt=newvolt
	if newamp>0:
		amphr=newamp
		batttime=newvolttime

	satcomms,cellcomms = parseComms(getComms(startTime))
	
	if cellcomms < AcousticComms:
		cellcomms = AcousticComms
		
	if not needcomms: 
		if DEBUG: 
			print("# No NEEDCOMS found. Using default  ", file=sys.stderr)
		needcomms = 60  #default
	
	CriticalError=False
	EnvirCritical=False
	CriticalTime=False
	WaterLoc=""
	if (critical):
		if DEBUG:
			print("# Starting CRITICAL parse  ", file=sys.stderr)
		dropWeight,ThrusterServo,CriticalError,CriticalTime,WaterCritical,WaterLoc,EnvirCritical = parseCritical(critical)
	
	if DEBUG: 
		print("## CRITICAL STATUS: ",CriticalError, file=sys.stderr)
		print("## WATER LOCATION: ",WaterLoc, file=sys.stderr)

	DVLError=False
	BadBattery=False
	SWError = False
	HWError = False
	OverloadError = False
	MotorLock = False
	CTDError = False
	PauseFault = False
	
	if faults:
		BadBattery,BadBatteryText,DVLError,SWError,OverloadError,HWError,WaterFault,MotorLock,CTDError,PauseFault,IgnoreOverride = parseFaults(faults)

	
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
	BadBatteryText = ""
	DVLError = False
	logtime = now
	startTime = now
	missionName = "Out of the water"
	CTDError = False
	padded = False
	PauseTime=9999999999999
	DropWeightOff = -1
	lTime=False
	
	
	

if Opt.report:
	print("###############\nVehicle: " ,VEHICLE.upper())
	print("Now: " ,hours(now))
	print("Epoch: ", int(now))
	# roundtime = int(now) // 100000
	# Archivename = "auv_brizo"+ "-" + str(roundtime)+".json"
	# print "Archivename: ",Archivename
	print("GroundFault: ",gf,hours(gftime))
	print("MissionDuration:    ",missionduration)
	print("TimeoutStart:",hours(timeoutstart))
	print("NeedComms:",needcomms)
	print("SatComms:",satcomms)
	print("CellComms:",cellcomms)
	ago_log = logtime - now
	print("LogRestart",hours(logtime), elapsed(ago_log), logtime)
	if VEHICLE=="pontus" and (not recovered):
		print("UBAT: ", ubatStatus, hours(ubatTime))
		print("FLOW: ",flowdat, hours(flowtime))
	print("SPEED: ",speed)  
	print("GPS",site)
	print("GPSTIme",hours(gpstime))
	print("OLDGPS",oldsite)
	print("OLDGPSTIme",hours(oldgpstime))
	  # last two points: [0] is most recent
	print("Distance:",deltadist,deltat,speedmadegood)
	print("Bearing: ",bearing)
	print("Battery: ",volt, amphr, batttime)
	print("DropWeight:",dropWeight)
	print("Thruster:  ",ThrusterServo)
	print("Mission: ",missionName,hours(missionTime))
	print("Deployed:  ", hours(startTime), dates(startTime),elapsed(startTime - now))
	if recovered and not Opt.anyway:
		print("Recovered: ",hours(recovered), elapsed(recovered - now), recovered)
		if plugged:
			print("Plugged in: ",hours(plugged))
	else:
		print("Still out there...")
	print("#####   ", VEHICLE, "######")


else:   #not opt report
	'''	
	.st0{fill:#CFDEE2;} <!-- WaveColor -->
	.st1{fill:none;stroke:#000000; }
	.st2{fill:#D4D2D2;stroke:#000000; } <!-- Vehicle Body Gray -->
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
	.stleak1orig{fill:#92c19b;} <!--orig green aux water leak-->
	.stleak1{fill:#a7fbf5;} <!--light blue aux water leak-->

	'''
	cdd={}
	
	#	these are made white with black stroke
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
	"color_ctd",
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
	"color_ot",
	"color_cartcircle",
	"color_missiondefault" ]
	for cname in colornames:
		cdd[cname] = 'st3' # white fill black stroke
	
	cdd["color_arrow"] = "st16"
	
	
	cdd["color_missiontext"] = ""  # no color = black. can make it red
	cdd["text_celllabel"]= ""
	
	# These are made invisible
	invisiblecolors=["color_bigcable",
	"color_smallcable",
	"color_cart",
	"color_cartcircle",
	"color_scheduled",
	"color_commago",
	"color_logago",
	"color_argo",
	"color_missionago",
	"color_lowgf",
	"color_highgf",
	"color_camerabody",
	"color_cameralens",
	"color_leak",
	"color_cam1",
	"color_cam2", 
	"dock_tri",
	"dock_line",
	"dock_eye",
	"dock_buoy",
	"color_ubat",
	"color_flow",
	"color_duration",
	"color_satcommstext",
	"color_nextcommstext",
	"color_timeouttext",
	"color_ampthresh",
	"color_voltthresh",
	"color_whitebeam",
	"color_redbeam",
	"color_whiteled",
	"color_redled"
]

	for cname in invisiblecolors:
		cdd[cname]='st18'
		
	# Show LEDs as off (dark gray) for galene

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
	"text_current",
	"text_batteryduration",
	"text_ampago",
	"text_cellago",
	"text_argoago",
	"text_needcomms",
	"text_gpsago",
	"text_logago",	
	"text_dvlstatus",
	"text_pauseshape",
	"text_logtime"
 ]
	
	for tname in textnames:
		cdd[tname]='na'
	cdd["text_arrow"]='90'

	# These need to be updated with the correct default thresholds
	cdd["text_voltthresh"]='13.7'
	cdd["text_ampthresh"]='50'
	
	# these should persist after recovery
	#These are made blank
	specialnames=[
	"svg_current",
	"text_vehicle","text_lastupdate","text_flowago","text_scheduled","text_arrivestation",
	"text_stationdist","text_currentdist",	"text_criticaltime","text_batteryunits",
	"text_leak","text_leakago","text_missionago","text_cameraago","text_waypoint",
	"text_criticalerror","text_camago","text_piscamp","text_argoago","text_roiago","text_LM","text_HM"]
	for tname in specialnames:
		cdd[tname]=''
	
	if DEBUG: 
		print("## CRITICAL STATUS (after cdd def) : ",CriticalError, file=sys.stderr)


	'''
	
	 _            _       
	| |_ ___   __| | ___  
	| __/ _ \ / _` |/ _ \ 
	| || (_) | (_| | (_) |
	 \__\___/ \__,_|\___/ 

	 
	 TODO: Warning: Battery Data not active. Expected only when running primaries
	 Change GPS calculation to look over a longer time scale
	 
	 '''
	versionnumber = __doc__.split('v')[1].split("-")[0].strip()
	cdd["text_version"]="v"+versionnumber
	
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
	if VEHICLE=="ahi" and lTime:
			cdd["text_roiago"] = elapsed(lTime-now)
			cdd["text_LM"] = f"{lROI:.1f}"
			cdd["text_HM"] = f"{hROI:.1f}"

	cdd["color_gf"]= "st{}".format(gfnum)
	if gf == "NA":
		cdd["text_gftime"] = "no scan"
		cdd["color_highgf"]="st18"
		cdd["color_lowgf"]="st18"
	elif gf == "OK":
		cdd["color_highgf"]="st18"
		cdd["color_lowgf"]="st18"
		ago_gftime = gftime - now 
		cdd["text_gftime"] = elapsed(ago_gftime)
	else:
		ago_gftime = gftime - now 
		cdd["text_gftime"] = elapsed(ago_gftime)
		if gflow:			
			cdd["color_highgf"]="st18"
			cdd["color_lowgf"]="st27"
			cdd["color_gf"]="st6"
		elif not recovered:
			cdd["color_highgf"]="st25"
			cdd["color_lowgf"]="st18"
			

		
	cdd["text_gf"] = gf

	###
	###   MISSION TIMEOUTS DISPLAY
	###

	# This in in hours
	# cdd["text_timeout"] = hours(timeoutstart+missionduration*3600*1000)

	cdd["text_timeout"] = hours(missionTime+missionduration*3600*1000) + " - " + elapsed((missionTime+missionduration*3600*1000) - now )
	if DockingTimeout:
		# elapsed((commreftime+needcomms*60*1000) - now)
		cdd["text_timeout"] = hours(missionTime+float(DockingTimeout)*3600*1000) + " - " + elapsed((missionTime+float(DockingTimeout)*3600*1000) - now )
		cdd["text_nextcomm"]= "Unclear - Docking"
	# cdd["text_nextcomm"] = hours(timeoutstart+needcomms*60*1000)
	else:
		cdd["text_nextcomm"] = hours(commreftime+needcomms*60*1000) + " - " + elapsed((commreftime+needcomms*60*1000) - now)
		cdd["text_needcomms"] = f"{needcomms} min"
	battsvg=""
	'''
<rect desc="cuorange" x="365.5" y="250.8" class="st27" width="4" height="21"/>
<rect desc="cuyellow" x="365.5" y="257.8" class="st26" width="4" height="14"/>
<rect desc="cugreen"  x="365.5" y="264.8" class="st25" width="4" height="7"/>'''
	if newavgcurrent > 0:
		cdd["text_current"] = newavgcurrent
		if newavgcurrent > 2.1:
			cdd['svg_current'] = '<rect desc="cuorange" x="365.5" y="250.8" class="st27" width="4" height="21"/>'
		elif newavgcurrent < 1.5:
			cdd['svg_current'] = '<rect desc="cugreen"  x="365.5" y="264.8" class="st25" width="4" height="7"/>'
		else:
			cdd['svg_current'] = '<rect desc="cuyellow" x="365.5" y="257.8" class="st26" width="4" height="14"/>'
	if DEBUG:
		print("# BATTERY REMAINING  ",batteryduration, file=sys.stderr)
	if batteryduration > -998:
		# changed duration to 2 days
		if batterydaysleft > 2:
			cdd["text_batteryduration"] = batterydaysleft
			cdd["text_batteryunits"] = "days"
		else:
			cdd["text_batteryduration"] = batteryduration
			cdd["text_batteryunits"] = "hours"
		cdd["color_duration"] = colorduration
		
	argoago = (argogoodtime-argotime)/(60*1000*60*24) 
	if DEBUG:
		print("last good argo in days:",argoago,file=sys.stderr)

	if argobatt == "Good":
		cdd["color_argo"]="st25"
	elif argobatt == "Low":
		# last good argo older than 5 days, make orange
		if argoago < -5:
			if DEBUG:
				print("OLD argo good",argoet,file=sys.stderr)
			cdd["color_argo"]="st27"
		else:
			cdd["color_argo"]="st26"
		cdd["text_argoago"] = argoet
	elif argobatt =="na":
		cdd["color_argo"]="st16" # Grey
		cdd["text_argoago"] = "NA"

		
	###
	###   MISSION OVERVIEW DISPLAY
	###

	cdd["text_vehicle"] = VEHICLE.upper()
	cdd["text_lastupdate"] = time.strftime('%H:%M')
	# Green = 5 if in defaults Lets go orange for not in
	# cdd["color_missiondefault"] = ['st27','st25'][missionName in mission_defaults] 
	cdd["color_missiondefault"] = missiondot


	# NOT USED YET! NOTES  
	# if noteTime:
	#	cdd["text_note"] = note
	#	cdd["text_notetime"] = elapsed(noteTime)
		

	
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
		cdd["text_argoago"] = argoet
		cdd["color_wavecolor"] = 'st18' # invisible
		cdd["color_arrow"]     = 'st18'
		cdd["color_dirtbox"] = 'st17'   # brown
		if plugged:
			cdd["text_missionago"]  = elapsed(plugged - now)
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
		# CriticalError = False                        # unicode bullet
		if missionName and missionTime:
			missionNameText = missionName
			if missionName == "Default":
				missionNameText = "DEFAULT"
				# minutes DEFAULT has been running
				ago_default = missionTime - now 
				# if in default more than 15 minutes, make mission name red
				defaulttextcolor = ""
				if (-ago_default / (60*1000)) > (15): 
					# 20 minutes past running
					defaulttextcolor = 'st31'
				cdd["color_missiontext"]=defaulttextcolor
		
			cdd["text_mission"]= missionNameText + " - " + hours(missionTime)+ " &#x2022; " + dates(missionTime,year=False)
			cdd["text_missionago"] = elapsed(missionTime - now)
			
		else:
			cdd["text_mission"]     = "PENDING " 
			
		if speed != 'na':
	#		if DEBUG:
	#			print >> sys.stderr, "#SPEED:",speed
			try:
				cdd["text_speed"]= speed + "m/s"
			except TypeError:
				cdd["text_speed"]= "%.2f" % speed + "m/s"
		else:
			cdd["color_thrust"] = 'st5'

		if DEBUG: 
			print("\n# COMPARING MISSION to SCHEDULED, mN,S,mT,St",missionName,Scheduled,missionTime,scheduledtime, file=sys.stderr)

		if VEHICLE == 'galene':
			cdd["color_whiteled"] = 'stledoff'
			cdd["color_redled"] = 'stledoff'
			cdd["color_cameralens"] = "st3"
			cdd["color_camerabody"] = "st11"
		# These Schedule parameters are set in parseDefaults and parseMission
		#removed this  and (missionName not in Scheduled)
		
		if Scheduled and (scheduledtime > missionTime):
			cdd["text_scheduled"] = Scheduled
			if "/" in Scheduled:
				Scheduled=Scheduled.split("/")[-1]
			cdd["color_scheduled"] = ['st27','st25'][Scheduled.replace(' [ASAP]','') in mission_defaults]   

		# MISSION TIMES
		timetotimeout =  ((missionTime+missionduration*3600*1000)  - now) / (60*1000)
	
		if DEBUG:
			print("#TIME TO MISSION TIMEOUT",timetotimeout, file=sys.stderr)

		if timetotimeout > 11:
			cdd["color_missionago"] = 'st4'
		elif timetotimeout < 1:
			cdd["color_missionago"] = 'st6'
		else:
			cdd["color_missionago"] = 'st5'

		# This is typically in minutes

		# CIRCLE NEXT TO COMM TIME in minutes
		# TODO: Add orange here.
		timetocomm = int(((commreftime+needcomms*60*1000) -now) / (60*1000))
		if DEBUG:
			print("#TIME TO COMM",timetocomm, file=sys.stderr)
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
		if (now - gpstime > 3600000*3):   # greater than 3 hours old.
			cdd["color_gps"] = 'st6'
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

		cdd["text_waypoint"] = "Arrive at " + WaypointName
		if DEBUG and (waypointtime >= 0):
			print("TIME TO STATION from GPS TIME, not now:",hours(waypointtime),elapsed(waypointtime), file=sys.stderr)
		if ReachedWaypoint > missionTime:
			arrivetext = f"Arrived: {WaypointName}"
			cdd["text_stationdist"]   = elapsed(waypointtime - now)

		elif (waypointdist) and (waypointtime == -1 or waypointdist < 0.4):
			if waypointdist:
				arrivetext = f"On {WaypointName} %.1f km" % waypointdist
			else:
				arrivetext = f"At {WaypointName}" 
		elif waypointtime == -2:
			arrivetext = "Nav missing"
		# Cheating by storing heading in waypointtime if mismatch in function
		elif waypointtime and waypointtime < 361:
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
			cdd["color_ubat"] = 'st3'
			cdd["color_flow"] = 'st3'
			if (flowdat < 999) and (ubatStatus=="st4"):
				if ((290 < flowdat) and (flowdat < 500)):
					cdd["color_flow"]= 'st4'
				elif (224 < flowdat):
					cdd["color_flow"]= 'st5'
				else:
					cdd["color_flow"]= 'st6'

			if flowtime:
				cdd["text_flowago"] = elapsed(flowtime-now)
			else:
				cdd["text_flowago"]=""

			cdd["color_ubat"] = ubatStatus
			
		else:
			cdd["color_ubat"] = 'st18'
			cdd["color_flow"] = 'st18'
		
		if AcousticComms:
			cdd["text_celllabel"] = "ACOUSTIC"
		else:
			cdd["text_celllabel"] = "Cell comms"
	
		# PARSE PISCIVORE CAMERA
		if VEHICLE in ["pontus","daphne","makai"]:	
			cdd["text_piscamp"]=pisctext
			# parse piscivore camera
			'''{text_camago}{color_cam1}{color_cam2} 2=gray, 3 white, 4 green 6 orange 11 dark gray'''
					
			if (camcat < 998) and (camcat > -1):
				if camchangetime:
					cdd["text_camago"] = elapsed(camchangetime-now)
				else:
					cdd["text_camago"]=""	
		
				if (camcat==5): #Too old data
					cdd["color_cam1"]= 'st6'
					cdd["color_cam2"]= 'st6'
				elif (camcat == 2): # two cameras on
					cdd["color_cam1"]= 'st4'
					cdd["color_cam2"]= 'st4'
				elif (camcat == 1):  # (one camera on)
					cdd["color_cam1"]= 'st4'
					cdd["color_cam2"]= 'st11'
				elif camcat == 0:  # no cameras on
					cdd["color_cam1"]= 'st11'
					cdd["color_cam2"]= 'st11'
				elif camcat == 3: # current > 200
					cdd["color_cam1"]= 'st6'
					cdd["color_cam2"]= 'st6'
					
					

			else: 
				cdd["text_camago"] = ""
				cdd["color_cam1"] = "st3"
				cdd["color_cam2"] = "st3"

		
		# THIS camera is not being used anymore
		# calanus: Running AyeRIS backseat app
		
		if VEHICLE == 'galene':
			if ChitonVal=="ON":
				cdd["text_cameraago"] = "ON " # + cdd["text_missionago"]
				cdd["color_camerabody"] = "st4"
			elif ChitonVal == "OFF":
				cdd["color_camerabody"] = "st3"
				cdd["text_cameraago"] = "OFF" # + cdd["text_missionago"]
			if WhiteLightOn == "ON":
				cdd["color_whiteled"]="whiteled"
				cdd["color_whitebeam"]="whitebeam"
			elif WhiteLightOn == "OFF":
				cdd["color_whiteled"]="stledoff" # dark gray
				cdd["color_whitebeam"]="st18" # invisible
			if RedLightOn == "ON":
				cdd["color_redled"]="redled"
				cdd["color_redbeam"]="redbeam"
			elif RedLightOn == "OFF":
				cdd["color_redled"]="stledoff" # dark gray
				cdd["color_redbeam"]="st18" # invisible
			
				
		# ubatTime TO ADD?
		

		###
		###   SPARKLINE for DEPTH DISPLAY
		###
		if depthdepth:
			#h0 362 for near the middle of the vehicle
			#h0 588 for the lower right corner 
			#x0=362,y0=295)
			#x0=308,y0=295)
			# Takes data from the getNewData function
			if DEBUG:
				print("# COMMREFTIME: ", commreftime, file=sys.stderr)
				print("# NOW: ", now, file=sys.stderr)
				#print("# SPARKINFO: ",depthtime,sparkpad, file=sys.stderr)
			sparktext = addSparkDepth(depthdepth,depthtime,padded=sparkpad,x0=131,y0=166,need_comm_mins = needcomms,lastcomm=commreftime)

		###
		###   SAT COMM DISPLAY
		###
		ago_satcomms = satcomms - now 
		cdd["text_commago"] = elapsed(ago_satcomms)
		cdd["text_sat"] = hours(satcomms)
		
		agolog = logtime - now
		cdd["text_logago"] = elapsed(agolog)
		cdd["text_logtime"] = hours(logtime)
		
		logcolor='st4'
		if (-agolog / (60*60*1000)) > 24: # hours since new log
			logcolor = 'st5'
		if (-agolog / (60*60*1000)) > 48:
			logcolor = 'st6'
		cdd["color_logago"] = logcolor
		
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
	
		satcommtextcolor = ""
		# minutes since satcomms
		if (-ago_satcomms / (60*1000)) > (needcomms+60) and (-ago_cellcomms / (60*1000)) > (needcomms+60): 
			# 60 minutes past needcomms
			satcommtextcolor = 'st31'
		cdd["color_satcommstext"]=satcommtextcolor
		
		
		nextcommtextcolor = ""
		timeouttextcolor = ""
		#commreftime = ms of last comm
		timeoutoverdue = (missionTime + missionduration*3600*1000) - now # (?? DURATION IS IN Hours??)
		commoverdue    = (commreftime + needcomms*60*1000) - now
		if -commoverdue / (60*1000) > 45:
			nextcommtextcolor = 'st31'
		if -timeoutoverdue / (60*1000) > 45:
			timeouttextcolor = 'st31'
		if DEBUG:
			print("COMM-OVERDUE: " ,commoverdue/(60*1000), file=sys.stderr)
			print("TIMEOUT-OVERDUE: " ,timeoutoverdue/(60*1000), file=sys.stderr)

		cdd["color_nextcommstext"] = nextcommtextcolor # no color = black
		cdd["color_timeouttext"] = timeouttextcolor # no color = black

		### BATTERY INFO
	
		cdd["color_wavecolor"] = 'st0'
		cdd["color_dirtbox"] = 'st18'

	
		if batttime:
	#		if DEBUG:
			#	print >> sys.stderr, "#BATTTIME", batttime
			cdd["text_ampago"] = elapsed(batttime-now)
		else:
			cdd["text_flowago"]=""
	

		cdd["text_volts"]= "%.1f" % volt
		cdd["text_amps"]= "%.1f" % amphr 

		voltnum=int(4 + 1*(volt<15) + 1*(volt<14.2))

		if BadBattery > 100: # this is the unixtine
			if DEBUG:
				print("# BAD BATTERY:",elapsed(BadBattery), file=sys.stderr)
			LowBattColor='st6'
		else:
			LowBattColor='st11'

		if volt > 0:
			cdd["color_amps"]  = "st{}".format(voltnum)  # change this to independent amp range 360-170
			# Changed to be more relevant to 13.7 v
			cdd["color_volts"] = "st{}".format(voltnum)
			cdd["color_bat1"] = ['st4',LowBattColor][volt < 13.0]
			cdd["color_bat2"] = ['st4',LowBattColor][volt < 13.71]
			cdd["color_bat3"] = ['st4',LowBattColor][volt < 14.0]
			cdd["color_bat4"] = ['st4',LowBattColor][volt < 14.5]
			cdd["color_bat5"] = ['st4',LowBattColor][volt < 15.0]
			cdd["color_bat6"] = ['st4',LowBattColor][volt < 15.5]
			cdd["color_bat7"] = ['st4',LowBattColor][volt < 16.0]
			cdd["color_bat8"] = ['st4',LowBattColor][volt < 16.5]

		#
		# Find battery thresholds for critical errors
		#
		cdd["color_ampthresh"] = "st12"
		cdd["color_voltthresh"] = "st12"
		
			
		if Ampthreshnum:
			cdd["text_ampthresh"] = f"{Ampthreshnum}"
			cdd["color_ampthresh"] = ['st12','st31'][amphr - Ampthreshnum < 5]
		
		if Voltthreshnum:
			cdd["text_voltthresh"] = f"{Voltthreshnum:.1f}"
			cdd["color_voltthresh"] = ['st12','st31'][volt - Voltthreshnum < 1.0]
		
		# IgnoreOverride is a time that an ignoring persisted message came through
		# If it is more recent than the Amp thresh then they are back to default.
		# Make them red
		if IgnoreOverride > AmpthreshTime:
			if DEBUG:
				print("THRESHOLD OVERRIDE: " ,(now-IgnoreOverride)/3600000, file=sys.stderr)
			cdd["text_voltthresh"]='13.7'
			cdd["text_ampthresh"]='50'
			cdd["color_voltthresh"] = ['st31']
			cdd["color_ampthresh"] = ['st31']


		if DEBUG and SWError:
			print("SOFTWARE ERROR: " ,(now-SWError)/3600000, file=sys.stderr)
		
		# Ignore SW errors more than 4 hours old	
		if (SWError and ((now - SWError)/3600000 < 4)):
			cdd["color_sw"] = 'st5'

		if (HWError and ((now - HWError)/3600000 < 4)):
			cdd["color_hw"] = 'st5'
			
		if (OverloadError and ((now - OverloadError)/3600000 < 4)):
			cdd["color_ot"] = 'st6'
			
		if (CTDError and not CTDoffCommand and ((now - CTDError)/3600000 < 4)):
			cdd["color_ctd"] = 'st6'
			
		elif CTDoffCommand:
			cdd["color_ctd"] = 'st5'
		else:
			cdd["color_ctd"] = 'st4'
		
		#DVL Error times out after 6 h
		if DVLError and ((now - DVLError)/3600000 < 6) and not GotDVL:
			DVLcolor = 'st6'
			cdd["text_dvlstatus"]="ERROR"
		elif DVLon:
			DVLcolor = 'st4'
			cdd["text_dvlstatus"]="ON"
		else:
			DVLcolor = 'st5'
			cdd["text_dvlstatus"]="OFF"

		if DEBUG: 
			print("## CRITICAL STATUS (after before text_ ) : ",CriticalError, file=sys.stderr)

		if CriticalError:
			if DEBUG: 
				print("## HAVE CRITICAL in RENDER: ",CriticalError, file=sys.stderr)
			cdd["text_criticalerror"] = "CRITICAL: "+ CriticalError
			cdd["text_criticaltime"]  = elapsed(CriticalTime-now)
		else:
			if DEBUG: 
				print("## NO CRITICAL ERROR in RENDER: ",CriticalError, file=sys.stderr)
	
		# else:
		# 	CriticalTime = 0
		
		cdd["color_dvl"] = DVLcolor
		
		if (WaterCritical):
			if DEBUG: 
				print("## FOUND WATER LEAK in RENDER",WaterLoc, file=sys.stderr)

			if "AUX" in WaterLoc:
				cdd["color_leak"] = "stleak1"
			else:
				cdd["color_leak"] = "stleak2"
			cdd["text_leak"] = "CRITICAL LEAK"+ WaterLoc + ":"
			cdd["text_leakago"] = elapsed(WaterCritical-now)
			
		elif (EnvirCritical):
			cdd["color_leak"] = "stleak2"
			cdd["text_leak"] = "ENVIRON. FAIL: "
			cdd["text_leakago"] = elapsed(EnvirCritical-now)

		elif (WaterFault):
			cdd["color_leak"] = "stleak1"
			cdd["text_leak"] = "AUX LEAK: "
			cdd["text_leakago"] = elapsed(WaterFault-now)
		
		if DockStatus ==1:  # Docked
			cdd["dock_buoy"]="st4"
			cdd["dock_line"]="stbuoyline"
			cdd["dock_eye"]="st3"
			cdd["dock_tri"]="st11"
			cdd["text_arrivestation"] = "On Dock"
			if DockingTime:
				cdd["text_waypoint"]= "Docked "+ elapsed(DockingTime-now)
		elif DockStatus ==3: # Trying to dock
			cdd["dock_buoy"]="st5"
			cdd["dock_line"]="stbuoyline"
			cdd["dock_eye"]="st3"
			cdd["dock_tri"]="st11"
			cdd["text_arrivestation"] = "Dock no Comms"
			if DockingTimeout:
				cdd["text_arrivestation"]= "Expect " + elapsed((missionTime+float(DockingTimeout)*3600*1000) - now )
			if DockingTime:
				cdd["text_waypoint"]= "Try started "+ elapsed(DockingTime-now)		
		elif DockStatus ==2: # Undocked
			cdd["dock_buoy"]="semitrans"
			cdd["dock_line"]="semitransline"
			cdd["dock_eye"] ="semitrans"
			cdd["dock_tri"] ="semitrans"
			if cdd["text_arrivestation"] == "Nav missing":
				cdd["text_arrivestation"] = "Undocked " + elapsed(DockingTime-now)

		# If there was a critical since the last schedule pause or schedule resume event, 
		# then the schedule is effectively paused.
		if DEBUG:
			print("\n### CRITICAL PAUSED ###  \nComparing Critical {}; to Pause {}; Paused {}; and PauseFault {}".format(CriticalTime,PauseTime,Paused,PauseFault),file=sys.stderr)
			
		# PauseTime starts as 9999+
		# Trying again with Faults and Criticals coming after UnPausing
		if not Paused: 
			if ((PauseTime < CriticalTime) or (PauseTime < PauseFault)):
				Paused=True
		
		if Paused:
			ResumeSoon = parseCommands(getCommands(PauseTime-100000))
			# if a resume command has been sent but not ack, then show pausesoon shape
			if DEBUG:
				print("#RESUMESOON INFO: ", PauseTime, ResumeSoon, file=sys.stderr)

			if PauseTime and (ResumeSoon > PauseTime):
				cdd["text_pauseshape"] = '''<text desc="pausedtext" transform="matrix(1 0 0 1 409 196)" class="st12 st9 st13">SCHEDULE:</text><g transform="translate(110 155.5)">
	<path class="purpleline" d="M347.4,37c0.1,0.1,0.1,0.3,0.1,0.5c0.1,0.5,0.1,1,0,1.5c-0.3,1.2-1.2,2.1-2.4,2.4c-0.5,0.1-1,0.1-1.5,0
	c-1.2-0.3-2.1-1.2-2.4-2.4c-0.1-0.5-0.1-1,0-1.5c0.3-1.2,1.2-2.1,2.4-2.4c0.4-0.1,0.9-0.1,1.3,0"/>
<polygon class="purplefill" points="343.9,33.2 344.6,36.8 349,34.8 "/></g>
		'''
			else:
				'''draw orange pause button'''
				if DEBUG:
					print("#PAUSED INFO: ", PauseTime, CriticalTime, file=sys.stderr)
				cdd["text_pauseshape"] = '''<text desc="pausedtext" transform="matrix(1 0 0 1 409 196)" class="st12 st9 st13">SCHEDULE:</text>
	<rect x="450" y="189" class="st27" width="8.2" height="8.2"/>
	<rect x="452" y="190.6" width="1.3" height="5"/>
	<rect x="455" y="190.6" width="1.3" height="5"/>
	'''
		else:
			cdd["text_pauseshape"] ='''<text desc="pausedtext" transform="matrix(1 0 0 1 409 196)" class="st12 st9 st13">SCHEDULE:</text>
	<rect x="450" y="189" class="st25" width="8.2" height="8.2"/> 
	<polygon class="stwhite" points="452,190 452,196 456.5,193"/>'''


		if DEBUG:
			print("#Speed and textspeed ", speed, cdd["text_speed"], file=sys.stderr)
		if (ThrusterServo>100) and ((now - ThrusterServo)/3600000 < 4):
			cdd["color_thrust"] = 'st6'
		else:
			cdd["color_thrust"] = 'st4'
			
		if speed == 'na':
			cdd["color_thrust"] = 'st5'
		
		if MotorLock and ((now - MotorLock)/3600000 < 1):
			cdd["color_thrust"] = 'st6'


		cdd["color_drop"] = ['st4','st6'][(dropWeight>1)]
		# if time for dropweight alert is older than the dropweight having been turned off
		if dropWeight < DropWeightOff:
			cdd["color_drop"] = 'st11'
			if DropWeightOff > 100:
				cdd["text_droptime"] = "OFF: " + elapsed(DropWeightOff-now)
		elif dropWeight > 100:
			cdd["text_droptime"] = elapsed(dropWeight-now)
		else:
			cdd["text_droptime"] =""
			
			

	# print "Launched:  ", hours(startTime)  
	# if recovered:
	#	print "Recovered: ",hours(recovered)

	if Opt.savefile:
		if DEBUG:
			print("#Saving file ", OutPath.format(bas=basefilepath,veh=VEHICLE), file=sys.stderr)
		with open(OutPath.format(bas=basefilepath,veh=VEHICLE),'w') as outfile:
			outfile.write(svghead)
			outfile.write(svgtext.format(**cdd))
			if text_note:
				outfile.write(svgstickynote.format(text_note=text_note,text_noteago=elapsed(text_noteago - now)))
			if BadBattery > 100:
				outfile.write(svgbadbattery.format(badcelltext=BadBatteryText))
			outfile.write(sparktext)
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
				if VEHICLE in ["pontus","daphne","makai"]:
					if (camcat < 998) and (camcat > -1):
						outfile.write(svgpiscivore.format(
							color_cam1  = cdd["color_cam1"],
							color_cam2  = cdd["color_cam2"],
							text_camago = cdd["text_camago"], 
							text_piscamp= cdd["text_piscamp"])
						)
				if VEHICLE == "ahi":
					# Trying pre-formatted
					outfile.write(svg_planktivore.format(
						text_LM = cdd["text_LM"],
						text_HM = cdd["text_HM"],
						text_roiago = cdd["text_roiago"]
					))
						
				if VEHICLE=="galene":
					outfile.write(svggalene)
			outfile.write(svgtail)
			
		#adding JSON version of cdd state dictionary
		with open(OutPath.format(bas=basefilepath,veh=VEHICLE).replace(".svg",".json"),'w') as jsonfile:
			jsonfile.write(json.dumps(cdd))

		if not recovered:
			''' Save file with time stamp of epoch seconds truncated by //100
				e.g., auv_daphne-16560980.json
			    1656098268.236587   
				16560980
				To retrieve, take unixtime //100'''
			roundtime = int(now) // 100000
			Archivename = "{bas}/archive/auv_{veh}".format(bas=basefilepath, veh=VEHICLE) +  "-"  +  str(roundtime) + ".json"	
			with open(Archivename,'w') as archivefile:
				archivefile.write(json.dumps(cdd))
				
			ArchiveImage = False
			
			if ArchiveImage:
				ArchiveImage = "{bas}/archive/auv_{veh}".format(bas=basefilepath,veh=VEHICLE) +  "-"  +  str(roundtime) + ".svg"	
				if DEBUG:
					print("Archiving file:",ArchiveImage,file=sys.stderr)
				with open(ArchiveImage,'w') as outfile:
					outfile.write(svghead)
					outfile.write(svgtext.format(**cdd))
					if text_note:
						outfile.write(svgstickynote.format(text_note=text_note,text_noteago=elapsed(text_noteago - now)))
					if BadBattery > 100:
						outfile.write(svgbadbattery.format(badcelltext=BadBatteryText))
					outfile.write(sparktext)
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
		print(svghead)
		print(svgtext.format(**cdd))   # insert values from dictionary by name
		if BadBattery:
			print(svgbadbattery.format(badcelltext=BadBatteryText))
		if text_note:
			print(svgstickynote.format(text_note=text_note,text_noteago=elapsed(text_noteago - now)))
		if len(Tracking)>=1:
			print(makeTrackSVG(Tracking,TrackTime))
		if not recovered:
			print(svglabels)
			if VEHICLE=="pontus":
				print(svgpontus)
		print(sparktext)
		print(svgtail)