#!/bin/bash

#SBATCH --job-name=bias_corr      # Specify job name

#SBATCH --partition=pq2     # Specify partition name

#SBATCH --time=12:00:00        # Set a limit on the total run time

#SBATCH --account=onennecke       # Charge resources on this project account

#SBATCH --output=log/%j  # Output file

#SBATCH --error=log/%j    # Error file

srun python BC_parallel.py