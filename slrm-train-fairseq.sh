#!/bin/bash
#SBATCH --time=1:00:00
#SBATCH --mem=4G
#SBATCH --gres=gpu:1
#SBATCH --job-name=train_fairseq
#SBATCH --output=log/%x_%j.out

input_data=$1
clstype=$2
output_dir=$3

# require the arguments to be passed
if [ -z "$input_data"  ] || [ -z "$clstype" ] || [ -z "$output_dir" ]; then
    echo "Usage: $0 <input_data> <clstype> <output_dir>"
    exit 1
fi

CUDA_VISIBLE_DEVICES=0 fairseq-train $input_data \
    --task simple_classification \
    --arch pytorch_tutorial_rnn \
    --optimizer adam --lr 0.001 --lr-shrink 0.5 \
    --max-tokens 1000 \
    --target-lang $clstype \
    --max-epoch 40 \
    --save-dir $output_dir
