import json

with open('data/omorfi_noun_lexemes_filtered_inflected_random100000.txt', 'r', encoding='utf-8') as f:
    train_words = set([line.split(':')[0] for line in f.readlines()])


with open('expts/random2000/data/samples.json', 'r', encoding='utf-8') as f:
    testset = json.load(f)

test_words = set([item.split('--')[0].strip() for item in testset])

print('train size:', len(train_words))
print('test size:', len(test_words))

contaminated = test_words.intersection(train_words)
print('contaminated:', contaminated)

