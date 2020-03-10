#! /bin/bash
#VEH='daphne pontus tethys galene sim triton makai'
VEH='daphne pontus makai'
rm -f auv_*.svg; for v in $VEH; do ./auvstatus.py -v $v -f; done
