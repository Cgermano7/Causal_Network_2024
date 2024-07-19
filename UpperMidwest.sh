#!/bin/bash
#SBATCH --nodes=1
#SBATCH -n 4
#SBATCH --mem 16G
#SBATCH --time=01:00:00
#SBATCH --job-name=UpperMidwest_precip_avg
#SBATCH --mail-user=rayarmy@schooner.oscer.ou.edu
#SBATCH --mail-type=ALL
#SBATCH --mail-type=END
#SBATCH --output=/home/rayarmy/UpperMidwest.out
#SBATCH --error=/home/rayarmy/UpperMidwest.err

module load netcdf4-python

python UpperMidwest.py
