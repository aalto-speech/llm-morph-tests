import argparse
from os import path, makedirs
from common import parse_omorstring, FIN_FEATS_CLASSES
import torch


def omorstring2class(omstr, classtype="person"):
    """Parse the omorstring and return the class."""
    parsed = parse_omorstring(omstr)
    if classtype in parsed:
        return FIN_FEATS_CLASSES[classtype][parsed[classtype]]


def inflected2fairseq(inflected, output_dir, clstype="person"):
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

        for i, inflected_line in enumerate(inflected):
            if i % 10 == 0:
                output = test_input
                output_label = test_output
            elif i % 10 == 1:
                output = valid_input
                output_label = valid_output
            else:
                output = train_input
                output_label = train_output

            wordform, omstr = inflected_line.strip().split(":")

            # Write the wordform with spaces between characters
            output.write(f"{' '.join(list(wordform))}\n")

            label = omorstring2class(omstr, clstype)
            if label is None:
                label = "none"
            output_label.write(f"{label}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inflected-words", type=str,
                        help="Path to a file with omorstrings and inflected words")
    parser.add_argument("--classtype", type=str, default="person",)
    parser.add_argument("--output-dir", type=str, help="Output directory")
    args = parser.parse_args()

    if not path.isdir(args.output_dir):
        print(f"Creating directory {args.output_dir}")
        makedirs(args.output_dir)

    with open(args.inflected_words, "r", encoding="utf-8") as f:
        inflected = f.readlines()

    inflected2fairseq(inflected, args.output_dir, args.classtype)
