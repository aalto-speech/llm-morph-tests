import argparse
import ast
import json

parser = argparse.ArgumentParser()
parser.add_argument("--preds", help="files with predictions", nargs="+")
parser.add_argument("--preds-include-prompt", action="store_true",
                    help="the preds include the prompt, so it should be removed")
parser.add_argument("--refs", help="files with references", nargs="+")
parser.add_argument("--out", help="output file")
args = parser.parse_args()

preds = []
for file in args.preds:
    with open(file, "r", encoding="utf-8") as f:
        preds += ast.literal_eval(f.readlines()[-1])

if args.preds_include_prompt:
    with open('expts/preliminary/prompts/inputs_0.json', "r", encoding="utf-8") as f:
        prompts = json.load(f)

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
    try:
        (ref_num, ref_case, ref_person) = [i.strip() for i in ref.split(',') if i.strip()][:3]
        (pred_num, pred_case, pred_person) = [i.strip() for i in pred.split(',') if i.strip()][:3]
        pred_person = pred_person.split('\n')[0]
    except:
        print('too few elements in ref or pred')
        continue

    print('pred_num:', pred_num,)
    print('ref_num:', ref_num)
    print('pred_case:', pred_case)
    print('ref_case:', ref_case)
    print('pred_person:', pred_person)
    print('ref_person:', ref_person)
    print()
    # exit()

    if pred_num == ref_num:
        correct_num += 1
    if pred_case == ref_case:
        correct_case += 1

    person = False
    if pred_person.startswith(ref_person):
        person = True
    # if pred includes "kolmas persoona" and ref includes "kolmas persoona":
    elif ref_person == "kolmas persoona" and \
        (pred_person.startswith("yksikön kolmas persoona") or \
         pred_person.startswith("monikon kolmas persoona")):
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
