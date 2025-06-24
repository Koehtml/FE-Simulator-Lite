import json
import argparse

parser = argparse.ArgumentParser(description='Adjust media_size for all problems in problems_database.json.')
parser.add_argument('--size', type=int, default=40, help='Desired media_size value (default: 100)')
args = parser.parse_args()

with open('problems_database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for problem in data["problems"]:
    problem["media_size"] = args.size

with open('problems_database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Set all problems\' media_size to {args.size}.') 