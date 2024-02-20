## Test sets to assess morphological knowledge in LLMs

### Generating the test sets
- select a set of lemmas that are used
    - consider e.g. the frequencies of the lemmas in the training data
- select the morphological categories that are used
    - initial categories:
        - number (singular, plural)
        - possessive suffix (1/2/3 person singular/plural)
        - grammatical case (nominative, accusative, genitive, etc.)
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