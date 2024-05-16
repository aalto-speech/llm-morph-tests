'''
The code requires AALTO_OPENAI_API_KEY environment variable to be set

Works with OpenAI v1.1.0 python library

Rewrite the base path with Aalto mappings
For all endpoints see https://www.aalto.fi/en/services/azure-openai#6-available-api-s
'''
import httpx, os
from openai import OpenAI
import argparse
import json
from tqdm import tqdm

argparser = argparse.ArgumentParser()
argparser.add_argument("--prompts", type=str, help="File of prompts to use")
argparser.add_argument("--model", type=str, help="Model to use", default="gpt4-turbo")
argparser.add_argument("--sample-range", type=str, help="Range of samples to use",
        default="0-100")
argparser.add_argument("--out", type=str, help="Output file name")
args = argparser.parse_args()

sample_range = [int(r) for r in args.sample_range.split("-")]

with open(args.prompts, "r", encoding='utf-8') as f:
    prompts = json.load(f)

converted_prompts = []
for prompt in prompts[sample_range[0]:sample_range[1]]:
    converted_prompts.append(
            {
                "role": "user",
                "content": prompt,
                }
            )

def update_base_url(request: httpx.Request) -> None:
    if request.url.path == "/chat/completions":
        if args.model == "gpt4":
            path_suffix = "/v1/chat/gpt4-8k"
        elif args.model == "gpt4-turbo":
            path_suffix = "/v1/openai/gpt4-1106-preview/chat/completions"
        elif args.model == "gpt3.5-turbo":
            path_suffix = "/v1/chat/gpt-35-turbo-1106"
        else:
            raise ValueError(f"Unknown model {args.model}")
        request.url = request.url.copy_with(path=path_suffix)

client = OpenAI(
        base_url="https://aalto-openai-apigw.azure-api.net",
        api_key=False, # API key not used, instead set below
        default_headers = {
            "Ocp-Apim-Subscription-Key": os.environ.get("AALTO_OPENAI_API_KEY"),
        },
        http_client=httpx.Client(
            event_hooks={
                "request": [update_base_url],
                }
            ),
        )

outputs = []
completions = []
# one msg at a time since we don't want the model to remember previous messages
buff = []
for i, msg in enumerate(tqdm(converted_prompts)):
    completion = client.chat.completions.create(
        model="no_effect", # the model variable must be set, but has no effect, URL defines model
        messages=[msg],
        max_tokens=50,
        temperature=1.0,
        top_p=1.0,
        )
    outputs.append(completion.choices[0].message.content)
    completions.append(completion)

    # print(completion)

    buff.append(completion)
    if i % 100 == 0 and i > 0:
        with open(args.out + f".completions.buff.{i}.json", "w", encoding='utf-8') as f:
            json.dump([c.dict() for c in completions], f)
        buff = []

with open(args.out, "w", encoding='utf-8') as f:
    json.dump(outputs, f)

with open(args.out + ".completions.json", "w", encoding='utf-8') as f:
    json.dump([c.dict() for c in completions], f)
