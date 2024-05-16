
with open('data/fairseq/rnn-results/results_random100000_person_random2000.txt', 'r', encoding='utf-8') as f:
    answers = f.read().split('####################################################')[1]
persons = [int(l.split()[0]) for l in answers.split('\n') if l.strip()]

with open('data/fairseq/rnn-results/results_random100000_case_random2000.txt', 'r', encoding='utf-8') as f:
    answers = f.read().split('####################################################')[1]
cases = [int(l.split()[0]) for l in answers.split('\n') if l.strip()]

with open('data/fairseq/rnn-results/results_random100000_number_random2000.txt', 'r', encoding='utf-8') as f:
    answers = f.read().split('####################################################')[1]
numbers = [int(l.split()[0]) for l in answers.split('\n') if l.strip()]

if not len(persons) == len(cases) == len(numbers):
    print("Lengths of the lists are not equal")
    print(len(persons), len(cases), len(numbers))
    exit()

check_all_correct = [p and c and n for p, c, n in zip(persons, cases, numbers)]
print(sum(check_all_correct) / len(check_all_correct))
