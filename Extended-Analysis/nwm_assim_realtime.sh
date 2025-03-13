#!/bin/bash
#####################################################################
## CREATED: JAN 2023                                                #
# EDIT HISTORY :                                                    #
#                                                                   #
#####################################################################
#####################################################################
# CODE PURPOSE:                                                     #
# obtain real time National Water Model Data for Long Range         #
# forecasts                                                         #
#                                                                   #
#####################################################################
# contact: yhon@umich.edu
#altered from James Kessler original code (nwm_from_archive.sh)
start=`date +%s` #get start time so we can determine how long our code is running
base_url='https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/v3.0/'
t0=`date +%Y%m%d -d "1 days ago"`        # first record to grab
tf=`date +%Y%m%d`
long=1 # get long fc
YYYYMMDD=$t0

# =====================================================================================================
# ============================  get long range forecast (init hours 0) ==================================
# =====================================================================================================

if [ $long == 1 ]; then
echo downloading 30 day  FC\'s...
YYYYMMDD=$t0
fhours=`seq -w 0 1 27`
cd nwm_assim_ext_rt/
mkdir $YYYYMMDD

while [[ ${YYYYMMDD} -le $tf ]]; do
        echo -n ${YYYYMMDD}:
	#download
	for fhour in ${fhours}; do
		echo $fhour
	        wget -P ${YYYYMMDD} ${base_url}nwm.${YYYYMMDD}/analysis_assim_extend/nwm.t16z.analysis_assim_extend.channel_rt.tm${fhour}.conus.nc
	done
        YYYYMMDD=$(date -d "$YYYYMMDD + 1 days" +%Y%m%d) #may not work in mac but work in linux
	mkdir ${YYYYMMDD}
done
fi


end=`date +%s` #doesnt work for mac nanoseconds
runtime=$((end-start))
echo $runtime
