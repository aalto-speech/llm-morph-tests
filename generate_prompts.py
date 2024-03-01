#!/bin/python3

def fill_template_random_egs(eg_word_forms, eg_word_answers, test_word, test_word_answer):
    
    template = 'Luokittele suomenkieliset sanat seuraaviin morfologisiin kategorioihin:'
    template += '\nA. yksikkö tai monikko,\nB. sijamuoto,\nC. omistusliite.'

    for i in range(len(eg_word_forms)):
        template += f'''\n\nSana: {eg_word_forms[i]}\nLuokittelu: {eg_word_answers[i]}'''

    template += f'''\n\nSana: {test_word}\nLuokittelu: {test_word_answer},'''
    return template


def fill_template_vesi_koivu_egs(test_word):

    template = 'Jäsennä taivutetut substantiivit tällä tavalla:'
    template += '\ntaivutusmuoto -- perusmuoto, yksikkö vai monikko, sijamuoto, omistusliite'

    template += '\n\nvedessään -- vesi, yksikkö, inessiivi, yksikön ensimmäinen persoona'
    template += '\nkoivuihimme -- koivu, monikko, illatiivi, monikon ensimmäinen persoona'
    template += f'\n{test_word}'
    return template


def convert_label(input, mapping):
    with open(mapping, "r", encoding="utf-8") as f:
        try:
            lines = {l.split('-')[0].strip(): l.split('-')[1].strip() for l in f.readlines()}
        except IndexError:
            print("Error: mapping file should have >= two columns separated by -",
                  f.readlines())
            exit(1)

    return lines[input]


def parse_sample(line):
    splitted = line.split()
    omorstring = splitted[0]
    word_form = splitted[1]

    lemma = re.search(r'(?<=WORD_ID=).*?(?=])', omorstring).group()
    number = re.search(r'(?<=NUM=).*?(?=])', omorstring).group()
    gcase = re.search(r'(?<=CASE=).*?(?=])', omorstring).group()
    possessive = re.search(r'(?<=POSS=).*?(?=])', omorstring).group()

    conv_number = convert_label(number, 'data/grammar/finnish-numbers.txt')
    conv_gcase = convert_label(gcase, 'data/grammar/finnish-cases.txt')
    conv_possessive = convert_label(possessive, 'data/grammar/finnish-persons.txt')

    return {'word': word_form, 'lemma': lemma, 'number': conv_number,
            'case': conv_gcase, 'poss': conv_possessive}


def make_word2refs(inflected_file):
    """ Create dict of word forms to their references. The inflected file contains
    rows with omorstring as first column and inflected form in second column."""

    word2refs_dict = {}
    with open(inflected_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        parsed = parse_sample(line)
        w_and_l = f"{parsed['word']} -- {parsed['lemma']}"
        if w_and_l not in word2refs_dict:
            word2refs_dict[w_and_l] = []
        word2refs_dict[w_and_l].append(
            f"{parsed['number']}, {parsed['case']}, {parsed['poss']}")

    # for word, feats in word2refs_dict.items():
    #     # all lemmas should be same for one word
    #     if len(set([ref.split(',')[0].strip() for ref in word2refs_dict[word]])) != 1:
    #         print(f"Error: multiple lemmas for word {word}:", word2refs_dict[word])
    #         exit(1)

    return word2refs_dict



if __name__ == "__main__":
    import re
    import random
    import argparse
    import pickle as pkl
    from os import path, mkdir
    import json

    args = argparse.ArgumentParser()
    args.add_argument("--input", type=str, help="File of omorstring + inflected form pairs")
    args.add_argument("--n_shot", type=str, help="Number of examples in the prompt")
    args.add_argument("--n_samples", type=int, help="Number of samples to generate")
    args.add_argument("--template_file", type=str, help="Path to template file")
    args.add_argument("--output_dir", type=str, help="Output dir name")
    args.add_argument("--batch_size", type=int, default=16, help="Batch size for writing to file")
    args = args.parse_args()

    # if path.isfile(args.input + '.pkl'):
    #     with open(args.input + '.pkl', "rb") as f:
    #         word2refs = pkl.load(f)
    # else:
    word2refs = make_word2refs(args.input)
    with open(args.input + '.pkl', "wb") as f:
        pkl.dump(word2refs, f)

    # get random n_samples from input
    samples = random.sample(sorted(word2refs), args.n_samples)

    prompts = []
    refs = []
    for sample in samples:
        prompts.append(fill_template_vesi_koivu_egs(sample))
        refs.append('\n'.join(word2refs[sample]))

    if not path.isdir(args.output_dir):
        print(f"Creating directory {args.output_dir}")
        mkdir(args.output_dir)
    # write to files in batches
    for i in range(0, len(prompts), args.batch_size):
        batch_prompts = prompts[i:i+args.batch_size]
        batch_refs = refs[i:i+args.batch_size]
        with open(f"{args.output_dir}/inputs_{i}.json", "w", encoding="utf-8") as fsample, \
                open(f"{args.output_dir}/refs_{i}.json", "w", encoding="utf-8") as fref:
            fsample.write(json.dumps(batch_prompts))
            fref.write(json.dumps(batch_refs))
    print(f"Generated {len(prompts)} prompts and references")
    print(f"Saved to {args.output_dir}")
