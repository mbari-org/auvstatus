#! /bin/bash
VEH='tethys galene daphne pontus triton makai brizo ahi sim'
for v in $VEH; do rm -f /var/www/html/widget/auv_$v.svg; python3 /var/www/html/widget/auvstatus.py -v $v -f; done
#for v in $VEH; do python3 /var/www/html/widget/auvstatus.py -v $v -f; done

# these should be ready for python3, but untested
python3 /var/www/html/widget/esp_widget.py -v makai -f
python3 /var/www/html/widget/esp_widget.py -v brizo -f
python3 /var/www/html/widget/esp_widget.py -v daphne -f
