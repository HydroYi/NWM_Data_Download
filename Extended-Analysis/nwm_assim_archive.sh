#!/bin/bash
# contact: yhon@umich.edu
#####################################################################
## CREATED: JAN 2023                                                #
# EDIT HISTORY :                                                    #
# Modified by Hong March 2025, automatcially set date                                                                  #
#####################################################################
#####################################################################
# CODE PURPOSE:                                                     #
# obtain archived National Water Model analysis and assimilation    #
# files. Can select if you want to download long range analysis,
# extended analysis, and standard analysis files.
#                                                                   #
#####################################################################
#altered from James Kessler original code (nwm_from_archive.sh)
start=`date +%s.%N`  #get start time so we can determine how long our code is running
base_url='gs://national-water-model'
# Get the first day of the previous month
t0=$(date -d "$(date +%Y-%m-01) -1 month" +%Y%m01)
# Need to get the first day of the current month as the end day
# tf=$(date -d "$(date +%Y-%m-01) -1 day" +%Y%m%d)
tf=$(date +%Y%m01)

# it is possible to set the dates manually if needed
# t0=20241201        # first record to grab
# tf=20241231

# Print the dates for verification
echo "Start date: $t0"
echo "End date: $tf"

std=0  # get standard analysis? retropsective
ext=1  # get extended analysis?
lr=0   # get long range analysis?
# =====================================================================================================
# ============================   get analysis =========================================================
# =====================================================================================================
YYYYMMDD=$t0

if [ $std == 1 ]; then   # retrospective
echo downloading/processing standard analysis files...
cd nwm_assim_std/

hours=`seq -w 0 23`
mkdir $YYYYMMDD

rm -rf temp
while [[ ${YYYYMMDD} -le $tf ]]; do
        mkdir temp
	for hour in ${hours}; do
        	echo ${YYYYMMDD}
        	gsutil cp ${base_url}/nwm.${YYYYMMDD}/analysis_assim/nwm.t${hour}z.analysis_assim.channel_rt.tm00.conus.nc temp
        	myfilesize=$(stat -f  "temp/nwm.t${hour}z.analysis_assim.channel_rt.tm00.conus.nc")
        	echo "$myfilesize"
	done
        mv temp/*channel_rt*.nc analysis_assim_std/$YYYYMMDD/
        rm -rf temp
        YYYYMMDD=$(date -d "$YYYYMMDD + 1 day" +%Y%m%d) #may work on linux and not mac
	mkdir analysis_assim_std/$YYYYMMDD
done
fi

# if [ $ext == 1 ]; then
# echo downloading/processing extended analysis files...

# # cd nwm_assim_ext/
# hours=`seq -w 0 27`
# # mkdir $YYYYMMDD
# rm -rf temp
# while [[ ${YYYYMMDD} -le $tf ]]; do
#         mkdir -p nwm_assim_ext/$YYYYMMDD
# 	for hour in ${hours}; do
#         	echo ${YYYYMMDD}
#         	gsutil cp ${base_url}/nwm.${YYYYMMDD}/analysis_assim_extend/nwm.t16z.analysis_assim_extend.channel_rt.tm${hour}.conus.nc nwm_assim_ext/$YYYYMMDD/
#         	myfilesize=$(stat -f "nwm_assim_ext/$YYYYMMDD/nwm.t16z.analysis_assim_extend.channel_rt.tm${hour}.conus.nc")
#         	echo "$myfilesize"
# 	done
#         YYYYMMDD=$(date -d "$YYYYMMDD + 1 day" +%Y%m%d) #may work on linux and not mac
# done
# fi

if [ $ext == 1 ]; then   # extended analysis
    echo "Downloading/processing extended analysis files..."

    hours=`seq -w 0 27`
    while [[ ${YYYYMMDD} -le $tf ]]; do
        # Create the date-specific folder
        mkdir -p nwm_assim_ext/$YYYYMMDD
        
        for hour in ${hours}; do
            echo "Processing ${YYYYMMDD} hour ${hour}"
            
            # Download directly into the date-specific folder
            gsutil cp ${base_url}/nwm.${YYYYMMDD}/analysis_assim_extend/nwm.t16z.analysis_assim_extend.channel_rt.tm${hour}.conus.nc nwm_assim_ext/$YYYYMMDD/
            
            # Check if download was successful
            if [ $? -ne 0 ]; then
                echo "Failed to download ${YYYYMMDD} hour ${hour}"
            else
                # Display file size if download is successful
                myfilesize=$(stat -c "%s" "nwm_assim_ext/$YYYYMMDD/nwm.t16z.analysis_assim_extend.channel_rt.tm${hour}.conus.nc")
                echo "File size: $myfilesize bytes"
            fi
        done
        
        # Increment the date
        YYYYMMDD=$(date -d "$YYYYMMDD + 1 day" +%Y%m%d)
    done
fi


if [ $lr == 1 ]; then     # long range forecast
echo downloading/processing standard analysis files...

hours=`seq -w 0 23`
rm -rf temp
while [[ ${YYYYMMDD} -le $tf ]]; do
        mkdir temp
	for hour in ${hours}; do
        	echo ${YYYYMMDD}
        	gsutil cp ${base_url}/nwm.${YYYYMMDD}/analysis_assim_long/nwm.t${hour}z.analysis_assim.channel_rt.tm00.conus.nc temp
        	myfilesize=$(stat -f %z "temp/nwm.t${hour}z.analysis_assim.channel_rt.tm00.conus.nc")
        	echo "$myfilesize"
	done
        mv temp/*channel_rt*.nc analysis_assim_long/
        rm -rf temp	
        YYYYMMDD=$(date -d "$YYYYMMDD + 1 day" +%Y%m%d) #may work on linux and not mac
done
fi

du -h nwm_assim_std/*/*assim*.nc > analysis_filesize.txt
end=`date +%s.%N` #doesnt work for mac nanoseconds
runtime=$((end-start))
echo runtime: $runtime seconds