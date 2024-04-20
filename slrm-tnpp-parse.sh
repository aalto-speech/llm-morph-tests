#!/bin/bash
#SBATCH --time=1-00
#SBATCH --mem=10G
#SBATCH --gres=gpu:1
#SBATCH --partition dgx-spa,dgx-common,gpu,gpushort
#SBATCH --constraint=volta
#SBATCH --job-name=tnpp
#SBATCH --output=log/%x_%j.out

# module purge
# source /scratch/work/moisioa3/compositional/Turku-neural-parser-pipeline/venv-tnpp-triton/bin/activate

input_file=$1

root_dir="/scratch/work/moisioa3/compositional"
tnpp_dir="/scratch/elec/morphogen/dbca/Turku-neural-parser-pipeline"

# when sentences are short (< 40 words) batch can be at least 8000?

# Finnish
# (set -x; cat "$input_file" | python3 ${tnpp_dir}/tnpp_parse.py \
#     --conf "${tnpp_dir}/models_fi_tdt_dia/pipelines.yaml" \
#     --batch-lines "5000" \
#     parse_sentlines \
#     > ${input_file%.gz}.parsed)

(set -x; cat "$input_file" | python3 ${tnpp_dir}/tnpp_parse.py \
    --conf "${tnpp_dir}/models_fi_tdt_dia/pipelines.yaml" \
    --batch-lines "5000" \
    parse_conllu_nolemmas \
    > ${input_file%.gz}.parsed)

# English
# (set -x; cat "$input_file" | python3 ${tnpp_dir}/tnpp_parse.py \
#     --conf "${tnpp_dir}/models_en_ewt_dia/pipelines.yaml" \
#     --batch-lines "5000" \
#     parse_sentlines \
#     > ${input_file%.gz}.parsed)
