#!/bin/bash

expt=$1
expt_dir="expts/${expt}"
config_file="${expt_dir}/config.sh"

. ${config_file}


# inflect lemmas with omorfi-generate.sh
cd omorfi
bash ../omorfi-inflect/permute-case-number-person.sh \
    ../${expt_dir}/lemmas.txt \
    ../${expt_dir}/cases.txt \
    ../${expt_dir}/numbers.txt \
    ../${expt_dir}/persons.txt \
    ../inflected

cd ..

# generate prompts
for template in $(ls ${expt_dir}/prompts/templates); do
    bash generate_prompts.sh $expt ${template%.sh}
done

# format prompts for llama
python llama_json.py \
    ${expt_dir}/prompts/generated/pt_short_2shot_finnish/*.input \
    ${expt_dir}/prompts/generated/pt_short_2shot_finnish/all_inputs.json
python llama_json.py \
    ${expt_dir}/prompts/generated/pt_short_2shot_finnish/*.ref \
    ${expt_dir}/prompts/generated/pt_short_2shot_finnish/all_refs.json

# run batch inference
sbatch triton_module_models.sh \
    expts/preliminary/prompts/generated/pt_short_2shot_finnish/all_inputs_48.json

# evaluate
python llama_results.py \
    --refs expts/preliminary/prompts/generated/pt_short_2shot_finnish/all_refs_{0,16,32}.json \
    --preds expts/preliminary/prompts/generated/pt_short_2shot_finnish/llama_preds_{0,16,32}.out \
    --out llama-7b-results.txt

python llama_results.py \
    --refs expts/preliminary/prompts/generated/pt_short_2shot_finnish/all_refs_{0,16,32}.json \
    --preds expts/preliminary/prompts/generated/pt_short_2shot_finnish/llama_13b_preds_{0,16,32}.out \
    --out llama-13b-results.txt