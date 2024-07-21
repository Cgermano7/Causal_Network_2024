# Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sklearn
import tigramite
from tigramite import data_processing as pp
from tigramite.toymodels import structural_causal_processes as toys
from tigramite import plotting as tp
from tigramite.pcmci import PCMCI
from tigramite.lpcmci import LPCMCI
from tigramite.independence_tests.parcorr import ParCorr
from tigramite.independence_tests.robust_parcorr import RobustParCorr
from tigramite.independence_tests.parcorr_wls import ParCorrWLS
from tigramite.independence_tests.gpdc import GPDC
from tigramite.independence_tests.cmiknn import CMIknn
from tigramite.independence_tests.cmisymb import CMIsymb
from tigramite.independence_tests.gsquared import Gsquared
from tigramite.independence_tests.regressionCI import RegressionCI

# Paths to the datasets
datasets = {
    'UpperMidwest': '/ourdisk/hpc/ai2es/datasets/dont_archive/era5/UpperMidwest_daily_sum.txt',
    'OhioValley': '/ourdisk/hpc/ai2es/datasets/dont_archive/era5/OhioValley_daily_sum.txt',
    'AO': '/ourdisk/hpc/ai2es/datasets/dont_archive/teleconnection_indices/AO_Daily_Filtered_Normalized.txt',
    'EPO': '/ourdisk/hpc/ai2es/datasets/dont_archive/teleconnection_indices/EPO_Daily_Filtered_Normalized.txt',
    'PNA': '/ourdisk/hpc/ai2es/datasets/dont_archive/teleconnection_indices/PNA_Daily_Filtered_Normalized.txt',
    'ENSO': '/ourdisk/hpc/ai2es/datasets/dont_archive/teleconnection_indices/ENSO_Daily_Filtered_Normalized.txt',
    'NAO': '/ourdisk/hpc/ai2es/datasets/dont_archive/teleconnection_indices/NAO_Daily_Filtered_Normalized.txt',
    'WPO': '/ourdisk/hpc/ai2es/datasets/dont_archive/teleconnection_indices/WPO_Daily_Filtered_Normalized.txt'
}

# Read and merge datasets
def read_dataset(filepath):
    df = pd.read_csv(filepath, sep=' ', header=None, names=['Year', 'Month', 'Day', 'Value'])
    df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
    return df.set_index('Date')['Value']

dataframes = {name: read_dataset(path) for name, path in datasets.items()}

# Align data by date
combined_df = pd.concat(dataframes.values(), axis=1)
combined_df.columns = list(dataframes.keys())
combined_df.dropna(inplace=True)  # Drop missing values

# Convert to numpy array
data = combined_df.values
T, N = data.shape

# Initialize dataframe object for Tigramite
var_names = list(combined_df.columns)
dataframe = pp.DataFrame(data, datatime=np.arange(T), var_names=var_names)

# Plot timeseries
tp.plot_timeseries(dataframe)
plt.show()

# Run PCMCI
pcmci = PCMCI(dataframe=dataframe, cond_ind_test=ParCorr())
results = pcmci.run_pcmci(tau_max=10, pc_alpha=0.05)

# Plotting results
pcmci.print_significant_links(p_matrix=results['p_matrix'], val_matrix=results['val_matrix'], alpha_level=0.05)
tp.plot_graph(
    val_matrix=results['val_matrix'],
    links_dict=pcmci.return_significant_parents(pq_matrix=results['p_matrix'], alpha_level=0.05),
    var_names=dataframe.var_names,
    link_colorbar_label='MCI',
    node_colorbar_label='auto-MCI'
)
plt.show()
