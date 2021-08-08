#! /bin/bash
VEH='daphne triton makai brizo'

for v in $VEH; do rm -f /var/www/html/widget/auv_$v.svg; python2.7 /var/www/html/widget/auvstatus.py -v $v -f; done
#for v in $VEH; do python2.7 /var/www/html/widget/auvstatus.py -v $v -f; done

# (carlos) ah, seems like the following as well, for the ESP widget itself:
python2.7 /var/www/html/widget/esp_widget.py -v makai -f
python2.7 /var/www/html/widget/esp_widget.py -v brizo -f
