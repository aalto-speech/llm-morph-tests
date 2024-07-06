#!/bin/bash
#SBATCH --time=00:25:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=30GB
#SBATCH --gres=gpu:3
#SBATCH --job-name=llm_inference
#SBATCH --output=log/%x_%j.out

# module load gcc/11.3.0
# module load intel-oneapi-compilers/2023.1.0
# module load cuda/11.8.0
# module load miniconda

# module load gcc/11.4.0
# module load scibuilder-spack-dev/2024-01
# module load cuda/12.2.1
# module load scicomp-python-env

# source activate hf23

model_path=$1
prompts=$2
temp=$3
model_name=$4

# run inference
echo "Running inference for $prompts"

if [ -z "$temp" ]; then
    temp=0.7
fi
echo "Temperature: $temp"

# python -m torch.distributed.launch

(set -x; torchrun \
    inference_transformers.py \
    --prompts $prompts \
    --model_path $model_path \
    --max_seq_len 512 --max_batch_size 16 \
    --temperature $temp --max_gen_len 512 \
    --output_file ${prompts%.json}_${model_name}_temp${temp}.jsonl)
