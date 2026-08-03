#!/bin/sh
IN=$1
NODES=$2
CPUS=$3
TIMEHRS=$4
FIL=${IN%.*}
SUBMIT=.qsub.${FIL}
THISDIR=$PWD
cat > $SUBMIT << !EOF
#!/bin/sh
# -------------------------------------------------------------------
#SBATCH -J $FIL
#SBATCH --chdir=$THISDIR
#SBATCH -o $IN.%J.log
#SBATCH -e $IN.%J.err
#SBATCH --job-name=$IN
#SBATCH --mail-type=END
#SBATCH --mail-user=diego@hi.is
#SBATCH --partition=64cpu_256mem
#SBATCH --mem-per-cpu=3900    # MB RAM per cpu core
#SBATCH --nodes=$NODES
#SBATCH --ntasks-per-node=$CPUS
#SBATCH --time=$TIMEHRS-00:00:00
# -------------------------------------------------------------------
cd $THISDIR
source ~/.bashrc
module load openmpi4
# Run GPAW
start=\`date +%s\`
mpiexec -n $CPUS gpaw python $IN
end=\`date +%s\`
# Write ending statements to stdout
runtime=\$((end-start))
echo Stop time is \`date\`
echo 'Time (s): ' \`printf '%d\n' \$runtime\`
echo 'Used walltime: ' \`printf '%dh:%dm:%ds\n' \$((\$runtime/3600)) \$((\$runtime%3600/60)) \$((\$runtime%60))\`
echo ========= Job finished ===================
!EOF
sbatch $SUBMIT
