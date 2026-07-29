#!/bin/bash
##SBATCH --exclude=compute-[1]
#SBATCH --mail-type=END
#SBATCH --mail-user=diego@hi.is
#SBATCH --partition=s-normal
#SBATCH --mem-per-cpu=3900    # MB RAM per cpu core
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=64
#SBATCH --time=2-00:00:00
#SBATCH --job-name=D4-CNNC-RKS-C
##SBATCH --output=job-%x-%A_%a.out
##SBATCH --error=job-%x-%A_%a.err



early_termination()
{
    echo "EARLY TERMINATION!"
    cp -r $tdir/*  $SLURM_SUBMIT_DIR
    rm -rf $tdir
}

trap early_termination 2 9 15

scratchlocation=/scratch/users/

inpname=$1

export job=orca

module purge
ml load OpenMPI

# OpenMPI Environment Variables for ORCA
export OMPI_MCA_btl='^uct,ofi'
export OMPI_MCA_pml='ucx'
export OMPI_MCA_mtl='^ofi'

# Devel ORCA
export PATH=/hpchome/share/orca/orca_6.1.0:$PATH
export LD_LIBRARY_PATH=/hpchome/share/orca/orca_6.1.0/lib:$LD_LIBRARY_PATH

#qdel()
#{
#    scancel $1
#}
#clean()
#{
#  rm -rf sub.sh.*
#  rm -rf *.txt
#  rm -rf *.out
#  rm -rf *.log
#  rm -rf *.trj
#}

export LC_ALL=C
echo "LANG is $LANG"
echo "LC_ALL is $LC_ALL"

export RSH_COMMAND="/usr/bin/ssh -x"

echo "SLURM_NODELIST is $SLURM_NODELIST"
#Create scratch
if [ ! -d $scratchlocation/$USER ] 
then
  mkdir -p $scratchlocation/$USER
fi
tdir=$(mktemp -d $scratchlocation/$USER/orcajob__$SLURM_JOBID-XXXX)
chmod +xr $tdir

if [ ! -d "$tdir" ]; then
echo "Scratch dir does not exist on this node"
echo "Exiting..."
exit
fi

#Copying submitted inputfile
cp $SLURM_SUBMIT_DIR/* $tdir/

# cd to scratch
cd $tdir

# Copy job and node info to beginning of outputfile
echo "Job execution start: $(date)" > $SLURM_SUBMIT_DIR/$job.out
echo "Walltime is: 240 hours" >> $SLURM_SUBMIT_DIR/$job.out
echo "Shared library path: $LD_LIBRARY_PATH" >> $SLURM_SUBMIT_DIR/$job.out
echo "Path environment: $PATH" >> $SLURM_SUBMIT_DIR/$job.out
echo "Slurm Job ID is: ${SLURM_JOBID}" >> $SLURM_SUBMIT_DIR/$job.out
echo "slurm Job name is: ${SLURM_JOB_NAME}" >> $SLURM_SUBMIT_DIR/$job.out
echo "Scratchdir is: $tdir" >> $SLURM_SUBMIT_DIR/$job.out

header=$(df -h | grep Filesy)
scratchsize=$(df -h | grep scratch)
echo "Scratch size is (before job run):" >> $SLURM_SUBMIT_DIR/$job.out
echo "$header" >> $SLURM_SUBMIT_DIR/$job.out
echo "$scratchsize" >> $SLURM_SUBMIT_DIR/$job.out

echo $SLURM_NODELIST >> $SLURM_SUBMIT_DIR/$job.out

# Full path is necessary for ORCA to run in parallel                                                                            
/hpchome/share/orca/orca_6.1.0/orca $inpname > $SLURM_SUBMIT_DIR/${inpname%.*}.out

header=$(df -h | grep Filesy)
scratchsize=$(df -h | grep scratch)
echo "" >> $SLURM_SUBMIT_DIR/$job.out
echo "Scratch size is (after job, before scratch deletion):" >> $SLURM_SUBMIT_DIR/$job.out
echo "$header" >> $SLURM_SUBMIT_DIR/$job.out
echo "$scratchsize" >> $SLURM_SUBMIT_DIR/$job.out

for f in "$tdir"/*; do
    [ -e "$f" ] || continue
    if [[ "$(basename "$f")" != "${inpname%.*}.out" ]]; then
        cp -r "$f" "$SLURM_SUBMIT_DIR/"
    fi
done

rm -rf $tdir

cd $SLURM_SUBMIT_DIR
rm *tmp
rm *tmp*
rm *bas*
