#!/bin/bash

###############################################################################
#### get the inflected forms from the FST

cd omorfi

# get noun, verb etc. lexemes from omorfi
# filter punctuation, proper names, acronyms etc.
grep NOUN omorfi/src/lexemes.tsv \
    | grep -v -P ACRO \
    | awk '{print $1}' \
    | grep -P ^[a-zäö]+$ \
    > data/omorfi_noun_lexemes_filtered.txt

grep VERB omorfi/src/lexemes.tsv \
    | awk '{print $1}' \
    | grep -P ^[a-zäö]+$ \
    > data/omorfi_verb_lexemes_filtered.txt

grep ADJ omorfi/src/lexemes.tsv \
    | awk '{print $1}' \
    | grep -P ^[a-zäö]+$ \
    > data/omorfi_adj_lexemes_filtered.txt


# dump the inflected forms of the filtered lexemes from the FST 
bash src/bash/generate-wordlist-withtags-nouns.sh \
    ../data/omorfi_noun_lexemes_filtered.txt \
    ../data/omorfi_noun_lexemes_filtered_inflected.txt

bash src/bash/generate-wordlist-withtags-verbs.sh \
    ../data/omorfi_verb_lexemes_filtered.txt \
    ../data/omorfi_verb_lexemes_filtered_inflected.txt

bash src/bash/generate-wordlist-withtags-adj.sh \
    ../data/omorfi_adj_lexemes_filtered.txt \
    ../data/omorfi_adj_lexemes_filtered_inflected.txt


filenumber=5
bash src/bash/generate-wordlist-withtags-nouns-parallel.sh \
    ../data/omorfi_noun_lexemes_filtered.txt.tail84000.0${filenumber} \
    ../data/omorfi_noun_lexemes_filtered_inflected.txt.0${filenumber} \
    temp${filenumber}

    
###############################################################################
#### generate prompts
inflected="data/inflected_1000_nouns/inflected_new_filtered_sorted.txt"
expt_dir="expts/prelim3000"

n_shot=0
for word_class in "noun"
do
    python generate_prompts.py \
        --inflected $inflected \
        --n_shot $n_shot \
        --n_samples 3000 \
        --word_class $word_class \
        --output_dir ${expt_dir}/data
done

for n_shot in 3
do
    python generate_prompts.py \
        --samples ${expt_dir}/data/samples.json \
        --n_shot $n_shot \
        --output_dir ${expt_dir}/data
done

###############################################################################
#### run LLMs

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
expt_dir="expts/prelim3000"
# n_shot=1
# model_name="gpt4-turbo"
sample_range="0-100"
for n_shot in 3 10
do
    for model_name in gpt4 gpt4-turbo
    do
        python inference_gpt.py \
            --prompts ${expt_dir}/data/prompts_${n_shot}shot.json \
            --model $model_name \
            --sample-range $sample_range \
            --out ${expt_dir}/data/prompts_${n_shot}shot_${model_name}_${sample_range}.jsonl
    done
done


###############################################################################

#### evaluate

# evaluate llama
expt_dir="expts/prelim3000"
n_shot=10
model_name="llama2_70b"
python evaluate.py \
    --refs ${expt_dir}/data/refs.json \
    --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}.jsonl \
    --out ${expt_dir}/results_${n_shot}shot_${model_name}.txt

# evaluate poro
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


# evaluate gpt4
expt_dir="expts/prelim3000"
# n_shot=1
# model_name="gpt4-turbo"
sample_range="0-100"
for n_shot in 0 1 3 10
do
    for model_name in gpt4 gpt4-turbo
    do
        python evaluate.py \
            --refs ${expt_dir}/data/refs.json \
            --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}_${sample_range}.jsonl \
            --refs-range 0 100 \
            --out ${expt_dir}/results_${n_shot}shot_${model_name}_${sample_range}_newparsing.txt
    done
done

###############################################################################

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


expt_dir="expts/prelim3000"
model_name="gpt4"
# n_shot=5
temp=1.0
sample_range="0-100"
for n_shot in 0
do
    for model_name in gpt4-turbo
    do
        python evaluate.py \
            --refs ${expt_dir}/data/refs.json \
            --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}_${sample_range}.jsonl \
            --out ${expt_dir}/confusion_matrix_${n_shot}shot_${model_name}_${sample_range}_temp${temp}.png \
            --confusion \
            --refs-range 0 100
    done
done
