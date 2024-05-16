# import os
from fairseq import checkpoint_utils, data, options, tasks

# Parse command-line arguments for generation
parser = options.get_generation_parser(default_task='simple_classification')
args = options.parse_args_and_arch(parser)

# Setup task
task = tasks.setup_task(args)

# Load model
print(f'| loading model from {args.path}')
models, _model_args = checkpoint_utils.load_model_ensemble([args.path], task=task)
model = models[0]

# prefix = os.path.join(args.data, f'test.input-{args.target_lang}')

all_preds = []
# with open(prefix + '.input', encoding='utf-8') as file:
with open(args.test_set + '.input', encoding='utf-8') as file:
    for line in file:
        sentence = line.strip()

        # Tokenize into characters
        # chars = ' '.join(list(sentence.strip()))
        tokens = task.source_dictionary.encode_line(
            sentence, add_if_not_exist=False,
        )

        # Build mini-batch to feed to the model
        batch = data.language_pair_dataset.collate(
            samples=[{'id': -1, 'source': tokens}],  # bsz = 1
            pad_idx=task.source_dictionary.pad(),
            eos_idx=task.source_dictionary.eos(),
            left_pad_source=False,
            input_feeding=False,
        )

        # Feed batch to the model and get predictions
        preds = model(**batch['net_input'])

        # Print top 3 predictions and their log-probabilities
        top_scores, top_labels = preds[0].topk(k=3)
        # for score, label_idx in zip(top_scores, top_labels):
        #     label_name = task.target_dictionary.string([label_idx])
        #     print('({:.2f})\t{}'.format(score, label_name))

        # get the top prediction 
        all_preds.append(task.target_dictionary.string([top_labels[0]]))

# with open(prefix + f'.{args.target_lang}', 'r', encoding="utf-8") as f:
with open(args.test_set + f'.{args.target_lang}', 'r', encoding="utf-8") as f:
    labels = [l.strip() for l in f.readlines()]

correct = 0
for pred, label in zip(all_preds, labels):
    if pred == label:
        correct += 1

print(f"Accuracy: {correct / len(labels)}")

print('####################################################')
for pred, label in zip(all_preds, labels):
    print(int(pred == label), pred, label)
