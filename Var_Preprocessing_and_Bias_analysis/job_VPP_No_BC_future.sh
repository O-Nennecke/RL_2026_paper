#!/bin/bash

#SBATCH --job-name=var_preprocessing_future      # Specify job name

#SBATCH --partition=pq1     # Specify partition name

#SBATCH --time=24:00:00        # Set a limit on the total run time

#SBATCH --account=onennecke       # Charge resources on this project account

#SBATCH --output=log/%j  # Output file

#SBATCH --error=log/%j    # Error file

srun python Var_Preprocessing_future.py