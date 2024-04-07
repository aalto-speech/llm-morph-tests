# Per-API call cost can be calculated as follows (GPT-4 8k context), using pseudocode (prices as of 21.6.2023):

# cost_gpt4_8k = usage.completion_tokens / 1000 * 0.057 + usage.prompt_tokens / 1000 * 0.029

import argparse

def calculate_cost(usage, model):
    if model == "gpt4":
        cost = ((usage.completion_tokens / 1000) * 0.057) + ((usage.prompt_tokens / 1000) * 0.029)
    elif model == "gpt4-turbo":
        cost = ((usage.completion_tokens / 1000) * 0.03) + ((usage.prompt_tokens / 1000) * 0.01)
    else:
        raise ValueError(f"Unknown model {model}")
    return cost

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--completion-tokens", type=int, help="Number of completion tokens used")
    parser.add_argument("--prompt-tokens", type=int, help="Number of prompt tokens used")
    parser.add_argument("--model", type=str, help="Model used")
    args = parser.parse_args()
    usage = argparse.Namespace(completion_tokens=args.completion_tokens, prompt_tokens=args.prompt_tokens)
    print(calculate_cost(usage, args.model))
