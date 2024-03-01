from transformers import AutoTokenizer, AutoModelForCausalLM

# MODEL_NAME = '/scratch/elec/t405-puhe/p/gpt3-finnish/gpt3-finnish-8B'
# MODEL_NAME = '/scratch/elec/morphogen/gpt3-finnish-13B'
MODEL_NAME = '/scratch/elec/morphogen/llms/Poro-34B'

print(f'Loading model {MODEL_NAME}...')

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

def generate(prompt, temperature=0.7, max_new_tokens=50):
    input = tokenizer(prompt, return_tensors='pt')
    output = model.generate(
        **input,
        do_sample=True,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        no_repeat_ngram_size=2,
    )
    return tokenizer.decode(output[0], skip_special_tokens=True)


with open('one_shot_prompt_finnish.txt', 'r', encoding='utf-8') as f:
    prompt = f.read()

print('The prompt is:')
print(prompt)
print('\n----------------------------\n')

print('The generated text is:')
print(generate(prompt))
