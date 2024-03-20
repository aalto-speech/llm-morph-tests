#!/bin/python3
import re
import random
import argparse
import pickle as pkl
from os import path, makedirs
import json
from tqdm import tqdm

def fill_template_random_egs(eg_word_forms, eg_word_answers, test_word, test_word_answer):
    template = 'Luokittele suomenkieliset sanat seuraaviin morfologisiin kategorioihin:'
    template += '\nA. yksikkö tai monikko,\nB. sijamuoto,\nC. omistusliite.'

    for i in range(len(eg_word_forms)):
        template += f'\n\nSana: {eg_word_forms[i]}\nLuokittelu: {eg_word_answers[i]}'

    template += f'''\n\nSana: {test_word}\nLuokittelu: {test_word_answer},'''
    return template


def fill_noun_template(test_word, n_shot=5):

    template = 'Jäsennä taivutetut substantiivit tällä tavalla:'
    template += '\ntaivutusmuoto -- perusmuoto, luku, sijamuoto, omistusliite\n'

    if n_shot >= 1:
        template += '\nvedessämme -- vesi, yksikkö, inessiivi, monikon ensimmäinen persoona'
    if n_shot >= 2:
        template += '\nrehtiyksiesi -- rehtiys, monikko, genetiivi, yksikön toinen persoona'
    if n_shot >= 3:
        template += '\npeukaloistanne -- peukalo, yksikkö, elatiivi, monikon toinen persoona'
    if n_shot >= 4:
        template += '\nkoivuumme -- koivu, yksikkö, illatiivi, monikon ensimmäinen persoona'
    if n_shot >= 5:
        template += '\nsängiltään -- sänki, monikko, ablatiivi, yksikön kolmas persoona'
    if n_shot == 10:
        template += '\nhuurteenani -- huurre, yksikkö, essiivi, yksikön ensimmäinen persoona'
        template += '\nkaistojaan -- kaista, monikko, partitiivi, monikon kolmas persoona'
        template += '\nkinoksiksensa -- kinos, monikko, translatiivi, yksikön kolmas persoona'
        template += '\nlaaksoillani -- laakso, monikko, adessiivi, yksikön ensimmäinen persoona'
        template += '\ntalollenne -- talo, yksikkö, allatiivi, monikon toinen persoona'

    template += f'\n{test_word}'

    return template


def convert_label(input_form, mapping):
    with open(mapping, "r", encoding="utf-8") as f:
        try:
            lines = {l.split('-')[0].strip(): l.split('-')[1].strip() for l in f.readlines()}
        except IndexError:
            print("Error: mapping file should have >= two columns separated by -",
                  f.readlines())
            exit(1)

    return lines[input_form]


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
            'case': conv_gcase, 'poss': conv_possessive, 'omorstring': omorstring}


def make_word2refs(inflected_file):
    """ Create dict of word forms to their references. The inflected file contains
    rows with omorstring as first column and inflected form in second column."""

    with open(inflected_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    wordlemma2refs_dict = {}
    for line in tqdm(lines, desc="Parsing omorstrings"):
        parsed = parse_sample(line)

        w_and_l = f"{parsed['word']} -- {parsed['lemma']}"
        if w_and_l not in wordlemma2refs_dict:
            wordlemma2refs_dict[w_and_l] = []
        wordlemma2refs_dict[w_and_l].append(
            (parsed['omorstring'], f"{parsed['number']}, {parsed['case']}, {parsed['poss']}")
        )

    # for word, feats in word2refs_dict.items():
    #     # all lemmas should be same for one word
    #     if len(set([ref.split(',')[0].strip() for ref in word2refs_dict[word]])) != 1:
    #         print(f"Error: multiple lemmas for word {word}:", word2refs_dict[word])
    #         exit(1)

    return wordlemma2refs_dict



if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument("--inflected", type=str, help="File of omorstring + inflected form pairs")
    args.add_argument("--samples", type=str, help="File of pre-selected samples to use")
    args.add_argument("--n_shot", type=int, help="Number of examples in the prompt")
    args.add_argument("--n_samples", type=int, help="Number of samples to generate")
    args.add_argument("--batch_size", type=int, default=16, help="Batch size for writing to file")
    args.add_argument("--word_class", type=str, help="Word class of the inflected words")
    args.add_argument("--output_dir", type=str, help="Output dir name")
    args = args.parse_args()

    if not path.isdir(args.output_dir):
        print(f"Creating directory {args.output_dir}")
        makedirs(args.output_dir)


    if not args.samples:
        if path.isfile(args.inflected + '.pkl'):
            with open(args.inflected + '.pkl', "rb") as f:
                word2refs = pkl.load(f)
        else:
            word2refs = make_word2refs(args.inflected)
            with open(args.inflected + '.pkl', "wb") as f:
                pkl.dump(word2refs, f)
                
        # get random n_samples from input
        samples = random.sample(sorted(word2refs), args.n_samples)
        if path.isfile(f"{args.output_dir}/samples.json"):
            print(f"Error: file {args.output_dir}/samples.json already exists")
            exit(1)
        with open(f"{args.output_dir}/samples.json",        "w", encoding="utf-8") as fsamples:
            fsamples.write(json.dumps(samples))
    else:
        with open(args.samples, "r", encoding="utf-8") as f:
            samples = json.load(f)

    prompts = []
    refs = []
    omorstrings = []
    for sample in samples:
        prompts.append(fill_noun_template(sample, args.n_shot))
        
        if args.inflected:
            refs.append('\n'.join([s[1] for s in word2refs[sample]]))
            omorstrings.append('\n'.join([s[0] for s in word2refs[sample]]))


    # write to files in batches
    # for i in range(0, len(prompts), args.batch_size):
    #     batch_prompts = prompts[i:i+args.batch_size]
    #     batch_refs = refs[i:i+args.batch_size]
    #     with open(f"{args.output_dir}/prompts_{args.n_shot}shot_{i}.json", "w", encoding="utf-8") as fsample, \
    #             open(f"{args.output_dir}/refs_{i}.json", "w", encoding="utf-8") as fref:
    #         fsample.write(json.dumps(batch_prompts))
    #         fref.write(json.dumps(batch_refs))

    # check that file doesn't exist
    if path.isfile(f"{args.output_dir}/prompts_{args.n_shot}shot.json"):
        print(f"Error: file {args.output_dir}/prompts_{args.n_shot}shot.json already exists")
        exit(1)
    with open(f"{args.output_dir}/prompts_{args.n_shot}shot.json", "w", encoding="utf-8") as fsample:
        fsample.write(json.dumps(prompts))

    
    
    if args.inflected:
        if path.isfile(f"{args.output_dir}/refs.json"):
            print(f"Error: file {args.output_dir}/refs.json already exists")
            exit(1)
        if path.isfile(f"{args.output_dir}/omorstrings.json"):
            print(f"Error: file {args.output_dir}/omorstrings.json already exists")
            exit(1)
        with open(f"{args.output_dir}/refs.json",           "w", encoding="utf-8") as fref, \
                open(f"{args.output_dir}/omorstrings.json",    "w", encoding="utf-8") as fomorstrings:
            fref.write(json.dumps(refs))
            fomorstrings.write(json.dumps(omorstrings))

    print(f"Generated {len(prompts)} prompts and references")
    print(f"Saved to {args.output_dir}")
