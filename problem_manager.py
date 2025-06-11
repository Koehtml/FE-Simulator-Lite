import json
import random
from typing import Dict, List, Optional

class Problem:
    def __init__(self, 
                 number: str,
                 category: str,
                 question: str,
                 media: str,
                 choices: List[str],
                 correct_answer: str):
        self.number = number
        self.category = category
        self.question = question
        self.media = media
        self.choices = choices
        self.correct_answer = correct_answer

class ProblemManager:
    def __init__(self, num_questions: int = 50):
        self.problems: List[Problem] = []
        self.current_index = 0
        self.num_questions = num_questions
        self._load_problems_from_database()
        self._shuffle_problems()

    def _load_problems_from_database(self):
        try:
            with open('problems_database.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                for problem_data in data['problems']:
                    problem = Problem(
                        number=problem_data["number"],
                        category=problem_data["category"],
                        question=problem_data["question"],
                        media=problem_data["media"],
                        choices=problem_data["choices"],
                        correct_answer=problem_data["correct_answer"]
                    )
                    self.problems.append(problem)
        except FileNotFoundError:
            print("Error: problems_database.json not found!")
            self.problems = []
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in problems_database.json!")
            self.problems = []

    def _shuffle_problems(self):
        """Shuffle and ensure exactly num_questions problems"""
        # First shuffle the entire list
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