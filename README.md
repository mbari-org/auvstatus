## LRAUV monitoring widget

Usage:

    auvstatus.py -v pontus -r   # prints a report to the screen
    auvstatus.py -v daphne -f   # save to file called auv_daphne.svg

   -v --vehicle specifies the vehicle
   -b           turns on debugging output
   -r           prints report
   -f           save to SVG file directly

### NOTES

  * It is in python 2.7 (lazy) but should only require built-in libraries
  * `LRAUV_svg.py` contains the template for substitution of style fields
  * It needs to reside in the same folder as auvstatus to be imported
  * Opening the SVG in an illustration program will reformat it 
  * This alpha version is very FRAGILE and can crash with unexpected input
  * There is a auto-refreshing version at http://jellywatch.org/auv.html
     - Could add daphne as a second panel below and add to crontab

## TODO

  * Long list of TODOs in the code, but caching GPS so it is robust between `restart logs`
