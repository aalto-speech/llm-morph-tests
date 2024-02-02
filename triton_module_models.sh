#!/bin/bash
#SBATCH --time=00:25:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=30GB
#SBATCH -A dgx-spa
#SBATCH --partition dgx-spa
#SBATCH --gres=gpu:8
#SBATCH --output=llama2inference-gpu.%J.out
#SBATCH --error=llama2inference-gpu.%J.err

module load gcc/11.3.0
module load intel-oneapi-compilers/2023.1.0
module load cuda/11.8.0

# get the model weights
# module load model-llama2/7b
# module load model-llama2/13b
module load model-llama2/70b

echo $MODEL_ROOT
# Expect output: /scratch/shareddata/dldata/llama-2/llama-2-7b
echo $TOKENIZER_PATH
# Expect output: /scratch/shareddata/dldata/llama-2/tokenizer.model

# activate your conda environment
module load miniconda
source activate llamamodule

path_to_scripts="/scratch/elec/morphogen/morphological-llm-test-set/llm-examples/batch-inference-llama2"

# run batch inference
torchrun --nproc_per_node 8 \
    ${path_to_scripts}/batch_inference.py \
    --prompts ${path_to_scripts}/prompts_morph.json \
    --ckpt_dir $MODEL_ROOT \
    --tokenizer_path $TOKENIZER_PATH \
    --max_seq_len 512 --max_batch_size 16
