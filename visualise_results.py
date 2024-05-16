

def parse_result_file_name(file_name):
    """Parse the result file name to get the model name and prompt type.
    e.g. results_1shot_gpt3.5-turbo_0-1000_newparsing.txt
    """
    parts = file_name.split('_')
    if parts[2] == 'llama2':
        return int(parts[1].split('shot')[0]), f'{parts[2]}-{parts[3].replace(".txt", "")}'
    return int(parts[1].split('shot')[0]), parts[2]


def read_results_file(results_file):
    with open(results_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return {line.split(':')[0].strip(): float(line.split(':')[1].strip()) for line in lines}


if __name__ == '__main__':
    import argparse
    import matplotlib.pyplot as plt
    import seaborn as sns

    parser = argparse.ArgumentParser()
    parser.add_argument('--result-files',  nargs='*', type=str, required=True)
    parser.add_argument('--output', type=str, default='figures/untitled.png')
    # parser.add_argument('--type', type=str, required=True)
    args = parser.parse_args()

    # Load the data
    data = {}
    for file in args.result_files:
        prompttype, model = parse_result_file_name(file)
        if model not in data:
            data[model] = {}
        data[model][prompttype] = read_results_file(file)

    print(data)

    results_per_model_and_category = {}
    for model, results in data.items():
        results_per_model_and_category[model] = {}
        for prompttype, result in results.items():
            for resulttype in result:
                if resulttype not in results_per_model_and_category[model]:
                    results_per_model_and_category[model][resulttype] = {}
                results_per_model_and_category[model][resulttype][prompttype] = result[resulttype]

    print(results_per_model_and_category)

    # Plot the results as a function of the prompttype int
    fig, ax = plt.subplots()
    for model, results_per_category in results_per_model_and_category.items():
        # x is prompttype, y is accuracy

        # set color palette
        # if 'gpt3.5-turbo' in model:
        #     color_palette = sns.color_palette("rocket", 4)
        # else:
        #     color_palette = sns.color_palette("Blues", 4)

        # for category, results in results_per_category.items():
        category = 'Complete'
        # sort the results by prompttype
        results = dict(sorted(results_per_category['Complete'].items()))
        x = list(results.keys())
        y = list(results.values())
        ax.plot(x, y, label=model,
                # color=color_palette.pop(0),
                marker='o')
    ax.set_xticks(x)
    ax.set_xticklabels(x)
    # y from 0 to 1
    ax.set_ylim(-0.1, 1)
    
    # figure size
    fig.set_size_inches(5, 6)
    
            
            
            
    ax.set_xlabel('Prompt type')
    ax.set_ylabel('Accuracy')
    ax.legend()
    plt.savefig(args.output)
    
        
