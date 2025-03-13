#############################################################################
#############################################################################
# Created by: Sophie Orendorf, Jan 2023
# Modified by: Yi Hong, Mar 2025
# Contact: yhon@umich.edu 
# Purpose: Obtain daily average streamflow for each lake from all streamlinks and gauges
# and output in a new netcdf
#
#Using hourly NWM Extended Analysis data 
#
#############################################################################
#############################################################################

#%% import packages
import tracemalloc
tracemalloc.start()

import pandas as pd
import datetime
import time
startTime = time.time()
import os, glob

# from netCDF4 import Dataset, MFDataset
import numpy as np 
import xarray as xr
#%%
# make sure to change the path to the working directory "Great-Lakes-NWM-Data-Download"
# os.chdir('C:/Research_Mich/BIL_SA/NWM/Monthly_download/Great-Lakes-NWM-Data-Download')
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
# Construct the paths to the CSV files
gauge_file = os.path.join(parent_dir, 'Input-Information-and-Data', 'Gages_link.csv')
all_file = os.path.join(parent_dir, 'Input-Information-and-Data', 'Download_link.csv')

##### WILL NEED TO CHANGE SHAPE FILE IF WE CHANGE THE VERSION OF NWM THAT WE USE ####

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
exclude_dates = ['20210525','20210526','20210529','20210530','20210623','20210623','20210712','20210713','20210714','20210728','20210729','20211004','20211005','20220111','20220112','20220207','20220208','20220209','20220210','20220331','20220401','20220614','20220615','20220925','20220926','20230813','20230814']


exclude_dates_nwm = ['2021-05-25','2021-05-26','2021-05-29','2021-05-31','2021-06-23','2021-06-23','2021-07-12','2021-07-13','2021-07-14','2021-07-28','2021-07-29','2021-10-04','2021-10-05','2022-01-11','2022-01-12','2022-02-07','2022-02-08','2022-02-09','2022-02-10','2022-03-31','2022-04-01','2022-06-14','2022-06-15','2022-09-25','2022-09-26','2023-08-13','2023-08-14']

#%%
# start_date = '20241220'
# end_date = '20241231'

# Calculate the first and last day of the previous month
today = datetime.date.today()
first_day_of_current_month = today.replace(day=1)
last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

start_date = first_day_of_previous_month.strftime('%Y%m%d')
end_date = first_day_of_current_month.strftime('%Y%m%d')   # Extended analysis has a lookback period, need to analyze until the curent month

dates1 = pd.date_range(start=start_date, end=end_date, freq="D")

dates2 = dates1[~dates1.isin(exclude_dates_nwm)]
dates = dates2.strftime('%Y%m%d')
dates_nwm1 = dates1[~dates1.isin(exclude_dates_nwm)]
dates_nwm = dates_nwm1.strftime('%Y-%m-%d')
dates = dates[~dates.isin(exclude_dates)]
dates_nwm = dates_nwm[~dates_nwm.isin(exclude_dates_nwm)]
dates_pd = dates1[~dates1.isin(exclude_dates)]

# Ensure the output directory exists
output_dir = os.path.join(script_dir, 'sf_cut')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

#%%
    #open the NWM dataset using xarray

for day, day_pd, day_nwm in zip(dates, dates_pd, dates_nwm):
    print(day)
    #link to multiple files from google cloud or aws for the dataset
    day_11 = day_pd - pd.tseries.offsets.DateOffset(days=1)
    day_1 = day_11.strftime('%Y%m%d')
    day_test = day_11.strftime('%Y-%m-%d')

    path1 = os.path.join(script_dir, 'nwm_assim_ext', day_1)
    path2 = os.path.join(script_dir, 'nwm_assim_ext', day)

    file_list1 = [os.path.join(path1, f"nwm.t16z.analysis_assim_extend.channel_rt.tm{hour:02d}.conus.nc") for hour in range(16, -1, -1)]
    file_list2 = [os.path.join(path2, f"nwm.t16z.analysis_assim_extend.channel_rt.tm{hour:02d}.conus.nc") for hour in range(22, 16, -1)]

    # file_list1 = [path1+"/nwm.t16z.analysis_assim_extend.channel_rt.tm{}.conus.nc".format('%02d' % i) for i in np.arange(16,-1,-1)]
    # file_list2 = [path2+"/nwm.t16z.analysis_assim_extend.channel_rt.tm{}.conus.nc".format('%02d' % i) for i in np.arange(22,16,-1)]

    file_list1 = [f for f in file_list1 if os.path.exists(f)]
    file_list2 = [f for f in file_list2 if os.path.exists(f)]

    # Skip processing if no valid files are found
    if not file_list1:
        print(f"Skipping {day_1}: No valid files found.")
        continue
    if not file_list2:
        print(f"Skipping {day}: No valid files found.")
        continue
    
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
    
    nwm_gauge_daily = nwm_gauge_sf.resample(time="D").mean()
    nwm_all_daily = nwm_all_sf.resample(time="D").mean()
    print(nwm_all_daily.time)
    nwm_all_daily.to_netcdf(os.path.join(output_dir, f'nwm_{day_1}_chrt_ext_assim_all_streamlinks.nc'))
    nwm_gauge_daily.to_netcdf(os.path.join(output_dir, f'nwm_{day_1}_chrt_ext_assim_gauge.nc'))

    
        
#print time for executing the python code
executionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(executionTime))

print(tracemalloc.get_traced_memory())

# stopping the library
tracemalloc.stop()
