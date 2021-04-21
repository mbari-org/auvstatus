#! /bin/bash
#VEH='daphne pontus tethys galene triton makai brizo sim'
VEH='pontus  galene triton'

for v in $VEH; do rm -f /var/www/html/widget/auv_$v.svg; /var/www/html/widget/auvstatus.py -v $v -f; done
