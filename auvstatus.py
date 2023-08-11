#! /usr/bin/env python3
# -*- coding: utf-8 -*-
'''
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
from LRAUV_svg import svgtext,svghead,svgpontus,svggalene,svgbadbattery,svgtail,svglabels,svgerror,svgerrorhead,svgwaterleak,svgstickynote,svgpiscivore   # define the svg text?
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

	if not timeafter:
		timeafter="1234567890123"
		
	BaseQuery = "https://{ser}/TethysDash/api/events?vehicles={v}{e}{n}{tm}{l}&from={t}"
	URL = BaseQuery.format(ser=servername,v=vehicle,e=event,n=name,tm=match,l=limit_str,t=timeafter)
	
	if DEBUG:
		print("### QUERY:",URL, file=sys.stderr)

	try:
		connection = urllib.request.urlopen(URL,timeout=5)		
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
		connection = urllib.request.urlopen(URL,timeout=5)		
		if connection:
			datastream = connection.read()
			result = unpackJSON(datastream)
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
		print("###\n### RUNNING ARGO LIMIT 1 starttime:",starttime, file=sys.stderr)
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
		retstring = [qString[1]]
		if DEBUG:
			print ("###\n### NEW OLD GPS:",retstring, file=sys.stderr)
	return retstring

def getMissionDefaults():
	'''MBARI specific Utility script. Not routinely used. 
	print standard defaults for the listed missions. some must have inheritance because it doesn't get them all'''
	missions=["Science/profile_station","Science/sci2","Science/mbts_sci2","Transport/keepstation","Maintenance/ballast_and_trim","Transport/keepstation_3km","Transport/transit_3km","Science/spiral_cast"]
	missions=["Science/mbts_sci2","Science/profile_station"]
	for mission in missions:
		URL = "https://{}/TethysDash/api/git/mission/{}.xml".format(servername,mission)
		print("\n#===========================\n",mission, "\n", file=sys.stderr)
		try:
			connection = urllib.request.urlopen(URL,timeout=5)
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

	record = runQuery(event="dataProcessed",limit="3",timeafter=starttime)
	
	for checkpath in record:
		allpaths.append(checkpath['path'])
		
	if (len(allpaths) ==3):   # get three most recent
		if allpaths[0]==allpaths[1]:   # if first two are the same, drop second
			z=allpaths.pop(1)
		else:            # otherwise drop last one
			z=allpaths.pop(2)
	
	firstlast = 0		
	
	for pathpart in allpaths:
		volt = 0
		amp  = 0
		volttime=0

		
		extrapath = pathpart
		NewURL = DataURL.format(ser=servername,vehicle=VEHICLE,extrapath=extrapath)
		if DEBUG:
			print("# DATA NewURL",NewURL, file=sys.stderr)
		datacon = urllib.request.urlopen(NewURL,timeout=5)
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
	cat = False
	ival = int(val)
	'''for piscivore, convert raw current to category'''
	if ival <=30:
		cat = 0
	elif ival < 125:
		cat = 1
	elif ival > 250:
		cat = 3
	elif ival > 125:
		cat = 2
	return cat
		
def getNewCameraPower(starttime):	
	nowcat=-999
	origtime = False
	nowpowtime = False
	'''Returns the most recent power consumption for the piscivore cameras'''
	'''PowerOnly.component_avgCurrent_loadControl'''
	'''https://okeanids.mbari.org/TethysDash/api/data/PowerOnly.component_avgCurrent_loadControl?vehicle=pontus&from=0&maxlen=2'''
	record = runNewStyleQuery(api="data/PowerOnly.component_avgCurrent_loadControl",extrastring="")
	if record and nowcat < -998:
		nowcat = ampToCat(record['values'][-1])
		nowpowtime = record['times'][-1]
		# -1 to 15, 16-65, 66-125
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
		nowpow=999
		nowpowtime=False
	return nowcat,nowpowtime
	
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

	'''
	volt= 0.0
	amp = 0.0
	avgcurrent = 0.0
	volttime= 0.0
	hoursleft = -999
	currentlist = []
	baseline = 1
	cameracurrent=-999
	cameratime = 0

	#DataURL='https://okeanids.mbari.org/TethysDash/api/data?vehicle={vehicle}'
	
	BattFields = runNewStyleQuery(api="data")
	if BattFields:
		for record in BattFields:
			if record['name'] == 'battery_voltage':
				# if DEBUG:
				# 	print("# VOLT RECORD",record, file=sys.stderr)
				volt = record['values'][-1]
				volttime = record['times'][-1]
			elif record['name'] == 'battery_charge':
				amp = record['values'][-1]
			elif record['name'] == 'average_current':
				currentlist = record['values'][-7:]
				if DEBUG:
					print("\n# CURRENT LIST",currentlist, file=sys.stderr)
	
				if currentlist:
					precisecurrent = sum(currentlist)/(len(currentlist)*1000)
					avgcurrent = round(precisecurrent,1)
			# elif record['name'] == 'PowerOnly.component_avgCurrent_loadControl':
	# 			cameracurrent = record['values'][-1]
	# 			cameratime = record['times'][-1]
	# 			if DEBUG:
	# 				print("\n# PISCIVORE CURRENT",cameracurrent, file=sys.stderr)
	if DEBUG:
		print("# New Battery",volt,amp,volttime,avgcurrent, file=sys.stderr)
	batterycolor = "st12"
	if amp > 0 and avgcurrent > 0.1:
		hoursleft = int(round((amp-baseline)/precisecurrent,0))
		if hoursleft < 48:
			batterycolor = "st31"

		
	return volt,amp,avgcurrent,volttime,hoursleft,batterycolor

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
		return argobatt,gpstime


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
	if ymax > dep_to_show + 10:
		dep_to_show = 120
	if ymax > dep_to_show + 10:
		dep_to_show = 160
	if ymax > dep_to_show + 10:
		dep_to_show = 240
	
	
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
		print("### SPARK TIME (minutes?)", (now-max(sublist)*60000)/(1000*60*60),file=sys.stderr)
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
	 
def parseCritical(recordlist):
	'''Maybe some of these are in logFault?'''
	Drop          = False
	ThrusterServo = False
	CriticalError = ""
	CriticalTime  = False
	Water         = False
	
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
			
		if RecordText.startswith("WATER DETECTED"):
			Water = Record["unixTime"]
			
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
			CriticalTime = Record["unixTime"]
			if DEBUG:
				print(RecordText,"\n",CriticalError, (now-CriticalTime)/3600000, file=sys.stderr)
			if (((now - CriticalTime)/3600000) > 6):
				CriticalError = ""
				CriticalTime = False
			
		# if Record["name"]=="CBIT" and Record.get("text","NA").startswith("LAST"):
	return Drop, ThrusterServo, CriticalError, CriticalTime, Water

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
		if (not Software) and "software overcurrent" in Record["text"].lower():
			Software = Record["unixTime"]
		
		if (not Overload) and "overload error" in Record["text"].lower():
			Overload = Record["unixTime"]
		
		if (not Hardware) and ("thruster uart error" in Record["text"].lower()):
			Hardware = Record["unixTime"]
		
		if (not CTDError) and ("Failed to acquire real or simulated CTD" in Record["text"]):
			CTDError = Record["unixTime"]
			
		if (not MotorLock) and ("motor stopped spinning" in Record["text"].lower()):
			MotorLock = Record["unixTime"]
				
		if Record["text"].upper().startswith("WATER ALARM AUX"):
			WaterFault = Record["unixTime"]
		
		# THIS ONE needs to take only the most recent DVL entry, in case it was off and now on. See other examples.

		if not DVLError and Record["name"] in ["DVL_Micro", "RDI_Pathfinder","AMEcho"] and "failed" in Record.get("text","NA").lower():
			DVLError=Record["unixTime"]
	return BadBattery,BadBatteryText,DVLError,Software,Overload,Hardware,WaterFault,MotorLock,CTDError

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
def parseImptMisc(recordlist):
	'''Loads events that persist across missions'''
   #FORMER HOME OF GF SCANS
	ubatStatus = "st3"
	ubatTime = False
	ubatBool = True
	
	NeedSched = True
	Paused = True
	
	FlowRate = False
	FlowTime = False
	
	LogTime = False
	DVL_on = False
	GotDVL = False
	
	StationLat = False
	StationLon = False
	
	CTDonCommand = False
	CTDoffCommand = False
	
	myre  =  re.compile(r'WP ?([\d\.\-]+)[ ,]+([\d\.\-]+)')
	wayre =  re.compile(r'point: ?([\d\.\-]+)[ ,]+([\d\.\-]+)')

	ReachedWaypoint = False
	NavigatingTo    = False
	WaypointName = "Waypoint"
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
		"36.87,-121.96" : "Upper Soquel" 
		}

	# CONFIGURE DVL config defaults
	GetDVLStartup = {
		'makai':True,
		'pontus':True, 
		'tethys':True,
		'daphne':False,
		'brizo':True,
		'galene':False,
		'polaris':True,
		'proxima':True,
		'stella':True,
		'pyxis':True
	}
	
	DVL_on = GetDVLStartup.get(VEHICLE,False)
	# NEW get DVL from grepping (or other) out of https://okeanids.mbari.org/TethysDash/api/vconfig?vehicle=daphne
	
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
		
		
		
		
		# got command schedule resume 
		# Can also have a Fault: Scheduling is paused
		# also Scheduling was paused by a command
		if NeedSched:
			if "got command schedule resume" in RecordText or "Scheduling is resumed" in RecordText:
				Paused = False
				PauseTime = Record["unixTime"]
				NeedSched = False
				if DEBUG:
					print("## Got SCHEDULE RESUME", elapsed(now-PauseTime), file=sys.stderr)
			elif bool(re.search('stop|got command schedule pause|restart |scheduling is paused',RecordText.lower())) and not ('schedule clear' in RecordText) and not ('restart logs' in RecordText) and not ('ESP' in RecordText):
				Paused = True
				PauseTime = Record["unixTime"]
				NeedSched = False
		
		# This will only parse the most recent event in the queue between Reached or Nav
		if not NavigatingTo and not ReachedWaypoint: 
			if Record["text"].startswith("Navigating to") and not "box" in Record["text"]:
				if DEBUG:
					print("## Found Navigating To Event", Record["text"], file=sys.stderr)
					'''Navigating to waypoint: 36.750000,-122.022003'''
				NavRes = wayre.search(Record["text"].replace("arcdeg",""))
				if NavRes:
					textlat,textlon = NavRes.groups()
					if textlat:
						StationLat = float(textlat)
						StationLon = float(textlon)
					if DEBUG:
						print("## Got LatLon from Navigating To", StationLat,StationLon, file=sys.stderr)
					NavigatingTo = Record["unixTime"]
			if Record["text"].lower().startswith("reached waypoint"):
				if DEBUG:
					print("## Found Reached Event", Record["text"], file=sys.stderr)
				waresult = wayre.search(Record["text"])
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
			CTD_command = bool(float(Record["text"].replace("loadAtStartup=","loadAtStartup ").split("loadAtStartup ")[1].split(" ")[0]))
			if CTD_command:
				CTDonCommand = Record["unixTime"]
			else:
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

	return ubatStatus, ubatTime, LogTime, DVL_on, GotDVL, StationLat, StationLon, ReachedWaypoint, WaypointName, CTDonCommand,CTDoffCommand,Paused
	

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
	ASAP = False
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
		
		if TimeoutDuration == False and \
		     ".MissionTimeout" in RecordText and RecordText.startswith("got") and not ("chedule" in RecordText):
			'''got command set profile_station.MissionTimeout 24.000000 hour'''
			'''got command set sci2.MissionTimeout 24.000000 hour'''
			TimeoutDuration = int(float(Record["text"].split("MissionTimeout ")[1].split(" ")[0]))
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
			print("\n#\n# MISSION: found Scheduled mission", Record["text"],Record["name"],"\n#\n#",file=sys.stderr)
		if RecordText.startswith("Started mission") or RecordText.startswith('got command schedule clear'):
			Cleared = True
			if DEBUG:
				print("## Got CLEAR", file=sys.stderr)
				
		# Mission Request - sched 20230609T11
		# sched 20230609T11 "load Science/profile_station.xml;

		
		if Scheduled == False and not Cleared and (RecordText.startswith('got command schedule "run') or RecordText.startswith('got command schedule "load') or RecordText.startswith('got command schedule asap "set')) :
			if "ASAP" in RecordText.upper():
				ASAP = True
			'''got command schedule "run " 3p78c'''
			if DEBUG:
				print("## Schedule Record ",RecordText, file=sys.stderr)

			if RecordText.startswith('got command schedule "run"') or RecordText.startswith('got command schedule "run "'):
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
			#	'''got command schedule "load Science/circle_acoustic_contact.xml'''
				#Scheduled = Record["text"].split("/")[1].replace('.xml"','')
				if "/" in RecordText[:30]:
					Scheduled = Record["text"].split("/")[1].split('.')[0]
				else:
					'''got command schedule "set circle_acoustic_contact'''
					Scheduled = RecordText.split('"')[1].split(' ')[1].split('.')[0]
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
		if NeedComms == False and (Record["name"]=="CommandLine" or Record["name"]=="CommandExec") and RecordText.startswith("got command") and not "chedule" in RecordText and ".NeedCommsTime" in RecordText:
			'''    command set keepstation.NeedCommsTime 60.000000 minute	'''
			'''got command set profile_station.NeedCommsTime 20.000000 minute'''
			'''got command set trackPatchChl_yoyo.NeedCommsTimeInTransit 45.000000'''
			'''got command set trackPatch_yoyo.NeedCommsTimePatchTracking 120.000000 minute 
			NeedCommsTimeVeryLong'''
			'''NeedCommsTimePatchMapping'''
			'''NeedCommsTimeMarginPatchTracking'''
			'''FrontSampling.NeedCommsTimeTransit'''
			if DEBUG:
				print("#Entering NeedComms",Record["text"], VEHICLE, NeedComms, file=sys.stderr)
			try:
				NeedComms = int(float(re.split("NeedCommsTime |NeedCommsTimePatchMapping |NeedCommsTimeInTransect |FrontSampling.NeedCommsTimeTransit |NeedCommsTimeInTransit |NeedCommsTimeMarginPatchTracking |NeedCommsTimePatchTracking ",Record["text"])[1].split(" ")[0]))
			except IndexError:
				try:  #This one assumes hours instead of minutes. SHOULD Code to check
					NeedComms = int(float(Record["text"].split("NeedCommsTimeVeryLong ")[1].split(" ")[0])) 
					if DEBUG:
						print("#Long NeedComms",Record["text"], VEHICLE, NeedComms, file=sys.stderr)
				except IndexError:	
					print("#NeedComms but no split",Record["text"], VEHICLE, file=sys.stderr)
			if NeedComms and "hour" in Record["text"]:
				NeedComms = NeedComms * 60
			if DEBUG:
				print("#FOUND NEEDCOMMS",NeedComms, VEHICLE, file=sys.stderr)
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
					print("Error parsing speed",Record["text"], file=sys.stderr)
					Speed = "na"
			
			if DEBUG:
				print("# FOUND SPEED:",Speed, file=sys.stderr)
			# Speed = "%.1f" % (float(Record["text"].split(".Speed")[1].split(" ")[0]))
		
	if not Speed:
			Speed = mission_defaults.get(MissionName,{}).get("Speed","na")
	if not NeedComms:
			NeedComms = mission_defaults.get(MissionName,{}).get("NeedCommsTime",0)
	if not TimeoutDuration:
			if DEBUG:
				print("# NO TIMEOUT - checking defaults", file=sys.stderr)
			
			TimeoutDuration = mission_defaults.get(MissionName,{}).get("MissionTimeout",0)
			TimeoutStart = MissionTime
	
			
	return TimeoutDuration, TimeoutStart, NeedComms,Speed,Scheduled,StationLat,StationLon

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
	'''<!-- tracking -->
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
	''' Print the html for the auv.html web page'''
	
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
		if days > 4:
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
		
def dates(unixtime):
	'''return epoch in DDmonYY string'''
	if unixtime:
		t1=time.localtime(unixtime/1000)
		TimeString = time.strftime('%d%b%y',t1)
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

if Opt.missions:
	'''utility to show default values for selected missions'''
	getMissionDefaults()
	sys.exit("Done")

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
Paused = True
PauseTime = False
WaypointName = "Waypoint"


# vehicle not recovered
if (not recovered) or Opt.anyway or DEBUG:
	critical  = getCritical(startTime)
	faults = getFaults(startTime)
	gfrecords = getCBIT(startTime)
	
	site,gpstime = parseGPS(getGPS(startTime))
	if DEBUG:
		print("## GPS: SITE:",site,gpstime, file=sys.stderr)

	oldsite,oldgpstime = parseGPS(newGetOldGPS(startTime,mylimit=2))
	if DEBUG:
		print("## PREVIOUS GPS: SITE:",oldsite,oldgpstime, file=sys.stderr)
		
	argobatt,argotime = parseARGO(getArgo(startTime))
		
	deltadist,deltat,speedmadegood,bearing = distance(site,gpstime,oldsite,oldgpstime)

# FULL RANGE OF RECORDS
	important = getImportant(startTime)

	# mission time is off if schedule paused (default) and resumed. Detect this and go back further?
	missionName,missionTime = parseMission(important)
	
	ubatStatus,ubatTime,logtime,DVLon,GotDVL,NavLat,NavLon,ReachedWaypoint,WaypointName,CTDonCommand,CTDoffCommand,Paused  = parseImptMisc(important)
	
	gf,gftime,gflow = parseCBIT(gfrecords)

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
		print("MISSION TIME AND RAW", hours(missionTime),dates(missionTime),missionTime, file=sys.stderr)
		
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
	
	
	newvolt,newamp,newavgcurrent,newvolttime,batteryduration,colorduration = getNewBattery()
	depthdepth,depthtime,sparkpad = getNewDepth(startTime)
	if VEHICLE == "pontus":
		camcat,camchangetime = getNewCameraPower(startTime)

	if DEBUG:
		print("# DURATION and timeout start", missionduration,timeoutstart, file=sys.stderr)
	#NEW BATTERY PARSING
		print("# NewBatteryData: ",newvolt,newamp,newavgcurrent,newvolttime,batteryduration, file=sys.stderr)

	#this is volt, amp, time
	volt,amphr,batttime,flowdat,flowtime,Tracking,TrackTime = getDataAsc(startTime,missionName)
	volt=newvolt
	amphr=newamp
	batttime=newvolttime

	satcomms,cellcomms = parseComms(getComms(startTime))

	if not needcomms: 
		needcomms = 60  #default
	
	CriticalError=False
	if (critical):
		if DEBUG:
			print("# Starting CRITICAL parse  ", file=sys.stderr)
		dropWeight,ThrusterServo,CriticalError,CriticalTime,WaterCritical = parseCritical(critical)

	DVLError=False
	BadBattery=False
	SWError = False
	HWError = False
	OverloadError = False
	MotorLock = False
	CTDError = False
	
	if faults:
		BadBattery,BadBatteryText,DVLError,SWError,OverloadError,HWError,WaterFault,MotorLock,CTDError = parseFaults(faults)

	
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
	PauseTime=False
	
	
	

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
		cdd[cname] = 'st3' # white fill
	
	cdd["color_arrow"] = "st16"
	cdd["color_ubat"] = "st18"
	cdd["color_flow"] = "st18"
	cdd["color_duration"] = "st18"
	cdd["color_satcommstext"]="st18" # no color = black
	# These are made invisible
	cartcolors=["color_bigcable",
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
	"color_cam2"]

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
	"text_current",
	"text_batteryduration",
	"text_ampago",
	"text_cellago",
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
	# these should persist after recovery
	#These are made blank
	specialnames=[
	"svg_current",
	"text_vehicle","text_lastupdate","text_flowago","text_scheduled","text_arrivestation",
	"text_stationdist","text_currentdist",	"text_criticaltime",
	"text_leak","text_leakago","text_missionago","text_cameraago","text_waypoint",
	"text_criticalerror","text_camago"
	]
	for tname in specialnames:
		cdd[tname]=''
	

	'''
	
	 _            _       
	| |_ ___   __| | ___  
	| __/ _ \ / _` |/ _ \ 
	| || (_) | (_| | (_) |
	 \__\___/ \__,_|\___/ 

	 
	 TODO: Warning: Battery Data not active. Expected only when running primaries
	 Change GPS calculation to look over a longer time scale
	 
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

	# cdd["text_nextcomm"] = hours(timeoutstart+needcomms*60*1000)
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

	if batteryduration > -998:
		cdd["text_batteryduration"] = batteryduration
		cdd["color_duration"] = colorduration

	if argobatt == "Good":
		cdd["color_argo"]="st25"
	elif argobatt == "Low":
		cdd["color_argo"]="st27"

		
	###
	###   MISSION OVERVIEW DISPLAY
	###

	cdd["text_vehicle"] = VEHICLE.upper()
	cdd["text_lastupdate"] = time.strftime('%H:%M')
	# Green = 5 if in defaults Lets go orange for not in
	cdd["color_missiondefault"] = ['st27','st25'][missionName in mission_defaults] 
	
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
		# CriticalError = False                                                               # unicode bullet
		if missionName and missionTime:
			missionNameText = missionName
			if missionName == "Default":
				missionNameText = "DEFAULT"
			cdd["text_mission"]= missionNameText + " - " + hours(missionTime)+ " &#x2022; " + dates(missionTime)
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
				
		if Scheduled:
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
		if ReachedWaypoint:
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
			
			# parse piscivore camera
			'''{text_camago}{color_cam1}{color_cam2} 2=gray, 3 white, 4 green 6 orange 11 dark gray'''
					
			if (camcat < 998) and (camcat > -1):
				if camchangetime:
					cdd["text_camago"] = elapsed(camchangetime-now)
				else:
					cdd["text_camago"]=""	
		
				if (camcat == 2): # two cameras on
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

		else:
			cdd["color_ubat"] = 'st18'
			cdd["color_flow"] = 'st18'
			
		if VEHICLE == 'galene':
			cdd["color_cameralens"] = "st3"
			if 'backseat' in missionName.lower():
				cdd["text_cameraago"] = "ON " # + cdd["text_missionago"]
				cdd["color_camerabody"] = "st4"
			else:
				cdd["color_camerabody"] = "st3"
				cdd["text_cameraago"] = "OFF " # + cdd["text_missionago"]
				
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
			print("SOFTWARE ERROR: " ,(now-SWError)/3600000, file=sys.stderr)
		
		# Ignore SW errors more than 4 hours old	
		if (SWError and ((now - SWError)/3600000 < 4)):
			cdd["color_sw"] = 'st5'

		if (HWError and ((now - HWError)/3600000 < 4)):
			cdd["color_hw"] = 'st5'
			
		if (OverloadError and ((now - OverloadError)/3600000 < 4)):
			cdd["color_ot"] = 'st5'
			
		if (CTDError and not CTDoffCommand and ((now - CTDError)/3600000 < 4)):
			cdd["color_ctd"] = 'st6'
			
		elif CTDoffCommand:
			cdd["color_ctd"] = 'st5'
		else:
			cdd["color_ctd"] = 'st4'
			
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
			cdd["text_criticalerror"] = "CRITICAL: "+ CriticalError
			cdd["text_criticaltime"]  = elapsed(CriticalTime-now)
		else:
			CriticalTime = 0
		
		cdd["color_dvl"] = DVLcolor
		
		if (WaterCritical):
			cdd["color_leak"] = "stleak2"
			cdd["text_leak"] = "CRITICAL LEAK: "
			cdd["text_leakago"] = elapsed(WaterCritical-now)

		elif (WaterFault):
			cdd["color_leak"] = "stleak1"
			cdd["text_leak"] = "AUX LEAK: "
			cdd["text_leakago"] = elapsed(WaterFault-now)
		
		
		# If there was a critical since the last schedule pause or schedule resume event, 
		# then the schedule is effectively paused.
		
		if Paused or (PauseTime < CriticalTime):
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
		if dropWeight > 100:
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
					if (camcat < 998) and (camcat > -1):
						outfile.write(svgpiscivore.format(
							color_cam1 = cdd["color_cam1"],
							color_cam2 = cdd["color_cam2"],
							text_camago = cdd["text_camago"] )
						)

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
	
