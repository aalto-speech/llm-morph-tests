from tqdm import tqdm
import json
import pickle as pkl
from collections import Counter

if False:
    # read the freqs of the forms in a corpus
    with open('data/stats/form_freqs_lower_10m.txt', 'r', encoding='utf-8') as f:
        freqs = {}
        for line in tqdm(f):
            splitted = line.split()
            if len(splitted) == 2:
                form, freq = splitted
                freqs[form.strip()] = int(freq.strip())

    # with open('expts/prelim3000_incorrect_peukalo/data/samples.json', 'r', encoding='utf-8') as f:
    #     samples = json.load(f)

    # with_freqs = {}
    # for sample in tqdm(samples):
    #     if sample.split('--')[0].strip() in freqs:
    #         with_freqs[sample] = freqs[sample.split('--')[0].strip()]
    #     else:
    #         with_freqs[sample] = 0

    # with open('expts/prelim3000_incorrect_peukalo/data/samples_with_freqs_from_corpus.json', 'w', encoding='utf-8') as f:
    #     json.dump(with_freqs, f, indent=4)


    ## read the omorfi tags of all forms
    with open('data/omorfi_noun_lexemes_filtered_inflected_all.txt', 'r', encoding='utf-8') as f:
        omorfis = {}
        for line in tqdm(f):
            splitted = line.split(':')
            if len(splitted) == 2:
                form, feats = splitted
                if form.strip() not in omorfis:
                    omorfis[form.strip()] = [feats.strip()]
                else:
                    omorfis[form.strip()].append(feats.strip())

    ## take the intersection of the forms in corpus and in omorfi
    print('intersecting...')
    intersect = set(freqs.keys()) & set(omorfis.keys())
    print('intersected:', len(intersect))

    combined_dict = {}
    for form in intersect:
        combined_dict[form] = {'freq': freqs[form], 'feats': omorfis[form]}


    with open('data/form_freqs_lower_10m_forms_to_freqs_and_feats.pkl', 'wb') as f:
        pkl.dump(combined_dict, f)


####################

# read the dict with freqs and feats per form
with open('data/form_freqs_lower_10m_forms_to_freqs_and_feats.pkl', 'rb') as f:
    combined_dict = pkl.load(f)

print_featsfreqs = False
if print_featsfreqs:
    feats2freq = {}
    for form, featsandfreqs in combined_dict.items():
        feats = ']['.join(featsandfreqs['feats'].split('][')[1:])
        freq = featsandfreqs['freq']
        if feats in feats2freq:
            feats2freq[feats] += freq
        else:
            feats2freq[feats] = freq

    # sort by freq
    feats2freq = {k: v for k, v in sorted(feats2freq.items(), key=lambda item: item[1], reverse=True)}

    for feats, freq in feats2freq.items():
        print(feats, freq)


# filter the forms to have have only those that have freq > 1 and have UPOS=NOUN, NUM=, CASE=, POSS=
filtered = {}
for form, featsandfreqs in combined_dict.items():
    if featsandfreqs['freq'] > 1:
        for feats in featsandfreqs['feats']:
            if all(feat in feats for feat in ['UPOS=NOUN', 'NUM=', 'CASE=', 'POSS=']):
                filtered[form] = featsandfreqs

with open('data/form_freqs_lower_10m_forms_and_freqs_filtered_seplines.txt', 'w', encoding='utf-8') as f:
    for form, featsandfreqs in filtered.items():
        for feats in featsandfreqs['feats']:
            if all(feat in feats for feat in ['UPOS=NOUN', 'NUM=', 'CASE=', 'POSS=']):
                f.write(f"{feats} {form} {featsandfreqs['freq']}\n")
