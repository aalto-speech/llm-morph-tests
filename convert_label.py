import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input", help="label")
parser.add_argument("mapping", help="file with mapping of labels: map first column to second")
args = parser.parse_args()

with open(args.mapping, "r", encoding="utf-8") as f:
    try:
        lines = {l.split('-')[0].strip(): l.split('-')[1].strip() for l in f.readlines()}
    except IndexError:
        print("Error: mapping file should have >= two columns separated by -", f.readlines())
        exit(1)

print(lines[args.input])
