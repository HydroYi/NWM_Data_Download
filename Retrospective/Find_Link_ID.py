# *=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# ** This script aims to match feature id of the NWM for each stations
# ** Edit by Yi Hong, 12/05/2024
# *=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
'''
feature id in NWM streamflow output correspond to NHDPlus Comid

'''



#%%    
# =============================================================================
# Import modules
# =============================================================================
#import sys
import os
import re
import pandas as pd
import netCDF4 as nc
import numpy as np
# import xarray as xr


#%%
# =============================================================================
# Start with a testing file, identify IDs for each comid
# =============================================================================
stn_info = pd.read_csv('C:/Users/hong/Desktop/NWM/code/WQstations_comid.csv')
# comid_list = stn_info['COMID'].tolist()

test_nc = nc.Dataset('P:/hpc/hong/NWM3_0/Retrospective/Download/2000/20000101.nc')
feature_id = test_nc.variables['feature_id'][:]     

# #%%
# def find_index(value, array):
#     return np.where(array == value)[0][0] if value in array else -1

# # Creating a new column 'Index_FID'
# stn_info['Index_FID'] = stn_info['COMID'].apply(lambda x: find_index(x, feature_id))
# count_minus_one = (stn_info['Index_FID'] == -1).sum()  # 578
#%% faster approach
# Create a dictionary to map each value in the array to its index
value_to_index = {value: index for index, value in enumerate(feature_id)}
# Use the map function to apply this mapping to the 'A' column to create the 'Index_A' column
stn_info['Index_FID'] = stn_info['COMID'].map(value_to_index).fillna(-1).astype(int)
count_minus_one = (stn_info['Index_FID'] == -1).sum()  # 578

stn_info.to_csv('C:/Users/hong/Desktop/NWM/code/WQstn_comid_FID.csv', index=False)

#%%
# =============================================================================
# Extract data from NWM files
# =============================================================================
df_nwm = pd.read_csv('C:/Users/hong/Desktop/NWM/code/WQstn_comid_FID.csv')
valid_indices = df_nwm['Index_FID'] != -1   # Extract data from another_array based on valid indices

path_nwm = 'P:/hpc/hong/NWM3_0/Retrospective/Download'
pattern = re.compile(r'(\d{8})\.nc$')

for iyear in range(1979,2023):
    ncfiles = os.listdir(os.path.join(path_nwm, str(iyear))) 
    
    for filename in ncfiles:
    # Check if the filename matches the pattern
        match = pattern.match(filename)
        if match: 
            yyyymmdd = match.group(1)
            temp_nc = nc.Dataset(os.path.join(os.path.join(path_nwm, str(iyear)), filename))            
            # feature_id = temp_nc.variables['feature_id'][:]     
            streamflows = temp_nc.variables['streamflow'][:]
            extracted_data = streamflows[df_nwm.loc[valid_indices, 'Index_FID']]
            df_nwm[yyyymmdd] = np.nan
            df_nwm.loc[valid_indices, yyyymmdd] = extracted_data

df_nwm.to_csv('C:/Users/hong/Desktop/NWM/code/WQstn_NWM.csv', index=False)







