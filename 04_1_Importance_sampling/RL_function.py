# Importing libraries
import os,sys,glob
import xarray as xr
import numpy as np

# Importing functions
import Functions.wind_model_func as wind_model_func
import Functions.solar_model_func as solar_model_func
import Functions.demand as demand_func
import Functions.grid_func as grid_func
import Functions.config as config

def main_observable(archive_path):
    
    # Import alpha mask for rescaling wind speed
    alpha_mask = xr.open_dataset('/climca/people/onennecke/land_sea_mask/alpha_land_sea.nc')

    # Load installed capacity data
    grid_offshore = xr.open_dataset('/climca/people/onennecke/Wind_Solar_MaStR/processed_data/wind_offshore_ic.nc')
    grid_offshore = grid_offshore['wind_off_cap']
    mask_offshore = xr.where(np.isfinite(grid_offshore), 1, 0)
    grid_onshore = xr.open_dataset('/climca/people/onennecke/Wind_Solar_MaStR/processed_data/wind_onshore_ic.nc')
    grid_onshore = grid_onshore['wind_on_cap']
    mask_onshore = xr.where(np.isfinite(grid_onshore), 1, 0)
    grid_solar = xr.open_dataset('/climca/people/onennecke/Wind_Solar_MaStR/processed_data/solar_ic_netto.nc')
    # grid_solar = xr.open_dataset('/climca/people/onennecke/Wind_Solar_MaStR/processed_data/solar_ic.nc')
    grid_solar = grid_solar['solar_cap']
    mask_solar = xr.where(np.isfinite(grid_solar), 1, 0)
    population = xr.open_dataset('/climca/people/onennecke/population_data/population_regrid_weights.nc')
    population = population['population']
    mask_population = xr.where(np.isfinite(population), 1, 0)
    # Overall mask
    overall_mask = mask_offshore + mask_onshore + mask_solar + mask_population
    overall_mask = xr.where(overall_mask > 0, 1, 0)
    # Load wind height data
    grid_onsh_hub_height = xr.open_dataset('/climca/people/onennecke/Wind_Solar_MaStR/processed_data/wind_onshore_height_weighted.nc')
    grid_offsh_hub_height = xr.open_dataset('/climca/people/onennecke/Wind_Solar_MaStR/processed_data/wind_offshore_height_weighted.nc')

    # Load regridded population weights data
    pop_regr_CIESIN_weights = xr.open_dataset('/climca/people/onennecke/population_data/population_regrid_weights.nc')

    # Load fit values from vdW Paper
    demand_fit_values = xr.open_dataset('/climca/people/onennecke/population_data/demand_fit_values_week.nc')
    
    
    # archive path wäre in deinem Fall /climca/people/ppfleiderer/data_for_onno/step0/c1_000
    h_files = glob.glob(f"{archive_path}/atm/hist/*.nc")
    assert len(h_files) > 0, f"h-file missing - {archive_path}"
    # assert len(h_files) == 1, f"multiple h1-files available - {archive_path}"
    h1_file = [f for f in h_files if "h1" in f]
    h2_file = [f for f in h_files if "h2" in f]
    
    # Load climate data
    variables = ['U10', 'FSDS', 'TREFHT', 'TREFHTMX'] # List of variables

    var_dict = {'U10': 'sfcWind', 'FSDS': 'rsds', 'TREFHT': 'tas', 'TREFHTMX': 'tasmax'}
    fincl2 = ['U10', 'TREFHT', 'TREFHTMX']
    datasets = []
    with xr.open_mfdataset(h1_file, preprocess=grid_func.preprocess) as ds1, xr.open_mfdataset(h2_file, preprocess=grid_func.preprocess) as ds2:
        for var in variables:
            ds = ds1 if var in fincl2 else ds2
            data = ds[[var]]
            nc = grid_func.regrid(data, s = 47, n = 56, w = 6, e = 16)
            if var == 'sfcWind':
                nc = wind_model_func._wind_scale(nc, 100, alpha_mask['mask'], 10)
            nc = nc.rename({var: var_dict[var]})
            datasets.append(nc)
        combined_ds = xr.merge(datasets)

        combined_ds['tas'] = combined_ds['tas'] - 273.15 # Convert temperature from Kelvin to Celsius
        combined_ds['tasmax'] = combined_ds['tasmax'] - 273.15 # Convert maximum temperature from Kelvin to Celsius

        wepot_off = wind_model_func.compute_wind_energy_potential(combined_ds['sfcWind'], grid_offsh_hub_height, 
                                                                    config.a_offshore, config.height_ref, v_cutin=config.v_cutin0_off_unb, 
                                                                    v_rated=config.v_rated0_off_unb, v_cutout=config.v_cutout0_off_unb)
        wepot_on = wind_model_func.compute_wind_energy_potential(combined_ds['sfcWind'], grid_onsh_hub_height, config.a_onshore, 
                                                                    config.height_ref, v_cutin=config.v_cutin0_on_weighted, 
                                                                    v_rated=config.v_rated0_on_weighted, v_cutout=config.v_cutout0_on_weighted)

        combined_ds['wind_off_pot'] = wepot_off['wind_off_pot']
        combined_ds['wind_on_pot'] = wepot_on['wind_on_pot']

        weprod_off = wind_model_func.compute_wind_energy_production(wepot_off, grid_offshore)
        weprod_on = wind_model_func.compute_wind_energy_production(wepot_on, grid_onshore)

        combined_ds['wind_off_prod'] = weprod_off['wind_off_prod']
        combined_ds['wind_on_prod'] = weprod_on['wind_on_prod']

        sepot = solar_model_func.compute_solar_energy_potential(combined_ds['rsds'], combined_ds['tas'], combined_ds['tasmax'], 
                                                                combined_ds['sfcWind'], constants=config.pv_constants_unb, 
                                                                gamma=config.gamma_unb, ref_temp=config.temp_ref_unb)

        # combined_ds['solar_pot'] = sepot['solar_pot'] 
        combined_ds['solar_pot'] = sepot

        seprod = solar_model_func.compute_solar_energy_production(sepot, grid_solar)

        # combined_ds['solar_prod'] = seprod['solar_prod']
        combined_ds['solar_prod'] = seprod


        # Calculate weighted sum
        weighted_temp_list = []
        for y in np.unique(combined_ds['tas']["time.year"].values):
            # print(y)
            ds_weigh_temp_0 = xr.Dataset()
            ds_weigh_temp_0['temp'] = (combined_ds['tas'].sel(time=str(y)) * pop_regr_CIESIN_weights['population']).sum(dim=['lat', 'lon'])
            weighted_temp_list.append(ds_weigh_temp_0)
            
        ds_weighted_temp = xr.concat(weighted_temp_list, dim="time") 

        # Calculate demand
        demand_ds = demand_func.compute_demand(ds_weighted_temp, demand_fit_values.sel(country = 9, period = 'week'))

        timeseries_ds = demand_ds.copy()

        timeseries_ds['sfcWind'] = combined_ds['sfcWind'].where(overall_mask == 1).mean(dim=['lat', 'lon'], skipna=True)
        timeseries_ds['rsds']    = combined_ds['rsds'].where(overall_mask == 1).mean(dim=['lat', 'lon'], skipna=True)
        timeseries_ds['tas']     = combined_ds['tas'].where(overall_mask == 1).mean(dim=['lat', 'lon'], skipna=True)
        timeseries_ds['tasmax']  = combined_ds['tasmax'].where(overall_mask == 1).mean(dim=['lat', 'lon'], skipna=True)

        timeseries_ds['wind_off_prod'] = combined_ds['wind_off_prod'].sum(dim=['lat', 'lon']) / 1000000
        timeseries_ds['wind_on_prod'] = combined_ds['wind_on_prod'].sum(dim=['lat', 'lon']) / 1000000
        timeseries_ds['solar_prod'] = combined_ds['solar_prod'].sum(dim=['lat', 'lon']) / 1000000

        timeseries_ds['total_prod'] = timeseries_ds['wind_off_prod'] + timeseries_ds['wind_on_prod'] + timeseries_ds['solar_prod']
        timeseries_ds['Netto'] = timeseries_ds['total_prod'] - timeseries_ds['demand']
        timeseries_ds['Residual_load'] = timeseries_ds['demand'] - timeseries_ds['total_prod']

        RL = sum(timeseries_ds['Residual_load']).values

        return RL