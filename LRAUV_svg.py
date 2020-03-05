svghead = '''<?xml version="1.0" encoding="utf-8"?>
<!-- March 3, 2020 version  -->
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

<!-- AUV Body -->
<path class="st2" d="M554.57,292.12l-279.27,0l0-60.4l279.27,0c16.68,0,30.2,13.52,30.2,30.2v0
	C584.77,278.6,571.25,292.12,554.57,292.12z"/>
	
<polygon class="st3" points="154.9,269.51 275.29,292.12 275.29,231.72 154.9,254.33 "/>
<polygon class="st3" points="255.42,235.44 244.05,237.4 244.8,183.82 255.99,180.82 "/>

<!-- status shapes -->

<rect desc="drop" x="284.79" y="282.44" class="{color_drop}" width="24.43" height="9.5"/>
<line class="st7" x1="475.36" y1="256.18" x2="475.36" y2="267.72"/>
<line class="st7" x1="468.58" y1="268.37" x2="482.15" y2="268.37"/>
<line class="st7" x1="469.91" y1="270.59" x2="480.82" y2="270.59"/>
<line class="st7" x1="471.24" y1="272.82" x2="479.49" y2="272.82"/>
<line class="st8" x1="472.57" y1="275.05" x2="478.16" y2="275.05"/> <!-- not sure -->
<circle desc="thrust" class="{color_thrust}" cx="175.51" cy="261.61" r="8.15"/>
<!--<circle desc="gf" class="st6" cx="488.44" cy="259.45" r="8.15"/>-->

<circle desc="bat1" class="{color_bat1}" cx="301.88" cy="241.38" r="4.07"/>
<circle desc="bat2" class="{color_bat2}" cx="312.19" cy="241.38" r="4.07"/>
<circle desc="bat3" class="{color_bat3}" cx="322.5" cy="241.38" r="4.07"/>
<circle desc="bat4" class="{color_bat4}" cx="332.81" cy="241.38" r="4.07"/>
<circle desc="bat5" class="{color_bat5}" cx="343.12" cy="241.38" r="4.07"/>
<circle desc="bat6" class="{color_bat6}" cx="353.43" cy="241.38" r="4.07"/>
<circle desc="bat7" class="{color_bat7}" cx="363.74" cy="241.38" r="4.07"/>
<!--<circle desc="bat8" class="st2" cx="374.05" cy="241.38" r="4.07"/>-->

<rect desc="satcomm" x="261.49" y="182.98" class="{color_satcomm}" width="24.43" height="11.5"/>
<rect desc="cell"    x="260.15" y="212.24" class="{color_cell}" width="26.43" height="11.31"/>
<rect desc="gps"     x="407.76" y="221.71" class="{color_gps}" width="26.93" height="10.17"/>
<rect desc="amps"    x="336.28" y="261.76" class="{color_amps}" width="25.5" height="10.5"/>
<rect desc="volts"   x="336.28" y="249.85" class="{color_volts}" width="25.5" height="10.5"/>
<rect desc="gf_rect" x="480" y="254.0" class="{color_gf}" width="24.43" height="10.5"/>
<polygon desc="sonar" class="{color_sonar}" points="541.91,287.26 553.41,287.26 558.97,295.79 541.52,295.79 "/>
<!-- end shapes -->


<!-- future <text desc="" transform="matrix(1 0 0 1 557.3993 228.8362)" class="st9 st10">B&amp;T?</text>
<circle desc="BT2" class="{color_bt2}" cx="546.72" cy="225.78" r="4.07"/>
<circle desc="BT1" class="{color_bt1}" cx="535.99" cy="225.78" r="4.07"/>
-->

<!-- vehicle-specific shapes -->
<circle desc="UBAT" class="{color_ubat}" cx="543.96" cy="246.8" r="4.07" /> 
<circle desc="flow" class="{color_flow}" cx="544.33" cy="259.45" r="4.07"/>
<text desc="" transform="matrix(1 0 0 1 551.3628 250.3636)" class="st9 st10">UBAT</text>
<text desc="" transform="matrix(1 0 0 1 551.3628 263.259)" class="st9 st10">FLOW</text>
<text desc="text_flowago" transform="matrix(1 0 0 1 541.0 272.0)" class="st12 st9 st13">{text_flowago}</text>

<!-- Dynamic values -->
<text desc="mission" transform="matrix(1 0 0 1 482.0 191.2224)" class="st9 st10 st12">{text_mission}</text>
<text desc="text_cell" transform="matrix(1 0 0 1 262.2472 221.3249)" class="st9 st10">{text_cell}</text>
<text desc="text_sat" transform="matrix(1 0 0 1 262.2478 192.1254)" class="st9 st10">{text_sat}</text>
<text desc="text_gps" transform="matrix(1 0 0 1 410.1005 229.6799)" class="st9 st10">{text_gps}</text>
<text desc="text_speed" transform="matrix(1 0 0 1 597.9696 276.3205)" class="st9 st10">{text_speed}</text>
<text desc="text_commgroup" transform="matrix(1 0 0 1 197.0165 298.3899)">
<tspan desc="text_nextcomm" x="0" y="0" class="st9 st10">{text_nextcomm}</tspan>
<tspan desc="text_timeout" x="0" y="10.8" class="st9 st10">{text_timeout}</tspan></text>
<text desc="text_commago" transform="matrix(1 0 0 1 339.0 191.2224)" class="st12 st9 st13">{text_commago}</text>
<text desc="text_cellago" transform="matrix(1 0 0 1 342.0 221.2224)" class="st12 st9 st13">{text_cellago}</text>
<text desc="text_volts" transform="matrix(1 0 0 1 338.0 257.9931)" class="st9 st10">{text_volts}</text>
<text desc="text_amps" transform="matrix(1 0 0 1 338.0 270.4917)" class="st9 st10">{text_amps}</text>
<text desc="text_ampago" transform="matrix(1 0 0 1 330.0 280.0)" class="st12 st9 st13">{text_ampago}</text>
<text desc="text_droptime" transform="matrix(1 0 0 1 342.619 301.9217)" class="st12 st9 st13">{text_droptime}</text>
<text desc="text_gftime" transform="matrix(1 0 0 1 479.3629 247.7823)" class="st12 st9 st13">{text_gftime}</text>
<text desc="text_gf" transform="matrix(1 0 0 1 484 262.4973)" class="st9 st10">{text_gf}</text>
<text desc="text_thrusttime" transform="matrix(1 0 0 1 198.0612 272.3985)" class="st12 st9 st13">{text_thrusttime}</text>
<text desc="text_vehicle" transform="matrix(1 0 0 1 398.7397 254.7336)" class="st14 st15">{text_vehicle}</text>
<text desc="text_lastupdate" transform="matrix(1 0 0 1 407.5942 268.0188)" class="st14 st15">{text_lastupdate}</text>

<!-- Static labels -->
<text desc="" transform="matrix(1 0 0 1 308.64 258.2642)" class="st9 st10">Volts:</text>
<text desc="" transform="matrix(1 0 0 1 304.7791 270.4165)" class="st9 st10">AmpH:</text>
<text desc="" transform="matrix(1 0 0 1 289.7587 302.4895)" class="st9 st10">Drop Weight</text>
<text desc="" transform="matrix(1 0 0 1 143.5453 298.3899)" class="st9 st10">NextComm:</text>
<text desc="" transform="matrix(1 0 0 1 143.0 309.1899)" class="st9 st10">Timeout: </text>
<text desc="" transform="matrix(1 0 0 1 482.912 279.8586)" class="st9 st10">GF</text>
<text desc="" transform="matrix(1 0 0 1 540.0956 283.4494)" class="st9 st10">DVL</text>
<text desc="" transform="matrix(1 0 0 1 439.3514 226.8654)" class="st9 st10">Last GPS</text>
<text desc="" transform="matrix(1 0 0 1 289.4541 191.2224)" class="st9 st10">Sat comms</text>
<text desc="" transform="matrix(1 0 0 1 439.0 191.2224)" class="st9 st10">MISSION:</text>
<text desc="" transform="matrix(1 0 0 1 291.6499 221.6039)" class="st9 st10">Cell comms</text>
<text desc="" transform="matrix(1 0 0 1 193.9667 264.552)" class="st9 st10">Thruster</text>

<g desc="arrow">
	<rect x="594.14" y="256.24" class="st16" width="11.73" height="7"/>
	<g>
		<polygon class="st16" points="618.22,259.74 600.81,266.86 604.94,259.74 600.81,252.63 		"/>
	</g>
</g>
</svg>
'''
