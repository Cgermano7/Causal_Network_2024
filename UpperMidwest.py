import os
from netCDF4 import Dataset
import numpy as np

def process_nc_file(filepath, lon_min, lon_max, lat_min, lat_max):
    with Dataset(filepath, 'r') as ds:
        lons = ds.variables['longitude'][:]
        lats = ds.variables['latitude'][:]
        tp = ds.variables['tp'][:]  # shape (time, latitude, longitude)

        # Convert longitude range from 0-360 to -180-180
        lons = np.where(lons > 180, lons - 360, lons)

        # Get the indices of the lat/lon points within the specified bounds
        lon_mask = (lons >= lon_min) & (lons <= lon_max)
        lat_mask = (lats >= lat_min) & (lats <= lat_max)
        
        if not np.any(lon_mask) or not np.any(lat_mask):
            print(f"No data points within bounds for file {filepath}")
            return None

        # Mask the data within the region
        tp_region = tp[:, lat_mask, :][:, :, lon_mask]

        # Compute the daily average total precipitation within the region
        daily_avg_tp = np.mean(tp_region, axis=(1, 2))

    return daily_avg_tp

def main(input_dir, output_filepath):
    # Define the bounds manually
    lon_min, lon_max = -97.25, -82.25
    lat_min, lat_max = 40.25, 49.25

    output_data = []

    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith('.nc'):
            year = filename.split('_')[2][:4]
            month = filename.split('_')[2][4:6]
            filepath = os.path.join(input_dir, filename)
            daily_avg_tp = process_nc_file(filepath, lon_min, lon_max, lat_min, lat_max)
            
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
    
    main(input_dir, output_filepath)
