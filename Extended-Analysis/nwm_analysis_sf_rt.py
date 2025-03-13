#!/bin/env python
"""
Created on Mon Jun 19 10:48:02 2023

@author: orendorf
"""
#############################################################################
#############################################################################
# Created by: Sophie Orendorf, Jun 2023
# Contact: orendorf@umich.edu 
# Purpose: Obtain daily average streamflow for each lake from all streamlinks
# aggregated together and outputted into one .csv file for the coordinating
# committee
#
#Using hourly NWM Standard Analysis data (NWMv2.1)
#
#############################################################################
#############################################################################


import tracemalloc
tracemalloc.start()

import pandas as pd
import time
startTime = time.time()
import os, glob

from netCDF4 import Dataset, MFDataset
import numpy as np 
import xarray as xr


gauge_file = 'Gages_link.csv'
all_file = 'Download_link.csv'

##### WILL NEED TO CHANGE SHAPE FILE IF WE CHANGE THE VERSION OF NWM THAT WE USE ####

# files obtained from Yi's code to get the stream IDs
#note from Yi's code
'''
With preliminary analysis, we could use the glb_flowlines_2.1.shp to define all streams flow into certain lake
“to” the link id of each lake:
    
Lake Superior: 904020529, (Lake: 4800002)
Lake Michigan-Huron: 13196034, (Lake: 4800004)
Lake Erie: 166764152, (Lake: 4800006)
Lake Ontario: 15502727, (Lake: 4800007)
 
Note: 4800001, Lake Nipigan; 4800005, Lake St-Claire

'''
all_csv = pd.read_csv(all_file, dtype=str)
gauge_csv = pd.read_csv(gauge_file, dtype=str)

#only select the streamlink ID so we can compare them to feature IDs in NWM file

all_id_pd = all_csv['ID'].astype(int)
gauge_id_pd = gauge_csv['ID'].astype(int)

#make csv data into xarray
all_id_pd = xr.DataArray(all_id_pd)
gauge_id_pd = xr.DataArray(gauge_id_pd)

"""
Columns for CSV files: 
['ID', 'to', 'order_', 'gages', 'Slope', 'Length', 'Shp_Lng'] 

ID: stream ID
to: which lake the stream flows to (see note above for lake IDs)
"""
#nwm forecast output file (netcdf)
#link to one NWM file 
today_date1 = pd.Timestamp.today()
today_date = today_date1 - pd.tseries.offsets.DateOffset(days=1)
yesterday_date = today_date1 - pd.tseries.offsets.DateOffset(days=2)
str_yesterday = yesterday_date.strftime('%Y%m%d')
str_today = today_date.strftime('%Y%m%d')

path1 = "nwm_assim_ext_rt/"+str_yesterday
path2 = "nwm_assim_ext_rt/"+str_today
file_list1 = [path1+"/nwm.t16z.analysis_assim_extend.channel_rt.tm{}.conus.nc".format('%02d' % i) for i in np.arange(16,-1,-1)]
file_list2 = [path2+"/nwm.t16z.analysis_assim_extend.channel_rt.tm{}.conus.nc".format('%02d' % i) for i in np.arange(21,16,-1)]
    #open the NWM dataset using xarray
ds_nwm1 = xr.open_mfdataset(file_list1, engine='netcdf4')
ds_nwm2 = xr.open_mfdataset(file_list2, engine='netcdf4')
    
ds_nwm_all1 = ds_nwm1.sel(feature_id=all_id_pd) 
ds_nwm_gauge1 = ds_nwm1.sel(feature_id=gauge_id_pd) 
    
ds_nwm_all2 = ds_nwm2.sel(feature_id=all_id_pd) 
ds_nwm_gauge2 = ds_nwm2.sel(feature_id=gauge_id_pd) 

ds_nwm_gauge = xr.concat([ds_nwm_gauge1, ds_nwm_gauge2], dim='time')
ds_nwm_all = xr.concat([ds_nwm_all1, ds_nwm_all2], dim='time')
    
nwm_gauge_sf = ds_nwm_gauge['streamflow']
nwm_all_sf = ds_nwm_all['streamflow']
    
nwm_gauge_daily = nwm_gauge_sf.resample(time="D",restore_coord_dims=True).mean()
nwm_all_daily = nwm_all_sf.resample(time="D",restore_coord_dims=True).mean()
print(ds_nwm_all.time)
nwm_all_sf.to_netcdf('nwm_assim_ext_rt/sf_cut/nwm_'+str(str_yesterday)+'_chrt_ext_assim_all_streamlinks.nc')
nwm_gauge_sf.to_netcdf('nwm_assim_ext_rt/sf_cut/nwm_'+str(str_yesterday)+'_chrt_ext_assim_gauge.nc')
        
#print time for executing the python code
executionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(executionTime))
print(tracemalloc.get_traced_memory())
# stopping the library
tracemalloc.stop()
