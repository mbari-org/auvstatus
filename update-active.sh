#! /bin/bash
#VEH='daphne pontus galene triton tethys makai brizo sim'
VEH='pontus brizo tethys makai'

#for v in $VEH; do rm -f /var/www/html/widget/auv_$v.svg; python2.7 /var/www/html/widget/auvstatus.py -v $v -f; done
for v in $VEH; do python2.7 /var/www/html/widget/auvstatus.py -v $v -f; done
python2.7 /var/www/html/widget/esp_widget.py -v makai -f
python2.7 /var/www/html/widget/esp_widget.py -v brizo -f
