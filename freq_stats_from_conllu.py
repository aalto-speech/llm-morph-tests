from conllu import parse_incr
from tqdm import tqdm
import gzip
import argparse
from collections import Counter

with open('data/ignored_tags.txt', 'r', encoding='utf-8') as f:
    ignored_tags = [l.strip() for l in f.read().split('\n') if l.strip()]

def check_filetype_read(filename):
    if filename.endswith('.gz'):
        return gzip.open, 'rt'
    return open, 'r'


def read_conllu_file(filename):
    """Read a file in the conllu format and yield the tokenlists."""
    open_func, read_mode = check_filetype_read(filename)
    with open_func(filename, read_mode, encoding='utf-8') as f:
        for tokenlist in tqdm(parse_incr(f)):
            yield tokenlist

# def filter_token_morph(token, lemma, noisy_pos_tags, noisy_tags, separator=';'):
#     if noisy_pos_tags and token['upos'] in noisy_pos_tags:
#         return None
#     if not token['feats']:
#         return None
#     if noisy_tags and any(morph_type in noisy_tags for morph_type in token['feats'].keys()):
#         return None
#     # filter out other rubbish also? semicolon is used as a separator
#     if separator in token['form']:
#         return None
#     return lemma

def parse_feats(token) -> str:
    """Parse morphological features from token."""
    feats_list = []
    if not token['feats']:
        return ''
    for morph_type, morph_class in token['feats'].items():
        morph_tag = f'{morph_type}={morph_class}'
        if ignored_tags:
            if any(morph_tag.startswith(ignored_tag) for ignored_tag in ignored_tags):
                continue
        # elif included_tags:
        #     if not any(morph_tag.startswith(included_tag) for included_tag in included_tags):
        #         continue
        feats_list.append(morph_tag)
    return '+'.join(feats_list)

def parse_lemmas(token):
    return token['lemma']


def token_iter_conllu(filename, parser_func):
    """Iterate over the lemmas in the conllu file."""
    for tokenlist in read_conllu_file(filename):
        for token in tokenlist:
            yield parser_func(token)


def freq_stats_from_conllu(filename, token_feat):
    """Return the frequency stats of the lemmas in the conllu file."""
    freq_stats = {}

    for token in token_iter_conllu(filename, parser_func):
        if token in freq_stats:
            freq_stats[token] += 1
        else:
            freq_stats[token] = 1
    return freq_stats


def write_all_lemmas(filename, counter):
    with open(filename, 'w', encoding='utf-8') as f:
        for lemma, freq in counter:
            f.write(f'{lemma} {freq}\n')


def main():
    args = argparse.ArgumentParser()
    args.add_argument('input_file', help='The conllu file to read.')
    args.add_argument('token_feat', help='The feature to use for the token.')
    # args.add_argument('min_len', type=int, help='The minimum length of the token.')
    args.add_argument('output_file', help='The file to write the lemmas to.')
    args = args.parse_args()



    if args.token_feat == 'lemma':
        parser_func = parse_lemmas
    else:
        parser_func = parse_feats

    # freq_stats = freq_stats_from_conllu(args.input_file, args.token_feat) #, args.min_len)
    write_all_lemmas(args.output_file, Counter(token_iter_conllu(args.input_file, parser_func,
                                    #  args.min_lemma_len
                                     ),
                                ).most_common())
    
    # print(ignored_tags)
    # for tokenlist in read_conllu_file(args.input_file):
    #     for token in tokenlist:
    #         print(token)
    #         print(token['feats'])
    #         print(parser_func(token))
    #         exit()

if __name__ == '__main__':
    main()
