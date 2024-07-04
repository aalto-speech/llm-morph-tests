import argparse
import ast
import json
from freq_stats_from_conllu import read_freq_stats
from common import NUM_LABELS, CASE_LABELS, PERSON_LABELS
from sklearn import metrics



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

    assert len(preds) == len(refs), "Number of preds and refs should be the same. " \
        + f"len(preds): {len(preds)}, len(refs): {len(refs)}"
    if prompt_file:
        assert len(preds) == len(prompts), "Number of preds and prompts should be the same"

    return preds, refs, prompts

def parse_pred_file_name(file_name):
    """Parse the prediction file name to get the model name and prompt type.
    e.g. prompts_10shot_gpt3.5-turbo_0-1000.jsonl
    """
    file_name = file_name.split('/')[-1]
    parts = file_name.split('_')
    return parts[2], int(parts[1].split('shot')[0])


def parse_answer_line(answer, cot=False, sample=None):
    """Parse the answer into a tuple of (number, case, person)."""
    if not answer:
        return ('', '', '')

    # if multiple rows, check if the reference is in the answer
    if '\n' in answer:
        if sample and sample in answer:
            answer = answer.split(sample)[1].split('\n')[0]
        elif not cot: # take the first one that is not empty
            rows = answer.split('\n')
            for row in rows:
                if row.strip():
                    answer = row
                    break
        else: # take the last one
            answer = answer.split('\n')[-1]

    # if -- is included take the second part
    if '--' in answer:
        afterdash = answer.split('--')[1].split(',')
        if len(afterdash) == 4: # remove the inflected form and also the base form
            answer = ','.join(afterdash[1:])
        elif len(afterdash) == 3:
            answer = ','.join(afterdash) # base form is probably omitted

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


def normalise_preds(pred, sample, last_line=False, verbose=False):
    """Normalise the predictions."""

    (pred_num, pred_case, pred_person) = parse_answer_line(pred, sample=sample, cot=last_line)

    if pred_num not in NUM_LABELS:
        if verbose:
            print(f"replacing pred_num {pred_num} with other")
            print('ref', sample, 'full answer:', pred)
            print()
        pred_num = "other"
    else:
        pred_num = NUM_LABELS[pred_num]

    if pred_case not in CASE_LABELS:
        if verbose:
            print(f"replacing pred_case {pred_case} with other")
        pred_case = "other"
    else:
        pred_case = CASE_LABELS[pred_case]

    if pred_person not in PERSON_LABELS:
        if pred_person.startswith('3. persoona') and pred_person != '3. persoona':
            pred_person = PERSON_LABELS['3. persoona']
        else:
            if verbose:
                print(f"replacing pred_person {pred_person} with other")
                pred_person = "other"
    else:
        pred_person = PERSON_LABELS[pred_person]

    return (pred_num, pred_case, pred_person)

def normalise_refs(ref):
    """Normalise the labels in the reference."""
    ref_lines = parse_ref(ref)
    new_ref_lines = []
    for ref_line in ref_lines:
        (ref_num, ref_case, ref_person) = ref_line

        if ref_num not in NUM_LABELS:
            raise ValueError(f"{ref_num} not in num_labels")
        ref_num = NUM_LABELS[ref_num]

        if ref_case not in CASE_LABELS:
            raise ValueError(f"{ref_case} not in case_labels")
        ref_case = CASE_LABELS[ref_case]

        if ref_person not in PERSON_LABELS:
            raise ValueError(f"{ref_person} not in person_labels")
        ref_person = PERSON_LABELS[ref_person]

        new_ref_lines.append((ref_num, ref_case, ref_person))

    return new_ref_lines


def check_exact_match(pred, ref, verbose=False):
    """Check the exact match for each of the three categories."""

    (pred_num, pred_case, pred_person) = pred

    best_match = 0
    results = (False, False, False)
    aligned = (None, None, None, None, None, None)
    for ref_line in ref:
        (ref_num, ref_case, ref_person) = ref_line
        match = (pred_num == ref_num, pred_case == ref_case, pred_person == ref_person)

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
        _, alignment = check_exact_match(pred, ref)
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

    for i, (pred, ref) in enumerate(zip(preds, refs)):
        (num_match, case_match, person_match), _ = check_exact_match(pred, ref)
        results['num'].append(num_match)
        results['case'].append(case_match)
        results['person'].append(person_match)
        results['complete'].append(num_match and case_match and person_match)

    return results


def get_avg_accuracies(preds, refs, verbose=False):
    """Make a dict of lists of boolean values of whether the prediction is correct"""
    results = { 'num': 0, 'case': 0,  'person': 0, 'complete': 0 }

    for i, (pred, ref) in enumerate(zip(preds, refs)):
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
        
        if not person_match:
            print('sample number:', i)
            print(f"pred: {pred}")
            print(f"ref: {ref}")
            print()

    return results

def get_f1_scores(preds, refs):
    """Get the F1 scores for the three categories."""
    aligned = get_aligned(preds, refs)

    num_preds = [a[0] for a in aligned]
    num_refs = [a[1] for a in aligned]
    case_preds = [a[2] for a in aligned]
    case_refs = [a[3] for a in aligned]
    person_preds = [a[4] for a in aligned]
    person_refs = [a[5] for a in aligned]

    num_f1 = metrics.f1_score(num_refs, num_preds, average='micro')
    case_f1 = metrics.f1_score(case_refs, case_preds, average='micro')
    person_f1 = metrics.f1_score(person_refs, person_preds, average='micro')

    return num_f1, case_f1, person_f1



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

    corr = pearsonr(list(freqs2accs), [np.mean(acc) for acc in freqs2accs.values()])
    print(f"Correlation between accuracy and {title} frequency: {corr}")


def many_confusion_mats(preds, refs, output_file, shots, model_name):
    """Plot confusion matrices for the three categories."""

    num_labels = ["SG", "PL", "other"]
    case_labels = list(set(CASE_LABELS.values()))
    case_labels.remove("other")
    case_labels.sort()
    case_labels.append("other")
    person_labels = ["SG1", "SG2", "PL1", "PL2", "3", "other"]
    ref_num_labels = [label for label in num_labels if label != "other"]
    ref_case_labels = [label for label in case_labels if label != "other"]
    ref_person_labels = [label for label in person_labels if label != "other"]

    import matplotlib.pyplot as plt
    import seaborn as sns

    # set style for the plots
    sns.set_theme('poster')
    sns.set_style('whitegrid')
    # sns.color_palette("rocket")

    heatmap_kwargs = {'annot': True, 'fmt': 'g', 'cmap': 'Blues',
                    'cbar': False}
        # annot=True, cmap='Blues', fmt='g'

    num_preds = len(preds)
    fig_case, ax_case = plt.subplots(num_preds, 1, figsize=(11, 6.5*len(preds)))
    fig_num, ax_num = plt.subplots(num_preds, 1, figsize=(6, 3*len(preds)))
    fig_person, ax_person = plt.subplots(num_preds, 1, figsize=(8, 4*len(preds)))

    # fig_num.suptitle(f"Number classification, {model_name}")
    # wrap title
    fig_num.suptitle(f"Number, {model_name}")
    fig_case.suptitle(f"Case classification, {model_name}")
    fig_person.suptitle(f"Poss.suffix classification, {model_name}")

    for i, pred in enumerate(preds):
        aligned = get_aligned(pred, refs)

        num_conf = metrics.confusion_matrix(
            [a[1] for a in aligned], [a[0] for a in aligned], labels=num_labels)
        case_conf = metrics.confusion_matrix(
            [a[3] for a in aligned], [a[2] for a in aligned], labels=case_labels)
        person_conf = metrics.confusion_matrix(
            [a[5] for a in aligned], [a[4] for a in aligned], labels=person_labels)

        # the last row and column are for "other" category
        # the reference should never be "other"
        assert num_conf[-1, :].sum() == 0
        assert case_conf[-1, :].sum() == 0
        assert person_conf[-1, :].sum() == 0
        # remove the last row
        num_conf = num_conf[:-1, :]
        case_conf = case_conf[:-1, :]
        person_conf = person_conf[:-1, :]

        sns.heatmap(num_conf, ax=ax_num[i], **heatmap_kwargs)
        ax_num[i].set_title(f"{shots[i]}-shot")
        ax_num[i].set_yticklabels(ref_num_labels, rotation=0)
        ax_num[i].set_xticklabels(num_labels, rotation=90)
        ax_num[i].set_ylabel("True label")
        ax_num[i].set_xlabel("Predicted label")

        sns.heatmap(case_conf, ax=ax_case[i], **heatmap_kwargs)
        ax_case[i].set_title(f"{shots[i]}-shot")
        ax_case[i].set_yticklabels(ref_case_labels, rotation=0)
        ax_case[i].set_xticklabels(case_labels, rotation=90)
        ax_case[i].set_ylabel("True label")
        ax_case[i].set_xlabel("Predicted label")

        sns.heatmap(person_conf, ax=ax_person[i], **heatmap_kwargs)
        ax_person[i].set_title(f"{shots[i]}-shot")
        ax_person[i].set_yticklabels(ref_person_labels, rotation=0)
        ax_person[i].set_xticklabels(person_labels, rotation=90)
        ax_person[i].set_ylabel("True label")
        ax_person[i].set_xlabel("Predicted label")

        # remove x tick labels for all but the last one
        if i < num_preds - 1:
            ax_num[i].set_xticklabels([])
            ax_case[i].set_xticklabels([])
            ax_person[i].set_xticklabels([])
        # remove x labels for all but the last one
        if i < num_preds - 1:
            ax_num[i].set_xlabel("")
            ax_case[i].set_xlabel("")
            ax_person[i].set_xlabel("")

    fig_num.tight_layout()
    fig_case.tight_layout()
    fig_person.tight_layout()

    fig_num.savefig(output_file + "_num.png")
    fig_case.savefig(output_file + "_case.png")
    fig_person.savefig(output_file + "_person.png")



def two_case_confusion_mats(preds1, refs1, preds2, refs2, output_file):
    """Plot confusion matrices for the three categories."""

    aligned = get_aligned(preds1, refs1)
    aligned2 = get_aligned(preds2, refs2)

    case_labels = list(set(CASE_LABELS.values()))
    case_labels.remove("other")
    case_labels.sort()
    case_labels.append("other")

    case_conf1 = metrics.confusion_matrix(
        [a[3] for a in aligned], [a[2] for a in aligned], labels=case_labels)
    case_conf2 = metrics.confusion_matrix(
        [a[3] for a in aligned2], [a[2] for a in aligned2], labels=case_labels)
    

    # the last row and column are for "other" category
    # the reference should never be "other"
    assert case_conf1[-1, :].sum() == 0
    assert case_conf2[-1, :].sum() == 0
    # remove the last row
    case_conf1 = case_conf1[:-1, :]
    case_conf2 = case_conf2[:-1, :]
    # fix the tics
    ref_case_labels = [label for label in case_labels if label != "other"]


    import matplotlib.pyplot as plt
    import seaborn as sns

    # set style for the plots
    sns.set_theme('poster')
    sns.set_style('whitegrid')
    # sns.color_palette("rocket")

    heatmap_kwargs = {'annot': True, 'fmt': 'g', 'cmap': 'Blues',
                      'cbar': False}
        # annot=True, cmap='Blues', fmt='g'

    _, ax = plt.subplots(2, 1, figsize=(11, 13))

    print(ref_case_labels, case_labels)
    # exit()

    sns.heatmap(case_conf1, ax=ax[0], **heatmap_kwargs)
    ax[0].set_title("Case classification, GPT-4-turbo, 0-shot")
    ax[0].set_yticklabels(ref_case_labels, rotation=0)
    ax[0].set_xticklabels(case_labels, rotation=90)
    ax[0].set_ylabel("True label")
    ax[0].set_xlabel("Predicted label")

    sns.heatmap(case_conf2, ax=ax[1], **heatmap_kwargs)
    ax[1].set_title("Case classification, GPT-4-turbo, 10-shot")
    ax[1].set_yticklabels(ref_case_labels, rotation=0)
    ax[1].set_xticklabels(case_labels, rotation=90)
    ax[1].set_ylabel("True label")
    ax[1].set_xlabel("Predicted label")


    plt.tight_layout()

    plt.savefig(output_file)


def confusion_mats(preds, refs, output_file):
    """Plot confusion matrices for the three categories."""

    aligned = get_aligned(preds, refs)

    num_labels = ["SG", "PL", "other"]
    case_labels = list(set(CASE_LABELS.values()))
    case_labels.remove("other")
    case_labels.sort()
    case_labels.append("other")
    person_labels = ["SG1", "SG2", "PL1", "PL2", "3", "other"]

    num_conf = metrics.confusion_matrix(
        [a[1] for a in aligned], [a[0] for a in aligned], labels=num_labels)
    case_conf = metrics.confusion_matrix(
        [a[3] for a in aligned], [a[2] for a in aligned], labels=case_labels)
    person_conf = metrics.confusion_matrix(
        [a[5] for a in aligned], [a[4] for a in aligned], labels=person_labels)

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
    ref_num_labels = [label for label in num_labels if label != "other"]
    ref_case_labels = [label for label in case_labels if label != "other"]
    ref_person_labels = [label for label in person_labels if label != "other"]

    print(num_conf)
    print(case_conf)
    print(person_conf)

    import matplotlib.pyplot as plt
    import seaborn as sns

    # set style for the plots
    sns.set_theme('poster')
    sns.set_style('whitegrid')
    # sns.color_palette("rocket")

    heatmap_kwargs = {'annot': True, 'fmt': 'g', 'cmap': 'Blues',
                      'cbar': False}
        # annot=True, cmap='Blues', fmt='g'
    
    # _, ax = plt.subplots(2, 1, figsize=(9, 18))
    
    # print(case_conf)
    # print(ref_case_labels, case_labels)
    # # exit()

    # sns.heatmap(case_conf, ax=ax[0], **heatmap_kwargs)
    # ax[0].set_title("Case")
    # ax[0].set_yticklabels(ref_case_labels, rotation=0)
    # ax[0].set_xticklabels(case_labels, rotation=90)
    # ax[0].set_ylabel("True label")
    # ax[0].set_xlabel("Predicted label")
    # # remove the bar
    # # ax.collections[0].colorbar.remove()

    # plt.tight_layout()

    # plt.savefig(output_file)


    _, ax = plt.subplots(1, 3, figsize=(40, 11))

    sns.heatmap(num_conf, ax=ax[0], **heatmap_kwargs)
    ax[0].set_title("Number")
    ax[0].set_yticklabels(ref_num_labels, rotation=0)
    ax[0].set_xticklabels(num_labels, rotation=90)
    ax[0].set_ylabel("True label")
    ax[0].set_xlabel("Predicted label")


    sns.heatmap(case_conf, ax=ax[1], **heatmap_kwargs)
    ax[1].set_title("Case")
    ax[1].set_yticklabels(ref_case_labels, rotation=0)
    ax[1].set_xticklabels(case_labels, rotation=90)
    ax[1].set_ylabel("True label")
    ax[1].set_xlabel("Predicted label")


    sns.heatmap(person_conf, ax=ax[2], **heatmap_kwargs)
    ax[2].set_title("Person")
    ax[2].set_yticklabels(ref_person_labels, rotation=0)
    ax[2].set_xticklabels(person_labels, rotation=90)
    ax[2].set_ylabel("True label")
    ax[2].set_xlabel("Predicted label")
    
    plt.tight_layout()

    plt.savefig(output_file)

    # exit()
    
    # _, ax = plt.subplots(1, 1, figsize=(10, 10))

    # print(ref_case_labels)

    # sns.heatmap(case_conf, ax=ax, **heatmap_kwargs)
    # ax.set_title("Case")
    # ax.set_yticklabels(ref_case_labels, rotation=0)
    # ax.set_xticklabels(case_labels, rotation=90)
    # ax.set_ylabel("True label")
    # ax.set_xlabel("Predicted label")
    # # remove the bar
    # ax.collections[0].colorbar.remove()

    # plt.tight_layout()

    # plt.savefig(output_file)



def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--preds", help="files with predictions", type=str, nargs='+')
    parser.add_argument("--preds-include-prompt", action="store_true",
                        help="the preds include the prompt, so it should be removed")
    parser.add_argument("--prompts", help="files with prompts", type=str, nargs='+')
    parser.add_argument("--refs", help="files with references", type=str)
    parser.add_argument("--lemma-freq-file", help="file with lemma frequencies")
    parser.add_argument("--form-freq-file", help="file with form frequencies")
    parser.add_argument("--form-freq-from-corpus-file",
                        help="file with form frequencies from corpus")
    parser.add_argument("--feats-freq-file", help="file with feature frequencies")
    parser.add_argument("--eval-type",
                        help="evaluation type",
                        choices=["accuracy", "acc-wrt-freq", "confusion",
                                 "many-confusions", "f1-scores"], default="accuracy")
    parser.add_argument("--out", help="output file")
    parser.add_argument("--refs-range", type=str, help="range of references to use")
    parser.add_argument("--cot", type=str, help="check only the last line of the prediction", nargs='?', const='')
    parser.add_argument("--samples", type=str, help="samples to check")
    args = parser.parse_args()

    if args.eval_type == "many-confusions":
        # preds_file1, preds_file2 = args.preds
        # preds1, refs1, _ = read_files(preds_file1, args.refs, args.prompts)
        # preds2, refs2, _ = read_files(preds_file2, args.refs, args.prompts)
        # normalised_preds1 = [normalise_preds(pred, sample=None, last_line=False) for pred in preds1]
        # normalised_refs1 = [normalise_refs(ref) for ref in refs1]
        # normalised_preds2 = [normalise_preds(pred, sample=None, last_line=False) for pred in preds2]
        # normalised_refs2 = [normalise_refs(ref) for ref in refs2]
        # two_case_confusion_mats(normalised_preds1, normalised_refs1, normalised_preds2, normalised_refs2, args.out)

        norm_preds = []
        shots = []
        if not args.prompts:
            args.prompts = [None] * len(args.preds)
        for preds_file, prompts_file in zip(args.preds, args.prompts):
            model_name, shot = parse_pred_file_name(preds_file)
            shots.append(shot)
            preds, refs, prompts = read_files(preds_file, args.refs, prompts_file)

            if prompts: # remove the prompt from the predictions
                assert len(prompts) == len(refs), "Number of prompts and refs should be the same"
                if args.preds_include_prompt:
                    preds = [pred[len(prompt):] for pred, prompt in zip(preds, prompts)]

            norm_preds.append([normalise_preds(pred, sample=None, last_line=False) for pred in preds])
            normalised_refs = [normalise_refs(ref) for ref in refs]

        many_confusion_mats(norm_preds, normalised_refs, args.out, shots, model_name)
        return

    if args.refs_range:
        args.refs_range = [int(i) for i in args.refs_range.split("-")]

    if len(args.preds) > 1:
        raise ValueError("Only one prediction file allowed for this evaluation type")
    preds = args.preds[0]
    prompts = args.prompts[0] if args.prompts else None
    preds, refs, prompts = read_files(
        preds, args.refs, prompts, refs_range=args.refs_range)

    if prompts: # remove the prompt from the predictions
        assert len(prompts) == len(refs), "Number of prompts and refs should be the same"
        if args.preds_include_prompt:
            preds = [pred[len(prompt):] for pred, prompt in zip(preds, prompts)]

    cot = bool(args.cot)
    if args.samples:
        with open(args.samples, "r", encoding="utf-8") as f:
            samples = json.load(f)
        normalised_preds = [normalise_preds(pred, sample=sample, last_line=cot) for pred, sample in zip(preds, samples)]
    else:
        normalised_preds = [normalise_preds(pred, sample=None, last_line=cot) for pred in preds]
    normalised_refs = [normalise_refs(ref) for ref in refs]

    # print the samples that are not exact matches for the person
    # for sample, ref, pred, pred_raw in zip(samples, normalised_refs, normalised_preds, preds):
    #     if not check_exact_match(pred, ref)[0][2]:
    #         print(f"sample: {sample}")
    #         print(f"ref: {ref}")
    #         print(f"pred: {pred}")
    #         print(f"pred_raw: {pred_raw}")
    #         print()



    if args.eval_type == "confusion": # plot confusion matrices
        confusion_mats(normalised_preds, normalised_refs, args.out)
        return

    if args.eval_type == "f1-scores":
        f1_scores = get_f1_scores(normalised_preds, normalised_refs)
        result_string = f"Number: {f1_scores[0]}\n" \
        + f"Case: {f1_scores[1]}\n" \
        + f"Person: {f1_scores[2]}\n"
    elif args.eval_type == "accuracy":
        results = get_avg_accuracies(normalised_preds, normalised_refs)
        result_string = f"Number: {results['num'] / len(refs)}\n" \
        + f"Case: {results['case'] / len(refs)}\n" \
        + f"Person: {results['person'] / len(refs)}\n" \
        + f"Complete: {results['complete'] / len(refs)}\n"

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(result_string)
    else:
        print(result_string)

    if args.eval_type == "acc-wrt-freq":

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
