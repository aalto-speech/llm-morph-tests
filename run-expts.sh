#!/bin/bash

###############################################################################
#### Experiments presented in the CMCL 2024 paper #############################
###############################################################################



###############################################################################
#### Get the inflected forms from the FST

git clone git@github.com:flammie/omorfi.git

cd omorfi
# get noun lexemes from omorfi
# filter punctuation, proper names, acronyms etc.
grep NOUN omorfi/src/lexemes.tsv \
    | grep -v -P ACRO \
    | awk '{print $1}' \
    | grep -P ^[a-zäö]+$ \
    > data/omorfi_noun_lexemes_filtered.txt

# dump the inflected forms of the filtered lexemes from the FST 
# in parallel since there are many
split -d -l 4000 \
    data/omorfi_noun_lexemes_filtered.txt \
    data/omorfi_noun_lexemes_filtered.txt.
screen
filenumber=0
bash generate-wordlist-withtags-nouns.sh \
    data/omorfi_noun_lexemes_filtered.txt.0${filenumber} \
    data/omorfi_noun_lexemes_filtered_inflected.txt.0${filenumber} \
    temp${filenumber}

# combine the results
cat data/omorfi_noun_lexemes_filtered_inflected.txt* \
    > data/omorfi_noun_lexemes_filtered_inflected_all.txt

# filter out those forms that don't include all three features: CASE, NUM, POSS
grep POSS= data/omorfi_noun_lexemes_filtered_inflected_all.txt \
    | grep CASE= | grep NUM= \
    >> data/omorfi_noun_lexemes_filtered_inflected_all_filtered.txt

# combine ambiguous forms so that any of the possible morphological analyses is accepted
python combine_words_with_same_surface_form.py

    
###############################################################################
#### Generate prompts from the real corpus set with frequencies
inflected=data/omorfi_noun_lexemes_filtered_inflected_all_filtered_form2feats_random5k.txt 
expt_dir="expts/random2000"

# create samples.json and 0-shot prompts
word_class="noun"
python generate_prompts.py \
    --inflected $inflected \
    --n_shot 0 \
    --n_samples 2000 \
    --word_class $word_class \
    --output_dir ${expt_dir}/data

# create rest of the n-shot prompts
for n_shot in 1 5 10
do
    python generate_prompts.py \
        --samples ${expt_dir}/data/samples.json \
        --n_shot $n_shot \
        --output_dir ${expt_dir}/data
done

###############################################################################
#### Run LLMs on the test set

#### run Llama2 models
# install llama2 dependencies from git@github.com:meta-llama/llama.git
cd llms
# some useful scripts to run the Llama model
git clone git@github.com:AaltoSciComp/llm-examples.git
cd ..

for n_shot in 0 1 5 10
do
    llama_v="7b"
    sbatch  --time=6:00:00 --partition gpu-v100-32g --gres=gpu:1 \
        slrm-llama.sh \
        $llama_v \
        ${expt_dir}/data/prompts_${n_shot}shot.json

    llama_v="13b"
    sbatch  --time=12:00:00 --partition gpu-v100-32g --gres=gpu:3 \
        slrm-llama.sh \
        $llama_v \
        ${expt_dir}/data/prompts_${n_shot}shot.json

    llama_v="70b"
    sbatch  --time=24:00:00 --partition gpu-v100-32g --gres=gpu:8 \
        slrm-llama.sh \
        $llama_v \
        ${expt_dir}/data/prompts_${n_shot}shot.json

    llama_v="7bc-chat"
    sbatch  --time=6:00:00 --partition gpu-v100-32g --gres=gpu:1 \
        slrm-llama.sh \
        $llama_v \
        ${expt_dir}/data/prompts_${n_shot}shot.json

    llama_v="13b-chat"
    sbatch  --time=12:00:00 --partition gpu-v100-32g --gres=gpu:3 \
        slrm-llama.sh \
        $llama_v \
        ${expt_dir}/data/prompts_${n_shot}shot.json

    llama_v="70b-chat"
    sbatch  --time=24:00:00 --partition gpu-v100-32g --gres=gpu:8 \
        slrm-llama.sh \
        $llama_v \
        ${expt_dir}/data/prompts_${n_shot}shot.json
done

#### run Poro-34B
# download Poro-34B model
cd llms
git clone https://huggingface.co/LumiOpen/Poro-34B
cd ..
# set 'model' path to downloaded model
model='/scratch/elec/morphogen/llm-morph-tests/llms/Poro-34B'
cotornot=""
temp=0.5

for n_shot in 0 1 5 10
do
    sbatch --time=12:00:00 --partition gpu-v100-32g \
        slrm-transformers.sh \
        $model \
        ${expt_dir}/data/prompts_${n_shot}shot${cotornot}.json \
        $temp \
        poro
done

#### run GPT models
# remember to set max tokens to 800 if running CoT
cotornot=""
sample_range="0-2000"
temp=0.0
for n_shot in 0 1 5 10
do
    for model_name in gpt4-turbo gpt3.5-turbo
    do
        python inference_gpt.py \
            --prompts ${expt_dir}/data/prompts_${n_shot}shot${cotornot}.json \
            --model $model_name \
            --sample-range $sample_range \
            --temperature $temp \
            --out ${expt_dir}/llm_outputs/${n_shot}shot${cotornot}_${model_name}_temp${temp}_${sample_range}.jsonl
    done
done

###############################################################################
#### evaluate LLMs

eval_type="accuracy"

# evaluate Llama2
for model_name in llama2_7b llama2_13b llama2_70b llama2_7b-chat llama2_13b-chat llama2_70b-chat
do
    for n_shot in 0 1 5 10
    do
        python evaluate.py \
            --refs ${expt_dir}/data/refs.json \
            --preds ${expt_dir}/llm_outputs/${n_shot}shot_${model_name}_temp0.0.jsonl \
            --out ${expt_dir}/results/results_${n_shot}shot_${model_name}_temp0.0_${eval_type}.txt \
            --eval-type $eval_type
    done
done

# evaluate poro
model_name="poro"
temp=0.5
for n_shot in 0 1 5 10
do
    python evaluate.py \
        --refs ${expt_dir}/data/refs.json \
        --preds ${expt_dir}/llm_outputs/${n_shot}shot_${model_name}_temp${temp}.jsonl \
        --preds-include-prompt \
        --prompts ${expt_dir}/data/prompts_${n_shot}shot.json \
        --out ${expt_dir}/results/results_${n_shot}shot_${model_name}_temp${temp}_${eval_type}.txt \
        --eval-type $eval_type
done

# evaluate GPT models
sample_range="0-2000"
cotornot=""
temp=0.0
for n_shot in 0 1 5 10
do
    for model_name in gpt4-turbo gpt3.5-turbo
    do
        echo ""
        echo "###################################################"
        echo "Evaluating ${n_shot}shot${cotornot} ${model_name} ${sample_range}"
        python evaluate.py \
            --refs ${expt_dir}/data/refs.json \
            --preds ${expt_dir}/llm_outputs/${n_shot}shot${cotornot}_${model_name}_temp${temp}_${sample_range}.jsonl \
            --refs-range $sample_range \
            --out ${expt_dir}/results/results_${n_shot}shot${cotornot}_${model_name}_temp${temp}_${sample_range}_${eval_type}.txt \
            --cot $cotornot \
            --samples ${expt_dir}/data/samples.json \
            --eval-type $eval_type
    done
done


###############################################################################
#### RNNs

# data pre-processing
raw_data="data/omorfi_noun_lexemes_filtered_inflected_all.txt"

# 80% of subset_size is used for training, 10% for validation and 10% for testing
# (RNNs are also tested on same random2000 set that is used with LLMs)
for subset_size in 1000 5000 10000 50000 100000
do
    random_subset="data/omorfi_noun_lexemes_filtered_inflected_random${subset_size}.txt"

    # take a random subset of subset_size samples
    shuf -n $subset_size $raw_data > $random_subset
    datadir="data/fairseq/random${subset_size}"

    for clstype in  "person" "number" "case"
    do
        python preprocess.py \
            --inflected-words $random_subset \
            --output-dir $datadir \
            --classtype $clstype

        fairseq-preprocess \
            --trainpref $datadir/train \
            --validpref $datadir/valid \
            --testpref $datadir/test \
            --source-lang input \
            --target-lang $clstype \
            --destdir $datadir/bin-${clstype} \
            --dataset-impl raw

        sbatch slrm-train-fairseq.sh \
            $datadir/bin-$clstype \
            $clstype \
            checkpoints/random${subset_size}/$clstype

        python eval_classifier.py \
            $datadir/bin-$clstype \
            --test-set $datadir/test \
            --target-lang $clstype \
            --path checkpoints/random${subset_size}/$clstype/checkpoint_best.pt \
            >> rnn-results/results_random${subset_size}_${clstype}.txt
    done
done

##### other test data set
datadir=data/fairseq/random2000
test_set_datadir="expts/random2000/data"

for subset_size in 1000
do
    for clstype in  "person" "number" "case"
    do
        python preprocess.py \
            --wordforms-json ${test_set_datadir}/samples.json \
            --omorstrings-json ${test_set_datadir}/omorstrings.json \
            --output-dir $datadir \
            --train-valid-test-split "0-0-100" \
            --classtype $clstype

        orig_datadir="data/fairseq/random${subset_size}"

        python eval_classifier.py \
            $orig_datadir/bin-$clstype \
            --target-lang $clstype \
            --path checkpoints/random${subset_size}/$clstype/checkpoint_best.pt \
            --test-set $datadir/test \
            > rnn-results/results_random${subset_size}_${clstype}_random2000_new.txt
    done
done



###############################################################################
### Draw figures

### Accuracies plotted as a function of number of shots (Figure 1 in the CMCL 2024 paper)
plottype=multiplot
python visualise_results.py \
    --result-files ${expt_dir}/results/results_*shot_gpt*-turbo_temp0.0_0-2000_accuracy.txt \
        ${expt_dir}/results/results_*shot_{llama2_70b,poro_temp0.5}_accuracy.txt \
    --plottype $plottype \
    --output ${expt_dir}/figures/results_${plottype}_all_accuracies.png


#### Confusion matrices (Figures in Appendix B in the CMCL 2024 paper)
temp=0.0
sample_range="0-2000"
cotornot=""
for model_name in gpt3.5-turbo gpt4-turbo
do
    python evaluate.py \
        --refs ${expt_dir}/data/refs.json \
        --preds ${expt_dir}/llm_outputs/{0,1,5,10}shot${cotornot}_${model_name}_temp${temp}_${sample_range}.jsonl \
        --out ${expt_dir}/figures/all_confusions${cotornot}_${model_name}_${sample_range}_temp${temp} \
        --eval-type many-confusions \
        --refs-range $sample_range
done

temp=0.5
for model_name in poro
do
    python evaluate.py \
        --refs ${expt_dir}/data/refs.json \
        --preds ${expt_dir}/llm_outputs/{0,1,5,10}shot_${model_name}_temp${temp}.jsonl \
        --out ${expt_dir}/figures/all_confusions_${model_name}_temp${temp} \
        --eval-type many-confusions \
        --preds-include-prompt \
        --prompts ${expt_dir}/data/prompts_{0,1,5,10}shot.json
done

for model_name in llama2_70b
do
    python evaluate.py \
        --refs ${expt_dir}/data/refs.json \
        --preds ${expt_dir}/llm_outputs/{0,1,5,10}shot_${model_name}.jsonl\
        --out ${expt_dir}/figures/all_confusions_${model_name} \
        --eval-type many-confusions
done

#### Two confusion matrices for GPT-4: 0-shot and 10-shot (Figures 2 and 3 in the CMCL 2024 paper)
temp=0.0
sample_range="0-2000"
cotornot=""
for category in person case
do
    for model_name in gpt4-turbo
    do
        python evaluate.py \
            --refs ${expt_dir}/data/refs.json \
            --preds ${expt_dir}/llm_outputs/{0,10}shot${cotornot}_${model_name}_temp${temp}_${sample_range}.jsonl \
            --out ${expt_dir}/figures/2confusion_matrices_${category}${cotornot}_${model_name}_${sample_range} \
            --eval-type two-${category}-confusion \
            --refs-range $sample_range
    done
done

