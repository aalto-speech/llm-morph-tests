#!/bin/bash
#SBATCH --time=00:25:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=30GB
#SBATCH --partition dgx-spa
#SBATCH --gres=gpu:2
#SBATCH --job-name=llama_inference
#SBATCH --output=log/%x_%j.out

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

# run batch inference
for prompt in "$@"
do
    echo "Running batch inference for $prompt"
    torchrun --nproc_per_node 2 \
        ${path_to_script}/batch_inference.py \
        --prompts $prompt \
        --ckpt_dir $MODEL_ROOT \
        --tokenizer_path $TOKENIZER_PATH \
        --max_seq_len 512 --max_batch_size 16 \
        --temperature 0.3 --max_gen_len 50 \
        --output_file ${prompt%.json}_llama2.jsonl
done


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
