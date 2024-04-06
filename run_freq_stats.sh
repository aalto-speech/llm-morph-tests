#!/bin/bash
#SBATCH --job-name=freq_stats
#SBATCH --time=00:30:00
#SBATCH --mem=2G
#SBATCH --output=log/%x_%j.out

args=("$@")
python freq_stats_from_conllu.py ${args[@]}
