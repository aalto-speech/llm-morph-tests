import json
import glob
import numpy as np

print('Finbench avg results:')
for model in glob.glob('evaluation/*/*'):
    with open(f'{model}/finbench_3shot.json', 'r') as f:
        finbench = json.load(f)

    avg = np.mean([r['multiple_choice_grade'] for r in finbench['results'].values()])
    print(f'{model}: {avg}')
