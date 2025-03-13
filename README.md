# NWM_Data_Download

This repository aims to download and process the NWM data for the Great Lakes region.

This is to download archived NWM real time (continuous) extended analysis data, long range forecast, and NWM retrospective/reanalysis data.

An overview of the code provided: the code will download the NWM data from the Amazon AWS website (retrospective), the THREDDS server (realtime extended analysis), and the Google Cloud repository of NWM data (archived extended analysis). The code will average the hourly data into daily data, extract the streamflow, and extract the streamlinks in the Great Lakes region. The streamlinks downloaded will either be the stream reaches that drain into the lakes and the gauges in the Great Lakes region (seperate files).

These data are manipulated from NWM data produced by the Office of Water Prediction. More information can be found: https://water.noaa.gov/about/nwm. The data are not owned by NOAA GLERL or CIGLR.

Important Links: THREDDS Server: https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwm/v3.0/ (realtime NWM data, most recent 2 days data) NWM Google Cloud Repository: https://console.cloud.google.com/marketplace/details/noaa-public/national-water-model?supportedpurview=project&pli=1 NWM AWS Repository: https://registry.opendata.aws/nwm-archive/
