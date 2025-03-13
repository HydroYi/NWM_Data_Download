#!/bin/bash
#SBATCH --job-name=download_nwm_ext
#SBATCH --output=download_nwm_ext%j.out
#SBATCH --error=download_nwm_ext%j.err
#SBATCH --time=50:00:00                # Maximum runtime (adjust as needed)
#SBATCH --nodes=1                      # Number of nodes
#SBATCH --ntasks=1                     # Number of tasks
#SBATCH --cpus-per-task=1              # Number of CPUs
#SBATCH --mem=4G                       # Memory per node
#SBATCH --mail-type=ALL                # Notifications for job (BEGIN, END, FAIL, ALL)
#SBATCH --account=yhon0

# Load necessary modules
module purge
module load python  # Load an appropriate Python module

python3 -m venv ~/gsutil_env
source ~/gsutil_env/bin/activate

# Activate virtual environment with gsutil
source ~/my_gsutil_env/bin/activate
pip install gsutil

# Make the script executable
chmod +x nwm_assim_archive.sh

# Run the script
./nwm_assim_archive.sh

# Deactivate the virtual environment
deactivate
