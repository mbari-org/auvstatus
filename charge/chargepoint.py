#! /usr/bin/env python3
# -*- coding: utf-8 -*-
''' use -p to print instead of save to file 
    use -f to define an alternative path
	
	Version 1.6 : Show unreachable on certain errors
    Version 1.5 : Added notifications for freed-up chargers
    Version 1.1'''

import argparse
import sys
import time
import os
from zeep import xsd
from zeep import Client
from zeep.wsse.username import UsernameToken


def get_options():
	parser = argparse.ArgumentParser(usage = __doc__) 
#	parser.add_argument('infile', type = argparse.FileType('rU'), nargs='?',default = sys.stdin, help="output of vars_retrieve")
	parser.add_argument("-b", "--DEBUG",	action="store_true",	 help="Print debug info")
	parser.add_argument("-p", "--myprint",	action="store_true",	 help="print to screen, not file")
	parser.add_argument("Args", nargs='*')
	options = parser.parse_args()
	return options


opt=get_options()

def sendMessage(MessageText="EV Status"):
	import smtplib
	import settings

	from email.mime.text import MIMEText


	# PCfB Stuff
	me = 'steve@jellywatch.org'
	port = 587
	lasthord = settings.pa
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
	server.login(me, lasthord)
	server.sendmail(me, you, msg.as_string() )
	server.quit()



UnitOrder = ["Outside1","Outside2","Garage1","Garage2"] # <-- Check which is 1 vs 2


ListQuery = {"Garage1": {'stationID': '1:812581' },       # 5,6
             "Garage2": {'stationID': '1:1762561'},       # 7,8
             "Outside1": {'stationID': '1:114123' },      # 1,2
             "Outside2": {'stationID': '1:1762571'}  }    # 3,4
				
# POSSIBLE STATUS STATES: AVAILABLE, INUSE, UNREACHABLE, UNKNOWN
				

if 'jellywatch' in os.uname():
	OutPath       = '/home/jellywatch/jellywatch.org/misc/charge.svg'
	StartTimePath = '/home/jellywatch/jellywatch.org/misc/startcharge.csv'
elif 'tethys' in os.uname().nodename:
	OutPath = '/var/www/html/widget/charge/charge.svg'
	StartTimePath = "/var/www/html/widget/charge/startcharge.csv"
else:
	OutPath = './charge.svg'
	StartTimePath = '.startcharge.csv'

Username = "c153d01bc218067cb536909438aa48e4581b9c7f0520d1478204543"
Password = "020968c4856a8fb1b23342856e1bc407"

client = False
wsdl_url = "https://webservices.chargepoint.com/cp_api_5.0.wsdl"
client = Client(wsdl_url, wsse=UsernameToken(Username, Password))

# Get our whole list of stations:
# stationData = client.service.getStations({})
# numStations = len(stationData.stationData)
if not client:
	sys.exit()
StatusArray=[]
for Site in UnitOrder:
	try:
		data = client.service.getStationStatus(ListQuery[Site])
		d = data.stationData[0]
		if opt.DEBUG:
			print(Site, d.stationID, d.Port[0].Status,d.Port[1].Status, file=sys.stderr)
		StatusArray += [d.Port[0].Status[0],d.Port[1].Status[0]]  # first letter
	except zeep.exceptions.Fault:
		StatusArray += ['U','U']   # Indicate unreachable
		sys.exit()
	except NameError:
		StatusArray += ['U','U']   # Indicate unreachable
		sys.exit()
if opt.DEBUG:
	print("StatusArray",StatusArray, file=sys.stderr)


StyleD = {"A":6,"I":7,"U":8}


#Special case for first station:
if StatusArray[0] == "A" and StatusArray[1] == "A":
	FirstValue = StyleD["A"]
elif StatusArray[0] == "I" or StatusArray[1] == "I":
	FirstValue = StyleD["I"]
else:
	FirstValue = StyleD["U"]
	
StyleList = [FirstValue]
for Stat in StatusArray[2:]:
	StyleList.append(StyleD.get(Stat))
##
###### MANUAL OVERRIDE
##
# 4: unit 6
# StyleList[4]=8

if opt.DEBUG:
	print("StyleList",StyleList, file=sys.stderr)
	

TimeString = time.strftime('%H:%M', time.localtime())

if opt.DEBUG:
	sendMessage("Test Message " + TimeString)

# TODO: Implementing a log that tracked duration of INUSE events (instead of querying). Write start time to text file at first transition?

if os.path.isfile(StartTimePath):
	with open(StartTimePath,'rU') as StartFile:
		# OldTimes = StartFile.readlines()[0].strip().split(",")
		OldTimes = StartFile.readlines()[0].strip().split(",")
else:
	OldTimes = ["9876543210"]*9

if opt.DEBUG:
	print("OldTimes",OldTimes, file=sys.stderr)

NewTime = int(time.time())

#Duration list is the duration *string* to report...
DurationList = [""] * 7

# Figure out if any occupied ports have opened up

AnyNowOpen = int(6 in StyleList)   # True if open, false if all full
AnyWereOpen = int(OldTimes[8])

if ((not AnyWereOpen) and AnyNowOpen):
	sendMessage("Charger now OPEN: " + TimeString)
	
if (AnyWereOpen and not(AnyNowOpen)):
	sendMessage("Chargers FULL: " + TimeString)
	
if opt.DEBUG:
	print("AnyWereOpen ",AnyWereOpen, file=sys.stderr)
	print("AnyNowOpen  ",AnyNowOpen, file=sys.stderr)
		
# Check offline and update time
Offline = (8 in StyleList)
OfflineBase = '<text class="cls-18" transform="translate(104 390)">OFFLINE: {}{} min.</text>\n'

if Offline:
	if opt.DEBUG: 
		print("# Found offline", DurationList, file=sys.stderr)
	duration = int(NewTime - int(OldTimes[7]))  # last value
	if duration < 1:
		offlineTime = NewTime
		duration = 0
	# keep previous old time from which to calculate duration
	else:
		offlineTime = int(OldTimes[7]) 
		
	minutes = int(duration/60)+1
	MinuteString = minutes
	HourString = ""
	if minutes>59:
		MinuteString = minutes%60
		HourString = str(minutes//60) + " hr. " 

	OfflineString = OfflineBase.format(HourString,MinuteString)
	
else:
	OfflineString = ""
	offlineTime = 9999999999

# NewOldList is the new start times to save in the file
NewOldList = DurationList[:]
NewOldList.append(offlineTime)
NewOldList.append(AnyNowOpen)


if opt.DEBUG:
	print("NewOldList before loop", NewOldList, file=sys.stderr)
	
for item in enumerate(zip(OldTimes,StyleList)):
	# INUSE = 7
	# item[1][1] 
	# (6, (9999999999, 6))
	ind = item[0]
	ot,stat = item[1]
	
	# style 6 is AVAILABLE, 7 is INUSE, 8 is offline.
	# Change to > 6 to track offline time
	if stat==7:    # track time offline?
		# Process for new duration and starttime
		duration = int(NewTime - int(ot))
		# in use, but first time so no previous times
		if duration < 1:
			outvalues = [NewTime, 1]
			
		# keep previous old time from which to calculate duration
		else:
			outvalues = [int(ot), int(duration/60)+1]
			
	#### RESUME HERE ####
	else:
		outvalues = [9999999999, ""]
	NewOldList[ind] = outvalues[0]
	DurationList[ind] = outvalues[1]

if opt.DEBUG:
	print("NewOldList After Loop",NewOldList, file=sys.stderr)
	print("DurationList",DurationList, file=sys.stderr)
	

SVGText = '''<svg id="Layer_9" data-name="Layer 9" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440.37 438.1">
<defs>
<style>.cls-1,.cls-9{fill:#d5d7d8;}.cls-1,.cls-10{stroke:#777;}.cls-1,.cls-10,.cls-6,.cls-7,.cls-8{stroke-miterlimit:10;}
.cls-1{stroke-width:1.29px;}.cls-2,.cls-3,.cls-5{isolation:isolate;font-size:12px;}.cls-2{fill:#4260ac;}
.cls-14,.cls-2,.cls-3,.cls-5,.cls-15,.cls-16,.cls-18{font-family:Helvetica, Helvetica;}.cls-3,.cls-15,.cls-18{fill:#999;}
.cls-4{letter-spacing:-0.02em;}.cls-5{fill:#231f20;}.cls-13,.cls-6{fill:#40d3ac;}.cls-6,.cls-7,.cls-8{stroke:#000;}
.cls-10,.cls-6,.cls-7,.cls-8{stroke-width:2px;}.cls-12,.cls-7{fill:#fbb040;}.cls-11,.cls-8{fill:#6d6d6d;}
.cls-10{fill:none;stroke-dasharray:2.04 2.04;}.cls-16{font-size:8px;}.cls-14,.cls-15,.cls-18{font-size:9px;}
.cls-17{fill:none;}.cls-17{stroke:#999;}</style></defs>
<title>ChargepointStatus</title>
<polyline class="cls-1" points="99.86 37.71 99.86 355.8 356.55 355.8 356.55 296.38 290.06 296.38 290.06 98.04 356.55 98.04 356.55 37.71 98.95 37.71"/>
<text class="cls-2" transform="translate(101.57 377.42)">Updated: %s</text>
<text class="cls-3" transform="translate(324.98 130.9)">Open</text>
<text class="cls-3" transform="translate(324.98 159.27)">In Use</text>
<text class="cls-3" transform="translate(324.98 187.64)">Offline</text>
<text class="cls-5" transform="translate(140.58 196.57)">7</text>
<text class="cls-5" transform="translate(140.58 166.78)">8</text>
<text class="cls-5" transform="translate(140.58 226.36)">6</text>
<text class="cls-5" transform="translate(140.58 256.14)">5</text>
<text class="cls-5" transform="translate(361.15 403)">4</text>
<text class="cls-5" transform="translate(332.78 403)">3</text>
<text class="cls-5" transform="translate(283.84 403)">2</text>
<text class="cls-5" transform="translate(255.48 403)">1</text>
<circle class="cls-%d" cx="120.72" cy="162.52" r="11.7"/>
<circle class="cls-%d" cx="120.72" cy="192.55" r="11.7"/>
<circle class="cls-%d" cx="120.72" cy="222.57" r="11.7"/>
<circle class="cls-%d" cx="120.72" cy="252.6" r="11.7"/>
<circle class="cls-%d" cx="363.28" cy="378.13" r="11.7"/>
<circle class="cls-%d" cx="335.62" cy="378.13" r="11.7"/>
<circle class="cls-%d" cx="259.73" cy="378.13" r="11.7"/>
<circle class="cls-9" cx="286.72" cy="378.13" r="11.7"/>
<circle class="cls-10" cx="286.72" cy="378.13" r="11.7" transform="translate(-172.35 498.32) rotate(-67.5)"/>
<circle class="cls-11" cx="312.95" cy="182.88" r="8.19"/>
<circle class="cls-12" cx="312.95" cy="154.97" r="8.19"/>
<circle class="cls-13" cx="312.95" cy="127.06" r="8.19"/>
<text class="cls-14" text-anchor="middle" transform="translate(120.83 165.67)">%s</text>
<text class="cls-14" text-anchor="middle" transform="translate(120.83 195.67)">%s</text>
<text class="cls-14" text-anchor="middle" transform="translate(120.83 226.67)">%s</text>
<text class="cls-14" text-anchor="middle" transform="translate(120.16 256.33)">%s</text>
<text class="cls-14" text-anchor="middle" transform="translate(363.16 381.33)">%s</text>
<text class="cls-14" text-anchor="middle" transform="translate(336.16 381.33)">%s</text>
<text class="cls-14" text-anchor="middle" transform="translate(259.83 381.33)">%s</text>
<text class="cls-15" transform="translate(325.65 171.94)">minutes</text>
<text class="cls-16" transform="translate(305.99 158.33)">123</text>
<path class="cls-17" d="M313.67,160.33s3,10,10,9.34"/>
%s</svg>
'''

if opt.DEBUG: 
	print("DurationList", DurationList, file=sys.stderr)
	print("OfflineString",OfflineString, file=sys.stderr)
# DurationStrings = ['{:^3}'.format(j) for j in DurationList]
OutString = SVGText % tuple([TimeString] + StyleList[::-1] + DurationList[::-1] + [OfflineString])

# print(os.uname().nodename)

if opt.myprint:
	print(OutString)
else:
	with open(OutPath,'w') as outfile:
		outfile.write(OutString)
		
with open(StartTimePath,'w') as NewStartFile:
	NewStartFile.write(",".join([str(z) for z in NewOldList]))

