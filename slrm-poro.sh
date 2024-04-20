#!/bin/bash
#SBATCH --time=00:25:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=30GB
#SBATCH --gres=gpu:3
#SBATCH --job-name=poro_inference
#SBATCH --output=log/%x_%j.out

module load gcc/11.3.0
module load intel-oneapi-compilers/2023.1.0
module load cuda/11.8.0

# activate your conda environment
module load miniconda
source activate hf23

model_path=$1
prompts=$2
temp=$3

# run inference
echo "Running inference for $prompts"

if [ -z "$temp" ]; then
    temp=0.7
fi
echo "Temperature: $temp"

# torchrun
# python -m torch.distributed.launch \

(set -x; torchrun \
    batch_inference_poro.py \
    --prompts $prompts \
    --model_path $model_path \
    --max_seq_len 512 --max_batch_size 16 \
    --temperature $temp --max_gen_len 50 \
    --output_file ${prompts%.json}_poro_temp${temp}.jsonl)
