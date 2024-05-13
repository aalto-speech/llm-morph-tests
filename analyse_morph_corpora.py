
morphynet_file = 'data/corpora/morphological/MorphyNet/fin/fin.inflectional.v1.tsv'

morphynet = []
with open(morphynet_file, 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip().split('\t')
        if len(line):
            morphynet.append(
                {
                    'lemma': line[0],
                    'inflection': line[1],
                    'tags': line[2],
                    'segmentation': line[3],
                }
            )

unimorph_file = 'data/corpora/morphological/unimorph/fin/fin.1'

unimorph = []
with open(unimorph_file, 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip().split('\t')
        if len(line):
            unimorph.append(
                {
                    'lemma': line[0],
                    'inflection': line[1],
                    'tags': line[2],
                }
           )

from collections import Counter

print(len(morphynet))

tags_freqs = Counter()
tags_freqs.update([morph['tags'] for morph in morphynet])

for tag, freq in tags_freqs.items():
    if tag.startswith('N'):
        print(tag, freq)

# same for unimorph
print()
print('uniomporg', len(unimorph))

tags_freqs = Counter()
tags_freqs.update([morph['tags'] for morph in unimorph])

for tag, freq in tags_freqs.items():
    if tag.startswith('N'):
        print(tag, freq)
