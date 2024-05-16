import argparse
from os import path, makedirs
from common import parse_omorstring, FIN_FEATS_CLASSES
# import torch
import json


def omorstring2class(omstr, classtype="person"):
    """Parse the omorstring and return the class."""
    parsed = parse_omorstring(omstr)
    if classtype in parsed:
        return FIN_FEATS_CLASSES[classtype][parsed[classtype]]


def inflected2fairseq(wordforms, omorstrings, output_dir, clstype="person",
                      train_valid_test_sizes=[0.8, 0.1, 0.1]):
    """Parse the omorstrings and write train, valid and test files for fairseq."""
    train_input_file = path.join(output_dir, "train.input")
    valid_input_file = path.join(output_dir, "valid.input")
    test_input_file = path.join(output_dir, "test.input")
    train_output_file = path.join(output_dir, f"train.{clstype}")
    valid_output_file = path.join(output_dir, f"valid.{clstype}")
    test_output_file = path.join(output_dir, f"test.{clstype}")

    with open(train_input_file, "w", encoding="utf-8") as train_input, \
            open(valid_input_file, "w", encoding="utf-8") as valid_input, \
            open(test_input_file, "w", encoding="utf-8") as test_input, \
            open(train_output_file, "w", encoding="utf-8") as train_output, \
            open(valid_output_file, "w", encoding="utf-8") as valid_output, \
            open(test_output_file, "w", encoding="utf-8") as test_output:

        train_size = train_valid_test_sizes[0] * len(wordforms)
        valid_size = train_valid_test_sizes[1] * len(wordforms)
        for i, w in enumerate(wordforms):
            if i < train_size:
                output = train_input
                output_label = train_output
            elif i < train_size + valid_size:
                output = valid_input
                output_label = valid_output
            else:
                output = test_input
                output_label = test_output

            # Write the wordform with spaces between characters
            output.write(f"{' '.join(list(w))}\n")

            label = omorstring2class(omorstrings[i], clstype)
            if label is None:
                label = "none"
            output_label.write(f"{label}\n")


parser = argparse.ArgumentParser()
parser.add_argument("--inflected-words", type=str,
                    help="Path to a file with omorstrings and inflected words")
parser.add_argument("--omorstrings-json", type=str,
                    help="Path to a file with omorstrings json file")
parser.add_argument("--wordforms-json", type=str,
                    help="Path to a file with wordforms json file")
parser.add_argument("--classtype", type=str, default="person",)
parser.add_argument("--train-valid-test-split", type=str, default="80-10-10")
parser.add_argument("--output-dir", type=str, help="Output directory")
args = parser.parse_args()

train_valid_test_sizes = [float(s)/100.0 for s in args.train_valid_test_split.split("-")]
print(f"Train-valid-test sizes: {train_valid_test_sizes}")

if not path.isdir(args.output_dir):
    print(f"Creating directory {args.output_dir}")
    makedirs(args.output_dir)

wordforms = []
omrstrings = []
if args.inflected_words:
    with open(args.inflected_words, "r", encoding="utf-8") as f:
        inflected = f.readlines()

    for inflected_line in inflected:
        try:
            wordform, omstr = inflected_line.strip().split(":")
        except ValueError:
            print(f"Error: {inflected_line} does not contain exactly 1 colon")
            continue
        wordforms.append(wordform)
        omrstrings.append(omstr)

elif args.omorstrings_json and args.wordforms_json:
    with open(args.omorstrings_json, "r", encoding="utf-8") as f:
        omrstrings = json.load(f)
    with open(args.wordforms_json, "r", encoding="utf-8") as f:
        wordforms = [w.split('--')[0].strip() for w in json.load(f)]

inflected2fairseq(wordforms, omrstrings, args.output_dir, args.classtype, train_valid_test_sizes)
