#!/bin/bash
# contact: yhon@umich.edu
#####################################################################
## CREATED: Nov 2024                                                #
# EDIT HISTORY :                                                    #
#                                                                   #
#####################################################################
#####################################################################
# CODE PURPOSE:                                                     #
# obtain National Water Model V3.0 Retrospective Data         #
#  Stream flow data (CHRTOUT)                                              #
#####################################################################

start=`date +%s`
base_url='https://noaa-nwm-retrospective-3-0-pds.s3.amazonaws.com/CONUS/netcdf/CHRTOUT/' #use with wget

# Example download Link
# https://noaa-nwm-retrospective-3-0-pds.s3.amazonaws.com/CONUS/netcdf/CHRTOUT/2023/202301301600.CHRTOUT_DOMAIN1

# =====================================================================================================
# ============================   Download =========================================================
# =====================================================================================================
#change based on which days of data you want to download
t0=19920609        # first record to grab
tf=19941231

t0_Y=1992        # first record to grab
tf_Y=1994

#tf=$(date +%Y%m%d) # last record to grab (default: today)

retro=1  # get reanalysis

YYYYMMDD=$t0

#for YY in $(seq $t0_Y 1 $tf_Y); do
#	mkdir /mnt/projects/hpc/hong/NWM3_0/Retrospective/Download/${YY}
#done

if [ $retro == 1 ]; then
echo downloading/processing retrospective/reanalysis files...

hours=`seq -w 0 23` #will create a list of the hours in the day to loop through and download from 
rm -rf temp 2> /dev/null
#loop through all of files within each day (all hours 00-23utc)

while [[ ${YYYYMMDD} -le $tf ]]; do
	mkdir temp
	YYYY=${YYYYMMDD:0:4}
	
	for hour in ${hours}; do
		echo $hour
		echo ${YYYYMMDD}
		YYYY=${YYYYMMDD:0:4}
		echo $YYYY
		wget ${base_url}${YYYY}/${YYYYMMDD}${hour}00.CHRTOUT_DOMAIN1  #use wget to download the NWM files
		#aws s3 cp --no-sign-request ${base_url}${YYYY}/${YYYYMMDD}${hour}00.CHRTOUT_DOMAIN1.comp temp/. #use with aws cli
		mv ${YYYYMMDD}${hour}00.CHRTOUT_DOMAIN1 temp/${YYYYMMDD}${hour}00.CHRTOUT_DOMAIN1.nc
		#myfilesize=$(stat -f "temp/${YYYYMMDD}${hour}00.CHRTOUT_DOMAIN1.nc")
        	#echo "$myfilesize"
	done
	#after downloading the data for one day, average the hourly data into daily data and output one single file with the daily average
	mv temp/*CHRT* /mnt/projects/hpc/hong/NWM3_0/Retrospective/Download/${YYYY}
	# uncomment/comment the code below if want to save hourly/daily data
	nc_filename=`ls /mnt/projects/hpc/hong/NWM3_0/Retrospective/Download/${YYYY}/${YYYYMMDD}*CHRTOUT*`  #get a list of all the files within a year of data
    ncra $nc_filename /mnt/projects/hpc/hong/NWM3_0/Retrospective/Download/${YYYY}/${YYYYMMDD}.nc
    rm /mnt/projects/hpc/hong/NWM3_0/Retrospective/Download/${YYYY}/${YYYYMMDD}*CHRTOUT*
    rm -rf temp
	#YYYYMMDD=$(date -j -v +1d -f "%Y%m%d" "$YYYYMMDD" +%Y%m%d) #mac
	#YYYYMMDD=$(date +%m-%d-%Y -d "$YYYYMMDD + 1 day") #may work on linux and not mac
	#advance to the next day
	YYYYMMDD=$(date -d "$YYYYMMDD + 1 day" +%Y%m%d) #may work on linux and not mac 
	#YYYY=${YYYYMMDD:0:4}
done
fi
#this command is reading how big the data files are 
du -h /mnt/projects/hpc/hong/NWM3_0/Retrospective/Download/*/*.nc > retrospective_filesize.txt
end=`date +%s` #doesnt work for mac nanoseconds

runtime=$((end-start)) #see how long it took for the code to run

echo runtime: $runtime seconds


