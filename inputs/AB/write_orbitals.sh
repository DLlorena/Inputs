#!/bin/bash

# Check if the filename argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <filename>"
  exit 1
fi

# Get the filename from the command line argument
filename=$1

# Loop over spin channels (0 and 1)
for alpha in 0 1; do
    # Loop over orbitals
    for num in {45..49}; do
        # Generate input dynamically and pass it to orca_plot
        printf "%s\n" "5" "7" "3" "$alpha" "2" "$num" "11" "12" | /hpchome/share/orca/orca_6.1.0/orca_plot "$filename" -i -
    done
done


if [ ! -d orbitals ]; then
  mkdir orbitals
fi

mv *cube orbitals/
