#! /bin/bash
VEH='daphne pontus tethys galene sim triton makai'
for v in $VEH; do /var/www/html/widget/auvstatus.py -v $v -f; done