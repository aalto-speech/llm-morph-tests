
with open('omorfi/src/lexemes.tsv', 'r', encoding='utf-8') as f:
    lexemes = [l.strip().split() for l in f.readlines()]

paradigm_freqs = {}
for lexeme in lexemes:
    paradigm = lexeme[2]
    if paradigm in paradigm_freqs:
        paradigm_freqs[paradigm] += 1
    else:
        paradigm_freqs[paradigm] = 1

sorted_paradigms = sorted(paradigm_freqs.items(), key=lambda x: x[1], reverse=True)

print('Paradigm\tFrequency')
for paradigm, freq in sorted_paradigms:
    print(f'{paradigm}\t{freq}')
