## Test sets to assess morphological knowledge in LLMs

### Generating the test sets
- select a set of lemmas that are used
    - take a random sample of the shortlisted lemmas
    - consider frequencies of the
        - lemmas
            - from lemma_freqs.txt file
        - morphological feats
            - from feats_freqs.txt file
        - morphological forms
            - from word_freqs.txt file
    - consider also diversity of the forms for lemma?
        - from lemma2feats.pkl file

- select the morphological categories that are used
    - initial categories:
        - nouns:
            - number (singular, plural)
            - possessive suffix (1/2/3 person singular/plural)
            - grammatical case (nominative, accusative, genitive, etc.)
        - verbs:
            - tense (present, past, etc.)
            - mood (indicative, conditional, etc.)
            - person (1/2/3)
            - number (singular, plural)
            - voice (active, passive)
            - verb type (transitive, intransitive)
        - adjectives:
            - degree (positive, comparative, superlative)
            - number (singular, plural)
            - case (nominative, accusative, genitive, etc.)
        - adverbs:
            - degree (positive, comparative, superlative)
            - case (nominative, accusative, genitive, etc.)
- generate the inflected forms for the lemmas
    - use the HFST tools (omorfi for Finnish)
- design the prompts for the test sets
    - prompts for pre-trained
    - prompts for instruct-tuned LLMs
- generate the test sets
    - for each lemma, generate the inflected forms
    - for each inflected form, generate the prompt
        - multiple-choice with the correct answer and wrong ones
- to test LLMs, sample the test sets
    - sample the lemmas
    - sample the inflected forms
    - sample the prompts

### Scripts
- `generate_test_sets.py`: script to generate the test sets, usage:
```
python generate_test_sets.py
```

- `sample_test_sets.py`: script to sample the test sets, usage:
```
python sample_test_sets.py
```

### TODO
- tarkista onko sg/pl sama, tai muut muodot