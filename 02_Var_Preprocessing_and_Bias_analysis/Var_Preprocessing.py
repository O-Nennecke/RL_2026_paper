###################################################################################
# Title: Var_Preprocessing.py

# Purpose: Preprocess ERA5 data and CMIP6 data: Regrid, Spatial and temporal selection, change calendar, and save to netCDF files.

# Author: Onno Nennecke on 03.06.2025 Modified: 18.07.2025

# Input data: 

#     - ERA5 lies here: /climca/people/ppfleiderer/ERA5/RL_climate/ERA5_raw/
#     - CMIP6 data lies here: /climca/data/CMIP6
#     - CMIP6 runs are defined in the csv file: /home/onennecke/CMIP_models/CMIP6_runs.csv
#     - Alpha mask for rescaling wind speed lies here: /home/onennecke/Capacity_data/alpha_land_sea.nc

# Output data:

#     - This file lies here: /climca/people/onennecke/not_debiased_data/
###################################################################################


# Importing libraries
import xarray as xr
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
import os
import glob
import cftime
import time
import re
import multiprocessing



# Importing functions
import Functions.grid_func as grid_func
import Functions.wind_model_func as wind_model_func


variables = ['U100', 'V100', 'SSRD', 'tas', 'tmax'] # List of variables
path = '/climca/people/ppfleiderer/ERA5/RL_climate/ERA5_raw/*'

# Select all files in the range 2015-2024
year_range = (2015, 2024)
all_files = [f for f in glob.glob(path) if f.endswith('.nc')]
all_files = sorted(all_files)

filtered_files = []
for file in all_files:
    # Extract year and month using regex
    match = re.search(r'(\d{4})', file)
    if match:
        year = int(match.group(1))
        if year_range is None or year_range[0] <= year <= year_range[1]:
            filtered_files.append(file)

# filtered_files

# Read datasets for each variable
files_by_variable = {}

# Group files by variable name
for f in filtered_files:
    match = re.search(r'/([^/]+)_(\d{4})\.nc$', f)
    if match:
        var = match.group(1)
        if var not in files_by_variable:
            files_by_variable[var] = []
        files_by_variable[var].append(f)

files_by_variable
# SSRD_list = files_by_variable['SSRD']
# SSRD_list

# Read datasets for each variable
datasets_by_variable = {}
for var, files in files_by_variable.items():
    # print(f'Processing {var}...')
    files_sorted = sorted(files)

    # Use the first file as coordinate reference
    ref_ds = xr.open_dataset(files_sorted[0])
    ref_lat = ref_ds.lat
    ref_lon = ref_ds.lon

    def preprocess(ds):
        ds = ds.sortby('lat')  # Ensure consistent order
        ds = ds.assign_coords(lat=ref_lat, lon=ref_lon)  # Align coordinates exactly
        return ds

    # Open and process all datasets with aligned coordinates
    ds = xr.open_mfdataset(files_sorted, combine='by_coords', preprocess=preprocess)
    
    if var == 'SSRD':
        ds = ds / 3600 # Convert from J/m2 to W/m2
    ds_daily = ds.resample(time='1D').mean()
    datasets_by_variable[var] = ds_daily
    if var == 'tas':
        tasmax = ds.resample(time='1D').max()
        tasmax = tasmax.rename({'var167': 'tasmax'})
        datasets_by_variable['tasmax'] = tasmax


datasets_by_variable

var_names = {'var169': 'rsds',
             'var167': 'tas',
             'var246': 'U100',
             'var247': 'V100',
             'tasmax': 'tasmax'}

ds_list = []

for i in datasets_by_variable:
    # print(i)
    # print(datasets_by_variable[i])
    # print('------------------')
    ds = datasets_by_variable[i]
    var = list(ds.data_vars)[0]
    ds = ds.rename({var: var_names[var]})
    ds = ds.sel(lat=slice(45, 60), lon=slice(4, 17))
    nc = grid_func.regrid(ds, s = 47, n = 56, w = 6, e = 16) # One ° less in the north to prevent NaN values
    # Append to list for later merging
    ds_list.append(nc)
    # ds.to_netcdf(f'/climca/people/onennecke/ERA5/{i}.nc')

# Read in tmax

# Combine all into a single dataset
ERA5_ds = xr.merge(ds_list)

# Assign coordinates for ESM
ERA5_ds = ERA5_ds.assign_coords(ESM='ERA5')
ERA5_ds = ERA5_ds.assign_coords(run='hist')  # Assign run coordinate
ERA5_ds = ERA5_ds.assign_coords(ESM_run='ERA5_hist')  # Assign ESM_run coordinate

# Remove every 29.02
ERA5_ds = ERA5_ds.where(~((ERA5_ds['time.month'] == 2) & (ERA5_ds['time.day'] == 29)), drop=True)

ERA5_ds['sfcWind'] = np.sqrt(ERA5_ds['U100']**2 + ERA5_ds['V100']**2)
# ERA5_ds['tas'] = ERA5_ds['tas'] - 273.15
# ERA5_ds['tasmax'] = ERA5_ds['tasmax'] - 273.15

ERA5_ds

ERA5_ssrd =  ERA5_ds['rsds']
# Save ERA5 data to a netCDF file
output_file = '/climca/people/onennecke/not_debiased_data/ERA5_hist_rsds.nc'
if os.path.isfile(output_file) == False:
    ERA5_ssrd.to_netcdf(output_file) 
# ERA5_ssrd
ERA5_sfcWind = ERA5_ds['sfcWind']
# Save ERA5 data to a netCDF file
output_file = '/climca/people/onennecke/not_debiased_data/ERA5_hist_sfcWind.nc'
if os.path.isfile(output_file) == False:
    ERA5_sfcWind.to_netcdf(output_file)
# ERA5_sfcWind
ERA5_tas = ERA5_ds['tas']
# Save ERA5 data to a netCDF file
output_file = '/climca/people/onennecke/not_debiased_data/ERA5_hist_tas.nc'
if os.path.isfile(output_file) == False:
    ERA5_tas.to_netcdf(output_file)
# ERA5_tas
ERA5_tasmax = ERA5_ds['tasmax']
# Save ERA5 data to a netCDF file
output_file = '/climca/people/onennecke/not_debiased_data/ERA5_hist_tasmax.nc'
if os.path.isfile(output_file) == False:
    ERA5_tasmax.to_netcdf(output_file)
# ERA5_tasmax

ERA5_time = ERA5_ds['time'].load()


variable = 'slp'
# Select all files in the range 2014-2024
path = f'/climca/data/ERA5/daily/{variable}/'
year_range = (2015, 2024)
all_files = sorted(glob.glob(os.path.join(path, '*.nc')))

filtered_files = []
for file in all_files:
    # Extract year and month using regex
    match = re.search(r'(\d{4})', file)
    if match:
        year = int(match.group(1))
        if year_range is None or year_range[0] <= year <= year_range[1]:
            filtered_files.append(file)

filtered_files

ds = xr.open_mfdataset(filtered_files, combine='by_coords', preprocess=grid_func.preprocess_ERA5_psl)

# Regrid the dataset
regridded_ds = grid_func.regrid(ds, s = 30, n = 70, w = 340, e = 30)

# Assign coordinates for ESM
regridded_ds = regridded_ds.assign_coords(ESM='ERA5')
regridded_ds = regridded_ds.assign_coords(run='hist')  # Assign run coordinate
regridded_ds = regridded_ds.assign_coords(ESM_run='ERA5_hist')  # Assign ESM_run coordinate


# Rename the variable to 'pls'
ERA5_ds_psl = regridded_ds.rename({'var151': 'psl'})

ERA5_ds_psl = ERA5_ds_psl.where(~((ERA5_ds_psl['time.month'] == 2) & (ERA5_ds_psl['time.day'] == 29)), drop=True)

ERA5_ds_psl = ERA5_ds_psl.assign_coords(time=ERA5_time)  # Ensure time coordinates are aligned

# Save ERA5 data to a netCDF file
output_file = '/climca/people/onennecke/not_debiased_data/ERA5_hist_psl.nc'
if os.path.isfile(output_file) == False:
    ERA5_ds_psl.to_netcdf(output_file) 


# Import alpha mask for rescaling wind speed
alpha_mask = xr.open_dataset('/home/onennecke/Capacity_data/alpha_land_sea.nc')

# Read the dataframe from the csv file
df = pd.read_csv('/home/onennecke/CMIP_models/CMIP6_runs_future.csv')

# Change the ref column to 1 for the first instance of each model
df['Ref'] = df.groupby(['ESM', 'Institution']).cumcount().apply(lambda x: 1 if x == 0 else 0)

df

# Load climate data

MIP = 'ScenarioMIP' # CMIP

scenario = 'ssp370'
time_res = 'day'
variables = ['sfcWind', 'rsds', 'tas', 'tasmax'] # List of variables
# variables = ['sfcWind', 'rsds', 'tas', 'tasmax', 'psl'] # List of variables

grid_def = '*'
version = '*'

# for i in range(len(df[0:2])):
def one_run(i):
    run_time = time.time()
    ESM = df['ESM'][i]
    Inst = df['Institution'][i]
    run = df['run'][i]
    ESM_run = f'{ESM}_{run}'
    print(f'Processing Run Nr. {i+1}, {ESM}, {Inst}, {run}, \n')
    
    
    for var in variables:
        output_file = f'/climca/people/onennecke/not_debiased_data/{ESM}_{run}_{var}.nc'
        if os.path.isfile( output_file ) == False:
            
            print(f'Processing variable: {var}')
            path = f'/climca/data/CMIP6/{MIP}/{Inst}/{ESM}/{scenario}/{run}/{time_res}/{var}/{grid_def}/{version}/{var}_{time_res}_{ESM}_{scenario}_{run}_*'
            files = [f for f in glob.glob(path) if f.endswith('.nc')]

            nc = xr.open_mfdataset(files, preprocess=grid_func.preprocess)
            nc = nc[[var]]
            nc = nc.sel(time=nc.time.dt.year.isin(range(2015, 2025))) # Filter years
            nc = grid_func.regrid(nc, s = 47, n = 56, w = 6, e = 16)  # Regrid the data
            
            nc = nc.drop_vars('height') if 'height' in nc.coords else nc
            
            if var == 'sfcWind':
                nc = wind_model_func._wind_scale(nc, 100, alpha_mask['mask'], 10)
            
            if isinstance(nc.time.values[0], cftime.Datetime360Day):
                print('Using 360-day calendar')
                # Duplicate the 30th of the month for these months
                extra_months = [4, 5, 6, 7, 8]

                # Duplicate the dataset for these time points
                duplicates = []
                for m in extra_months:
                    mask = (nc['time.month'] == m) & (nc['time.day'] == 30)
                    ds_dup = nc.sel(time=nc.time[mask])
                    duplicates.append(ds_dup)

                # Put everything together and sort by time
                nc = xr.concat([nc] + duplicates, dim='time').sortby('time')

                nc = nc.assign_coords(time=ERA5_time)  # Replace time coordinates with ERA5 time
            elif isinstance(nc.time.values[0], cftime.DatetimeNoLeap):
                print('Using no-leap calendar')
                nc = nc.assign_coords(time=ERA5_time)  # Ensure time coordinates are aligned
            else:
                print('Using standard calendar')
                nc = nc.where(~((nc['time.month'] == 2) & (nc['time.day'] == 29)), drop=True)
                nc = nc.assign_coords(time=ERA5_time)  # Ensure time coordinates are aligned
            
            nc = nc.assign_coords(ESM=ESM)  # Assign ESM coordinate
            nc = nc.assign_coords(run=run)  # Assign run coordinate
            nc = nc.assign_coords(ESM_run=ESM_run)  # Assign ESM_run coordinate
            
            nc = nc.load()
            
            # Save the dataset
            nc.to_netcdf(output_file)

            print('Run time: ', int(np.floor((time.time()  - run_time) / 60)),'m', round((time.time()  - run_time) % 60,1),'s', '\n')
            # return nc
            # break
    var = 'psl'

    output_file = f'/climca/people/onennecke/not_debiased_data/{ESM}_{run}_{var}.nc'

    if os.path.isfile( output_file ) == False:

        run_time = time.time()

        print(f'Processing variable: {var}')
        path = f'/climca/data/CMIP6/{MIP}/{Inst}/{ESM}/{scenario}/{run}/{time_res}/{var}/{grid_def}/{version}/{var}_{time_res}_{ESM}_{scenario}_{run}_*'
        files = [f for f in glob.glob(path) if f.endswith('.nc')]


        nc = xr.open_mfdataset(files, preprocess=grid_func.preprocess_psl)
        nc = nc[[var]]
        nc = nc.sel(time=nc.time.dt.year.isin(range(2015, 2025))) # Filter years
        nc = grid_func.regrid(nc, s = 30, n = 70, w = 340, e = 30)

        nc = nc.drop_vars('height') if 'height' in nc.coords else nc

        if isinstance(nc.time.values[0], cftime.Datetime360Day):
            print('Using 360-day calendar')
            # Duplicate the 30th of the month for these months
            extra_months = [4, 5, 6, 7, 8]

            # Duplicate the dataset for these time points
            duplicates = []
            for m in extra_months:
                mask = (nc['time.month'] == m) & (nc['time.day'] == 30)
                ds_dup = nc.sel(time=nc.time[mask])
                duplicates.append(ds_dup)

            # Put everything together and sort by time
            nc = xr.concat([nc] + duplicates, dim='time').sortby('time')

            nc = nc.assign_coords(time=ERA5_time)  # Replace time coordinates with ERA5 time
        elif isinstance(nc.time.values[0], cftime.DatetimeNoLeap):
            print('Using no-leap calendar')
            nc = nc.assign_coords(time=ERA5_time)  # Ensure time coordinates are aligned
        else:
            print('Using standard calendar')
            nc = nc.where(~((nc['time.month'] == 2) & (nc['time.day'] == 29)), drop=True)
            nc = nc.assign_coords(time=ERA5_time)  # Ensure time coordinates are aligned

        nc = nc.assign_coords(ESM=ESM)  # Assign ESM coordinate
        nc = nc.assign_coords(run=run)  # Assign run coordinate
        nc = nc.assign_coords(ESM_run=ESM_run)  # Assign ESM_run coordinate
        
        nc = nc.load()

        # Save the dataset
        nc.to_netcdf(output_file)

        print('Run time: ', int(np.floor((time.time()  - run_time) / 60)),'m', round((time.time()  - run_time) % 60,1),'s')


for i in range(len(df)):
    one_run(i)

# p = multiprocessing.Pool(64)
# p.map(one_run, range(len(df)))
