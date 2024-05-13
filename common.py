import re

FIN_NUM_CLASSES = {
    "yksikkö": 0,
    "monikko": 1,
}
FIN_NUM_CLASSES_UDEP = {
    "Sing": 0,
    "Plur": 1,
}
FIN_NUM_CLASSES_UNIMORPH = {
    "SG": 0,
    "PL": 1,
}
FIN_PERSON_CLASSES = {
    # "yksikön ensimmäinen persoona": 0,
    # "yksikön toinen persoona": 1,
    # "monikon ensimmäinen persoona": 2,
    # "monikon toinen persoona": 3,
    # "kolmas persoona": 4,
    "1. persoonan yksikkö": 0,
    "2. persoonan yksikkö": 1,
    "1. persoonan monikko": 2,
    "2. persoonan monikko": 3,
    "3. persoona": 4,
}
FIN_PERSON_CLASSES_UDEP = {
    "Sing1": 0,
    "Sing2": 1,
    "Plur1": 2,
    "Plur2": 3,
    "3": 4,
}
FIN_PERSON_CLASSES_UNIMORPH = {
    "SG1": 0,
    "SG2": 1,
    "PL1": 2,
    "PL2": 3,
    "3": 4,
}
FIN_CASE_CLASSES = {
    "abessiiivi": 0,
    "ablatiivi": 1,
    "adessiivi": 2,
    "allatiivi": 3,
    "elatiivi": 4,
    "essiivi": 5,
    "genetiivi": 6,
    "illatiivi": 7,
    "inessiivi": 8,
    "instruktiivi": 9,
    "nominatiivi": 10,
    "partitiivi": 11,
    "translatiivi": 12,
    "komitatiivi": 13,
}
FIN_CASE_CLASSES_UDEP = {
    "Abe": 0,
    "Abl": 1,
    "Ade": 2,
    "All": 3,
    "Ela": 4,
    "Ess": 5,
    "Gen": 6,
    "Ill": 7,
    "Ine": 8,    
    "Ins": 9,
    "Nom": 10,
    "Par": 11,
    "Tra": 12,
    "Com": 13,
}
FIN_CASE_CLASSES_UNIMORPH = {s.upper(): i for s, i in FIN_CASE_CLASSES_UDEP.items()}

FIN_FEATS_CLASSES = {
    "number": {**FIN_NUM_CLASSES_UDEP, **FIN_NUM_CLASSES_UNIMORPH, **FIN_NUM_CLASSES},
    "person": {**FIN_PERSON_CLASSES_UDEP, **FIN_PERSON_CLASSES_UNIMORPH, **FIN_PERSON_CLASSES},
    "case": {**FIN_CASE_CLASSES_UDEP, **FIN_CASE_CLASSES_UNIMORPH, **FIN_CASE_CLASSES},
}


NUM_LABELS = {
    "yksikkö": "SG",
    "monikko": "PL",
    "Sing": "SG",
    "Plur": "PL",
    "SG": "SG",
    "PL": "PL",
    "other": "other",
}

PERSON_LABELS = {
    "yksikön ensimmäinen persoona": "SG1",
    "yksikön toinen persoona": "SG2",
    "yksikön kolmas persoona": "3",
    "monikon ensimmäinen persoona": "PL1",
    "monikon toinen persoona": "PL2",
    "monikon kolmas persoona": "3",
    "kolmas persoona": "3",
    "1. persoonan yksikkö": "SG1",
    "2. persoonan yksikkö": "SG2",
    "1. persoonan monikko": "PL1",
    "2. persoonan monikko": "PL2",
    "3. persoona": "3",
    "3. persoonan yksikkö": "3",
    "3. persoonan monikko": "3",
    "Sing1": "SG1",
    "Sing2": "SG2",
    "Plur1": "PL1",
    "Plur2": "PL2",
    "3": "3",
    "other": "other",
}

CASE_LABELS = {
    "abessiivi": "ABE",
    "ablatiivi": "ABL",
    "adessiivi": "ADE",
    "allatiivi": "ALL",
    "elatiivi": "ELA",
    "essiivi": "ESS",
    "genetiivi": "GEN",
    "illatiivi": "ILL",
    "inessiivi": "INE",
    "instruktiivi": "INS",
    "nominatiivi": "NOM",
    "partitiivi": "PAR",
    "translatiivi": "TRA",
    "komitatiivi": "COM",
    "Abe": "ABE",
    "Abl": "ABL",
    "Ade": "ADE",
    "All": "ALL",
    "Ela": "ELA",
    "Ess": "ESS",
    "Gen": "GEN",
    "Ill": "ILL",
    "Ine": "INE",
    "Ins": "INS",
    "Nom": "NOM",
    "Par": "PAR",
    "Tra": "TRA",
    "Com": "COM",
    "other": "other",
}

# CASE_LABELS_RAW = """ ABE-    abessiivi-       vajanto    -     abessive    -    talotta
#     ABL-    ablatiivi-       ulkoeronto  -    ablative    -    talolta
#     ADE-    adessiivi-       ulko-olento  -   adessive    -    talolla
#     ALL-    allatiivi-       ulkotulento  -   allative    -    talolle
#     ELA-    elatiivi-        sisäeronto   -   elative     -    talosta
#     ESS-    essiivi-         olento      -    essive       -   talona
#     GEN-    genetiivi-       omanto      -    genitive     -   talon
#     ILL-    illatiivi-       sisätulento  -   illative     -   taloon
#     INE-    inessiivi -      sisäolento   -   inessive      -  talossa
#     NOM-    nominatiivi -    nimentö     -    nominative   -   talo
#     PAR-    partitiivi  -    osanto      -    partitive    -   taloa
#     TRA-    translatiivi  -  tulento    -     translative  -   taloksi"""
#     # INS-    instruktiivi-    keinonto     -   instructive   -  taloin
#     # COM-    komitatiivi -    seuranto     -   comitative   -   taloineen
# CASE_LABELS = [label.split("-")[1].strip() for label in CASE_LABELS_RAW.split("\n")]
# CASE_LABELS.append("other")

# CASE_LABELS_TRANSLATED = [label.split("-")[0].strip().lower().capitalize() for label in CASE_LABELS_RAW.split("\n")]
# CASE_LABELS_TRANSLATED.append("other")


def parse_omorstring(omorstring):
    """Parse the omorstring and return the classes."""
    regex2key = {
        "NUM=": "number",
        "POSS=": "person",
        "CASE=": "case",
        "WORD_ID=": "lemma",
        "UPOS=": "upos",
    }
    classes = {}
    # classes['lemma'] = re.search(r'(?<=WORD_ID=).*?(?=])', omorstring).group()
    # classes['number'] = re.search(r'(?<=NUM=).*?(?=])', omorstring).group()
    # classes['gcase'] = re.search(r'(?<=CASE=).*?(?=])', omorstring).group()
    # classes['possessive'] = re.search(r'(?<=POSS=).*?(?=])', omorstring).group()
    # classes['upos'] = re.search(r'(?<=UPOS=).*?(?=])', omorstring).group()
    for key, value in regex2key.items():
        if key in omorstring:
            classes[value] = re.search(rf'(?<={key}).*?(?=])', omorstring).group()
    return classes
