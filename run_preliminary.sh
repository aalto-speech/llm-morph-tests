#!/bin/bash

expt_dir="expts/prelim3000"

inflected="data/inflected_1000_nouns/inflected_new_filtered_sorted.txt"

# generate prompts
n_shot=1
for word_class in "noun"
do
    python generate_prompts.py \
        --inflected $inflected \
        --n_shot $n_shot \
        --n_samples 3000 \
        --batch_size 16 \
        --word_class $word_class \
        --output_dir ${expt_dir}/data
done

for n_shot in 5
do
    python generate_prompts.py \
        --inflected $inflected \
        --samples ${expt_dir}/data/samples.json \
        --n_shot $n_shot \
        --n_samples 100 \
        --batch_size 16 \
        --word_class $word_class \
        --output_dir ${expt_dir}/data
done


# run llama
sbatch --gres=gpu:1 run_llama.sh "7b" ${expt_dir}/data/prompts_1shot.json
sbatch --gres=gpu:1 run_llama.sh "7b" ${expt_dir}/data/prompts_5shot.json

sbatch --gres=gpu:8 --time=12:00:00 --dependency=afterany:29153714 \
    run_llama.sh "70b" ${expt_dir}/data/prompts_5shot.json

# run poro
sbatch --dependency=afterany:29154816 --time=12:00:00 \
    run_poro.sh ${expt_dir}/data/prompts_1shot.json

# run GPT-4



# evaluate
python evaluate.py \
    --refs expts/preliminary/data/refs.json \
    --preds expts/preliminary/data/prompts_5shot_llama2_70b.jsonl \
    --out llama-70b-results.txt
