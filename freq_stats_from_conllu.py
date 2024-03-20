from conllu import parse_incr
from tqdm import tqdm
import gzip
import argparse
from collections import Counter
import pickle as pkl

with open('data/stats/filters/ignored_tags.txt', 'r', encoding='utf-8') as f:
    ignored_tags = [l.strip() for l in f.read().split('\n') if l.strip()]

with open('data/stats/filters/noisy_tags.txt', 'r', encoding='utf-8') as f:
    noisy_tags = [l.strip() for l in f.read().split('\n') if l.strip()]

with open('data/lemmas_from_dict.txt', 'r', encoding='utf-8') as f:
    included_lemmas = [l.strip() for l in f.read().split('\n') if l.strip()]


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
        return None
    for morph_type, morph_class in token['feats'].items():
        morph_tag = f'{morph_type}={morph_class}'
        if any(morph_tag.startswith(ignored_tag) for ignored_tag in ignored_tags):
            continue
        if any(morph_tag.startswith(noisy_tag) for noisy_tag in noisy_tags):
            return None
        feats_list.append(morph_tag)
    return token['upos'] + '+' + '+'.join(feats_list)


def parse_lemmas(token):
    if not token['feats']:
        return None
    for morph_type, morph_class in token['feats'].items():
        morph_tag = f'{morph_type}={morph_class}'
        if any(morph_tag.startswith(noisy_tag) for noisy_tag in noisy_tags):
            return None
    if token['lemma'] in included_lemmas:
        return token['lemma']
    return None


def parse_forms(token):
    if not token['feats']:
        return None
    for morph_type, morph_class in token['feats'].items():
        morph_tag = f'{morph_type}={morph_class}'
        if any(morph_tag.startswith(noisy_tag) for noisy_tag in noisy_tags):
            return None
    # if token['lemma'] in included_lemmas:
    return token['form'].lower()
    # return None


def parse_lemma_upos(token):
    if not token['feats']:
        return None
    for morph_type, morph_class in token['feats'].items():
        morph_tag = f'{morph_type}={morph_class}'
        if any(morph_tag.startswith(noisy_tag) for noisy_tag in noisy_tags):
            return None
    return (token['lemma'], token['upos'])


def parse_all(token):
    feats_list = []
    if not token['feats']:
        return None
    for morph_type, morph_class in token['feats'].items():
        morph_tag = f'{morph_type}={morph_class}'
        if any(morph_tag.startswith(ignored_tag) for ignored_tag in ignored_tags):
            continue
        if any(morph_tag.startswith(noisy_tag) for noisy_tag in noisy_tags):
            return None
        feats_list.append(morph_tag)
    return token['form'] + '+' + token['lemma']  + '+' + token['upos'] + '+' + '+'.join(feats_list)


def parse_lemma2feats(token):
    feats_list = []
    if not token['feats']:
        return None
    for morph_type, morph_class in token['feats'].items():
        morph_tag = f'{morph_type}={morph_class}'
        if any(morph_tag.startswith(ignored_tag) for ignored_tag in ignored_tags):
            continue
        if any(morph_tag.startswith(noisy_tag) for noisy_tag in noisy_tags):
            return None
        feats_list.append(morph_tag)
    return (token['lemma'], token['form'].lower() + '+' + token['upos'] + '+' + '+'.join(feats_list))


def token_iter_conllu(filename, parser_func):
    """Iterate over the lemmas in the conllu file."""
    for tokenlist in read_conllu_file(filename):
        for token in tokenlist:
            yield parser_func(token)


def freq_stats_from_conllu(filename, parser_func):
    """Return the frequency stats of the lemmas in the conllu file."""
    freq_stats = {}

    for token in token_iter_conllu(filename, parser_func):
        if token is not None:
            if token in freq_stats:
                freq_stats[token] += 1
            else:
                freq_stats[token] = 1
        print(freq_stats)
    return freq_stats


def write_all_lemmas(filename, counter):
    with open(filename, 'w', encoding='utf-8') as f:
        for lemma, freq in counter:
            f.write(f'{lemma} {freq}\n')


def read_freq_stats(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        freq_stats = {}
        for line in f:
            splitted = line.split()
            if len(splitted) == 2:
                lemma, freq = splitted
                freq_stats[lemma] = int(freq)
    return freq_stats


def shortlist_lemma_freqs(freqs_file):
    freqs = read_freq_stats(freqs_file)
    with open('data/lemmas_from_dict.txt', 'r', encoding='utf-8') as f:
        from_dict = {l.strip() for l in f.read().split('\n') if l.strip()}

    shortlist = list(set(freqs.keys()).intersection(from_dict))
    sorted_shortlist = sorted(shortlist, key=lambda x: freqs[x], reverse=True)

    with open(freqs_file + '.shortlist', 'w', encoding='utf-8') as f:
        for lemma in sorted_shortlist:
            f.write(f'{freqs[lemma]} {lemma}\n')


def main():
    args = argparse.ArgumentParser()
    args.add_argument('input_file', help='The conllu file to read.')
    args.add_argument('token_feat', help='The feature to use for the token.' , default='all')
    args.add_argument('output_file', help='The file to write the lemmas to.')
    args.add_argument('--min_len', type=int, help='The minimum length of the token.')
    args.add_argument('--filter', action='store_true',
                    help='Take intersection of lemmas from dict.')
    args = args.parse_args()

    if args.token_feat == 'lemma2feats':
        parser_func = parse_lemma2feats
        lemma2feats = {}
        for token in token_iter_conllu(args.input_file, parser_func):
            if token is not None:
                if token[0] not in lemma2feats:
                    lemma2feats[token[0]] = []
                lemma2feats[token[0]].append(token[1])
        # lemma2feats_counter = {lemma: Counter(feats) for lemma, feats in lemma2feats.items()}
        lemma2feats_freqs = {lemma: len(feats) for lemma, feats in lemma2feats.items()}
        # with open(args.output_file + '.pkl', 'wb') as pklf:
        #     pkl.dump(lemma2feats_counter, pklf)
        with open(args.output_file + '.freqs.pkl', 'wb') as pklf:
            pkl.dump(lemma2feats_freqs, pklf)
    else:
        if args.token_feat == 'lemma':
            parser_func = parse_lemma_upos
        elif args.token_feat == 'feats':
            parser_func = parse_feats
        elif args.token_feat == 'all':
            parser_func = parse_all
        elif args.token_feat == 'wordform':
            parser_func = parse_forms
        else:
            raise ValueError(f'Unknown token feature: {args.token_feat}')

        # freq_stats = freq_stats_from_conllu(args.input_file, args.token_feat) #, args.min_len)
        write_all_lemmas(args.output_file, Counter(token_iter_conllu(args.input_file, parser_func,
                                        #  args.min_lemma_len
                                        ),
                                    ).most_common())

        # classes = {'NOUN': [], 'VERB': [], 'ADJ': []}
        # for item in token_iter_conllu(args.input_file, parse_lemma_upos):
        #     if item is not None:
        #         lemma, upos = item
        #         if upos in classes:
        #             classes[upos].append(lemma)

        # for cls, wordlist in classes.items():
        #     counter = Counter(wordlist)
        #     with open(args.output_file + f'.{cls}.txt', 'w', encoding='utf-8') as f:
        #         for lemma, freq in counter.most_common():
        #             f.write(f'{lemma} {freq}\n')


    # print(ignored_tags)
    # for tokenlist in read_conllu_file(args.input_file):
    #     for token in tokenlist:
    #         print(token)
    #         print(token['feats'])
    #         print(parser_func(token))
    #         exit()

if __name__ == '__main__':
    main()
