

def parse_result_file_name(file_name):
    """Parse the result file name to get the model name and prompt type.
    e.g. results_1shot_gpt3.5-turbo_0-1000_newparsing.txt
    """
    parts = file_name.split('_')
    if parts[2] == 'llama2':
        return int(parts[1].split('shot')[0]), f'{parts[2]}-{parts[3].replace(".txt", "")}'
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


if __name__ == '__main__':
    import argparse
    import matplotlib.pyplot as plt
    import seaborn as sns

    parser = argparse.ArgumentParser()
    parser.add_argument('--result-files',  nargs='*', type=str, required=True)
    parser.add_argument('--output', type=str, default='figures/untitled.png')
    parser.add_argument('--resulttype', type=str, required=True)
    parser.add_argument('--rnn', action='store_true')
    args = parser.parse_args()

    if args.rnn:
        # Load the data
        data = {}
        for file in args.result_files:
            train_size, resulttype, test_set = parse_rnn_result_file_name(file)
            if resulttype not in data:
                data[resulttype] = {}
            data[resulttype][train_size] = read_rnn_results_file(file)

        # Plot the results as a function of the prompttype int
        fig, ax = plt.subplots()
        for resulttype, results in data.items():
            # sort the results by key
            results = dict(sorted(results.items()))
            x = list(results.keys())
            y = list(results.values())
            ax.plot(x, y, label=resulttype, marker='o')
        ax.set_xticks(x)
        ax.set_xticklabels(x)
        # y from 0 to 1
        # ax.set_ylim(-0.05, 1)

        # figure size
        fig.set_size_inches(5, 5)

        ax.set_xlabel('Number of examples in training set')
        ax.set_ylabel('Accuracy')
        ax.set_title('Classification accuracy of RNN models')
        ax.legend()
        plt.savefig(args.output)

    else:
        # Load the data
        data = {}
        for file in args.result_files:
            prompttype, model = parse_result_file_name(file)
            if model not in data:
                data[model] = {}
            data[model][prompttype] = read_results_file(file)

        # results_per_model_and_category = {}
        # for model, results in data.items():
        #     results_per_model_and_category[model] = {}
        #     for prompttype, result in results.items():
        #         for resulttype in result:
        #             if resulttype not in results_per_model_and_category[model]:
        #                 results_per_model_and_category[model][resulttype] = {}
        #             results_per_model_and_category[model][resulttype][prompttype] = result[resulttype]

        # print(results_per_model_and_category)
        results_per_category_per_model_per_shot = {}
        for model, shot_resulttype in data.items():
            for shot, resulttype_result in shot_resulttype.items():
                for resulttype, result in resulttype_result.items():
                    if resulttype not in results_per_category_per_model_per_shot:
                        results_per_category_per_model_per_shot[resulttype] = {}
                    if model not in results_per_category_per_model_per_shot[resulttype]:
                        results_per_category_per_model_per_shot[resulttype][model] = {}
                    results_per_category_per_model_per_shot[resulttype][model][shot] = result
        print(results_per_category_per_model_per_shot)

        results_per_model = results_per_category_per_model_per_shot[args.resulttype]


        # four different markers
        markers = ['o', 's', 'D', '^']
        color_palette = sns.color_palette("deep", 6)

        # Plot the results as a function of the prompttype int
        fig, ax = plt.subplots()
        # for model, model_results in results_per_model.items():
        for model in ['gpt4-turbo', 'gpt3.5-turbo', 'llama2-70b', 'poro']:
        # for model in ['llama2-70b', 'llama2-70b-chat', 'llama2-13b', 'llama2-13b-chat', 'llama2-7b']:
            model_results = results_per_model[model]

            model = model.replace('gpt3.5-turbo', 'GPT-3.5-turbo')
            model = model.replace('gpt4-turbo', 'GPT-4-turbo')
            model = model.replace('llama2-70b', 'Llama-70B')
            model = model.replace('poro', 'Poro-34B')


            # x is prompttype, y is accuracy

            # set color palette
            # if 'gpt3.5-turbo' in model:
            #     color_palette = sns.color_palette("rocket", 4)
            # else:
            #     color_palette = sns.color_palette("Blues", 4)

            # for category, results in results_per_category.items():
            # category = 'Complete'
            # sort the results by key
            results = dict(sorted(model_results.items()))
            x = list(results.keys())
            y = list(results.values())
            ax.plot(x, y, label=model,
                    color=color_palette.pop(0),
                    marker=markers.pop(0))
        ax.set_xticks(x)
        ax.set_xticklabels(x)
        # y from 0 to 1
        ax.set_ylim(-0.05, 1)

        # x = [0,10]
        # y = [0.84,0.84]
        # ax.plot(x, y, label='RNN 80k',
        #         color=color_palette.pop(0),
        #         linestyle='--')
        # x = [0,10]
        # y = [0.765,0.765]
        # ax.plot(x, y, label='RNN 4k',
        #         color=color_palette.pop(0),
        #         linestyle='-.')

        # figure size
        fig.set_size_inches(4.5, 4.5)

        ax.set_xlabel('Number of examples in prompt')
        if "f1-scores" in args.result_files[0]:
            ax.set_ylabel('F1-score, micro average')
        else:
            ax.set_ylabel('Accuracy')
        if args.resulttype == 'Person':
            ax.set_title('Possessive suffix')
        else:
            ax.set_title(args.resulttype)
        # ax.set_title(f'Classification accuracy of {args.resulttype} classes')
        ax.legend()

        plt.tight_layout()
        plt.savefig(args.output)
