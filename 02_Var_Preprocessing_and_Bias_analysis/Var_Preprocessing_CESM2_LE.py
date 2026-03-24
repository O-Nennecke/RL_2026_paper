###################################################################################
# Title: Var_Preprocessing_CESM2_LE.py

# Purpose: Preprocess CESM2_LE data: Regrid, Spatial and temporal selection, change calendar, and save to netCDF files.

# Author: Onno Nennecke on 03.06.2025 Modified: 16.02.2026

# Input data: 

#     - warming_year data lies here: /home/onennecke/CMIP_models/warming_thresholds.csv
#     - CMIP6 data lies here: /climca/data/CMIP6
#     - CMIP6 runs are defined in the csv file: /home/onennecke/CMIP_models/CMIP6_runs.csv
#     - Alpha mask for rescaling wind speed lies here: /home/onennecke/Capacity_data/alpha_land_sea.nc

# Output data:

#     - This file lies here: /climca/people/onennecke/not_debiased_data/
#     - This file lies here: /climca/people/onennecke/not_debiased_data_future/
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

# Import alpha mask for rescaling wind speed
alpha_mask = xr.open_dataset('/home/onennecke/Capacity_data/alpha_land_sea.nc')

# Read the dataframe from the csv file
df = pd.read_csv("/home/onennecke/CMIP_models/CESM2_LE_runs_long.csv", dtype=str)
# df = pd.read_csv("/home/onennecke/CMIP_models/CESM2_LE_runs.csv", dtype=str)

warming_thresholds = pd.read_csv('/home/onennecke/CMIP_models/warming_thresholds.csv')

# Load climate data
variables = ['U10', 'FSDS', 'TREFHT', 'TREFHTMX'] # List of variables
# variables = ['U10', 'FSDS', 'TREFHT', 'TREFHTMX', 'PSL'] # List of variables
# var_dict = {'sfcWind': 'U10', 'rsds': 'FSDS', 'tas': 'TREFHT', 'tasmax': 'TREFHTMX', 'psl': 'PSL'}
var_dict = {'U10': 'sfcWind', 'FSDS': 'rsds', 'TREFHT': 'tas', 'TREFHTMX': 'tasmax', 'PSL': 'psl'}



# for i in range(len(df[0:2])):
def one_run(i):
    ESM = 'CESM2_LE'
    run_time = time.time()
    run_type = df['run_type'][i]
    model_version = df['model_version'][i]
    experiment = df['experiment'][i]
    resolution = df['resolution'][i]
    LE_ID_frcng = df['LE_ID_frcng'][i]
    ensemble_member = df['ensemble_member'][i]
    component = df['component'][i]
    frequency = df['frequency'][i]
    run_id = df['run_id'][i]
    ESM_run = f'{ESM}_{run_id}'
    

    print(f'Processing Run Nr. {i+1}, {run_id}\n')

    start_year = 2015
    end_year = 2024

    time_range = pd.date_range(start=f'{start_year}-01-01', end=f'{end_year}-12-31', freq='D')

    time_range = time_range[~((time_range.month == 2) & (time_range.day == 29))]

    new_time = xr.DataArray(time_range, dims='time')

    middle_year = warming_thresholds.loc[warming_thresholds["ESM"] == "CESM2","Year_reached_2C"].item()
    start_year_future = middle_year - 5
    end_year_future = middle_year + 4

    time_range = pd.date_range(start=f'{start_year_future}-01-01', end=f'{end_year_future}-12-31', freq='D')

    time_range = time_range[~((time_range.month == 2) & (time_range.day == 29))]

    new_time_future = xr.DataArray(time_range, dims='time')
    
    for var in variables:
        output_var = var_dict[var]
        output_file = f'/climca/people/onennecke/not_debiased_data/CESM2_{run_id}_{output_var}.nc'

        if os.path.isfile( output_file ) == False:
            
            print(f'Processing variable: {var} 2015-2024')
            if var == 'TREFHT':
                path = f'/climca/data/CESM2_LE/TREFHT_new/day_raw/b.e21.{experiment}.f09_g17.{LE_ID_frcng}.{ensemble_member}.cam.h1.{var}.20150101-20241231.nc'
            else:
                path = f'/climca/data/CESM2_LE/{var}/day_raw/b.e21.{experiment}.f09_g17.{LE_ID_frcng}.{ensemble_member}.cam.h1.{var}.20150101-20241231.nc' 
            files = [f for f in glob.glob(path) if f.endswith('.nc')]

            nc = xr.open_mfdataset(files, preprocess=grid_func.preprocess)
            nc = nc[[var]]
            nc = nc.sel(time=nc.time.dt.year.isin(range(start_year, end_year + 1))) # Filter years
            nc = grid_func.regrid(nc, s = 47, n = 56, w = 6, e = 16)  # Regrid the data
            
            nc = nc.drop_vars('height') if 'height' in nc.coords else nc
            
            nc = nc.rename({var: var_dict[var]})
            
            if var == 'sfcWind':
                nc = wind_model_func._wind_scale(nc, 100, alpha_mask['mask'], 10)
            
            nc = nc.assign_coords(time=new_time)  # Ensure time coordinates are aligned
            
            nc = nc.assign_coords(ESM=ESM)  # Assign ESM coordinate
            nc = nc.assign_coords(run=run_id)  # Assign run coordinate
            nc = nc.assign_coords(ESM_run=ESM_run)  # Assign ESM_run coordinate
            
            nc = nc.load()
            
            # Save the dataset
            nc.to_netcdf(output_file)

            print('Run time: ', int(np.floor((time.time()  - run_time) / 60)),'m', round((time.time()  - run_time) % 60,1),'s', '\n')
            
        output_file = f'/climca/people/onennecke/not_debiased_data_future/CESM2_{run_id}_{output_var}.nc'

        if os.path.isfile( output_file ) == False:
            
            print(f'Processing variable: {var} {start_year_future}-{end_year_future}')
            if var == 'TREFHT':
                files = [f'/climca/data/CESM2_LE/TREFHT_new/day_raw/b.e21.{experiment}.f09_g17.{LE_ID_frcng}.{ensemble_member}.cam.h1.{var}.20350101-20441231.nc', 
                         f'/climca/data/CESM2_LE/TREFHT_new/day_raw/b.e21.{experiment}.f09_g17.{LE_ID_frcng}.{ensemble_member}.cam.h1.{var}.20450101-20541231.nc']
            else:
                files = [f'/climca/data/CESM2_LE/{var}/day_raw/b.e21.{experiment}.f09_g17.{LE_ID_frcng}.{ensemble_member}.cam.h1.{var}.20350101-20441231.nc', 
                         f'/climca/data/CESM2_LE/{var}/day_raw/b.e21.{experiment}.f09_g17.{LE_ID_frcng}.{ensemble_member}.cam.h1.{var}.20450101-20541231.nc']

            nc = xr.open_mfdataset(files, preprocess=grid_func.preprocess)
            nc = nc[[var]]
            nc = nc.sel(time=nc.time.dt.year.isin(range(start_year_future, end_year_future + 1))) # Filter years
            nc = grid_func.regrid(nc, s = 47, n = 56, w = 6, e = 16)  # Regrid the data
            
            nc = nc.drop_vars('height') if 'height' in nc.coords else nc
            
            nc = nc.rename({var: var_dict[var]})
            
            if var == 'sfcWind':
                nc = wind_model_func._wind_scale(nc, 100, alpha_mask['mask'], 10)
            
            nc = nc.assign_coords(time=new_time_future)  # Ensure time coordinates are aligned
            
            nc = nc.assign_coords(ESM=ESM)  # Assign ESM coordinate
            nc = nc.assign_coords(run=run_id)  # Assign run coordinate
            nc = nc.assign_coords(ESM_run=ESM_run)  # Assign ESM_run coordinate
            
            nc = nc.load()
            
            # Save the dataset
            nc.to_netcdf(output_file)

            print('Run time: ', int(np.floor((time.time()  - run_time) / 60)),'m', round((time.time()  - run_time) % 60,1),'s', '\n')
            # return nc
            # break
    
    var = 'PSL'
    output_var = 'psl'
    
    output_file = f'/climca/people/onennecke/not_debiased_data/CESM2_{run_id}_{output_var}.nc'

    if os.path.isfile( output_file ) == False:

        run_time = time.time()

        print(f'Processing variable: {var} 2015-2024')
        if var == 'TREFHT':
            path = f'/climca/data/CESM2_LE/TREFHT_new/day_raw/b.e21.{experiment}.f09_g17.{LE_ID_frcng}.{ensemble_member}.cam.h1.{var}.20150101-20241231.nc'
        else:
            path = f'/climca/data/CESM2_LE/{var}/day_raw/b.e21.{experiment}.f09_g17.{LE_ID_frcng}.{ensemble_member}.cam.h1.{var}.20150101-20241231.nc' 
        files = [f for f in glob.glob(path) if f.endswith('.nc')]


        nc = xr.open_mfdataset(files, preprocess=grid_func.preprocess_psl)
        nc = nc[[var]]
        nc = nc.sel(time=nc.time.dt.year.isin(range(start_year, end_year + 1))) # Filter years
        nc = grid_func.regrid(nc, s = 30, n = 70, w = 340, e = 30)

        nc = nc.drop_vars('height') if 'height' in nc.coords else nc
        nc = nc.rename({var: var_dict[var]})

        nc = nc.assign_coords(time=new_time)  # Ensure time coordinates are aligned

        nc = nc.assign_coords(ESM=ESM)  # Assign ESM coordinate
        nc = nc.assign_coords(run=run_id)  # Assign run coordinate
        nc = nc.assign_coords(ESM_run=ESM_run)  # Assign ESM_run coordinate
        
        nc = nc.load()

        # Save the dataset
        nc.to_netcdf(output_file)

        print('Run time: ', int(np.floor((time.time()  - run_time) / 60)),'m', round((time.time()  - run_time) % 60,1),'s')
        
    output_file = f'/climca/people/onennecke/not_debiased_data_future/CESM2_{run_id}_{output_var}.nc'

    if os.path.isfile( output_file ) == False:

        run_time = time.time()

        print(f'Processing variable: {var} {start_year_future}-{end_year_future}')
        if var == 'TREFHT':
            files = [f'/climca/data/CESM2_LE/TREFHT_new/day_raw/b.e21.{experiment}.f09_g17.{LE_ID_frcng}.{ensemble_member}.cam.h1.{var}.20350101-20441231.nc', 
                     f'/climca/data/CESM2_LE/TREFHT_new/day_raw/b.e21.{experiment}.f09_g17.{LE_ID_frcng}.{ensemble_member}.cam.h1.{var}.20450101-20541231.nc']
        else:
            files = [f'/climca/data/CESM2_LE/{var}/day_raw/b.e21.{experiment}.f09_g17.{LE_ID_frcng}.{ensemble_member}.cam.h1.{var}.20350101-20441231.nc', 
                        f'/climca/data/CESM2_LE/{var}/day_raw/b.e21.{experiment}.f09_g17.{LE_ID_frcng}.{ensemble_member}.cam.h1.{var}.20450101-20541231.nc']

        nc = xr.open_mfdataset(files, preprocess=grid_func.preprocess_psl)

        nc = nc[[var]]
        nc = nc.sel(time=nc.time.dt.year.isin(range(start_year_future, end_year_future + 1))) # Filter years
        nc = grid_func.regrid(nc, s = 30, n = 70, w = 340, e = 30)

        nc = nc.drop_vars('height') if 'height' in nc.coords else nc
        nc = nc.rename({var: var_dict[var]})

        nc = nc.assign_coords(time=new_time_future)  # Ensure time coordinates are aligned

        nc = nc.assign_coords(ESM=ESM)  # Assign ESM coordinate
        nc = nc.assign_coords(run=run_id)  # Assign run coordinate
        nc = nc.assign_coords(ESM_run=ESM_run)  # Assign ESM_run coordinate
        
        nc = nc.load()

        # Save the dataset
        nc.to_netcdf(output_file)

        print('Run time: ', int(np.floor((time.time()  - run_time) / 60)),'m', round((time.time()  - run_time) % 60,1),'s')




p = multiprocessing.Pool(64)
p.map(one_run, range(len(df)))

# for i in range(len(df)):
#     one_run(i)
    # break
