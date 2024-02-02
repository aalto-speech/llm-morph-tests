"""
This script takes a file with omorfi formatted strings and converts them to
llm prompt format. The input file should have one inflected word per line, e.g.:
[WORD_ID=auto][UPOS=NOUN][NUM=SG][CASE=GEN][POSS=SG1]	autoni
[WORD_ID=auto][UPOS=NOUN][NUM=SG][CASE=GEN][POSS=SG2]	autosi

The output file will have one inflected word per line, and its analysis, e.g.:
autoni: auto, noun, singular, genitive, first person singular
"""

import argparse
import re
import sys

mappings = {
    'NOUN': 'noun',
    'VERB': 'verb',
    'ADJ': 'adjective',
    'ADV': 'adverb',
    'PRON': 'pronoun',
    'ADP': 'adposition',
    'AUX': 'auxiliary',
    'CONJ': 'conjunction',
    'DET': 'determiner',
    'INTJ': 'interjection',
    'NUM': 'numeral',
    'PART': 'particle',
    'PROPN': 'proper noun',
    'PUNCT': 'punctuation',
    'SCONJ': 'subordinating conjunction',
    'SYM': 'symbol',
    'X': 'other',
    'UNK': 'unknown',
    'SG': 'singular',
    'PL': 'plural',
    'SG1': 'first person singular',
    'SG2': 'second person singular',
    'SG3': 'third person singular',
    'PL1': 'first person plural',
    'PL2': 'second person plural',
    'PL3': 'third person plural',
    'NOM': 'nominative',
    'GEN': 'genitive',
    'PAR': 'partitive',
    'INE': 'inessive',
    'ELA': 'elative',
    'ILL': 'illative',
    'ADE': 'adessive',
    'ABL': 'ablative',
    'ALL': 'allative',
    'ESS': 'essive',
    'TRA': 'translative',
    'ABE': 'abessive',
    'COM': 'comitative',
    '1': 'first person',
    '2': 'second person',
    '3': 'third person',
    'PRES': 'present tense',
    'PAST': 'past tense',
    'COND': 'conditional',
    'POT': 'potential',
    'IMP': 'imperative',
    'IND': 'indicative',
    'INF': 'infinitive',
    'PART': 'participle',
    'CONN': 'connegative',
    'COMP': 'comparative',
    'SUPER': 'superlative',
    'A': 'active',
    'P': 'passive',
    'POS': 'positive',
    'COMP': 'comparative',
    'SUPER': 'superlative',
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='input file')
    parser.add_argument('output_file', help='output file')
    args = parser.parse_args()

    with open(args.input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(args.output_file, 'w', encoding='utf-8') as f:
        for line in lines:
            analysis, word = line.split('\t')
            analysis = analysis.strip()
            word = word.strip()
            analysis = analysis.split('][')
            analysis = analysis[1:]
            analysis = [a.strip('[]') for a in analysis]
            analysis = [a.split('=') for a in analysis]
            analysis = [mappings[a[1]] for a in analysis]
            analysis = ', '.join(analysis)
            f.write(f'{word}: {analysis}\n')

if __name__ == '__main__':
    main()
