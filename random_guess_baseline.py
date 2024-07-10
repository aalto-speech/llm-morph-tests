"""
Calculates the average accuracy of a random guess baseline in the morphological analysis task.
"""
import argparse
import json
import random
from common import NUM_LABELS, CASE_LABELS, PERSON_LABELS
from evaluate import normalise_refs, get_avg_accuracies

def get_results(refs_file='expts/random2000/data/refs.json'):
                
    with open(refs_file, "r", encoding="utf-8") as f:
        refs = json.load(f)
    normalised_refs = [normalise_refs(ref) for ref in refs]

    NUM_OPTIONS = list(set(NUM_LABELS.values()))
    NUM_OPTIONS.remove("other")

    PERSON_OPTIONS = list(set(PERSON_LABELS.values()))
    PERSON_OPTIONS.remove("other")

    CASE_OPTIONS = list(set(CASE_LABELS.values()))
    CASE_OPTIONS.remove("other")

    num_runs = 100
    all_accuracies = {'num': 0, 'case': 0, 'person': 0, 'complete': 0}
    for i in range(num_runs):
        preds = []
        for i in range(len(normalised_refs)):
            random_num = random.choice(NUM_OPTIONS)
            random_person = random.choice(PERSON_OPTIONS)
            random_case = random.choice(CASE_OPTIONS)
            preds.append((random_num, random_case, random_person))

        accs = get_avg_accuracies(preds, normalised_refs, verbose=False)

        all_accuracies['num'] += accs['num'] / len(normalised_refs)
        all_accuracies['case'] += accs['case'] / len(normalised_refs)
        all_accuracies['person'] += accs['person'] / len(normalised_refs)
        all_accuracies['complete'] += accs['complete'] / len(normalised_refs)

    return {'number': all_accuracies['num'] / num_runs,
            'case': all_accuracies['case'] / num_runs,
            'person': all_accuracies['person'] / num_runs,
            'complete': all_accuracies['complete'] / num_runs}

def print_results(normalised_refs):
    all_accuracies = get_results(normalised_refs)
    print("Random guess baseline:")
    print("Number accuracy: {:.2f}%".format(all_accuracies['num'] * 100))
    print("Case accuracy: {:.2f}%".format(all_accuracies['case'] * 100))
    print("Person accuracy: {:.2f}%".format(all_accuracies['person'] * 100))
    print("Complete accuracy: {:.2f}%".format(all_accuracies['complete'] * 100))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refs", help="file with references", type=str)
    args = parser.parse_args()

    print_results(args.refs)
