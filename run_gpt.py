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

argparser = argparse.ArgumentParser()
argparser.add_argument("--prompts", type=str, help="File of prompts to use")
argparser.add_argument("--out", type=str, help="Output file name")
args = argparser.parse_args()

with open(args.prompts, "r", encoding='utf-8') as f:
    prompts = json.load(f)

converted_prompts = []
for prompt in prompts[:10]:
    converted_prompts.append(
            {
                "role": "user",
                "content": prompt,
                }
            )

def update_base_url(request: httpx.Request) -> None:
    if request.url.path == "/chat/completions":
        request.url = request.url.copy_with(path="/v1/chat/gpt4-8k")

client = OpenAI(
        base_url="https://aalto-openai-apigw.azure-api.net",
        api_key=False, # API key not used, and rather set below
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
for msg in converted_prompts:
    print(msg)
    completion = client.chat.completions.create(
        model="no_effect", # the model variable must be set, but has no effect, URL defines model
        # messages=[
        #     {
        #         "role": "user",
        #         "content": prompt,
        #         }
        #     ],
        # messages=converted_prompts,
        messages=[msg],
        )
    outputs.append(completion.choices[0].message["content"])
    completions.append(completion)

with open(args.out, "w", encoding='utf-8') as f:
    json.dump(outputs, f)

with open(args.out + ".completions.json", "w", encoding='utf-8') as f:
    json.dump([c.dict() for c in completions], f)
