import json
import argparse

# conda activate hf23

parser = argparse.ArgumentParser(description='Compare tokenizers')
parser.add_argument('--model', type=str, default='gpt')
parser.add_argument('--input_json', type=str, default='expts/random2000/data/samples.json')
args = parser.parse_args()

with open(args.input_json, 'r', encoding='utf-8') as file:
    samples = json.load(file)

words = [s.split('--')[0] for s in samples]

if args.model == 'poro':
    from transformers import AutoTokenizer
    model_path = '/scratch/elec/morphogen/llm-morph-tests/llms/Poro-34B'
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    word_lens = []
    tokenised_lens = []
    last_token_lens = []
    for w in words:
        word_lens.append(len(w))
        print(w, [tokenizer.convert_ids_to_tokens(t).replace('Ã¤', 'ä').replace('Ã¶', 'ö') for t in tokenizer.encode(w)[:-1]])
        tokenised_lens.append(len(tokenizer.encode(w)[:-1]))
        last_token_lens.append(len(tokenizer.convert_ids_to_tokens(tokenizer.encode(w)[-2:-1])[0].replace('Ã¤', 'ä').replace('Ã¶', 'ö')))

    print('Poro-34B')
    print('Average word length:', sum(word_lens)/len(word_lens))
    print('Average tokenised length:', sum(tokenised_lens)/len(tokenised_lens))
    print('Average chars per token:', sum(word_lens)/sum(tokenised_lens))
    print('Average chars per last token:', sum(last_token_lens)/len(last_token_lens))


elif args.model == 'llama':
    from llama.tokenizer import Tokenizer
    tokenizer = Tokenizer(model_path='/scratch/shareddata/dldata/llama-2/tokenizer.model')

    word_lens = []
    tokenised_lens = []
    last_token_lens = []
    for w in words:
        word_lens.append(len(w))
        print(w, tokenizer.sp_model.encode(w, out_type=str)[:-1])
        tokenised_lens.append(len(tokenizer.encode(w, bos=False, eos=False)))
        last_token_lens.append(len(tokenizer.sp_model.encode(w, out_type=str)[-2]))

    print('Llama2')
    print('Average word length:', sum(word_lens)/len(word_lens))
    print('Average tokenised length:', sum(tokenised_lens)/len(tokenised_lens))
    print('Average chars per token:', sum(word_lens)/sum(tokenised_lens))
    print('Average chars per last token:', sum(last_token_lens)/len(last_token_lens))


elif args.model == 'gpt-3.5-turbo' or args.model == 'gpt-4':
    import tiktoken
    enc = tiktoken.encoding_for_model(args.model)

    word_lens = []
    tokenised_lens = []
    last_token_lens = []
    for w in words:
        word_lens.append(len(w))
        print(w, [t.decode('utf-8') for t in enc.decode_tokens_bytes(enc.encode(w)[:-1])])
        tokenised_lens.append(len(enc.encode(w)))
        last_token_lens.append(len(enc.decode_tokens_bytes(enc.encode(w))[-2].decode('utf-8')))

    print(args.model)
    print('Average word length:', sum(word_lens)/len(word_lens))
    print('Average tokenised length:', sum(tokenised_lens)/len(tokenised_lens))
    print('Average chars per token:', sum(word_lens)/sum(tokenised_lens))
    print('Average chars per last token:', sum(last_token_lens)/len(last_token_lens))
