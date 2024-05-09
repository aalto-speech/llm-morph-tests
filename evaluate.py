import argparse
import ast
import json
from freq_stats_from_conllu import read_freq_stats
from common import NUM_LABELS, CASE_LABELS, PERSON_LABELS, NUM_LABELS_TRANSLATED, CASE_LABELS_TRANSLATED, PERSON_LABELS_TRANSLATED


# def read_preds_and_refs(pred_files, ref_files, prompt_files=None):
#     """Read the predictions and references from the files."""
    
#     print(f"pred_files: {pred_files}")
#     print(f"ref_files: {ref_files}")
#     print(f"prompt_files: {prompt_files}")
    
#     preds = []
#     for file in pred_files:
#         with open(file, "r", encoding="utf-8") as f:
#             preds += ast.literal_eval(f.readlines()[-1])

#     prompts = []
#     if prompt_files:
#         for file in prompt_files:
#             with open(file, "r", encoding="utf-8") as f:
#                 prompts += ast.literal_eval(f.read())

#     refs = []
#     for file in ref_files:
#         with open(file, "r", encoding="utf-8") as f:
#             refs += ast.literal_eval(f.read())

#     assert len(preds) == len(refs), "Number of predictions and references should be the same"
#     if prompt_files:
#         assert len(preds) == len(prompts), "Number of predictions and prompts should be the same"

#     return preds, refs, prompts

def read_files(pred_file, ref_file, prompt_file=None, refs_range=None):
    """Read the predictions and references from the files."""

    with open(pred_file, "r", encoding="utf-8") as f:
        preds = json.load(f)

    with open(ref_file, "r", encoding="utf-8") as f:
        refs = json.load(f)
    if refs_range:
        refs = refs[refs_range[0]:refs_range[1]]

    if prompt_file:
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompts = json.load(f)
    else:
        prompts = None

    assert len(preds) == len(refs), "Number of predictions and references should be the same. " \
        + f"len(preds): {len(preds)}, len(refs): {len(refs)}"
    if prompt_file:
        assert len(preds) == len(prompts), "Number of predictions and prompts should be the same"

    return preds, refs, prompts



def parse_answer_line(answer):
    """Parse the answer into a tuple of (number, case, person)."""
    if '--' in answer: # remove the inflected form and also the base form
        answer = ','.join(answer.split('--')[1].split(',')[1:])


    parsed = [i.strip() for i in answer.split(',') if i.strip()]
    if len(parsed) > 3:
        return tuple(parsed[1:4])
    elif len(parsed) == 3:
        return tuple(parsed)
    elif len(parsed) == 2:
        return tuple(parsed + [''])
    elif len(parsed) == 1:
        return tuple(parsed + ['', ''])
    else:
        return tuple(['', '', ''])


def parse_ref(refs):
    """Parse the answer into a tuple of (number, case, person)."""
    if isinstance(refs, str):
        refs = refs.split('\n')
    return [parse_answer_line(ref) for ref in refs if ref.strip()]


def normalise_preds(pred):
    """Normalise the predictions."""

    (pred_num, pred_case, pred_person) = parse_answer_line(pred)
    pred_person = pred_person.split('\n')[0]

    if pred_num not in NUM_LABELS:
        print(f"replacing pred_num {pred_num} with other")
        pred_num = "other"

    if pred_case not in CASE_LABELS:
        print(f"replacing pred_case {pred_case} with other")
        pred_case = "other"

    if pred_person not in PERSON_LABELS:
        if pred_person in ["yksikön kolmas persoona", "monikon kolmas persoona"]:
            pred_person = "kolmas persoona"
        else:
            print(f"replacing pred_person {pred_person} with other")
            pred_person = "other"

    return (pred_num, pred_case, pred_person)

def normalise_refs(ref):
    ref_lines = parse_ref(ref)
    for ref_line in ref_lines:
        (ref_num, ref_case, ref_person) = ref_line

        if ref_num not in NUM_LABELS:
            raise ValueError(f"{ref_num} not in num_labels")
        if ref_case not in CASE_LABELS:
            raise ValueError(f"{ref_case} not in case_labels")
        if ref_person not in PERSON_LABELS:
            raise ValueError(f"{ref_person} not in person_labels")

    return ref_lines


def check_exact_match(pred, ref, verbose=False, parse=True):
    """Check the exact match for each of the three categories."""

    if parse:
        pred = parse_answer_line(pred)
    (pred_num, pred_case, pred_person) = pred
    if parse:
        pred_person = pred_person.split('\n')[0]
    if parse:
        ref = parse_ref(ref)

    best_match = 0
    results = (False, False, False)
    aligned = (None, None, None, None, None, None)
    for ref_line in ref:
        (ref_num, ref_case, ref_person) = ref_line

        match = ( pred_num == ref_num, \
            pred_case == ref_case, \
            # pred_person.startswith(ref_person) or \
            #     (ref_person == "kolmas persoona" and \
            #     ( pred_person.startswith("yksikön kolmas persoona") or \
            #     pred_person.startswith("monikon kolmas persoona") )
            #     )
            pred_person == ref_person
            )

        if match.count(True) >= best_match:
            best_match = match.count(True)
            results = match
            aligned = (pred_num, ref_num, pred_case, ref_case, pred_person, ref_person)

    if verbose:
        print(f"Pred_num: {pred_num}, ref_num: {ref_num}")
        print(f"Pred_case: {pred_case}, ref_case: {ref_case}")
        print(f"Pred_person: {pred_person}, ref_person: {ref_person}")
        print(f"Results: {results}")
        print()

    return results, aligned


def get_aligned(preds, refs):
    """Get the aligned predictions and references."""
    aligned = []
    for pred, ref in zip(preds, refs):
        _, alignment = check_exact_match(pred, ref, parse=False)
        aligned.append(alignment)
    return aligned


def get_exact_matches(preds, refs):
    """Make a dict of lists of boolean values of whether the prediction is correct"""
    results = {
        'num': [],
        'case': [],
        'person': [],
        'complete': []
        }

    for pred, ref in zip(preds, refs):
        (num_match, case_match, person_match), _ = check_exact_match(pred, ref)
        results['num'].append(num_match)
        results['case'].append(case_match)
        results['person'].append(person_match)
        results['complete'].append(num_match and case_match and person_match)

    return results


def get_avg_accuracies(preds, refs, verbose=True):
    """Make a dict of lists of boolean values of whether the prediction is correct"""
    results = {
        'num': 0,
        'case': 0,
        'person': 0,
        'complete': 0
        }

    for pred, ref in zip(preds, refs):
        (num_match, case_match, person_match), _ = check_exact_match(pred, ref)
        if num_match:
            results['num'] += 1
        if case_match:
            results['case'] += 1
        if person_match:
            results['person'] += 1
        if num_match and case_match and person_match:
            results['complete'] += 1
        
        if verbose:
            print(pred)
            print(ref)
            print(f"num_match: {num_match}, case_match: {case_match}, person_match: {person_match}")
            print()

    return results



def parse_lemma_form_from_prompt(prompt):
    form_lemma = prompt.split('\n')[-1]
    return form_lemma.split('--')[1].strip(), form_lemma.split('--')[0].strip()



def plot_accuracy_wrt_freq(matches, keys, freqs, title):
    """Plot accuracy wrt frequency.
    Also calculate how much accuracy correlates with frequency.
    
    Parameters:
    matches: list of boolean values of whether the prediction is correct
    keys: list of keys to match the frequencies
    freqs: dict of frequencies
    title: title of the plot
    """

    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.stats import pearsonr

    freqs2accs = {}

    for key, match in zip(keys, matches):
        if key in freqs:
            # freqs_list.append(freqs[key])
            # acc_list.append(match)
            if freqs[key] in freqs2accs:
                freqs2accs[freqs[key]].append(match)
            else:
                freqs2accs[freqs[key]] = [match]

    print(freqs2accs)

    plt.scatter(freqs2accs.keys(), [np.mean(v) for v in freqs2accs.values()])
    plt.xlabel(f"{title} frequency")
    plt.ylabel("Accuracy")
    plt.title(f"Accuracy wrt {title} frequency")
    # plt.show()
    plt.savefig(f'accuracy_wrt_{title}_freq_mean.png')

    print(f"Correlation between accuracy and {title} frequency: {pearsonr(list(freqs2accs.keys()), [np.mean(freqs2accs[key]) for key in freqs2accs.keys()])}")


def confusion_mats(preds, refs, output_file):
    """Plot confusion matrices for the three categories."""

    import numpy as np
    from sklearn.metrics import confusion_matrix

    aligned = get_aligned(preds, refs)

    num_conf = confusion_matrix([a[1] for a in aligned], [a[0] for a in aligned], labels=NUM_LABELS)
    case_conf = confusion_matrix([a[3] for a in aligned], [a[2] for a in aligned], labels=CASE_LABELS)
    person_conf = confusion_matrix([a[5] for a in aligned], [a[4] for a in aligned], labels=PERSON_LABELS)

    # the last row and column are for "other" category
    # the reference should never be "other"
    assert num_conf[-1, :].sum() == 0
    assert case_conf[-1, :].sum() == 0
    assert person_conf[-1, :].sum() == 0
    # remove the last row
    num_conf = num_conf[:-1, :]
    case_conf = case_conf[:-1, :]
    person_conf = person_conf[:-1, :]
    # fix the tics
    ref_num_labels = [label for label in NUM_LABELS if label != "other"]
    ref_case_labels = [label for label in CASE_LABELS if label != "other"]
    ref_person_labels = [label for label in PERSON_LABELS if label != "other"]


    print(num_conf)
    print(case_conf)
    print(person_conf)

    import matplotlib.pyplot as plt
    import seaborn as sns

    # set style for the plots
    sns.set_theme('poster')
    sns.set_style('whitegrid')
    # sns.color_palette("rocket")

    heatmap_kwargs = {'annot': True, 'fmt': 'g', 'cmap': 'Blues'}
        # annot=True, cmap='Blues', fmt='g'

    _, ax = plt.subplots(1, 3, figsize=(60, 17))

    sns.heatmap(num_conf, ax=ax[0], **heatmap_kwargs)
    ax[0].set_title("Number")
    ax[0].set_yticklabels(ref_num_labels, rotation=0)
    ax[0].set_xticklabels(NUM_LABELS, rotation=90)
    ax[0].set_ylabel("True label")
    ax[0].set_xlabel("Predicted label")


    sns.heatmap(case_conf, ax=ax[1], **heatmap_kwargs)
    ax[1].set_title("Case")
    ax[1].set_yticklabels(ref_case_labels, rotation=0)
    ax[1].set_xticklabels(CASE_LABELS, rotation=90)
    ax[1].set_ylabel("True label")
    ax[1].set_xlabel("Predicted label")


    sns.heatmap(person_conf, ax=ax[2], **heatmap_kwargs)
    ax[2].set_title("Person")
    ax[2].set_yticklabels(ref_person_labels, rotation=0)
    ax[2].set_xticklabels(PERSON_LABELS, rotation=90)
    ax[2].set_ylabel("True label")
    ax[2].set_xlabel("Predicted label")

    plt.tight_layout()

    plt.savefig(output_file)



def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--preds", help="files with predictions", type=str)
    parser.add_argument("--preds-include-prompt", action="store_true",
                        help="the preds include the prompt, so it should be removed")
    parser.add_argument("--translate-preds", action="store_true",
                        help="translate the predictions")
    parser.add_argument("--prompts", help="files with prompts", type=str)
    parser.add_argument("--refs", help="files with references", type=str)
    parser.add_argument("--lemma-freq-file", help="file with lemma frequencies")
    parser.add_argument("--form-freq-file", help="file with form frequencies")
    parser.add_argument("--form-freq-from-corpus-file", help="file with form frequencies from corpus")
    parser.add_argument("--feats-freq-file", help="file with feature frequencies")
    parser.add_argument("--acc-wrt-freq", action="store_true",
                        help="plot accuracy wrt frequency")
    parser.add_argument("--omorstrings", type=str, help="file with omorstrings")
    parser.add_argument("--out", help="output file")
    parser.add_argument("--confusion", help="plot confusion matrices", action="store_true")
    parser.add_argument("--refs-range", type=int, nargs=2, help="range of references to use")
    args = parser.parse_args()

    preds, refs, prompts = read_files(args.preds, args.refs, args.prompts, refs_range=args.refs_range)

    if args.translate_preds:
        for i, pred in enumerate(preds):
            # print(pred)
            (pred_num, pred_case, pred_person) = parse_answer_line(pred)
            # print(f"pred_num: {pred_num}, pred_case: {pred_case}, pred_person: {pred_person}")

            if pred_num and pred_num in NUM_LABELS_TRANSLATED:
                translated_num = NUM_LABELS[ NUM_LABELS_TRANSLATED.index(pred_num) ]
            else:
                translated_num = "other"
            if pred_case and pred_case in CASE_LABELS_TRANSLATED:
                translated_case = CASE_LABELS[ CASE_LABELS_TRANSLATED.index(pred_case) ]
            else:
                translated_case = "other"
            if pred_person and pred_person in PERSON_LABELS_TRANSLATED:
                translated_person = PERSON_LABELS[ PERSON_LABELS_TRANSLATED.index(pred_person) ]
            else:
                translated_person = "other"

            preds[i] = f'{translated_num}, {translated_case}, {translated_person}'
            # print(preds[i])
    
    if prompts:
        assert len(prompts) == len(refs), "Number of prompts and references should be the same"
        if args.preds_include_prompt:
            preds = [pred[len(prompt):] for pred, prompt in zip(preds, prompts)]

    if args.confusion:
        normalised_preds = [normalise_preds(pred) for pred in preds]
        normalised_refs = [normalise_refs(ref) for ref in refs]
        confusion_mats(normalised_preds, normalised_refs, args.out)
    else:
        results = get_avg_accuracies(preds, refs)

        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(f"Number: {results['num'] / len(refs)}\n")
                f.write(f"Case: {results['case'] / len(refs)}\n")
                f.write(f"Person: {results['person'] / len(refs)}\n")
                f.write(f"Complete: {results['complete'] / len(refs)}\n")
        else:
            print(f"Number: {results['num'] / len(refs)}")
            print(f"Case: {results['case'] / len(refs)}")
            print(f"Person: {results['person'] / len(refs)}")
            print(f"Complete: {results['complete'] / len(refs)}")

        if args.acc_wrt_freq:

            ems = get_exact_matches(preds, refs)

            with open(args.prompts, "r", encoding="utf-8") as f:
                prompts = json.load(f)

            if args.lemma_freq_file:
                freqs = read_freq_stats(args.lemma_freq_file)
                fig_title = "lemma"
                freq_dict_keys = [parse_lemma_form_from_prompt(prompt)[0] for prompt in prompts]
                # print(f"freq_dict_keys: {freq_dict_keys}")

                plot_accuracy_wrt_freq(ems['person'], freq_dict_keys, freqs, fig_title)

            if args.form_freq_file:
                freqs = read_freq_stats(args.form_freq_file)
                fig_title = "form"
                freq_dict_keys = [parse_lemma_form_from_prompt(prompt)[1] for prompt in prompts]
                # print(f"freq_dict_keys: {freq_dict_keys}")

                plot_accuracy_wrt_freq(ems['person'], freq_dict_keys, freqs, fig_title)

            if args.form_freq_from_corpus_file:
                with open(args.form_freq_from_corpus_file, "r", encoding="utf-8") as f:
                    freqs = json.load(f)
                fig_title = "form_from_corpus_person"
                freq_dict_keys = [f"{parse_lemma_form_from_prompt(prompt)[1]} -- {parse_lemma_form_from_prompt(prompt)[0]}" for prompt in prompts]

                plot_accuracy_wrt_freq(ems['person'], freq_dict_keys, freqs, fig_title)

            if args.feats_freq_file:
                freqs = read_freq_stats(args.feats_freq_file)
                fig_title = "feature"

if __name__ == "__main__":
    main()
