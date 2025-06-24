import json
import random
import os
from typing import Dict, List, Optional

class Problem:
    def __init__(self, 
                 number: str,
                 category: str,
                 question: str,
                 media: str,
                 choices: List[str],
                 correct_answer: str,
                 media_size: int = 100):  # Default to 100 if not specified
        self.number = number
        self.category = category
        self.question = question
        self.media = media
        self.choices = choices
        self.correct_answer = correct_answer
        self.media_size = media_size

class ProblemManager:
    def __init__(self, num_questions: int = 50):
        self.problems: List[Problem] = []
        self.all_problems: List[Problem] = []  # Store all problems
        self.current_index = 0
        self.num_questions = num_questions
        self.selected_categories = None
        self._load_problems_from_database()
        self._shuffle_problems()

    def _load_problems_from_database(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), 'problems_database.json'), 'r', encoding='utf-8') as file:
                data = json.load(file)
                for problem_data in data['problems']:
                    problem = Problem(
                        number=problem_data["number"],
                        category=problem_data["category"],
                        question=problem_data["question"],
                        media=problem_data["media"],
                        choices=problem_data["choices"],
                        correct_answer=problem_data["correct_answer"],
                        media_size=problem_data.get("media_size", 100)  # Use get() to default to 100 if not present
                    )
                    self.all_problems.append(problem)
        except FileNotFoundError:
            print(f"Error: {os.path.join(os.path.dirname(__file__), 'problems_database.json')} not found!")
            self.all_problems = []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {os.path.join(os.path.dirname(__file__), 'problems_database.json')}!")
            self.all_problems = []

    def set_categories(self, categories: List[str]):
        """Set the selected categories and filter problems accordingly"""
        self.selected_categories = categories
        self.problems = [p for p in self.all_problems if p.category in categories]
        self._shuffle_problems()

    def _shuffle_problems(self):
        """Shuffle and ensure exactly num_questions problems"""
        # If no categories are set, use all problems
        if self.selected_categories is None:
            self.problems = self.all_problems.copy()
        
        # First shuffle the filtered list
        random.shuffle(self.problems)
        
        # If we have fewer problems than requested, use all of them
        if len(self.problems) <= self.num_questions:
            return
            
        # Take exactly num_questions problems
        self.problems = self.problems[:self.num_questions]
        self.current_index = 0

    def get_current_problem(self) -> Optional[Problem]:
        if 0 <= self.current_index < len(self.problems):
            return self.problems[self.current_index]
        return None

    def next_problem(self) -> Optional[Problem]:
        if self.current_index < len(self.problems) - 1:
            self.current_index += 1
            return self.get_current_problem()
        return None

    def previous_problem(self) -> Optional[Problem]:
        if self.current_index > 0:
            self.current_index -= 1
            return self.get_current_problem()
        return None

    def jump_to_problem(self, index: int) -> Optional[Problem]:
        if 0 <= index < len(self.problems):
            self.current_index = index
            return self.get_current_problem()
        return None

    def total_problems(self) -> int:
        """Return the total number of problems in the current exam"""
        return len(self.problems) 

    def reshuffle_problems(self):
        """Reshuffle the problems and reset the current index"""
        self._shuffle_problems()

    def get_problems_by_category(self, category: str) -> List[Problem]:
        """Get all problems from a specific category"""
        return [p for p in self.problems if p.category == category]

    def get_categories(self) -> List[str]:
        """Get a list of all unique categories"""
        return list(set(p.category for p in self.problems)) 