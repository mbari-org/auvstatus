svghead = '''<?xml version="1.0" encoding="utf-8"?>
<!-- Apr 13 2023 version  -->
<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
	 viewBox="120 155 534 176" xml:space="preserve">
<style type="text/css">
	.st0{fill:#CFDEE2;} <!-- WaveColor -->
	.st1{fill:none;stroke:#000000; }
	.st2{fill:#D4D2D2;stroke:#000000; } <!-- Background wave -->
	.st3{fill:#FFFFFF;stroke:#000000; } <!--White Fill -->
	.st4{fill:#5AC1A4;stroke:#000000; } <!--Green Fill -->
	.st5{fill:#FFE850;stroke:#000000; } <!--Yellow Fill -->
	.st6{fill:#EF9D30;stroke:#000000; } <!--Orange Fill -->
	.st7{fill:#FFFFFF;stroke:#000000;stroke-linecap:round; }
	.st8{fill:#C6C4C4;stroke:#000000;stroke-linecap:round; }
	.st9{font-family:HelveticaNeue, Helvetica, Arial, sans-serif;}
	.st10{font-size:9px;}
	.st11{fill:#6D6E6E;stroke:#000000; } <!-- DarkGray Fill-->
	.st12{fill:#606060;}  <!--MidGray text -->
	.st13{font-size:7px;}
	.st14{font-family:HelveticaNeue-Medium, Helvetica, Arial, sans-serif; }
	.st15{font-size:11px;}
	.st16{fill:#A2A0A0;} <!-- Arrow gray-->
	.st17{fill:#e3cfa7;} <!-- DirtBrown-->
	.st18{fill:none;stroke:none; } <!--invisible-->
	.st19{fill:#555555;stroke:#000000;stroke-miterlimit:10;}  <!-- Cart color -->
	.st20{fill:#e3cfa7;stroke:#000000;stroke-miterlimit:10;}  <!-- Circle color -->
	.st21{fill:none;stroke:#46A247;stroke-width:4;stroke-miterlimit:10;} <!-- old small cable color -->
	.st22{fill:none;stroke:#555555;stroke-width:9;stroke-linecap:round;stroke-miterlimit:10;} <!-- big cablecolor -->
	.st23{fill:none;stroke:#46A247;stroke-width:4;stroke-miterlimit:10;} <!-- small cable color2 -->
	.st24{font-size:6px;}
	.st25{fill:#5AC1A4;stroke:none; } <!--Green No Stroke -->
	.st26{fill:#FFE850;stroke:none; } <!--Yellow No Stroke -->
	.st27{fill:#EF9D30;stroke:none; } <!--Orange No Stroke -->	
	.st28{fill:#333333; } <!-- DarkGray Fill-->
	.st30{font-size:8px;} 
	.st31{fill:#B4372D;} <!-- Maroon text-->
	.st32{fill:#aaaaaa;stroke:#000000; } <!-- LighterGray Fill-->
	.st33{fill:#FFEEBB;stroke:none; } <!--PaleYellow No Stroke -->
	.stleak2{fill:#7DA6D8;} <!-- critical water leak-->
	.stleak1{fill:#92c19b;} <!--aux water leak-->
	.sparkbg{fill:#E8E8F0;stroke:none; } <!-- light bluegray Fill-->
	.sparkline{fill:none;stroke:#000000; stroke-width:0.2;}  <!-- changed from black to invisible line -->
	.sparkpoly{fill:#549fd4;stroke:none; } <!--seafoamgreen No Stroke -->	
	.sparktext{font-size:6px; } 
	.gridline{fill:none;stroke:#BBBBBB; stroke-width:0.3;}  
	</style>
'''

svgtext = '''
<rect desc="backgroundbox" x="126.91" y="161.76" class="st3" width="514.08" height="156.08"/>
<!-- Background wave -->
<g transform="translate(0 8)">
	<g>
		<path class="{color_wavecolor}" d="M640.68,200.81v108.71H126.47V198.07l5.36,0.98c10.57-0.98,15.74-8.04,15.74-8.04l0.18,0.2
			c0,0,3.21,10.75,14.54,10.32c11.33-0.43,18.44-11.08,18.44-11.08s3.19,9.61,16.79,9.09c13.6-0.52,14.98-8.01,14.98-8.01
			s3.95,9.58,16.03,9.12c12.09-0.46,16.47-9.21,16.47-9.21s3.93,8.43,14.49,7.46c10.57-0.98,15.74-8.04,15.74-8.04
			s3.15,8.92,11.62,8.92c8.47,0,16.04-8.38,16.04-8.38s3.21,10.75,14.54,10.32c11.33-0.43,18.44-11.08,18.44-11.08
			s3.19,9.61,16.79,9.09c13.6-0.52,14.98-8.01,14.98-8.01s3.95,9.58,16.03,9.12c12.09-0.46,16.47-9.21,16.47-9.21
			s3.93,8.43,14.49,7.46c10.57-0.98,15.74-8.04,15.74-8.04l0.18,0.2c0,0,3.21,10.75,14.54,10.32c11.33-0.43,18.44-11.08,18.44-11.08
			s3.19,9.61,16.79,9.09c13.6-0.52,14.98-8.01,14.98-8.01s3.95,9.58,16.03,9.12c12.09-0.46,16.47-9.21,16.47-9.21
			s3.93,8.43,14.49,7.46c10.57-0.98,15.74-5.72,15.74-5.72s5,8.97,16.33,8.54c11.33-0.43,18.44-11.08,18.44-11.08
			s3.19,9.61,16.79,9.09c13.6-0.52,14.98-8.01,14.98-8.01S628.59,201.27,640.68,200.81"/>
	</g>
</g>
<rect desc="dirtbox" x="126.91" y="281.76" class="{color_dirtbox}" width="514.08" height="36.08"/>
<rect desc="backgroundbox" x="126.91" y="161.76" class="st1" width="514.08" height="156.08"/>
<line desc="bigcable" class="{color_bigcable}" x1="250.77" y1="292.21" x2="268.73" y2="281.71"/>
<path desc="smallcable" class="{color_smallcable}" d="M137.01,323.1c0,0,7.44-8.93,20.84-8.93s20.85,8.93,42.05,8.93s29.77-18.98,47.66-28.86"/>

<!-- AUV Body -->
<path class="st2" d="M554.57,292.12l-279.27,0l0-60.4l279.27,0c16.68,0,30.2,13.52,30.2,30.2v0
	C584.77,278.6,571.25,292.12,554.57,292.12z"/>
	
<polygon class="st3" points="154.9,269.51 275.29,292.12 275.29,231.72 154.9,254.33 "/>
<polygon class="st3" points="255.42,235.44 244.05,237.4 244.8,189.82 255.99,186.82 "/>

<!-- add new overcurrent lights -->
<text desc="HardwareLabel" text-anchor="right" transform="matrix(1 0 0 1 245 254)" class="st9 st10">HW</text>
<text desc="SoftwareLabel" text-anchor="right" transform="matrix(1 0 0 1 245 267)" class="st9 st10">SW</text>
<text desc="OtherLabel"    text-anchor="right" transform="matrix(1 0 0 1 245 280)" class="st9 st10">OT</text>

<!-- battery consumption meter -->
<text desc="text_batteryduration" x="372" y="255"  class="st12 st9 st13">{text_batteryduration}</text>
<rect desc="current"  x="365" y="250" class="st32" width="5" height="22"/>
<text desc="text_current" x="372" y="267"  class="st12 st9 st13">{text_current}</text>
{svg_current}


<!-- status shapes -->

<rect desc="drop" x="284.79" y="282.44" class="{color_drop}" width="24.43" height="9.5"/>
<g><title>Ground Fault: None means not detected. False means no recent scan</title>
<line class="st7" x1="475.36" y1="256.18" x2="475.36" y2="267.72"/> <!-- Ground fault -->
<line class="st7" x1="468.58" y1="268.37" x2="482.15" y2="268.37"/>
<line class="st7" x1="469.91" y1="270.59" x2="480.82" y2="270.59"/>
<line class="st7" x1="471.24" y1="272.82" x2="479.49" y2="272.82"/>
</g>
<line class="st8" x1="472.57" y1="275.05" x2="478.16" y2="275.05"/> <!-- not sure -->
<circle desc="thrust" class="{color_thrust}" cx="175.51" cy="261.61" r="8.15"/>
<!--<circle desc="gf" class="st6" cx="488.44" cy="259.45" r="8.15"/>-->

<!--<circle desc="bat1" class="{color_bat1}" cx="295" cy="241.38" r="4"/>-->
<g><title>Batteries in 0.5 increment from 13.5 to 16.5</title>
<circle desc="bat1" class="{color_bat1}" cx="309" cy="241.38" r="4"/>
<circle desc="bat2" class="{color_bat2}" cx="319" cy="241.38" r="4"/>
<circle desc="bat3" class="{color_bat3}" cx="329" cy="241.38" r="4"/>
<circle desc="bat4" class="{color_bat4}" cx="339" cy="241.38" r="4"/>
<circle desc="bat5" class="{color_bat5}" cx="349" cy="241.38" r="4"/>
<circle desc="bat6" class="{color_bat6}" cx="359" cy="241.38" r="4"/>
<circle desc="bat7" class="{color_bat7}" cx="369" cy="241.38" r="4"/>
<circle desc="bat8" class="{color_bat8}" cx="379" cy="241.38" r="4"/>
</g>


<circle desc="CTD" class="{color_ctd}" cx="544" cy="241" r="4" /> 
<circle desc="missiondefault"   class="{color_missiondefault}" cx="405" cy="183" r="2"/>
<circle desc="scheduleddefault" class="{color_scheduled}"      cx="405" cy="193.5" r="1.6"/>
<circle desc="commoverdue"     class="{color_commago}"        cx="138.5" cy="295.5" r="2"/>
<circle desc="missionoverdue"     class="{color_missionago}"     cx="138.5" cy="306" r="2"/>
<rect desc="satcomm" x="261.49" y="182.98" class="{color_satcomm}" width="24.43" height="11.5"/>
<rect desc="cell"    x="260.15" y="212.24" class="{color_cell}" width="26.43" height="11.31"/>
<rect desc="gps"     x="407.76" y="221.71" class="{color_gps}" width="26.93" height="10.17"/>
<rect desc="amps"    x="336.28" y="261.76" class="{color_amps}" width="25.5" height="10.5"/>
<rect desc="volts"   x="336.28" y="249.85" class="{color_volts}" width="25.5" height="10.5"/>
<rect desc="gf_rect" x="480" y="254.0" class="{color_gf}" width="24.43" height="10.5"/>
<circle desc="HW" class="{color_hw}" cx="267" cy="251" r="4" /> 
<circle desc="SW" class="{color_sw}" cx="267" cy="264" r="4"/>
<circle desc="OT" class="{color_ot}" cx="267" cy="277" r="4" /> 


<polygon desc="dvl" class="{color_dvl}" points="541.91,287.26 553.41,287.26 558.97,295.79 541.52,295.79 "/>

<!--cart-->
<polygon desc="cart" class="{color_cart}" points="348.8,282.24 348.8,315.73 524.05,315.73 524.05,282.24 503.4,282.24 496.15,301.22 381.17,301.22 
	369.22,282.74 "/>
<circle desc="circle1" class="{color_cartcircle}" cx="362.59" cy="298.44" r="5.86"/>
<circle desc="circle2" class="{color_cartcircle}" cx="510.1" cy="298.44" r="5.86"/>

<!--pontus specific but can be made invisible-->
<text desc="text_flowago" transform="matrix(1 0 0 1 541.0 272.0)" class="st12 st9 st13">{text_flowago}</text>
<circle desc="UBAT" class="{color_ubat}" cx="544" cy="251" r="4" /> 
<circle desc="flow" class="{color_flow}" cx="544" cy="261" r="4"/>
<!-- end shapes -->


<!-- future <text desc="" transform="matrix(1 0 0 1 557.3993 228.8362)" class="st9 st10">B&amp;T?</text>
<circle desc="BT2" class="{color_bt2}" cx="546.72" cy="225.78" r="4.07"/>
<circle desc="BT1" class="{color_bt1}" cx="535.99" cy="225.78" r="4.07"/>
-->

<g desc="arrow" transform="rotate (-90,604.94,259.74), rotate({text_arrow},605,259.74)">
    <rect x="594.14" y="256.24" class="st16" width="11.73" height="7"/>
    <g>
        <polygon class="st16" points="618.22,259.74 600.81,266.86 604.94,259.74 600.81,252.63       "/>
    </g>
</g>

<!-- Dynamic values -->
<text desc="mission" transform="matrix(1 0 0 1 452.0 186)" class="st9 st10 st12">{text_mission}</text>
<text desc="missionsched" transform="matrix(1 0 0 1 409.5 196)" class="st12 st9 st13">{text_scheduled}</text>
<text desc="text_cell" transform="matrix(1 0 0 1 262.2472 221.3249)" class="st9 st10">{text_cell}</text>
<text desc="text_sat" transform="matrix(1 0 0 1 262.2478 192.1254)" class="st9 st10">{text_sat}</text>
<text desc="text_gps" transform="matrix(1 0 0 1 410.1005 229.6799)" class="st9 st10">{text_gps}</text>
<text desc="text_bearing" transform="matrix(1 0 0 1 596 262.3)" class="st9 st13">{text_bearing}</text>
<text desc="text_thrusttime" transform="matrix(1 0 0 1 592 276.3205)" class="st9 st10">{text_thrusttime}</text>
<text desc="text_nextcomm" transform="matrix(1 0 0 1 195 298.3899)" class="st9 st10">{text_nextcomm}</text>
<text desc="text_timeout"  transform="matrix(1 0 0 1 195 309.1899)" class="st9 st10">{text_timeout}</text>
<text desc="text_commago" transform="matrix(1 0 0 1 339.0 191.2224)" class="st12 st9 st13">{text_commago}</text>
<text desc="text_logtime" transform="matrix(1 0 0 1 185.0 221.6039)" class="st9 st10">{text_logtime}</text>
<text desc="text_logago" transform="matrix(1 0 0 1 185.0 231.2224)" class="st12 st9 st13">{text_logago}</text>
<text desc="text_cellago" transform="matrix(1 0 0 1 342.0 221.2224)" class="st12 st9 st13">{text_cellago}</text>
<text desc="text_volts" transform="matrix(1 0 0 1 338.0 257.9931)" class="st9 st10">{text_volts}</text>
<text desc="text_amps" transform="matrix(1 0 0 1 338.0 270.4917)" class="st9 st10">{text_amps}</text>
<text desc="text_ampago" transform="matrix(1 0 0 1 330.0 280.0)" class="st12 st9 st13">{text_ampago}</text>
<text desc="text_droptime" transform="matrix(1 0 0 1 285 307)" class="st12 st9 st13">{text_droptime}</text>
<text desc="text_gftime" transform="matrix(1 0 0 1 479.3629 250)" class="st12 st9 st13">{text_gftime}</text>
<text desc="text_gpsago" transform="matrix(1 0 0 1 481 226.5)" class="st12 st9 st13">{text_gpsago}</text>
<text desc="text_gf" transform="matrix(1 0 0 1 482 262.4973)" class="st9 st10">{text_gf}</text>
<text desc="text_speed" transform="matrix(1 0 0 1 198.0612 270)" class="st12 st9 st13">{text_speed}<title>Speed estimated from last two GPS fixes</title></text>
<text desc="text_vehicle" transform="matrix(1 0 0 1 400 254.7336)" class="st14 st15">{text_vehicle}</text>
<text desc="text_lastupdate" transform="matrix(1 0 0 1 406.0 280.0)" class="st14 st15">{text_lastupdate}</text>
<text desc="reckoned_detail" transform="matrix(1 0 0 1 592 293)" class="st12 st9 st24">{text_reckondistance}</text>
<text desc="text_arrivestation" transform="matrix(1 0 0 1 581 230)" class="st9 st13">{text_arrivestation}</text>
<text desc="text_stationdist" transform="matrix(1 0 0 1 582 238)" class="st12 st9 st24">{text_stationdist}</text>
<text desc="text_currentdist" transform="matrix(1 0 0 1 582 245)" class="st12 st9 st24">{text_currentdist}</text>
<text desc="text_dvlstatus" transform="matrix(1 0 0 1 542 304)" class="st12 st9 st13">{text_dvlstatus}</text>
<text desc="text_criticalerror" transform="matrix(1 0 0 1 352.0 300)" class="st9 st30 st31">{text_criticalerror}</text>
<text desc="text_criticaltime" transform="matrix(1 0 0 1 354 307)" class="st12 st9 st13">{text_criticaltime}</text>



<!-- Static labels -->  
<text transform="matrix(1 0 0 1 409.0 186)" class="st9 st10">MISSION:</text>
<text transform="matrix(1 0 0 1 404.0 268.0)" class="st12 st9 st13">UPDATED:</text>
'''
svglabels='''
<!-- create new variable for these -->
<text desc="reckoned_label" transform="matrix(1 0 0 1 592 286)" class="st12 st9 st24">reckoned<title>Speed estimated from last two GPS fixes</title></text>
<text desc="speeded_label" transform="matrix(1 0 0 1 199 275)" class="st12 st9 st24">command</text>
<text transform="matrix(1 0 0 1 308.64 258.2642)" class="st9 st10">Volts:</text>
<text transform="matrix(1 0 0 1 304.7791 270.4165)" class="st9 st10">AmpH:</text>
<text desc="text_amplabel" x="372" y="272" class="st12 st9 st24">amps</text>
<text desc="text_durationlabel" x="372" y="260" class="st12 st9 st24">hours</text>
<text transform="matrix(1 0 0 1 285 300)" class="st12 st9 st13">DROP WEIGHT</text>
<text transform="matrix(1 0 0 1 143.5453 298.3899)" class="st9 st10">NextComm:</text>
<text transform="matrix(1 0 0 1 143.0 309.1899)" class="st9 st10">Timeout: </text>
<text desc="" transform="matrix(1 0 0 1 551 244)" class="st9 st10">CTD</text>

<g><title>Ground Fault: None means not detected. False means no recent scan</title>
<text transform="matrix(1 0 0 1 485 273)" class="st12 st9 st13">GROUND</text>
<text transform="matrix(1 0 0 1 485 281)" class="st12 st9 st13">FAULT</text>
</g>
<text transform="matrix(1 0 0 1 540.0956 283.4494)" class="st9 st10">DVL</text>
<text transform="matrix(1 0 0 1 439.3514 226.8654)" class="st9 st10">Last GPS</text>
<text transform="matrix(1 0 0 1 289.4541 191.2224)" class="st9 st10">Sat comms</text>
<text transform="matrix(1 0 0 1 291.6499 221.6039)" class="st9 st10">Cell comms</text>
<text transform="matrix(1 0 0 1 144.0 221.6039)" class="st9 st10">Log start:</text>
<text transform="matrix(1 0 0 1 193.9667 260.552)" class="st9 st10">Thruster</text>
<text desc="arrive_label" transform="matrix(1 0 0 1 580 222)" class="st12 st9 st24">Arrive Waypoint</text>
'''

svgbadbattery='''<g><title>Bad battery cell detected</title>
	<circle desc="badbatteryspot" class="st28" cx="309" cy="241.38" r="2"/>
	<circle desc="badbatteryspot" class="st28" cx="329" cy="241.38" r="2"/>
	<circle desc="badbatteryspot" class="st28" cx="349" cy="241.38" r="2"/>
	<circle desc="badbatteryspot" class="st28" cx="369" cy="241.38" r="2"/>
	<text transform="matrix(1 0 0 1 286.0 242)" class="st12 st9 st13">BAD</text>
	<text transform="matrix(1 0 0 1 286.0 249)" class="st12 st9 st13">CELL</text>
	{badcelltext}
</g>	
'''



svgpontus='''
<!-- vehicle-specific shapes -->
<text desc="" transform="matrix(1 0 0 1 551.3628 254.5)" class="st9 st10">UBAT</text>
<text desc="" transform="matrix(1 0 0 1 551.3628 264.5)" class="st9 st10">Flow</text>
'''

svgwaterleak='''<!--water leak-->
<g transform="translate(119.3 -107.2)">
<path class="{color_leak}" d="M422,396.5v2.2H190.4v-3.1l2.4,0.3c4.8-0.3,7.1-2.8,7.1-2.8l0.1,0.1c0,0,1.4,3.7,6.6,3.6
	c5.1-0.1,8.3-3.8,8.3-3.8s1.4,3.3,7.6,3.1s6.8-2.8,6.8-2.8s1.8,3.3,7.2,3.1c5.5-0.2,7.4-3.2,7.4-3.2s1.8,2.9,6.5,2.6
	c4.8-0.3,7.1-2.8,7.1-2.8s1.4,3.1,5.2,3.1c3.8,0,7.2-2.9,7.2-2.9s1.4,3.7,6.6,3.6c5.1-0.1,8.3-3.8,8.3-3.8s1.4,3.3,7.6,3.1
	s6.8-2.8,6.8-2.8s1.8,3.3,7.2,3.1c5.5-0.2,7.4-3.2,7.4-3.2s1.8,2.9,6.5,2.6c4.8-0.3,7.1-2.8,7.1-2.8l0.1,0.1c0,0,1.4,3.7,6.6,3.6
	c5.1-0.1,8.3-3.8,8.3-3.8s1.4,3.3,7.6,3.1c6.1-0.2,6.8-2.8,6.8-2.8s1.8,3.3,7.2,3.1c5.5-0.2,7.4-3.2,7.4-3.2s1.8,2.9,6.5,2.6
	c4.8-0.3,7.1-2,7.1-2s2.3,3.1,7.4,2.9s8.3-3.8,8.3-3.8s1.4,3.3,7.6,3.1c6.1-0.2,6.8-2.8,6.8-2.8s1.8,3.3,7.3,3.1"/>
</g>
<text transform="matrix(1 0 0 1 439 290.0)" class="st12 st9 st13">{text_leak}{text_leakago}</text>

'''

svgtail = '''
</svg>
'''

svgstickynote = '''<rect desc="stickyrect" x="409" y="166" class="st33" width="180" height="11.5"/>
<text desc="sticky" transform="matrix(1 0 0 1 412.0 175)" class="st9 st13 st28">{text_note}</text>
<text desc="stickyago" transform="matrix(1 0 0 1 591.0 176)" class="st9 st24 st12">{text_noteago}</text>
<text desc="noteago"   transform="matrix(1 0 0 1 591.0 171)" class="st9 st24 st12">#note</text>'''



svgerrorhead =  '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" 
	id="Layer_1" width="514" height="156" viewbox = "0 0 514 156" xml:space="preserve">
<style type="text/css">
	.st0{fill:#EEAA88;} <!-- WaveColor -->
	.st9{font-family:'HelveticaNeue';}
	.st10{font-size:14px;}
	.st11{fill:#6D6E6E;stroke:#000000; } <!-- DarkGray Fill-->
	.st12{fill:#606060;}  <!--MidGray text -->
	</style>
'''
svgerror ='''<rect desc="backgroundbox" class="st0" width="512" height="154"/>
		<text desc="text_vehicle" x="50%" y="40%" text-anchor="middle" class="st9 st10 st12">COMMS INTERRUPTED: {text_vehicle}</text>
		<text desc="text_lastupdate" x="50%" y="55%" text-anchor="middle" class="st9 st10 st12">{text_lastupdate}</text>
		
</svg>
'''
