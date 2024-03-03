from typing import Optional,Union,List
import fire
import torch
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
import sys
import os

MODEL_NAME = '/scratch/elec/morphogen/llm-morph-tests/llms/Poro-34B'
# MODEL_NAME = 'TurkuNLP/gpt3-finnish-small'

def main(
        prompts: Union[str, List[str],],
        ckpt_dir: str,
        tokenizer_path: str,
        temperature: float = 0.6,
        top_p: float = 0.9,
        max_seq_len: int = 512,
        max_batch_size: int = 8,
        model_parallel_size: Optional[int] = None,
        seed: int = 1,
        max_gen_len: Optional[int] = None,
        output_file: Optional[str] = None,
    ):
    try:
        with open(prompts, 'r', encoding='utf-8') as file:
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
    torch.manual_seed(seed)
    if local_rank > 0:
        sys.stdout = open(os.devnull, "w")

    torch.manual_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    torch.set_default_tensor_type(torch.cuda.HalfTensor)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map="balanced",)
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
            temperature=temperature,
            max_new_tokens=max_gen_len,
            # no_repeat_ngram_size=2,
        )
        outputs.append(str(tokenizer.decode(output[0], skip_special_tokens=True)))

        write_buffer.append(outputs[-1])
        if len(write_buffer) >= 100:
            with open(output_file + f'.{i}.buff', "w", encoding="utf-8") as f:
                json.dump(write_buffer, f, ensure_ascii=False, indent=4)
            write_buffer = []
            i += 1

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(outputs, f, ensure_ascii=False, indent=4)
    else:
        print(outputs)


if __name__ == "__main__":
    fire.Fire(main)
