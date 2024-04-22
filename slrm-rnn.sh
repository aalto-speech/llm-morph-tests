#!/bin/bash
#SBATCH --job-name=test
#SBATCH --time=00:30:00
#SBATCH --mem=2G
#SBATCH --output=log/%x_%j.out

# clstype="number"
# clstype="case"
clstype="person"
datadir=data/fairseq/prelim3000
# subset_size=50000
subset_size=10k

# python preprocess.py \
#     --wordforms-json expts/prelim3000/data/samples.json \
#     --omorstrings-json expts/prelim3000/data/omorstrings.json \
#     --output-dir $datadir \
#     --train-valid-test-split "0-0-100" \
#     --classtype $clstype

orig_datadir="data/fairseq/random${subset_size}"

python eval_classifier.py \
    $orig_datadir/bin-$clstype \
    --target-lang $clstype \
    --path checkpoints/random${subset_size}/$clstype/checkpoint_best.pt \
    --test-set $datadir/test \
    >> results_random${subset_size}_${clstype}_prelim3000.txt
