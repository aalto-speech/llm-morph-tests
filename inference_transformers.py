# from typing import Optional,Union,List
# import fire
import sys
import os
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm


if __name__ == "__main__":
    # fire.Fire(main)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompts', type=str, required=True)
    parser.add_argument('--model_path', type=str,
                        default='/scratch/elec/morphogen/llm-morph-tests/llms/Poro-34B')
    parser.add_argument('--temperature', type=float, default=0.6)
    parser.add_argument('--top_p', type=float, default=0.9)
    parser.add_argument('--max_seq_len', type=int, default=512)
    parser.add_argument('--max_batch_size', type=int, default=8)
    parser.add_argument('--model_parallel_size', type=int, default=None)
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--max_gen_len', type=int, default=None)
    parser.add_argument('--output_file', type=str, default=None)
    args = parser.parse_args()

    try:
        with open(args.prompts, 'r', encoding='utf-8') as file:
            prompts = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        pass  # Not a valid JSON file, so move on to other checks

    if not isinstance(prompts, (str, list)):
        raise TypeError("prompts must be a json file, string or a list of strings")
    if isinstance(prompts, list) and not all(isinstance(item, str) for item in prompts):
        raise TypeError("All items in the prompts must be strings")

    print('GPU available:', torch.cuda.is_available())

    if not torch.distributed.is_initialized():
        torch.distributed.init_process_group("nccl")

    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    torch.cuda.set_device(local_rank)
    # seed must be the same in all processes
    torch.manual_seed(args.seed)
    if local_rank > 0:
        sys.stdout = open(os.devnull, "w", encoding="utf-8")

    torch.manual_seed(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    torch.set_default_tensor_type(torch.cuda.HalfTensor)
    model = AutoModelForCausalLM.from_pretrained(args.model_path, device_map="balanced",)
                                                #  torch_dtype=torch.float16)

    model.eval()

    inputs = [tokenizer(prompt, return_tensors='pt') for prompt in prompts]
    outputs = []
    write_buffer = []
    i = 0
    for prompt in tqdm(inputs, desc="Generating"):
        output = model.generate(
            **prompt,
            do_sample=True,
            temperature=args.temperature,
            max_new_tokens=args.max_gen_len,
            # no_repeat_ngram_size=2,
        )
        outputs.append(str(tokenizer.decode(output[0], skip_special_tokens=True)))

        write_buffer.append(outputs[-1])
        if len(write_buffer) >= 100:
            with open(args.output_file + f'.{i}.buff', "w", encoding="utf-8") as f:
                json.dump(write_buffer, f, ensure_ascii=False, indent=4)
            write_buffer = []
            i += 1

    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8") as f:
            json.dump(outputs, f, ensure_ascii=False, indent=4)
    else:
        print(outputs)
