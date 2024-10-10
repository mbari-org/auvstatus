#!/usr/bin/env python3
'''
v 1.2.4 : Added spares left indicator
v 1.2.3 : Moved SPR string above % pumped
v 1.2.2 : Added toxin report if SPR is present (replacing % pumped)
v 1.2.1 : Adding json export of percentages and times
v 1.2   : import functions from auvstatus instead of repeating them
v 1.1.2 : Fixed reporting of one-off failed samples 
v 1.1.1 : Fixed some parsing of re-pumped samplers. Need to confirm with true redo.
v 1.1   : Starting version numbers!
'''


from ESPelements import svghead,svgtail
from auvstatus import runNewStyleQuery,getNewDeployment,runQuery,getDeployment,getRecovery, getPlugged,hours,dates,elapsed

import argparse
import sys
import time
import os
# import requests
import json
import re
import ssl
import urllib.request, urllib.error, urllib.parse
from datetime import datetime,timedelta

''' AVAILABLE STYLES
 .st1 { fill: #dcddde; }
 .st2, .st3 { fill: #fff; }
 .st2 { stroke: #9b509f; }
 .st10, .st2, .st3 { stroke-miterlimit: 10; }
 .st10, .st2 { stroke-width: 2px; }
 .st3 { stroke: #231f20; }
 .st4 { fill: #ef972c; }   <!-- orange circle-->
 .st5 { fill: #727373; }
 .st6 { fill: #5cba48; }
 .st7, .st8, .st9 { font-size: 7px; }
 .st7, .st8 { fill: #231f20; }
 .te5, .st7, .st9 { font-family: Helvetica; }
 .st8 { font-family: Helvetica-Bold, Helvetica; font-weight: 700; }
 .st9 { fill: #919396; }
 .st10 { fill: none; stroke: #fff; }

 .fill_gray { fill: #bbbbbb; }
 .fill_white { fill: #fff; }
 .stroke_purple { stroke: #ab60af; fill:none; stroke-width: 2px; }
 .stroke_black  { stroke: #000; fill:none; stroke-width: 2px; }
 .stroke_blue  { stroke: #067878; fill:none; stroke-width: 2px; stroke-dasharray:1.1 1.4;}
 .stroke_green  { stroke: #5cba48; fill:none; stroke-width: 3px;}
 .stroke_dash  { stroke-dasharray:1.1 1.4;}
 .stroke_2px { stroke-width: 2px; }
 .stroke_white { fill: none; stroke: #fff; }
 .stroke_none {stroke: none; fill:none};
 .stroke_darkGray { stroke: #231f20; fill: none; stroke-width: 2px;}
 .fill_orange { fill: #ef972c; }
 .fill_yellow { fill: #efef00; }
 .fill_lightgray { fill: #e2e2e2; }
 .thick_orange     { stroke-width:4px; fill:none; stroke: #ef972c; }
 .thick_yellow     { stroke-width:4px; fill:none; stroke: #f7ca0b; }
 .thick_gray       { stroke-width:4px; fill:none; stroke: #bbbbbb; }
 .thick_green      { stroke-width:4px; fill:none; stroke: #5cba48; }
 .fill_green { fill: #5cba48; }
 .font_size4 { font-size: 4px; }
 .font_size5 { font-size: 5px; }
 .font_size7 { font-size: 7px; }
 .font_size9 { font-size: 9px; }
 .fill_red {fill: #e24466; }
 .fill_purple {fill:#ab60af;}
 .fill_darkgray { fill: #7b7e82; }
 .font_helv { font-family: Helvetica; }
 .font_helvBold { font-family: Helvetica-Bold, Helvetica; font-weight: 700; }
 .fill_lightergray { fill: #919396; }
'''

	
	

##############
##
##  ESP FUNCTIONS - Generates the grid of numbered elements

def getstrings():

	# generate circles
	string_circle_big   = ''
	string_circle_small = ''
	string_text_label   = ''
	string_pct_label    = ''
	string_spr_label    = ''
	string_time_label    = ''
	string_pie          = ''
	string_line_small   = ''
	# Generate matrix of circles

	for row in range(nrows):
		for col in range(ncols):
			ind = row*ncols + col+1
			xval = 31 + spcol * col
			yval = 24 + sprow * row
			
			string_line_small   +=  '<line desc="line_{ind:02d}" class="{{{ind}}}" x1="{xval}" x2="{xval}" y1="{yval}" y2="{y2val}" />\n'.format(ind=ind,xval=xval,yval=yval,y2val=yval+small_radius+8)

			string_circle_big   += '<circle desc="c_big_{ind:02d}" class="{{{ind}}}" cx="{xval}" cy="{yval}" r="{radius}"/>\n'.format(ind=ind,xval=xval,yval=yval,radius = small_radius+2)
			string_circle_small += '<circle desc="c_small_{ind:02d}" class="{{{ind}}}" cx="{xval}" cy="{yval}" r="{radius}"/>\n'.format(ind=ind,xval=xval,yval=yval,radius=small_radius)
			# change colors in function makepiestring()
			string_pie += makepiestring(index=ind,xp=xval,yp=yval,radius=small_radius)
			
			xval = 5+ spcol * (col + 1)
			yval = sprow * (row +1)
			string_text_label   += '<text desc="t_label_{ind:02d}" class="st7" text-anchor="middle" transform="translate({xval} {yval})">{ind:02d}</text>\n'.format(ind=ind,st=style_text_label,xval=xval,yval=yval)
			
			# Percent labels for incomplete samples - ABOVE the number
			string_spr_label   += '<text desc="spr_label_{ind:02d}" text-anchor="middle" class="st8 font_size5 fill_darkgray" transform="translate({xval} {yval})">{{{ind}}}</text>\n'.format(ind=ind,xval=xval,yval=yval-9.4)
			
			string_pct_label   += '<text desc="pct_label_{ind:02d}" text-anchor="middle" class="te5 font_size4 fill_purple" transform="translate({xval} {yval})">{{{ind}}}</text>\n'.format(ind=ind,xval=xval,yval=yval-6)
			
			string_time_label   += '<text desc="time_label_{ind:02d}" text-anchor="middle" class="te5 font_size4 fill_darkgray" transform="translate({xval} {yval})">{{{ind}}}</text>\n'.format(ind=ind,xval=xval,yval=yval+5)
			

	return string_circle_big, string_circle_small, string_line_small, string_pie, string_text_label, string_pct_label, string_time_label, string_spr_label
	
	
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
	qString = runQuery(name="ESPComponent",limit="2000",match=".*Selecting.*",timeafter=starttime)
	retstring = ""
	if qString:
		retstring = qString
	
	return retstring

def checkAcoustic(starttime):
	qString = ""
	qString = runQuery(name="hs2dash",limit="20",match=".*LRAUVcntSamples.*",timeafter=starttime)
	if DEBUG:
		print("\n### ACOUSTIC ",qString,file=sys.stderr)
	return qString

def parseAcoustic(records):
	# TODO!
	for Record in records:
		RecordText = Record.get("text","NA")
		if DEBUG and RecordText:
			print("#ACOUSTIC RECORD: ",RecordText)
			
def parseESP(recordlist,big_circle_list):
	'''
[sample #30] ESP log summary report (2 messages):
@20:23:06.72 Selecting Cartridge 22
@21:18:10.47 Sampled 1000.0ml

[sample #23] ESP log summary report (3 messages):
@21:35:45.54 Selecting Cartridge 29
@22:29:01.26 Cartridge::Sampler::Clogged in FILTERING -- Cartridge clogged
@22:29:01.45 Sampled 872.3ml

@17:07:18.55 Selecting Cartridge 31
@17:10:22.88 Cartridge::Sampler::Leak in FILTERING -- Isolated cartridge pressure fell by 15% to 58.6psia
@17:10:22.89 Retry #1 of 2
@17:10:22.94 Selecting Cartridge 30
@18:07:41.18 Sampled  1000.0ml"

NEW? 
[sample #1] ESP log summary report (3 messages):
@15:14:26.79 Selecting Cartridge 51
@16:10:09.76 Sampled 1000.0ml
@17:00:54.39 <SPRlogger> SPRsummary:5.3RIU,220RIU,179RIU,279RIU,none,none,none after 3211s
SPRsummary:15.8RIU,177RIU,175RIU,237RIU,none,none,2.16ng/L after 3231s
'''
	ESPL = [999] * 61 # Initialize percent list
	TimeList = [''] * 61 #
	cartre = re.compile(r"Selecting Cartridge (\d+)")
	# editing VolumeResult regex for entries like
	# "@21:27:49.79 Cmd::Paused in FILTERING --  during Sample Pump (SP) move after sampling 1161.4ml
	mlre    = re.compile(r"Sampled +([\d\.]+)ml")
	pausere = re.compile(r"after sampling +([\d\.]+)ml")
	sprre   = re.compile(r"SPRsummary.+,(.+) after")
	sparere   = re.compile(r"([\d]+) +spares? remain")


	firstnum = False
	firsttime = False
	RedoList = []
	DoneList = []
	SPRdict = {}
	Sparenum = 'na'

	
	for Record in recordlist:
		RecordText = Record.get("text","NA")
		Redo = False
		
		if "Cartridge" in RecordText:
			if Sparenum == 'na':
				SpareResult = sparere.findall(RecordText)
				if SpareResult:
					Sparenum = SpareResult[-1]
			CartResult = cartre.findall(RecordText)	
			if CartResult:
				Cartnum = int(CartResult[-1])
				if DEBUG:
					print("C",CartResult,RecordText,file=sys.stderr)
					

				VolumeResult = mlre.findall(RecordText)
				SPRResult = sprre.findall(RecordText)
				
				if VolumeResult:
					if DEBUG:
						print("## VOLUMERESULT",VolumeResult,file=sys.stderr)
				else:
					VolumeResult = 	pausere.findall(RecordText)
					if DEBUG: 
						if VolumeResult:
							print("## FOUND PARTIAL RESULT",VolumeResult,file=sys.stderr)
						else:
							print("## NO VOLUME RESULT FOUND",RecordText,file=sys.stderr)
					if not VolumeResult:
						VolumeResult=[-199]
					
				if len(CartResult) == 1:
					Cartnum = int(CartResult[-1])
					if VolumeResult:
						mls = VolumeResult[-1]
						if Cartnum not in DoneList:
							DoneList.append(Cartnum)
							ESPL[Cartnum] = round(float(mls)/10)
							TimeList[Cartnum] = Record["unixTime"]					
					else:
						mls=-100
						VolumeResult=[-199]
						
					if SPRResult:
						if DEBUG:
							print("\n## SPR",SPRResult,file=sys.stderr)
						if 'ng' in SPRResult[0]:
							spout = SPRResult[0].replace('ng/L','')
						else:
							spout = SPRResult[0].upper()
						SPRdict[Cartnum] = spout
						
					if not firstnum: # MOST RECENT
						firstnum = Cartnum
						firsttime = Record["unixTime"]
						if mls != "999":
							big_circle_list[Cartnum] = "stroke_purple"
						if DEBUG:
							print("FIRST CIRCLE:",Cartnum)
				else:  # handling error with a redo, more than one cartridge
				
					# ON a redo:
					# insert errors numbers to the cartridge numbers
					Cartnum = int(CartResult[0])
					vols = ["-99"] * (len(CartResult)-len(VolumeResult)) + VolumeResult[:]
					if DEBUG:
						print("\n## Cartridges in redo:",CartResult,file=sys.stderr)
						
					if ESPL[Cartnum] != 999:
						RedoList.append(Cartnum)
						big_circle_list[Cartnum] = "stroke_green"
						if DEBUG:
							print("\n## Found REUSE:",Cartnum,mls,file=sys.stderr)

					#if DEBUG:
						#print("VOLS:",vols,"\nCARTS:",CartResult,file=sys.stderr)
					for c,v in list(zip(CartResult,vols))[::-1]:
						if not firstnum: # MOST RECENT
							firstnum = int(CartResult[-1])
							firsttime = Record["unixTime"]
							big_circle_list[firstnum] = "stroke_purple stroke_dash"
							if DEBUG:
								print("FIRST CIRCLE in REDO:",firstnum,file=sys.stderr)
						elif v != "-99":
							big_circle_list[int(c)] = "stroke_blue"
							if DEBUG:
								print("SETTING RESAMPLE BLUE: ",c,file=sys.stderr)
							
						ESPL[int(c)]= round(float(v)/10)
						TimeList[int(c)] = Record["unixTime"]					
# 					if not firstnum:
# 						firstnum = int(c)
# 						if v != "-99":
# 							big_circle_list[int(c)] = "stroke_purple stroke_dash"
# 						firsttime = Record["unixTime"]
					
	if DEBUG:
		print("BigCircleList",big_circle_list,file=sys.stderr)
		print("REDO list",RedoList,file=sys.stderr)
		print("TIME list",TimeList,file=sys.stderr)	
		print("SPR Dict",SPRdict,file=sys.stderr)	
			
	return ESPL,firstnum,firsttime,big_circle_list,RedoList,TimeList,SPRdict,Sparenum

def printLegend(lowerleft):
	lowerx=lowerleft[0]
	lowery=lowerleft[1]+10
	offsetx=24
	legend=''
		
	legend += '\n<circle class="fill_green" cx="{xval}" cy="{yval}" r="{radius}"/>'.format(
	    xval   = lowerx+4+offsetx *0,
	    yval   = lowery,
	    radius = small_radius-4)
	legend += '\n<text class="te5 font_size5" transform="translate({tx} {ty})">GOOD</text>'.format(
	    tx = lowerx - (small_radius-4)/2 +offsetx *0,
	    ty = lowery+2)
	legend += '\n<circle class="fill_yellow" cx="{xval}" cy="{yval}" r="{radius}"/>'.format(
	    xval   = lowerx +3 +offsetx *1,
	    yval   = lowery ,
	    radius = small_radius-4)
	legend += '\n<text class="te5 font_size5" transform="translate({tx} {ty})">PART</text>'.format(
	    tx = lowerx- (small_radius-4)/2 +offsetx *1,
	    ty = lowery +2)
	legend += '\n<circle class="fill_orange" cx="{xval}" cy="{yval}" r="{radius}"/>'.format(
	    xval   = lowerx +2 +offsetx *2,
	    yval   = lowery ,
	    radius = small_radius-4)
	legend += '\n<text class="te5 font_size5" transform="translate({tx} {ty})">FAIL</text>'.format(
	    tx = lowerx -(small_radius-4)/2 +offsetx *2,
	    ty = lowery +2)
	legend += '\n<circle class="stroke_purple" cx="{xval}" cy="{yval}" r="{radius}"/>'.format(
	    xval   = lowerx +2 +offsetx *3,
	    yval   = lowery ,
	    radius = small_radius-4)
	legend += '\n<text class="te5 font_size5" transform="translate({tx} {ty})">LAST</text>'.format(
	    tx = lowerx -(small_radius-2)/2 +offsetx *3,
	    ty = lowery +2)
	legend += '\n<circle class="stroke_blue stroke_dash" cx="{xval}" cy="{yval}" r="{radius}"/>'.format(
	    xval   = lowerx +2 +offsetx *4,
	    yval   = lowery ,
	    radius = small_radius-4)
	legend += '\n<text class="te5 font_size5" transform="translate({tx} {ty})">REDO</text>'.format(
	    tx = lowerx -(small_radius-2)/2 +offsetx *4 -1,
	    ty = lowery +2)
	legend += '\n<circle class="stroke_green" cx="{xval}" cy="{yval}" r="{radius}"/>'.format(
	    xval   = lowerx +2 +offsetx *5,
	    yval   = lowery ,
	    radius = small_radius-4)
	legend += '\n<text class="te5 font_size5" transform="translate({tx} {ty})">REUSED</text>'.format(
	    tx = lowerx -(small_radius-2)/2 + offsetx *5 -4,
	    ty = lowery +2)
	    
	return legend
	
def writefile(myoutpath,RedoList,ArchiveStr="UPDATED"):
	with open(myoutpath.format(VEHICLE),'w') as outfile:
		outfile.write(svghead)
		outfile.write(string_circle_big.format(*style_circle_big))
		if Opt.lines:
			outfile.write(string_line_small.format(*linestylelist))
		else:	
			outfile.write(string_circle_small.format(*stylelist))
			outfile.write(string_text_label)
			if DEBUG:
				print("PCTLIST:",pctlist)
			outfile.write(string_pct_label.format(*pctlist))
			if (sprlist):
				outfile.write(string_spr_label.format(*sprlist))
			outfile.write(string_time_label.format(*TimeList))

		extratext = ''
		if RedoList:
			extratext = "+ {} reused".format(len(RedoList))
		outfile.write('<text class="font_helv font_size7" transform="translate({tx} {ty})">Last Sample: {upd}</text>'.format(upd=text_lastsample + 
		     " - " + VEHICLE.upper(),tx=lowerleft[0],ty=lowerleft[1]-2)) # 25 190
		timestring = dates(now) + " - " +hours(now) + " ({})".format(decimalday(now))
		outfile.write('<text class="font_helv font_size6" transform="translate({tx} {ty})">{arch}: {upd}</text>'.format(arch=ArchiveStr,upd=timestring,tx=lowerright[0]-80,ty=lowerright[1]-1)) # 175 190
		if sprlist:
			extratext += "[SPR PRESENT]"
		# SAMPLE SUMMARY
		outfile.write('<text class="te5 font_size5" transform="translate({tx} {ty})">Good Samples: {upd} {extra}</text>'.format(upd=GoodCount,tx=lowerright[0]-80,ty=lowerright[1]+7,extra=extratext)) # 175 190
		outfile.write('<text class="te5 font_size5" transform="translate({tx} {ty})">Samples Failed: {upd}</text>'.format(upd=LeakCount,tx=lowerright[0]-80,ty=lowerright[1]+13)) # 175 190
		if not(sparesleft == 'na'):
			outfile.write('<text class="te5 font_size5" transform="translate({tx} {ty})">Spares Left: {upd}</text>'.format(upd=sparesleft,tx=lowerright[0]-25,ty=lowerright[1]+13)) # 175 190
		outfile.write('<text class="te5 st5 font_size5" transform="translate({tx} {ty})">(Samples count down from high to low)</text>'.format(upd=LeakCount,tx=lowerright[0]-81,ty=lowerright[1]+19.5)) # 175 190
		outfile.write(printLegend(lowerleft))

		outfile.write(svgtail)
		
def decimalday(myt):
	if (myt):
		mytime = int(myt)/1000.0
		nowsec = datetime.fromtimestamp(mytime)
		hourfraction = (nowsec - datetime(nowsec.year-1,12,31)).seconds / 3600.0/24.0
		dayfraction  = (nowsec - datetime(nowsec.year-1,12,31)).days 
		daystr = "{:.02f}".format(dayfraction+hourfraction)
		if DEBUG:
			print("TIME:",myt,daystr)

	else:
		daystr = ''
	return daystr
	
def get_options():
	parser = argparse.ArgumentParser(usage = __doc__) 
#	parser.add_argument('infile', type = argparse.FileType('rU'), nargs='?',default = sys.stdin, help="output of vars_retrieve")
	parser.add_argument("-b", "--DEBUG",	action="store_true", help="Print debug info")
	parser.add_argument("-t", "--testout",	action="store_true", help="print testmatrix")
	parser.add_argument("-l", "--lines",	action="store_true", help="use lines not circles")
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
text_lastsample = "na"
if Opt.savefile:
	Opt.testout = False
	
# For the server, use tethysdash
if 'tethysdash' in os.uname()[1]:
	OutPath       = '/var/www/html/widget/esp_{0}.svg'
	
# *** Can specify your username and path here
elif 'jellywatch' in os.uname():
	OutPath       = '/home/jellywatch/jellywatch.org/misc/esp_{0}.svg'

else:
	OutPath = './esp_{0}.svg'


now = 1000 * time.mktime(time.localtime())  # (*1000?)

# VEHICLE IS GLOBAL

startTime = getDeployment()
#TEMPORARY

if not startTime:
	if DEBUG:
		sys.exit("##  Vehicle {0} has no deployments".format(VEHICLE))
	else:
		sys.exit()

recovered = getRecovery(starttime=startTime)
plugged = getPlugged(recovered)

# TEMPORARY OVERRIDE. REMOVE
# if VEHICLE == 'makai':
# 	plugged = False
# 	recovered = False
# 	startTime='1681494142142'

##########################################
# 
# ESP WIDGET configuration

nrows = 6
ncols = 10
ncells = nrows * ncols

spcol = 26 # spacing between columns across
sprow = 26 # spacing between rows vertically

textoffset = 20
lowerright = (spcol * ncols, sprow * nrows + textoffset)
lowerleft  = (spcol, sprow * nrows + textoffset)

stylelist = ["fill_lightergray"] * (ncells +1)
linestylelist = ["thick_gray"] * (ncells +1)
style_circle_big = ["stroke_none"] * (ncells +1)

style_circle_small = ["fill_green"] * (ncells+1)

style_text_label = "font_size7 font_helvBold"

text_label = ["00"] * (ncells +1)

percentlist = [5] * (ncells + 1)
TimeList = [''] * (ncells + 1)

small_radius = 10

if Opt.lines:
	spcol=7
	sprow=15
	small_radius=1

# PARSE RECORDS and SET FORMAT HERE
GoodCount = 'na'
LeakCount = 'na'
sparesleft= 'na'
RedoList = []
mytimes = []
outlist = []
pctlist = []
sprlist = []
if (not recovered) or DEBUG:
	
	parseAcoustic(checkAcoustic(startTime))
	
	esprecords = getESP(startTime)
# 	if DEBUG:
# 		print(esprecords,file=sys.stderr)
	
	if esprecords:
		outlist,mostrecent,lastsample,style_circle_big,RedoList,mytimes,sprd,sparesleft  = parseESP(esprecords,style_circle_big)
		#['r' if i > 50 else 'y' if i > 2 else 'g' for i in x]
		if DEBUG:
			print ("\n#OUTLIST ", outlist,file=sys.stderr)
			print ("\n#SPARES: ", sparesleft,file=sys.stderr)
			
		stylelist = \
		['fill_gray' if i > 500 \
		else 'fill_green' if i > 90  \
		else 'fill_orange' if i < 0  \
		else  'fill_yellow' for i in outlist]
		
		linestylelist = \
		['thick_gray' if i > 500 \
		else 'thick_green' if i > 90  \
		else 'thick_orange' if i < 0  \
		else 'thick_yellow' for i in outlist]


# 		GENERATE LIST OF PERCENTAGES
		pctlist = ['--X--' if i <10 else '' if i > 90 else '{inte:02d}%'.format(inte=int(round(i))) for i in outlist]
		for ri in RedoList:
			pctlist[ri] = 'reuse'
		if sprd:
			sprlist = [''] * (nrows * ncols +1)
		# SPRdict from toxin records.		
			for spi in sprd:
				sprlist[spi] = sprd.get(spi)
		
		if mostrecent:
			if DEBUG:
				print ("\n#MOSTRECENT OVERRIDE ", mostrecent,style_circle_big[mostrecent],file=sys.stderr)
			if not "dash" in style_circle_big[mostrecent]:
				style_circle_big[mostrecent] = 'stroke_purple'
			text_lastsample = elapsed(lastsample - now)
		# Changing from 10 to 1 on the min sample
		GoodCount = sum([1 for x in outlist if 10 < x < 101])
		LeakCount = sum([1 for x in outlist if x < 10])
		TimeList = [decimalday(x) for x in mytimes]
		
	else:
		pctlist = [''] * (nrows * ncols +1)


# for p in range(61):
# 	percentlist[p] = getpieval(p,small_radius)

########################	
# GENERATE SVG HERE

string_circle_big, string_circle_small, string_line_small, string_pie, string_text_label,string_pct_label,string_time_label,string_spr_label = getstrings()

if DEBUG:
	print ("\n#PCTLIST ", pctlist,file=sys.stderr)
#	print ("\n#string_spr_label \n", string_spr_label,file=sys.stderr)
#	print ("\n#string_pct_label \n", string_pct_label,file=sys.stderr)
	# print ("\n#new pctlist \n", pctlist,file=sys.stderr)
# 	print ("\n#string_pct_label ", string_pct_label.format(*pctlist),file=sys.stderr)
# 	print ("\n#LEGEND ", printLegend(lowerleft),file=sys.stderr)

if Opt.testout:
	print(svghead)
# 	printmatrix()   # not used?
	print(makepiechart(percent=75,xp=79,yp=48,radius=10))
# 	print(string_circle_big.format(*style_circle_big))
	print(string_circle_small.format(*stylelist))
	print(string_pie.format(*percentlist))
	print(string_text_label)
	
	print('<text class="font_helv font_size7" transform="translate(25 190)">Last Sample: {0}</text>'.format("Last sampled: 21:34"))

	print(svgtail)

if Opt.savefile and (not recovered):
	deployID="none"
	deploytime,deployID = getNewDeployment()
	if DEBUG:
		print (sys.stderr, "#Saving file ", OutPath.format(VEHICLE))		
		print (sys.stderr, "#DEPLOYMENT: ", deployID)
	
	writefile(OutPath,RedoList)
	writefile(OutPath.replace('.svg','-archive.svg'),RedoList,ArchiveStr="ARCHIVED")
	# outlist and mytimes contain percentages and time events.
	Archivename = "/var/www/html/widget/archive/auv_{v}-{d}.json".format(v=VEHICLE,d=deployID)
	with open(Archivename,'w') as archivefile:
		archivefile.write(json.dumps([mytimes,outlist]))

	#writefile(OutPath.replace('-archive.svg','.json'),RedoList,ArchiveStr="ARCHIVED")

elif Opt.savefile:
	NoDeployString = '''<svg id="Layer_1" data-name="Layer 1" 
xmlns="http://www.w3.org/2000/svg"  
x="0px" y="0px" viewBox="0 0 300 110" xml:space="preserve">
 <defs>
 <style>
 .fill_gray { fill: #bbbbbb; }
 .font_size9 { font-size: 9px; }
 .fill_lightgray { fill: #DDD; }
 .font_helv { font-family: Helvetica; }
    </style>
  </defs>
  <rect class="fill_lightgray" x="3.91" width="290" height="80"/> 
  <text class="font_helv font_size9" transform="translate(100 45)">NO ESP MISSION for '''

	with open(OutPath.format(VEHICLE),'w') as outfile:
		outfile.write(NoDeployString)
		outfile.write(VEHICLE.upper())
		outfile.write('''</text></svg>''')
		
		
''' OTHER ELEMENTS LIKE TIME AND WHITE LINE:
  <text class="st7" transform="translate(22.54 52.58)">12:34</text>
  <text class="st9" transform="translate(58.37 47.49)">04/02</text>
  <text class="st9" transform="translate(58.37 53.35)">12:34</text>
  <line class="st10" y1="56.19" x2="275.72" y2="56.19"/>
  '''
