#!/usr/bin/env python3

from ESPelements import svghead,svgtail

import argparse
import sys
import time
import os
import requests
import json
import re
import ssl

# ssl._create_default_https_context = ssl._create_unverified_context

# Default timeouts for selected missions
''' AVAILABLE STYLES
 .fill_gray { fill: #dcddde; }
 .fill_white { fill: #fff; }
 .stroke_purple { stroke: #9b509f; fill:none; stroke-width: 2px; }
 .stroke_black  { stroke: #000; fill:none; stroke-width: 2px; }
 .stroke_none {stroke: none; fill:none};
 .stroke_2px { stroke-width: 2px; }
 .stroke_white { fill: none; stroke: #fff; }
 .stroke_darkGray { stroke: #231f20; fill: none; stroke-width: 2px;}
 .fill_orange { fill: #ef972c; }
 .fill_yellow { fill: #efef00; }
 .fill_lightgray { fill: #727373; }
 .fill_green { fill: #5cba48; }
 .font_size7 { font-size: 7px; }
 .fill_darkgray { fill: #231f20; }
 .font_helv { font-family: Helvetica; }
 .font_helvBold { font-family: Helvetica-Bold, Helvetica; font-weight: 700; }
 .fill_lightergray { fill: #919396; }
'''


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
		print("### QUERY:",URL, file=sys.stderr)
	
	connection = requests.get(URL,timeout=5)		
	if connection:
		raw = connection.text
		# if DEBUG:
		# 	print("##### START RAW #######\n",raw[:100],"##### START RAW #######\n",file=sys.stderr)
		structured = json.loads(raw)
		connection.close()
		result = structured['result']
	else:
		print ("# Query timeout",URL,file=sys.stderr)
		result = ''
	return result

	
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

##############
##
##  ESP FUNCTIONS

def getstrings():

	spcol = 26 # between columns across
	sprow = 26
	# generate circles
	string_circle_big = ''
	string_circle_small = ''
	string_text_label= ''
	string_pie = ''
	# Generate matrix of circles

	for row in range(nrows):
		for col in range(ncols):
			ind = row*ncols + col+1
			xval = 31 + spcol * col
			yval = 24 + sprow * row
			string_circle_big   += '<circle desc="c_big_{ind:02d}" class="{{{ind}}}" cx="{xval}" cy="{yval}" r="13"/>\n'.format(ind=ind,xval=xval,yval=yval)
			string_circle_small += '<circle desc="c_small_{ind:02d}" class="{{{ind}}}" cx="{xval}" cy="{yval}" r="{radius}"/>\n'.format(ind=ind,xval=xval,yval=yval,radius=small_radius)
			# change colors in function makepiestring()
			string_pie += makepiestring(index=ind,xp=xval,yp=yval,radius=small_radius)
			xval = 27 + spcol * col
			yval = 26 + sprow * row
			string_text_label   += '<text desc="t_label_{ind:02d}" class="st7" transform="translate({xval} {yval})">{ind:02d}</text>\n'.format(ind=ind,st=style_text_label,xval=xval,yval=yval)
	return string_circle_big, string_circle_small, string_pie, string_text_label
	
def getpieval(pct,radius):
	pi = 3.1416
	return ((pct) * pi*radius) / 100

def makepiestring(index,xp,yp,radius):
	# fill in all except leave numeric placeholder for percent 
	pi = 3.1416
	fulldash = pi*radius
	xoff = -(xp+yp)
	yoff = xp - yp

	piestring = '''
	<circle r="{radius}" cx="{xp}" cy="{yp}" class="fill_green"></circle>
	<circle desc="pie_{index:02d}" r="{smallradius}" cx="{xp}" cy="{yp}" fill="transparent"
	stroke="#ef972c"
	stroke-width="{radius}"
	stroke-dasharray="{{{index}}} {fulldash}"
	transform="rotate(-90) translate({xoff} {yoff})"></circle>
	'''.format(index=index,xp=xp,yp=yp,radius=radius,
	   smallradius=radius/2.0,fulldash=fulldash,
	   xoff=xoff,yoff=yoff)
	return piestring

def makepiechart(percent,xp,yp,radius):
	# fill in all except percent 
	pi = 3.1416
	value = getpieval(100-percent,radius)
	fulldash = pi*radius
	xoff = -(xp+yp)
	yoff = xp - yp

	piestring = '''
	<circle r="{radius}" cx="{xp}" cy="{yp}" class="fill_green"></circle>
	<circle r="{smallradius}"  cx="{xp}" cy="{yp}" fill="transparent"
	stroke="#ef972c"
	stroke-width="{radius}"
	stroke-dasharray="{value} {fulldash}"
	transform="rotate(-90) translate({xoff} {yoff})"></circle>
	'''.format(value=value,xp=xp,yp=yp,radius=radius,
	   smallradius=radius/2.0,fulldash=fulldash,
	   xoff=xoff,yoff=yoff)
	return piestring

def getESP(starttime):
	'''get critical entries, like drop weight
	ESPComponent'''
	qString = runQuery(name="ESPComponent",limit="2000",timeafter=starttime)
	retstring = ""
	if qString:
		retstring = qString
	
	return retstring
	
def parseESP(recordlist):
	'''
[sample #30] ESP log summary report (2 messages):
@20:23:06.72 Selecting Cartridge 22
@21:18:10.47 Sampled 1000.0ml

[sample #23] ESP log summary report (3 messages):
@21:35:45.54 Selecting Cartridge 29
@22:29:01.26 Cartridge::Sampler::Clogged in FILTERING -- Cartridge clogged
@22:29:01.45 Sampled 872.3ml
'''
	ESPL = [999] * 61 # Initialize 
	cartre = re.compile(r"Selecting Cartridge (\d+)")
	mlre   = re.compile(r"Sampled +([\d\.]+)ml")
	firstnum = False
	
	for Record in recordlist:
		RecordText = Record.get("text","NA")
		
		if "Cartridge" in RecordText:
			CartResult = cartre.search(RecordText)	
			if CartResult:
				Cartnum = int(CartResult.groups()[0])
				
				if not firstnum: # MOST RECENT
					firstnum = Cartnum
					firsttime = Record["unixTime"]
					
				VolumeResult = mlre.search(RecordText)				
				if VolumeResult:
					mls = VolumeResult.groups()[0]
					ESPL[Cartnum] = round(float(mls)/10)
			
			if DEBUG:
				print(RecordText,Record["name"],file=sys.stderr)
			
	return ESPL,firstnum,firsttime

def get_options():
	parser = argparse.ArgumentParser(usage = __doc__) 
#	parser.add_argument('infile', type = argparse.FileType('rU'), nargs='?',default = sys.stdin, help="output of vars_retrieve")
	parser.add_argument("-b", "--DEBUG",	action="store_true", help="Print debug info")
	parser.add_argument("-t", "--testout",	action="store_true", help="print testmatrix")
	parser.add_argument("-f", "--savefile",action="store_true", help="save to SVG named by vehicle at default location")
	parser.add_argument("-v", "--vehicle",	default="pontus"  , help="specify vehicle")
	parser.add_argument("Args", nargs='*')
	options = parser.parse_args()
	return options


#########################
#
Opt = get_options()
global DEBUG
DEBUG = Opt.DEBUG
global VEHICLE
VEHICLE = Opt.vehicle

if Opt.savefile:
	Opt.testout = False
	
# For the server, use tethysdash
if 'tethysdash' in os.uname()[1]:
	OutPath       = '/var/www/html/widget/esp_{}.svg'
	
# *** Can specify your username and path here
elif 'jellywatch' in os.uname():
	OutPath       = '/home/jellywatch/jellywatch.org/misc/esp_{}.svg'

else:
	OutPath = './auv_{}.svg'


now = 1000 * time.mktime(time.localtime())  # (*1000?)

# VEHICLE IS GLOBAL

startTime = getDeployment()

	

if not startTime:
	if DEBUG:
		sys.exit("##  Vehicle {} has no deployments".format(VEHICLE))
	else:
		sys.exit()

recovered = getRecovery(starttime=startTime)

plugged = getPlugged(recovered)


	


##########################################
# 
# ESP WIDGET configuration



nrows = 6
ncols = 10
ncells = nrows * ncols

stylelist = [999] * (ncells +1)

style_circle_big = ["stroke_none"] * (ncells +1)

style_circle_small = ["fill_green"] * (ncells+1)

style_text_label = "font_size7 font_helvBold"

text_label = ["00"] * (ncells +1)

percentlist = [5] * (ncells + 1)

small_radius = 10

# PARSE RECORDS and SET FORMAT HERE

if (not recovered) or DEBUG:
	esprecords  = getESP(startTime)
	if DEBUG:
		print(esprecords,file=sys.stderr)
	
	if esprecords:
		outlist,mostrecent,lastsample = parseESP(esprecords)
		'''['r' if i > 50 else 'y' if i > 2 else 'g' for i in x]'''
		stylelist = \
		['fill_gray' if i > 500 \
		else 'fill_green' if i > 95  \
		else 'fill_orange' if i < 0  \
		else  'fill_yellow' for i in outlist]
		if mostrecent:
			style_circle_big[mostrecent] = 'stroke_purple'
			text_lastsample = elapsed(lastsample - now)

for p in range(61):
	percentlist[p] = getpieval(p,small_radius)

########################	
# GENERATE SVG HERE

string_circle_big, string_circle_small, string_pie, string_text_label = getstrings()

if Opt.testout:
	print(svghead)
	# printmatrix()
	# print(makepiechart(percent=75,xp=79,yp=48,radius=10))
	print(string_circle_big.format(*style_circle_big))
	print(string_circle_small.format(*stylelist))
	# print(string_pie.format(*percentlist))
	print(string_text_label)

	print('<text class="font_helv font_size9" transform="translate(25 190)">Last Sample: {}</text>'.format(text_lastsample))

	print(svgtail)

if Opt.savefile:
	if DEBUG:
		print (sys.stderr, "#Saving file ", OutPath.format(VEHICLE))
	with open(OutPath.format(VEHICLE),'w') as outfile:
		outfile.write(svghead)
		outfile.write(string_circle_big.format(*style_circle_big))
		outfile.write(string_circle_small.format(*stylelist))
		outfile.write(string_text_label)
		outfile.write('<text class="font_helv font_size9" transform="translate(25 190)">Last Sample: {}</text>'.format(text_lastsample))
		outfile.write(svgtail)
		



''' OTHER ELEMENTS LIKE TIME AND WHITE LINE:
  <text class="st7" transform="translate(22.54 52.58)">12:34</text>
  <text class="st9" transform="translate(58.37 47.49)">04/02</text>
  <text class="st9" transform="translate(58.37 53.35)">12:34</text>
  <line class="st10" y1="56.19" x2="275.72" y2="56.19"/>
  '''