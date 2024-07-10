
def parse_result_file_name(file_name):
    """Parse the result file name to get the model name and prompt type.
    e.g. results_1shot_gpt3.5-turbo_0-1000_newparsing.txt
    """
    parts = file_name.split('_')
    if parts[2] == 'llama2':
        return int(parts[1].split('shot')[0]), f'{parts[2]}_{parts[3].replace(".txt", "")}'
    return int(parts[1].split('shot')[0]), parts[2]


def parse_rnn_result_file_name(file_name):
    """Parse the result file name to get the train size, type and test set.
    format results_random<train_size>_<type>_<test_set>.txt
    """
    parts = file_name.split('_')
    return int(parts[1].replace('random', '')), parts[2], parts[3].replace('.txt', '')


def read_results_file(results_file):
    with open(results_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return {line.split(':')[0].strip(): float(line.split(':')[1].strip()) for line in lines}


def read_rnn_results_file(results_file):
    with open(results_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        if 'Accuracy' in line:
            return float(line.split(':')[1].strip())

def multiplot():

    # Load the data
    data = {}
    for file in args.result_files:
        prompttype, model = parse_result_file_name(file)
        if model not in data:
            data[model] = {}
        data[model][prompttype] = read_results_file(file)

    # rearrange to a dict
    results_per_category_per_model_per_shot = {}
    for model, shot_resulttype in data.items():
        for shot, resulttype_result in shot_resulttype.items():
            for resulttype, result in resulttype_result.items():
                if resulttype not in results_per_category_per_model_per_shot:
                    results_per_category_per_model_per_shot[resulttype] = {}
                if model not in results_per_category_per_model_per_shot[resulttype]:
                    results_per_category_per_model_per_shot[resulttype][model] = {}
                results_per_category_per_model_per_shot[resulttype][model][shot] = result
    # print(results_per_category_per_model_per_shot)

    fig, axs = plt.subplots(1, 4, sharex=True) # ,gridspec_kw={'height_ratios': [2, 1.5, 0.5]})
    category_names = {
        'Person': 'Possessive suffix',
        'Case': 'Case',
        'Number': 'Number',
        'Complete': 'Combined'
        }

    # RNN results
    rnn_results = {}
    with open('rnn-results/total_results.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    rnn_results['Complete'] = float([line for line in lines if line.strip()][-1])
    rnn_results['Person'] = read_rnn_results_file('rnn-results/results_random100000_person_random2000_new.txt')
    rnn_results['Case'] = read_rnn_results_file('rnn-results/results_random100000_case_random2000_new.txt')
    rnn_results['Number'] = read_rnn_results_file('rnn-results/results_random100000_number_random2000_new.txt')

    # random baseline results
    from random_guess_baseline import get_results
    random_results = get_results()


    for i, (category, results_per_model_per_shot) in enumerate(results_per_category_per_model_per_shot.items()):

        color_palette = sns.color_palette('deep', 6)
        markers = ['o', 's', 'D', '^']

        for model in ['gpt4-turbo', 'gpt3.5-turbo', 'llama2_70b', 'poro']:

            model_results = results_per_model_per_shot[model]
            model = model.replace('gpt3.5-turbo', 'GPT-3.5-turbo')
            model = model.replace('gpt4-turbo', 'GPT-4-turbo')
            model = model.replace('llama2_70b', 'Llama2-70B')
            model = model.replace('poro', 'Poro-34B')

            results = dict(sorted(model_results.items()))
            x = list(results.keys())
            y = list(results.values())
            sns.lineplot(
                x=x,
                y=y,
                label=model,
                color=color_palette.pop(0),
                marker=markers.pop(0),
                ax=axs[i],
                )
            axs[i].get_legend().remove()
            axs[i].set_xticks(x)
            axs[i].set_xticklabels(x)
            axs[i].set_ylim(-0.05, 1.05)
            axs[i].set_title(category_names[category])

        # RNN results
        x = [0,10]
        y = [rnn_results[category], rnn_results[category]]
        axs[i].plot(x, y, label='RNN 80k',
                color=color_palette.pop(0),
                linestyle='--')
        # Random guess baseline results
        y = [random_results[category.lower()], random_results[category.lower()]]
        axs[i].plot(x, y, label='Random guess',
                color=color_palette.pop(0),
                linestyle=':')


        fig.set_size_inches(12, 3.7)
        axs[0].set_ylabel('Accuracy')
        # remove y tics
        axs[1].set_yticks([])
        axs[2].set_yticks([])
        axs[3].set_yticks([])
        
        fig.text(0.5, 0.00, 'Number of examples in prompt', ha='center')
        
        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='lower left') 
        sns.move_legend(fig, 'lower left', bbox_to_anchor=(.15, .11),
                        # title='Model'
                        )

        # plt.tight_layout()
        plt.savefig(args.output , bbox_inches="tight", dpi=500)


if __name__ == '__main__':
    import argparse
    import matplotlib.pyplot as plt
    import seaborn as sns

    parser = argparse.ArgumentParser()
    parser.add_argument('--result-files',  nargs='*', type=str, required=True)
    parser.add_argument('--output', type=str, default='figures/untitled.png')
    parser.add_argument('--resulttype', type=str)
    parser.add_argument('--plottype', type=str, required=True, default='lineplot')
    parser.add_argument('--rnn', action='store_true')
    args = parser.parse_args()

    if args.plottype == 'multiplot':
        multiplot()
