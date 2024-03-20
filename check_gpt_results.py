with open('gpt-4-10samples.txt', 'r', encoding='utf-8') as f:
    preds = f.readlines()

import json
with open('expts/prelim3000/data/prompts_1shot.json', 'r', encoding='utf-8') as f:
    refs = json.load(f)[:10]
    

corr_num = 0
corr_person = 0
corr_case = 0
for p, r in zip(preds, refs):
    print(f"Pred: {p.strip()}\nRef: {r}\n\n")
    pred_split = [i.strip() for i in p.split(',') if i]
    ref_split = [i.strip() for i in r.split(',') if i]
    if pred_split[0] == ref_split[0]:
        corr_num += 1
    if pred_split[1] == ref_split[1]:
        corr_case += 1
    if pred_split[2] == ref_split[2]:
        corr_person += 1
print(f"Num: {corr_num/10}, Person: {corr_person/10}, Case: {corr_case/10}")
