import xarray as xr
import numpy as np

def create_ref_grid(variable_name):
    # Create reference grid
    lats = np.arange(47, 57)    # Latitude
    lons = np.arange(5, 17)     # Longitude

    # Initialize values for the empty grid (with NaN)
    data = np.full((len(lats), len(lons)), np.nan)

    # Create new xarray.DataArray based on the dimensions
    grid = xr.DataArray(
        data=data,
        coords={"lat": lats, "lon": lons},
        dims=["lat", "lon"],
        name=variable_name
    )
    
    # Add metadata for grid type and CRS
    grid.attrs['gridtype'] = 'lonlat'  # Set gridtype to lonlat (NOT generic)
    grid.attrs['crs'] = 'EPSG:4326'  # CRS for WGS84
    grid['crs'] = 4326
    grid['gridtype'] = 'lonlat'
    
    grid['lat'].attrs['standard_name'] = 'latitude'
    grid['lon'].attrs['standard_name'] = 'longitude'
    return grid