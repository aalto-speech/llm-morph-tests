#!/bin/bash

expt_dir="expts/prelim3000"

inflected="data/inflected_1000_nouns/inflected_new_filtered_sorted.txt"

#### inflect words
# inflect lemmas with omorfi-generate.sh
cd omorfi
bash ../omorfi-inflect/permute-case-number-person.sh \
    ../${expt_dir}/lemmas.txt \
    ../${expt_dir}/cases.txt \
    ../${expt_dir}/numbers.txt \
    ../${expt_dir}/persons.txt \
    ../inflected
cd ..



#### generate prompts
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

for n_shot in 10
do
    python generate_prompts.py \
        --samples ${expt_dir}/data/samples.json \
        --n_shot $n_shot \
        --batch_size 16 \
        --output_dir ${expt_dir}/data
done


#### run llama
n_shot=5

sbatch --gres=gpu:1 run_llama.sh "7b" ${expt_dir}/data/prompts_${n_shot}shot.json

sbatch --gres=gpu:8 --time=12:00:00 --dependency=afterany:29199073 \
    run_llama.sh "70b" ${expt_dir}/data/prompts_${n_shot}shot.json


#### run poro
# --partition=gpu,dgx-common 
# sbatch --gres=gpu:2 --mem=3GB --partition=gpu,gpushort \
# model_name='TurkuNLP/gpt3-finnish-small'
n_shot=5
model_name='/scratch/elec/morphogen/llm-morph-tests/llms/Poro-34B'
sbatch --time=12:00:00 -A dgx-spa --partition dgx-spa \
    run_poro.sh \
    $model_name \
    ${expt_dir}/data/prompts_${n_shot}shot.json \
    0.3


#### run GPT-4
n_shot=1
model_name="gpt4"
python run_gpt.py \
    --prompts ${expt_dir}/data/prompts_${n_shot}shot.json \
    --out ${expt_dir}/data/prompts_${n_shot}shot_${model_name}.jsonl


#### evaluate
expt_dir="expts/prelim3000"
n_shot=10
model_name="llama2_70b"
python evaluate.py \
    --refs ${expt_dir}/data/refs.json \
    --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}.jsonl \
    --out ${expt_dir}/results_${n_shot}shot_${model_name}.txt


expt_dir="expts/prelim3000"
n_shot=5
model_name="poro"
temp=0.1
(set -x; python evaluate.py \
    --refs ${expt_dir}/data/refs.json \
    --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}_temp${temp}.jsonl \
    --preds-include-prompt \
    --prompts ${expt_dir}/data/prompts_${n_shot}shot.json \
    --out ${expt_dir}/results_${n_shot}shot_${model_name}_temp${temp}.txt)


#### correlation with lemma freq, word form freqs, feats freqs
omorstring_file="${expt_dir}/data/omorstrings.json"
lemma_freq_file="data/stats/lemma_freqs.NOUN.txt"
feats_freq_file="data/stats/upos_feats_freqs.txt"
word_form_freq_file="data/stats/form_freqs.txt"

n_shot=5
model_name="llama2_70b"
python evaluate.py \
    --refs ${expt_dir}/data/refs.json \
    --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}.jsonl \
    --out ${expt_dir}/results_${n_shot}shot_${model_name}.txt \
    --acc-wrt-freq \
    --prompts ${expt_dir}/data/prompts_${n_shot}shot.json \
    --form-freq-file $word_form_freq_file \
    # --lemma-freq-file $lemma_freq_file


#### confusion matrix
expt_dir="expts/prelim3000"
# model_name="llama2_70b"
model_name="poro"
n_shot=5
temp=0.3
python evaluate.py \
    --refs ${expt_dir}/data/refs.json \
    --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}_temp${temp}.jsonl \
    --out ${expt_dir}/confusion_matrix_${n_shot}shot_${model_name}_temp${temp}.png \
    --confusion \
    --preds-include-prompt \
    --prompts ${expt_dir}/data/prompts_${n_shot}shot.json
