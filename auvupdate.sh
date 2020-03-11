#! /bin/bash
#VEH='daphne pontus tethys galene triton makai brizo sim'
VEH='daphne pontus tethys galene triton makai'
rm -f /var/www/html/widget/auv_*.svg
for v in $VEH; do /var/www/html/widget/auvstatus.py -v $v -f; done
