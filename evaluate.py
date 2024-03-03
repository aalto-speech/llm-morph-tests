import argparse
import ast
import json

def read_preds_and_refs(pred_files, ref_files):
    preds = []
    for file in pred_files:
        with open(file, "r", encoding="utf-8") as f:
            preds += ast.literal_eval(f.readlines()[-1])

    # if args.preds_include_prompt:
    #     with open('expts/preliminary/prompts/inputs_0.json', "r", encoding="utf-8") as f:
    #         prompts = json.load(f)

    refs = []
    for file in ref_files:
        with open(file, "r", encoding="utf-8") as f:
            refs += ast.literal_eval(f.read())

    assert len(preds) == len(refs), "Number of predictions and references should be the same"

    return preds, refs


def parse_answer(answer):
    """Parse the answer into a tuple of (number, case, person)."""
    try:
        return [i.strip() for i in answer.split(',') if i.strip()][:3]
    except ValueError:
        print('too few elements in answer')
        return None


def check_exact_match(pred, ref):
    """Check the exact match for each of the three categories."""

    (ref_num, ref_case, ref_person) = parse_answer(ref)
    (pred_num, pred_case, pred_person) = parse_answer(pred)
    pred_person = pred_person.split('\n')[0]

    results = ( pred_num == ref_num, \
        pred_case == ref_case, \
        pred_person.startswith(ref_person) or \
            (ref_person == "kolmas persoona" and \
            (pred_person.startswith("yksikön kolmas persoona") or \
            pred_person.startswith("monikon kolmas persoona"))))

    print(f"Pred_num: {pred_num}, ref_num: {ref_num}")
    print(f"Pred_case: {pred_case}, ref_case: {ref_case}")
    print(f"Pred_person: {pred_person}, ref_person: {ref_person}")
    print(f"Results: {results}")
    print()
    return results

def get_accuracies(preds, refs):
    """Make a dict of lists of boolean values of whether the prediction is correct"""
    results = {
        'num': 0,
        'case': 0,
        'person': 0,
        'complete': 0
        }

    for pred, ref in zip(preds, refs):
        num_match, case_match, person_match = check_exact_match(pred, ref)
        if num_match:
            results['num'] += 1
        if case_match:
            results['case'] += 1
        if person_match:
            results['person'] += 1
        if num_match and case_match and person_match:
            results['complete'] += 1

    return results


def lemma_frequencies(lemma_freq_file):
    with open(lemma_freq_file, "r", encoding="utf-8") as f:
        lemma_freqs = json.load(f)
    return lemma_freqs


# def accuracy_wrt_freq(accuracies, refs, freqs):
#     """Plot accuracy wrt frequency.
#     Also calculate how much accuracy correlates with frequency."""
    
#     freq2acc = {}
#     for ref in refs:
#         parsed_ref = parse_answer(ref)
#         if parsed_ref is None:
#             continue
#         lemma = parsed_ref[3]
        
        


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--preds", help="files with predictions", nargs="+")
    parser.add_argument("--preds-include-prompt", action="store_true",
                        help="the preds include the prompt, so it should be removed")
    parser.add_argument("--refs", help="files with references", nargs="+")
    parser.add_argument("--lemma-freq-file", help="file with lemma frequencies")
    parser.add_argument("--out", help="output file")
    args = parser.parse_args()


    preds, refs = read_preds_and_refs(args.preds, args.refs)
    results = get_accuracies(preds, refs)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(f"Number: {results['num'] / len(refs)}\n")
        f.write(f"Case: {results['case'] / len(refs)}\n")
        f.write(f"Person: {results['person'] / len(refs)}\n")
        f.write(f"Complete: {results['complete'] / len(refs)}\n")


if __name__ == "__main__":
    main()
