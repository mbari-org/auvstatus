#! /bin/bash
VEH='tethys ahi galene daphne pontus triton makai brizo aku opah sim'
for v in $VEH; do python3 /var/www/html/widget/auvstatus.py -v $v -f; done
#python3 /var/www/html/widget/auvstatus.py -v ahi -f --archiveimage 

# these should be ready for python3, but untested
python3 /var/www/html/widget/esp_widget.py -v makai -f
python3 /var/www/html/widget/esp_widget.py -v brizo -f
python3 /var/www/html/widget/esp_widget.py -v daphne -f
