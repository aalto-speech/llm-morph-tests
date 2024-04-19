

with open('data/omorfi_noun_lexemes_filtered_inflected.txt.00', 'r', encoding='utf-8') as f:
    lines = [l.split(':')[0].strip() for l in  f.readlines() if l.strip()]

with open('data/omorfi_noun_lexemes_filtered_inflected.txt.00.plain', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
    f.write('\n')
