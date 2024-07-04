import json

with open('expts/random2000/data/samples.json', 'r', encoding='utf-8') as file:
    samples = json.load(file)

words = [s.split('--')[0] for s in samples]

poro = False
if poro:
    from transformers import AutoTokenizer
    model_path = '/scratch/elec/morphogen/llm-morph-tests/llms/Poro-34B'
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    word_lens = []
    tokenised_lens = []
    for w in words:
        word_lens.append(len(w))
        tokenised_lens.append(len(tokenizer.encode(w)))

    print('Poro-34B')
    print('Avergae word length:', sum(word_lens)/len(word_lens))
    print('Average tokenised length:', sum(tokenised_lens)/len(tokenised_lens))
    print('Average chars per token:', sum(word_lens)/sum(tokenised_lens))

llama = False
if llama:
    from llama.tokenizer import Tokenizer
    tokenizer = Tokenizer(model_path='/scratch/shareddata/dldata/llama-2/tokenizer.model')

    word_lens = []
    tokenised_lens = []
    for w in words:
        word_lens.append(len(w))
        tokenised_lens.append(len(tokenizer.encode(w, bos=False, eos=False)))

    print('Llama2')
    print('Avergae word length:', sum(word_lens)/len(word_lens))
    print('Average tokenised length:', sum(tokenised_lens)/len(tokenised_lens))
    print('Average chars per token:', sum(word_lens)/sum(tokenised_lens))

gpt = True
if gpt:
    import tiktoken
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    word_lens = []
    tokenised_lens = []
    for w in words:
        word_lens.append(len(w))
        tokenised_lens.append(len(enc.encode(w)))
        
    print('GPT-3.5-turbo')
    print('Avergae word length:', sum(word_lens)/len(word_lens))
    print('Average tokenised length:', sum(tokenised_lens)/len(tokenised_lens))
    print('Average chars per token:', sum(word_lens)/sum(tokenised_lens))
    