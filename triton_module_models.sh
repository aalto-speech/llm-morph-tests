#!/bin/bash
#SBATCH --time=00:25:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=30GB
#SBATCH --partition dgx-spa
#SBATCH --gres=gpu:2
#SBATCH --output=log/llama2inference-gpu.%J.out
#SBATCH --error=log/llama2inference-gpu.%J.err
#SBATCH -A dgx-spa

module load gcc/11.3.0
module load intel-oneapi-compilers/2023.1.0
module load cuda/11.8.0

# get the model weights
# module load model-llama2/7b
module load model-llama2/13b
# module load model-llama2/70b

echo $MODEL_ROOT
# Expect output: /scratch/shareddata/dldata/llama-2/llama-2-7b
echo $TOKENIZER_PATH
# Expect output: /scratch/shareddata/dldata/llama-2/tokenizer.model

# activate your conda environment
module load miniconda
source activate llamamodule

path_to_script="/scratch/elec/morphogen/llm-morph-tests/llms/llm-examples/batch-inference-llama2"

prompts=$1

echo "Running batch inference for $prompts"

# run batch inference
torchrun --nproc_per_node 2 \
    ${path_to_script}/batch_inference.py \
    --prompts $prompts \
    --ckpt_dir $MODEL_ROOT \
    --tokenizer_path $TOKENIZER_PATH \
    --max_seq_len 512 --max_batch_size 16
