#!/bin/bash
#SBATCH --time=00:25:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=30GB
#SBATCH --partition dgx-spa
#SBATCH -A dgx-spa
#SBATCH --gres=gpu:1
#SBATCH --job-name=llama_inference
#SBATCH --output=log/%x_%j.out

module load gcc/11.3.0
module load intel-oneapi-compilers/2023.1.0
module load cuda/11.8.0

llama_version=$1
prompts=$2

module load model-llama2/$llama_version
echo "Using llama version $llama_version in $MODEL_ROOT"
echo "and tokenizer in $TOKENIZER_PATH"

if [[ "$llama_version" == "7b" ]]; then
    nprocs=1
elif [[ "$llama_version" == "13b" ]]; then
    nprocs=2
elif [[ "$llama_version" == "70b" ]]; then
    nprocs=8
else
    echo "Invalid llama version"
    exit 1
fi

module load miniconda
source activate llamamodule

echo "Running inference for $prompts"
torchrun --nproc_per_node $nprocs \
    llms/llm-examples/batch-inference-llama2/batch_inference.py \
    --prompts $prompts \
    --ckpt_dir $MODEL_ROOT \
    --tokenizer_path $TOKENIZER_PATH \
    --max_seq_len 512 --max_batch_size 16 \
    --temperature 0.5 --max_gen_len 50 \
    --output_file ${prompts%.json}_llama2_${llama_version}.jsonl



# model_name = "meta-llama/Llama-2-70b-chat-hf"
# tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=huggingface_token, cache_dir="cache")
# model = LlamaForCausalLM.from_pretrained(model_name, 
#                                          use_auth_token=huggingface_token, 
#                                          cache_dir="cache",
#                                          torch_dtype=torch.float16,
#                                          device_map="auto")
# model.eval()
# # check model device
# print(model.device)
# print(model.hf_device_map)
# print(model.generation_config)
