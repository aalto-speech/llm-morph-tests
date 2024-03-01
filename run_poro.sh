#!/bin/bash
#SBATCH --time=00:25:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=30GB
#SBATCH --partition dgx-spa
#SBATCH -A dgx-spa
#SBATCH --gres=gpu:3
#SBATCH --job-name=poro_inference
#SBATCH --output=log/%x_%j.out

module load gcc/11.3.0
module load intel-oneapi-compilers/2023.1.0
module load cuda/11.8.0

# activate your conda environment
module load miniconda
source activate hf23

# run batch inference
for prompt in "$@"
do
    echo "Running batch inference for $prompt"
    # torchrun 
    python -m torch.distributed.launch \
        batch_inference_poro.py \
        --prompts $prompt \
        --ckpt_dir $MODEL_ROOT \
        --tokenizer_path $TOKENIZER_PATH \
        --max_seq_len 512 --max_batch_size 16 \
        --temperature 0.7 --max_gen_len 50 \
        --output_file ${prompt%.json}_poro.jsonl
done
