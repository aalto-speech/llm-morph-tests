#!/bin/bash
#SBATCH --time=2:00:00
#SBATCH --mem=4G
#SBATCH --gres=gpu:1
#SBATCH --job-name=train_fairseq
#SBATCH --output=log/%x_%j.out

# CUDA_VISIBLE_DEVICES=0 fairseq-train \
#     data-bin/iwslt14.tokenized.de-en \
#     --arch transformer_iwslt_de_en --share-decoder-input-output-embed \
#     --optimizer adam --adam-betas '(0.9, 0.98)' --clip-norm 0.0 \
#     --lr 5e-4 --lr-scheduler inverse_sqrt --warmup-updates 4000 \
#     --dropout 0.3 --weight-decay 0.0001 \
#     --criterion label_smoothed_cross_entropy --label-smoothing 0.1 \
#     --max-tokens 4096 \
#     --eval-bleu \
#     --eval-bleu-args '{"beam": 5, "max_len_a": 1.2, "max_len_b": 10}' \
#     --eval-bleu-detok moses \
#     --eval-bleu-remove-bpe \
#     --eval-bleu-print-samples \
#     --best-checkpoint-metric bleu --maximize-best-checkpoint-metric

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
