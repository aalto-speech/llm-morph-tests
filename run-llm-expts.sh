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

# verbs
bash src/bash/generate-wordlist-withtags.sh \
    data/omorfi_verb_lexemes_filtered.txt \
    data/omorfi_verb_lexemes_filtered_inflected.txt

# do nouns in parallel since there are many
split -d -l 4000 \
    data/omorfi_noun_lexemes_filtered.txt \
    data/omorfi_noun_lexemes_filtered.txt.
screen
filenumber=0
bash generate-wordlist-withtags-nouns.sh \
    data/omorfi_noun_lexemes_filtered.txt.0${filenumber} \
    data/omorfi_noun_lexemes_filtered_inflected.txt.0${filenumber} \
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


#### generate prompts from the real corpus set with frequencies
# inflected="data/form_freqs_lower_10m_forms_and_freqs_filtered_seplines.txt"
# inflected="data/inflected_1000_nouns/inflected_new_filtered_sorted.txt"
inflected=data/omorfi_noun_lexemes_filtered_inflected_all_filtered_form2feats_random5k.txt 
expt_dir="expts/random2000"

word_class="noun"
python generate_prompts.py \
    --inflected $inflected \
    --n_shot 0 \
    --n_samples 2000 \
    --word_class $word_class \
    --output_dir ${expt_dir}/data

for n_shot in 1 5 10
do
    python generate_prompts.py \
        --samples ${expt_dir}/data/samples.json \
        --n_shot $n_shot \
        --output_dir ${expt_dir}/data
done

###############################################################################
#### run LLMs

#### run llama-2
n_shot=1

sbatch --gres=gpu:1 llama.slrm "7b" ${expt_dir}/data/prompts_${n_shot}shot.json

expt_dir="expts/random2000"
llama_v="7b"
n_shot=10
sbatch  --time=6:00:00 -A dgx-spa --partition dgx-spa --gres=gpu:v100:1 \
    --dependency=afterany:31391942,31391944,31391945,31391947,31391949,31391950 \
    slrm-llama.sh \
    $llama_v \
    ${expt_dir}/data/prompts_${n_shot}shot.json


sbatch  --time=6:00:00 -A dgx-spa --partition dgx-spa --gres=gpu:v100:1 \
    slrm-llama.sh \
    $llama_v \
    ${expt_dir}/data/prompts_${n_shot}shot.json


#SBATCH --partition dgx-spa
#SBATCH -A dgx-spa

#### run llama-3 --- skip this since there is no time & it's not important
hub_dir=/scratch/shareddata/dldata/huggingface-hub-cache/hub/

# 70b
model="${hub_dir}/models--meta-llama--Meta-Llama-3-70B/snapshots/7cde9a27957f27ce5677b1f838ccaeeb69acc8d0/"

# 8b
model="${hub_dir}/models--meta-llama--Meta-Llama-3-8B/snapshots/b6887ce03ea47d068bf8502ba6ed27f8c5c12a6b/"

expt_dir="expts/random2000"
n_shot=0
sbatch --time=12:00:00 -A dgx-spa --partition dgx-spa \
    slrm-transformers.sh \
    $model \
    ${expt_dir}/data/prompts_${n_shot}shot.json \
    0.5 \
    llama3_8b



#### run poro
# --partition=gpu,dgx-common 
# sbatch --gres=gpu:2 --mem=3GB --partition=gpu,gpushort \
# model_name='TurkuNLP/gpt3-finnish-small'
expt_dir="expts/random2000"
n_shot=10
model='/scratch/elec/morphogen/llm-morph-tests/llms/Poro-34B'
sbatch --time=24:00:00 --dependency=afterany:31391838 -A dgx-spa --partition dgx-spa \
    slrm-transformers.sh \
    $model \
    ${expt_dir}/data/prompts_${n_shot}shot.json \
    0.5 \
    poro

-A dgx-spa --partition dgx-spa 
--partition=gpu --gres=gpu:v100:3

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
expt_dir="expts/random2000"
for model_name in llama2_7b
do
    for n_shot in 10
    do
        python evaluate.py \
            --refs ${expt_dir}/data/refs.json \
            --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}.jsonl \
            --out ${expt_dir}/results_${n_shot}shot_${model_name}.txt
    done
done

# evaluate poro
expt_dir="expts/random2000"
model_name="poro"
temp=0.5
for n_shot in 1 5
do
    (set -x; python evaluate.py \
        --refs ${expt_dir}/data/refs.json \
        --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}_temp${temp}.jsonl \
        --preds-include-prompt \
        --prompts ${expt_dir}/data/prompts_${n_shot}shot.json \
        --out ${expt_dir}/results_${n_shot}shot_${model_name}_temp${temp}.txt)
done

# evaluate gpt4
expt_dir="expts/prelim3000"
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

# evaluate TNPP
expt_dir="expts/prelim3000"
(set -x; python evaluate.py \
    --refs ${expt_dir}/data/refs.json \
    --preds ${expt_dir}/data/samples.json.conllu.parsed.json \
    --translate-preds \
    --out ${expt_dir}/results_tnpp.txt)

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


expt_dir="expts/prelim3000_incorrect_peukalo"
n_shot=1
model_name="llama2_70b"
python evaluate.py \
    --refs ${expt_dir}/data/refs.json \
    --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}.jsonl \
    --out ${expt_dir}/results_${n_shot}shot_${model_name}_new.txt \
    --acc-wrt-freq \
    --prompts ${expt_dir}/data/prompts_${n_shot}shot.json \
    --form-freq-from-corpus-file ${expt_dir}/data/samples_with_freqs_from_corpus.json

    # --form-freq-file $word_form_freq_file \
    # --lemma-freq-file $lemma_freq_file


#### confusion matrix
expt_dir="expts/random2000"
model_name="poro"
n_shot=10
temp=0.5
python evaluate.py \
    --refs ${expt_dir}/data/refs.json \
    --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}_temp${temp}.jsonl \
    --out ${expt_dir}/confusion_matrix_${n_shot}shot_${model_name}_temp${temp}.png \
    --confusion \
    --preds-include-prompt \
    --prompts ${expt_dir}/data/prompts_${n_shot}shot.json

# llama
expt_dir="expts/random2000"
model_name="llama2_70b"
n_shot=10
python evaluate.py \
    --refs ${expt_dir}/data/refs.json \
    --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}.jsonl \
    --out ${expt_dir}/confusion_matrix_${n_shot}shot_${model_name}.png \
    --confusion


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
