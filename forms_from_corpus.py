from tqdm import tqdm
import json

with open('data/stats/form_freqs_lower_10m.txt', 'r', encoding='utf-8') as f:
    freqs = {}
    for line in tqdm(f):
        splitted = line.split()
        if len(splitted) == 2:
            form, freq = splitted
            freqs[form.strip()] = int(freq.strip())

with open('expts/prelim3000_incorrect_peukalo/data/samples.json', 'r', encoding='utf-8') as f:
    samples = json.load(f)

with_freqs = {}
for sample in tqdm(samples):
    if sample.split('--')[0].strip() in freqs:
        with_freqs[sample] = freqs[sample.split('--')[0].strip()]
    else:
        with_freqs[sample] = 0

with open('expts/prelim3000_incorrect_peukalo/data/samples_with_freqs_from_corpus.json', 'w', encoding='utf-8') as f:
    json.dump(with_freqs, f, indent=4)
