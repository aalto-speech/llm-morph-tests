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

for n_shot in 0
do
    python generate_prompts.py \
        --samples ${expt_dir}/data/samples.json \
        --n_shot $n_shot \
        --output_dir ${expt_dir}/data
done

# chain of thought
for n_shot in 1
do
    python generate_prompts.py \
        --samples ${expt_dir}/data/samples.json \
        --n_shot $n_shot \
        --cot \
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

expt_dir="expts/random2000"
llama_v="70b"
n_shot=10
sbatch  --time=24:00:00 -A dgx-spa --partition dgx-spa --gres=gpu:v100:8 \
    slrm-llama.sh \
    $llama_v \
    ${expt_dir}/data/prompts_${n_shot}shot.json


# CoT
expt_dir="expts/random2000"
llama_v="70b-chat"
sbatch  --time=16:00:00 -A dgx-spa --partition dgx-spa --gres=gpu:v100:8 \
    --dependency=afterany:31400814 \
    slrm-llama.sh \
    $llama_v \
    ${expt_dir}/data/prompts_1shot_cot.json
    
    

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
cotornot=""
temp=0.0
model='/scratch/elec/morphogen/llm-morph-tests/llms/Poro-34B'
sbatch --time=12:00:00 --partition=gpu \
    --gres=gpu:v100:3 \
    slrm-transformers.sh \
    $model \
    ${expt_dir}/data/prompts_${n_shot}shot${cotornot}.json \
    $temp \
    poro

-A dgx-spa --partition dgx-spa 
--partition=gpu --gres=gpu:v100:3

#### run GPT models
expt_dir="expts/random2000"
# remember to set max tokens to 800 if running CoT
cotornot=""
sample_range="700-2000"
temp=0.0
for n_shot in 0
do
    for model_name in gpt4-turbo
    do
        python inference_gpt.py \
            --prompts ${expt_dir}/data/prompts_${n_shot}shot${cotornot}.json \
            --model $model_name \
            --sample-range $sample_range \
            --temperature $temp \
            --out ${expt_dir}/data/prompts_${n_shot}shot${cotornot}_${model_name}_temp${temp}_${sample_range}.jsonl
    done
done


########## combine files
temp=0.0
for n_shot in 10
do
    for model_name in gpt4-turbo
    do
        python combine_json.py \
            --json_files  expts/random2000/data/prompts_${n_shot}shot_${model_name}_temp${temp}_0-1000.jsonl \
                          expts/random2000/data/prompts_${n_shot}shot_${model_name}_temp${temp}_1000-2000.jsonl \
            --output_file expts/random2000/data/prompts_${n_shot}shot_${model_name}_temp${temp}_0-2000.jsonl
    done
done

###############################################################################

#### evaluate

# evaluate llama
expt_dir="expts/random2000"
eval_type="accuracy"
# for model_name in llama2_7b llama2_13b llama2_70b llama2_13b-chat llama2_70b-chat

for model_name in llama2_7b
do
    for n_shot in 10
    do
        python evaluate.py \
            --refs ${expt_dir}/data/refs.json \
            --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}_temp0.0.jsonl \
            --out ${expt_dir}/results_${n_shot}shot_${model_name}_temp0.0_${eval_type}.txt \
            --eval-type $eval_type
    done
done

# evaluate poro
expt_dir="expts/random2000"
# expt_dir="expts/prelim3000_incorrect_peukalo"
model_name="poro"
temp=0.5
# eval_type="f1-scores"
eval_type="accuracy"
# eval_type="print_errors"
# n_shot=5
for n_shot in 0 1 5 10
do
    python evaluate.py \
        --refs ${expt_dir}/data/refs.json \
        --preds ${expt_dir}/data/prompts_${n_shot}shot_${model_name}_temp${temp}.jsonl \
        --preds-include-prompt \
        --prompts ${expt_dir}/data/prompts_${n_shot}shot.json \
        --out ${expt_dir}/results_${n_shot}shot_${model_name}_temp${temp}_${eval_type}.txt \
        --eval-type $eval_type
done

# evaluate gpt models
expt_dir="expts/random2000"
sample_range="0-700"
cotornot=""
# eval_type="f1-scores"
eval_type="accuracy"
temp=0.0
for n_shot in 0
do
    for model_name in gpt4-turbo
    do
        echo ""
        echo "###################################################"
        echo "Evaluating ${n_shot}shot${cotornot} ${model_name} ${sample_range}"
        python evaluate.py \
            --refs ${expt_dir}/data/refs.json \
            --preds ${expt_dir}/data/prompts_${n_shot}shot${cotornot}_${model_name}_temp${temp}_${sample_range}.jsonl \
            --refs-range $sample_range \
            --out ${expt_dir}/results_${n_shot}shot${cotornot}_${model_name}_temp${temp}_${sample_range}_${eval_type}.txt \
            --cot $cotornot \
            --samples ${expt_dir}/data/samples.json \
            --eval-type $eval_type
    done
done

# expt_dir="expts/random2000"
expt_dir="expts/prelim3000_incorrect_peukalo"
sample_range="0-100"
cotornot=""
# eval_type="f1-scores"
eval_type="accuracy"
for n_shot in 10
do
    for model_name in gpt4
    do
        echo ""
        echo "###################################################"
        echo "Evaluating ${n_shot}shot${cotornot} ${model_name} ${sample_range}"
        python evaluate.py \
            --refs ${expt_dir}/data/refs.json \
            --preds ${expt_dir}/data/prompts_${n_shot}shot${cotornot}_${model_name}_${sample_range}.jsonl \
            --refs-range $sample_range \
            --out ${expt_dir}/results_${n_shot}shot${cotornot}_${model_name}_${sample_range}_${eval_type}.txt \
            --cot $cotornot \
            --samples ${expt_dir}/data/samples.json \
            --eval-type $eval_type
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


###############################################################################
#### confusion matrix

# poro
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


# gpt
expt_dir="expts/random2000"
sample_range="0-1000"
cotornot=""
temp=0.0
for n_shot in 10
do
    for model_name in gpt4
    do
        python evaluate.py \
            --refs ${expt_dir}/data/refs.json \
            --preds ${expt_dir}/data/prompts_${n_shot}shot${cotornot}_${model_name}_temp${temp}_${sample_range}.jsonl \
            --out ${expt_dir}/confusion_matrix_${n_shot}shot${cotornot}_${model_name}_${sample_range}_temp${temp}.png \
            --eval-type "confusion" \
            --refs-range $sample_range
    done
done

#  two case confusions
expt_dir="expts/random2000"
# n_shot=5
temp=0.0
sample_range="0-2000"
cotornot=""
category="case"
for model_name in gpt4-turbo
do
    python evaluate.py \
        --refs ${expt_dir}/data/refs.json \
        --preds ${expt_dir}/data/prompts_0shot${cotornot}_${model_name}_${sample_range}.jsonl ${expt_dir}/data/prompts_10shot${cotornot}_${model_name}_temp${temp}_${sample_range}.jsonl \
        --out ${expt_dir}/2confusion_matrix_${category}${cotornot}_${model_name}_${sample_range}.png \
        --eval-type two-${category}-confusion \
        --refs-range $sample_range
done

#  many confusions
expt_dir="expts/random2000"
# n_shot=5
temp=0.0
sample_range="0-2000"
cotornot=""
for model_name in gpt4-turbo
do
    python evaluate.py \
        --refs ${expt_dir}/data/refs.json \
        --preds ${expt_dir}/data/prompts_0shot${cotornot}_${model_name}_${sample_range}.jsonl \
            ${expt_dir}/data/prompts_{1,5,10}shot${cotornot}_${model_name}_temp${temp}_${sample_range}.jsonl \
        --out ${expt_dir}/all_confusions${cotornot}_${model_name}_${sample_range}_temp${temp}.png \
        --eval-type many-confusions \
        --refs-range $sample_range
done
for model_name in gpt3.5-turbo
do
    python evaluate.py \
        --refs ${expt_dir}/data/refs.json \
        --preds ${expt_dir}/data/prompts_{0,1,5,10}shot${cotornot}_${model_name}_temp${temp}_${sample_range}.jsonl \
        --out ${expt_dir}/all_confusions${cotornot}_${model_name}_${sample_range}_temp${temp}.png \
        --eval-type many-confusions \
        --refs-range $sample_range
done

expt_dir="expts/random2000"
temp=0.5
for model_name in poro
do
    python evaluate.py \
        --refs ${expt_dir}/data/refs.json \
        --preds ${expt_dir}/data/prompts_{0,1,5,10}shot_${model_name}_temp${temp}.jsonl\
        --out ${expt_dir}/all_confusions_${model_name}_temp${temp}.png \
        --many-confusions \
        --preds-include-prompt \
        --prompts ${expt_dir}/data/prompts_{0,1,5,10}shot.json
done

expt_dir="expts/random2000"
cotornot=""
for model_name in llama2_70b
do
    python evaluate.py \
        --refs ${expt_dir}/data/refs.json \
        --preds ${expt_dir}/data/prompts_{0,1,5,10}shot${cotornot}_${model_name}.jsonl\
        --out ${expt_dir}/all_confusions${cotornot}_${model_name}.png \
        --many-confusions \
        --refs-range $sample_range
done





expt_dir="expts/random2000"
sample_range="0-2000"
cotornot=""
for n_shot in 10
do
    for model_name in gpt3.5-turbo
    do
        echo ""
        echo "###################################################"
        echo "Evaluating ${n_shot}shot${cotornot} ${model_name} ${sample_range}"
        python evaluate.py \
            --refs ${expt_dir}/data/refs.json \
            --preds ${expt_dir}/data/prompts_${n_shot}shot${cotornot}_${model_name}_${sample_range}.jsonl \
            --refs-range $sample_range \
            --out ${expt_dir}/confusion_matrix_${n_shot}shot${cotornot}_${model_name}_${sample_range}_temp${temp}.png \
            --cot $cotornot \
            --confusion \
            --samples ${expt_dir}/data/samples.json
    done
done

###############################################################################
### other plots
resulttype=Complete
python visualise_results.py \
    --result-files expts/random2000/results_*shot_*_0-2000*.txt \
        expts/random2000/results_*shot_{llama2_70b.,poro}* \
    --resulttype $resulttype \
    --output results_plot_${resulttype}_withrnn_full9.png

resulttype=Complete
python visualise_results.py \
    --result-files expts/random2000/results_*shot_llama2_{70,13}* \
    --resulttype $resulttype \
    --output results_plot_llama_${resulttype}.png


plottype=multiplot
python visualise_results.py \
    --result-files expts/random2000/results_*shot_gpt*-turbo_0-2000_f1-scores.txt \
        expts/random2000/results_*shot_{llama2_70b,poro}*f1-scores.txt \
    --plottype $plottype \
    --output results_multiplot.png
   
plottype=multiplot
python visualise_results.py \
    --result-files expts/random2000/results_*shot_gpt*-turbo_temp0.0_0-2000_accuracy.txt \
        expts/random2000/results_0shot_gpt4-turbo_temp0.0_0-700_accuracy.txt \
        expts/random2000/results_*shot_{llama2_70b,poro_temp0.5}_accuracy.txt \
    --plottype $plottype \
    --output results_multiplot_accuracies_gpt4-turbo0shot700.png
     
    



for resulttype in Case Person Number
do
    python visualise_results.py \
        --result-files expts/random2000/results_*shot_*_0-2000*_f1-scores.txt \
            expts/random2000/results_*shot_{llama2_70b,poro}*_f1-scores* \
        --resulttype $resulttype \
        --output results_plot_${resulttype}_full_f1-scores.png
done
