#!/bin/bash
#SBATCH --job-name=preproc_fairseq
#SBATCH --time=00:30:00
#SBATCH --mem=2G
#SBATCH --output=log/%x_%j.out

# module load miniconda
# conda activate fairseq

train_prefix=$1
valid_prefix=$2
test_prefix=$3

fairseq-preprocess \
  --trainpref $train_prefix --validpref $valid_prefix --testpref $test_prefix \
  --source-lang input --target-lang label \
  --destdir data/fairseq --dataset-impl raw
