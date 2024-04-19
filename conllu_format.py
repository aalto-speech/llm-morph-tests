
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

def edit_conllu():
    # replace all lemmas with "lannanajo", all upos with "NOUN" and all feats with "_"
    # leave other fields as they are
    new_tokens = []
    for tokenlist in read_conllu_file('data/omorfi_noun_lexemes_filtered_inflected.txt.00.plain.head100.parsed'):
        assert len(tokenlist) == 1
        newtokenlist = tokenlist.copy()
        # print(f'lannanajo {tokenlist[0]["form"]}',newtokenlist.metadata)
        # exit()
        newtokenlist.metadata['text'] = f'lannanajo {tokenlist[0]["form"]}'
        token = tokenlist[0].copy()
        token['form'] = 'lannanajo'
        token['lemma'] = 'lanta#ajo'
        token['upos'] = 'NOUN'
        token['feats'] = '_'
        newtokenlist[0] = token

        token = tokenlist[0].copy()
        token['form'] = tokenlist[0]['form']
        token['lemma'] = 'lanta#ajo'
        token['upos'] = 'NOUN'
        token['feats'] = '_'
        newtokenlist.append(token)
        new_tokens.append(newtokenlist)


    with open('data/omorfi_noun_lexemes_filtered_inflected.txt.00.plain.head100.parsed.edited4', 'w', encoding='utf-8') as f:
        for tokenlist in new_tokens:
            f.write(tokenlist.serialize())
            f.write('\n')

    # for tokenlist in read_conllu_file('data/omorfi_noun_lexemes_filtered_inflected.txt.00.plain.head100.parsed'):
    #     for token in tokenlist:
    #         print(token['form'], token['lemma'], token['upos'], token['feats'])
            

def make_conllu_format(input_file):
    """Make a conllu file from a text file with.
    The format of the input file is taivutusmuoto -- perusmuoto

    The format of the output file is:
    # text = perusmuoto taivutusmuoto
    1 perusmuoto perusmuoto NOUN _	_	0	root	_	SpacesAfter=\n
    1 taivutusmuoto perusmuoto NOUN _	_	0	root	_	SpacesAfter=\n
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        # lines = f.readlines()
        lines = json.load(f)
    # print(lines[:10])
    # exit()

    new_tokens = []
    for i, line in enumerate(lines):
        taivutusmuoto, perusmuoto = line.strip().split(' -- ')
        token = TokenList()
        token.metadata['text'] = f'{perusmuoto} {taivutusmuoto}'
        token.metadata['sent_id'] = str(i+1)
        token.append({'id': 1, 'form': perusmuoto, 'lemma': perusmuoto,
                      'upos': 'NOUN', 'xpos': '_', 'feats': '_', 'head': 0, 'deprel':
                      'root', 'deps': '_', 'misc': 'SpacesAfter=\\n'})
        token.append({'id': 2, 'form': taivutusmuoto, 'lemma': perusmuoto,
                      'upos': 'NOUN', 'xpos': '_', 'feats': '_', 'head': 0,
                      'deprel': 'root', 'deps': '_', 'misc': 'SpacesAfter=\\n'})
        new_tokens.append(token)

    with open(input_file + '.conllu', 'w', encoding='utf-8') as f:
        for tokenlist in new_tokens:
            f.write(tokenlist.serialize())
            f.write('\n')


def conllu2json(input_file):
    """Take the morphological tags from the conllu file and return
    them as a list in a json file.
    """
    morph_tags = []
    for tokenlist in read_conllu_file(input_file):
        if not tokenlist[1]['feats']:
            morph_tags.append('other, other, other')
            continue
        tags = ''
        if 'Case' not in tokenlist[1]['feats']:
            case = 'Nom'
        else:
            case = tokenlist[1]['feats']['Case']
        
        if 'Number' in tokenlist[1]['feats']:
            tags += f"{tokenlist[1]['feats']['Number']}, "
        else:
            tags += 'other, '
        
        tags += f"{case}, "

        if 'Number[psor]' in tokenlist[1]['feats'] and 'Person[psor]' in tokenlist[1]['feats']:
            tags += f"{tokenlist[1]['feats']['Number[psor]']}{tokenlist[1]['feats']['Person[psor]']}"
        elif 'Person[psor]' in tokenlist[1]['feats']:
            tags += f"{tokenlist[1]['feats']['Person[psor]']}"
        
        morph_tags.append(tags)
    
    with open(input_file + '.json', 'w', encoding='utf-8') as f:
        json.dump(morph_tags, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    from conllu import parse_incr, TokenList
    from tqdm import tqdm
    import gzip
    import argparse
    import json

    argparser = argparse.ArgumentParser(description='Make a conllu file from a text file with perusmuoto -- taivutusmuoto')
    argparser.add_argument('input_file', help='Input file with perusmuoto -- taivutusmuoto')
    args = argparser.parse_args()

    # make_conllu_format(args.input_file)
    # edit_conllu()
    conllu2json(args.input_file)
