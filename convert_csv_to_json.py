import csv
import json
import re

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Remove any problematic characters and normalize whitespace
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    return text

def convert_csv_to_json():
    problems = []
    
    with open('50 Problems for Beta Version.csv', 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Clean up the media filename
            media = clean_text(row['Files & media'])
            
            # Clean up the question text
            question = clean_text(row['Question'])
            
            # Clean up choices
            choices = [clean_text(choice) for choice in [row['A'], row['B'], row['C'], row['D']]]
            
            problem = {
                "number": clean_text(row['#']),
                "category": clean_text(row['Category']),
                "question": question,
                "media": media,
                "choices": choices,
                "correct_answer": clean_text(row['Answer'])
            }
            problems.append(problem)
    
    # Create the JSON structure
    json_data = {
        "problems": problems
    }
    
    # Write to JSON file with proper encoding
    with open('problems_database.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(json_data, jsonfile, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    convert_csv_to_json() 