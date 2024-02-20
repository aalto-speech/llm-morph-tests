import argparse
import ast

parser = argparse.ArgumentParser()
parser.add_argument("--preds", help="files with predictions", nargs="+")
parser.add_argument("--refs", help="files with references", nargs="+")
parser.add_argument("--out", help="output file")
args = parser.parse_args()

preds = []
for file in args.preds:
    with open(file, "r", encoding="utf-8") as f:
        preds += ast.literal_eval(f.readlines()[-1])

refs = []
for file in args.refs:
    with open(file, "r", encoding="utf-8") as f:
        refs += ast.literal_eval(f.read())
# print(preds, '\n\n', refs)

assert len(preds) == len(refs), "Number of predictions and references should be the same"

# there are some refs with multiple identical lines
# for ref in refs:
#     print(ref)
# exit() 

correct_num = 0
correct_case = 0
correct_person = 0
correct = 0
for pred, ref in zip(preds, refs):
    (ref_num, ref_case, ref_person) = [i.strip() for i in ref.split(',')[:3]]
    (pred_num, pred_case, pred_person) = [i.strip() for i in pred.split(',')[:3]]

    if pred_num == ref_num:
        correct_num += 1
    if pred_case == ref_case:
        correct_case += 1

    person = False
    if pred_person == ref_person:
        person = True
    # if pred includes "kolmas persoona" and ref includes "kolmas persoona":
    elif ref_person == "kolmas persoona" and "kolmas persoona" in pred:
        person = True
    if person:
        correct_person += 1

    if pred_num == ref_num and pred_case == ref_case and person:
        correct += 1

with open(args.out, "w", encoding="utf-8") as f:
    f.write(f"Number: {correct_num / len(refs)}\n")
    f.write(f"Case: {correct_case / len(refs)}\n")
    f.write(f"Person: {correct_person / len(refs)}\n")
    f.write(f"Completely correct: {correct / len(refs)}\n") 
