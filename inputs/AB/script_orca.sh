#!/bin/bash
##SBATCH --exclude=compute-[1]
##SBATCH --mail-type=END
##SBATCH --mail-user=diego@hi.is
#SBATCH --partition=s-normal
##SBATCH --mem-per-cpu=3900    # MB RAM per cpu core
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=64
#SBATCH --time=2-00:00:00
#SBATCH --job-name=lidiabs

# Load ORCA module (replace with your cluster's module command)

ml use /hpcapps/lib-edda/modules/all/Core
ml use /hpcapps/lib-chem/modules/all 

ml load ORCA/6.1.0
iname=$1
cp $iname $TMPDIR
cd $TMPDIR

# Set ORCA executable path if needed, or make sure it's in your PATH
full_orca=$(which orca)

# Run ORCA calculation
$full_orca $iname > $SLURM_SUBMIT_DIR/$iname.out

cp ${iname}* $SLURM_SUBMIT_DIR
