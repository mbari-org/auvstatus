#!/usr/bin/env python3
from ESPelements import svghead,svgtail

nrows = 6
ncols = 10
ncells = nrows * ncols

style_circle_big = ["stroke_darkGray"] * (ncells +1)

style_circle_small = ["fill_green"] * (ncells+1)

style_text_label = "font_size7 font_helvBold"

text_label = ["00"] * (ncells +1)

percentlist = [5] * (ncells + 1)

small_radius = 10

def getstrings():

	spcol = 32 # between columns across
	sprow = 40
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

# SET FORMAT HERE
for i in [11,22,33,44,55]:
	style_circle_big[i] = "stroke_purple"
for j in [21,32,43,54]:
	style_circle_small[j] = "fill_orange"

for p in range(61):
	percentlist[p] = getpieval(p,small_radius)
	
string_circle_big, string_circle_small, string_pie, string_text_label = getstrings()
# GENERATE SVG HERE
print(svghead)
# printmatrix()
# print(makepiechart(percent=75,xp=79,yp=48,radius=10))
print(string_circle_big.format(*style_circle_big))
	# print(string_circle_small.format(*style_circle_small))
print(string_pie.format(*percentlist))
print(string_text_label)

print(svgtail)


''' OTHER ELEMENTS LIKE TIME AND WHITE LINE:
 <text class="st7" transform="translate(22.54 46.71)">04/01</text>
  <text class="st7" transform="translate(22.54 52.58)">12:34</text>
  <text class="st9" transform="translate(58.37 47.49)">04/02</text>
  <text class="st9" transform="translate(58.37 53.35)">12:34</text>
  <line class="st10" y1="56.19" x2="275.72" y2="56.19"/>
  '''