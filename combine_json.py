import json
import argparse
import os

def combine_jsonl(jsonl_files, output_file):
    all_lines = []
    for jsonl_file in jsonl_files:
        if 'completions' in jsonl_file:
            with open(jsonl_file, 'r', encoding='utf-8') as infile:
                jsonlist = json.load(infile)
                for item in jsonlist[:-1]:
                    all_lines.append(item['choices'][0]['message']['content'])
                    # print(item['choices'][0]['message']['content'])
                    # exit()
        else:
            with open(jsonl_file, 'r', encoding='utf-8') as infile:
                all_lines += json.load(infile)
    
    print(len(all_lines))
    
    # check that the output file doesn't exist
    if output_file and os.path.isfile(output_file):
        print(f"Error: file {output_file} already exists")
        exit(1)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(all_lines, outfile, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_files', nargs='+', help='List of jsonl files to combine')
    parser.add_argument('--output_file', help='Output file')
    args = parser.parse_args()

    combine_jsonl(args.json_files, args.output_file)

    