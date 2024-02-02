#/bin/python3
# -*- coding: utf-8 -*-

# This script generates samples for the morphological test suite
# using the uralicNLP library.

from uralicNLP import uralicApi
# uralicApi.download("fin")


finnish_cases = {
    # 'Abe': 'abessive',
    # 'Ade': 'adessive',
    # 'All': 'allative',
    # 'Abl': 'ablative',
    # 'Gen': 'genitive',
    # 'Ins': 'instructive',
    # 'Ine': 'inessive',
    'Ill': 'illative',
    'Ela': 'elative',
    'Tra': 'translative',
    'Ess': 'essive',
    # 'Par': 'partitive',
    'Nom': 'nominative',
}

finnish_persons = {
    'PxSg1': 'first person singular',
    'PxSg2': 'second person singular',
    'PxSg3': 'third person singular',
    'PxPl1': 'first person plural',
    'PxPl2': 'second person plural',
    'PxPl3': 'third person plural',
}

finnish_numbers = {
    'Sg': 'singular',
    'Pl': 'plural',
}

finnish_clitics = [
    'Qst',
    'Foc/kin',
]

def generate_forms(lemma):
    morph_forms = []
    for case_short, case in finnish_cases.items():
        for person_short, person in finnish_persons.items():
            for number_short, number in finnish_numbers.items():
                feat_string = f'{lemma}+N+{number_short}+{case_short}+{person_short}'
                inflected = [item[0] for item in uralicApi.__api_generate(feat_string, "fin")]
                for form in inflected:
                    tupl = (form, feat_string, f'{lemma}, {number}, {case}, {person}')
                    morph_forms.append(tupl)
                    print(tupl)

    return morph_forms


def main():
    # forms = generate_forms('kaista')
    forms = generate_forms('kinos')

if __name__ == '__main__':
    main()
