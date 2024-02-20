import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("input_files", help="input files", nargs="+", type=str)
parser.add_argument("output_file", help="output file", type=str)
parser.add_argument("batch_size", type=int, default=16)
args = parser.parse_args()

inputs = []
for file in args.input_files:
    with open(file, "r", encoding="utf-8") as f:
        inputs.append(f.read())

# write to files in batches
for i in range(0, len(inputs), args.batch_size):
    with open(f"{args.output_file}_{i}.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(inputs[i:i+args.batch_size]))

# with open(args.output_file, "w", encoding="utf-8") as f:
#     f.write(json.dumps(inputs))
