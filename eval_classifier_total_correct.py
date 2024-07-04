
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        answers = f.read().split('####################################################')[1]
    try:
        output = [int(l.split()[0]) for l in answers.split('\n') if l.strip()]
    except:
        print(filename)
        exit()
    return output


for dataset_size in ['1000', '5000', '10000', '50000', '100000']:

    persons = read_file(f'data/fairseq/rnn-results/results_random{dataset_size}_person_random2000_new.txt')
    cases = read_file(f'data/fairseq/rnn-results/results_random{dataset_size}_case_random2000_new.txt')
    numbers = read_file(f'data/fairseq/rnn-results/results_random{dataset_size}_number_random2000_new.txt')

    if not len(persons) == len(cases) == len(numbers):
        print("Lengths of the lists are not equal")
        print(len(persons), len(cases), len(numbers))
        exit()

    print(f"Results for dataset size {dataset_size}")
    check_all_correct = [p and c and n for p, c, n in zip(persons, cases, numbers)]
    print(sum(check_all_correct) / len(check_all_correct))
