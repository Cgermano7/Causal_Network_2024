import os
from netCDF4 import Dataset
import numpy as np
import geopandas as gpd

def read_shapefile_bounds(shapefile_path):
    shapefile = gpd.read_file(shapefile_path)
    bounds = shapefile.total_bounds  # minx, miny, maxx, maxy
    print(f"Shapefile bounds: {bounds}")
    return bounds

def process_nc_file(filepath, bounds):
    with Dataset(filepath, 'r') as ds:
        lons = ds.variables['longitude'][:]
        lats = ds.variables['latitude'][:]
        tp = ds.variables['tp'][:]  # shape (time, latitude, longitude)

        # Print the longitude and latitude ranges
        print(f"Longitude range: {lons.min()} to {lons.max()}")
        print(f"Latitude range: {lats.min()} to {lats.max()}")

        # Get the indices of the lat/lon points within the bounds
        lon_mask = (lons >= bounds[0]) & (lons <= bounds[2])
        lat_mask = (lats >= bounds[1]) & (lats <= bounds[3])
        
        if not np.any(lon_mask) or not np.any(lat_mask):
            print(f"No data points within bounds for file {filepath}")
            return None

        # Mask the data within the region
        tp_region = tp[:, lat_mask, :][:, :, lon_mask]

        # Check if the masked region contains valid data
        if np.isnan(tp_region).all():
            print(f"All values are NaN in the masked region for file {filepath}")
            return None

        # Compute the daily average total precipitation within the region
        daily_avg_tp = np.mean(tp_region, axis=(1, 2))
        
    return daily_avg_tp

def main(input_dir, output_filepath, shapefile_path):
    bounds = read_shapefile_bounds(shapefile_path)
    
    output_data = []

    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith('.nc'):
            year = filename.split('_')[2][:4]
            month = filename.split('_')[2][4:6]
            filepath = os.path.join(input_dir, filename)
            daily_avg_tp = process_nc_file(filepath, bounds)
            
            if daily_avg_tp is not None:
                for day, avg_tp in enumerate(daily_avg_tp, start=1):
                    output_data.append(f"{year} {month} {day:02d} {avg_tp:.2f}")
    
    # Save to output file
    with open(output_filepath, 'w') as f:
        for line in output_data:
            f.write(f"{line}\n")

if __name__ == "__main__":
    input_dir = "/ourdisk/hpc/ai2es/datasets/dont_archive/era5/TP_Daily/"
    output_filepath = "UpperMidwest_daily_avg.txt"
    shapefile_path = "UpperMidwest.shp"
    
    main(input_dir, output_filepath, shapefile_path)
