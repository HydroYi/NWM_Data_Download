# *=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
# ** This script is for comparing total inflows from NWM and GLERL data
#
# ** Created by Yi Hong, 03/28/2023, Modified for use in extended analysis data and near real time data 
# ** Modified by Yi Hong, 03/12/2025, adjust for data
# ** Contact: yhon@umich.edu
# *=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*
#%%    
# =============================================================================
# Import modules
# =============================================================================
import os
import datetime
# from calendar import monthrange
import numpy as np
# import re
# import calendar
import netCDF4 as nc
import pandas as pd

#%%
# =============================================================================
# Configuration settings
# ============================================================================
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
# Construct the paths to the CSV files
Dir_link = os.path.join(parent_dir, 'Input-Information-and-Data')  #link to where your input files are located
Dir_data = os.path.join(script_dir, 'sf_cut')  #link to where your input file

# =============================================================================
link_lakes = ['SU','MIHU','ER','ON']  #names in the link file
id_remove = [15568147,10850322,12211186]  # these Link_IDs are wrongly represented
links_GL = pd.read_csv(os.path.join(Dir_link,'Download_link.csv')) #set up the directory link to input data
id_GL = links_GL['ID'].to_list()
id_GL = [i for i in id_GL if i not in id_remove] #remove the link IDs that are represented wrong

# Calculate the first and last day of the previous month
today = datetime.date.today()
first_day_of_current_month = today.replace(day=1)
last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
new_mon_num = first_day_of_previous_month.strftime('%m')
new_mon_str = first_day_of_previous_month.strftime('%b')
new_yr_num = first_day_of_previous_month.strftime('%Y')

# Calculate the month before the last month
month_before_last = first_day_of_previous_month- datetime.timedelta(days=1)
prev_mon_num = month_before_last.strftime('%m')
prev_mon_str = month_before_last.strftime('%b')
prev_yr_num = month_before_last.strftime('%Y')

# Construct the path for df_link_prev
data_prev_path = os.path.join(script_dir, f"Updated_{prev_yr_num}_{prev_mon_num}")
# Ensure the new data directory exists
new_dir = os.path.join(script_dir, f"Updated_{new_yr_num}_{new_mon_num}")
if not os.path.exists(new_dir):
    os.makedirs(new_dir)

begin_date = first_day_of_previous_month.strftime('%Y%m%d')
end_date = last_day_of_previous_month.strftime('%Y%m%d')
# start_date = '20241220'
# end_date = '20241231'

begin_mon=datetime.datetime.strptime(begin_date,'%Y%m%d')
end_mon=datetime.datetime.strptime(end_date,'%Y%m%d')
rng_date = pd.date_range(begin_mon,end_mon,freq='D')
rng_mon = pd.date_range(begin_mon,end_mon,freq='M')  # Different to pd.period_range, date_range ends last day of month, the other ends first day of month

rng_mon = pd.period_range(begin_mon,end_mon,freq='M').to_timestamp()   # to_timestamp() in order to compare timestamp
rng_year = pd.period_range(begin_mon,end_mon,freq='Y').to_timestamp()

month_names=list(map(lambda x: datetime.datetime.strptime(str(x), '%m').strftime('%b'),list(range(1,13))))
print(month_names)

#%%
# =============================================================================
# Extract WRF-Hydro routing data
# =============================================================================

df_link = pd.DataFrame(index=rng_date, columns=id_GL)
# These are the dates with missing data for extended analysis folders
exclude_dates = ['20210524','20210525','20210528','20210529','20210622','20210623','20210711','20210712','20210713','20210727','20210728','20211003','20211004','20220110','20220111','20220206','20220207','20220208','20220209','20220330','20220331','20220613','20220614','20220924','20220925','20230613','20230614','20230813','20230812','20230905','20230906']
dates1 = pd.date_range(start=begin_date, end=end_date, freq="D")
dates1 = dates1[~dates1.isin(exclude_dates)]
dates = dates1.strftime('%Y%m%d')
dates_nwm = dates1.strftime('%Y-%m-%d')
#%%
df_link_prev = pd.read_csv(os.path.join(data_prev_path, f'Daily_2021_{prev_yr_num}_links_{prev_mon_str}.csv'),sep=',',header=0) #take the link data file that was just created
df_link_prev = df_link_prev.rename(columns = {df_link_prev.columns[0]:'Date'})
df_link_prev['Date'] = pd.to_datetime(df_link_prev['Date'], format='%Y%m%d') 
df_link_prev = df_link_prev.sort_values(by=['Date']).set_index('Date') 
#%
for day in dates:
    nc_file = nc.Dataset(os.path.join(Dir_data, 'nwm_'+str(day)+'_chrt_ext_assim_all_streamlinks.nc'))
    feature_id = nc_file.variables['feature_id'][:]     # select the feature ID variable to subset later
    streamflow = nc_file.variables['streamflow'][:]      # select only streamflow variable, array of (5,365,3586)   

    time = nc_file.variables['time'] 
    time_conv = nc.num2date(time[:].data, time.units, only_use_python_datetimes=True)

    for iday in range(len(time_conv)):        
        cft = datetime.datetime.strptime(str(time_conv[iday]),'%Y-%m-%d %H:%M:%S')
        idate = cft.replace(minute=0,hour=0,second=0)
        
        for cid in id_GL:
            df_link.loc[idate,cid] = streamflow[iday,:][np.where(feature_id == cid)].data[0] #loop through GL gauge ID list and 

    nc_file.close()
#%    
df_link_prev.columns = df_link_prev.columns.astype("int64")
columns_match = list(df_link_prev.columns) == list(df_link.columns)
print("Are column names identical?", columns_match)

# Combine df_link_prev with df_link
df_link_new = pd.concat([df_link_prev, df_link])
# Save the combined DataFrame to a new file
df_link_new.to_csv(os.path.join(new_dir, f'Daily_2021_{new_yr_num}_links_{new_mon_str}.csv'), sep=',', index=True, date_format='%Y%m%d')

#%%
# =============================================================================
# Select links for all lakes
# =============================================================================
all_links = pd.read_csv(os.path.join(Dir_link,'Download_link.csv'))
# dict_link = {'SU':['sup','Superior'], 'ER':['eri','Erie'], 'ON':['ont','Ontario']}
#%
#extract the links for each lake (loop through each lake)
for l_lake in link_lakes:
    link_id = all_links['ID'].loc[all_links['TO_LAKE']==l_lake].to_list()
    id_GL = [i for i in link_id if i not in id_remove]

    link_id = [int(i) for i in id_GL]
    # Select for different lakes
    Qd = df_link_new.filter(link_id)
    Qd[Qd<=0] = np.nan
    Q_mon = Qd.resample('MS').mean() # with only the links for that lake, resample to monthly average
    Q_mon['Total Inflow (cms)']= Q_mon[[s for s in link_id]].sum(axis=1) #calculate the sum for monthly total inflow by adding up all the links for each lake
    Qd['Total Inflow (cms)']= Qd[[s for s in link_id]].sum(axis=1) #calculate the sum for daily total inflow by summing up all the links for each lake
            
    Qd['Total Inflow (cms)'].to_csv(os.path.join(new_dir, f'Daily_2021_{new_yr_num}_{l_lake}_{new_mon_str}.csv'),sep=',',index=True, date_format='%Y%m%d')
    Q_mon['Total Inflow (cms)'].to_csv(os.path.join(new_dir, f'Monthly_2021_{new_yr_num}_{l_lake}_{new_mon_str}.csv'),sep=',',index=True, date_format='%Y%m%d')






