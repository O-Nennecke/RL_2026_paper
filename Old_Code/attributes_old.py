from datetime import datetime
import Functions.config as config


def set_global_attributes(dataset, source, grid="gaussian n80", area="EU13+2"):
    """
    set global attributes to xarray.dataset

    parameters
    ----------
    dataset (xarray.Dataset): dataset for which to update attributes
    parameter (string): option to set for different variables 'demand', 'etc..'

    returns
    -------
    dataset (xarray.DataSet) : dataSet with update attributes
    """

    dataset.attrs.update(
        author=config.author_name,
        project=config.project_name,
        source=source,
        history=f'Computed {datetime.now().strftime("%d-%b-%Y (%H:%M)")}',
        area=area,
        grid=grid,
    )

    return dataset


def set_lat_lon_attributes(dataset, names=["lat", "lon"]):
    """
    set attributes to lat and lon dimensions of xarray.dataset

    parameters
    ----------
    dataset (xarray.Dataset): dataset for which to update attributes
    parameter (string): option to set for different variables 'demand', 'etc..'

    returns
    -------
    dataset (xarray.DataSet) : dataSet with update attributes
    """

    dataset = dataset.rename({names[0]: "lat", names[1]: "lon"})
    dataset.lat.attrs.update(
        standard_name="latitude", long_name="latitude", units="degrees_north", axis="Y"
    )
    
    dataset.lon.attrs.update(
        standard_name="longitude", long_name="longitude", units="degrees_east", axis="X"
    )
    
    return dataset



def set_demand_attributes(dataset):
    dataset.demand.attrs.update(
        standard_name="demand",
        long_name="demand computed from weighted T",
        units="GWh",
    )
    return dataset



def update_energy_attributes(
    energy_production, energy_type, unit, eur=False, potential=False
):
    """
    If `eur` is False (default), generates attribute description for location specific , and returns it.
    If `eur` is True, then instead generates attributes for values summed over Europe, and returns that.

    parameters
    ----------
    energy_production (xarray.DataArray): the variable that gets updated
    energy_type (string): the (new) short name of of the energy_type that will be updates
    unit (string): the units of the energy_type that should be updated.
    eur (bool): True for European sum, False for otherwise

    returns
    -------
    xarray.DataArray: input dataArray with updated attributes
    """
    short_name = "tot_" + energy_type if eur else energy_type
    what = " energy potential" if potential else " energy production"
    long_name = "European total " + energy_type + what if eur else energy_type + what

    energy_production.attrs.update(
        units=unit, short_name=short_name, long_name=long_name
    )

    return energy_production