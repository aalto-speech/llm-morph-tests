#/bin/bash

# copied from /m/triton/scratch/morphogen/dbca/exp/subset-d-1m/filters.sh

# lemmas that are not in the Finnish dictionary are removed from the group of analysed words
included_lemmas_file="data/included_lemmas.txt"
cat '/scratch/elec/morphogen/dbca/data/proper-names/all_finnish_lemmas.txt' \
    '/scratch/elec/morphogen/dbca/data/proper-names/english_given_names.txt' \
    '/scratch/elec/morphogen/dbca/data/proper-names/finnish_given_names.txt' \
    '/scratch/elec/morphogen/dbca/data/proper-names/paikannimet_list.txt' \
    > "$included_lemmas_file"

# words with these POS tags are removed from the group of analysed words
# NOISY_POS_TAGS = set() #['PROPN'])

# words with these morphological tags are removed from the group of analysed words
noisy_tags_file="data/noisy_tags.txt"
echo 'Typo
Abbr
Style
Foreign
NumType
AdpType' > "$noisy_tags_file"

# these tags are removed from the morphological tag list
ignored_tags_file="data/ignored_tags.txt"
echo 'Degree=Pos
Reflex=Yes
PronType=
Derivation=' > "$ignored_tags_file"


# these compounds are ignored when computing compound divergence (atoms are still used)
# IGNORED_COMPOUNDS = set() #set(['Case=Nom+Number=Sing'])

# lemmas with these characters are removed from the group of analysed words
# EXCLUDED_CHARS = set(punctuation).union(set('1234567890')).union(set(' '))
