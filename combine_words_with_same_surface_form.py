from tqdm import tqdm

form2feats = {}
with open('data/omorfi_noun_lexemes_filtered_inflected_all_filtered.txt', 'r', encoding='utf-8') as f:
    for line in tqdm(f.readlines()):
        line = line.strip()
        splitted = line.split(':')
        if len(splitted) == 2:
            form = splitted[0]
            feats = splitted[1]
        else:
            continue
        if form not in form2feats:
            form2feats[form] = feats
        else:
            form2feats[form] += '|' + feats

with open('data/omorfi_noun_lexemes_filtered_inflected_all_filtered_form2feats.txt', 'w', encoding='utf-8') as f:
    for form, feats in form2feats.items():
        f.write(form + ':' + feats + '\n')
