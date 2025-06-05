import csv
import json

def convert_csv_to_json():
    problems = []
    
    with open('50 Problems for Beta Version.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        first_row = next(reader)
        print('CSV Keys:', list(first_row.keys()))  # Debug print
        csvfile.seek(0)
        reader = csv.DictReader(csvfile)
        for row in reader:
            problem = {
                "number": row['\ufeff#'],  # Use BOM-prefixed key
                "category": row['Category'],
                "question": row['Question'],
                "media": row['Files & media'],  # Updated column name
                "choices": [
                    row['A'],
                    row['B'],
                    row['C'],
                    row['D']
                ],
                "correct_answer": row['Answer']
            }
            problems.append(problem)
    
    # Write to JSON file
    with open('problems_database.json', 'w', encoding='utf-8') as jsonfile:
        json.dump({"problems": problems}, jsonfile, indent=4)

if __name__ == "__main__":
    convert_csv_to_json() 